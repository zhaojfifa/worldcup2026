// R4 — runtime CONTENT cache (Owner GO 2026-06-16: daily content cutover without a frontend deploy).
//
// The backend serves a daily CONTENT package (prediction artifacts + observation artifacts +
// selectedHotspot + lifecycle) at GET /api/v1/runtime-content. dailyFixtures.bootstrapRuntime()
// fetches it, validates freshness + that its date matches the EFFECTIVE daily-manifest date (so the
// homepage never shows mixed backend/frontend dates), and calls setRuntimeContent(). The content
// accessors below then prefer runtime content; bundled artifacts remain the fallback.
//
// This module has NO imports (pure cache) so predictionArtifacts.ts / dailyFixtures.ts can both use it
// without an import cycle. Nothing here invents content; it only surfaces what was uploaded.

export interface RuntimeContentPackage {
  date: string | null;
  generated_at?: string | null;
  source_mode?: string | null;
  selectedHotspot?: any;
  lifecycle?: any;
  predictions?: Record<string, any>;
  observations?: Record<string, any>;
  shares?: Record<string, any>;
  freshness?: { stored?: boolean; stale?: boolean; age_seconds?: number };
}

let RC: RuntimeContentPackage | null = null;   // gated, validated package (or null → use bundled)
let RC_DATE: string | null = null;

/** Called by the bootstrap AFTER it has validated freshness + date-match. Pass null to clear. */
export function setRuntimeContent(pkg: RuntimeContentPackage | null): void {
  RC = pkg && pkg.date ? pkg : null;
  RC_DATE = RC?.date ?? null;
}

export function runtimeActive(): boolean { return RC != null; }
export function runtimeDate(): string | null { return RC_DATE; }
export function runtimeSource(): string | null { return RC?.source_mode ?? null; }

/** A prediction artifact from the runtime package, by fixture_key or numeric id. null → use bundled. */
export function getRuntimePrediction(key: string | null | undefined): any | null {
  if (!RC || !key) return null;
  const preds = RC.predictions || {};
  if (preds[String(key)]) return preds[String(key)];
  for (const a of Object.values(preds)) {
    if (a && (String((a as any).fixture_key) === String(key) || String((a as any).id) === String(key))) return a;
  }
  return null;
}

/** An observation/recap artifact from the runtime package. null → use bundled. */
export function getRuntimeObservation(key: string | null | undefined): any | null {
  if (!RC || !key) return null;
  const obs = RC.observations || {};
  if (obs[String(key)]) return obs[String(key)];
  for (const a of Object.values(obs)) {
    if (a && (String((a as any).id) === String(key) || String((a as any).fixture_key) === String(key))) return a;
  }
  return null;
}

export function getRuntimeSelectedHotspot(): any | null { return RC?.selectedHotspot ?? null; }
export function getRuntimeLifecycle(): any | null { return RC?.lifecycle ?? null; }

/** Fetch the raw runtime-content package from the backend (no validation here). */
export async function fetchRuntimeContentRaw(apiBase: string, signal?: AbortSignal): Promise<RuntimeContentPackage | null> {
  try {
    const res = await fetch(`${apiBase}/api/v1/runtime-content`, { cache: 'no-store', signal });
    if (!res.ok) return null;
    return (await res.json()) as RuntimeContentPackage;
  } catch {
    return null;
  }
}
