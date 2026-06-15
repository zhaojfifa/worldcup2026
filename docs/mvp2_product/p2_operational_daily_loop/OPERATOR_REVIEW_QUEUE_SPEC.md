# P2 · OPERATOR_REVIEW_QUEUE_SPEC

> Durable queue: `docs/data_audit/mvp2_operator_review_queue/<date>.json`. Guard:
> `scripts/check_operator_review_queue.py`. The review gate CANNOT be bypassed.

## Item schema (every queue uses these 10 fields)
`fixture_id · match · status · source · deadline · owner · next_action · guard_status ·
artifact_path · publish_eligibility`

## Status ladder (prediction)
`NO_DRAFT → GENERATED → GUARD_PASSED → APPROVED(reviewed JSON written) → ARTIFACT_READY(applied)`.

## Publish gate (enforced)
`publish_eligibility = PUBLISHED` ⟺ `status == ARTIFACT_READY` (a reviewed JSON was applied by
`mvp2_build_daily_prediction_artifact.py apply`). Any GENERATED/GUARD_PASSED/APPROVED/NO_DRAFT item is
`REVIEW_REQUIRED`. An auto-LLM draft can NEVER reach PUBLISHED without the operator's reviewed JSON.

## next_action examples
- NO_DRAFT → "generate-drafts"
- GUARD_PASSED → "operator review → reviewed JSON"
- APPROVED → "build artifact (apply --reviewed)"
- ARTIFACT_READY → "live — monitor T-30"

## Today (2026-06-15): 3 items (Belgium/Saudi/Spain) all ARTIFACT_READY → PUBLISHED (each went through a
reviewed JSON). Gate proven: generated/ drafts exist but publishing flowed through reviewed/.
