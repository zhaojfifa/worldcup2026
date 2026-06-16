# P5B · Claude Self-Review — Match-Lifecycle Homepage Orchestration

Verdict: **PASS** (pending Codex independent review + Owner merge).

## Lifecycle selector source
scripts/mvp2_homepage_lifecycle_selector.py computes per-fixture lifecycle_state from kickoff + status +
recap_ready + model source + a time basis, then roles (primary/secondary/latest_recap/next/pending/
excluded/blocked) → docs/data_audit/mvp2_homepage_lifecycle/<date>.json + bundled
frontend/src/data/homepageLifecycle.json. selectProductLoop now READS the artifact (primary/secondary/
latest_recap) instead of the static selectedHotspot board.

## No finished primary
primary = earliest UPCOMING source-qualified (computed|operator_confirmed) with reviewed copy; never
finished, never operator_estimated, never archive/demo. validate + check_p5b_no_finished_primary +
check_p5b_homepage_lifecycle_selector PASS. ROTATION PROVEN: editorial 12:00 basis → primary Belgium;
--now 20:00 (after Belgium KO) → primary rotates to Saudi-Uruguay (06-rotation-proof.txt).

## Recap handoff
latest_recap = most recent finished tracked match (RECAP_READY > OBSERVATION_ONLY > PENDING). Brazil-
Morocco (observation) is the latest_recap; finished-pending tracked surfaced. No fake full recap.
check_p5b_recap_handoff PASS.

## No archive/demo active leak
WC-2022 (Germany/Qatar) + demo pairings (Brazil-Argentina) classified ARCHIVE_ONLY/EXCLUDED_DEMO, never
an active role; demo_pair_leak (active surface, folds stripped) PASS. check_p5b_archive_demo_exclusion PASS.

## No fake data / no betting / no auto-send
win_prob/confidence null; no fabricated event; OBSERVATION_ONLY labelled; send_status HOLD across the
lifecycle artifact; reviewed-JSON gate intact; no betting/odds.

## Internal daily trace
/internal/daily 🔁 Match lifecycle card: active date/time basis · primary + reason · latest recap ·
secondary · next · pending recap · archive/demo excluded · blocked · next action · HOLD.
check_p5b_internal_daily_lifecycle_trace PASS.

## Screenshot evidence
docs/qa_screenshots/p5b_match_lifecycle_homepage/local/ (01 lifecycle primary, 02 latest recap,
03 secondary, 04 internal lifecycle trace, 05 artifact report, 06 rotation proof, 07 predict, 08 recap).

## Scope
1 primary + 1-2 secondary + latest recap + next upcoming. No 3-5 expansion, no scheduler, no backend
deploy, no secrets. P5A quality guards still PASS (homepage guard updated to read the lifecycle primary).
