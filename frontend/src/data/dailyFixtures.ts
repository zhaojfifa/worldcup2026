// P1.3b — RUNTIME daily fixtures source (Owner verdict 2026-06-13: 能更新才是硬道理).
// The homepage reads the daily fixture registry at RUNTIME (fetch /data/daily-fixtures.json),
// not only at build time — so a cron that rewrites the manifest can refresh the live slate
// (once a hosted writable source exists; see GROWTH_P13B doc for the honest limitation).
// The build-time generated import is kept ONLY as a fallback when the fetch fails.
import fallbackManifest from './dailyFixtures.generated.json';

export interface DailyFixtureRow {
  id: string | null;
  external_game_id?: string;
  home: string;
  away: string;
  kickoffUtc: string | null;
  status: string;
  lifecycle_state: string;
  preMatchAllowed?: boolean;
  recapReady: boolean;
  recapNeeded?: boolean;
  renderable?: boolean;
  heroCandidate: boolean;
  recapCandidate: boolean;
  nextCandidate: boolean;
  scoreHome?: number | null;
  scoreAway?: number | null;
}

export interface DailyManifest {
  generated_for_date: string;
  generated_at: string;
  source_mode?: string;
  fixture_count?: number;
  fixtures: DailyFixtureRow[];
}

export const FALLBACK_MANIFEST = fallbackManifest as DailyManifest;
const STATIC_URL = '/data/daily-fixtures.json';
// P1.3c: backend-hosted source updates WITHOUT a frontend rebuild. Uses the configured API base
// (same as api/client.ts), defaulting to the known prod backend.
const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '')
  || 'https://worldcup2026-api-71n6.onrender.com';
const BACKEND_URL = `${API_BASE}/api/v1/daily-fixtures`;

export type ManifestSource = 'backend' | 'static' | 'bundled';
export interface ManifestLoad { manifest: DailyManifest; source: ManifestSource }

function validManifest(m: unknown): m is DailyManifest {
  return !!m && Array.isArray((m as DailyManifest).fixtures) && (m as DailyManifest).fixtures.length > 0;
}

async function tryFetch(url: string, timeoutMs: number): Promise<DailyManifest | null> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    const res = await fetch(url, { cache: 'no-store', signal: ctrl.signal });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const m = await res.json();
    return validManifest(m) ? (m as DailyManifest) : null;
  } catch {
    return null;
  }
}

/** P1.3c fetch priority: 1) backend (live, updatable without rebuild) → 2) static deployed file
 *  → 3) bundled build-time data. NEVER throws; a broken source falls through, never crashes. */
export async function fetchDailyManifest(): Promise<ManifestLoad> {
  const backend = await tryFetch(BACKEND_URL, 3500);
  if (backend) return { manifest: backend, source: 'backend' };
  console.warn('[dailyFixtures] backend unavailable → trying static deployed file');
  const stat = await tryFetch(STATIC_URL, 2500);
  if (stat) return { manifest: stat, source: 'static' };
  console.warn('[dailyFixtures] static file unavailable → bundled fallback');
  return { manifest: FALLBACK_MANIFEST, source: 'bundled' };
}

/** Hero-eligible entries = fixtures with a bundled narrative (renderable) and an id.
 *  A completed match with no narrative stays in the manifest (recap-needed) but is never a hero. */
export function heroEntries(m: DailyManifest): { id: string; kickoffUtc: string | null }[] {
  return m.fixtures
    .filter(f => (f.renderable ?? true) && f.id)
    .map(f => ({ id: f.id as string, kickoffUtc: f.kickoffUtc }));
}

/** Minutes since the manifest was generated (for a subtle freshness/staleness indicator). */
export function manifestAgeMinutes(m: DailyManifest, now: Date = new Date()): number | null {
  if (!m.generated_at) return null;
  const t = Date.parse(m.generated_at);
  return Number.isNaN(t) ? null : Math.max(0, Math.round((now.getTime() - t) / 60000));
}
