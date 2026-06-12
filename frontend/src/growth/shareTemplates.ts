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

/** A. pre-match share copy（今晚主看）— judgement lines = LLM fields verbatim. */
export function prematchShareCopy(fixtureId: string, loc: Locale, ref?: string): string | null {
  const n = getProductNarrative(fixtureId, loc);
  if (!n || n.mode === 'real_recap') return null;
  const link = shareLink(`/predict/${fixtureId}`, loc, ref);
  const title = fixtureTitle(fixtureId);
  const topVar = n.watch_next_signals?.[0]?.name || n.risk_factors?.[0]?.name || '';
  if (loc === 'zh') {
    return [`今晚主看：${title}`, `俅哥主看：${n.main_lean}`, `${n.scoreline_view}`,
            topVar ? `最大变量：${topVar}` : '',
            '开球前 30 分钟，群内会更新最终倾向和比分区间。', '👇进群等临场修正：', link]
      .filter(Boolean).join('\n');
  }
  if (loc === 'vi') {
    return [`Trận đáng xem: ${title}`, `Tiên Tri nghiêng về: ${n.main_lean}`, `${n.scoreline_view}`,
            topVar ? `Biến số lớn nhất: ${topVar}` : '',
            'Nhóm sẽ cập nhật thiên hướng cuối và vùng tỷ số 30 phút trước giờ đá.',
            '👇Vào nhóm chờ hiệu chỉnh sát giờ:', link].filter(Boolean).join('\n');
  }
  if (loc === 'my') {
    return [`ဒီညအဓိကပွဲ: ${title}`, `Oracle ဦးတည်ချက်: ${n.main_lean}`, `${n.scoreline_view}`,
            topVar ? `အကြီးဆုံး variable: ${topVar}` : '',
            'ပွဲမစခင် မိနစ် ၃၀ မှာ အဖွဲ့ထဲ နောက်ဆုံးအမြင် တင်ပေးမည်။',
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
  if (loc === 'zh') {
    return [`俅哥复盘：${n.short_title}`, `${n.screenshot_line}`,
            '这就是为什么赛前看方向，临场看变量，赛后看校准。',
            `下一场 ${nextTitle}，开球前 30 分钟群内重算。`, '👇进群看临场修正：', link].join('\n');
  }
  if (loc === 'vi') {
    return [`Tiên Tri phục dựng: ${n.short_title}`, `${n.screenshot_line}`,
            'Vì vậy: trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh.',
            `Trận tới ${nextTitle}, nhóm tính lại 30 phút trước giờ đá.`,
            '👇Vào nhóm xem hiệu chỉnh sát giờ:', link].join('\n');
  }
  if (loc === 'my') {
    return [`Oracle ပြန်သုံးသပ်ချက်: ${n.short_title}`, `${n.screenshot_line}`,
            'ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်။',
            `နောက်ပွဲ ${nextTitle} — ပွဲမစခင် မိနစ် ၃၀ အဖွဲ့ထဲ ပြန်တွက်မည်။`,
            '👇အဖွဲ့ဝင်ရန်:', link].join('\n');
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
