import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import type { DailyManifest, DailyFixtureRow } from '../data/dailyFixtures';

// P1.4 — Match-to-Product Orchestration: when the daily registry updates, the homepage
// immediately shows completed matches (recap desk), upcoming fixtures needing pre-match
// narrative, and an operator status line. All derived from the runtime manifest fixtures
// (works across backend/static/bundled tiers). NEVER shows a finished match as a fresh
// pre-match prediction; NEVER fabricates a recap for a no-narrative fixture.

const FINISHED = new Set(['FINISHED', 'RECAP_PENDING', 'RECAP_READY', 'ARCHIVED']);

const L = {
  zh: { recapTitle: '今日完赛 · 复盘台', recapEn: 'RECAP DESK', view: '查看复盘',
        pending: '复盘生成中', needs: '待生成复盘', upTitle: '即将开赛 · 待生成赛前判断',
        upEn: 'UPCOMING · NEEDS PRE-MATCH', needPre: '待生成赛前判断',
        status: '赛程已同步 · 复盘队列已更新 · 下一场赛前判断已就绪' },
  vi: { recapTitle: 'Trận kết thúc hôm nay · Bàn phục dựng', recapEn: 'RECAP DESK', view: 'Xem phục dựng',
        pending: 'Đang dựng phục dựng', needs: 'Chờ tạo phục dựng', upTitle: 'Sắp đá · Chờ tạo nhận định trước trận',
        upEn: 'UPCOMING · NEEDS PRE-MATCH', needPre: 'Chờ tạo nhận định trước trận',
        status: 'Đã đồng bộ lịch · Hàng đợi phục dựng đã cập nhật · Nhận định trận tới đã sẵn sàng' },
  my: { recapTitle: 'ဒီနေ့ ပြီးဆုံးပွဲ · Recap Desk', recapEn: 'RECAP DESK', view: 'ပြန်သုံးသပ်ချက် ကြည့်ရန်',
        pending: 'ပြန်သုံးသပ်ချက် ပြင်ဆင်နေသည်', needs: 'ပြန်သုံးသပ်ချက် ထုတ်ရန် စောင့်ဆဲ',
        upTitle: 'မကြာမီ · ပွဲကြိုအမြင် ထုတ်ရန်', upEn: 'UPCOMING · NEEDS PRE-MATCH',
        needPre: 'ပွဲကြိုအမြင် ထုတ်ရန် စောင့်ဆဲ',
        status: 'ပွဲစဉ် sync ပြီး · recap queue update ပြီး · နောက်ပွဲ ပွဲကြိုအမြင် အသင့်' },
  en: { recapTitle: "Today's finished · Recap desk", recapEn: 'RECAP DESK', view: 'View recap',
        pending: 'Recap generating', needs: 'Recap to be generated', upTitle: 'Upcoming · needs pre-match',
        upEn: 'UPCOMING · NEEDS PRE-MATCH', needPre: 'Pre-match to be generated',
        status: 'Fixtures synced · recap queue updated · next pre-match ready' },
};
function loc3(loc: Locale) { return loc === 'zh' ? L.zh : loc === 'vi' ? L.vi : loc === 'my' ? L.my : L.en; }

function scoreStr(f: DailyFixtureRow): string {
  return f.scoreHome != null ? `${f.scoreHome}-${f.scoreAway}` : '';
}

/** B. Today Completed / Recap Desk — finished fixtures with the right recap state. */
export function RecapDesk({ manifest, loc }: { manifest: DailyManifest; loc: Locale }) {
  const navigate = useNavigate();
  const C = loc3(loc);
  const finished = manifest.fixtures.filter(f => FINISHED.has(f.lifecycle_state));
  if (!finished.length) return null;
  return (
    <>
      <div className="sec-en"><span className="zh">🗂️ {C.recapTitle}</span><span className="en">{C.recapEn}</span></div>
      <div className="card md-card">
        {finished.map(f => {
          const ready = f.recapReady && !!f.id;
          const mapped = !!f.id;
          const label = ready ? null : mapped ? C.pending : C.needs;
          return (
            <div className="md-row" key={`${f.home}-${f.away}`}>
              <span className="md-teams">{f.home} <b className="md-score">{scoreStr(f)}</b> {f.away}</span>
              {ready
                ? <button className="md-cta" onClick={() => navigate(`/recap/${f.id}`)}>{C.view} ▸</button>
                : <span className={`md-chip ${mapped ? 'pending' : 'needs'}`}>{label}</span>}
            </div>
          );
        })}
      </div>
    </>
  );
}

/** C. Upcoming / Needs Pre-match — scheduled fixtures without a narrative. */
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
            <span className="md-chip needs">{C.needPre}</span>
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
