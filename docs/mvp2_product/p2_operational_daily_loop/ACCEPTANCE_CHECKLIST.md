# P2 · ACCEPTANCE_CHECKLIST

## READY_TO_DEPLOY requires ALL:
| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | runtime MATCH remains PASS | `check_runtime_daily_fixtures.py … --expected-date 2026-06-15 --expected-fixture 1489377` PASS | ✅ |
| 2 | daily ops command works | `mvp2_daily_ops.py` 9 subcommands run end to end; selftest 8/8 | ✅ |
| 3 | review queue works | `mvp2_operator_review_queue/2026-06-15.json`; `check_operator_review_queue.py` PASS (gate not bypassable) | ✅ |
| 4 | T-30 queue exists | `mvp2_t30_queue/2026-06-15.json`; `check_t30_queue.py` PASS | ✅ |
| 5 | recap queue exists | `mvp2_recap_queue/2026-06-15.json`; `check_recap_queue.py` PASS | ✅ |
| 6 | share refresh works | `mvp2_share_packages/2026-06-15.json`; `check_share_package_refresh.py` PASS | ✅ |
| 7 | /internal/daily is a real command center | dailyOpsState.json rendered; `check_internal_daily_command_center.py` PASS | ✅ |
| 8 | all guards pass | 22 source guards exit 0; build PASS; live visible-copy PASS | ✅ |
| 9 | screenshots provided | `docs/qa_screenshots/mvp2_p2_command_center/` (12) | ✅ |
| 10 | send remains HOLD | dailyOpsState.send_status=HOLD; no auto-send/auto-publish | ✅ |

## READY_WITH_P1_ISSUES conditions that apply
- Daily loop works but some states are honestly OBSERVATION_READY (1489371) / PENDING (1539002). ✅ APPLIES
- Auto-LLM still requires operator review (drafts GENERATED/GUARD_PASSED → reviewed JSON → artifact). ✅ APPLIES
- Full recap blocked where event data is missing (1489371). ✅ APPLIES

## HOLD conditions (none triggered)
runtime FALLBACK · review-gate bypassable · invented T-30/recap · queues file-only-not-visible · no
screenshots · guards missing — none of these are true.

## Verification
```
python3 scripts/mvp2_daily_ops.py close-day --date 2026-06-15
python3 scripts/check_daily_ops_loop.py; python3 scripts/check_operator_review_queue.py;
python3 scripts/check_t30_queue.py; python3 scripts/check_recap_queue.py;
python3 scripts/check_share_package_refresh.py; python3 scripts/check_internal_daily_command_center.py
python3 scripts/check_runtime_daily_fixtures.py --base-url https://worldcup2026-api-71n6.onrender.com --expected-date 2026-06-15 --expected-fixture 1489377
```
