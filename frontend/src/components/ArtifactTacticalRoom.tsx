import type { Locale } from '../i18n/useLocale';
import type { PredictionArtifact } from '../data/predictionArtifacts';
import { predictionArtifactLocale } from '../data/predictionArtifacts';
import { buildStrongCallFromArtifact } from '../growth/strongCallProjection';
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
        focus: '今日建模关注', matchup: '战术对位', risks: '风险变量', thirty: '开球前 30 分钟修正', kickoffTba: '开球时间待确认' },
  vi: { title: 'Dự đoán điểm nóng hôm nay', room: 'Phòng chiến thuật', kicker: '⚡ Nhận định mạnh của Tiên Tri', en: 'STRONG CALL', mainSub: 'Nhận định chính hôm nay',
        leanL: 'Tiên Tri chốt', scoreL: 'Tỷ số chính', backupL: 'Phương án phụ', riskL: 'Rủi ro bất ngờ', varL: 'Biến số lớn nhất', whyL: 'Vì sao',
        extL: '🌐 Kỳ vọng bên ngoài · Xu hướng công khai', t30L: '⏱️ T-30 · Hiệu chỉnh 30 phút trước trận',
        focus: 'Tiêu điểm phân tích hôm nay', matchup: 'Đối đầu chiến thuật', risks: 'Biến số rủi ro', thirty: 'Hiệu chỉnh 30 phút trước trận', kickoffTba: 'Giờ bóng lăn chờ xác nhận' },
  my: { title: 'ဒီနေ့ အဓိကပွဲ ခန့်မှန်း', room: 'နည်းဗျူဟာခန်း', kicker: '⚡ Oracle ၏ ပြတ်သားသောအမြင်', en: 'STRONG CALL', mainSub: 'ဒီနေ့ အဓိက အမြင်',
        leanL: 'Oracle ပြတ်ပြတ်', scoreL: 'အဓိကစကော', backupL: 'အရန်', riskL: 'အံ့အားသင့် အန္တရာယ်', varL: 'အကြီးဆုံး variable', whyL: 'ဘာကြောင့်',
        extL: '🌐 ပြင်ပမျှော်လင့်ချက် · လူထုထင်မြင်ချက်', t30L: '⏱️ T-30 · ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ',
        focus: 'ဒီနေ့ ပိုင်းခြားသုံးသပ် အာရုံစိုက်ချက်', matchup: 'နည်းဗျူဟာ ထိပ်တိုက်', risks: 'အန္တရာယ် variable', thirty: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ', kickoffTba: 'ပွဲစချိန် အတည်ပြုရန်' },
  en: { title: "Today's hotspot prediction", room: 'Tactical room', kicker: '⚡ Strong call', en: 'STRONG CALL', mainSub: "Today's main read",
        leanL: 'Lean', scoreL: 'Score', backupL: 'Backup', riskL: 'Upset risk', varL: 'Biggest variable', whyL: 'Why',
        extL: '🌐 External expectation · public tendency', t30L: '⏱️ T-30 · 30-minute correction',
        focus: 'Modeling focus', matchup: 'Tactical matchup', risks: 'Risk variables', thirty: '30-minute pre-match correction', kickoffTba: 'Kickoff time pending' },
};
function chrome(loc: Locale) { return loc === 'zh' ? CHROME.zh : loc === 'vi' ? CHROME.vi : loc === 'my' ? CHROME.my : CHROME.en; }

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
      </div>

      <div className="card th-hero plp-predict">
        <FocusList title={C.focus} items={A.analysis.modeling_focus} />
        <FocusList title={C.matchup} items={A.analysis.tactical_matchup} />
        <FocusList title={C.risks} items={A.analysis.risk_variables} />
        <div className="plp-focus">
          <div className="plp-focus-title">{C.thirty}</div>
          <ul className="plp-bullets">{A.analysis.thirty_minute_checklist.map((b, i) => <li key={i}>{b}</li>)}</ul>
        </div>
        <ShareBlock kind="prematch" fixtureId={art.fixture_key} loc={loc}
                    joinLabel={A.operations.join_cta} joinTo="/community" />
      </div>
    </>
  );
}
