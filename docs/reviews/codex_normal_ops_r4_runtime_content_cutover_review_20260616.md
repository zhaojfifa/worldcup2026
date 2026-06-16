# Codex Independent Adversarial Review — NORMAL OPS R4 (Runtime Content Cutover)

- Branch: `ops/r4-runtime-content-cutover` · HEAD `d53a230`
- Reviewer: Codex (independent, adversarial)
- Date: 2026-06-16
- Scope reviewed: R4 = move daily prediction/recap/selectedHotspot CONTENT to a backend RUNTIME
  package; frontend reads runtime content FIRST, bundled as fallback; daily cutover = one command,
  no frontend deploy; no mixed backend/frontend dates.

## OVERALL VERDICT: **PASS**

The mechanism is sound and proven both by source inspection and by an empirical local backend run.
Backend is additive (reuses `runtime_manifests`, no migration), public read is empty-but-valid,
admin upload is token-gated and rejects empty predictions, freshness is computed, send stays HOLD.
Frontend prefers runtime content but only when it is fresh AND date-matched AND has predictions —
otherwise it falls back to bundled. Production is untouched and green; the runtime-content endpoint
is not yet live (404). Two LOW non-blocking observations recorded; nothing rises to a patch.

---

## Check 1 — Diff scope / no migration

`git diff main...HEAD --stat` change set matches the brief exactly:
- backend: `app/main.py` (register only, +1 router line), `app/routers/runtime_content.py` (new),
  `app/services/runtime_content_service.py` (new).
- frontend: `App.tsx`, `data/runtimeContent.ts` (new), `data/predictionArtifacts.ts`,
  `data/dailyFixtures.ts`, `pages/HomePage.tsx`.
- scripts: `mvp2_runtime_content_cutover.py` + 4 `check_r4_*.py`.
- docs/reviews + evidence (JSON package, cutover record, 4 screenshots, proof txt, self-review).

No homepage/product UI redesign (HomePage diff is a 1-line swap `fetchDailyManifest`→`bootstrapRuntime`;
backend/app/main.py:11,50 register-only). **No DB migration file** in the diff (no alembic/migrations).
`runtime_content_service.py:21,23` reuses `RuntimeManifest` (`models/runtime_manifest.py:26-33`,
table `runtime_manifests`) under a NEW key `runtime_content_current` — additive key, no new table/column.

DIFF_SCOPE_OK=yes · NO_SCHEMA_MIGRATION=yes · NO_PRODUCT_UI_REDESIGN=yes

## Check 2 — Backend correctness (source + EMPIRICAL)

Source (`runtime_content.py`): GET `/api/v1/runtime-content` is public (`:31-33`); empty-but-valid
returned when nothing stored or date mismatch (`runtime_content_service.py:73-77`, no 500). POST
`/admin/runtime-content/upload` calls `require_admin` (`:23-28`, 401 if token unset/missing/wrong) and
rejects a missing date (422, `:45-46`) and empty/absent `predictions` (422, `:47-48`). `send_status`
is forced to `HOLD` in normalize and in the response (`service:36,41`; router `:52`). Freshness
(age_seconds/stale at 36h) computed in `assemble_response` (`:78-90`).

Empirical (local backend `:8013`, throwaway token, killed after):
- GET runtime-content → 200 (returned a package; local dev sqlite was pre-populated by a prior local
  cutover). The empty-but-valid shape was directly exercised via GET `/runtime-content/2026-06-14`
  (date mismatch) → 200 `{"date":null,...,"predictions":{},"freshness":{"stored":false}}` — same code
  branch as the no-row case, confirming empty-but-valid + no 500.
- POST upload WITHOUT token → **401**.
- POST upload WITH `x-admin-token: cdxr4` of the sample `{date,predictions{1489377}}` → **`stored:true`**;
  subsequent GET returned it.
- POST `{"date":"x","predictions":{}}` → **422** (empty predictions rejected).

BACKEND_RUNTIME_CONTENT_OK=yes

## Check 3 — Frontend runtime-first + no-mixed-date

- `runtimeContent.ts` has **no `import` statements** (pure cache) → no import cycle (verified line scan;
  guard `check_r4_frontend_runtime_first` also asserts this).
- `predictionArtifacts.ts:199-204` `getPredictionArtifact` calls `getRuntimePrediction(key)` and returns
  it BEFORE `PREDICTION.find(...)`; `:220-224` `getObservationArtifact` checks `getRuntimeObservation`
  before `OBSERVATION.find(...)`. Bundled arrays retained as fallback.
- `dailyFixtures.ts:178-205` `bootstrapRuntime` enables runtime content only when
  `pkg && fresh && dateMatch && hasContent` where `fresh` = stored && !stale && age_seconds ≤ 36h
  (`:185-187`), `dateMatch` = `pkg.date === effectiveDate` (`:188`, effectiveDate =
  `load.manifest.generated_for_date`, `:182`), `hasContent` = non-empty predictions (`:189`); else
  `setRuntimeContent(null)` → bundled (`:193`). There is no path where a runtime package of a
  DIFFERENT date than the slate is used. `selectProductLoop` prefers runtime lifecycle/selectedHotspot
  (`:264,266`) but resolves every role against the manifest slate via `byKey`, so a runtime ref not in
  the slate degrades to the bundled/fallback selection.
- `App.tsx:27-37` awaits `bootstrapRuntime()` before rendering routes, with a 3s `setTimeout(done)` so
  it never hangs; deep links to `/predict` and `/recap` therefore see the populated cache.

FRONTEND_RUNTIME_FIRST=yes · NO_MIXED_DATE=yes · BUNDLED_FALLBACK_RETAINED=yes

## Check 4 — No-deploy claim

Sound from the code: content accessors read RC at call time and override bundled, RC is populated by a
runtime fetch (no rebuild), and RC is null whenever the package is absent/stale/wrong-date — bundled is
the safe fallback. So a content change is a backend upload, not a frontend build. The self-review
(`...claude_self_review.md:3-5,37-51,66-68`) explicitly states a ONE-TIME activation deploy of the
runtime-first frontend + runtime-content backend is required before the live no-deploy behavior is
active, and that until then bundled content renders unchanged. Caveat correctly disclosed.

NO_FRONTEND_DEPLOY_FOR_DAILY_CONTENT=yes (with the one-time activation deploy caveat, disclosed)

## Check 5 — R4 guards (non-vacuous, all PASS)

- `check_r4_runtime_content_cutover --selftest`: 6/6 (assembles a real package from artifacts; asserts
  date, HOLD, non-empty predictions, selectedHotspot, primary 1489377, recap 1489371).
- `check_r4_frontend_runtime_first --selftest`: 6/6 (string-orders `getRuntimePrediction` before
  `PREDICTION.find`, etc.; asserts no-import cache).
- `check_r4_no_frontend_deploy_required --selftest`: 4/4 (override path + bundled fallback both present).
- `check_r4_no_mixed_date_runtime --selftest`: 5/5 (asserts `pkg.date === effectiveDate` gate).
- `mvp2_runtime_content_cutover --selftest`: 3/3 (delegates to the R3 gate selftest: data-only blocked,
  finished primary blocked, missing registry blocked).
Each inspects real wiring (not vacuous).

## Check 6 — Cutover safety

`mvp2_runtime_content_cutover.py`: `run()` runs the R3 gate (`:117`); on FAIL it restores the snapshot,
writes `CUTOVER_BLOCKED`, uploads nothing, returns 2 (`:118-125`). Upload happens only `if do_upload and
target` after a gate PASS (`:131-139`); `do_upload = bool(target) or upload`. `assemble_package`
(`:71-93`) pulls from existing `selectedHotspot.json`/`homepageLifecycle.json`/`dailyContentQueue.json`
+ on-disk prediction/observation artifacts — no fabrication; send_status HOLD baked in (`:92`). Token
read from `$ADMIN_API_TOKEN` (`:132`) and passed only as a header in `_post`; it is never printed (only
server responses are printed, `:137-138`). HOLD echoed (`:147`).

CUTOVER_UPLOADS_ONLY_AFTER_GATE=yes

## Check 7 — Production untouched / green

- `check_live_source_consistency.py` (prod URLs): PASS — backend_date=2026-06-15, active_date=2026-06-15,
  primary=1489377 (06-15 baseline intact).
- `curl https://worldcup2026-api-71n6.onrender.com/api/v1/runtime-content` → **404** (mechanism not yet
  deployed; R4 only touched a local backend).

PRODUCTION_GREEN_UNTOUCHED=yes

## Check 8 — Compliance

Scan of added lines in the new backend/frontend/script files: the only hits for
betting/odds/handicap/auto-send/win_prob/confidence are NEGATION comments/docstrings ("No auto-send",
"NO user/payment data", win_prob/confidence stays null in the bundled artifact interface — unchanged by
R4). No fabricated probability/confidence introduced; the runtime layer only stores/serves opaque
product content. `send_status` HOLD everywhere. The backend service holds only public product content
(selectedHotspot/predictions/observations/shares/lifecycle); no user/payment/attribution fields.

FAKE_DATA=none · BETTING_VOCAB=none · AUTO_SEND=none · SEND_STATUS=HOLD

## Check 9 — Secret scan

- `git grep -lc "<REDACTED_ADMIN_TOKEN — per Owner security boundary; scrubbed 2026-06-16>" -- . ':!*.png'` → **no matches** (token value absent from all tracked files).
- `backend/.env` is NOT tracked (`git ls-files` empty).
- `git diff main...HEAD` introduces no `.env`/token file.

ADMIN_TOKEN_LEAK=false

---

## Defects / Observations

- **LOW (non-blocking, robustness):** in `bootstrapRuntime`, `fetchRuntimeContentRaw(API_BASE)`
  (dailyFixtures.ts:184) is called WITHOUT an AbortController/timeout signal, unlike the manifest
  `tryFetch` (3500ms). A hanging (not failing) backend connection would leave the bootstrap promise
  pending. Impact is mitigated to nil: App.tsx has its own 3s render guard, and HomePage's initial
  `daily` state already defaults to `FALLBACK_MANIFEST` (HomePage.tsx:57-59), so the homepage renders
  bundled content regardless. Consider passing a timeout signal for tidiness; not required.
- **LOW (non-blocking):** the upload endpoint validates `date` presence but not format (a value like
  "x" is accepted; the 422 in the test came from empty predictions). Harmless here because the
  cutover script always supplies an ISO date and the frontend `pkg.date === effectiveDate` gate makes
  a malformed date fall back to bundled. Optional hardening.

## Confirmation lines

DIFF_SCOPE_OK=yes
NO_SCHEMA_MIGRATION=yes
BACKEND_RUNTIME_CONTENT_OK=yes
FRONTEND_RUNTIME_FIRST=yes
NO_MIXED_DATE=yes
BUNDLED_FALLBACK_RETAINED=yes
NO_FRONTEND_DEPLOY_FOR_DAILY_CONTENT=yes (one-time activation deploy caveat noted + disclosed in self-review)
CUTOVER_UPLOADS_ONLY_AFTER_GATE=yes
PRODUCTION_GREEN_UNTOUCHED=yes
FAKE_DATA=none
BETTING_VOCAB=none
AUTO_SEND=none
SEND_STATUS=HOLD
ADMIN_TOKEN_LEAK=false
NO_PRODUCT_UI_REDESIGN=yes
