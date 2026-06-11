import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { UPCOMING_FIXTURES, getUpcomingFixture } from '../data/upcomingFixtures';
import { getProductNarrative } from '../data/productNarrativeData';
import { getRescore } from '../data/rescoreData';

// Home entry for REAL World Cup 2026 fixtures (bundled engineering facts) whose
// persona tactical-room narrative (LLM-generated, guard-passed) is ready.
// Persona: zh 中文先知 · vi Tiên Tri Bóng Đá (Giành Cup, engine ScoutScore).
// Section labels/buttons are UI chrome; the football intelligence lives in /predict/:id.
const L10N = {
  zh: { title: 'World Cup 2026 · 真实赛程', en: 'TACTICAL ROOM', cta: '俅哥战术室', today: '今日开球', upcoming: '即将开球' },
  vi: { title: 'World Cup 2026 · Lịch thi đấu thật', en: 'TACTICAL ROOM', cta: 'Phòng chiến thuật Tiên Tri', today: 'Đá hôm nay', upcoming: 'Sắp diễn ra' },
  en: { title: 'World Cup 2026 · Real fixtures', en: 'TACTICAL ROOM', cta: 'Giành Cup Tactical Room', today: 'Kicks off today', upcoming: 'Upcoming' },
};

const HERO = {
  zh: { badge: '⚡ World Cup 2026 揭幕窗口 · 真实比赛', enter: '进入俅哥战术室', join: '加入赛前情报群',
        status: '🔮 俅哥已生成今日赛前判断 · 临场 30 分钟将重新计算 · 数据同步 ' },
  vi: { badge: '⚡ World Cup 2026 · Trận thật', enter: 'Vào phòng chiến thuật Tiên Tri', join: 'Vào nhóm tình báo trước trận',
        status: '🔮 Tiên Tri Bóng Đá đã có nhận định hôm nay · Tính lại 30 phút trước giờ bóng lăn · Đồng bộ ' },
  en: { badge: '⚡ World Cup 2026 · Real fixture', enter: 'Open the Tactical Room', join: 'Join the pre-match group',
        status: '🔮 Pre-match view ready · Re-scored 30 minutes before kickoff · Synced ' },
};

function heroFor(loc: Locale) {
  return loc === 'zh' ? HERO.zh : loc === 'vi' ? HERO.vi : HERO.en;
}

function kickoffLabel(iso: string, loc: Locale): string {
  const d = new Date(iso);
  const locale = loc === 'zh' ? 'zh-CN' : loc === 'vi' ? 'vi-VN' : 'en-GB';
  return d.toLocaleString(locale, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

/** Persona status strip (Owner hierarchy item 1). syncTime is the app's data-sync stamp. */
export function TrialStatusStrip({ loc, syncTime }: { loc: Locale; syncTime: string }) {
  const H = heroFor(loc);
  return <div className="trial-status">{H.status}{syncTime}</div>;
}

/** Main trial entry card (Owner hierarchy item 2): the selected real fixture. */
export function TrialHeroCard({ loc, fixtureId }: { loc: Locale; fixtureId: string }) {
  const navigate = useNavigate();
  const H = heroFor(loc);
  const fx = getUpcomingFixture(fixtureId);
  if (!fx) return null;
  const n = getProductNarrative(fixtureId, loc);
  return (
    <div className="card th-hero">
      <div className="th-badge">{H.badge}</div>
      <div className="th-teams">{fx.flagHome} {fx.home} <span className="ut-vs">vs</span> {fx.away} {fx.flagAway}</div>
      <div className="th-meta">{kickoffLabel(fx.kickoffUtc, loc)} · {fx.venue} ({fx.city}) · {fx.round}</div>
      {n && <div className="th-hook">“{n.short_title}”</div>}
      <div className="pp-cta-row">
        <button className="recap-cta-btn" onClick={() => navigate(`/predict/${fixtureId}`)}>{H.enter} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{H.join} ▸</button>
      </div>
    </div>
  );
}

/** Secondary upcoming fixtures (Owner hierarchy item 3). */
export function UpcomingTacticalStrip({ loc, excludeId }: { loc: Locale; excludeId?: string }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? L10N.zh : loc === 'vi' ? L10N.vi : L10N.en;
  const todayIso = new Date().toISOString().slice(0, 10);
  const rows = UPCOMING_FIXTURES.filter(f => f.id !== excludeId && getProductNarrative(f.id, loc));
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

// ── 俅哥今日看点 (QiuGe sprint, Task B): ONLY current trial-operation hooks ──
// Hooks are LLM-written (narrative short_title / rescore public_teaser /
// rescore group_join_hook) — never hand-written. Historical recap stays in the
// lower calibration section only. No interaction counts (none are real).
const HOT = {
  zh: { title: '俅哥今日看点', en: 'HOT READS', room: '战术室', rescore: '临场修正', group: '入群' },
  vi: { title: 'Điểm nóng hôm nay của Tiên Tri', en: 'HOT READS', room: 'Phòng chiến thuật', rescore: 'Hiệu chỉnh sát giờ', group: 'Vào nhóm' },
  en: { title: "Today's hot reads", en: 'HOT READS', room: 'Tactical room', rescore: '30-min re-score', group: 'Join' },
};

export function HotTopicsSection({ loc }: { loc: Locale }) {
  const navigate = useNavigate();
  const H = loc === 'zh' ? HOT.zh : loc === 'vi' ? HOT.vi : HOT.en;
  const n69 = getProductNarrative('1489369', loc);
  const n71 = getProductNarrative('1489371', loc);
  const rs = getRescore('1489369', loc);
  const rows = [
    n69 && { key: 'room69', hook: n69.short_title, to: '/predict/1489369', tag: H.room, hot: true },
    n71 && { key: 'room71', hook: n71.short_title, to: '/predict/1489371', tag: H.room, hot: true },
    rs && { key: 'rescore', hook: rs.public_teaser, to: '/predict/1489369#rescore', tag: H.rescore, hot: false },
    rs && { key: 'join', hook: rs.group_join_hook, to: '/community', tag: H.group, hot: false },
  ].filter(Boolean) as { key: string; hook: string; to: string; tag: string; hot: boolean }[];
  if (!rows.length) return null;
  return (
    <>
      <div className="sec-en">
        <span className="zh">🔥 {H.title}</span>
        <span className="en">{H.en}</span>
      </div>
      <div className="card ut-card">
        {rows.map(e => (
          <button className="ut-row" key={e.key} onClick={() => navigate(e.to)}>
            <div className="ut-main">
              <span className="ut-teams pp-hot-line">{e.hook}</span>
            </div>
            <span className={`ut-chip ${e.hot ? 'today' : ''}`}>{e.tag}</span>
            <span className="pp-arrow">▸</span>
          </button>
        ))}
      </div>
    </>
  );
}
