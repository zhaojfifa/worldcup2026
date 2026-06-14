import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { selectProductLoop, type DailyManifest, type DailyFixtureRow } from '../data/dailyFixtures';
import { frozenFor } from './UpcomingTacticalStrip';

// MVP2-P2 Homepage Product Loop (Owner Harness-X brief 2026-06-14).
// The homepage IS the football-intelligence loop around ONE daily hotspot:
//   昨日热点复盘 (track result) → 今日热点预测 (today's main match) → secondary schedule
//   → other recaps → group conversion.
// The two featured slots come from the EDITORIAL slate order (selectProductLoop), NOT a
// hardcoded popularity ranking. Copy never exposes internal generation state and never
// shows a fake recap (查看复盘 only when recapReady=true).

function scoreLine(f: DailyFixtureRow): string | null {
  if (f.scoreHome == null || f.scoreAway == null) return null;
  return `${f.scoreHome} - ${f.scoreAway}`;
}
function kickoff(iso: string | null, loc: Locale): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  const locale = loc === 'zh' ? 'zh-CN' : loc === 'vi' ? 'vi-VN' : 'en-GB';
  return d.toLocaleString(locale, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

const L = {
  zh: {
    recapTitle: '🔥 昨日热点复盘', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: '这是昨日主推的热点比赛，赛后观察已开启。',
    predTitle: '🎯 今日热点预测', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: '今日主推 · 开球前判断',
    predWhy: '今日主推比赛：开球前看方向，开球前 30 分钟修正。',
    enterToday: '进入今日判断', joinLive: '加入临场情报群',
    schedTitle: '🗓️ 今日赛程', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ 其他复盘', otherEn: 'OTHER RECAPS', done: '已完赛',
    growthWhy: '想看临场 30 分钟修正和赛后观察，进群。', joinGroup: '加入情报群',
    upcoming: '即将开赛', viewRecap: '查看复盘', joinPost: '加入情报群看赛后观察',
    empty: '今日暂无可用赛程，运营同步后更新。',
  },
  vi: {
    recapTitle: '🔥 Phục dựng điểm nóng hôm qua', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: 'Đây là trận điểm nóng được chọn hôm qua; quan sát sau trận đã mở.',
    predTitle: '🎯 Dự đoán điểm nóng hôm nay', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: 'Trận chính hôm nay · nhận định trước trận',
    predWhy: 'Trận chính hôm nay: xem hướng trước trận, hiệu chỉnh 30 phút trước giờ bóng lăn.',
    enterToday: 'Vào nhận định hôm nay', joinLive: 'Vào nhóm sát giờ',
    schedTitle: '🗓️ Lịch hôm nay', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ Phục dựng khác', otherEn: 'OTHER RECAPS', done: 'Đã kết thúc',
    growthWhy: 'Muốn xem hiệu chỉnh 30 phút trước trận và quan sát sau trận, vào nhóm.', joinGroup: 'Vào nhóm',
    upcoming: 'Sắp đá', viewRecap: 'Xem phục dựng', joinPost: 'Vào nhóm xem quan sát sau trận',
    empty: 'Hôm nay chưa có lịch khả dụng; sẽ cập nhật sau khi vận hành đồng bộ.',
  },
  my: {
    recapTitle: '🔥 မနေ့ အဓိကပွဲ ပြန်သုံးသပ်', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: 'ဒါက မနေ့ ရွေးချယ်ထားသော အဓိကပွဲ; ပွဲပြီးသုံးသပ်ချက် စတင်ဖွင့်ပြီ။',
    predTitle: '🎯 ဒီနေ့ အဓိကပွဲ ခန့်မှန်း', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: 'ဒီနေ့ အဓိကပွဲ · ပွဲမစခင် အမြင်',
    predWhy: 'ဒီနေ့ အဓိကပွဲ — ပွဲမစခင် ဦးတည်ချက်၊ ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ။',
    enterToday: 'ဒီနေ့ အမြင် ဝင်ကြည့်ရန်', joinLive: 'ပွဲနီး အဖွဲ့ ဝင်ရန်',
    schedTitle: '🗓️ ဒီနေ့ ပွဲစဉ်', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ အခြား ပြန်သုံးသပ်ချက်', otherEn: 'OTHER RECAPS', done: 'ပြီးဆုံး',
    growthWhy: 'ပွဲနီး မိနစ် ၃၀ ပြန်ညှိချက်နှင့် ပွဲပြီးသုံးသပ်ချက် ကြည့်ချင်ရင် အဖွဲ့ဝင်ပါ။', joinGroup: 'အဖွဲ့ဝင်ရန်',
    upcoming: 'မကြာမီ', viewRecap: 'ပြန်သုံးသပ်ချက် ကြည့်ရန်', joinPost: 'ပွဲပြီးနောက် သုံးသပ်ချက်ကြည့်ရန် အဖွဲ့ဝင်ပါ',
    empty: 'ဒီနေ့ အသုံးပြုနိုင်သော ပွဲစဉ် မရှိသေးပါ; sync ပြီးနောက် update ပါမည်။',
  },
  en: {
    recapTitle: '🔥 Yesterday’s hotspot recap', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: 'This was yesterday’s featured hotspot match; post-match observation is open.',
    predTitle: '🎯 Today’s hotspot prediction', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: 'Today’s main match · pre-match read',
    predWhy: 'Today’s main match: direction before kickoff, re-scored 30 minutes before.',
    enterToday: 'See today’s read', joinLive: 'Join the live group',
    schedTitle: '🗓️ Today’s schedule', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ Other recaps', otherEn: 'OTHER RECAPS', done: 'Finished',
    growthWhy: 'Want the 30-minute live correction and post-match notes? Join the group.', joinGroup: 'Join the group',
    upcoming: 'Upcoming', viewRecap: 'View recap', joinPost: 'Join for post-match notes',
    empty: 'No usable fixtures today; updates after the operator syncs.',
  },
};
function loc3(loc: Locale) { return loc === 'zh' ? L.zh : loc === 'vi' ? L.vi : loc === 'my' ? L.my : L.en; }

function SecHead({ zh, en }: { zh: string; en: string }) {
  return <div className="sec-en"><span className="zh">{zh}</span><span className="en">{en}</span></div>;
}

/** Zone 2 — 昨日热点复盘 (the tracked hotspot that just finished). NEVER a fake recap:
 *  查看复盘 appears only when recapReady=true; otherwise 赛后校准中 + post-match group CTA. */
function HotspotRecap({ f, loc }: { f: DailyFixtureRow; loc: Locale }) {
  const navigate = useNavigate();
  const C = loc3(loc);
  const FZ = frozenFor(loc);
  const sc = scoreLine(f);
  const ready = !!f.recapReady && !!f.id;
  return (
    <>
      <SecHead zh={C.recapTitle} en={C.recapEn} />
      <div className="card th-hero th-frozen plp-recap">
        <div className="th-badge sc-frozen-badge">{ready ? FZ.ready : FZ.pending}</div>
        <div className="th-teams">{f.home} <span className="ut-vs">vs</span> {f.away}{sc ? `　${sc}` : ''}</div>
        <div className="th-meta">{C.recapWhy}</div>
        <div className="pp-cta-row">
          {ready && f.id && (
            <button className="recap-cta-btn" onClick={() => navigate(`/recap/${f.id}`)}>{FZ.viewRecap} ▸</button>
          )}
          <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{FZ.joinPost} ▸</button>
        </div>
      </div>
    </>
  );
}

/** Zone 3 — 今日热点预测 (today's main match). Lightweight when no full narrative exists
 *  (manual fixture, id=null) — still a first-class card, never buried in a list. */
function HotspotPrediction({ f, loc }: { f: DailyFixtureRow; loc: Locale }) {
  const navigate = useNavigate();
  const C = loc3(loc);
  const ko = kickoff(f.kickoffUtc, loc);
  const canEnter = !!f.id && (f.renderable ?? false);
  return (
    <>
      <SecHead zh={C.predTitle} en={C.predEn} />
      <div className="card th-hero plp-predict">
        <div className="th-badge">{C.predState}</div>
        <div className="th-teams">{f.home} <span className="ut-vs">vs</span> {f.away}</div>
        {ko && <div className="th-meta">{ko}</div>}
        <div className="th-meta">{C.predWhy}</div>
        <div className="pp-cta-row">
          {canEnter && (
            <button className="recap-cta-btn" onClick={() => navigate(`/predict/${f.id}`)}>{C.enterToday} ▸</button>
          )}
          <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{C.joinLive} ▸</button>
        </div>
      </div>
    </>
  );
}

/** Zone 4 — 今日赛程 (secondary schedule, lightweight status only). */
function SecondarySchedule({ rows, loc }: { rows: DailyFixtureRow[]; loc: Locale }) {
  const C = loc3(loc);
  if (!rows.length) return null;
  return (
    <>
      <SecHead zh={C.schedTitle} en={C.schedEn} />
      <div className="card ut-card">
        {rows.map(f => {
          const ko = kickoff(f.kickoffUtc, loc);
          return (
            <div className="md-row" key={f.external_game_id || `${f.home}-${f.away}`}>
              <span className="md-teams">{f.home} <span className="ut-vs">vs</span> {f.away}</span>
              {ko && <span className="md-meta">{ko}</span>}
              <span className="md-chip upcoming">{C.upcoming}</span>
            </div>
          );
        })}
      </div>
    </>
  );
}

/** Zone 5 — 其他复盘 (secondary recaps). Labeled OTHER recaps, never the today-hotspot-recap
 *  lead, always below the hotspot recap. 查看复盘 only when recapReady=true (real recap exists). */
function OtherRecaps({ rows, loc }: { rows: DailyFixtureRow[]; loc: Locale }) {
  const navigate = useNavigate();
  const C = loc3(loc);
  if (!rows.length) return null;
  return (
    <>
      <SecHead zh={C.otherTitle} en={C.otherEn} />
      <div className="card ut-card">
        {rows.map(f => {
          const sc = scoreLine(f);
          const ready = !!f.recapReady && !!f.id;
          return (
            <div className="md-row" key={f.external_game_id || `${f.home}-${f.away}`}>
              <span className="md-teams">{f.home} <span className="ut-vs">vs</span> {f.away}{sc ? `　${sc}` : ''}</span>
              {ready && f.id ? (
                <button className="md-cta" onClick={() => navigate(`/recap/${f.id}`)}>{C.viewRecap} ▸</button>
              ) : (
                <span className="md-chip done">{C.done}</span>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

/** Zone 6 — Growth conversion tied to the two featured stories (value, not money/referral). */
function GrowthConversion({ loc }: { loc: Locale }) {
  const navigate = useNavigate();
  const C = loc3(loc);
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <div className="ra-line">{C.growthWhy}</div>
      <button className="recap-cta-btn" style={{ width: '100%' }} onClick={() => navigate('/community')}>
        {C.joinGroup} ▸
      </button>
    </div>
  );
}

/** The full MVP2-P2 product loop: hotspot recap → hotspot prediction → schedule → other
 *  recaps → group CTA. Driven by the editorial slate order (selectProductLoop). */
export function HomeProductLoop({ manifest, loc }: { manifest: DailyManifest; loc: Locale }) {
  const C = loc3(loc);
  const { featuredRecap, featuredPrediction, otherRecaps, secondarySchedule } = selectProductLoop(manifest);
  if (!featuredRecap && !featuredPrediction && !otherRecaps.length && !secondarySchedule.length) {
    return <div className="card th-hero"><div className="th-badge">{C.empty}</div></div>;
  }
  return (
    <>
      {featuredRecap && <HotspotRecap f={featuredRecap} loc={loc} />}
      {featuredPrediction && <HotspotPrediction f={featuredPrediction} loc={loc} />}
      <SecondarySchedule rows={secondarySchedule} loc={loc} />
      <OtherRecaps rows={otherRecaps} loc={loc} />
      <GrowthConversion loc={loc} />
    </>
  );
}
