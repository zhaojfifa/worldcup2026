import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  fetchDailyManifest, selectProductLoop, leadReadiness, leadKey, manifestAgeMinutes,
  FALLBACK_MANIFEST, type ManifestLoad, type DailyFixtureRow,
} from '../data/dailyFixtures';
import { getSelectedHotspot } from '../data/selectedHotspot';
import {
  getPredictionArtifact, getObservationArtifact, predictionArtifactLocale, recapState,
} from '../data/predictionArtifacts';
import { getProductNarrative } from '../data/productNarrativeData';
import contentQueueRaw from '../data/dailyContentQueue.json';
import opsStateRaw from '../data/dailyOpsState.json';

// P1 content factory — typed view of the bundled daily content queue (built by
// scripts/mvp2_build_daily_content_queue.py). Rendered as the operator command console below.
interface QueueRow {
  fixture_key: string; home: string; away: string; status?: string; kickoffUtc?: string | null;
  content_state?: string; source_coverage?: string; model_source?: string | null;
  recommended_score?: string | null; risk_level?: string | null; priority_score?: number;
}
interface RecapRow { fixture_key: string; home: string; away: string; score?: string | null; recap_state: string; has_observation: boolean }
interface T30Row { fixture_key: string; home: string; away: string; t30_status: string }
interface AutogenRow { fixture_key: string; home: string; away: string; provider?: string; mode?: string; status?: string }
interface ContentQueue {
  date?: string; primary_hotspot?: QueueRow | null; secondary_matches?: QueueRow[];
  recap_queue?: RecapRow[]; t30_queue?: T30Row[]; send_status?: string; autogen_drafts?: AutogenRow[];
}
const CONTENT_QUEUE = contentQueueRaw as ContentQueue;

// P2 — daily-ops command-center snapshot (written by scripts/mvp2_daily_ops.py). Each queue item:
// fixture_id · match · status · publish_eligibility · next_action.
interface OpsQueueItem {
  fixture_id: string; match: string; status: string; publish_eligibility?: string; next_action?: string;
}
interface T30SourceItem {
  fixture_id: string; match: string; source_status: string; update_eligibility?: string;
  lineup_availability?: boolean; injury_news_availability?: boolean; next_operator_action?: string;
}
interface AutorunState {
  last_run?: string; mode?: string; runtime_match?: string; next_run?: string;
  steps_executed?: { step: string }[]; steps_skipped?: { step: string }[]; steps_blocked?: { step: string }[];
  required_operator_actions?: string[];
}
interface FreshnessState {
  freshness_status?: string; runtime_date?: string | null; artifact_date?: string | null;
  stale_reason?: string | null; homepage_primary_fixture?: string; secondary_fixtures?: string[];
}
interface ClosureItem {
  fixture_id: string; match: string; predicted_score?: string | null; actual_score?: string | null;
  result_status?: string; recap_eligibility?: string; why_it_hit_or_missed?: string | null; operator_next_action?: string;
}
interface OpsState {
  date?: string; primary?: string; secondary?: string[];
  review_queue?: OpsQueueItem[]; t30_queue?: OpsQueueItem[]; recap_queue?: OpsQueueItem[];
  share_packages?: OpsQueueItem[]; day_close?: { ready?: number; blocked?: number; status?: string; next_action?: string };
  t30_sources?: T30SourceItem[]; autorun?: AutorunState | null;
  freshness?: FreshnessState | null; recommendation_closure?: ClosureItem[];
  next_operator_action?: string; send_status?: string;
}
const OPS_STATE = opsStateRaw as OpsState;

// P7 P0-2 — /internal/daily operator content-readiness panel (Owner). NOT a public marketing page:
// an unlinked operator control surface. Reads ONLY the public runtime manifest + the build-bundled
// artifacts + the selected_hotspot record — no secrets, no admin token, no backend auth (P0), no
// send. It exists to PREVENT DRIFT (selected_hotspot == homepage lead, artifact present, T-30 +
// observation readiness) and to give the operator the links for the manual send flow.

type Verdict = 'ok' | 'warn' | 'fail' | 'na';
const ICON: Record<Verdict, string> = { ok: '✅', warn: '⚠️', fail: '❌', na: '—' };

function Row({ label, verdict, detail }: { label: string; verdict: Verdict; detail: string }) {
  return (
    <div className="idr" data-v={verdict}>
      <span className="idr-i">{ICON[verdict]}</span>
      <span className="idr-l">{label}</span>
      <span className="idr-d">{detail}</span>
    </div>
  );
}

export function DailyStatusPage() {
  const navigate = useNavigate();
  const [daily, setDaily] = useState<ManifestLoad>({ manifest: FALLBACK_MANIFEST, source: 'bundled',
    drift: { backendDate: null, backendAgeMin: null, selectedDate: null, selectedKey: null,
      backendContainsSelected: false, status: 'FALLBACK', reason: 'loading…' } });
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    let alive = true;
    fetchDailyManifest().then(r => { if (alive) { setDaily(r); setLoaded(true); } });
    return () => { alive = false; };
  }, []);

  const m = daily.manifest;
  const sel = getSelectedHotspot();
  const { featuredPrediction, featuredRecap } = selectProductLoop(m);
  const r = leadReadiness(m);
  const art = sel ? getPredictionArtifact(sel.fixture_key) : null;
  const artZh = art ? predictionArtifactLocale(art, 'zh') : null;
  const scoreCall = artZh?.prediction.score_call ?? null;
  const shareCopy = artZh?.operations.share_copy ?? null;
  const t30 = art?.t30?.status ?? null;
  // P8 P0 — content-fact readiness (source_facts / model_fields provenance).
  const sf = art?.source_facts ?? null;
  const mf = art?.model_fields ?? null;
  const oc = art?.operator_confirmation ?? null;
  const mfSource = mf?.source ?? null;   // computed | seed | operator_estimated | operator_confirmed | unavailable
  const predKey = sel ? encodeURIComponent(sel.fixture_key) : null;
  // R1 P0 — daily content-production-chain readiness (recorded on the artifact by the builder).
  const cc = art?.content_chain ?? null;
  const dr = daily.drift;   // R2a backend-vs-selection drift
  const shareKitReady = !!shareCopy && !!predKey;
  const artifactReady = !!art && !!sf && !!mf && (!!cc?.reviewed_applied || !!oc?.confirmed);

  // recap carryover: the finished featured recap must resolve to an observation/recap artifact
  const recapRow: DailyFixtureRow | null = featuredRecap;
  const recapKey = recapRow ? (recapRow.id ?? leadKey(recapRow)) : null;
  const obs = recapKey ? getObservationArtifact(recapKey) : null;
  const ageMin = manifestAgeMinutes(m);

  const v = (b: boolean): Verdict => (b ? 'ok' : 'fail');

  // R3 — data-source validity, LLM grounding, update-SLA and recap-SLA state surfaced explicitly.
  const dataSourceValid = !!mf && mfSource !== 'unavailable' && mf.no_fake_probability === true &&
    mf.win_prob == null && mf.confidence == null;
  const groundingReady = !!cc?.prompt_generated && (!!cc?.reviewed_applied || !!oc?.confirmed);
  const slaReady = !!sel && r.leadMatchesSelection && artifactReady && !!t30 && (!recapRow || !!obs);
  // recap SLA state for the carryover finished fixture (named, not just present/absent)
  const recapProductRecap = recapKey ? getProductNarrative(recapKey, 'zh') : null;
  const hasProductRecap = !!recapProductRecap &&
    (recapProductRecap.mode === 'historical_recap' || recapProductRecap.mode === 'real_recap');
  const recapSt = recapKey ? recapState(recapKey, hasProductRecap) : null;
  const lastGen = cc?.built_at || art?.date || null;
  const nextAction = !sel ? '选定今日热点 (selectedHotspot.json)'
    : !artifactReady ? '生成/复核预测产物 (mvp2_build_daily_prediction_artifact.py)'
    : daily.source !== 'backend' ? '上传后端日程清单 (mvp2_match_sync.py upload — 需运营生产令牌)'
    : recapRow && recapSt === 'RECAP_PENDING' ? '为已完赛热点生成赛后观察/复盘回执'
    : t30 === 'pending' ? '开球前 30 分钟确认首发并更新 T-30'
    : '保持 HOLD · 等 Owner 分渠道 GO';

  return (
    <div className="page-enter internal-daily">
      <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">Internal · Daily readiness</span></div>
      <div className="id-banner">🛠️ 内部运营台 · 每日就绪 / DAILY READINESS（内部，请勿外发）</div>

      {/* P4 — CRITICAL OPS VIEW (top screen). Answers in 10s: 今天是不是新内容 / 昨天推荐有没有复盘 /
          哪场命中或偏差为什么 / 哪些文案还需复核 / 今天能不能发 / 下一步该做什么. Reads dailyOpsState
          (freshness + recommendation_closure folded in by mvp2_daily_ops.py). Stale is FLAGGED, never hidden. */}
      <div className="sec-en"><span className="zh">🚨 今日关键运营 / Critical ops</span><span className="en">CRITICAL</span></div>
      <div className="card id-card">
        <Row label="今日内容是否新鲜 / Daily freshness"
             verdict={OPS_STATE.freshness ? (OPS_STATE.freshness.freshness_status === 'FRESH' ? 'ok' : (OPS_STATE.freshness.freshness_status === 'STALE' ? 'warn' : 'fail')) : 'warn'}
             detail={OPS_STATE.freshness ? `${OPS_STATE.freshness.freshness_status} · runtime=${OPS_STATE.freshness.runtime_date ?? '—'} · artifact=${OPS_STATE.freshness.artifact_date ?? '—'}${OPS_STATE.freshness.stale_reason ? ' · ' + OPS_STATE.freshness.stale_reason : ''}` : 'no freshness gate (run check_daily_freshness)'} />
        <Row label="今日主推比赛 / Today primary" verdict={OPS_STATE.primary ? 'ok' : 'fail'}
             detail={OPS_STATE.primary ? `${OPS_STATE.primary}` : 'MISSING'} />
        {/* P4R — source trace: active content date, yesterday recap fixture, and which copy the renderer projects. */}
        <Row label="生效内容日期 / Active content date" verdict={(OPS_STATE.freshness?.artifact_date) ? 'ok' : 'warn'}
             detail={`active=${OPS_STATE.freshness?.artifact_date ?? OPS_STATE.date ?? '—'} · runtime=${OPS_STATE.freshness?.runtime_date ?? '—'}`} />
        <Row label="昨日复盘比赛 / Yesterday recap fixture" verdict={recapKey ? 'ok' : 'warn'}
             detail={recapRow ? `${recapRow.home} vs ${recapRow.away} (${recapKey})` : 'none'} />
        <Row label="预测文案来源 / Prediction copy source" verdict={art?.rendered_copy_source ? 'ok' : 'warn'}
             detail={art?.rendered_copy_source ?? 'unknown — re-run apply (reviewed JSON → i18n sync)'} />
        {/* P5A — copy version per match (p5a_v2 = strong copy contract applied). */}
        <Row label="文案版本 / Copy version" verdict={art?.copy_version === 'p5a_v2' ? 'ok' : 'warn'}
             detail={`primary=${art?.copy_version ?? '—'} · secondary=${(CONTENT_QUEUE.secondary_matches ?? []).map(s => { const a = getPredictionArtifact(s.fixture_key); return `${s.fixture_key}:${a?.copy_version ?? '—'}`; }).join(' · ') || '—'}`} />
        <Row label="复盘文案来源 / Recap copy source" verdict={obs ? 'ok' : (recapRow ? 'warn' : 'na')}
             detail={obs ? `observation receipt (recap_ready=${obs.recap_ready})` : recapRow ? 'full recap / pending' : '—'} />
        <Row label="今日次级推荐 / Today secondary" verdict={(OPS_STATE.secondary?.length ?? 0) >= 2 ? 'ok' : 'warn'}
             detail={(OPS_STATE.secondary ?? []).join(', ') || 'none'} />
        <Row label="昨日推荐闭环 / Yesterday closure" verdict={(OPS_STATE.recommendation_closure?.length ?? 0) >= 1 ? 'ok' : 'warn'}
             detail={(OPS_STATE.recommendation_closure ?? []).map(c => `${c.fixture_id}:${c.result_status}`).join(' · ') || 'no closure (run recommendation_closure)'} />
        <Row label="命中/偏差/待观察 / Hit·Miss·Pending" verdict="na"
             detail={(OPS_STATE.recommendation_closure ?? []).map(c => `${c.match}: pred ${c.predicted_score ?? '—'} vs ${c.actual_score ?? '—'} → ${c.result_status}${c.recap_eligibility ? '/' + c.recap_eligibility : ''}`).join(' · ') || '—'} />
        <Row label="文案复核状态 / Copy review" verdict={(OPS_STATE.review_queue ?? []).every(i => i.publish_eligibility === 'PUBLISHED') && (OPS_STATE.review_queue?.length ?? 0) >= 1 ? 'ok' : 'warn'}
             detail={(OPS_STATE.review_queue ?? []).map(i => `${i.fixture_id}:${i.publish_eligibility}`).join(' · ') || 'none'} />
        <Row label="分享物料状态 / Share packages" verdict={(OPS_STATE.share_packages ?? []).every(i => i.status === 'SHARE_READY') && (OPS_STATE.share_packages?.length ?? 0) >= 1 ? 'ok' : 'warn'}
             detail={(OPS_STATE.share_packages ?? []).map(i => `${i.fixture_id}:${i.status}`).join(' · ') || 'none'} />
        <Row label="今天能不能发 / Can we send" verdict="warn" detail="HOLD — 需 Owner 分渠道 GO；不自动发送" />
        <Row label="下一步运营动作 / Next action" verdict="warn" detail={OPS_STATE.next_operator_action ?? '—'} />
      </div>

      <div className="card id-card">
        <Row label="Date / 日期" verdict={loaded ? 'ok' : 'warn'} detail={`${m.generated_for_date ?? '—'}${loaded ? '' : ' · loading…'}`} />
        <Row label="Selected hotspot / 今日选定" verdict={sel ? 'ok' : 'fail'}
             detail={sel ? `${sel.home} vs ${sel.away} (${sel.fixture_key}) · ${sel.source}` : 'MISSING — no selected_hotspot bundled'} />
        <Row label="Live homepage lead / 首页主推" verdict={featuredPrediction ? 'ok' : 'fail'}
             detail={featuredPrediction ? `${featuredPrediction.home} vs ${featuredPrediction.away} (${r.leadKey})` : 'NONE — no artifact-backed lead'} />
        <Row label="Selected == lead / 一致性" verdict={!sel ? 'na' : (r.leadMatchesSelection ? 'ok' : 'fail')}
             detail={!sel ? 'no selection' : r.leadMatchesSelection ? 'match' : (r.selectionInSlate ? 'MISMATCH — selection in slate but not the lead (check artifact)' : 'selection not in today’s slate (fallback lead shown)')} />
        <Row label="Prediction artifact / 预测产物" verdict={v(!!art)}
             detail={art ? `present · ${art.fixture_key} · confirmed=${art.prediction_confirmed}` : 'MISSING for selected hotspot'} />
        <Row label="Score-call hook / 主比分" verdict={v(!!scoreCall)}
             detail={scoreCall ? `主比分 ${scoreCall} · 备选 ${artZh?.prediction.backup_score ?? '—'} · 冷门风险 ${artZh?.prediction.risk_level ?? '—'}` : 'no confirmed score call'} />
        {/* P8 P0 — content-fact provenance readiness. */}
        <Row label="Source facts / 事实来源" verdict={v(!!sf)}
             detail={sf ? `data_mode=${sf.data_mode} · fixture_source=${sf.fixture_source} · has_model_fields=${sf.has_model_fields} · refs=${sf.source_refs.length}` : 'MISSING source_facts (P8 not reconnected)'} />
        <Row label="Model fields / 建模字段" verdict={mf ? (mfSource && mfSource !== 'unavailable' ? 'ok' : 'warn') : 'fail'}
             detail={mf ? `source=${mfSource} · status=${mf.model_status} · recommended_score=${mf.recommended_score ?? '—'} · backup=${(mf.backup_scores ?? []).join('/') || '—'} · risk_level=${mf.risk_level ?? '—'}` : 'MISSING model_fields'} />
        <Row label="win_prob / confidence" verdict="na"
             detail={`win_prob=${mf?.win_prob ?? 'null'} · confidence=${mf?.confidence ?? 'null'} · unavailable acceptable (no fake probability)`} />
        <Row label="No-fake-probability / 不伪概率" verdict={v(mf?.no_fake_probability === true)}
             detail={mf?.no_fake_probability === true ? 'model_fields.no_fake_probability=true' : 'NOT asserted'} />
        <Row label="Source tag legend / 来源标记" verdict="na"
             detail="computed · seed · operator_estimated · operator_confirmed · unavailable" />
        <Row label="Operator confirmation / 人工确认" verdict={v(!!oc?.confirmed)}
             detail={oc?.confirmed ? `by=${oc.confirmed_by || '—'} · at=${oc.confirmed_at || '—'} · edited=${(oc.edited_fields ?? []).length}` : 'not confirmed'} />
        {/* R1 P0 — daily content production chain readiness (facts → prompt → review → artifact). */}
        <Row label="Data-source lookup / 数据源查找" verdict={cc ? (cc.model_lookup === 'found' ? 'ok' : 'warn') : 'fail'}
             detail={cc ? `${cc.model_lookup} · ${cc.model_lookup_note}` : 'MISSING content_chain (builder not run)'} />
        <Row label="Prompt file / 提示词产物" verdict={v(!!cc?.prompt_generated)}
             detail={cc?.prompt_generated ? (cc.prompt_path ?? 'generated') : 'not generated (run builder: prompt)'} />
        <Row label="Reviewed JSON / 复核产物" verdict={v(!!cc?.reviewed_applied)}
             detail={cc?.reviewed_applied ? `applied · provider=${cc.llm_provider} · ${cc.reviewed_path ?? ''}` : 'not applied (run builder: apply --reviewed)'} />
        <Row label="Artifact ready / 产物就绪" verdict={v(artifactReady)}
             detail={artifactReady ? 'fixture_identity + source_facts + model_fields + judgement + chain' : 'incomplete content chain'} />
        <Row label="Share kit / 分享物料" verdict={v(shareKitReady)}
             detail={shareKitReady ? 'share_copy + share card route present' : 'missing share copy or route'} />
        <Row label="Share copy / 分享文案" verdict={v(!!shareCopy)} detail={shareCopy ? 'present (operations.share_copy)' : 'missing'} />
        <Row label="Share card / 分享卡" verdict={v(!!predKey)} detail={predKey ? `/share/fixture/${predKey}` : 'n/a'} />
        <Row label="T-30 status / 临场就绪" verdict={t30 === 'ready' ? 'ok' : t30 === 'skipped' ? 'ok' : 'warn'}
             detail={t30 ? `${t30}${t30 === 'pending' ? ' · honest checkpoint until lineups out (no faked update)' : ''}` : 'no t30 slot'} />
        <Row label="Observation / recap / 复盘回执" verdict={!recapRow ? 'na' : (obs ? 'ok' : 'fail')}
             detail={!recapRow ? 'no finished featured fixture' : obs ? `present · recap_ready=${obs.recap_ready} (${obs.recap_ready ? 'full recap' : 'observation receipt'})` : `MISSING for finished ${recapRow.home} vs ${recapRow.away}`} />
        <Row label="Recap carryover / 次日承接" verdict={!recapRow ? 'na' : (recapKey && obs ? 'ok' : 'warn')}
             detail={!recapRow ? '—' : recapKey ? `keyed by ${recapRow.id ? 'id' : 'fixture_key'} (${recapKey})` : 'no key'} />
        <Row label="Slate freshness / 数据新鲜度" verdict={daily.source === 'backend' ? 'ok' : 'warn'}
             detail={`source=${daily.source} · age=${ageMin == null ? '—' : ageMin + 'm'} · ${m.fixtures?.length ?? 0} fixtures`} />
        {/* R2a — backend-vs-selection drift (a stale backend must NOT silently override the fresh pick). */}
        <Row label="Backend manifest date / 后端日期" verdict={dr.backendDate ? 'ok' : 'warn'}
             detail={`backend date=${dr.backendDate ?? 'MISSING'}${dr.backendAgeMin != null ? ' · age=' + Math.round(dr.backendAgeMin / 60) + 'h' : ''}`} />
        <Row label="Selected date / 选定日期" verdict={dr.selectedDate ? 'ok' : 'warn'}
             detail={`selected=${dr.selectedDate ?? '—'} (${dr.selectedKey ?? '—'})`} />
        <Row label="Backend contains selection / 含选定" verdict={dr.backendContainsSelected ? 'ok' : 'warn'}
             detail={dr.backendContainsSelected ? 'yes — backend slate has the selected hotspot' : 'no — backend slate is missing the selected hotspot'} />
        <Row label="Active source / 生效来源" verdict={daily.source === 'backend' ? 'ok' : (daily.source === 'static' || daily.source === 'bundled' ? 'warn' : 'fail')}
             detail={`${daily.source}${daily.source !== 'backend' ? ' (bundled/static fresh fallback)' : ' (live runtime)'}`} />
        <Row label="Drift status / 漂移状态" verdict={dr.status === 'MATCH' ? 'ok' : dr.status === 'FALLBACK' ? 'warn' : 'fail'}
             detail={`${dr.status} · ${dr.reason}`} />
        {/* R3 — data-source validity, content grounding, update + recap SLA state, last gen, next action. */}
        <Row label="Data source validity / 数据源有效性" verdict={mf ? (dataSourceValid ? 'ok' : 'warn') : 'fail'}
             detail={mf ? `model_fields.source=${mfSource} · data_mode=${sf?.data_mode ?? '—'} · ${mfSource === 'computed' ? 'real ScoutScore' : mfSource === 'unavailable' ? 'no computed source' : 'operator'} · no_fake_probability=${mf.no_fake_probability === true}` : 'no model_fields'} />
        <Row label="Content grounding / 内容接地" verdict={groundingReady ? 'ok' : 'warn'}
             detail={cc ? `prompt=${!!cc.prompt_generated} · reviewed=${!!cc.reviewed_applied} · provider=${cc.llm_provider}` : 'no content_chain'} />
        <Row label="Update SLA state / 更新就绪" verdict={slaReady ? 'ok' : 'warn'}
             detail={slaReady ? 'slate-current + artifact-ready + T-30 explicit + recap state explicit' : 'one or more SLA states not yet ready (see rows above)'} />
        <Row label="Recap SLA state / 复盘状态" verdict={!recapRow ? 'na' : (recapSt === 'RECAP_READY' || recapSt === 'OBSERVATION_READY' ? 'ok' : recapSt === 'RECAP_PENDING' ? 'warn' : 'fail')}
             detail={!recapRow ? 'no finished featured fixture' : `${recapSt}${recapSt === 'OBSERVATION_READY' ? ' (observation receipt — full recap not built; no raw error)' : recapSt === 'RECAP_READY' ? ' (full recap available)' : recapSt === 'RECAP_PENDING' ? ' (safe post-match page; build observation/recap)' : ' (no local source — safe generic page, never backend error)'}`} />
        <Row label="Last successful generation / 上次生成" verdict={lastGen ? 'ok' : 'warn'}
             detail={lastGen ? `${lastGen} (content_chain.built_at / artifact date)` : 'unknown'} />
        <Row label="Next operator action / 下一步运营动作" verdict="warn" detail={nextAction} />
        <Row label="Send status / 发送状态" verdict="warn" detail="HOLD — manual only; Owner per-channel GO required; no auto-send" />
      </div>

      {/* P1 content factory — daily content QUEUE console: primary + secondary + recap + T-30 with
          per-match content_state, source coverage, and SLA. Reads the bundled dailyContentQueue.json. */}
      <div className="sec-en"><span className="zh">🏭 内容工厂队列 / Content factory queue</span><span className="en">QUEUE</span></div>
      <div className="card id-card">
        <Row label="Queue date / 队列日期" verdict={CONTENT_QUEUE.date ? 'ok' : 'warn'} detail={CONTENT_QUEUE.date ?? '—'} />
        {CONTENT_QUEUE.primary_hotspot ? (
          <Row label="Primary hotspot / 主热点" verdict={(CONTENT_QUEUE.primary_hotspot.content_state === 'PUBLISHED' || CONTENT_QUEUE.primary_hotspot.content_state === 'ARTIFACT_READY') ? 'ok' : 'warn'}
               detail={`${CONTENT_QUEUE.primary_hotspot.home} vs ${CONTENT_QUEUE.primary_hotspot.away} · ${CONTENT_QUEUE.primary_hotspot.content_state} · source=${CONTENT_QUEUE.primary_hotspot.source_coverage}`} />
        ) : <Row label="Primary hotspot / 主热点" verdict="fail" detail="MISSING" />}
        <Row label="Secondary matches / 次要赛事" verdict={(CONTENT_QUEUE.secondary_matches?.length ?? 0) >= 1 ? 'ok' : 'warn'}
             detail={`${CONTENT_QUEUE.secondary_matches?.length ?? 0} selected`} />
        {(CONTENT_QUEUE.secondary_matches ?? []).map(s => (
          <Row key={s.fixture_key}
               label={`· ${s.home} vs ${s.away}`}
               verdict={(s.content_state === 'PUBLISHED' || s.content_state === 'ARTIFACT_READY') ? 'ok' : (s.content_state === 'FIXTURE_READY' ? 'fail' : 'warn')}
               detail={`${s.content_state} · prediction=${s.content_state === 'PUBLISHED' ? 'ready' : 'pending'} · prompt/review=${s.content_state === 'PUBLISHED' || s.content_state === 'REVIEW_READY' ? 'applied' : 'pending'} · source=${s.source_coverage} · score=${s.recommended_score ?? '—'} · /predict/${s.fixture_key}`} />
        ))}
        <Row label="T-30 queue / 临场队列" verdict={(CONTENT_QUEUE.t30_queue?.length ?? 0) >= 1 ? 'ok' : 'na'}
             detail={(CONTENT_QUEUE.t30_queue ?? []).map(t => `${t.home}:${t.t30_status}`).join(' · ') || 'none'} />
        <Row label="Recap queue / 复盘队列" verdict={(CONTENT_QUEUE.recap_queue?.length ?? 0) >= 1 ? 'ok' : 'na'}
             detail={(CONTENT_QUEUE.recap_queue ?? []).map(rq => `${rq.home} vs ${rq.away} ${rq.score ?? ''}→${rq.recap_state}`).join(' · ') || 'none'} />
        <Row label="Source coverage / 来源覆盖" verdict={(CONTENT_QUEUE.secondary_matches ?? []).concat(CONTENT_QUEUE.primary_hotspot ? [CONTENT_QUEUE.primary_hotspot] : []).some(x => x.source_coverage === 'missing') ? 'warn' : 'ok'}
             detail={(CONTENT_QUEUE.secondary_matches ?? []).concat(CONTENT_QUEUE.primary_hotspot ? [CONTENT_QUEUE.primary_hotspot] : []).filter(x => x.source_coverage !== 'computed').map(x => `${x.home}/${x.away}:${x.source_coverage}`).join(' · ') || 'all computed'} />
        {/* P1B — auto-LLM generated-draft status (draft only; operator review still required before publish). */}
        <Row label="Auto-draft status / 自动草稿" verdict={(CONTENT_QUEUE.autogen_drafts?.length ?? 0) >= 1 ? 'ok' : 'na'}
             detail={(CONTENT_QUEUE.autogen_drafts ?? []).length
               ? (CONTENT_QUEUE.autogen_drafts ?? []).map(g => `${g.home}:${g.status}(${g.provider}/${g.mode})`).join(' · ') + ' · review required before publish'
               : 'no generated drafts (run autogen generator)'} />
        <Row label="Queue send status / 队列发送" verdict="warn" detail={`${CONTENT_QUEUE.send_status ?? 'HOLD'} — no auto-send`} />
      </div>

      {/* P2 — operator command center: review/T-30/recap/share queues + day close + next action.
          Reads the dailyOpsState.json snapshot (written by mvp2_daily_ops.py). Answers
          "what is ready, what is blocked, what do I do next?" — never auto-sends, never auto-publishes. */}
      <div className="sec-en"><span className="zh">🛰️ 每日指挥台 / Daily command center</span><span className="en">COMMAND CENTER</span></div>
      <div className="card id-card">
        <Row label="Runtime / 运行时" verdict={dr.status === 'MATCH' ? 'ok' : dr.status === 'FALLBACK' ? 'warn' : 'fail'}
             detail={`drift=${dr.status} (see slate/drift rows above)`} />
        <Row label="Today queue / 今日队列" verdict={OPS_STATE.primary ? 'ok' : 'warn'}
             detail={`primary=${OPS_STATE.primary ?? '—'} · secondary=${(OPS_STATE.secondary ?? []).join(',') || '—'}`} />
        <Row label="Review queue / 复核队列" verdict={(OPS_STATE.review_queue?.length ?? 0) >= 1 ? 'ok' : 'warn'}
             detail={(OPS_STATE.review_queue ?? []).map(i => `${i.fixture_id}:${i.status}/${i.publish_eligibility}`).join(' · ') || 'none'} />
        <Row label="Artifact readiness / 产物就绪" verdict={(OPS_STATE.review_queue ?? []).some(i => i.publish_eligibility === 'PUBLISHED') ? 'ok' : 'warn'}
             detail={`${(OPS_STATE.review_queue ?? []).filter(i => i.publish_eligibility === 'PUBLISHED').length} published · ${(OPS_STATE.review_queue ?? []).filter(i => i.publish_eligibility !== 'PUBLISHED').length} review-required`} />
        <Row label="T-30 queue / 临场队列" verdict={(OPS_STATE.t30_queue?.length ?? 0) >= 1 ? 'ok' : 'na'}
             detail={(OPS_STATE.t30_queue ?? []).map(i => `${i.fixture_id}:${i.status}`).join(' · ') || 'none'} />
        <Row label="FT observation+recap / 复盘队列" verdict={(OPS_STATE.recap_queue?.length ?? 0) >= 1 ? 'ok' : 'na'}
             detail={(OPS_STATE.recap_queue ?? []).map(i => `${i.fixture_id}:${i.publish_eligibility}`).join(' · ') || 'none'} />
        <Row label="Share package / 分享物料队列" verdict={(OPS_STATE.share_packages ?? []).every(i => i.status === 'SHARE_READY') && (OPS_STATE.share_packages?.length ?? 0) >= 1 ? 'ok' : 'warn'}
             detail={(OPS_STATE.share_packages ?? []).map(i => `${i.fixture_id}:${i.status}`).join(' · ') || 'none'} />
        <Row label="Day close / 收日" verdict={OPS_STATE.day_close ? 'ok' : 'warn'}
             detail={OPS_STATE.day_close ? `status=${OPS_STATE.day_close.status} · ready=${OPS_STATE.day_close.ready} · blocked=${OPS_STATE.day_close.blocked}` : 'not closed'} />
        {/* P3A — daily auto-run status. P3B — T-30 source coverage by match. */}
        <Row label="Daily auto-run / 每日自动运行" verdict={OPS_STATE.autorun ? ((OPS_STATE.autorun.steps_blocked?.length ?? 0) === 0 ? 'ok' : 'fail') : 'warn'}
             detail={OPS_STATE.autorun ? `mode=${OPS_STATE.autorun.mode} · runtime=${OPS_STATE.autorun.runtime_match} · last run ${OPS_STATE.autorun.last_run}` : 'not run (mvp2_daily_autorun.py run)'} />
        <Row label="Autorun steps / 运行步骤" verdict={(OPS_STATE.autorun?.steps_blocked?.length ?? 0) === 0 ? 'ok' : 'fail'}
             detail={OPS_STATE.autorun ? `passed=${OPS_STATE.autorun.steps_executed?.length ?? 0} · skipped=${(OPS_STATE.autorun.steps_skipped ?? []).map(s => s.step).join(',') || 0} · blocked=${(OPS_STATE.autorun.steps_blocked ?? []).map(s => s.step).join(',') || 0}` : '—'} />
        <Row label="Next scheduled/manual run / 下次运行" verdict="na" detail={OPS_STATE.autorun?.next_run ?? 'operator-triggered (manual; no scheduler)'} />
        <Row label="T-30 source coverage / 临场数据来源" verdict={(OPS_STATE.t30_sources?.length ?? 0) >= 1 ? ((OPS_STATE.t30_sources ?? []).some(s => s.source_status === 'SOURCE_READY') ? 'ok' : 'warn') : 'na'}
             detail={(OPS_STATE.t30_sources ?? []).map(s => `${s.fixture_id}:${s.source_status}`).join(' · ') || 'none'} />
        <Row label="T-30 source detail / 来源缺口" verdict="na"
             detail={(OPS_STATE.t30_sources ?? []).map(s => `${s.fixture_id} lineup=${s.lineup_availability} injury=${s.injury_news_availability} → ${s.update_eligibility}`).join(' · ') || 'no live lineup/injury feed — operator confirms at KO-30'} />
        <Row label="Next operator action / 下一步" verdict="warn" detail={OPS_STATE.next_operator_action ?? '—'} />
        <Row label="Send status / 发送状态" verdict="warn" detail={`${OPS_STATE.send_status ?? 'HOLD'} — manual only; Owner per-channel GO; no auto-send`} />
      </div>

      <div className="sec-en"><span className="zh">🔗 运营链接 / Operator links</span><span className="en">LINKS</span></div>
      <div className="card id-links">
        <button className="btn-mini" onClick={() => navigate('/')}>Homepage 首页</button>
        {predKey && <button className="btn-mini" onClick={() => navigate(`/predict/${predKey}`)}>Predict 战术室</button>}
        {recapKey && <button className="btn-mini" onClick={() => navigate(`/recap/${encodeURIComponent(recapKey)}`)}>Recap/Observation 复盘</button>}
        {predKey && <button className="btn-mini" onClick={() => navigate(`/share/fixture/${predKey}?lang=zh`)}>Prediction share card 预测分享卡</button>}
        {recapKey && <button className="btn-mini" onClick={() => navigate(`/share/recap/${encodeURIComponent(recapKey)}?lang=zh`)}>Recap share card 复盘分享卡</button>}
        <button className="btn-mini" onClick={() => navigate('/join')}>Join / ref 加入</button>
      </div>

      <div className="muted-note">内部运营就绪检查 · 只读 · 不发送任何内容 · 不含密钥 / Internal readiness · read-only · sends nothing · no secrets.</div>
    </div>
  );
}
