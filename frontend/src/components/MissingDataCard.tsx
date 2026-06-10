// Honest data-gap card — what the model could NOT see (injuries P0 / xG / form).
// Never inferred away; gaps are stated, never "no injuries".
export function MissingDataCard({ items }: { items: string[] }) {
  return (
    <div className="card eb-missing">
      {items.map((it, i) => (
        <div className="eb-miss-row" key={i}>⚠ {it}</div>
      ))}
    </div>
  );
}
