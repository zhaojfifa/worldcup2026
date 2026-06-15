# P1B · LLM_FAILURE_AND_FALLBACK_POLICY

> What happens when the provider is slow, errors, returns junk, or the key is absent.

## Failure modes & handling (in `mvp2_autogen_prediction_draft.py`)
| Failure | Handling |
|---------|----------|
| key absent (env) | `--live` raises a clear error naming the env var; operator runs dry-run or sets the key |
| network/timeout | 60s timeout, 2 retries; then a clear `SystemExit` (no partial/garbage write) |
| non-JSON response | regex-extract the first `{...}`; if unparseable → fail (no fabricated draft) |
| draft fails guard | written with `status=NEEDS_REVIEW` + `guard_issues[]` (NOT GUARD_PASSED); operator must fix/reject |
| provider unavailable entirely | **dry-run mode** produces a deterministic, model-grounded draft offline (no network) |

## Fallback ladder
1. `--live` provider (DeepSeek default).
2. On any live failure → operator re-runs in **dry-run** (offline, deterministic, model-grounded).
3. Dry-run draft → same review gate (generated → review → reviewed → artifact).
4. If even model_fields are unavailable (cold-start) → the dry-run draft is honest about it
   (operator_estimated, "对手数据冷启动…"), never inventing a computed model.

## Hard guarantees under failure
- No partial or fabricated draft is ever published.
- A failed/weak draft is `NEEDS_REVIEW`, never silently applied.
- The artifact is only written by the existing `apply` step from an operator reviewed JSON — a
  provider failure can never reach a customer surface.
- No auto-send under any failure path; send stays HOLD.

## Cost / safety
One call per fixture per generation; no loops, no batch fan-out, no background scheduling. Keys local
dev only; never committed or printed (`check_auto_llm_factory.py` enforces no key literal).
