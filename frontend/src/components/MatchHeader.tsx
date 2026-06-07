import type { Match } from '../types';
import { useLocale } from '../i18n/useLocale';
import { teamLoc } from '../i18n/viMapping';

function fmt(iso: string) {
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${mm}-${dd} ${hh}:${mi}`;
}

export function MatchHeader({ match }: { match: Match }) {
  const loc = useLocale();
  const tn = (name: string) => teamLoc(name, loc);
  return (
    <div className="mh">
      <div className="team">
        <div className="flag">{match.homeTeam.flag}</div>
        <div className="name">{tn(match.homeTeam.name)}</div>
      </div>
      <div className="team">
        <div className="vs">VS</div>
        <div className="time">{fmt(match.kickoffTime)}</div>
      </div>
      <div className="team">
        <div className="flag">{match.awayTeam.flag}</div>
        <div className="name">{tn(match.awayTeam.name)}</div>
      </div>
    </div>
  );
}
