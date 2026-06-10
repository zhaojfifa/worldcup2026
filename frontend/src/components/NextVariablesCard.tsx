import type { NextVariable } from '../data/evidenceData';

// Forward-framed "what the next model still needs to watch" — replaces the cold
// "missing data" card. The honest raw gaps (injuries unresolved / xG not
// ingested) are retained in the collapsed internal block, not shown here.
export function NextVariablesCard({ items }: { items: NextVariable[] }) {
  return (
    <div className="card eb-next">
      {items.map((v, i) => (
        <div className="eb-next-row" key={i}>
          <div className="eb-next-name">🎯 {v.name}</div>
          <div className="eb-next-note">{v.note}</div>
        </div>
      ))}
    </div>
  );
}
