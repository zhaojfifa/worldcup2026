// P1.3b — RUNTIME daily fixtures source (Owner verdict 2026-06-13: 能更新才是硬道理).
// The homepage reads the daily fixture registry at RUNTIME (fetch /data/daily-fixtures.json),
// not only at build time — so a cron that rewrites the manifest can refresh the live slate
// (once a hosted writable source exists; see GROWTH_P13B doc for the honest limitation).
// The build-time generated import is kept ONLY as a fallback when the fetch fails.
import fallbackManifest from './dailyFixtures.generated.json';
import { hasPredictionArtifact } from './predictionArtifacts';
import { getSelectedHotspot } from './selectedHotspot';
import homepageLifecycleRaw from './homepageLifecycle.json';

// P5B — the homepage match-lifecycle artifact (built by scripts/mvp2_homepage_lifecycle_selector.py).
// It DRIVES the homepage roles (primary/secondary/latest_recap) so the page FOLLOWS match progress
// instead of a fixed selectedHotspot board. A finished match is never the primary here.
interface LifecycleRole { fixture_id: string; match: string; lifecycle_state: string; active_content_role: string }
interface HomepageLifecycle {
  primary_prediction?: LifecycleRole | null; secondary_predictions?: LifecycleRole[];
  latest_recap?: LifecycleRole | null;
}
const HOMEPAGE_LIFECYCLE = homepageLifecycleRaw as HomepageLifecycle;

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

export interface ManifestFreshness {
  stored?: boolean; stored_at?: string; age_seconds?: number; stale?: boolean;
}
export interface DailyManifest {
  generated_for_date: string;
  generated_at: string;
  // The PUBLIC backend exposes the slate date as `date` (the bundled/static manifest uses
  // `generated_for_date`). Carried so normalization can map it; `freshness` is the backend's
  // upload-time staleness signal (time since the manifest was stored, not since the slate was built).
  date?: string;
  slate_date?: string;
  freshness?: ManifestFreshness;
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
// R2a — drift between the live backend slate and the bundled selected_hotspot.
//   MATCH    = backend is fresh + contains the selected hotspot → backend used.
//   FALLBACK = backend stale/date-missing/missing the selection → bundled/static fresh slate used.
//   BLOCKED  = even the fallback slate does not contain the selected hotspot (should never ship).
export type DriftStatus = 'MATCH' | 'FALLBACK' | 'BLOCKED';
export interface ManifestDrift {
  backendDate: string | null;
  backendAgeMin: number | null;
  selectedDate: string | null;
  selectedKey: string | null;
  backendContainsSelected: boolean;
  status: DriftStatus;
  reason: string;
}
export interface ManifestLoad { manifest: DailyManifest; source: ManifestSource; drift: ManifestDrift }

const STALE_HOURS = 36;

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
    if (!validManifest(m)) return null;
    // Normalize the backend slate-date field: the public endpoint returns `date`; downstream R2a
    // logic reads `generated_for_date`. Map it so a correctly-uploaded backend is not mis-read as
    // "no date" (which would wrongly force FALLBACK). Never invents a date.
    const mm = m as DailyManifest;
    if (!mm.generated_for_date) mm.generated_for_date = mm.date || mm.slate_date || mm.generated_for_date;
    return mm;
  } catch {
    return null;
  }
}

function containsKey(m: DailyManifest, key: string | null): boolean {
  return !!key && (m.fixtures ?? []).some(f => leadKey(f) === key);
}

/** R2a acceptance: the backend slate is authoritative ONLY when it is fresh (has a date, not older
 *  than the selection, not stale by age) AND actually contains the bundled selected hotspot. A
 *  stale / date-missing / mismatched backend must NOT silently override the fresh bundled content. */
function backendAcceptable(m: DailyManifest, selKey: string | null, selDate: string | null, now: Date):
  { ok: boolean; reason: string } {
  if (!selKey) return { ok: true, reason: 'no selected_hotspot bundled (legacy accept)' };
  if (!m.generated_for_date) return { ok: false, reason: 'backend manifest has no date' };
  if (!containsKey(m, selKey)) return { ok: false, reason: `backend slate does not contain selected ${selKey}` };
  if (selDate && m.generated_for_date < selDate)
    return { ok: false, reason: `backend date ${m.generated_for_date} older than selection ${selDate}` };
  if (m.freshness?.stale === true)
    return { ok: false, reason: 'backend manifest flagged stale by the backend freshness signal' };
  const age = manifestAgeMinutes(m, now);
  if (age != null && age > STALE_HOURS * 60)
    return { ok: false, reason: `backend manifest stale (${Math.round(age / 60)}h > ${STALE_HOURS}h)` };
  return { ok: true, reason: 'backend fresh and contains the selection' };
}

/** R2a fetch priority — backend ONLY if fresh AND it contains the selected hotspot; otherwise fall
 *  back to the bundled/static fresh manifest so a stale backend cannot override the fresh selection.
 *  NEVER throws; always returns a drift verdict for /internal/daily. */
export async function fetchDailyManifest(): Promise<ManifestLoad> {
  const sel = getSelectedHotspot();
  const selKey = sel?.fixture_key ?? null;
  const selDate = sel?.date ?? null;
  const now = new Date();
  const backend = await tryFetch(BACKEND_URL, 3500);
  if (backend) {
    const a = backendAcceptable(backend, selKey, selDate, now);
    if (a.ok) {
      return { manifest: backend, source: 'backend', drift: {
        backendDate: backend.generated_for_date ?? null, backendAgeMin: manifestAgeMinutes(backend, now),
        selectedDate: selDate, selectedKey: selKey, backendContainsSelected: containsKey(backend, selKey),
        status: 'MATCH', reason: a.reason } };
    }
    console.warn('[dailyFixtures] backend rejected (%s) → fresh bundled/static fallback', a.reason);
    const fb = (await tryFetch(STATIC_URL, 2500)) ?? null;
    const manifest = fb ?? FALLBACK_MANIFEST;
    const okFallback = !selKey || containsKey(manifest, selKey);
    return { manifest, source: fb ? 'static' : 'bundled', drift: {
      backendDate: backend.generated_for_date ?? null, backendAgeMin: manifestAgeMinutes(backend, now),
      selectedDate: selDate, selectedKey: selKey, backendContainsSelected: containsKey(backend, selKey),
      status: okFallback ? 'FALLBACK' : 'BLOCKED',
      reason: `backend rejected (${a.reason}); using ${fb ? 'static' : 'bundled'} fallback${okFallback ? '' : ' — fallback ALSO lacks the selection (BLOCKED)'}` } };
  }
  console.warn('[dailyFixtures] backend unavailable → static/bundled fallback');
  const stat = await tryFetch(STATIC_URL, 2500);
  const manifest = stat ?? FALLBACK_MANIFEST;
  const okFallback = !selKey || containsKey(manifest, selKey);
  return { manifest, source: stat ? 'static' : 'bundled', drift: {
    backendDate: null, backendAgeMin: null, selectedDate: selDate, selectedKey: selKey,
    backendContainsSelected: false, status: okFallback ? 'FALLBACK' : 'BLOCKED',
    reason: `backend unavailable; using ${stat ? 'static' : 'bundled'} fallback${okFallback ? '' : ' — fallback ALSO lacks the selection (BLOCKED)'}` } };
}

/** Hero-eligible entries = fixtures with a bundled narrative (renderable) and an id.
 *  A completed match with no narrative stays in the manifest (recap-needed) but is never a hero. */
export function heroEntries(m: DailyManifest): { id: string; kickoffUtc: string | null }[] {
  return m.fixtures
    .filter(f => (f.renderable ?? true) && f.id)
    .map(f => ({ id: f.id as string, kickoffUtc: f.kickoffUtc }));
}

// ── MVP2-P2 homepage product loop ──────────────────────────────────────────
// The product is a CLOSED LOOP around ONE daily hotspot match: predict → track →
// recap → next hotspot. The two featured slots are EDITORIAL (operator/LLM decide
// which match is the hotspot — NEVER a hardcoded popularity ranking). The operator
// expresses that decision via SLATE ORDER: the first finished fixture = yesterday's
// tracked hotspot (its recap lead), the first scheduled fixture = today's hotspot
// prediction. The frontend renders the confirmed order; it does not rank teams.
const FINISHED_STATES = new Set(['FINISHED', 'RECAP_PENDING', 'RECAP_READY', 'ARCHIVED']);

export interface ProductLoop {
  featuredRecap: DailyFixtureRow | null;       // tracked hotspot that just finished (recap lead)
  featuredPrediction: DailyFixtureRow | null;  // today's hotspot prediction
  otherRecaps: DailyFixtureRow[];              // remaining finished fixtures (secondary)
  secondarySchedule: DailyFixtureRow[];        // remaining scheduled fixtures (secondary)
}

/** The artifact-lookup key for a fixture (decoded): numeric id, else the manual fixture_key
 *  (external_game_id). Matches PredictionArtifact.fixture_key — NOT URL-encoded. */
export function leadKey(f: DailyFixtureRow): string | null {
  return f.id ?? f.external_game_id ?? null;
}

export function selectProductLoop(m: DailyManifest): ProductLoop {
  const fixtures = m.fixtures ?? [];
  const finished = fixtures.filter(f => FINISHED_STATES.has(f.lifecycle_state));
  const scheduled = fixtures.filter(f =>
    !FINISHED_STATES.has(f.lifecycle_state)
    && (f.preMatchAllowed ?? f.lifecycle_state === 'SCHEDULED'));
  // P7 P0-1 (Owner): selected_hotspot is the AUTHORITY for the lead — not slate order. The lead
  // must still resolve to a prediction artifact (P6 P0-2 gate kept).
  //  - selection present + in the slate + has an artifact → it is the lead.
  //  - selection present + in the slate but NO artifact → lead = null (NO silent fallback to a
  //    different match as the official pick; /internal/daily flags the readiness failure).
  //  - selection present but NOT in today's scheduled slate (e.g. already kicked off) → safe
  //    fallback to the first artifact-backed scheduled fixture.
  //  - no selection persisted → safe fallback (first artifact-backed scheduled).
  // P5B — LIFECYCLE-DRIVEN selection (Owner): the homepage follows match progress. The lifecycle
  // selector chose the primary (earliest upcoming source-qualified, NEVER finished), the secondary set
  // and the latest recap. Resolve those to manifest rows. Fall back to the selectedHotspot/slate logic
  // only when the lifecycle artifact has no primary (e.g. PRIMARY_REVIEW_REQUIRED) — never silently
  // promote a finished match.
  const lc = HOMEPAGE_LIFECYCLE;
  const byKey = (fk: string | undefined | null) => fk ? fixtures.find(f => leadKey(f) === fk) ?? null : null;
  const sel = getSelectedHotspot();
  const artifactBacked = () => scheduled.find(f => hasPredictionArtifact(leadKey(f))) ?? null;

  let featuredPrediction: DailyFixtureRow | null = null;
  const lcPrimary = byKey(lc.primary_prediction?.fixture_id);
  if (lcPrimary && !FINISHED_STATES.has(lcPrimary.lifecycle_state) && hasPredictionArtifact(leadKey(lcPrimary))) {
    featuredPrediction = lcPrimary;             // lifecycle primary (upcoming, source-qualified)
  } else if (!lc.primary_prediction) {
    // lifecycle says no valid primary → keep the legacy gate (selectedHotspot/artifact-backed) but
    // still never a finished match (scheduled-only).
    if (sel) {
      const selRow = scheduled.find(f => leadKey(f) === sel.fixture_key) ?? null;
      featuredPrediction = selRow ? (hasPredictionArtifact(leadKey(selRow)) ? selRow : null) : artifactBacked();
    } else {
      featuredPrediction = artifactBacked();
    }
  }

  // latest recap: lifecycle's pick (a finished match) → else first finished.
  const lcRecap = byKey(lc.latest_recap?.fixture_id);
  const featuredRecap = (lcRecap && FINISHED_STATES.has(lcRecap.lifecycle_state)) ? lcRecap : (finished[0] ?? null);

  // secondary: lifecycle's secondary set (resolved + scheduled), then any remaining scheduled.
  const lcSecondary = (lc.secondary_predictions ?? [])
    .map(r => byKey(r.fixture_id)).filter((f): f is DailyFixtureRow => !!f && !FINISHED_STATES.has(f.lifecycle_state));
  const secondarySchedule = [
    ...lcSecondary.filter(f => f !== featuredPrediction),
    ...scheduled.filter(f => f !== featuredPrediction && !lcSecondary.includes(f)),
  ];
  return {
    featuredRecap,
    featuredPrediction,
    otherRecaps: finished.filter(f => f !== featuredRecap),
    secondarySchedule,
  };
}

/** P7 P0-1/P0-2 — readiness verdict for the homepage lead vs the persisted selected_hotspot.
 *  Used by /internal/daily; pure, no fetch. */
export interface LeadReadiness {
  selectedKey: string | null;
  leadKey: string | null;
  selectionPresent: boolean;
  selectionInSlate: boolean;
  leadMatchesSelection: boolean;
  leadHasArtifact: boolean;
}
export function leadReadiness(m: DailyManifest): LeadReadiness {
  const sel = getSelectedHotspot();
  const { featuredPrediction } = selectProductLoop(m);
  const lk = featuredPrediction ? leadKey(featuredPrediction) : null;
  const inSlate = !!sel && (m.fixtures ?? []).some(f => leadKey(f) === sel.fixture_key);
  return {
    selectedKey: sel?.fixture_key ?? null,
    leadKey: lk,
    selectionPresent: !!sel,
    selectionInSlate: inSlate,
    leadMatchesSelection: !!sel && lk === sel.fixture_key,
    leadHasArtifact: hasPredictionArtifact(lk),
  };
}

/** Minutes since the manifest became authoritative. Prefer the backend's `freshness` (time since the
 *  manifest was UPLOADED — the operationally relevant signal); fall back to `generated_at` (the slate
 *  BUILD time) for the bundled/static manifest which has no freshness block. */
export function manifestAgeMinutes(m: DailyManifest, now: Date = new Date()): number | null {
  const fr = m.freshness;
  if (fr) {
    if (typeof fr.age_seconds === 'number') return Math.max(0, Math.round(fr.age_seconds / 60));
    if (fr.stored_at) {
      const ts = Date.parse(fr.stored_at);
      if (!Number.isNaN(ts)) return Math.max(0, Math.round((now.getTime() - ts) / 60000));
    }
  }
  if (!m.generated_at) return null;
  const t = Date.parse(m.generated_at);
  return Number.isNaN(t) ? null : Math.max(0, Math.round((now.getTime() - t) / 60000));
}
