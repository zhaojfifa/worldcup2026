/**
 * Lightweight locale switch (zh | vi | my) — NOT a full i18n framework.
 *
 * Resolution order on first load:
 *   1. URL ?lang=zh / ?lang=vi / ?lang=my   (persisted; legacy ?lang=mm → my)
 *   2. localStorage giandcup_lang
 *   3. browser language (zh / zh-CN / zh-TW → zh · vi / vi-VN → vi · my / my-MM → my)
 *   4. default 'zh'
 *
 * Reactive via useSyncExternalStore — switching updates all subscribers without a
 * page reload. No external dependency.
 */
import { useSyncExternalStore } from 'react';

// 'en' is the international fallback for all non-Chinese locales.
// 'my' (Burmese, ISO 639-1) is a first-class customer locale since the
// VI-naming + MY-locale consolidation sprint; legacy code 'mm' is accepted
// as an alias at every entry point and normalized to 'my'.
export type Locale = 'zh' | 'en' | 'vi' | 'my';

// Per-locale fallback chains. zh stays Chinese-only; every other locale falls back
// to English (NOT Chinese) to avoid mixed-language UI.
export const FALLBACK_CHAIN: Record<Locale, Locale[]> = {
  zh: ['zh'],
  en: ['en', 'zh'],
  vi: ['vi', 'en'],
  my: ['my', 'en'],
};

const STORAGE_KEY = 'giandcup_lang';
const listeners = new Set<() => void>();

/**
 * Normalize an external language tag (URL param / localStorage / browser) to a
 * selectable customer locale. 'en' stays the internal fallback layer (no tag maps
 * to it). Returns null for anything unrecognized.
 */
function normalize(v: unknown): Locale | null {
  if (typeof v !== 'string' || !v) return null;
  const tag = v.toLowerCase();
  if (tag === 'my' || tag === 'mm' || tag.startsWith('my-')) return 'my';
  if (tag === 'zh' || tag.startsWith('zh-')) return 'zh';
  if (tag === 'vi' || tag.startsWith('vi-')) return 'vi';
  return null;
}

function fromBrowser(): Locale | null {
  try {
    const tags = [...(navigator.languages ?? []), navigator.language];
    for (const t of tags) {
      const loc = normalize(t);
      if (loc) return loc;
    }
  } catch {
    /* ignore */
  }
  return null;
}

function readInitial(): Locale {
  if (typeof window === 'undefined') return 'zh';
  try {
    const q = normalize(new URLSearchParams(window.location.search).get('lang'));
    if (q) {
      window.localStorage.setItem(STORAGE_KEY, q);
      return q;
    }
    const stored = normalize(window.localStorage.getItem(STORAGE_KEY));
    if (stored) return stored;
    const nav = fromBrowser();
    if (nav) return nav;
  } catch {
    /* ignore storage/URL errors; fall back to zh */
  }
  return 'zh';
}

let current: Locale = readInitial();

export function getLocale(): Locale {
  return current;
}

/** Switch locale: persist + reflect in the URL (?lang=) WITHOUT navigating away. */
export function setLocale(next: Locale): void {
  if (next === current) return;
  current = next;
  try {
    window.localStorage.setItem(STORAGE_KEY, next);
    const url = new URL(window.location.href);
    url.searchParams.set('lang', next);
    window.history.replaceState({}, '', url);
  } catch {
    /* ignore */
  }
  listeners.forEach((fn) => fn());
}

function subscribe(fn: () => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** React hook: re-renders the component when the locale changes. */
export function useLocale(): Locale {
  return useSyncExternalStore(subscribe, getLocale, getLocale);
}
