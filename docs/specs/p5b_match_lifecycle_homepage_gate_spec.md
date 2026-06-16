# P5B · Gate Spec — Match-Lifecycle Homepage (frozen)

## Lifecycle states
UPCOMING_PREDICTION_READY · UPCOMING_REVIEW_REQUIRED · T30_WINDOW_PENDING · T30_READY · LIVE_OR_LOCKED ·
FINISHED_RECAP_PENDING · FINISHED_OBSERVATION_READY · FINISHED_RECAP_READY · ARCHIVE_ONLY · EXCLUDED_DEMO ·
SOURCE_MISSING.

## Homepage ranking rules
- primary_prediction: earliest UPCOMING (by kickoff, after now) that is source-qualified (model source
  computed|operator_confirmed) AND has reviewed copy. NEVER finished. NEVER operator_estimated. NEVER
  archive/demo. None → PRIMARY_REVIEW_REQUIRED (blocked; no stale board).
- secondary_predictions: 1-2 other upcoming/same-day with copy; operator_estimated allowed if labelled,
  never primary.
- latest_recap: most recent finished tracked match; RECAP_READY (real_recap) > OBSERVATION_ONLY (score,
  no event) > PENDING (no score, not shown as completed).
- archive (2022) / demo fixtures: role=archive_only/excluded; never primary/secondary/latest_recap.

## Source of truth
runtime daily-fixtures manifest (kickoff/status) + reviewed prediction artifacts (copy_version + model
source) + observation/recap artifacts. Selector writes docs/data_audit/mvp2_homepage_lifecycle/<date>.json
+ bundled frontend/src/data/homepageLifecycle.json; homepage reads the bundled artifact.

## Allowed files
scripts/mvp2_homepage_lifecycle_selector.py, frontend/src/data/homepageLifecycle.json + loader,
dailyFixtures.ts (selectProductLoop reads lifecycle), HomeProductLoop.tsx, DailyStatusPage.tsx trace,
6 P5B guards, screenshots, docs.

## Forbidden
3-5 match expansion, scheduler, backend schema/deploy, betting/odds, fake score/event/lineup/injury/
probability/confidence, auto-send/publish, operator_estimated→primary, archive/demo as active, secrets.

## Guards: check_p5b_homepage_lifecycle_selector / _rendering / _no_finished_primary / _recap_handoff /
_internal_daily_lifecycle_trace / _archive_demo_exclusion. Rendered guards inspect DOM.
## Review: Claude self-review PASS + Codex PASS before merge. Send HOLD.
