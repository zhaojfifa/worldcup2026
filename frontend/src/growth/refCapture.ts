// Growth P1 — app-wide ?ref= capture (Owner GO 2026-06-12).
// First-touch wins, localStorage, 30 days. NO identity capture: we send only
// {ref, surface, lang, device_class}; invalid refs are counted server-side and
// never attached. Mock mode / offline = silently skipped (never blocks the UI).
const BASE = (import.meta.env.VITE_API_BASE_URL as string) ?? 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const KEY = 'growth_ref';
const TTL_MS = 30 * 24 * 3600 * 1000;
const CODE_RE = /^(QG|TT|FO)-[A-Z0-9]{4,6}$/;

interface StoredRef { code: string; ts: number; }

export function getStoredRef(): string | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const v = JSON.parse(raw) as StoredRef;
    if (!v.code || Date.now() - v.ts > TTL_MS) { localStorage.removeItem(KEY); return null; }
    return v.code;
  } catch { return null; }
}

function deviceClass(): string {
  return /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop';
}

function post(path: string, body: unknown): void {
  if (USE_MOCK) return;
  try {
    fetch(`${BASE}${path}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body), keepalive: true,
    }).catch(() => { /* growth tracking must never break the product */ });
  } catch { /* ignore */ }
}

/** Call once on app bootstrap. Captures ?ref= (first-touch) and records the click. */
export function captureRef(locale: string): void {
  try {
    const params = new URLSearchParams(window.location.search);
    const raw = (params.get('ref') ?? '').toUpperCase().trim();
    if (!raw || !CODE_RE.test(raw)) return;
    const existing = getStoredRef();
    const force = params.get('ref_force') === '1'; // operator testing escape only
    if (existing && !force) return; // first-touch wins
    localStorage.setItem(KEY, JSON.stringify({ code: raw, ts: Date.now() } satisfies StoredRef));
    post('/api/v1/growth/click', {
      ref: raw, surface: window.location.pathname || '/', lang: locale, device_class: deviceClass(),
    });
  } catch { /* never block rendering */ }
}

/** Call when the user taps a group CTA; records join-intent against the stored ref. */
export function recordJoinIntent(surface: string, locale: string): void {
  const code = getStoredRef();
  if (!code) return;
  post('/api/v1/growth/join-intent', { ref: code, surface, lang: locale });
}
