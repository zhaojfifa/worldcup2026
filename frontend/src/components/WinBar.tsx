import type { WinProb } from '../types';

interface Props {
  prob: WinProb;
  homeLabel?: string;
  awayLabel?: string;
}

export function WinBar({ prob, homeLabel = '主队胜', awayLabel = '客队胜' }: Props) {
  return (
    <>
      <div className="winbar">
        <div className="seg" style={{ width: `${prob.home}%`, background: 'var(--green)' }}>{prob.home}%</div>
        <div className="seg" style={{ width: `${prob.draw}%`, background: 'var(--amber)' }}>{prob.draw}%</div>
        <div className="seg" style={{ width: `${prob.away}%`, background: 'var(--red)' }}>{prob.away}%</div>
      </div>
      <div className="winlabels">
        <span>🟢 {homeLabel}</span>
        <span>🟡 平局</span>
        <span>🔴 {awayLabel}</span>
      </div>
    </>
  );
}
