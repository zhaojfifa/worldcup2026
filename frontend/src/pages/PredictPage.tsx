import { useEffect } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useLocale } from '../i18n/useLocale';
import { getProductNarrative, predictSlugToId } from '../data/productNarrativeData';
import { getUpcomingFixture } from '../data/upcomingFixtures';
import { ProductPredictView } from '../components/ProductProofViews';
import { StrongCallCard } from '../components/StrongSignalCard';
import { fixtureFreshness } from '../lib/freshness';

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
      zh: { live: '⏸️ 比赛进行中 · 赛前判断已冻结', pending: '🗂️ 比赛已结束 · 赛后复盘生成中',
            sub: '赛前看方向，临场看变量，赛后看校准。复盘就绪后这里会更新。', recap: '查看复盘 ▸' },
      vi: { live: '⏸️ Trận đang diễn ra · Nhận định trước trận đã khóa', pending: '🗂️ Trận đã kết thúc · Đang dựng phục dựng',
            sub: 'Trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh.', recap: 'Xem phục dựng ▸' },
      my: { live: '⏸️ ပွဲ ဆက်ကစားနေဆဲ · ပွဲကြိုအမြင် အေးခဲထား', pending: '🗂️ ပွဲ ပြီးဆုံးပြီ · ပြန်သုံးသပ်ချက် ပြင်ဆင်နေသည်',
            sub: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်။', recap: 'ပြန်သုံးသပ်ချက် ကြည့်ရန် ▸' },
      en: { live: '⏸️ Match in progress · pre-match call frozen', pending: '🗂️ Match finished · recap generating',
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
        </>
      ) : (
        <div className="status-card"><div className="ic">🔮</div><div className="st">{B.none}</div></div>
      )}
    </div>
  );
}
