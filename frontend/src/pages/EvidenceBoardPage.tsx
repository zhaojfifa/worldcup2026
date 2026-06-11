import { useNavigate, useParams } from 'react-router-dom';
import { useLocale } from '../i18n/useLocale';
import { getBundledEvidence } from '../data/evidenceData';
import { getNarrative } from '../data/narrativeData';
import { EvidenceBoard } from '../components/EvidenceBoard';
import { NarrativeView } from '../components/NarrativeView';

// Evidence Board v2 — main view prefers the LLM-generated narrative (DeepSeek,
// guard-passed) per docs/MVP2_LLM_NARRATIVE_CONTRACT.md. The hand-written
// evidenceData copy is a DETERMINISTIC FALLBACK only (en/mm, or no narrative).
// Bundled-only; no payment/Token; vi Han=0.
const PAGE_LABELS = {
  zh: { back: '证据面板', lead: '俅哥怎么看这场', ctaQ: '想看这场的完整复盘叙事？', ctaRecap: '查看历史复盘', ctaHome: '查看俅哥判断', ledger: '数据来源 / Source Ledger（点击展开）' },
  vi: { back: 'Bảng bằng chứng', lead: 'AI nhìn trận này thế nào', ctaQ: 'Muốn xem phần phục dựng đầy đủ của trận này?', ctaRecap: 'Xem phục dựng lịch sử', ctaHome: 'Xem quan điểm AI hôm nay', ledger: 'Nguồn dữ liệu / Source Ledger (nhấn để mở)' },
  en: { back: 'Evidence Board', lead: 'How the AI reads this match', ctaQ: 'Want the full recap narrative for this match?', ctaRecap: 'See historical recap', ctaHome: "See today's AI view", ledger: 'Source Ledger (click to expand)' },
};

export function EvidenceBoardPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const { fixtureId = '855737' } = useParams();
  const L = loc === 'zh' ? PAGE_LABELS.zh : loc === 'vi' ? PAGE_LABELS.vi : PAGE_LABELS.en;
  const c = getBundledEvidence(fixtureId, loc);
  const narr = getNarrative(fixtureId, loc);

  if (!c) {
    return (
      <div className="page-enter">
        <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{L.back}</span></div>
        <div className="status-card"><div className="ic">🧭</div><div className="st">—</div></div>
      </div>
    );
  }

  // ── Preferred: LLM-generated narrative main view ──────────────────────────
  if (narr) {
    return (
      <div className="page-enter">
        <div className="backbar">
          <button className="bk" onClick={() => navigate(`/recap/${fixtureId}`)}>←</button>
          <span className="ti">{L.back}</span>
        </div>
        <div className="card recap-hero eb-hero">
          <h1 className="recap-headline">{narr.hero_title}</h1>
          <p className="recap-oneliner">{narr.hero_subtitle}</p>
        </div>
        <div className="eb-replaynote">🗂️ {c.replayNote}</div>

        <NarrativeView narrative={narr} loc={loc} />

        {/* provenance — source ledger, collapsed */}
        <details className="card recap-ledger">
          <summary>{L.ledger}</summary>
          <table className="recap-ledger-tbl"><tbody>
            {c.sourceLedger.map((r, i) => (
              <tr key={i}><td>{r.field}</td><td>{r.endpoint}</td><td>API-FOOTBALL</td></tr>
            ))}
          </tbody></table>
        </details>

        <div className="card recap-cta">
          <div className="recap-cta-q">{L.ctaQ}</div>
          <button className="recap-cta-btn" onClick={() => navigate(`/recap/${fixtureId}`)}>{narr.cta_copy || L.ctaRecap} ▸</button>
          <button className="recap-cta-btn alt" onClick={() => navigate('/')} style={{ marginTop: 8 }}>{L.ctaHome} ▸</button>
        </div>
        <div className="muted-note">{c.disclaimer}</div>
      </div>
    );
  }

  // ── Deterministic fallback (en/mm, or LLM/guard unavailable) ──────────────
  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate(`/recap/${fixtureId}`)}>←</button>
        <span className="ti">{L.back}</span>
      </div>
      <div className="card recap-hero eb-hero">
        <h1 className="recap-headline">{c.title}</h1>
        <p className="recap-oneliner">{c.subtitle}</p>
      </div>
      <div className="eb-replaynote">🗂️ {c.replayNote}</div>
      <div className="eb-fs-list">
        {c.firstCards.map(fc => (
          <div className={`eb-fs-card ${fc.key}`} key={fc.key}>
            <span className="eb-fs-label">{fc.label}</span>
            <span className="eb-fs-text">{fc.text}</span>
          </div>
        ))}
      </div>
      <div className="sec-en"><span className="zh">{L.lead}</span><span className="en">THE READ</span></div>
      <div className="card"><p className="eb-lead">{c.customerLead}</p></div>
      <EvidenceBoard content={c} loc={loc} />
      <div className="card recap-cta">
        <div className="recap-cta-q">{L.ctaQ}</div>
        <button className="recap-cta-btn" onClick={() => navigate(`/recap/${fixtureId}`)}>{L.ctaRecap} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/')} style={{ marginTop: 8 }}>{L.ctaHome} ▸</button>
      </div>
      <div className="muted-note">{c.disclaimer}</div>
    </div>
  );
}
