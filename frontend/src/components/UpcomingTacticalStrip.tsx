import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { UPCOMING_FIXTURES } from '../data/upcomingFixtures';
import { getProductNarrative } from '../data/productNarrativeData';

// Home strip: REAL World Cup 2026 fixtures (bundled engineering facts) whose AI
// tactical-room narrative (LLM-generated, guard-passed) is ready. Section labels are
// UI chrome; the football intelligence lives behind /predict/:id.
const L10N = {
  zh: { title: 'World Cup 2026 · 真实赛程', en: 'AI TACTICAL ROOM', cta: 'AI 战术室', today: '今日开球', upcoming: '即将开球' },
  vi: { title: 'World Cup 2026 · Lịch thi đấu thật', en: 'AI TACTICAL ROOM', cta: 'Phòng chiến thuật AI', today: 'Đá hôm nay', upcoming: 'Sắp diễn ra' },
  en: { title: 'World Cup 2026 · Real fixtures', en: 'AI TACTICAL ROOM', cta: 'AI Tactical Room', today: 'Kicks off today', upcoming: 'Upcoming' },
};

function kickoffLabel(iso: string, loc: Locale): string {
  const d = new Date(iso);
  const locale = loc === 'zh' ? 'zh-CN' : loc === 'vi' ? 'vi-VN' : 'en-GB';
  return d.toLocaleString(locale, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

export function UpcomingTacticalStrip({ loc }: { loc: Locale }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? L10N.zh : loc === 'vi' ? L10N.vi : L10N.en;
  const todayIso = new Date().toISOString().slice(0, 10);
  const rows = UPCOMING_FIXTURES.filter(f => getProductNarrative(f.id, loc));
  if (!rows.length) return null;
  return (
    <>
      <div className="sec-en">
        <span className="zh">⚽ {L.title}</span>
        <span className="en">{L.en}</span>
      </div>
      <div className="card ut-card">
        {rows.map(f => {
          const isToday = f.kickoffUtc.slice(0, 10) === todayIso;
          return (
            <button className="ut-row" key={f.id} onClick={() => navigate(`/predict/${f.id}`)}>
              <div className="ut-main">
                <span className="ut-teams">{f.flagHome} {f.home} <span className="ut-vs">vs</span> {f.away} {f.flagAway}</span>
                <span className="ut-meta">{kickoffLabel(f.kickoffUtc, loc)} · {f.venue}</span>
              </div>
              <span className={`ut-chip ${isToday ? 'today' : ''}`}>{isToday ? L.today : L.upcoming}</span>
              <span className="ut-cta">{L.cta} ▸</span>
            </button>
          );
        })}
      </div>
    </>
  );
}
