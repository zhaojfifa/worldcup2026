# R1 — DAILY_CONTENT_PRODUCTION_FLOW

> The target daily content production chain. Built by `scripts/mvp2_build_daily_prediction_artifact.py`
> (R1 P0). **No automatic LLM call** — the LLM step is operator-manual (paste prompt → paste back JSON).
> When the model/source lookup fails, `operator_estimated` fields are allowed but `/internal/daily` says so.

```
1. SYNC FIXTURE SLATE
   scripts/mvp2_match_sync.py sync --date YYYYMMDD
   → docs/data_audit/mvp2_match_sync/daily_fixtures_YYYYMMDD.json
   → frontend/public/data/daily-fixtures.json (runtime)  [unchanged backbone]

2. MAP DAILY FIXTURE → KNOWN API/MODEL SOURCE (if possible)
   builder.model_lookup(fixture):
     - numeric id present + backend Prediction / bundled ScoutScore frame exists → source='computed'|'seed'
     - manual fixture (id=null), no frame → source='unavailable' → operator_estimated path
   Records source_facts.fixture_source + data_mode + model_lookup result.

3. SELECT HOTSPOT
   frontend/src/data/selectedHotspot.json  (P7 mechanism — PRESERVED, unchanged)
   builder reads it to know which fixture_key is today's lead.

4. BUILD PREDICTION FACTS (source_facts + model_fields)
   - lookup found  → model_fields from the model (recommended_score/risk_level [+ win_prob/confidence
                     ONLY if genuinely computed]); source='computed'|'seed'
   - lookup absent → model_fields.source='operator_estimated'; win_prob/confidence stay null;
                     recommended_score/risk_level operator-provided; no_fake_probability=true
   source_facts.has_model_fields reflects the source tag; missing_fields lists null numerics.

5. GENERATE LLM PROMPT (no API call)
   builder prompt → docs/data_audit/mvp2_predictions/prompts/YYYYMMDD_<fixture_key>_prompt.md
   Prompt embeds: fixture facts · available model_fields (or "unavailable") · missing fields ·
   tactical variables · safe market/public-expectation wording rule · T-30 checklist · recap-receipt
   format · the exact OUTPUT JSON schema + safety flags. (See LLM_ENHANCEMENT_FLOW.md.)
   Artifact content_chain.prompt_generated=true, prompt_path recorded.

6. OPERATOR PASTES PROMPT → DeepSeek/Gemini/Kimi (MANUAL, MVP)
   Operator runs the model themselves (engineering does NOT auto-call). Operator copies the JSON back.

7. OPERATOR CONFIRMS FIELDS + saves reviewed JSON
   docs/data_audit/mvp2_predictions/reviewed/YYYYMMDD_<fixture_key>_reviewed.json
   (For a fixture with no LLM run yet, the operator-authored judgement is saved with
    llm_provider='operator_manual' — honest provenance, NOT a claimed LLM run.)

8. WRITE PREDICTION ARTIFACT
   builder apply --reviewed <file>
   → frontend/src/data/predictionArtifacts/<artifact>.json
   merges: fixture_identity + source_facts + model_fields + llm_judgment (from reviewed) +
   operator_confirmation + operations(share_copy) + safety + content_chain(reviewed_applied=true).

9. HOMEPAGE + /predict READ THE ARTIFACT
   buildStrongCall → homepage score hook + ArtifactTacticalRoom (数据与建模依据 block). [unchanged render]

10. T-30 UPDATE
    Before kickoff, operator re-checks lineups → builder/operator sets artifact.t30
    (status pending→ready, update_text). [P1: wire mvp2_generate_rescore_models.py for live diff]

11. FT → OBSERVATION / RECAP ARTIFACT
    After full-time, operator writes the observation receipt (recap_ready=false) or, P1, runs
    mvp2_build_recap_frame_real.py → LLM real_recap (sha256 provenance). Never a fake recap.

12. NEXT-DAY CARRYOVER
    The finished hotspot becomes the recap lead (selectProductLoop featuredRecap); keyed by
    fixture_key OR id so a manual hotspot (id=null) carries over. [unchanged]
```

## Provenance recorded on the artifact (so /internal/daily can show readiness)
`content_chain`: `{ date, model_lookup: found|unavailable, model_lookup_note, prompt_path,
prompt_generated, reviewed_path, reviewed_applied, llm_provider, built_by, built_at }` —
plus the existing `source_facts`, `model_fields`, `t30`, and the observation artifact. The browser
page reads these (no filesystem access needed) to render the full chain status.
