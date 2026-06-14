import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { selectProductLoop, type DailyManifest, type DailyFixtureRow } from '../data/dailyFixtures';
import { frozenFor } from './UpcomingTacticalStrip';
import { CopyLink } from './CopyLink';

// MVP2-P3 — the tactical-room route key for a fixture. Real fixtures route by numeric id;
// manual fixtures (id=null, e.g. today's hotspot before a narrative exists) route by their
// external_game_id so /predict can resolve them from the runtime manifest.
function predictKey(f: DailyFixtureRow): string {
  return f.id ?? encodeURIComponent(f.external_game_id ?? `${f.home}-${f.away}`);
}

// MVP2-P2/P3 Homepage Product Loop (Owner Harness-X brief 2026-06-14).
// The homepage IS the football-intelligence funnel around ONE daily hotspot. P3 order
// (hotspot PREDICTION first — the funnel entrance):
//   今日热点预测 (today's main match) → 昨日热点复盘 (yesterday's tracked hotspot) →
//   secondary schedule → other recaps → group conversion.
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
    predWhy: '今日主推比赛：基于数据更新 + 建模判断，开球前看方向，开球前 30 分钟修正。',
    enterToday: '进入战术室', joinLive: '加入临场情报群',
    copyShare: '复制/分享入口', copyDone: '已复制 ✓', viewObs: '查看赛后观察',
    schedTitle: '🗓️ 今日赛程', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ 其他复盘', otherEn: 'OTHER RECAPS', done: '已完赛',
    growthWhy: '想看完整临场 30 分钟修正、建模变量和赛后校准，进群。', joinGroup: '加入情报群',
    upcoming: '即将开赛', viewRecap: '查看复盘', joinPost: '加入情报群看赛后观察',
    recapFocus: '赛后校准关注',
    recapBullets: ['{home} 控制力是否低于赛前预期', '{away} 防守压缩与反击质量是否改变判断', '{score} 结果对后续走势的影响'],
    predFocus: '今日建模关注',
    predBullets: ['节奏差异：{home} 推进与 {away} 反击转换', '风险变量：首发边路配置与中场压迫强度', '临场修正：开球前 30 分钟看首发、阵型与热度变化'],
    thirtyMin: '开球前 30 分钟重点看：首发阵容、阵型变化、核心球员状态、临场热度、风险方向。',
    empty: '今日暂无可用赛程，运营同步后更新。',
  },
  vi: {
    recapTitle: '🔥 Phục dựng điểm nóng hôm qua', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: 'Đây là trận điểm nóng được chọn hôm qua; quan sát sau trận đã mở.',
    predTitle: '🎯 Dự đoán điểm nóng hôm nay', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: 'Trận chính hôm nay · nhận định trước trận',
    predWhy: 'Trận chính hôm nay: dựa trên dữ liệu cập nhật + phân tích, xem hướng trước trận, hiệu chỉnh 30 phút trước giờ bóng lăn.',
    enterToday: 'Vào phòng chiến thuật', joinLive: 'Vào nhóm sát giờ',
    copyShare: 'Sao chép / chia sẻ', copyDone: 'Đã sao chép ✓', viewObs: 'Xem quan sát sau trận',
    schedTitle: '🗓️ Lịch hôm nay', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ Phục dựng khác', otherEn: 'OTHER RECAPS', done: 'Đã kết thúc',
    growthWhy: 'Muốn xem đầy đủ hiệu chỉnh 30 phút, biến số phân tích và hiệu chỉnh sau trận, vào nhóm.', joinGroup: 'Vào nhóm',
    upcoming: 'Sắp đá', viewRecap: 'Xem phục dựng', joinPost: 'Vào nhóm xem quan sát sau trận',
    recapFocus: 'Tiêu điểm hiệu chỉnh sau trận',
    recapBullets: ['{home}: khả năng kiểm soát có thấp hơn kỳ vọng trước trận', '{away}: nén phòng ngự và chất lượng phản công có đổi nhận định', '{score}: ảnh hưởng tới cục diện bảng đấu'],
    predFocus: 'Tiêu điểm phân tích hôm nay',
    predBullets: ['Khác biệt nhịp độ: {home} lên bóng ổn định, {away} chuyển đổi phản công nhanh', 'Biến số rủi ro: cấu hình hai biên đá chính và cường độ pressing giữa sân', 'Hiệu chỉnh sát giờ: 30 phút trước bóng lăn xem đội hình, sơ đồ, độ nóng'],
    thirtyMin: 'Sát giờ 30 phút tập trung: đội hình ra sân, thay đổi sơ đồ, phong độ trụ cột, độ nóng, hướng rủi ro.',
    empty: 'Hôm nay chưa có lịch khả dụng; sẽ cập nhật sau khi vận hành đồng bộ.',
  },
  my: {
    recapTitle: '🔥 မနေ့ အဓိကပွဲ ပြန်သုံးသပ်', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: 'ဒါက မနေ့ ရွေးချယ်ထားသော အဓိကပွဲ; ပွဲပြီးသုံးသပ်ချက် စတင်ဖွင့်ပြီ။',
    predTitle: '🎯 ဒီနေ့ အဓိကပွဲ ခန့်မှန်း', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: 'ဒီနေ့ အဓိကပွဲ · ပွဲမစခင် အမြင်',
    predWhy: 'ဒီနေ့ အဓိကပွဲ — data update + model အမြင်ဖြင့်၊ ပွဲမစခင် ဦးတည်ချက်၊ ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ။',
    enterToday: 'နည်းဗျူဟာခန်း ဝင်ရန်', joinLive: 'ပွဲနီး အဖွဲ့ ဝင်ရန်',
    copyShare: 'Link ကူး / share', copyDone: 'ကူးပြီး ✓', viewObs: 'ပွဲပြီး စောင့်ကြည့်ချက် ကြည့်ရန်',
    schedTitle: '🗓️ ဒီနေ့ ပွဲစဉ်', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ အခြား ပြန်သုံးသပ်ချက်', otherEn: 'OTHER RECAPS', done: 'ပြီးဆုံး',
    growthWhy: 'ပွဲနီး မိနစ် ၃၀ ပြန်ညှိ၊ ပိုင်းခြားသုံးသပ် variable နှင့် ပွဲပြီးပြန်ညှိချက် အပြည့်အစုံ ကြည့်ချင်ရင် အဖွဲ့ဝင်ပါ။', joinGroup: 'အဖွဲ့ဝင်ရန်',
    upcoming: 'မကြာမီ', viewRecap: 'ပြန်သုံးသပ်ချက် ကြည့်ရန်', joinPost: 'ပွဲပြီးနောက် သုံးသပ်ချက်ကြည့်ရန် အဖွဲ့ဝင်ပါ',
    recapFocus: 'ပွဲပြီး ပြန်ညှိ အာရုံစိုက်ချက်',
    recapBullets: ['{home} ၏ ထိန်းချုပ်မှု ပွဲကြိုမျှော်မှန်းချက်အောက် ရှိမရှိ', '{away} ၏ ခံစစ်ဖိအားနှင့် ပြန်တိုက်အရည်အသွေး အမြင်ပြောင်းစေမလား', '{score} ရလဒ်က နောက်ပိုင်း အုပ်စုအခြေအနေအပေါ် သက်ရောက်မှု'],
    predFocus: 'ဒီနေ့ ပိုင်းခြားသုံးသပ် အာရုံစိုက်ချက်',
    predBullets: ['အရှိန်ကွာခြားချက်: {home} တည်ငြိမ်စွာ တိုးတက်၊ {away} ပြန်တိုက် မြန်ဆန်', 'အန္တရာယ် variable: ပွဲထွက်အစီအစဉ်နှင့် အလယ်တန်း ဖိအား', 'ပွဲနီးပြင်ဆင်ချက်: ပွဲမစခင် မိနစ် ၃၀ — ပွဲထွက်၊ ပုံစံ၊ အပူချိန်'],
    thirtyMin: 'ပွဲမစခင် မိနစ် ၃၀ အဓိကကြည့်ရန်: ပွဲထွက်အစီအစဉ်၊ ပုံစံပြောင်းလဲမှု၊ အဓိကကစားသမား အခြေအနေ၊ အပူချိန်၊ အန္တရာယ်ဦးတည်ချက်။',
    empty: 'ဒီနေ့ အသုံးပြုနိုင်သော ပွဲစဉ် မရှိသေးပါ; sync ပြီးနောက် update ပါမည်။',
  },
  en: {
    recapTitle: '🔥 Yesterday’s hotspot recap', recapEn: 'YESTERDAY · HOTSPOT RECAP',
    recapWhy: 'This was yesterday’s featured hotspot match; post-match observation is open.',
    predTitle: '🎯 Today’s hotspot prediction', predEn: 'TODAY · HOTSPOT PREDICTION',
    predState: 'Today’s main match · pre-match read',
    predWhy: 'Today’s main match: data update + model read — direction before kickoff, re-scored 30 minutes before.',
    enterToday: 'Enter tactical room', joinLive: 'Join the live group',
    copyShare: 'Copy / share link', copyDone: 'Copied ✓', viewObs: 'View post-match observation',
    schedTitle: '🗓️ Today’s schedule', schedEn: 'TODAY · SCHEDULE',
    otherTitle: '🗂️ Other recaps', otherEn: 'OTHER RECAPS', done: 'Finished',
    growthWhy: 'Want the full 30-minute live correction, modeling variables and post-match calibration? Join the group.', joinGroup: 'Join the group',
    upcoming: 'Upcoming', viewRecap: 'View recap', joinPost: 'Join for post-match notes',
    recapFocus: 'Post-match calibration focus',
    recapBullets: ['{home}: was control below the pre-match expectation', '{away}: did defensive compression and counter quality change the call', '{score}: effect on the group outlook'],
    predFocus: 'Modeling focus',
    predBullets: ['Tempo gap: {home} steady build-up vs {away} fast counter-transition', 'Risk variables: starting wide setup and midfield pressing intensity', 'Live correction: 30 minutes before kickoff — XI, formation, heat'],
    thirtyMin: 'In the 30 minutes before kickoff, watch: starting XI, formation changes, key-player status, live heat, risk direction.',
    empty: 'No usable fixtures today; updates after the operator syncs.',
  },
};
function loc3(loc: Locale) { return loc === 'zh' ? L.zh : loc === 'vi' ? L.vi : loc === 'my' ? L.my : L.en; }

function SecHead({ zh, en }: { zh: string; en: string }) {
  return <div className="sec-en"><span className="zh">{zh}</span><span className="en">{en}</span></div>;
}

/** Interpolate {home}/{away}/{score} into an analysis FRAME. Frames are generic structure
 *  (engineering's "stage"); team names come from the manifest. Question-framed — never a
 *  fabricated stat, fake certainty, or invented score. */
function interp(tpl: string, home: string, away: string, score: string | null): string {
  return tpl.replace('{home}', home).replace('{away}', away).replace('{score}', score ?? '');
}

function FocusBlock({ title, bullets, home, away, score, extra }:
  { title: string; bullets: string[]; home: string; away: string; score: string | null; extra?: string }) {
  return (
    <div className="plp-focus">
      <div className="plp-focus-title">{title}</div>
      <ul className="plp-bullets">
        {bullets.map((b, i) => <li key={i}>{interp(b, home, away, score)}</li>)}
      </ul>
      {extra && <div className="plp-30min">{extra}</div>}
    </div>
  );
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
        <FocusBlock title={C.recapFocus} bullets={C.recapBullets} home={f.home} away={f.away} score={sc} />
        <div className="pp-cta-row">
          {/* recapReady=true → 查看复盘 (real recap); recapReady=false but tracked → 查看赛后观察
              (safe observation page, never a fake recap). Both land on /recap/:id. */}
          {f.id && (
            <button className="recap-cta-btn" onClick={() => navigate(`/recap/${f.id}`)}>
              {ready ? FZ.viewRecap : C.viewObs} ▸
            </button>
          )}
          <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{FZ.joinPost} ▸</button>
        </div>
        {f.id && (
          <div className="share-block">
            <CopyLink path={`/recap/${f.id}`} loc={loc} label={C.copyShare} doneLabel={C.copyDone} />
          </div>
        )}
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
  // The today-hotspot tactical room is ALWAYS reachable (Owner P0-2: never bury it). Real
  // fixtures open their narrative; a manual fixture opens the /predict fallback tactical room.
  const key = predictKey(f);
  return (
    <>
      <SecHead zh={C.predTitle} en={C.predEn} />
      <div className="card th-hero plp-predict">
        <div className="th-badge">{C.predState}</div>
        <div className="th-teams">{f.home} <span className="ut-vs">vs</span> {f.away}</div>
        {ko && <div className="th-meta">{ko}</div>}
        <div className="th-meta">{C.predWhy}</div>
        <FocusBlock title={C.predFocus} bullets={C.predBullets} home={f.home} away={f.away} score={null} extra={C.thirtyMin} />
        <div className="pp-cta-row">
          <button className="recap-cta-btn" onClick={() => navigate(`/predict/${key}`)}>{C.enterToday} ▸</button>
          <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{C.joinLive} ▸</button>
        </div>
        <div className="share-block">
          <CopyLink path={`/predict/${key}`} loc={loc} label={C.copyShare} doneLabel={C.copyDone} />
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
  // MVP2-P3 (Owner verdict): hotspot PREDICTION is always first — the homepage is the funnel
  // entrance. Yesterday's recap is second (trust receipt), then secondary schedule / other recaps.
  return (
    <>
      {featuredPrediction && <HotspotPrediction f={featuredPrediction} loc={loc} />}
      {featuredRecap && <HotspotRecap f={featuredRecap} loc={loc} />}
      <SecondarySchedule rows={secondarySchedule} loc={loc} />
      <OtherRecaps rows={otherRecaps} loc={loc} />
      <GrowthConversion loc={loc} />
    </>
  );
}
