import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useLocale, type Locale } from '../i18n/useLocale';
import { getProductNarrative, predictSlugToId } from '../data/productNarrativeData';
import { getUpcomingFixture } from '../data/upcomingFixtures';
import { ProductPredictView } from '../components/ProductProofViews';
import { StrongCallCard } from '../components/StrongSignalCard';
import { DetailShareRow } from '../components/DetailShareRow';
import { fetchDailyManifest, type DailyFixtureRow } from '../data/dailyFixtures';
import { fixtureFreshness } from '../lib/freshness';

// MVP2-P3 — lightweight tactical-room fallback for today's hotspot when no full LLM narrative
// exists yet (manual fixture, id=null). Engineering supplies the STAGE (question-framed analysis
// /risk variables + the 30-minute checklist); no invented score, no fake certainty, no data source.
const FALLBACK = {
  zh: { banner: '⚡ 今日热点预测 · 战术室', state: '今日主推 · 开球前判断',
        why: '今日主推比赛：基于数据更新 + 大模型判断，开球前看方向，开球前 30 分钟修正。',
        focus: '今日建模关注', risk: '风险变量', thirtyTitle: '开球前 30 分钟修正',
        bullets: ['节奏差异：{home} 推进与 {away} 反击转换', '中场与边路：首发配置与压迫强度如何影响走势'],
        risks: ['首发与阵型：开球前公布的首发是否改变方向', '核心球员状态与临场热度'],
        thirty: '开球前 30 分钟重点看：首发阵容、阵型变化、核心球员状态、临场热度、风险方向。',
        loading: '正在载入今日热点…', kickoffTba: '开球时间待运营确认' },
  vi: { banner: '⚡ Dự đoán điểm nóng hôm nay · Phòng chiến thuật', state: 'Trận chính hôm nay · nhận định trước trận',
        why: 'Trận chính hôm nay: dựa trên dữ liệu cập nhật + nhận định mô hình, xem hướng trước trận, hiệu chỉnh 30 phút trước giờ bóng lăn.',
        focus: 'Tiêu điểm phân tích hôm nay', risk: 'Biến số rủi ro', thirtyTitle: 'Hiệu chỉnh 30 phút trước trận',
        bullets: ['Khác biệt nhịp độ: {home} lên bóng và {away} chuyển đổi phản công', 'Giữa sân & hai biên: cấu hình đá chính và cường độ pressing'],
        risks: ['Đội hình & sơ đồ: đội hình công bố có đổi hướng không', 'Phong độ trụ cột và độ nóng sát giờ'],
        thirty: 'Sát giờ 30 phút tập trung: đội hình ra sân, thay đổi sơ đồ, phong độ trụ cột, độ nóng, hướng rủi ro.',
        loading: 'Đang tải điểm nóng hôm nay…', kickoffTba: 'Giờ bóng lăn chờ vận hành xác nhận' },
  my: { banner: '⚡ ဒီနေ့ အဓိကပွဲ ခန့်မှန်း · နည်းဗျူဟာခန်း', state: 'ဒီနေ့ အဓိကပွဲ · ပွဲမစခင် အမြင်',
        why: 'ဒီနေ့ အဓိကပွဲ — data update + model အမြင်ဖြင့်၊ ပွဲမစခင် ဦးတည်ချက်၊ ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ။',
        focus: 'ဒီနေ့ ပိုင်းခြားသုံးသပ် အာရုံစိုက်ချက်', risk: 'အန္တရာယ် variable', thirtyTitle: 'ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ',
        bullets: ['အရှိန်ကွာခြားချက်: {home} တိုးတက်မှုနှင့် {away} ပြန်တိုက်', 'အလယ်တန်းနှင့် အနား: ပွဲထွက်နှင့် ဖိအား'],
        risks: ['ပွဲထွက်နှင့် ပုံစံ: ကြေညာသော ပွဲထွက်က ဦးတည်ချက် ပြောင်းမလား', 'အဓိကကစားသမား အခြေအနေနှင့် အပူချိန်'],
        thirty: 'ပွဲမစခင် မိနစ် ၃၀ အဓိကကြည့်ရန်: ပွဲထွက်၊ ပုံစံ၊ အဓိကကစားသမား၊ အပူချိန်၊ အန္တရာယ်ဦးတည်ချက်။',
        loading: 'ဒီနေ့ အဓိကပွဲ ဖွင့်နေသည်…', kickoffTba: 'ပွဲစချိန် operator အတည်ပြုရန်' },
  en: { banner: '⚡ Today’s hotspot prediction · tactical room', state: 'Today’s main match · pre-match read',
        why: 'Today’s main match: data update + model read — direction before kickoff, re-scored 30 minutes before.',
        focus: 'Modeling focus', risk: 'Risk variables', thirtyTitle: '30-minute pre-match correction',
        bullets: ['Tempo gap: {home} build-up vs {away} counter-transition', 'Midfield & wings: starting setup and pressing intensity'],
        risks: ['XI & formation: does the announced lineup change the call', 'Key-player status and live heat'],
        thirty: 'In the 30 minutes before kickoff, watch: starting XI, formation changes, key-player status, live heat, risk direction.',
        loading: 'Loading today’s hotspot…', kickoffTba: 'Kickoff time pending operator confirmation' },
};
function fbFor(loc: Locale) { return loc === 'zh' ? FALLBACK.zh : loc === 'vi' ? FALLBACK.vi : loc === 'my' ? FALLBACK.my : FALLBACK.en; }
function interp(tpl: string, home: string, away: string) { return tpl.replace('{home}', home).replace('{away}', away); }

// Pre-match modeling product page (/predict/:slug). Two flavours, same LLM-narrative
// main view: hypothetical 2026 sample (slug 2026-brazil-argentina) and REAL scheduled
// fixtures (numeric ids — the persona tactical room). Engineering renders the stage
// only; customer langs zh/vi/my; en shows a neutral placeholder.
const BARS = {
  zh: { back: '赛前建模', backReal: '俅哥战术室', banner: '🔮 2026 World Cup · 赛前建模样例',
        bannerReal: '⚡ World Cup 2026 · 俅哥战术室（赛前判断）', none: '该样例暂未提供此语言版本', kickoff: '开球', venue: '球场' },
  vi: { back: 'Mô hình hóa trước trận', backReal: 'Phòng chiến thuật Tiên Tri Bóng Đá', banner: '🔮 World Cup 2026 · Mẫu mô hình hóa trước trận',
        bannerReal: '⚡ World Cup 2026 · Phòng chiến thuật Tiên Tri Bóng Đá', none: 'Mẫu này chưa có bản ngôn ngữ hiện tại', kickoff: 'Giờ bóng lăn', venue: 'Sân' },
  my: { back: 'ပွဲကြို သုံးသပ်ချက်', backReal: 'Football Oracle နည်းဗျူဟာခန်း', banner: '🔮 2026 World Cup · ပွဲကြို နမူနာ',
        bannerReal: '⚡ World Cup 2026 · Football Oracle နည်းဗျူဟာခန်း (ပွဲကြို)', none: 'ဤနမူနာအတွက် ဘာသာပြန် မရသေးပါ', kickoff: 'ပွဲစချိန်', venue: 'ကွင်း' },
  en: { back: 'Pre-match modeling', backReal: 'Giành Cup Tactical Room', banner: '🔮 2026 World Cup · pre-match modeling sample',
        bannerReal: '⚡ World Cup 2026 · Giành Cup Tactical Room (pre-match)', none: 'This sample is not available in the current language yet', kickoff: 'Kickoff', venue: 'Venue' },
};

function kickoffLocal(iso: string, loc: string): string {
  const d = new Date(iso);
  // 'my' keeps Latin digits/format (density profile keeps concise English terms).
  const locale = loc === 'zh' ? 'zh-CN' : loc === 'vi' ? 'vi-VN' : 'en-GB';
  return d.toLocaleString(locale, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

export function PredictPage() {
  const navigate = useNavigate();
  const loc = useLocale();
  const { slug = '2026-brazil-argentina' } = useParams();
  const [search] = useSearchParams();
  const B = loc === 'zh' ? BARS.zh : loc === 'vi' ? BARS.vi : loc === 'my' ? BARS.my : BARS.en;
  const id = predictSlugToId(slug);
  const n = getProductNarrative(id, loc);
  const fx = getUpcomingFixture(id);
  // No narrative AND no bundled fixture → resolve the manual hotspot from the runtime manifest
  // (today's prediction may have no LLM narrative yet but must still open a tactical room).
  const needsFallback = !n && !fx;
  const [manualFx, setManualFx] = useState<DailyFixtureRow | null | undefined>(undefined);
  useEffect(() => {
    if (!needsFallback) return;
    let alive = true;
    fetchDailyManifest().then(r => {
      if (!alive) return;
      const row = r.manifest.fixtures.find(f => f.id === slug || f.external_game_id === slug) ?? null;
      setManualFx(row);
    }).catch(() => { if (alive) setManualFx(null); });
    return () => { alive = false; };
  }, [needsFallback, slug]);
  const isReal = n?.fixture_basis === 'real_scheduled' || !!fx;
  const opsOpen = search.get('ops') === '1'; // QA/operator helper: open the internal fold for screenshots
  const { hash } = useLocation();
  // Post-match: the bundled narrative for this fixture is now the real recap —
  // the pre-match tactical room is over, so the recap page is the only honest surface.
  const isRecap = n?.mode === 'real_recap';
  // P1.2b runtime guard: even before the recap is bundled, once kickoff has passed the
  // page must NOT look like a fresh pre-match prediction (stale status defeated).
  const fr = fixtureFreshness(fx?.kickoffUtc ?? null, n?.mode);
  const frozen = isReal && !isRecap && !fr.preMatchAllowed;
  useEffect(() => {
    if (isRecap) navigate(`/recap/${id}`, { replace: true });
  }, [isRecap, id, navigate]);
  useEffect(() => {
    if (hash) setTimeout(() => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth' }), 60);
  }, [hash]);
  if (isRecap) return null;

  if (frozen) {
    const FZ = {
      zh: { live: '⏸️ 比赛进行中 · 赛前判断已冻结', pending: '🗂️ 比赛已结束 · 赛后校准中',
            sub: '赛前看方向，临场看变量，赛后看校准。校准就绪后这里会更新。', recap: '查看复盘 ▸' },
      vi: { live: '⏸️ Trận đang diễn ra · Nhận định trước trận đã khóa', pending: '🗂️ Trận đã kết thúc · Đang hiệu chỉnh sau trận',
            sub: 'Trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh.', recap: 'Xem phục dựng ▸' },
      my: { live: '⏸️ ပွဲ ဆက်ကစားနေဆဲ · ပွဲကြိုအမြင် အေးခဲထား', pending: '🗂️ ပွဲ ပြီးဆုံးပြီ · ပွဲပြီး ပြန်ညှိနေဆဲ',
            sub: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်။', recap: 'ပြန်သုံးသပ်ချက် ကြည့်ရန် ▸' },
      en: { live: '⏸️ Match in progress · pre-match call frozen', pending: '🗂️ Match finished · post-match calibration',
            sub: 'Pre-match for direction, late for variables, post-match for calibration.', recap: 'View recap ▸' },
    }[loc === 'zh' ? 'zh' : loc === 'vi' ? 'vi' : loc === 'my' ? 'my' : 'en'];
    return (
      <div className="page-enter">
        <div className="backbar">
          <button className="bk" onClick={() => navigate('/')}>←</button>
          <span className="ti">{B.backReal}</span>
        </div>
        {fx && (
          <div className="card ut-fixmeta">
            <span className="ut-teams">{fx.flagHome} {fx.home} <span className="ut-vs">vs</span> {fx.away} {fx.flagAway}</span>
            <span className="ut-meta">{B.kickoff} {kickoffLocal(fx.kickoffUtc, loc)} · {B.venue} {fx.venue} ({fx.city}) · {fx.round}</span>
          </div>
        )}
        <div className="status-card sc-frozen">
          <div className="ic">{fr.state === 'LIVE' ? '⏸️' : '🗂️'}</div>
          <div className="st">{fr.state === 'LIVE' ? FZ.live : FZ.pending}</div>
          <div className="sub2">{FZ.sub}</div>
        </div>
        <DetailShareRow path={`/predict/${id}`} loc={loc} kind="predict" />
      </div>
    );
  }

  // P0-4: lightweight tactical-room fallback for today's hotspot (manual fixture, no narrative).
  if (needsFallback) {
    const F = fbFor(loc);
    return (
      <div className="page-enter">
        <div className="backbar">
          <button className="bk" onClick={() => navigate('/')}>←</button>
          <span className="ti">{B.backReal}</span>
        </div>
        <div className="recap-banner">{F.banner}</div>
        {manualFx === undefined ? (
          <div className="status-card"><div className="ic">🔮</div><div className="st">{F.loading}</div></div>
        ) : manualFx ? (
          <>
            <div className="card ut-fixmeta">
              <span className="ut-teams">{manualFx.home} <span className="ut-vs">vs</span> {manualFx.away}</span>
              <span className="ut-meta">{B.kickoff} {manualFx.kickoffUtc ? kickoffLocal(manualFx.kickoffUtc, loc) : F.kickoffTba}</span>
            </div>
            <div className="card th-hero plp-predict">
              <div className="th-badge">{F.state}</div>
              <div className="th-meta">{F.why}</div>
              <div className="plp-focus">
                <div className="plp-focus-title">{F.focus}</div>
                <ul className="plp-bullets">{F.bullets.map((b, i) => <li key={i}>{interp(b, manualFx!.home, manualFx!.away)}</li>)}</ul>
              </div>
              <div className="plp-focus">
                <div className="plp-focus-title">{F.risk}</div>
                <ul className="plp-bullets">{F.risks.map((b, i) => <li key={i}>{interp(b, manualFx!.home, manualFx!.away)}</li>)}</ul>
              </div>
              <div className="plp-focus">
                <div className="plp-focus-title">{F.thirtyTitle}</div>
                <div className="plp-30min">{F.thirty}</div>
              </div>
              <DetailShareRow path={`/predict/${slug}`} loc={loc} kind="predict" />
            </div>
          </>
        ) : (
          <div className="status-card"><div className="ic">🔮</div><div className="st">{B.none}</div></div>
        )}
      </div>
    );
  }

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">{isReal ? B.backReal : B.back}</span>
      </div>
      <div className="recap-banner">{isReal ? B.bannerReal : B.banner}</div>
      {fx && (
        <div className="card ut-fixmeta">
          <span className="ut-teams">{fx.flagHome} {fx.home} <span className="ut-vs">vs</span> {fx.away} {fx.flagAway}</span>
          <span className="ut-meta">{B.kickoff} {kickoffLocal(fx.kickoffUtc, loc)} · {B.venue} {fx.venue} ({fx.city}) · {fx.round}</span>
        </div>
      )}
      {n ? (
        <>
          {isReal && <StrongCallCard n={n} loc={loc} />}
          <ProductPredictView n={n} loc={loc} opsOpen={opsOpen} />
          {isReal && <DetailShareRow path={`/predict/${id}`} loc={loc} kind="predict" />}
        </>
      ) : (
        <div className="status-card"><div className="ic">🔮</div><div className="st">{B.none}</div></div>
      )}
    </div>
  );
}
