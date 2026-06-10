import type { EvidenceItem } from '../data/evidenceData';

// One real, provenance-tagged match statistic (label / value / source endpoint).
// Values are observed match data (e.g. possession %), never a prediction %.
export function EvidenceCard({ item }: { item: EvidenceItem }) {
  return (
    <div className="eb-evcard">
      <div className="t">{item.label}</div>
      <div className="v">{item.value}</div>
      <div className="s">{item.source}</div>
    </div>
  );
}
