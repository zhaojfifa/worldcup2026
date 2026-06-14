import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { ObservationArtifact } from '../data/predictionArtifacts';
import { observationArtifactLocale } from '../data/predictionArtifacts';
import { CopyLink } from './CopyLink';
import { recordJoinIntent } from '../growth/refCapture';

// MVP2-P4 — safe post-match observation RECEIPT rendered from an observation artifact.
// Recovered from the real bundled pre-match narrative + the actual score; NEVER a fake recap.
// recap_ready=false → 完整复盘确认后开放, calibration focus + receipt only, no full-recap link.
// Share/copy + the artifact's own join CTA (加入情报群看赛后观察). No auto-send.
const CHROME = {
  zh: { back: '赛后观察', shareHead: '复制/分享', copy: '复制观察链接', done: '已复制 ✓' },
  vi: { back: 'Quan sát sau trận', shareHead: 'Sao chép / chia sẻ', copy: 'Sao chép link quan sát', done: 'Đã sao chép ✓' },
  my: { back: 'ပွဲပြီး စောင့်ကြည့်ချက်', shareHead: 'Link ကူး / share', copy: 'စောင့်ကြည့် link ကူး', done: 'ကူးပြီး ✓' },
  en: { back: 'Post-match observation', shareHead: 'Copy / share', copy: 'Copy observation link', done: 'Copied ✓' },
};
function chrome(loc: Locale) { return loc === 'zh' ? CHROME.zh : loc === 'vi' ? CHROME.vi : loc === 'my' ? CHROME.my : CHROME.en; }

export function ObservationReceipt({ art, loc }: { art: ObservationArtifact; loc: Locale }) {
  const navigate = useNavigate();
  const C = chrome(loc);
  const O = observationArtifactLocale(art, loc);
  const path = `/recap/${art.id}`;
  return (
    <div className="page-enter">
      <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{C.back}</span></div>
      <div className="recap-banner">🗂️ {C.back}</div>
      <div className="card th-frozen">
        <div className="th-badge sc-frozen-badge">{O.state_line}</div>
        <div className="th-teams">{art.home} <span className="ut-vs">vs</span> {art.away}　{art.score}</div>

        <div className="sc-card" style={{ marginTop: 6 }}>
          <div className="sc-row"><span className="sc-v sc-lead">{O.receipt_title}</span></div>
          <div className="sc-row"><span className="sc-v">{O.pre_match_call}</span></div>
          <div className="sc-row"><span className="sc-v" style={{ fontWeight: 700 }}>{O.actual_line}</span></div>
          <div className="sc-frame" style={{ textAlign: 'left' }}>{O.assessment}</div>
        </div>

        <div className="plp-focus">
          <div className="plp-focus-title">{O.calibration_title}</div>
          <ul className="plp-bullets">{O.calibration_points.map((b, i) => <li key={i}>{b}</li>)}</ul>
        </div>

        <div className="th-meta">{O.pending_line}</div>

        <button className="recap-cta-btn" style={{ width: '100%', marginTop: 8 }}
                onClick={() => { recordJoinIntent(path, loc); navigate('/community'); }}>{O.join_cta} ▸</button>
        <div className="plp-focus-title" style={{ marginTop: 10 }}>📤 {C.shareHead}</div>
        <div className="share-block">
          <CopyLink path={path} loc={loc} label={C.copy} doneLabel={C.done} />
        </div>
      </div>
    </div>
  );
}
