# R2 — R2_IMPLEMENTATION_SPEC

> Narrow, result-oriented. Scripts/frontend/docs only. No backend deploy, no schema change, no auto-LLM,
> no runtime-data upload by engineering, no auto-send, no fake win_prob/confidence.

## P0
1. **Select a fresh hotspot** — Belgium vs Egypt (1489377, 06-15 19:00 UTC), real fixture from
   API-FOOTBALL. (If no fresh slate existed → HOLD; it does, so proceed.)
2. **Persist selected hotspot** — `frontend/src/data/selectedHotspot.json` → date 2026-06-15,
   fixture_key `1489377`; + dated `docs/data_audit/mvp2_match_sync/selected_hotspot_20260615.json`.
3. **Build model/source fields** — extend `mvp2_build_daily_prediction_artifact.model_lookup` to compute
   ScoutScore (Elo+form+Poisson+upset_band) from kaggle for a fixture whose teams resolve → `source=
   "computed"` with `source_refs`; cold-start team → `unavailable`→operator_estimated (disclosed).
4. **Generate LLM prompt** — `… prompt --date 20260615 --fixture-key 1489377` →
   `docs/data_audit/mvp2_predictions/prompts/20260615_1489377_prompt.md` (embeds the computed model_fields).
5. **Apply reviewed LLM JSON** — `docs/data_audit/mvp2_predictions/reviewed/20260615_1489377_reviewed.json`
   (operator-authored from the computed model; `llm_provider="operator_manual"` — honest, no LLM auto-run).
6. **Write prediction artifact** — `frontend/src/data/predictionArtifacts/match_Belgium-Egypt-20260615.json`
   with id `1489377`, fixture_key `1489377`: source_facts + model_fields(computed) + llm_judgment +
   operator_confirmation + content_chain + t30(pending) + i18n(zh/vi/my/en, vi/my Han=0) + operations +
   safety. Register it in `predictionArtifacts.ts` (PREDICTION list).
7. **Fresh manifest** — rewrite `frontend/public/data/daily-fixtures.json` + `dailyFixtures.generated.json`
   → `generated_for_date=2026-06-15`: hotspot 1489377 (SCHEDULED, renderable) + the other 06-15 fixtures
   + carryover recap 1489371 (RECAP_PENDING, observation artifact) + 1489369 (RECAP_READY). Drop 06-14.
8. **/internal/daily** — already shows source/model/chain readiness (R1); confirm it reflects the fresh
   date + computed source. Add a "Slate vs selection freshness" row (stale check).
9. **Homepage** — no redesign; it already reads selected_hotspot → score hook. Verify it shows 1489377.
10. **Guards** — add a STALENESS check to `check_daily_content_flow.py` + `check_daily_readiness.py`
    (FAIL if selected_hotspot.date < manifest generated_for_date, or no artifact, etc.); keep the
    existing source_facts/model_fields/prompt/reviewed/share/t30/no-fake-prob checks; `check_prediction_
    artifact.py` already validates the new artifact; `check_homepage_product_loop.py` unchanged (source-level).

## Screenshots (mandatory)
Local preview with the live backend **bypassed** (so the fresh static manifest is used), since the live
backend still serves 06-14: homepage (fresh hotspot first), `/predict/1489377` (strong call + data/model
basis), `/internal/daily` (fresh date + computed source + chain), prediction share card, `/recap/1489371`.

## P1 (deferred)
Real DeepSeek/Gemini auto-generation of the narrative; backend manifest upload automation; ScoutScore for
cold-start teams (data backfill); rescore generator for T-30 live diff; A4 real_recap; surfacing an
Elo-implied probability band (only if Owner ever lifts the no-number floor — currently NO).

## Boundaries
No backend/schema change; no runtime-data upload (operator step); no auto-LLM; no auto-send; win_prob/
confidence never surfaced; no betting/trading vocab; vi/my Han=0.
