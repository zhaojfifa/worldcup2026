import type { Match } from '../types';
import { useCopy } from '../i18n/dict';
import { useLocale } from '../i18n/useLocale';
import { teamLoc } from '../i18n/viMapping';
import { getWc2022Recap } from '../data/wc2022DerivedRecaps';

/**
 * Real WC2022 result recap — shown for finished matches that have a DERIVED real
 * result (Kaggle ↔ Render alignment). Displays the real score, the actual winner,
 * the AI's original lean, a favorite-failed / upset tag, and a calibration
 * conclusion. Historical recap for model calibration — NOT a current prediction.
 * Renders nothing for matches without a derived recap.
 */
export function RealResultRecap({ match }: { match: Match }) {
  const t = useCopy();
  const loc = useLocale();
  const recap = getWc2022Recap(match.id);
  if (!recap) return null;

  const home = teamLoc(match.homeTeam.name, loc);
  const away = teamLoc(match.awayTeam.name, loc);
  const winnerTeam = recap.winner === 'home' ? home : recap.winner === 'away' ? away : t.lwDrawWord;
  const favTeam = recap.aiFavorite === 'home' ? home : away;
  const conclusion = recap.conclusion[loc] ?? recap.conclusion.en ?? '';

  return (
    <div className="card accent-blue" style={{ marginTop: 14 }}>
      <div className="sec-en" style={{ marginTop: 0 }}>
        <span className="zh">🎯 {t.realResultTitle}</span>
        <span className="en">REAL RESULT</span>
      </div>

      {recap.favoriteFailed && (
        <div className="risk-tagrow" style={{ marginBottom: 10 }}>
          <span className="risk-tag">⚡ {t.tagFavoriteFailed}</span>
          <span className="risk-tag">{t.tagUpset}</span>
        </div>
      )}

      <div className="crow">
        <span className="small" style={{ color: '#3A4A60' }}>{t.realScoreLabel}</span>
        <span className="b small">{home} {recap.homeGoals}–{recap.awayGoals} {away}</span>
      </div>
      <div className="crow">
        <span className="small" style={{ color: '#3A4A60' }}>{t.actualWinnerLabel}</span>
        <span className="b small" style={{ color: 'var(--green)' }}>{winnerTeam}</span>
      </div>
      <div className="crow">
        <span className="small" style={{ color: '#3A4A60' }}>{t.aiTendencyLabel}</span>
        <span className="b small" style={{ color: 'var(--red)' }}>{favTeam} {t.winLabel} · {recap.favoriteProb}%</span>
      </div>

      <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75, marginTop: 10 }}>🧭 {conclusion}</p>
      <p className="xs sub" style={{ lineHeight: 1.7, marginTop: 8 }}>{t.calibrationNote}</p>
    </div>
  );
}
