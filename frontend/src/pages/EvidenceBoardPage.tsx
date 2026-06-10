import { useNavigate, useParams } from 'react-router-dom';
import { useLocale } from '../i18n/useLocale';
import { getBundledEvidence } from '../data/evidenceData';
import { EvidenceBoard } from '../components/EvidenceBoard';

// Evidence Board v2 — additive surface (route /evidence/:fixtureId). Leads with
// the AI lean + confidence TIER (stars, no %), then the reusable EvidenceBoard
// panel. Bundled-only (VITE_USE_MOCK pattern; no backend dependency this cut).
// Compliance: historical replay framing, no payment, no Token, vi Han=0.
const PAGE_LABELS = {
  zh: {
    back: '证据面板', lean: 'AI 倾向', tier: '信心档位', replay: '历史回放',
    ctaQ: '想看这场的完整复盘叙事？', ctaRecap: '查看历史复盘', ctaHome: '查看今日 AI 观点',
  },
  vi: {
    back: 'Bảng bằng chứng', lean: 'Xu hướng AI', tier: 'Mức tin cậy', replay: 'Phát lại lịch sử',
    ctaQ: 'Muốn xem phần phục dựng đầy đủ của trận này?', ctaRecap: 'Xem phục dựng lịch sử', ctaHome: 'Xem quan điểm AI hôm nay',
  },
  en: {
    back: 'Evidence Board', lean: 'AI lean', tier: 'Confidence', replay: 'Historical replay',
    ctaQ: 'Want the full recap narrative for this match?', ctaRecap: 'See historical recap', ctaHome: "See today's AI view",
  },
};

// Confidence tier -> filled stars (of 5). NEVER a probability / %.
function tierStars(tier: 'low' | 'medium' | 'high'): number {
  return tier === 'high' ? 4 : tier === 'medium' ? 3 : 2;
}

export function EvidenceBoardPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const { fixtureId = '855737' } = useParams();
  const L = loc === 'zh' ? PAGE_LABELS.zh : loc === 'vi' ? PAGE_LABELS.vi : PAGE_LABELS.en;

  // Static bundled content; re-resolves on locale change via useLocale() re-render.
  const c = getBundledEvidence(fixtureId, loc);

  if (!c) {
    return (
      <div className="page-enter">
        <div className="backbar"><button className="bk" onClick={() => navigate('/')}>←</button><span className="ti">{L.back}</span></div>
        <div className="status-card"><div className="ic">🧭</div><div className="st">—</div></div>
      </div>
    );
  }

  const filled = tierStars(c.tier);
  const stars = '★'.repeat(filled) + '☆'.repeat(5 - filled);
  const vClass = c.verdict === 'hit' ? 'green' : c.verdict === 'partial' ? 'amber' : 'red';

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate(`/recap/${fixtureId}`)}>←</button>
        <span className="ti">{L.back}</span>
      </div>

      {/* replay disclaimer banner */}
      <div className="recap-banner">🧭 {c.badge} · {c.replayTag}</div>

      {/* headline + one-liner */}
      <div className="card recap-hero">
        <h1 className="recap-headline">{c.headline}</h1>
        <p className="recap-oneliner">{c.oneLiner}</p>
      </div>

      {/* first glance: AI lean + confidence TIER (no %) + verdict */}
      <div className="card eb-lean">
        <div className="eb-lean-row">
          <div className="eb-lean-cell">
            <div className="l">{L.lean}</div>
            <div className="v">{c.leanSide}</div>
            <div className="eb-replaytag">{L.replay}</div>
          </div>
          <div className="eb-lean-cell">
            <div className="l">{L.tier}</div>
            <div className="v">{c.tierLabel}</div>
            <div className="eb-stars" aria-label={`${filled}/5`}>{stars}</div>
          </div>
        </div>
        <div className="eb-verdict-row"><span className={`pillv ${vClass}`}>{c.verdictLabel}</span></div>
        <p className="eb-leantext">{c.leanText}</p>
      </div>

      {/* reusable evidence panel: factors + evidence + missing + boundary + ledgers */}
      <EvidenceBoard content={c} loc={loc} />

      {/* continuation — link to full recap + home (additive, no payment / Token) */}
      <div className="card recap-cta">
        <div className="recap-cta-q">{L.ctaQ}</div>
        <button className="recap-cta-btn" onClick={() => navigate(`/recap/${fixtureId}`)}>{L.ctaRecap} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/')} style={{ marginTop: 8 }}>{L.ctaHome} ▸</button>
      </div>

      <div className="muted-note">{c.disclaimer}</div>
    </div>
  );
}
