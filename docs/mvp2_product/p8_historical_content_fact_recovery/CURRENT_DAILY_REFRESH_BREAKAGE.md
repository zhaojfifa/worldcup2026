# P8 — CURRENT_DAILY_REFRESH_BREAKAGE

> How the daily-refresh path (P1.3 `mvp2_match_sync` + manifest + prediction artifacts) bypassed the old
> content-fact layer. Diagnosis: this is a **mapping / route-resolution loss**, NOT data absence and NOT
> content-generation deletion. Every producer still exists.

## What `daily_fixtures` currently carries

`DailyFixtureRow` (`frontend/src/data/dailyFixtures.ts`) and the backend
`daily_fixtures_service.py` carry **only**: `id`, `external_game_id`, `home`, `away`, `kickoffUtc`,
`status`, `lifecycle_state`, `preMatchAllowed`, `recapReady`, `recapNeeded`, `renderable`,
`heroCandidate`/`recapCandidate`/`nextCandidate`, `scoreHome`/`scoreAway`. **Verified:**
`git grep 'win_prob|recommended_score|risk_level|confidence' backend/app/services/daily_fixtures_service.py`
returns **nothing**. The manifest is, by construction, **identity + lifecycle + final-score only**. No
model fields, no judgement fields.

## What `selected_hotspot` currently carries

`selectedHotspot.json`: `date`, `fixture_key`, `home`, `away`, `source`, `prediction_artifact_path`,
`operator_confirmed`, `status`. It is a **pointer/selector** (which fixture is today's lead + where its
artifact lives), not a content store. Correct by design — it should stay a selector.

## What the prediction artifact currently carries

`manual_Nether-Japan-20260614.json`: full **qualitative** judgement (`primary_direction`, `score_call`
"2-1", `backup_score`, `risk_level` "中高", `risk_note`, `top_variable`, `why`, tactical bullets, risk
variables, external expectation, 30-min checklist, share/join copy) — **all `field_sources =
operator_confirmed`**. But the **structured model layer is empty**: `win_prob` and `confidence` =
`"unavailable"`; `data_snapshot` / `modeling_output` / `generated_judgment` = `null`; `confidence` value
= `null`. The artifact's own `note` says these "stay null until the P1 model + generation bridge fills
them." So the *sockets exist*; the *bridge does not*.

## Which old fields are missing (for the daily hotspot)

- **Structured numeric tier:** `win_prob`, numeric `confidence`, `recommended_score` (as a model
  output) — present in `baseline.py`/`/matches`, absent from the manifest/artifact for `id=null`.
- **Real-data provenance on judgement fields:** `risk_factors` historically carried `source_refs` +
  `assumption_flag` (LLM over a ScoutScore frame); the manual artifact's `risk_variables` have **no
  provenance**.
- **Model-derived score/lean/risk:** historically `scoreline_view`/`main_lean`/`risk_level` came from
  Poisson/Elo/upset_band → LLM; for the manual hotspot they are hand-typed with no model behind them.

## Which old fields are hand-filled now

Everything judgement-shaped for the daily hotspot: `score_call`, `risk_level`, `risk_note`,
`primary_direction`, `top_variable`, `why`, `tactical_matchup`, `risk_variables`, `external_expectation`,
`thirty_minute_checklist`, all share/join copy. Provenance = `operator_confirmed`. This is honest but
**does not scale past ~1 fixture/day and carries no model/LLM backing** (P6 finding, still true).

## Which old APIs / scripts are bypassed

- **`/api/v1/matches`** (+ `match_service.py` + `baseline.predict` + `transform.listItemToMatch`): still
  live, still imported by `useAppStore`, but the homepage product loop reads the **manifest** instead, so
  the model-field path renders only the demoted mock tiles. Bypassed for the daily hotspot.
- **ScoutScore generator chain** (`mvp2_build_scoutscore_v0_2_factors.py` →
  `mvp2_generate_*_narratives.py` → guard → `productNarratives/*.json`): never invoked by
  `mvp2_match_sync.py`. The daily slate is produced without ever running the model/LLM generators, so a
  new fixture gets no narrative — hence the operator-only artifact.
- **`mvp2_project_external_signals.py`**: hardcoded to a TEAMS map (only 1489371) → not run for new
  fixtures.

## Why manual fixtures have `id=null` and no model fields

`mvp2_match_sync.KNOWN` maps only **3 verified fixtures** to an internal id/kickoff. A fixture not in
`KNOWN` (e.g. Netherlands–Japan) gets `internal_fixture_id=null` and a `manual:<...>` slug — **by design,
to never fake a real id**. With `id=null` there is (a) no `Prediction` DB row to read numeric model
fields from, and (b) no entry in the hardcoded 5-id `ProductNarrative` map. So both historical content
tiers fail to resolve, and the operator artifact is the only remaining source.

## Why homepage / predict are artifact-backed but not model-backed

The P4→P7 recovery deliberately made the artifact the resolution target for `id=null` (so the slate can
update without a rebuild — "能更新才是硬道理"). That restored the **update mechanism and the shell** but
chose `operator_confirmed` as the only provenance, leaving the `model_fields`/`data_snapshot` sockets
null. The homepage score hook (`buildStrongCall` → `buildStrongCallFromArtifact`) reads the operator
`score_call`; it never reaches a model output because none is attached.

## Root-cause classification

**This is primarily a MAPPING / ROUTE-RESOLUTION loss, secondarily a CONTENT-GENERATION-wiring loss —
NOT data absence and NOT deletion:**

1. **Mapping loss (primary):** the daily manifest schema and the `id=null` key drop the join to both the
   backend `Prediction` model fields and the bundled `ProductNarrative`. The boundary is the manifest /
   artifact key, not a missing producer.
2. **Generation-wiring loss (secondary):** the ScoutScore→LLM generator that historically produced the
   rich, provenanced fields was never connected to the daily slate, so a new fixture has no model/LLM
   content to map even if the key resolved.
3. **NOT data absence:** `baseline.py`, the ScoutScore frame builder, the kaggle data, and the LLM keys
   (local) all still exist and run.
4. **NOT route-render loss:** `/predict`, `/recap`, `/share` all render fine; they just render the
   thinner operator artifact because that is the only source attached to the route.

**Implication for recovery:** the fix is a **bridge/generator + a `model_fields` socket fill**
(frontend/scripts/docs), not a re-implementation of the model or the page. See
`FIELD_RECONNECTION_PLAN.md`.
