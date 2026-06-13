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
const RUNTIME_URL = '/data/daily-fixtures.json';

export interface ManifestLoad { manifest: DailyManifest; source: 'runtime' | 'fallback' }

/** Fetch the runtime manifest; fall back to the bundled build-time data on ANY failure.
 *  Never throws — a missing/broken runtime file must not crash the homepage. */
export async function fetchDailyManifest(): Promise<ManifestLoad> {
  try {
    const res = await fetch(RUNTIME_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const m = (await res.json()) as DailyManifest;
    if (!m || !Array.isArray(m.fixtures) || m.fixtures.length === 0) throw new Error('empty manifest');
    return { manifest: m, source: 'runtime' };
  } catch (e) {
    console.warn('[dailyFixtures] runtime fetch failed → bundled fallback:', e);
    return { manifest: FALLBACK_MANIFEST, source: 'fallback' };
  }
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
