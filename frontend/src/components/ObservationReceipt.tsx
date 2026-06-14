import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { ObservationArtifact } from '../data/predictionArtifacts';
import { observationArtifactLocale } from '../data/predictionArtifacts';
import { ShareBlock } from './ShareBlock';

// MVP2-P5 — strong post-match observation RECEIPT from the observation artifact: pre-match call
// → actual score → hit/miss (partial) → calibration focus → next-match impact. Recovered from the
// real bundled pre-match narrative + actual score; NEVER a fake recap (recap_ready=false →
// 完整复盘确认后开放). Share/operator actions via the existing ShareBlock (copy link / copy share
// text / share card / join), now artifact-aware.
const CHROME = {
  zh: { back: '赛后观察', nextL: '下一场影响' },
  vi: { back: 'Quan sát sau trận', nextL: 'Ảnh hưởng trận tới' },
  my: { back: 'ပွဲပြီး စောင့်ကြည့်ချက်', nextL: 'နောက်ပွဲ သက်ရောက်မှု' },
  en: { back: 'Post-match observation', nextL: 'Next-match impact' },
};
function chrome(loc: Locale) { return loc === 'zh' ? CHROME.zh : loc === 'vi' ? CHROME.vi : loc === 'my' ? CHROME.my : CHROME.en; }

export function ObservationReceipt({ art, loc }: { art: ObservationArtifact; loc: Locale }) {
  const navigate = useNavigate();
  const C = chrome(loc);
  const O = observationArtifactLocale(art, loc);
  return (
    <div className="page-enter">
      <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{C.back}</span></div>
      <div className="recap-banner">🗂️ {C.back}</div>
      <div className="card th-frozen">
        <div className="th-badge sc-frozen-badge">{O.state_line}</div>
        <div className="th-teams">{art.home} <span className="ut-vs">vs</span> {art.away}　{art.score}</div>

        <div className="card sc-card" style={{ marginTop: 6 }}>
          <div className="sc-row"><span className="sc-v sc-lead">{O.receipt_title}</span></div>
          <div className="sc-row"><span className="sc-v">{O.pre_match_call}</span></div>
          <div className="sc-row"><span className="sc-v" style={{ fontWeight: 700 }}>{O.actual_line}</span></div>
          <div className="sc-frame" style={{ textAlign: 'left' }}>{O.assessment}</div>
          {O.deviation && <div className="sc-row"><span className="sc-v">{O.deviation}</span></div>}
        </div>

        <div className="plp-focus">
          <div className="plp-focus-title">{O.calibration_title}</div>
          <ul className="plp-bullets">{O.calibration_points.map((b, i) => <li key={i}>{b}</li>)}</ul>
        </div>

        <div className="plp-focus">
          <div className="plp-focus-title">{C.nextL}</div>
          <div className="plp-30min">{O.next_impact}</div>
        </div>

        <div className="th-meta">{O.pending_line}</div>

        <ShareBlock kind="recap" fixtureId={art.id} loc={loc}
                    joinLabel={O.join_cta} joinTo="/community" />
      </div>
    </div>
  );
}
