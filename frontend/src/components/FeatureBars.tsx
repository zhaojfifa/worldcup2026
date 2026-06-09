import type { FeatureFactor } from '../types';
import { useLocale } from '../i18n/useLocale';
import { featureLabelLoc, factorSourceLoc, factorInterpretationLoc } from '../i18n/viMapping';
import { useCopy } from '../i18n/dict';

export function FeatureBars({ features }: { features: FeatureFactor[] }) {
  const loc = useLocale();
  const t = useCopy();
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
              <span style={{ color: '#3A4A60' }}>{featureLabelLoc(f.label, loc)}</span>
              <span className="b" style={{ color }}>{pos ? '+' : ''}{f.value}%</span>
            </div>
            <div className="track">
              <div className="fill" style={{ width: `${w}%`, background: color }} />
            </div>
            <div className="fbar-meta">
              <span className="fbar-src">{t.factorSourceWord}: {factorSourceLoc(f.label, loc)}</span>
            </div>
            <div className="fbar-interp">{factorInterpretationLoc(f.label, loc)}</div>
          </div>
        );
      })}
    </>
  );
}
