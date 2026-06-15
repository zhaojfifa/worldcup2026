# P7 — IMPLEMENTATION_PLAN

> Proposed only. No implementation until an Owner GO. P0 = recover the mechanism + wiring + an operator surface,
> frontend/script-first, no required backend/schema change. P1 = reconnect the model/LLM content ENGINE (Owner-gated,
> needs API budget). Compliance floor unchanged.

## P0 — Mechanism + wiring + operator surface (frontend / scripts / artifacts + guards)

**P0-1 — Structured prediction-artifact schema.** Extend `PredictionArtifact` to carry the four content layers
explicitly: `data_snapshot` (model fields + `source_ref`/`assumption_flag`), `modeling_output` (score band / lean /
risk), `llm_judgment` (tactical / why / external / t30 copy), `operator_confirmation` (the confirmed call + overrides).
For MVP, `operator_confirmation` may stand alone (disclosed qualitative call, `confidence:null`); `data_snapshot`/
`modeling_output`/`llm_judgment` are optional until P1 fills them. Backwards-compatible with the current flat artifact.
Files: `frontend/src/data/predictionArtifacts.ts` (+ JSON shape), `check_prediction_artifact.py` (validate the new
optional blocks + require provenance when a model field claims to be data-derived).

**P0-2 — Wire `selected_hotspot_<date>.json` into the runtime.** Bundle the selected-hotspot record into the frontend
(build-time) and make `selectProductLoop` prefer it (then fall back to slate-order + `hasPredictionArtifact`). Guard:
the homepage lead MUST equal the selected hotspot, and the selected hotspot MUST have an artifact. Files:
`frontend/src/data/dailyFixtures.ts`, a small `selectedHotspot.ts` loader, `check_homepage_product_loop.py`.

**P0-3 — Persisted T-30 slot.** Add a `t30` block to the artifact (placeholder pre-lineups; `t30_update` filled at T-30)
so the T-30 correction is a real, persisted, honest checkpoint instead of in-group-only. UI already has `#live30`.
Files: artifact shape + `ArtifactTacticalRoom.tsx` (render placeholder vs update) + guard.

**P0-4 — Observation keyed by fixture_key (fix carryover).** Key `OBSERVATION` by the same `fixture_key`/`leadKey` the
slate uses, not numeric id only, so a manual hotspot carries over into next-day recap. Files: `predictionArtifacts.ts`
(`getObservationArtifact(key)`), `RecapDetailPage.tsx`, `HomeProductLoop.tsx` recap link, guard.

**P0-5 — Internal operator page `/internal/daily`** (admin-gated, no nav link) — the content-readiness panel from
`UPDATE_MECHANISM_PAGE_SPEC.md` Option A (reads the runtime manifest + bundled artifacts + selected_hotspot). Optional
terse public status line (Option B). Files: `frontend/src/pages/DailyStatusPage.tsx`, `App.tsx` route, reuse the
`/internal/growth` token-wall pattern.

**P0-6 — De-duplicate + de-stale the CLI.** Make `mvp2_growth_cli.py` source the recap "next match" hook from the
registry/observation (kill the hardcoded "Brazil vs Morocco"); ideally factor the scoreband/risk logic so the CLI mirror
and `strongCallProjection.ts` cannot drift. Files: `scripts/mvp2_growth_cli.py`.

**P0-7 — Prune dead code.** Remove or clearly quarantine `MatchDesk.tsx` (dead) and the unused `freshness.ts`
`pickActiveFixture`/`heroEntries`, so the live mechanism is unambiguous. Files: those two.

**P0-8 — Guards + docs.** Extend `check_prediction_artifact.py` (provenance + new blocks), `check_homepage_product_loop.py`
(lead == selected_hotspot), `check_growth_copy.py` (scan the new page + t30 + selected_hotspot). Update `P6_DAILY_WORKFLOW.md`
and refresh the stale `DAILY_UPDATE_FLOW.md`.

**Deploy impact (P0):** frontend-only (page + artifact shape + wiring) + scripts + docs. **No backend, no schema, no
runtime upload, no send.** A backend `GET /internal/daily-status` is explicitly NOT required for P0 (the page reads the
existing manifest + bundled data).

## P1 — Reconnect the content ENGINE (Owner-gated; needs API budget; deferred)

- **Model bridge:** `mvp2_match_sync` (or a new `mvp2_build_hotspot_frame`) runs the ScoutScore frame builder for the
  selected daily hotspot (Elo gap / form / H2H / Poisson bands / upset_band) → `data_snapshot` + `modeling_output` with
  `source_ref`/`assumption_flag`. Generalize off the hardcoded SAMPLES + Scout-Pack requirement (Elo/form/H2H need only
  team names + the kaggle CSV).
- **LLM bridge:** run the existing `mvp2_generate_*` generators + `check_mvp2_product_narrative_guard.py` for the hotspot
  to fill `llm_judgment` (tactical / why / external / t30 copy). DeepSeek default, Gemini benchmark.
- **External-signal generalization:** generalize `mvp2_project_external_signals.py` off the hardcoded TEAMS map so any
  fixture can carry a recorded-signal-backed external_expectation; guard requires a real recorded signal.
- **T-30 + A4 recap pipelines** for the hotspot: `mvp2_build_rescore_diff` (announced XI/GK) + the A4 model+LLM recap
  (archived-prediction sha256 provenance) → flip `recap_ready`.
- **Daily artifact scaffolder CLI** that chains: select → frame → narrate → assemble artifact (the missing generator).
- **(Optional) backend runtime store** for artifacts + a read-only daily-status endpoint (move artifacts off build-time
  bundling so content updates without a redeploy — the artifact analogue of the P1.3c slate store).

## Risks
- **Provenance honesty:** P0 still ships operator-confirmed numerics; the guard must DISCLOSE them as qualitative (not
  imply a model probability). Mitigation: `operator_confirmation` block + `confidence:null` + disclosed note.
- **Drift between selected_hotspot and the runtime lead:** mitigated by the P0-2 guard.
- **Public status leakage:** Option B must stay terse/customer-safe (no 生成中/待生成). Mitigated by guard + keep it Option A first.
- **P1 cost/compliance:** real LLM calls + model output reintroduce the "no fake probability / source_refs" discipline —
  keep win_prob/% out of the customer surface entirely.

## Rollback
Each P0 item is an independent frontend/script/docs commit on a feature branch; revert the commit (or the FF on main) and
redeploy the prior bundle. No backend/schema/data migration, so rollback is a frontend redeploy + (for scripts) a git revert.
No send is involved at any point.
