import type { Locale } from '../i18n/useLocale';
import type { PredictionArtifact } from '../data/predictionArtifacts';
import { predictionArtifactLocale } from '../data/predictionArtifacts';
import { DetailShareRow } from './DetailShareRow';

// MVP2-P4 — rich tactical room rendered from a Prediction Artifact (Owner: no longer generic
// when an artifact exists). Shows the fixture identity, the pre-match read (direction/score/
// confidence/risk — 方向待临场确认 when null, never invented), modeling focus, tactical matchup,
// risk variables, the 30-minute checklist, and the copy/share + join operations.
const CHROME = {
  zh: { title: '今日热点预测', room: '战术室', kickoffTba: '开球时间待确认',
        predHead: '俅哥赛前判断', dirL: '方向', scoreL: '比分', backupL: '备选', confL: '信心', riskL: '风险等级', noteL: '风险提示',
        focus: '今日建模关注', matchup: '战术对位', risks: '风险变量', thirty: '开球前 30 分钟修正', shareHead: '复制/分享' },
  vi: { title: 'Dự đoán điểm nóng hôm nay', room: 'Phòng chiến thuật', kickoffTba: 'Giờ bóng lăn chờ xác nhận',
        predHead: 'Nhận định trước trận của Tiên Tri', dirL: 'Hướng', scoreL: 'Tỷ số', backupL: 'Phụ', confL: 'Độ tin', riskL: 'Mức rủi ro', noteL: 'Lưu ý rủi ro',
        focus: 'Tiêu điểm phân tích hôm nay', matchup: 'Đối đầu chiến thuật', risks: 'Biến số rủi ro', thirty: 'Hiệu chỉnh 30 phút trước trận', shareHead: 'Sao chép / chia sẻ' },
  my: { title: 'ဒီနေ့ အဓိကပွဲ ခန့်မှန်း', room: 'နည်းဗျူဟာခန်း', kickoffTba: 'ပွဲစချိန် အတည်ပြုရန်',
        predHead: 'Oracle ပွဲကြို အမြင်', dirL: 'ဦးတည်ချက်', scoreL: 'စကော', backupL: 'အရန်', confL: 'ယုံကြည်မှု', riskL: 'အန္တရာယ်အဆင့်', noteL: 'အန္တရာယ် မှတ်ချက်',
        focus: 'ဒီနေ့ ပိုင်းခြားသုံးသပ် အာရုံစိုက်ချက်', matchup: 'နည်းဗျူဟာ ထိပ်တိုက်', risks: 'အန္တရာယ် variable', thirty: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ', shareHead: 'Link ကူး / share' },
  en: { title: "Today's hotspot prediction", room: 'Tactical room', kickoffTba: 'Kickoff time pending',
        predHead: 'Giành Cup pre-match read', dirL: 'Direction', scoreL: 'Score', backupL: 'Backup', confL: 'Confidence', riskL: 'Risk level', noteL: 'Risk note',
        focus: 'Modeling focus', matchup: 'Tactical matchup', risks: 'Risk variables', thirty: '30-minute pre-match correction', shareHead: 'Copy / share' },
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
export function ArtifactTacticalRoom({ art, loc, path }: { art: PredictionArtifact; loc: Locale; path: string }) {
  const C = chrome(loc);
  const A = predictionArtifactLocale(art, loc);
  const p = A.prediction;
  // Numeric call is shown only when confirmed; otherwise the honest pending label (never invented).
  const dir = p.primary_direction ?? A.pending_label;
  const score = p.score_call ?? A.pending_label;
  return (
    <>
      <div className="recap-banner">⚡ {C.title} · {C.room}</div>
      <div className="card ut-fixmeta">
        <span className="ut-teams">{art.home} <span className="ut-vs">vs</span> {art.away}</span>
        <span className="ut-meta">{art.kickoffUtc ? kickoffLocal(art.kickoffUtc, loc) : C.kickoffTba}</span>
      </div>

      <div className="card th-hero plp-predict">
        <div className="th-badge">{C.predHead}</div>
        <div className="sc-card" style={{ marginTop: 6 }}>
          <div className="sc-row"><span className="sc-k">{C.dirL}</span><span className="sc-v sc-lead">{dir}</span></div>
          <div className="sc-row"><span className="sc-k">{C.scoreL}</span><span className="sc-v">{score}</span></div>
          {p.backup_score && <div className="sc-row"><span className="sc-k">{C.backupL}</span><span className="sc-v">{p.backup_score}</span></div>}
          {p.confidence && <div className="sc-row"><span className="sc-k">{C.confL}</span><span className="sc-v">{p.confidence}</span></div>}
          {p.risk_level && <div className="sc-row"><span className="sc-k">{C.riskL}</span><span className="sc-v">{p.risk_level}</span></div>}
          {p.risk_note && <div className="sc-frame" style={{ textAlign: 'left' }}>⚠️ {C.noteL}：{p.risk_note}</div>}
        </div>

        <FocusList title={C.focus} items={A.analysis.modeling_focus} />
        <FocusList title={C.matchup} items={A.analysis.tactical_matchup} />
        <FocusList title={C.risks} items={A.analysis.risk_variables} />
        <div className="plp-focus">
          <div className="plp-focus-title">{C.thirty}</div>
          <ul className="plp-bullets">{A.analysis.thirty_minute_checklist.map((b, i) => <li key={i}>{b}</li>)}</ul>
        </div>

        <div className="plp-focus-title" style={{ marginTop: 10 }}>📤 {C.shareHead}</div>
        <DetailShareRow path={path} loc={loc} kind="predict" />
      </div>
    </>
  );
}
