# P3A/P3B · ACCEPTANCE_CHECKLIST

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | daily autorun works | `mvp2_daily_autorun.py` plan/run(dry-run + execute-reviewed-only)/report; selftest 5/5 | ✅ |
| 2 | T-30 source ingestion state exists | `mvp2_t30_sources/2026-06-15.json` (3 fixtures, SOURCE_PARTIAL); selftest 7/7 | ✅ |
| 3 | no fake T-30 claims | `check_no_fake_t30_claims.py` PASS (lineup/injury=false honest; no faked update_text) | ✅ |
| 4 | /internal/daily shows autorun + source coverage | command center rows; `check_internal_daily_command_center.py` PASS | ✅ |
| 5 | runtime MATCH remains PASS | live runtime check PASS (date 2026-06-15, 1489377, freshness ok) | ✅ |
| 6 | all existing + new guards pass | 25 source guards exit 0 + runtime PASS; build PASS; visible-copy PASS | ✅ |
| 7 | autorun does not bypass review | build-artifacts skipped in dry-run; applies ONLY reviewed JSON | ✅ |
| 8 | send remains HOLD | autorun + dailyOpsState send_status=HOLD; no auto-send/auto-publish | ✅ |

## Decision: READY_WITH_P1_ISSUES
Autorun works; T-30 source is honestly SOURCE_PARTIAL (no live lineup/injury feed — operator confirms
at KO-30); operator review gate required; no fake claims; screenshots provided; send HOLD.

## Carryover (accepted)
- No live lineup/injury/news ingestion → T-30 stays operator-confirmed (SOURCE_PARTIAL).
- Auto-LLM still operator-reviewed; 1489371 OBSERVATION_READY; 1539002 recap PENDING;
  Spain-CapeVerde operator_estimated (not primary).
- No scheduler — autorun is operator-triggered (no cron, no auto-send).
