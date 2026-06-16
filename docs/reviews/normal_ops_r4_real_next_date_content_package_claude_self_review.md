# NORMAL OPS R4 · Claude Self-Review — Runtime Content Cutover (no daily frontend deploy)

Verdict: **OPERATE** (mechanism delivered + proven end-to-end locally). Live activation needs ONE
operator deploy of the runtime-first frontend + backend; thereafter daily content cutovers are
deploy-free. Production kept green throughout (R4 touched only a LOCAL backend).

## Problem R4 solves
Prediction/recap/selectedHotspot CONTENT was bundled in the frontend JS, so every daily content change
needed a frontend rebuild + Render deploy. R4 makes the frontend read content from a backend runtime
package FIRST, bundled content as fallback — so a daily cutover is a backend upload, no deploy.

## What changed
Backend (additive; reuses the runtime_manifests key/value table — NO schema migration):
- `app/services/runtime_content_service.py` — store/serve a content package (key runtime_content_current);
  empty-but-valid when none; freshness (age/stale) computed; send_status always HOLD.
- `app/routers/runtime_content.py` — GET /api/v1/runtime-content, GET /runtime-content/{date},
  POST /api/v1/admin/runtime-content/upload (x-admin-token; rejects empty predictions). Registered in main.
Frontend (runtime-first, bundled fallback):
- `data/runtimeContent.ts` — pure cache (no imports → no cycle): setRuntimeContent + getRuntimePrediction/
  Observation/SelectedHotspot/Lifecycle + fetchRuntimeContentRaw.
- `data/predictionArtifacts.ts` — getPredictionArtifact/getObservationArtifact prefer runtime, bundled fallback.
- `data/dailyFixtures.ts` — bootstrapRuntime() fetches the manifest (R2a) + runtime content, enables runtime
  ONLY when fresh AND its date == the EFFECTIVE manifest date AND predictions present (NEVER mixed dates);
  selectProductLoop prefers runtime lifecycle/selectedHotspot.
- `App.tsx` — awaits bootstrapRuntime() (idempotent, 3s timeout → bundled) before rendering routes, so deep
  links to /predict and /recap also see the runtime cache. HomePage reuses the same bootstrap.
Cutover + guards:
- `scripts/mvp2_runtime_content_cutover.py` — R3 sync+lifecycle+gate, then assembles the content package from
  the gate-verified artifacts and uploads BOTH the slate manifest and the runtime content (only on gate PASS;
  restore + CUTOVER_BLOCKED on fail). Token from $ADMIN_API_TOKEN, never printed.
- `check_r4_runtime_content_cutover` / `_frontend_runtime_first` / `_no_frontend_deploy_required` /
  `_no_mixed_date_runtime` (all --selftest green).

## Command
`python3 scripts/mvp2_runtime_content_cutover.py --date YYYY-MM-DD --source api-football --target production`

## End-to-end LOCAL proof (the core deliverable)
1. Local backend (runtime-content mechanism) + frontend built runtime-first (pointed at local backend).
2. Cutover 2026-06-15 (manual, noon) --target local → GATE PASS → uploaded slate (6) + content (3 predictions,
   1 observation), send HOLD.
3. /predict/1489377 rendered the RUNTIME content. THE NO-DEPLOY PROOF: a unique hook marker
   (俅哥运行时内容验证R4-NODEPLOY) was injected into the runtime package and re-uploaded; /predict then rendered
   the marker WITH NO REBUILD — **bundle hash identical (index-DgV6r1sD.js before and after)**.
4. CORS note: the local backend was restarted with the preview origin allowed (prod CORS already allows the
   prod frontend origin).

## Production safety
R4 uploaded ONLY to the LOCAL backend. Production backend has no runtime-content endpoint yet (GET returns
404) and stays on the green 06-15 baseline (live source-consistency PASS). The runtime-first frontend +
backend ship via ONE operator deploy; until then bundled content renders unchanged (fallback). No
backend SCHEMA migration (reused runtime_manifests). No homepage/product/UI redesign.

## Compliance
No fake score/event/lineup/injury/probability/confidence; no betting/odds/handicap; no auto-send/publish;
send HOLD everywhere. Token from untracked backend/.env, never printed/committed.

## Guards
4 R4 guards PASS (selftest) + R4 endpoint guard (local). Regression: R3 gate, R2 auto-refresh, prediction-
artifact provenance, growth-copy — all PASS. Prod-config frontend BUILD PASS; backend imports clean.

## Evidence
docs/qa_screenshots/normal_ops_r4_runtime_content_cutover/ (01-04 cutover + no-deploy proof text · 05 predict
runtime marker · 06 homepage runtime · 07 recap runtime observation · 08 internal-daily).

## Carryover
- ONE-TIME activation deploy (operator): deploy the runtime-first frontend + the runtime-content backend.
  After that, daily content cutover = `mvp2_runtime_content_cutover.py ... --target production` with NO deploy.
- After activation, run the live no-deploy proof on prod (upload content twice, bundle hash unchanged).
- LOW (inherited): sync side-writes the bundled FE manifest; the cutover snapshots/restores on block.
