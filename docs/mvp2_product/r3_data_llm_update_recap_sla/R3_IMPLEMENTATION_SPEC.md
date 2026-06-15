# R3 · R3_IMPLEMENTATION_SPEC

> Phase B spec. Minimum changes only. No UI redesign, no homepage redesign, no business-direction
> change, no backend schema change, no auto-send, no auto-LLM. Frontend + scripts + docs only.

## Guiding constraints

- Reuse existing artifacts/types; do not introduce new data shapes where one exists.
- Every customer-visible fact stays source-tagged; win_prob/confidence stay null.
- Send stays HOLD. Engineering holds no prod token; backend manifest upload is operator P1.

## P0 changes

### 1. `scripts/check_data_source_validity.py` (NEW)
Static + optional-live guard. Verifies:
- selected hotspot present/active; its artifact exists.
- artifact `source_facts.fixture_source`/`data_mode` valid; `source_refs` present when
  `model_fields.source=="computed"`.
- `model_fields.source` ∈ {computed, seed, operator_estimated, operator_confirmed, unavailable},
  clearly NOT mock; `win_prob`/`confidence` null; `no_fake_probability=true`.
- selected hotspot `date` not older than slate date (no stale-as-ready).
- `--base-url` (optional): live `/api/v1/daily-fixtures` freshness echoed; a stale backend is
  reported as WARN (R2a fallback covers it) unless `--strict`.
- `--selftest`.

### 2. `scripts/check_llm_grounding.py` (NEW)
Verifies the prompt→reviewed→artifact→page chain for the selected hotspot's artifact:
- `content_chain.prompt_path` exists on disk and contains the fixture key + `model_fields.source` +
  the "DO NOT INVENT" missing-fields line.
- if `reviewed_applied`: `reviewed_path` exists; reviewed JSON carries `main_lean`/`primary_score`
  and preserves model-derived facts (primary_score or risk_level consistent with model_fields).
- artifact `content_chain` points to both paths; `llm_judgment` OR `i18n.zh.prediction` present.
- no betting/fake-probability vocab in reviewed JSON.
- `--selftest`.

### 3. `scripts/check_daily_update_sla.py` (NEW)
Asserts SLA-state visibility (per DAILY_UPDATE_SLA.md): selected hotspot current; artifact ready;
T-30 explicit; FT/recap state explicit for finished tracked fixtures; send HOLD. `--selftest`.

### 4. `scripts/check_recap_pipeline.py` (NEW)
Verifies the recap route no longer leaks backend failure:
- `RecapDetailPage.tsx` gates `api.getRecap` (does NOT call it unconditionally — observation/
  product-narrative paths skip it).
- `predictionArtifacts.ts` exports `recapState`.
- every observation artifact has `recap_ready=false` (no fake recap) and full content fields.
- the carryover finished fixture resolves to a non-RECAP_ERROR state.
- `--selftest`.

### 5. Recap route fix — `frontend/src/pages/RecapDetailPage.tsx`
Gate the useEffect: compute `hasLocalRecapSource = !!(bundled product recap) || !!(observation
artifact)`; only call `api.getRecap` when there is NO local source (preserves 855737's backend path).
No change to what users see; removes the 404 leak.

### 6. Recap state helper — `frontend/src/data/predictionArtifacts.ts`
Add `export type RecapState = 'OBSERVATION_READY'|'RECAP_PENDING'|'RECAP_READY'|'RECAP_ERROR'` and
`export function recapState(key, hasProductRecap): RecapState`. Pure, no I/O.

### 7. Full recap vs observation for 1489371
Keep 1489371 as **explicit observation-only** (`recap_ready=false`). Document in the artifact `note`
that a full recap is intentionally not authored (insufficient archived narrative). Do NOT fabricate.

### 8. `/internal/daily` strengthening — `frontend/src/pages/DailyStatusPage.tsx`
Add rows (text/state only, no redesign):
- **Data source validity** — `model_fields.source` + `source_facts.data_mode` + computed/estimated.
- **LLM grounding** — content_chain prompt+reviewed present + provider.
- **Update SLA state** — derived: slate-current / artifact-ready / T-30 / recap.
- **Recap SLA state** — `recapState` for the carryover fixture (named state, not just present/absent).
- **Last successful generation** — `content_chain.built_at` / artifact date.
- **Next required operator action** — derived hint (e.g. "upload backend manifest" when source≠backend;
  "build full recap or keep observation" for the carryover).
- **Send HOLD** — already present; keep.

## Out of scope (explicitly NOT doing)
- No homepage/predict redesign. No new visual components beyond text rows.
- No backend lifecycle enum change, no new DB table/route.
- No auto-LLM, no auto-send, no payment/token/betting.
- No backend manifest upload (operator P1, prod token).

## Required checks after implementation
`npm run build`; existing 8 guards; the 4 new guards (+ `--selftest` each);
live `check_customer_visible_copy.py`, `check_runtime_daily_fixtures.py` (live backend stale ⇒ known
P1, reported honestly).
