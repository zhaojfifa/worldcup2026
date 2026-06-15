# P1 · ACCEPTANCE_CHECKLIST

> Maps each Owner acceptance criterion to concrete, checkable evidence. Updated after Phase B.

## READY_TO_DEPLOY requires ALL:

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | primary + secondary match queue exists | `dailyContentQueue.json`; `check_content_queue.py` PASS (8/8) | ✅ |
| 2 | ≥ primary + one secondary prediction artifact ready | 4 prediction artifacts (Belgium, Saudi-Uruguay, Spain-CapeVerde, Nether-Japan); `check_prediction_artifact` PASS | ✅ |
| 3 | LLM prompt/review chain for selected matches | 3 prompts + 3 reviewed JSONs (predictions/); content_chain on each artifact | ✅ |
| 4 | copy quality guard passes | `check_llm_copy_quality.py` PASS (3 matches, 6/6 selftest) | ✅ |
| 5 | recap flow guard passes | `check_recap_generation_flow.py` PASS (8/8 selftest) | ✅ |
| 6 | operator console shows queues and SLA | `check_operator_console.py` PASS; /internal/daily queue console (shot 04) | ✅ |
| 7 | homepage + /predict screenshots pass | shots 01 (home primary+secondary), 02 (predict primary), 03 (predict secondary) | ✅ |
| 8 | recap route works without raw errors | R3 gate retained; `check_recap_pipeline.py` PASS; shot 05 | ✅ |
| 9 | all guards pass | 13 source guards exit 0; build PASS; live visible-copy PASS | ✅ |
| 10 | send remains HOLD | queue send_status=HOLD; artifacts no_auto_send=true; console HOLD | ✅ |

## READY_WITH_P1_ISSUES (the conditions that apply here)
- auto-LLM remains manual but traceable (`llm_provider=operator_manual`; content_chain records prompt+reviewed). — APPLIES
- backend manifest still FALLBACK but homepage correct (R2a). — APPLIES (live backend stale)
- full recap remains observation-only for 1489371 but state is explicit (OBSERVATION_READY). — APPLIES

## Verification commands
```
cd frontend && npm run build
python3 scripts/check_customer_visible_copy.py https://worldcup2026-izid.onrender.com
python3 scripts/check_homepage_product_loop.py
python3 scripts/check_prediction_artifact.py
python3 scripts/check_growth_copy.py
python3 scripts/check_daily_readiness.py
python3 scripts/check_daily_content_flow.py
python3 scripts/check_data_source_validity.py
python3 scripts/check_llm_grounding.py
python3 scripts/check_daily_update_sla.py
python3 scripts/check_recap_pipeline.py
python3 scripts/check_content_queue.py            # P1
python3 scripts/check_llm_copy_quality.py         # P1
python3 scripts/check_recap_generation_flow.py    # P1
python3 scripts/check_operator_console.py         # P1
```
