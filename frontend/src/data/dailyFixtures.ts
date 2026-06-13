// P1.3 — daily fixture registry → homepage active manifest.
// The hero source is the GENERATED registry manifest (scripts/mvp2_match_sync.py), not a
// hardcoded fixture list. Only renderable fixtures (those with a bundled narrative) appear
// here, so the hero can always back a real customer surface. Falls back to the bundled
// upcoming fixtures if the manifest is empty (e.g. before the first sync).
import manifest from './dailyFixtures.generated.json';
import { UPCOMING_FIXTURES } from './upcomingFixtures';

export interface DailyManifestFixture {
  id: string;
  home: string;
  away: string;
  kickoffUtc: string | null;
  status: string;
  lifecycle_state: string;
  recapReady: boolean;
  heroCandidate: boolean;
  recapCandidate: boolean;
  nextCandidate: boolean;
}

export interface ActiveEntry { id: string; kickoffUtc: string | null }

const ROWS = ((manifest as { fixtures?: DailyManifestFixture[] })?.fixtures ?? []);

/** Registry-driven candidate ids for the homepage hero (recapReady is recomputed LIVE from
 *  the bundled narrative by the caller, never trusted from the possibly-stale manifest). */
export function activeFixtureEntries(): ActiveEntry[] {
  if (ROWS.length) return ROWS.map(r => ({ id: r.id, kickoffUtc: r.kickoffUtc }));
  return UPCOMING_FIXTURES.map(f => ({ id: f.id, kickoffUtc: f.kickoffUtc }));
}

export const MANIFEST_DATE: string | null =
  (manifest as { generated_for_date?: string })?.generated_for_date ?? null;
