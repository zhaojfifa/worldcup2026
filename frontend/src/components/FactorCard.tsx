import type { FactorView } from '../data/evidenceData';

// One factor in customer voice: 影响 / 解读 + a friendly provenance line. The 3
// decisive factors get a subtle emphasis; no internal jargon (assumption /
// replay_only / data_status) and no numeric score (no fake probability).
interface Props {
  factor: FactorView;
  labels: { impact: string; interp: string; source: string };
}

export function FactorCard({ factor: f, labels }: Props) {
  return (
    <div className={`factor-card${f.decisive ? ' decisive' : ''}`}>
      <div className="fc-head">
        <span className="fc-name">{f.name}</span>
        <span className={`factor-tag ${f.tag}`}>{f.tagLabel}</span>
      </div>
      <div className="fc-row"><span className="fc-k">{labels.impact}</span><span className="fc-v">{f.impact}</span></div>
      <div className="fc-row"><span className="fc-k">{labels.interp}</span><span className="fc-v">{f.interpretation}</span></div>
      <div className="fc-srcline">{labels.source}: {f.source}</div>
    </div>
  );
}
