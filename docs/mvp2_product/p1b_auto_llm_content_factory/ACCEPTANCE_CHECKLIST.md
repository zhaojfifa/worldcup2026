# P1B · ACCEPTANCE_CHECKLIST

## P1A — Runtime Data MATCH

| # | Criterion | Result |
|---|-----------|--------|
| A1 | upload path audited | `mvp2_match_sync.py upload` reads `daily_fixtures_<date>.json`, POSTs to prod admin endpoint with `x-admin-token` |
| A2 | upload registry ready | `KNOWN` extended with real IDs (1489377/1489379/1489380/1539002) + `manual_scores_20260615.md` + `sync` → `daily_fixtures_20260615.json` (date 2026-06-15, 1489377 present) |
| A3 | prod token available to engineering? | **NO** — engineering holds no prod `ADMIN_API_TOKEN` (local dev token must not be fired at prod) |
| A4 | runtime MATCH achieved | **BLOCKED on operator upload** — see Deploy instruction |

**P1A = BLOCKED** (prod token unavailable). Homepage stays correct via R2a fallback; `/internal/daily`
shows drift FALLBACK honestly; send HOLD. Operator command + verification documented below.

## P1B — Auto-LLM Content Factory

| # | Criterion | Result |
|---|-----------|--------|
| B1 | provider abstraction (DeepSeek/Gemini/Kimi) | ✅ `mvp2_autogen_prediction_draft.py` (DeepSeek live-verified) |
| B2 | auto-LLM draft works for primary + ≥1 secondary | ✅ live DeepSeek drafts for 1489377 + 1489379 (GUARD_PASSED) |
| B3 | generated JSON guard-checked | ✅ `check_auto_llm_factory.py` PASS (7/7 selftest) |
| B4 | reviewed JSON still required before publish | ✅ `check_llm_generated_review_flow.py` PASS (operator gate, no auto-publish) |
| B5 | artifact build from reviewed JSON works | ✅ `mvp2_build_daily_prediction_artifact.py apply` (used for the published secondaries) |
| B6 | recap_seed exists + grounded | ✅ `check_recap_seed_grounding.py` PASS (4/4 selftest) |
| B7 | dry-run/offline + selftest | ✅ generator `--selftest` 7/7; dry-run is deterministic, model-grounded |
| B8 | no secrets committed | ✅ keys read from env/backend/.env; guard fails on key literal |
| B9 | operator console shows generated/review status | ✅ /internal/daily "Auto-draft status" row |
| B10 | all guards pass | ✅ 16 source guards exit 0; build PASS; live visible-copy PASS |
| B11 | send HOLD | ✅ no auto-publish, no auto-send |

## Overall: READY_WITH_P1_ISSUES
P1A MATCH passes via operator upload (command ready); auto-LLM is live-capable (DeepSeek verified)
with a deterministic dry-run fallback; reviewed JSON remains the publish gate; recap_seed grounded;
backend manifest still FALLBACK until the operator upload; send HOLD.

## Deploy instruction (operator)
```
# P1A — clear runtime MATCH (prod token required; engineering holds none):
export ADMIN_API_TOKEN='<prod token>'
python3 scripts/mvp2_match_sync.py upload --date 2026-06-15 --target production
# expected response: stored manifest with 6 fixtures incl. 1489377; then verify:
python3 scripts/check_runtime_daily_fixtures.py --base-url https://worldcup2026-api-71n6.onrender.com --expected-date 2026-06-15 --expected-fixture 1489377
# expected: PASS; /internal/daily drift FALLBACK → MATCH.
# Frontend: Render Manual Deploy of main (Root frontend · npm install && npm run build · dist).
```
