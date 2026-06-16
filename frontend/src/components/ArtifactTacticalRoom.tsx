import type { Locale } from '../i18n/useLocale';
import type { PredictionArtifact } from '../data/predictionArtifacts';
import { predictionArtifactLocale } from '../data/predictionArtifacts';
import { buildStrongCallFromArtifact, CALIBRATION_LINE } from '../growth/strongCallProjection';
import { ShareBlock } from './ShareBlock';

// MVP2-P5 — the strong tactical room rendered from a Prediction Artifact via THE canonical
// strong-call projection (same values/labels as the narrative StrongCallCard). Unconfirmed
// numerics surface as the pending labels (方向待临场确认 / 比分待开球前 30 分钟确认) — never invented.
// Share/operator actions come from the existing ShareBlock (copy link / copy share text /
// share card / join), now artifact-aware.
const CHROME = {
  zh: { title: '今日热点预测', room: '战术室', kicker: '⚡ 俅哥强判断', en: 'STRONG CALL', mainSub: '今日主推判断',
        leanL: '俅哥主看', scoreL: '主比分', backupL: '备选', riskL: '冷门风险', varL: '最大变量', whyL: '为什么',
        extL: '🌐 外部预期 · 公开预测倾向', t30L: '⏱️ T-30 · 开球前 30 分钟修正',
        focus: '今日建模关注', matchup: '战术对位', risks: '风险变量', thirty: '开球前 30 分钟修正', kickoffTba: '开球时间待确认',
        rescoreCta: '看 30 分钟临场修正',
        reasonL: '关键依据', pressL: '胜负手', hideL: '可能翻车在哪', watchL: '临场重点看', confL: '把握度', groupL: '为什么进群',
        t30StateL: 'T-30 临场状态', t30Pending: '待确认 · 首发公布后群内更新最终倾向与参考比分', t30Skipped: '无重大变化，维持赛前判断' },
  vi: { title: 'Dự đoán điểm nóng hôm nay', room: 'Phòng chiến thuật', kicker: '⚡ Nhận định mạnh của Tiên Tri', en: 'STRONG CALL', mainSub: 'Nhận định chính hôm nay',
        leanL: 'Tiên Tri chốt', scoreL: 'Tỷ số chính', backupL: 'Phương án phụ', riskL: 'Rủi ro bất ngờ', varL: 'Biến số lớn nhất', whyL: 'Vì sao',
        extL: '🌐 Kỳ vọng bên ngoài · Xu hướng công khai', t30L: '⏱️ T-30 · Hiệu chỉnh 30 phút trước trận',
        focus: 'Tiêu điểm phân tích hôm nay', matchup: 'Đối đầu chiến thuật', risks: 'Biến số rủi ro', thirty: 'Hiệu chỉnh 30 phút trước trận', kickoffTba: 'Giờ bóng lăn chờ xác nhận',
        rescoreCta: 'Xem hiệu chỉnh 30 phút sát giờ',
        reasonL: 'Cơ sở chính', pressL: 'Điểm quyết định', hideL: 'Có thể lật ở đâu', watchL: 'Sát giờ chú ý', confL: 'Mức chắc chắn', groupL: 'Vì sao vào nhóm',
        t30StateL: 'Trạng thái T-30', t30Pending: 'Chờ xác nhận · đội hình ra sẽ cập nhật thiên hướng cuối + tỷ số tham khảo trong nhóm', t30Skipped: 'Không thay đổi lớn, giữ nhận định trước trận' },
  my: { title: 'ဒီနေ့ အဓိကပွဲ ခန့်မှန်း', room: 'နည်းဗျူဟာခန်း', kicker: '⚡ Oracle ၏ ပြတ်သားသောအမြင်', en: 'STRONG CALL', mainSub: 'ဒီနေ့ အဓိက အမြင်',
        leanL: 'Oracle ပြတ်ပြတ်', scoreL: 'အဓိကစကော', backupL: 'အရန်', riskL: 'အံ့အားသင့် အန္တရာယ်', varL: 'အကြီးဆုံး variable', whyL: 'ဘာကြောင့်',
        extL: '🌐 ပြင်ပမျှော်လင့်ချက် · လူထုထင်မြင်ချက်', t30L: '⏱️ T-30 · ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ',
        focus: 'ဒီနေ့ ပိုင်းခြားသုံးသပ် အာရုံစိုက်ချက်', matchup: 'နည်းဗျူဟာ ထိပ်တိုက်', risks: 'အန္တရာယ် variable', thirty: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ', kickoffTba: 'ပွဲစချိန် အတည်ပြုရန်',
        rescoreCta: 'မိနစ် ၃၀ ပွဲနီး ပြန်ညှိ ကြည့်ရန်',
        reasonL: 'အဓိက အခြေခံ', pressL: 'အရေးပါဆုံး အချက်', hideL: 'ဘယ်မှာ လှန်နိုင်', watchL: 'ပွဲနီး ဂရုစိုက်', confL: 'သေချာမှု', groupL: 'အဘယ်ကြောင့် ဝင်သင့်',
        t30StateL: 'T-30 အခြေအနေ', t30Pending: 'အတည်ပြုရန် စောင့်ဆဲ · lineup ထွက်ရင် အဖွဲ့ထဲ နောက်ဆုံးအမြင်+ရည်ညွှန်းစကော တင်မည်', t30Skipped: 'ပြောင်းလဲမှု မရှိ၊ ပွဲကြိုအမြင် ဆက်ထား' },
  en: { title: "Today's hotspot prediction", room: 'Tactical room', kicker: '⚡ Strong call', en: 'STRONG CALL', mainSub: "Today's main read",
        leanL: 'Lean', scoreL: 'Score', backupL: 'Backup', riskL: 'Upset risk', varL: 'Biggest variable', whyL: 'Why',
        extL: '🌐 External expectation · public tendency', t30L: '⏱️ T-30 · 30-minute correction',
        focus: 'Modeling focus', matchup: 'Tactical matchup', risks: 'Risk variables', thirty: '30-minute pre-match correction', kickoffTba: 'Kickoff time pending',
        rescoreCta: 'See the 30-minute live correction',
        reasonL: 'Key basis', pressL: 'Decisive point', hideL: 'Where it could flip', watchL: 'Watch before kickoff', confL: 'Confidence', groupL: 'Why join',
        t30StateL: 'T-30 status', t30Pending: 'Pending · final lean + reference score posted in the group once lineups are out', t30Skipped: 'No major change; pre-match read holds' },
};
function chrome(loc: Locale) { return loc === 'zh' ? CHROME.zh : loc === 'vi' ? CHROME.vi : loc === 'my' ? CHROME.my : CHROME.en; }

// P8 P0 — customer-safe DATA & PROVENANCE block (Owner 2026-06-15). Surfaces the reconnected
// content-fact layer: fixture-fact source, data mode, source-tagged recommended score / risk level,
// the honestly-absent numerics, and the judgement provenance — with NO model/AI/probability/betting
// wording (persona voice only; vi/my stay Han=0; win_prob/confidence never shown).
const DATA_CHROME = {
  zh: { title: '📊 数据与建模依据', srcL: '赛程事实来源', srcV: '运营每日选定', modeL: '当前数据模式', modeBase: '人工确认',
        scoreL: '推荐比分', backupL: '备选', riskL: '风险等级', missL: '缺失项', missV: '暂无自动胜率 / 数值置信度',
        judgeL: '判断来源', judgeV: '数据快照 + 俅哥判断草案 + 人工确认' },
  vi: { title: '📊 Dữ liệu & cơ sở nhận định', srcL: 'Nguồn dữ kiện trận', srcV: 'Vận hành chọn mỗi ngày', modeL: 'Chế độ dữ liệu hiện tại', modeBase: 'Xác nhận thủ công',
        scoreL: 'Tỷ số đề xuất', backupL: 'Phương án phụ', riskL: 'Mức rủi ro', missL: 'Mục còn thiếu', missV: 'Chưa có tỷ lệ tự động / độ tin cậy dạng số',
        judgeL: 'Nguồn nhận định', judgeV: 'Ảnh dữ liệu + bản nháp Tiên Tri + xác nhận thủ công' },
  my: { title: '📊 Data & အခြေခံ', srcL: 'ပွဲ အချက်အလက် ရင်းမြစ်', srcV: 'Operator နေ့စဉ် ရွေးချယ်', modeL: 'လက်ရှိ data mode', modeBase: 'Operator အတည်ပြု',
        scoreL: 'အကြံပြု စကော', backupL: 'အရန်', riskL: 'အန္တရာယ် အဆင့်', missL: 'လိုအပ်နေသေး', missV: 'အလိုအလျောက် ရာခိုင်နှုန်း / ကိန်းဂဏန်း confidence မရှိသေး',
        judgeL: 'ဆုံးဖြတ်ချက် ရင်းမြစ်', judgeV: 'Data snapshot + Oracle မူကြမ်း + operator အတည်ပြု' },
  en: { title: '📊 Data & basis', srcL: 'Fixture-fact source', srcV: 'Operator daily selection', modeL: 'Current data mode', modeBase: 'Operator-confirmed',
        scoreL: 'Recommended score', backupL: 'Backup', riskL: 'Risk level', missL: 'Missing', missV: 'No automatic win-rate / numeric confidence yet',
        judgeL: 'Judgement source', judgeV: 'Data snapshot + persona draft read + operator confirmation' },
};
function dataChrome(loc: Locale) { return loc === 'zh' ? DATA_CHROME.zh : loc === 'vi' ? DATA_CHROME.vi : loc === 'my' ? DATA_CHROME.my : DATA_CHROME.en; }

/** P8 P0 data/provenance block. Renders ONLY from the source-tagged model_fields/source_facts;
 *  win_prob/confidence are never shown (kept in missing_fields). Skips silently if absent (back-compat). */
function DataBacking({ art, loc, riskDisplay }: { art: PredictionArtifact; loc: Locale; riskDisplay: string }) {
  const sf = art.source_facts;
  const mf = art.model_fields;
  if (!sf || !mf) return null;
  const D = dataChrome(loc);
  const score = mf.recommended_score;
  const backups = mf.backup_scores ?? [];
  return (
    <div className="card db-card">
      <div className="db-title">{D.title}</div>
      <div className="sc-row"><span className="sc-k">{D.srcL}</span><span className="sc-v">{D.srcV}</span></div>
      <div className="sc-row"><span className="sc-k">{D.modeL}</span><span className="sc-v">{D.modeBase} · {mf.source}</span></div>
      {score && (
        <div className="sc-row"><span className="sc-k">{D.scoreL}</span>
          <span className="sc-v"><span className="sc-primary-score">{score}</span>
            {backups.length > 0 && <span className="sc-backup">　{D.backupL}: {backups.join(' / ')}</span>}
          </span>
        </div>
      )}
      {riskDisplay && <div className="sc-row"><span className="sc-k">{D.riskL}</span><span className="sc-v">{riskDisplay}</span></div>}
      <div className="sc-row"><span className="sc-k">{D.missL}</span><span className="sc-v">{D.missV}</span></div>
      <div className="sc-row"><span className="sc-k">{D.judgeL}</span><span className="sc-v">{D.judgeV}</span></div>
    </div>
  );
}

function kickoffLocal(iso: string, loc: Locale): string {
  const d = new Date(iso);
  const locale = loc === 'zh' ? 'zh-CN' : loc === 'vi' ? 'vi-VN' : 'en-GB';
  return d.toLocaleString(locale, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function FocusList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="plp-focus">
      <div className="plp-focus-title">{title}</div>
      <ul className="plp-bullets">{items.map((b, i) => <li key={i}>{b}</li>)}</ul>
    </div>
  );
}

/** `path` is the share/route path for this artifact (e.g. /predict/<fixture_key>). */
export function ArtifactTacticalRoom({ art, loc }: { art: PredictionArtifact; loc: Locale }) {
  const C = chrome(loc);
  const A = predictionArtifactLocale(art, loc);
  const call = buildStrongCallFromArtifact(art, loc);
  if (!call) return null;
  return (
    <>
      <div className="recap-banner">⚡ {C.title} · {C.room}</div>
      <div className="card ut-fixmeta">
        <span className="ut-teams">{art.home} <span className="ut-vs">vs</span> {art.away}</span>
        <span className="ut-meta">{art.kickoffUtc ? kickoffLocal(art.kickoffUtc, loc) : C.kickoffTba}</span>
      </div>

      {/* Strong call — same projection + sc-* styling as the narrative StrongCallCard. */}
      <div className="card sc-card">
        <div className="sc-kicker"><span className="zh">{C.kicker}</span><span className="en">{C.en}</span></div>
        <div className="sc-frame" style={{ textAlign: 'left' }}>{C.mainSub}</div>
        <div className="sc-row"><span className="sc-k">{C.leanL}</span><span className="sc-v sc-lead">{call.main_lean}</span></div>
        {call.primary_score ? (
          <div className="sc-row"><span className="sc-k">{C.scoreL}</span>
            <span className="sc-v"><span className="sc-primary-score">{call.primary_score}</span>
              {call.backup_scores.length > 0 && <span className="sc-backup">　{C.backupL}: {call.backup_scores.join(' / ')}</span>}
            </span>
          </div>
        ) : (
          <div className="sc-row"><span className="sc-k">{C.scoreL}</span><span className="sc-v">{call.scoreline_raw}</span></div>
        )}
        {call.risk_label && <div className="sc-row"><span className="sc-k">{C.riskL}</span><span className="sc-v">{call.risk_label}</span></div>}
        {call.top_variable && <div className="sc-row"><span className="sc-k">{C.varL}</span><span className="sc-v">{call.top_variable}</span></div>}
        {call.why && <div className="sc-row"><span className="sc-k">{C.whyL}</span><span className="sc-v">{call.why}</span></div>}
        {call.external_expectation.length > 0 && (
          <div className="sc-ext">
            <div className="sc-ext-label">{C.extL}</div>
            {call.external_expectation.map((x, i) => <div className="sc-ext-line" key={i}>· {x}</div>)}
          </div>
        )}
        <div className="sc-row"><span className="sc-k">{C.t30L}</span><span className="sc-v">{call.t30_hook}</span></div>
        {/* P6 P0-3: restore the calibration frame line + a scroll anchor to the T-30 block (#live30). */}
        {CALIBRATION_LINE[loc] && <div className="sc-frame" style={{ textAlign: 'left' }}>{CALIBRATION_LINE[loc]}</div>}
        <a className="sc-rescore-link" href="#live30">{C.rescoreCta} ▸</a>
      </div>

      {/* P5A copy v2 — stronger persuasive read (additive; only when the reviewed copy carries it). */}
      {A.copy_v2 && (
        <div className="card sc-card p5a-v2">
          {A.copy_v2.hook_headline && <div className="sc-row"><span className="sc-v sc-lead">{A.copy_v2.hook_headline}</span></div>}
          {A.copy_v2.main_reason && <div className="sc-row"><span className="sc-k">{C.reasonL}</span><span className="sc-v">{A.copy_v2.main_reason}</span></div>}
          {A.copy_v2.pressure_point && <div className="sc-row"><span className="sc-k">{C.pressL}</span><span className="sc-v">{A.copy_v2.pressure_point}</span></div>}
          {A.copy_v2.hidden_risk && <div className="sc-row"><span className="sc-k">{C.hideL}</span><span className="sc-v">{A.copy_v2.hidden_risk}</span></div>}
          {A.copy_v2.tactical_watch && <div className="sc-row"><span className="sc-k">{C.watchL}</span><span className="sc-v">{A.copy_v2.tactical_watch}</span></div>}
          {A.copy_v2.confidence_language && <div className="sc-row"><span className="sc-k">{C.confL}</span><span className="sc-v">{A.copy_v2.confidence_language}</span></div>}
          {A.copy_v2.group_hook && <div className="sc-row"><span className="sc-v" style={{ color: 'var(--blueMid)', fontWeight: 700 }}>{C.groupL}：{A.copy_v2.group_hook}</span></div>}
        </div>
      )}

      {/* P8 P0: customer-safe data & provenance block (source-tagged; no win_prob/confidence). */}
      <DataBacking art={art} loc={loc} riskDisplay={call.risk_label} />

      <div className="card th-hero plp-predict">
        <FocusList title={C.focus} items={A.analysis.modeling_focus} />
        <FocusList title={C.matchup} items={A.analysis.tactical_matchup} />
        <FocusList title={C.risks} items={A.analysis.risk_variables} />
        <div className="plp-focus" id="live30">
          <div className="plp-focus-title">{C.thirty}</div>
          {/* P7 P0-4: honest T-30 readiness — pending checkpoint (never a faked update), or the
              operator-confirmed re-check once lineups are out. */}
          {(() => {
            const t = art.t30;
            const txt = !t || t.status === 'pending' ? C.t30Pending
              : t.status === 'skipped' ? C.t30Skipped
                : (t.update_text || C.t30Pending);
            const cls = t && t.status === 'ready' ? 'ready' : 'pending';
            return <div className={`t30-status ${cls}`}><span className="t30-k">{C.t30StateL}</span> {txt}</div>;
          })()}
          <ul className="plp-bullets">{A.analysis.thirty_minute_checklist.map((b, i) => <li key={i}>{b}</li>)}</ul>
        </div>
        <ShareBlock kind="prematch" fixtureId={art.fixture_key} loc={loc}
                    joinLabel={A.operations.join_cta} joinTo="/community" />
      </div>
    </>
  );
}
