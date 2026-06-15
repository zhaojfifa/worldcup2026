# P1B · AUTO_LLM_REVIEW_WORKFLOW

> The generated draft NEVER publishes directly. Operator review remains the gate. Enforced by
> `check_llm_generated_review_flow.py`.

## Flow
```
prompt (docs/data_audit/mvp2_predictions/prompts/<date>_<key>_prompt.md)
 → LLM DRAFT  (mvp2_autogen_prediction_draft.py generate [--live])
            → docs/data_audit/mvp2_predictions/generated/<date>_<key>_generated.json  [GENERATED]
 → guard check (guard_draft inline + check_auto_llm_factory.py)                       [GUARD_PASSED|NEEDS_REVIEW]
 → operator review (human edits/approves; copies into reviewed JSON)                  [APPROVED|REJECTED]
            → docs/data_audit/mvp2_predictions/reviewed/<date>_<key>_reviewed.json
 → artifact build (mvp2_build_daily_prediction_artifact.py apply --reviewed …)        [ARTIFACT_READY]
 → page projection (/predict, homepage, /internal/daily)
```

## Statuses
`GENERATED → GUARD_PASSED → NEEDS_REVIEW → APPROVED → REJECTED → ARTIFACT_READY`.
The generated file records `status` + `guard_issues`. A GUARD_PASSED draft is still a DRAFT — the
operator must produce the reviewed JSON before `apply` writes the artifact.

## Operator gate (invariant the guard enforces)
- The generator writes ONLY to `generated/` — never into `frontend/src/data/predictionArtifacts/`
  (no auto-publish path).
- For any fixture that has a published prediction artifact, that artifact's
  `content_chain.reviewed_applied` must be true and the reviewed file must exist on disk — i.e. the
  draft did not silently become the live artifact.
- Every generated draft carries a non-publishing note ("GENERATED draft for OPERATOR REVIEW only —
  NOT published…").

## Required paths (all present)
`docs/data_audit/mvp2_predictions/prompts/` · `…/generated/` · `…/reviewed/`.

## This sprint
2 live DeepSeek drafts in `generated/` (GUARD_PASSED). The PUBLISHED artifacts (Belgium, Saudi-Uruguay)
were built earlier from operator-reviewed JSON (content_chain.reviewed_applied=true) — proving the
gate: drafts exist, but publishing still flowed through reviewed JSON. No auto-publish, no auto-send.
