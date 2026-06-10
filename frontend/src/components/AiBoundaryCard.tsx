// AI boundary — which fields the AI MAY explain vs MUST NOT touch. In the
// customer product voice this lives inside the collapsed INTERNAL block (it is
// engineering/compliance truth, not a customer selling point), so it renders
// without its own card wrapper.
interface Props {
  allowed: string[];
  forbidden: string[];
  allowedTitle: string;
  forbiddenTitle: string;
}

export function AiBoundaryCard({ allowed, forbidden, allowedTitle, forbiddenTitle }: Props) {
  return (
    <div className="eb-boundary">
      <div className="eb-bcol allow">
        <div className="eb-btitle">✓ {allowedTitle}</div>
        {allowed.map((a, i) => <div className="eb-bitem" key={i}>{a}</div>)}
      </div>
      <div className="eb-bcol forbid">
        <div className="eb-btitle">✕ {forbiddenTitle}</div>
        {forbidden.map((a, i) => <div className="eb-bitem" key={i}>{a}</div>)}
      </div>
    </div>
  );
}
