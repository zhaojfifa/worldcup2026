import { useNavigate } from 'react-router-dom';
import type { Locale } from '../i18n/useLocale';
import { UPCOMING_FIXTURES, getUpcomingFixture } from '../data/upcomingFixtures';
import { getProductNarrative } from '../data/productNarrativeData';
import { getRescore } from '../data/rescoreData';
import { ShareBlock } from './ShareBlock';
import { buildStrongCall } from '../growth/strongCallProjection';
import { fixtureFreshness } from '../lib/freshness';

// P1.2b — frozen/recap state copy when a fixture is no longer pre-match (kickoff passed).
// Defensive: shown even if the bundled narrative still says pre-match (stale status).
// pending copy must NOT expose internal recap-generation state (RECAP_PENDING is internal;
// recap_ready=false does NOT mean a customer recap is being produced). Owner hotfix 2026-06-14:
// use post-match calibration language, never 复盘生成中 / 生成中 / 待生成复盘.
// joinPost: a FINISHED fixture must NOT show a 赛前/pre-match group CTA (the match is over).
// Owner hotfix 2026-06-14: post-match observation CTA only in the frozen block.
const FROZEN = {
  zh: { live: '比赛进行中 · 赛前卡已冻结 · 赛后开启校准', pending: '比赛已结束 · 赛后校准中', ready: '比赛已结束 · 查看复盘', viewRecap: '查看复盘', joinPost: '加入情报群看赛后观察' },
  vi: { live: 'Trận đang diễn ra · thẻ trước trận đã khóa · hiệu chỉnh sau trận', pending: 'Trận đã kết thúc · Đang hiệu chỉnh sau trận', ready: 'Trận đã kết thúc · Xem phục dựng', viewRecap: 'Xem phục dựng', joinPost: 'Vào nhóm xem quan sát sau trận' },
  my: { live: 'ပွဲ ဆက်ကစားနေဆဲ · ပွဲကြိုကတ် အေးခဲထား · ပွဲပြီး ပြန်ညှိမည်', pending: 'ပွဲ ပြီးဆုံးပြီ · ပွဲပြီး ပြန်ညှိနေဆဲ', ready: 'ပွဲ ပြီးဆုံးပြီ · ပြန်သုံးသပ်ချက် ကြည့်ရန်', viewRecap: 'ပြန်သုံးသပ်ချက် ကြည့်ရန်', joinPost: 'ပွဲပြီးနောက် သုံးသပ်ချက်ကြည့်ရန် အဖွဲ့ဝင်ပါ' },
  en: { live: 'Match in progress · pre-match card frozen · calibration after the match', pending: 'Match finished · post-match calibration', ready: 'Match finished · View recap', viewRecap: 'View recap', joinPost: 'Join for post-match notes' },
};
function frozenFor(loc: Locale) { return loc === 'zh' ? FROZEN.zh : loc === 'vi' ? FROZEN.vi : loc === 'my' ? FROZEN.my : FROZEN.en; }

// Product Closure P1 (Owner §6): the home conversion area is the ACTIVE 2026 loop —
// main match → strong call → 30-min rescore hook → latest 2026 recap trust anchor →
// join group. All judgement strings below are LLM fields; labels are stage chrome.

// Home entry for REAL World Cup 2026 fixtures (bundled engineering facts) whose
// persona tactical-room narrative (LLM-generated, guard-passed) is ready.
// Personas: zh 俅哥说球 · vi Tiên Tri Bóng Đá · my Football Oracle (temporary
// trial name — Burmese persona name pending Owner; see
// docs/MVP2_MYANMAR_PERSONA_NAMING_OPTIONS.md). Giành Cup, engine ScoutScore.
// Section labels/buttons are UI chrome; the football intelligence lives in /predict/:id.
const L10N = {
  zh: { title: 'World Cup 2026 · 真实赛程', en: 'TACTICAL ROOM', cta: '俅哥战术室', today: '今日开球', upcoming: '即将开球' },
  vi: { title: 'World Cup 2026 · Lịch thi đấu thật', en: 'TACTICAL ROOM', cta: 'Phòng chiến thuật Tiên Tri', today: 'Đá hôm nay', upcoming: 'Sắp diễn ra' },
  my: { title: 'World Cup 2026 · တကယ့်ပွဲစဉ်', en: 'TACTICAL ROOM', cta: 'Oracle နည်းဗျူဟာခန်း', today: 'ဒီနေ့ ကန်မည်', upcoming: 'မကြာမီ' },
  en: { title: 'World Cup 2026 · Real fixtures', en: 'TACTICAL ROOM', cta: 'Giành Cup Tactical Room', today: 'Kicks off today', upcoming: 'Upcoming' },
};

const HERO = {
  zh: { badge: '⚡ World Cup 2026 揭幕窗口 · 真实比赛', enter: '进入俅哥战术室', join: '加入赛前情报群',
        status: '🔮 俅哥已生成今日赛前判断 · 开球前 30 分钟将重算 · 数据同步 ' },
  vi: { badge: '⚡ World Cup 2026 · Trận thật', enter: 'Vào phòng chiến thuật Tiên Tri', join: 'Vào nhóm tin báo trước trận',
        status: '🔮 Tiên Tri Bóng Đá đã có nhận định hôm nay · Tính lại 30 phút trước giờ bóng lăn · Đồng bộ ' },
  my: { badge: '⚡ World Cup 2026 · တကယ့်ပွဲ', enter: 'Oracle နည်းဗျူဟာခန်း ဝင်ရန်', join: 'ပွဲကြိုသတင်း အဖွဲ့ ဝင်ရန်',
        status: '🔮 Football Oracle ၏ ယနေ့ ပွဲကြိုအမြင် ထွက်ပြီ · ပွဲမစခင် မိနစ် ၃၀ ပြန်တွက်မည် · ထပ်တူ ' },
  en: { badge: '⚡ World Cup 2026 · Real fixture', enter: 'Open the Tactical Room', join: 'Join the pre-match group',
        status: '🔮 Pre-match view ready · Re-scored 30 minutes before kickoff · Synced ' },
};

function heroFor(loc: Locale) {
  return loc === 'zh' ? HERO.zh : loc === 'vi' ? HERO.vi : loc === 'my' ? HERO.my : HERO.en;
}

function kickoffLabel(iso: string, loc: Locale): string {
  const d = new Date(iso);
  // 'my' keeps Latin digits/format (mm density profile keeps concise English terms).
  const locale = loc === 'zh' ? 'zh-CN' : loc === 'vi' ? 'vi-VN' : 'en-GB';
  return d.toLocaleString(locale, { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

/** Persona status strip (Owner hierarchy item 1). syncTime is the app's data-sync stamp. */
export function TrialStatusStrip({ loc, syncTime }: { loc: Locale; syncTime: string }) {
  const H = heroFor(loc);
  return <div className="trial-status">{H.status}{syncTime}</div>;
}

const MAIN_LABEL = {
  zh: { today: '今日主推比赛', next: '下一场重点比赛 · 即将开赛战术室', lean: '俅哥主看', score: '主比分', backup: '备选' },
  vi: { today: 'Trận đáng xem nhất hôm nay', next: 'Trận trọng điểm tiếp theo', lean: 'Tiên Tri chốt', score: 'Tỷ số chính', backup: 'Phương án phụ' },
  my: { today: 'ဒီနေ့ အဓိကပွဲ', next: 'နောက်လာမည့် အဓိကပွဲ', lean: 'Oracle ပြတ်ပြတ်', score: 'အဓိကစကော', backup: 'အရန်' },
  en: { today: "Today's main match", next: 'Next key match', lean: 'Lean', score: 'Score', backup: 'Backup' },
};

/** Main trial entry card (Owner §6 item 1/2): the ACTIVE real fixture with the strong call. */
export function TrialHeroCard({ loc, fixtureId }: { loc: Locale; fixtureId: string }) {
  const navigate = useNavigate();
  const H = heroFor(loc);
  const M = loc === 'zh' ? MAIN_LABEL.zh : loc === 'vi' ? MAIN_LABEL.vi : loc === 'my' ? MAIN_LABEL.my : MAIN_LABEL.en;
  const fx = getUpcomingFixture(fixtureId);
  if (!fx) return null;
  const n = getProductNarrative(fixtureId, loc);
  // P1.2b runtime guard: kickoff passed -> NEVER render the pre-match hero, even if the
  // bundled narrative still says pre-match. Show frozen / recap-pending / recap-ready.
  const fr = fixtureFreshness(fx.kickoffUtc, n?.mode);
  if (!fr.preMatchAllowed) {
    const FZ = frozenFor(loc);
    const line = fr.recapAllowed ? FZ.ready : fr.state === 'LIVE' ? FZ.live : FZ.pending;
    return (
      <div className="card th-hero th-frozen">
        <div className="th-badge sc-frozen-badge">{line}</div>
        <div className="th-teams">{fx.flagHome} {fx.home} <span className="ut-vs">vs</span> {fx.away} {fx.flagAway}</div>
        <div className="th-meta">{kickoffLabel(fx.kickoffUtc, loc)} · {fx.venue} ({fx.city}) · {fx.round}</div>
        {fr.recapAllowed ? (
          // recap_ready=true: a real recap exists -> 查看复盘 allowed. Match is finished, so the
          // group CTA is POST-match (never 加入赛前情报群).
          <div className="pp-cta-row">
            <button className="recap-cta-btn" onClick={() => navigate(`/recap/${fixtureId}`)}>{FZ.viewRecap} ▸</button>
            <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{FZ.joinPost} ▸</button>
          </div>
        ) : (
          // recap_ready=false (live / post-match calibration): NO recap link (no fake recap);
          // POST-match group CTA only (the match is over -> no 赛前/pre-match wording).
          <div className="pp-cta-row">
            <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{FZ.joinPost} ▸</button>
          </div>
        )}
      </div>
    );
  }
  const isToday = fx.kickoffUtc.slice(0, 10) === new Date().toISOString().slice(0, 10);
  return (
    <div className="card th-hero">
      <div className="th-badge">{H.badge} · {isToday ? M.today : M.next}</div>
      <div className="th-teams">{fx.flagHome} {fx.home} <span className="ut-vs">vs</span> {fx.away} {fx.flagAway}</div>
      <div className="th-meta">{kickoffLabel(fx.kickoffUtc, loc)} · {fx.venue} ({fx.city}) · {fx.round}</div>
      {n && <div className="th-hook">“{n.short_title}”</div>}
      {n && n.main_lean && <div className="sc-row" style={{ border: 0, paddingTop: 2 }}>
        <span className="sc-k">{M.lean}</span><span className="sc-v sc-lead">{n.main_lean}</span>
      </div>}
      {(() => { // canonical projection: home shows the SAME 主比分/备选 as predict/share/CLI
        const call = buildStrongCall(fixtureId, loc);
        if (!call?.primary_score) return null;
        return <div className="sc-row" style={{ border: 0, paddingTop: 0 }}>
          <span className="sc-k">{M.score}</span>
          <span className="sc-v"><span className="sc-primary-score">{call.primary_score}</span>
            {call.backup_scores.length > 0 && <span className="sc-backup">　{M.backup}: {call.backup_scores.join(' / ')}</span>}</span>
        </div>;
      })()}
      <div className="pp-cta-row">
        <button className="recap-cta-btn" onClick={() => navigate(`/predict/${fixtureId}`)}>{H.enter} ▸</button>
        <button className="recap-cta-btn alt" onClick={() => navigate('/community')}>{H.join} ▸</button>
      </div>
      {/* P1.5a: share buttons removed from the homepage hero (live on /share + detail pages) */}
    </div>
  );
}

// ── Home: 30-min rescore hook (Owner §6 item 4 / §9) ────────────────────────
const RH = {
  zh: { title: '⏱️ 30 分钟临场修正', en: 'LIVE 30-MIN RE-SCORE', frame: '赛前看方向，临场看变量。',
        cta: '看临场修正逻辑', win: '首发公布后（约开球前 60–30 分钟），群内更新最终倾向、参考比分、冷门风险。' },
  vi: { title: '⏱️ Hiệu chỉnh 30 phút trước trận', en: 'LIVE 30-MIN RE-SCORE', frame: 'Trước trận xem hướng, sát giờ xem biến số.',
        cta: 'Xem logic hiệu chỉnh sát giờ', win: 'Khi đội hình công bố (~60–30 phút trước giờ đá), nhóm sẽ cập nhật thiên hướng cuối, tỷ số tham khảo, rủi ro bất ngờ.' },
  my: { title: '⏱️ မိနစ် ၃၀ ပွဲနီးပြန်တွက်ချက်', en: 'LIVE 30-MIN RE-SCORE', frame: 'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable ။',
        cta: 'ပြန်တွက်ချက် logic ကြည့်ရန်', win: 'Lineup ထွက်ပြီးနောက် (ပွဲမစခင် ၆၀–၃၀ မိနစ်) အဖွဲ့ထဲ နောက်ဆုံးအမြင် · ရည်ညွှန်းစကော · risk အသစ် တင်ပေးမည်။' },
};

export function RescoreHookCard({ loc, fixtureId }: { loc: Locale; fixtureId: string }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? RH.zh : loc === 'vi' ? RH.vi : loc === 'my' ? RH.my : null;
  const rs = getRescore(fixtureId, loc);
  const fx = getUpcomingFixture(fixtureId);
  const n = getProductNarrative(fixtureId, loc);
  // P1.2b: the 30-min rescore hook is a PRE-MATCH promise — hide it once kickoff passed.
  if (fx && !fixtureFreshness(fx.kickoffUtc, n?.mode).preMatchAllowed) return null;
  if (!L) return null;
  return (
    <>
      <div className="sec-en"><span className="zh">{L.title}</span><span className="en">{L.en}</span></div>
      <div className="card rh-card">
        <div className="sc-frame" style={{ textAlign: 'left', margin: '0 0 4px' }}>{L.frame}</div>
        {rs?.public_teaser && <div className="rh-line">“{rs.public_teaser}”</div>}
        <div className="rh-line" style={{ color: 'var(--sub)', fontSize: 12 }}>{L.win}</div>
        <button className="recap-cta-btn" style={{ width: '100%' }}
                onClick={() => navigate(`/predict/${fixtureId}#rescore`)}>{L.cta} ▸</button>
      </div>
    </>
  );
}

// ── Home: latest 2026 recap trust anchor (Owner §6 item 5 / §10) ────────────
const RA = {
  zh: { title: '🗂️ 最新 2026 复盘 · 赛后看校准', en: 'LATEST 2026 RECAP', cta: '看俅哥怎么校准' },
  vi: { title: '🗂️ Phục dựng 2026 mới nhất · Sau trận xem hiệu chỉnh', en: 'LATEST 2026 RECAP', cta: 'Xem Tiên Tri hiệu chỉnh thế nào' },
  my: { title: '🗂️ နောက်ဆုံး 2026 ပြန်သုံးသပ်ချက်', en: 'LATEST 2026 RECAP', cta: 'Oracle ဘယ်လိုပြန်ညှိလဲ ကြည့်ရန်' },
};

export function RecapAnchorCard({ loc, fixtureId }: { loc: Locale; fixtureId: string }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? RA.zh : loc === 'vi' ? RA.vi : loc === 'my' ? RA.my : null;
  const n = getProductNarrative(fixtureId, loc);
  if (!L || !n || n.mode !== 'real_recap') return null;
  return (
    <>
      <div className="sec-en"><span className="zh">{L.title}</span><span className="en">{L.en}</span></div>
      <div className="card ra-card">
        <div className="ra-line"><b>{n.short_title}</b></div>
        <div className="ra-line" style={{ fontSize: 12, color: 'var(--sub)' }}>{n.screenshot_line}</div>
        <button className="recap-cta-btn alt" style={{ width: '100%' }}
                onClick={() => navigate(`/recap/${fixtureId}`)}>{L.cta} ▸</button>
        <ShareBlock kind="recap" fixtureId={fixtureId} loc={loc} />
      </div>
    </>
  );
}

/** Secondary upcoming fixtures (Owner hierarchy item 3). */
export function UpcomingTacticalStrip({ loc, excludeId }: { loc: Locale; excludeId?: string }) {
  const navigate = useNavigate();
  const L = loc === 'zh' ? L10N.zh : loc === 'vi' ? L10N.vi : loc === 'my' ? L10N.my : L10N.en;
  const todayIso = new Date().toISOString().slice(0, 10);
  // finished/live fixtures belong to the recap anchor, not the upcoming strip. P1.2b:
  // exclude by RUNTIME freshness (kickoff passed), not just the narrative recap flag.
  const rows = UPCOMING_FIXTURES.filter(f => {
    const n = getProductNarrative(f.id, loc);
    return f.id !== excludeId && n && n.mode !== 'real_recap'
      && fixtureFreshness(f.kickoffUtc, n.mode).preMatchAllowed;
  });
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
  zh: { title: '俅哥强判断', en: 'STRONG CALLS', room: '战术室', recap: '复盘', group: '入群' },
  vi: { title: 'Nhận định mạnh của Tiên Tri', en: 'STRONG CALLS', room: 'Phòng chiến thuật', recap: 'Phục dựng', group: 'Vào nhóm' },
  my: { title: 'Oracle ပြတ်သားအမြင်', en: 'STRONG CALLS', room: 'နည်းဗျူဟာခန်း', recap: 'ပြန်သုံးသပ်', group: 'အဖွဲ့ဝင်' },
  en: { title: 'Strong calls', en: 'STRONG CALLS', room: 'Tactical room', recap: 'Recap', group: 'Join' },
};

export function HotTopicsSection({ loc }: { loc: Locale }) {
  const navigate = useNavigate();
  const H = loc === 'zh' ? HOT.zh : loc === 'vi' ? HOT.vi : loc === 'my' ? HOT.my : HOT.en;
  // P1.2b: a strong-call hook routes by RUNTIME freshness — pre-match -> tactical room,
  // recap-ready -> recap page, live/recap-pending -> dropped (no fresh strong call to show).
  const strongRow = (id: string) => {
    const n = getProductNarrative(id, loc);
    if (!n) return null;
    const fx = getUpcomingFixture(id);
    const fr = fixtureFreshness(fx?.kickoffUtc ?? null, n.mode);
    if (fr.preMatchAllowed) return { key: `room${id}`, hook: n.short_title, to: `/predict/${id}`, tag: H.room, hot: true };
    if (fr.recapAllowed) return { key: `recap${id}`, hook: n.short_title, to: `/recap/${id}`, tag: H.recap, hot: false };
    return null;
  };
  const rs = getRescore('1489371', loc) || getRescore('1489369', loc);
  const rows = [
    strongRow('1489371'),
    strongRow('1489369'),
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
