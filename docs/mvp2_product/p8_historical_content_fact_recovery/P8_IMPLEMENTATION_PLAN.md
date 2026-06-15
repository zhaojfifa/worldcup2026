# P8 — P8_IMPLEMENTATION_PLAN

> Proposed only after discovery. **NOTHING here is implemented.** P0 is strictly frontend / scripts /
> docs (no backend route, no DB table, no schema migration, deploy = frontend bundle only). P1 is the
> heavier model/LLM/backend work that each needs its own Owner GO. The compliance floor (no fake
> probability, no auto-send) holds throughout. P7's `selected_hotspot` mechanism is **preserved**.

## P0 — reconnect + surface provenance (frontend / scripts / docs only)

1. **Schema: add the `model_fields` / `source_facts` socket to the artifact.** Formalise
   `model_fields` (was the null `modeling_output`) + `source_facts` on `PredictionArtifact`
   (`frontend/src/data/predictionArtifacts.ts`). Back-compat: legacy `i18n`/`field_sources` still drive
   render. Per `TARGET_CONTENT_FACT_SCHEMA.md`. *(Owner Q3, Q5)*

2. **Populate the current hotspot's artifact** (`manual_Nether-Japan-20260614.json`) with a
   `source_facts` + `model_fields` object. If Owner Q1/Q3 = no computed source yet →
   `source:"unavailable"`, numerics `null`, `has_model_fields:false` (honest). If a P0-lite
   ScoutScore frame is run (Owner Q6) → `risk_level`/`recommended_score` with `source:"computed"` +
   `source_refs`.

3. **`/predict` data-backed content block.** Add a "model read" block to `ArtifactTacticalRoom.tsx`
   (and the strong path) that renders `model_fields` **with its source tag** — or a "model read pending /
   operator call" label when `unavailable`. **Never** render a bare `win_prob`/`confidence` without its
   source. *(Owner Q1, Q3, Q4)*

4. **Homepage score hook reads `model_fields` first, then operator artifact fallback.** Extend
   `buildStrongCall`/`buildStrongCallFromArtifact` (`strongCallProjection.ts`) precedence:
   `model_fields` (computed/seed) → operator artifact → null. No new probability surfaced unless
   authorized. *(Owner Q4)*

5. **`/internal/daily` shows `source_facts` / `model_fields` readiness.** Extend `DailyStatusPage.tsx`
   to display `data_mode`, `has_model_fields`, and per-field `source` for the lead — so the operator sees
   the data-backing state at a glance. *(Owner Q4)*

6. **Guards assert source/status, not fake values.** Extend `check_prediction_artifact.py` +
   `check_homepage_product_loop.py` to require a `source_facts` block and a `model_fields.source` tag
   (and the P6 score-call hook), and to **reject** a numeric `win_prob`/`confidence` whose `source` is
   `operator_*` or `unavailable`. No assertion that any number exists.

7. **(Optional P0-lite) deterministic ScoutScore frame, no LLM.** A small
   `scripts/mvp2_build_daily_prediction.py` that runs only the kaggle ScoutScore *frame*
   (Elo/form/H2H/Poisson `upset_band`) for the daily fixture → emits `model_fields`
   (`risk_level`/`recommended_score`, `source:"computed"`, `source_refs`), leaving prose
   operator-authored. Operator-confirm gate preserved. *(Owner Q6)*

8. **Preserve P7 `selected_hotspot`.** No change to `selectedHotspot.json`/`.ts` selection logic; P8 only
   fills the artifact it already points to. *(Owner Q5)*

**P0 deploy impact:** frontend bundle only (rendered changes) + docs/scripts (schema, guard, optional
frame builder). No backend, no DB, no endpoint. Rollback = frontend revert + prior-bundle redeploy.
No-send posture untouched.

## P1 — real model + generation + runtime store (each its own GO)

1. **Full daily prediction generator with LLM + provenance** (Option C full): ScoutScore frame →
   DeepSeek/Gemini for `main_lean`/`risk_factors` with `source_refs` → guard → artifact
   `model_fields` + `llm_judgment`. Scales past 1 fixture/day; restores Era-1 quality for any fixture.
2. **Automated DeepSeek/Gemini/Kimi prompt execution** wired into the daily slate (still operator-confirm
   before live; no auto-send).
3. **API-FOOTBALL expansion** so new fixtures get a real `fixture_id`/kickoff (shrinks the `id=null`
   manual case).
4. **Backend runtime artifact store** (Option E): persist full artifacts (incl. `model_fields`) behind
   `GET /api/v1/daily-fixtures`, admin upload — no-rebuild content updates. **Backend/schema change → own GO.**
5. **External signal refresh:** generalize `mvp2_project_external_signals.py` off its hardcoded TEAMS map;
   guard requires a recorded signal.
6. **A4 full recap pipeline** (`mvp2_build_recap_frame_real.py` → LLM `real_recap` with sha256 provenance)
   to replace the operator observation receipt for the daily hotspot.

## Sequencing

P0 items 1–6 are one frontend/scripts slice (ships together, deploy = bundle). Item 7 is an optional
add-on if Owner authorizes a computed source now. P1 items are independent and each gated. Recommended:
ship P0 (provenance-honest sockets + readiness) first so the product **declares** its data-backing state,
then add the generator (P1.1) to actually fill it with real-data provenance.
