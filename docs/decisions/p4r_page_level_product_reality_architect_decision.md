# P4R+ · Architect Decision — Page-Level Product Reality

Verdict: **GO.**

## What is broken?
The reviewed-LLM-copy pipeline produced correct artifacts and guards, but (a) the RENDERER read
`i18n` while `apply` wrote `llm_judgment` (reviewed copy was dead-rendered), and (b) guards inspected
artifact JSON, not the rendered DOM — so "looks stale/generic" could not be caught or disproven. P4R
fixed (a) by syncing reviewed JSON → zh `i18n` and added 4 rendered guards. P4R+ formalizes the
Harness-X role separation and adds a single page-level source-trace gate.

## Which pages are affected?
Homepage (primary / yesterday recap / secondary cards), `/predict/<primary>`, `/predict/<secondary>`,
`/recap/<recap>`, `/share/fixture/<primary>`, recap share card, `/internal/daily` critical-ops.

## Source-of-truth chain
runtime daily-fixtures (backend→static→bundled) → active daily package (dailyContentQueue +
selectedHotspot) → reviewed LLM prediction artifact (`predictionArtifacts/*.json`, zh `i18n` synced
from `docs/data_audit/mvp2_predictions/reviewed/*`) → rendered homepage/predict/share; recommendation
closure + `observation_*.json` → rendered `/recap`; `dailyOpsState.json` → `/internal/daily`.

## Which state means BLOCKED?
`BLOCKED_DAILY_FRESHNESS` (runtime≠artifact date). Honest non-blocking states that must be SHOWN, not
hidden: `COPY_MISSING`, `REVIEW_REQUIRED`, `OBSERVATION_ONLY`, `PENDING`, `SOURCE_MISSING`.

## Out of scope
backend schema, auto-send, auto-publish, scheduler, payment/referral/token, fake event/full recap,
fake lineup/injury/probability/confidence, broad homepage redesign. vi/my/en prediction copy stay
authored translations (reviewed JSON is zh-canonical).

## Must be proven on screenshots
homepage real today primary + real yesterday recap; /predict reviewed LLM copy (headline/score/risk/
variable/share); /recap observation recap labelled; /internal/daily source-trace rows
(prediction_copy_source=operator_reviewed_llm_judgment); share card upgraded copy. Guards must inspect
rendered DOM, and all must PASS locally before merge + against live after deploy.
