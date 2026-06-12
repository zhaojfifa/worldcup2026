// Growth P1.1 — share copy templates (Owner-approved skeletons, 2026-06-12).
// HARD RULE: every JUDGEMENT line ({lean}/{scoreline}/{variable}/{recapLine}) is filled
// from guard-passed LLM narrative fields at assembly time — the skeleton supplies only
// framing the Owner wrote (赛前看方向，临场看变量，赛后看校准 etc). No betting words,
// no win guarantees, no process/audit leakage, no fake urgency.
import type { Locale } from '../i18n/useLocale';
import { getProductNarrative } from '../data/productNarrativeData';
import { getUpcomingFixture } from '../data/upcomingFixtures';
import { getStoredRef } from './refCapture';

export const SITE = 'https://worldcup2026-izid.onrender.com';

// Operator default codes per language (Owner §2): used only when the visitor has no ref.
export const DEFAULT_REF: Record<string, string> = { zh: 'QG-TEST1', vi: 'TT-VN88', my: 'FO-MM21' };

export function refFor(loc: Locale): string {
  return getStoredRef() ?? DEFAULT_REF[loc] ?? DEFAULT_REF.zh;
}

export function shareLink(path: string, loc: Locale, ref?: string): string {
  const r = ref ?? refFor(loc);
  const sep = path.includes('?') ? '&' : '?';
  return `${SITE}${path}${sep}ref=${r}`;
}

function fixtureTitle(id: string): string {
  const fx = getUpcomingFixture(id);
  return fx ? `${fx.home} vs ${fx.away}` : id;
}

/** Deterministic split of the LLM scoreline band: first listed score = primary,
 * rest = alternatives. Parsing only — the band itself stays the LLM's judgement. */
export function splitScoreband(scorelineView: string): { primary: string; alts: string[] } | null {
  const scores = scorelineView.match(/\d+\s*[-–]\s*\d+/g)?.map(s => s.replace(/\s/g, ''));
  if (!scores || !scores.length) return null;
  return { primary: scores[0], alts: scores.slice(1) };
}

/** A. pre-match share copy — STRONG RESULT FIRST (Owner copy structure 2026-06-12):
 * 1 strong result → 2 主比分/备选 → 3 risk → 4 why → 5 T-30 hook → 6 CTA.
 * Every judgement string ({main_lean}/{scoreline}/{risk_level}/{hero_subtitle}/projection)
 * stays a guard-passed LLM field or fixed projection — only the ORDER is engineered. */
export function prematchShareCopy(fixtureId: string, loc: Locale, ref?: string): string | null {
  const n = getProductNarrative(fixtureId, loc);
  if (!n || n.mode === 'real_recap') return null;
  const link = shareLink(`/predict/${fixtureId}`, loc, ref);
  const title = fixtureTitle(fixtureId);
  const band = splitScoreband(n.scoreline_view);
  const why = n.hero_subtitle || '';
  if (loc === 'zh') {
    return [`今晚主看：${title}`,
            `俅哥主看：${n.main_lean}`,
            band ? `主比分：${band.primary}` : n.scoreline_view,
            band && band.alts.length ? `备选：${band.alts.join(' / ')}` : '',
            `冷门风险：${n.risk_level}`,
            why ? `为什么：${why}` : '',
            '开球前 30 分钟，首发 11 人出来后，群内更新最终倾向和比分区间。',
            '👇进群等临场修正：', link].filter(Boolean).join('\n');
  }
  if (loc === 'vi') {
    return [`Trận đáng xem: ${title}`,
            `Tiên Tri chốt: ${n.main_lean}`,
            band ? `Tỷ số chính: ${band.primary}` : n.scoreline_view,
            band && band.alts.length ? `Phương án phụ: ${band.alts.join(' / ')}` : '',
            `Rủi ro bất ngờ: ${n.risk_level}`,
            why ? `Vì sao: ${why}` : '',
            'Đội hình công bố là nhóm cập nhật thiên hướng cuối + vùng tỷ số, 30 phút trước giờ đá.',
            '👇Vào nhóm chờ hiệu chỉnh sát giờ:', link].filter(Boolean).join('\n');
  }
  if (loc === 'my') {
    return [`ဒီညအဓိကပွဲ: ${title}`,
            `Oracle ပြတ်ပြတ်: ${n.main_lean}`,
            band ? `အဓိကစကော: ${band.primary}` : n.scoreline_view,
            band && band.alts.length ? `အရန်: ${band.alts.join(' / ')}` : '',
            `Risk: ${n.risk_level}`,
            why ? `ဘာကြောင့်: ${why}` : '',
            'Lineup ထွက်တာနဲ့ ပွဲမစခင် မိနစ် ၃၀ မှာ အဖွဲ့ထဲ နောက်ဆုံးအမြင် + စကောအပိုင်းအခြား တင်မည်။',
            '👇အဖွဲ့ဝင်ပြီး ပြန်တွက်ချက် စောင့်ပါ:', link].filter(Boolean).join('\n');
  }
  return null;
}

/** B. recap share copy — recap line = LLM screenshot_line verbatim. */
export function recapShareCopy(fixtureId: string, loc: Locale, ref?: string, nextFixtureId = '1489371'): string | null {
  const n = getProductNarrative(fixtureId, loc);
  if (!n || n.mode !== 'real_recap') return null;
  const link = shareLink(`/recap/${fixtureId}`, loc, ref);
  const nextTitle = fixtureTitle(nextFixtureId);
  // Recap structure (Owner): 1 result → 2 what was right → 3 what changed →
  // 4 what to learn → 5 next fixture hook. Lines 1-3 = LLM fields verbatim.
  const right = n.validated_factors?.[0]?.name || '';
  if (loc === 'zh') {
    return [`俅哥复盘：${n.short_title}`,
            right ? `抓对了什么：${right}` : '',
            `${n.screenshot_line}`,
            '学到什么：赛前看方向，临场看变量，赛后看校准。',
            `下一场 ${nextTitle}，开球前 30 分钟继续看首发修正。`, '👇进群看临场修正：', link]
      .filter(Boolean).join('\n');
  }
  if (loc === 'vi') {
    return [`Tiên Tri phục dựng: ${n.short_title}`,
            right ? `Bắt đúng: ${right}` : '',
            `${n.screenshot_line}`,
            'Bài học: trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh.',
            `Trận tới ${nextTitle}, tiếp tục xem hiệu chỉnh đội hình 30 phút trước giờ đá.`,
            '👇Vào nhóm xem hiệu chỉnh sát giờ:', link].filter(Boolean).join('\n');
  }
  if (loc === 'my') {
    return [`Oracle ပြန်သုံးသပ်ချက်: ${n.short_title}`,
            right ? `မှန်ခဲ့သည်: ${right}` : '',
            `${n.screenshot_line}`,
            'သင်ခန်းစာ: ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်။',
            `နောက်ပွဲ ${nextTitle} — ပွဲမစခင် မိနစ် ၃၀ lineup ပြန်တွက်ချက် ဆက်ကြည့်ပါ။`,
            '👇အဖွဲ့ဝင်ရန်:', link].filter(Boolean).join('\n');
  }
  return null;
}

/** C. join-page share copy（进群看什么）. */
export function joinShareCopy(loc: Locale, ref?: string): string {
  const link = shareLink('/join', loc, ref);
  if (loc === 'vi') {
    return ['Vào nhóm để xem gì?', 'Nhận định mạnh trước trận, hiệu chỉnh 30 phút sát giờ, phục dựng sau trận.',
            'Không chỉ xem tỷ số — xem vì sao nó thay đổi.', '👇Vào nhóm Tiên Tri Bóng Đá:', link].join('\n');
  }
  if (loc === 'my') {
    return ['အဖွဲ့ထဲ ဘာကြည့်မလဲ?', 'ပွဲကြို ပြတ်သားအမြင် · မိနစ် ၃၀ ပြန်တွက်ချက် · ပွဲပြီး ပြန်သုံးသပ်ချက်။',
            'စကောသာမက ဘာကြောင့်ပြောင်းလဲလဲကိုပါ ကြည့်ပါ။', '👇Football Oracle အဖွဲ့ဝင်ရန်:', link].join('\n');
  }
  return ['进群看什么？', '赛前强判断、30 分钟临场修正、赛后复盘校准。', '不只是看比分，更看为什么会变。',
          '👇加入俅哥情报群：', link].join('\n');
}

/** Next-fixture warm-up（新比赛预热）— hook = LLM short_title verbatim. */
export function nextFixtureCopy(fixtureId: string, loc: Locale, ref?: string): string | null {
  const n = getProductNarrative(fixtureId, loc);
  const fx = getUpcomingFixture(fixtureId);
  if (!n || !fx) return null;
  const link = shareLink(`/predict/${fixtureId}`, loc, ref);
  const when = fx.kickoffUtc.slice(5, 16).replace('T', ' ');
  if (loc === 'vi') {
    return [`Sắp đá: ${fx.home} vs ${fx.away} (${when} UTC)`, `“${n.short_title}”`,
            'Vào nhóm trước: đội hình công bố là Tiên Tri tính lại ngay trước giờ đá.',
            '👇Xem nhận định + chờ hiệu chỉnh:', link].join('\n');
  }
  if (loc === 'my') {
    return [`မကြာမီ: ${fx.home} vs ${fx.away} (${when} UTC)`, `“${n.short_title}”`,
            'Lineup ထွက်တာနဲ့ Oracle ချက်ချင်း ပြန်တွက်မည် — အရင်ဝင်ထားပါ။', '👇ကြည့်ရန်:', link].join('\n');
  }
  return [`即将开赛：${fx.home} vs ${fx.away}（${when} UTC）`, `“${n.short_title}”`,
          '为什么要赛前进群？首发一公布，俅哥开球前 30 分钟就重算。', '👇看判断 + 等临场修正：', link].join('\n');
}
