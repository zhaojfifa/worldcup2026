import { useNavigate, useParams } from 'react-router-dom';
import { useLocale } from '../i18n/useLocale';
import { getBundledEvidence } from '../data/evidenceData';
import { EvidenceBoard } from '../components/EvidenceBoard';

// Evidence Board v2 — customer product voice. First screen leads with the
// model's ANSWER (title + subtitle + 4 read/verify/takeaway/value cards + a
// readable paragraph). The replay statement is small; MISS / source-required /
// assumption live only in the collapsed internal block (see EvidenceBoard).
// Bundled-only; no payment/Token; vi Han=0.
const PAGE_LABELS = {
  zh: { back: '证据面板', lead: 'AI 怎么看这场', ctaQ: '想看这场的完整复盘叙事？', ctaRecap: '查看历史复盘', ctaHome: '查看今日 AI 观点' },
  vi: { back: 'Bảng bằng chứng', lead: 'AI nhìn trận này thế nào', ctaQ: 'Muốn xem phần phục dựng đầy đủ của trận này?', ctaRecap: 'Xem phục dựng lịch sử', ctaHome: 'Xem quan điểm AI hôm nay' },
  en: { back: 'Evidence Board', lead: 'How the AI reads this match', ctaQ: 'Want the full recap narrative for this match?', ctaRecap: 'See historical recap', ctaHome: "See today's AI view" },
};

export function EvidenceBoardPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const { fixtureId = '855737' } = useParams();
  const L = loc === 'zh' ? PAGE_LABELS.zh : loc === 'vi' ? PAGE_LABELS.vi : PAGE_LABELS.en;
  const c = getBundledEvidence(fixtureId, loc);

  if (!c) {
    return (
      <div className="page-enter">
        <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{L.back}</span></div>
        <div className="status-card"><div className="ic">🧭</div><div className="st">—</div></div>
      </div>
    );
  }

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate(`/recap/${fixtureId}`)}>←</button>
        <span className="ti">{L.back}</span>
      </div>

      {/* hero — customer headline + subtitle (the answer, not the audit) */}
      <div className="card recap-hero eb-hero">
        <h1 className="recap-headline">{c.title}</h1>
        <p className="recap-oneliner">{c.subtitle}</p>
      </div>

      {/* replay statement kept small, does not dominate */}
      <div className="eb-replaynote">🗂️ {c.replayNote}</div>

      {/* first screen — 4 answer cards */}
      <div className="eb-fs-list">
        {c.firstCards.map(fc => (
          <div className={`eb-fs-card ${fc.key}`} key={fc.key}>
            <span className="eb-fs-label">{fc.label}</span>
            <span className="eb-fs-text">{fc.text}</span>
          </div>
        ))}
      </div>

      {/* the model's read — one readable paragraph */}
      <div className="sec-en"><span className="zh">{L.lead}</span><span className="en">AI READ</span></div>
      <div className="card"><p className="eb-lead">{c.customerLead}</p></div>

      {/* factors + evidence + next variables + operator copy + internal fold */}
      <EvidenceBoard content={c} loc={loc} />

      {/* continuation — additive, no payment / Token */}
      <div className="card recap-cta">
        <div className="recap-cta-q">{L.ctaQ}</div>
        <button className="recap-cta-btn" onClick={() => navigate(`/recap/${fixtureId}`)}>{L.ctaRecap} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/')} style={{ marginTop: 8 }}>{L.ctaHome} ▸</button>
      </div>

      <div className="muted-note">{c.disclaimer}</div>
    </div>
  );
}
