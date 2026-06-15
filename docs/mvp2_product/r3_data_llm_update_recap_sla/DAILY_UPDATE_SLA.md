# R3 · DAILY_UPDATE_SLA

> Phase A — audit only. Audited 2026-06-15. Defines the daily operating contract so "能更新" is
> not just possible but RELIABLE. Times are UTC, relative to the day's key kickoff (KO).
> Owner gate stays: send = HOLD; every send needs explicit per-channel GO.

## State machine (one editorial day)

| State | Owner | Input | Output | Deadline | Guard | Failure mode | Customer fallback |
|-------|-------|-------|--------|----------|-------|--------------|-------------------|
| **A. Morning slate sync** | operator | `manual_scores_YYYYMMDD.md` (+ optional API fetch) | `daily_fixtures_YYYYMMDD.json`, `recap_queue_*`, `dailyFixtures.generated.json`, `public/data/daily-fixtures.json` | by 10:00 UTC | `mvp2_match_sync.py --selftest`; `check_runtime_daily_fixtures.py` (code wiring) | slate not regenerated → stale lifecycle | bundled/static manifest (R2a) |
| **B. Hotspot selection** | operator | slate + editorial judgement | `selectedHotspot.json` (status=active) + audit mirror | by 11:00 UTC | `check_daily_readiness.py` step1; `check_homepage_product_loop.py` (selection==lead) | no/stale selection → homepage lead wrong | R2a: stale selection FAILS go-live (won't ship) |
| **C. Prediction generation** | operator | selected hotspot + ScoutScore | prompt → reviewed JSON → prediction artifact (`model_fields`+`llm_judgment`+`content_chain`) | by 13:00 UTC | `check_daily_content_flow.py`; `check_prediction_artifact.py`; `check_llm_grounding.py` (R3) | artifact missing/incomplete → hollow lead | `hasPredictionArtifact` gate blocks hollow hero |
| **D. T-30 update** | operator | lineups released (KO−30) | artifact `t30.status` pending→ready/skipped, `update_text` | KO−30 to KO | `check_prediction_artifact.py` (t30 valid, pending⇒no faked text); `check_daily_update_sla.py` (R3) | faked update / no re-check | t30 stays `pending` honestly (no faked text) |
| **E. Full-time observation** | operator | API-FOOTBALL FT score | `observation_{id}.json` (recap_ready=false) | FT+45 min | `check_prediction_artifact.py` (observation, no fake recap); `check_recap_pipeline.py` (R3) | no observation for finished hotspot | OBSERVATION page (receipt), never error |
| **F. Next-day recap** | operator | observation + ScoutScore replay + archived pre-match | full recap artifact (recap_ready=true) OR explicit observation-only carryover | next day by 12:00 UTC | `check_recap_pipeline.py` (R3); `check_daily_readiness.py` step7 | no recap & no observation → /recap leaks 404 | observation receipt with clear label |

## Current reliability assessment (the Owner's concern: "daily update is not operationally reliable")

- **A. Slate sync** — SEMI-AUTOMATED. Script is solid; the *upload to production backend* is the
  weak link. As of 2026-06-15 the live backend is **STALE (06-14, no 1489377)**; R2a fallback keeps
  the homepage correct but `check_runtime_daily_fixtures.py --expected-date/--expected-fixture`
  FAILS. **Reliability gap = the upload step is manual + needs prod token engineering doesn't hold.**
- **B. Hotspot selection** — MANUAL, reliable (build-bundled, guarded, R2a staleness gate).
- **C. Prediction generation** — MANUAL-LLM (operator pastes prompt), reliable & traceable; auto-LLM
  is P1.
- **D. T-30** — MANUAL checkpoint; honest `pending` default. Reliable but depends on operator being
  present at KO−30.
- **E. FT observation** — MANUAL; reliable for the one tracked hotspot. 1489371 has an observation.
- **F. Recap** — **WEAKEST.** No full recap for 1489371; backend has no accountability file → the
  recap route's unconditional backend call leaks a 404 (see RECAP_PIPELINE_AUDIT). Observation is a
  correct fallback but the route must stop leaking the error and `/internal/daily` must show the
  recap SLA state explicitly.

## R3 SLA enforcement (what `check_daily_update_sla.py` will assert)

1. selected hotspot `date` == slate `generated_for_date` (current, not stale).
2. prediction artifact ready (source_facts + model_fields + judgement + content_chain).
3. T-30 state explicit (`pending`|`ready`|`skipped`; pending ⇒ no faked update_text).
4. FT/recap state explicit for any finished tracked fixture (observation OR full recap present).
5. send status = HOLD (`safety.no_auto_send=true`; no auto-send wiring).

The SLA check is a **state-visibility** gate (not a clock): it proves each state is represented and
honest. Wall-clock deadlines above are operator guidance, surfaced on `/internal/daily` as the
"Last successful generation" / "Next required operator action" rows (R3).
