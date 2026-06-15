# R3 · ACCEPTANCE_CHECKLIST

> Map every Owner acceptance criterion to a concrete, checkable artifact. Updated as Phase B lands.

## READY_TO_DEPLOY requires ALL:

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | data source validity explicit | `check_data_source_validity.py` PASS (9/9 selftest); DATA_SOURCE_AUDIT.md | ✅ |
| 2 | model field source explicit | `model_fields.source=computed` (Belgium-Egypt); MODEL_FIELD_COVERAGE.md; check PASS | ✅ |
| 3 | LLM prompt grounded in model fields | `check_llm_grounding.py` PASS (7/7); prompt cites model_fields + DO-NOT-INVENT | ✅ |
| 4 | reviewed JSON exists | `docs/data_audit/mvp2_predictions/reviewed/20260615_1489377_reviewed.json` (on disk) | ✅ |
| 5 | artifact content_chain traceable | content_chain prompt_path+reviewed_path exist on disk | ✅ |
| 6 | daily update SLA visible | `check_daily_update_sla.py` PASS (6/6); /internal/daily SLA rows (shot 03) | ✅ |
| 7 | recap route no raw failure | recap route gated (no unconditional api.getRecap); `check_recap_pipeline.py` PASS (6/6) | ✅ |
| 8 | recap state explicit | `recapState()` exported; /internal/daily recap SLA row = OBSERVATION_READY | ✅ |
| 9 | screenshots prove the above | 6 screenshots in `docs/qa_screenshots/mvp2_r3_data_llm_recap/` | ✅ |
| 10 | all guards pass | 9 source guards exit 0; build PASS; live visible-copy PASS | ✅ |
| 11 | send remains HOLD | `safety.no_auto_send=true`; /internal/daily HOLD row (shot 03) | ✅ |

## READY_WITH_P1_ISSUES allowed if:
- auto-LLM still manual but traceable (`llm_provider=operator_manual`). — EXPECTED
- backend manifest upload pending but fallback correct (R2a). — EXPECTED (live backend stale)
- recap observation-only (1489371) but no raw failure leaks. — EXPECTED

## HOLD if any:
- homepage stale; data source hidden; LLM grounding unprovable; recap route still leaks error;
  no screenshots; guards missing.

## Verification commands
```
cd frontend && npm run build
python3 scripts/check_customer_visible_copy.py https://worldcup2026-izid.onrender.com
python3 scripts/check_runtime_daily_fixtures.py --base-url https://worldcup2026-api-71n6.onrender.com --expected-date 2026-06-15 --expected-fixture 1489377
python3 scripts/check_homepage_product_loop.py
python3 scripts/check_prediction_artifact.py
python3 scripts/check_growth_copy.py
python3 scripts/check_daily_readiness.py
python3 scripts/check_daily_content_flow.py
python3 scripts/check_data_source_validity.py        # R3
python3 scripts/check_llm_grounding.py               # R3
python3 scripts/check_daily_update_sla.py            # R3
python3 scripts/check_recap_pipeline.py              # R3
```
