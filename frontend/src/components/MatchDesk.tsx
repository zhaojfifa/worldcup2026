import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { DailyManifest, DailyFixtureRow } from '../data/dailyFixtures';

// P1.4 — Match-to-Product Orchestration: when the daily registry updates, the homepage
// immediately shows completed matches (recap desk), upcoming fixtures needing pre-match
// narrative, and an operator status line. All derived from the runtime manifest fixtures
// (works across backend/static/bundled tiers). NEVER shows a finished match as a fresh
// pre-match prediction; NEVER fabricates a recap for a no-narrative fixture.

const FINISHED = new Set(['FINISHED', 'RECAP_PENDING', 'RECAP_READY', 'ARCHIVED']);

// P1.5b — Daily Featured Copy Policy. The public homepage promises ONE featured pre-match pick
// and ONE featured public recap per day; all other matches are lightweight status only (more
// coverage happens manually inside the group). So finished fixtures split into the featured
// recap (the only recap-ready item, with a 查看复盘 button) and completed non-featured matches
// (已完赛 status, NO recap button — we do not imply a recap is being produced for them). Upcoming
// non-featured matches read 即将开赛 (NOT 待生成赛前判断 — no promise of a public pre-match page).
const L = {
  zh: { recapTitle: '今日复盘', recapEn: 'TODAY · RECAP', view: '查看复盘',
        resultTitle: '今日赛况', resultEn: 'TODAY · RESULTS', done: '已完赛',
        upTitle: '即将开赛', upEn: 'UPCOMING', upcoming: '即将开赛',
        status: '赛程已同步 · 今日复盘已就绪 · 下一场主推已就绪' },
  vi: { recapTitle: 'Phục dựng hôm nay', recapEn: 'TODAY · RECAP', view: 'Xem phục dựng',
        resultTitle: 'Kết quả hôm nay', resultEn: 'TODAY · RESULTS', done: 'Đã kết thúc',
        upTitle: 'Sắp đá', upEn: 'UPCOMING', upcoming: 'Sắp đá',
        status: 'Đã đồng bộ lịch · Phục dựng hôm nay đã sẵn sàng · Trận đáng xem tiếp theo đã sẵn sàng' },
  my: { recapTitle: 'ဒီနေ့ ပြန်သုံးသပ်ချက်', recapEn: 'TODAY · RECAP', view: 'ပြန်သုံးသပ်ချက် ကြည့်ရန်',
        resultTitle: 'ဒီနေ့ ပွဲရလဒ်များ', resultEn: 'TODAY · RESULTS', done: 'ပြီးဆုံး',
        upTitle: 'မကြာမီ ပွဲများ', upEn: 'UPCOMING', upcoming: 'မကြာမီ',
        status: 'ပွဲစဉ် sync ပြီး · ဒီနေ့ ပြန်သုံးသပ်ချက် အသင့် · နောက်အဓိကပွဲ အသင့်' },
  en: { recapTitle: "Today's recap", recapEn: 'TODAY · RECAP', view: 'View recap',
        resultTitle: "Today's results", resultEn: 'TODAY · RESULTS', done: 'Finished',
        upTitle: 'Upcoming', upEn: 'UPCOMING', upcoming: 'Upcoming',
        status: 'Fixtures synced · today’s recap ready · next featured pick ready' },
};
function loc3(loc: Locale) { return loc === 'zh' ? L.zh : loc === 'vi' ? L.vi : loc === 'my' ? L.my : L.en; }

function scoreStr(f: DailyFixtureRow): string {
  return f.scoreHome != null ? `${f.scoreHome}-${f.scoreAway}` : '';
}

/** B. Today's finished fixtures — featured recap (only recap-ready item) + completed non-featured. */
export function RecapDesk({ manifest, loc }: { manifest: DailyManifest; loc: Locale }) {
  const navigate = useNavigate();
  const C = loc3(loc);
  const finished = manifest.fixtures.filter(f => FINISHED.has(f.lifecycle_state));
  if (!finished.length) return null;
  const featured = finished.filter(f => f.recapReady && !!f.id);
  const completed = finished.filter(f => !(f.recapReady && !!f.id));
  return (
    <>
      {featured.length > 0 && (
        <>
          <div className="sec-en"><span className="zh">🔮 {C.recapTitle}</span><span className="en">{C.recapEn}</span></div>
          <div className="card md-card">
            {featured.map(f => (
              <div className="md-row" key={`${f.home}-${f.away}`}>
                <span className="md-teams">{f.home} <b className="md-score">{scoreStr(f)}</b> {f.away}</span>
                <button className="md-cta" onClick={() => navigate(`/recap/${f.id}`)}>{C.view} ▸</button>
              </div>
            ))}
          </div>
        </>
      )}
      {completed.length > 0 && (
        <>
          <div className="sec-en"><span className="zh">🗂️ {C.resultTitle}</span><span className="en">{C.resultEn}</span></div>
          <div className="card md-card">
            {completed.map(f => (
              <div className="md-row" key={`${f.home}-${f.away}`}>
                <span className="md-teams">{f.home} <b className="md-score">{scoreStr(f)}</b> {f.away}</span>
                <span className="md-chip done">{C.done}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}

/** C. Upcoming non-featured — scheduled fixtures shown as lightweight status only. */
export function UpcomingNeedsNarrative({ manifest, loc }: { manifest: DailyManifest; loc: Locale }) {
  const C = loc3(loc);
  const rows = manifest.fixtures.filter(f =>
    (f.preMatchAllowed ?? f.lifecycle_state === 'SCHEDULED') && !(f.renderable ?? false));
  if (!rows.length) return null;
  return (
    <>
      <div className="sec-en"><span className="zh">📋 {C.upTitle}</span><span className="en">{C.upEn}</span></div>
      <div className="card md-card">
        {rows.map(f => (
          <div className="md-row" key={`${f.home}-${f.away}`}>
            <span className="md-teams">{f.home} <span className="ut-vs">vs</span> {f.away}</span>
            <span className="md-chip upcoming">{C.upcoming}</span>
          </div>
        ))}
      </div>
    </>
  );
}

/** D. Operator Status Line — safe text, no source URLs, no betting wording. */
export function OperatorStatusLine({ loc }: { loc: Locale }) {
  return <div className="md-status">✅ {loc3(loc).status}</div>;
}
