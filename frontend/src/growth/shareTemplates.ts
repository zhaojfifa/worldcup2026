// Growth P1.1 — share copy templates (Owner-approved skeletons, 2026-06-12).
// HARD RULE: every JUDGEMENT line ({lean}/{scoreline}/{variable}/{recapLine}) is filled
// from guard-passed LLM narrative fields at assembly time — the skeleton supplies only
// framing the Owner wrote (赛前看方向，临场看变量，赛后看校准 etc). No betting words,
// no win guarantees, no process/audit leakage, no fake urgency.
import type { Locale } from '../i18n/useLocale';
import { getProductNarrative } from '../data/productNarrativeData';
import { getUpcomingFixture } from '../data/upcomingFixtures';
import { getStoredRef } from './refCapture';
import { buildStrongCall, buildRecapCall } from './strongCallProjection';
// canonical helpers re-exported for backwards compatibility — the implementation
// lives ONLY in strongCallProjection.ts (P1.1c-fix: split/harmonize happen once)
export { splitScoreband, harmonizedRisk } from './strongCallProjection';

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

/** A. pre-match share copy — STRONG RESULT FIRST (Owner copy structure 2026-06-12):
 * 1 strong result → 2 主比分/备选 → 3 risk → 4 why → 5 T-30 hook → 6 CTA.
 * Every judgement string ({main_lean}/{scoreline}/{risk_level}/{hero_subtitle}/projection)
 * stays a guard-passed LLM field or fixed projection — only the ORDER is engineered. */
export function prematchShareCopy(fixtureId: string, loc: Locale, ref?: string): string | null {
  const c = buildStrongCall(fixtureId, loc);
  if (!c) return null;
  const link = shareLink(`/predict/${fixtureId}`, loc, ref);
  const head = loc === 'zh' ? '今晚主看' : loc === 'vi' ? 'Trận đáng xem' : 'ဒီညအဓိကပွဲ';
  const leanL = loc === 'zh' ? '俅哥主看' : loc === 'vi' ? 'Tiên Tri chốt' : 'Oracle ပြတ်ပြတ်';
  const scoreL = loc === 'zh' ? '主比分' : loc === 'vi' ? 'Tỷ số chính' : 'အဓိကစကော';
  const backupL = loc === 'zh' ? '备选' : loc === 'vi' ? 'Phương án phụ' : 'အရန်';
  const riskL = loc === 'zh' ? '冷门风险' : loc === 'vi' ? 'Rủi ro bất ngờ' : 'Risk';
  const whyL = loc === 'zh' ? '为什么' : loc === 'vi' ? 'Vì sao' : 'ဘာကြောင့်';
  return [`${head}：${c.teams}`,
          `${leanL}：${c.main_lean}`,
          c.primary_score ? `${scoreL}：${c.primary_score}` : c.scoreline_raw,
          c.backup_scores.length ? `${backupL}：${c.backup_scores.join(' / ')}` : '',
          `${riskL}：${c.risk_label}`,
          c.why ? `${whyL}：${c.why}` : '',
          c.t30_hook,
          `👇${c.cta_line}：`, link].filter(Boolean).join('\n');
}

/** B. recap share copy — recap line = LLM screenshot_line verbatim. */
export function recapShareCopy(fixtureId: string, loc: Locale, ref?: string): string | null {
  const r = buildRecapCall(fixtureId, loc);
  if (!r) return null;
  const link = shareLink(`/recap/${fixtureId}`, loc, ref);
  const head = loc === 'zh' ? '俅哥复盘' : loc === 'vi' ? 'Tiên Tri phục dựng' : 'Oracle ပြန်သုံးသပ်ချက်';
  const rightL = loc === 'zh' ? '赛前看对了什么' : loc === 'vi' ? 'Bắt đúng' : 'မှန်ခဲ့သည်';
  const devL = loc === 'zh' ? '比分为什么偏离' : loc === 'vi' ? 'Vì sao tỷ số lệch' : 'စကော ဘာကြောင့်လွဲ';
  const ctaL = loc === 'zh' ? '👇进群看临场修正：' : loc === 'vi' ? '👇Vào nhóm xem hiệu chỉnh sát giờ:' : '👇အဖွဲ့ဝင်ရန်:';
  return [`${head}：${r.result_title}`,
          r.what_was_right ? `${rightL}：${r.what_was_right}` : '',
          `${devL}：${r.why_deviated}`,
          r.calibration_line,
          r.next_hook, ctaL, link].filter(Boolean).join('\n');
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
