/**
 * Lightweight locale switch (zh | vi) — NOT a full i18n framework.
 *
 * Resolution order on first load:
 *   1. URL ?lang=vi / ?lang=zh   (also persisted)
 *   2. localStorage giandcup_lang
 *   3. default 'zh'
 *
 * Reactive via useSyncExternalStore — switching updates all subscribers without a
 * page reload. No external dependency. Only zh & vi; Burmese (my/mm) is deferred.
 */
import { useSyncExternalStore } from 'react';

// 'mm' (Myanmar/Burmese) is reserved for a future locale — no UI button, no copy
// yet. Burmese is deferred this sprint; the type slot lets the structure extend
// without a refactor.
export type Locale = 'zh' | 'vi' | 'mm';

const STORAGE_KEY = 'giandcup_lang';
const listeners = new Set<() => void>();

// Only zh & vi are user-selectable today (mm intentionally excluded).
function isLocale(v: unknown): v is Locale {
  return v === 'zh' || v === 'vi';
}

function readInitial(): Locale {
  if (typeof window === 'undefined') return 'zh';
  try {
    const q = new URLSearchParams(window.location.search).get('lang');
    if (isLocale(q)) {
      window.localStorage.setItem(STORAGE_KEY, q);
      return q;
    }
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (isLocale(stored)) return stored;
  } catch {
    /* ignore storage/URL errors; fall back to zh */
  }
  return 'zh';
}

let current: Locale = readInitial();

export function getLocale(): Locale {
  return current;
}

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
