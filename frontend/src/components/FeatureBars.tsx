import type { FeatureFactor } from '../types';

export function FeatureBars({ features }: { features: FeatureFactor[] }) {
  const max = Math.max(...features.map(f => Math.abs(f.value)));
  return (
    <>
      {features.map(f => {
        const pos = f.value >= 0;
        const color = pos ? 'var(--green)' : 'var(--red)';
        const w = (Math.abs(f.value) / max) * 100;
        return (
          <div className="fbar" key={f.label}>
            <div className="fbar-top">
              <span style={{ color: '#3A4A60' }}>{f.label}</span>
              <span className="b" style={{ color }}>{pos ? '+' : ''}{f.value}%</span>
            </div>
            <div className="track">
              <div className="fill" style={{ width: `${w}%`, background: color }} />
            </div>
          </div>
        );
      })}
    </>
  );
}
