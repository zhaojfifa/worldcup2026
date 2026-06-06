import type { WinProb } from '../types';
import { useLocale } from '../i18n/useLocale';

interface Props {
  prob: WinProb;
  homeLabel?: string;
  awayLabel?: string;
}

export function WinBar({ prob, homeLabel = '主队胜', awayLabel = '客队胜' }: Props) {
  const drawLabel = useLocale() === 'vi' ? 'Hòa' : '平局';
  return (
    <>
      <div className="winbar">
        <div className="seg" style={{ width: `${prob.home}%`, background: 'var(--green)' }}>{prob.home}%</div>
        <div className="seg" style={{ width: `${prob.draw}%`, background: 'var(--amber)' }}>{prob.draw}%</div>
        <div className="seg" style={{ width: `${prob.away}%`, background: 'var(--red)' }}>{prob.away}%</div>
      </div>
      <div className="winlabels">
        <span>🟢 {homeLabel}</span>
        <span>🟡 {drawLabel}</span>
        <span>🔴 {awayLabel}</span>
      </div>
    </>
  );
}
