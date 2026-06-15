import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  fetchDailyManifest, selectProductLoop, leadReadiness, leadKey, manifestAgeMinutes,
  FALLBACK_MANIFEST, type ManifestLoad, type DailyFixtureRow,
} from '../data/dailyFixtures';
import { getSelectedHotspot } from '../data/selectedHotspot';
import {
  getPredictionArtifact, getObservationArtifact, predictionArtifactLocale,
} from '../data/predictionArtifacts';

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
  const [daily, setDaily] = useState<ManifestLoad>({ manifest: FALLBACK_MANIFEST, source: 'bundled' });
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
  const predKey = sel ? encodeURIComponent(sel.fixture_key) : null;

  // recap carryover: the finished featured recap must resolve to an observation/recap artifact
  const recapRow: DailyFixtureRow | null = featuredRecap;
  const recapKey = recapRow ? (recapRow.id ?? leadKey(recapRow)) : null;
  const obs = recapKey ? getObservationArtifact(recapKey) : null;
  const ageMin = manifestAgeMinutes(m);

  const v = (b: boolean): Verdict => (b ? 'ok' : 'fail');

  return (
    <div className="page-enter internal-daily">
      <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">Internal · Daily readiness</span></div>
      <div className="id-banner">🛠️ 内部运营台 · 每日就绪 / DAILY READINESS（内部，请勿外发）</div>

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
        <Row label="Send status / 发送状态" verdict="warn" detail="HOLD — manual only; Owner per-channel GO required; no auto-send" />
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
