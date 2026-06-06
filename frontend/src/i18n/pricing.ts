/**
 * Locale-aware MVP pricing. Never hardcode ¥ in pages — read from here.
 *
 * These are **MVP operational prices**, NOT real-time exchange rates.
 * Vietnamese mode shows VND (₫); Chinese shows RMB; English shows USD.
 * MTC is a platform point count and is identical across locales.
 *
 * Fallback: vi/mm → en, en → en, zh → zh (mirrors i18n fallback policy: no
 * non-Chinese locale falls back to RMB).
 */
import type { Locale } from './useLocale';

export interface PriceCopy {
  singleUnlock: string;  // 单场解锁
  monthlyVip: string;    // 月度社群订阅
  tokenUnlock: string;   // MTC 解锁（跨语言一致）
}

const PRICE: Record<'zh' | 'en' | 'vi', PriceCopy> = {
  zh: { singleUnlock: '39 元',    monthlyVip: '199 元/月',        tokenUnlock: '390 MTC' },
  en: { singleUnlock: 'US$5.5',   monthlyVip: 'US$28/month',      tokenUnlock: '390 MTC' },
  vi: { singleUnlock: '139.000₫', monthlyVip: '699.000₫/tháng',   tokenUnlock: '390 MTC' },
};

/** Resolve pricing for a locale (vi/mm → en fallback; en → en; zh → zh). */
export function getPrice(locale: Locale): PriceCopy {
  if (locale === 'zh') return PRICE.zh;
  if (locale === 'vi') return PRICE.vi;
  return PRICE.en; // en + mm (deferred) both use the English/USD prices
}
