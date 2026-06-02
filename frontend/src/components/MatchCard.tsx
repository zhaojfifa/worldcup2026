import type { Match } from '../types';
import { WinBar } from './WinBar';

const TAG_LABELS: Record<string, string> = {
  focus: '🏆 焦点战',
  upset: '🔥 爆冷预警',
  live:  '⚡ 临场监听',
  'high-conf': '🎯 高信心',
};

const RISK_LABELS = { low: '低风险', medium: '中风险', high: '高风险' };

function fmtTime(iso: string) {
  const d = new Date(iso);
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${hh}:${mi}`;
}

function fmtDate(iso: string) {
  const d = new Date(iso);
  return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

interface Props {
  match: Match;
  onClick: () => void;
}

/**
 * LiveScore-style AI match card.
 * Renders the same shape for focus and regular matches; the `is-focus`
 * modifier adds the gold accent bar.
 */
export function MatchCard({ match, onClick }: Props) {
  const tag = match.tag ?? 'focus';
  const isFocus = tag === 'focus';

  return (
    <div className={`mcard ${isFocus ? 'is-focus' : ''}`} onClick={onClick} role="button">
      {/* Model label + update time */}
      <div className="mcard-top">
        <span className="mono-label">AI PRE-MATCH MODEL</span>
        <span className="upd-label">
          <span className="sync-dot" />UPDATED {fmtTime(match.updatedAt)}
        </span>
      </div>

      {/* Tags */}
      <div className="mcard-tags">
        <span className={`tag-chip ${tag}`}>{TAG_LABELS[tag]}</span>
        <span className={`risk-chip ${match.riskLevel}`}>{RISK_LABELS[match.riskLevel]}</span>
        {tag === 'live' && <span className="tag-chip live">● LIVE 临场</span>}
      </div>

      {/* Teams */}
      <div className="mh">
        <div className="team">
          <div className="flag">{match.homeTeam.flag}</div>
          <div className="name">{match.homeTeam.name}</div>
        </div>
        <div className="team">
          <div className="vs">VS</div>
          <div className="time">{fmtDate(match.kickoffTime)} {fmtTime(match.kickoffTime)}</div>
        </div>
        <div className="team">
          <div className="flag">{match.awayTeam.flag}</div>
          <div className="name">{match.awayTeam.name}</div>
        </div>
      </div>

      {/* Win probability bar */}
      <div className="mt8">
        <WinBar
          prob={match.winProb}
          homeLabel={`${match.homeTeam.name}胜`}
          awayLabel={`${match.awayTeam.name}胜`}
        />
      </div>

      {/* Confidence index + recommended score */}
      <div className="mcard-meta">
        <div className="conf-block">
          <div className="conf-head">
            <span className="lbl">信心指数</span>
            <span className="num">{Math.round(match.confidence)}</span>
          </div>
          <div className="conf-track">
            <div className="conf-fill" style={{ width: `${match.confidence}%` }} />
          </div>
        </div>
        {match.recommendedScore && (
          <div className="score-block">
            <div className="lbl">AI 推荐比分</div>
            <div className="val">{match.recommendedScore}</div>
          </div>
        )}
      </div>

      {/* CTA */}
      <div className="mcard-cta">🔒 解锁 AI 战术底牌 →</div>
    </div>
  );
}
