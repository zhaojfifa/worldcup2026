import type { FactorView } from '../data/evidenceData';

// One ScoutScore factor rendered as Source / Impact / Interpretation, with an
// honesty flag when the factor is an assumption (no source_refs). No numeric
// score/weight is shown — qualitative status only (no fake probability).
interface Props {
  factor: FactorView;
  labels: { source: string; impact: string; interp: string; assumption: string };
}

export function FactorCard({ factor: f, labels }: Props) {
  return (
    <div className="factor-card">
      <div className="fc-head">
        <span className="fc-name">{f.name}</span>
        <span className={`factor-tag ${f.tag}`}>{f.tagLabel}</span>
        {f.assumption && <span className="fc-assume">{labels.assumption}</span>}
      </div>
      <div className="fc-row"><span className="fc-k">{labels.source}</span><span className="fc-v fc-src">{f.source}</span></div>
      <div className="fc-row"><span className="fc-k">{labels.impact}</span><span className="fc-v">{f.impact}</span></div>
      <div className="fc-row"><span className="fc-k">{labels.interp}</span><span className="fc-v">{f.interpretation}</span></div>
    </div>
  );
}
