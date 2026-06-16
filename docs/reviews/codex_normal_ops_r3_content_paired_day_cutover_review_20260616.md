# Codex Independent Adversarial Review — NORMAL OPS R3 (content-paired day cutover)

- Branch: `ops/r3-content-paired-cutover`  HEAD `2a0f4c1`
- Reviewer: Codex (independent adversarial)
- Date: 2026-06-16
- Scope: R3 = content-paired day cutover with a hard pre-upload consistency gate. Find real defects; modify no file except this review.

## Overall verdict: PASS_WITH_PATCHES

The core R3 invariant is correctly implemented and empirically proven: a DATA-ONLY cutover is hard-blocked, the upload happens strictly after the gate passes, a blocked cutover restores the bundled homepage artifacts byte-for-byte (no homepage change), production stays green on the 06-15 baseline, and send stays HOLD. No product/UI/backend/schema change. No token leak. One LOW-severity defect: the gate docstrings (and one guard's selftest docstring) overclaim recap-artifact pairing that is not actually enforced (`_observation` is dead code).

---

## Check 1 — Diff scope

`git diff main...HEAD --stat` + `git status --short`: tracked code changes are limited to:
- `scripts/mvp2_day_cutover.py` (new, 139 lines)
- `scripts/check_r3_day_cutover_consistency.py` (new, the gate)
- `scripts/check_r3_no_data_only_cutover.py` (new guard)
- `scripts/check_r3_selected_content_matches_slate.py` (new guard)
- `docs/reviews/normal_ops_r3_content_paired_day_cutover_claude_self_review.md` (self-review)
- new audit/evidence under `docs/data_audit/mvp2_day_cutover/` + `docs/qa_screenshots/normal_ops_r3.../`

`git diff main...HEAD -- frontend/` = EMPTY. `git diff main...HEAD -- backend/` = EMPTY.
Scheduler scan (`cron|schedule|setInterval|APScheduler`) on the diff hit only the literal fixture status string `SCHEDULED` and selftest registry rows — no actual scheduler. No scheduler added.

Note (not a branch defect): the working tree carries pre-existing uncommitted audit artifacts (`docs/data_audit/mvp2_homepage_lifecycle/2026-06-15.json` modified, `.../2026-06-16.json` untracked) left by the implementer — audit data only, no product/UI impact.

DIFF_SCOPE_SCRIPTS_ONLY=yes
PRODUCT_UI_UNCHANGED=yes
BACKEND_SCHEMA_CHANGE=no

## Check 2 — The gate (`check_r3_day_cutover_consistency.py`)

`gate(date_iso, reg, sel, lc, queue)` is PURE/importable: accepts injected artifacts, defaults to disk reads (lines 62-68). Enforced rules:
- registry date == target (l72-73)
- selectedHotspot.date == target → DATA-ONLY block (l79-80)
- selected primary fixture in slate (l82-83)
- primary has a reviewed prediction artifact with `copy_version` AND `prediction_confirmed` (l85-90 via `_reviewed_pred`)
- primary not finished in slate status/lifecycle (l91-93)
- lifecycle primary == selectedHotspot, and not-missing (l99-104)
- secondaries in slate (l106-109)
- finished recap fixture must have a score (l111-117)

Selftest is non-vacuous: 3 distinct true conditions (data-only blocked, finished primary blocked, missing registry blocked) — l121-138, exercised below.

DEFECT R3-1 (LOW): docstring l12 claims the gate verifies a recap fixture "has an observation/recap artifact"; the guard `check_r3_selected_content_matches_slate.py` docstring (l3-4) and its selftest docstring (l6-7, "recap without artifact fails") claim the same. The gate never calls `_observation` (defined l54, unused — confirmed by grep: only `_reviewed_pred` is called at l86). It only checks `score_home is None` for finished recap fixtures (l116). So recap-artifact pairing is documented but NOT enforced, and the selected-content guard's selftest has no recap case (only 2 prediction cases). Impact bounded: the prediction-pairing (the actual R3 concern for the 06-16 prediction cutover) IS enforced; recap-artifact pairing is an overclaim. Suggested patch: either call `_observation` in the gate for recap fixtures, or correct the docstrings to state only score-presence is enforced.

## Check 3 — Cutover orchestrator (`mvp2_day_cutover.py`)

- Upload is strictly after the gate: `ok, fails = r3.gate(date_iso)` (l86) precedes `ms.cmd_upload(...)` (l106), and `cmd_upload` is only reached on the PASS branch guarded by `if do_upload and target` (l105). On FAIL the function returns at l101 before any upload.
- On FAIL: `_restore(snap)` (l89) reverts all 5 snapshotted bundled artifacts (`dailyFixtures.generated.json`, `public/data/daily-fixtures.json`, `homepageLifecycle.json`, `selectedHotspot.json`, `dailyContentQueue.json` — l38-44); snapshot taken before sync/build (l73), so both the R2 sync and lifecycle build are reverted. Writes `*_blocked.json` with `uploaded: False`, does NOT upload.
- send_status HOLD always emitted (l91, l100, l111, l116 — both branches).
- Token: never read or printed here; upload delegates to `ms.cmd_upload` (l106) which reads `$ADMIN_API_TOKEN`. No token literal in the file.

UPLOAD_ONLY_AFTER_GATE=yes
BLOCK_RESTORES_ARTIFACTS=yes

## Check 4 — Empirical BLOCK path (no upload, no token)

Recorded md5 before:
- selectedHotspot.json `a73d5b25210c0cecb4a367d62ed234eb`
- homepageLifecycle.json `9f963b17b7f79b734bc70158e76d3426`
- dailyFixtures.generated.json `d9b1aa8656af503a78c1dc2cc7547995`

Ran `python3 scripts/mvp2_day_cutover.py --date 2026-06-16 --source api-football` (no `--target`). Output: `CUTOVER_BLOCKED — 5 gate failure(s)`, first reason `DATA_ONLY_CUTOVER: selectedHotspot.date '2026-06-15' != runtime date '2026-06-16'`, then `selected primary 1489377 not in generated slate`, lifecycle-no-primary, two secondaries not in slate. Printed `bundled artifacts RESTORED` and `SEND_STATUS=HOLD`.

md5 after: identical to before for all three. `git status --short frontend/` = clean (no side-written files). Cleaned audit side-writes with `git checkout -- docs/data_audit/mvp2_match_sync/ frontend/` → clean. PASS path with `--target` was NOT run; nothing uploaded.

DATA_ONLY_CUTOVER_BLOCKED=yes

## Check 5 — R3 guard selftests + date modes

- `check_r3_day_cutover_consistency.py --selftest`: 3/3 PASS (exit 0)
- `--date 2026-06-15`: PASS (exit 0) — data+content paired
- `--date 2026-06-16`: FAIL / CUTOVER_BLOCKED (exit 1) — DATA_ONLY + slate/secondary mismatches
- `check_r3_no_data_only_cutover.py --selftest`: 4/4 PASS (incl. source-inspection of restore + upload-after-gate)
- `--date 2026-06-16`: correctly BLOCKED, PASS (exit 0)
- `check_r3_selected_content_matches_slate.py --selftest`: 2/2 PASS
- `--date 2026-06-15`: PASS (exit 0)

All as expected.

## Check 6 — Production currently GREEN on baseline

- `check_live_source_consistency.py`: PASS — backend_date=2026-06-15, active_date=2026-06-15, primary=1489377 (frontend active package == backend runtime).
- `check_live_api_daily_source.py`: PASS — date=2026-06-15, 6 fixtures, stale=False, admin path protected.

Production is on the last green 06-15 baseline; the blocked 06-16 cutover left it untouched.

PRODUCTION_STAYS_GREEN_ON_FAIL=yes
SELECTED_CONTENT_MATCHES_SLATE=yes (for the live 06-15 baseline)

## Check 7 — Regression sample

- `check_r2_auto_data_refresh.py --date 2026-06-16`: PASS (scores honest, no invention)
- `check_p5b_no_finished_primary.py` (live): PASS (primary upcoming, matches lifecycle)
- `check_p5b_recap_handoff.py --date 2026-06-15`: PASS (finished routed to recap/pending; no fake recap)

No regression.

## Check 8 — Compliance

- betting/odds/handicap/盘口/竞猜/投注/下注/稳赚/必中/跟单 scan over the 4 new scripts: NONE FOUND.
- probability/confidence introduction (`win_prob|probability|confidence`): NONE in the new scripts (no fabricated probability/confidence added).
- send HOLD wording present (consistency gate l152; cutover l13/l91/l100/l111/l116). No auto-send/publish path; upload is the only network write and is gated + manual via `--target`.

FAKE_DATA=none
BETTING_VOCAB=none
AUTO_SEND=none
SEND_STATUS=HOLD

## Check 9 — Secret scan

- `git grep -lc "<token>" -- . ':!*.png'`: NO MATCHES — token value absent from all tracked files on this branch.
- `git ls-files | grep -c 'backend/.env'`: 0 — backend/.env not tracked.
- `git diff main...HEAD` introduced no `.env` file and 0 occurrences of the token value.
- Self-review doc and this review contain no token value.

ADMIN_TOKEN_LEAK=false

---

## Confirmation lines

DIFF_SCOPE_SCRIPTS_ONLY=yes
PRODUCT_UI_UNCHANGED=yes
BACKEND_SCHEMA_CHANGE=no
DATA_ONLY_CUTOVER_BLOCKED=yes
UPLOAD_ONLY_AFTER_GATE=yes
BLOCK_RESTORES_ARTIFACTS=yes
SELECTED_CONTENT_MATCHES_SLATE=yes
PRODUCTION_STAYS_GREEN_ON_FAIL=yes
FAKE_DATA=none
BETTING_VOCAB=none
AUTO_SEND=none
SEND_STATUS=HOLD
ADMIN_TOKEN_LEAK=false

## Defects

- R3-1 (LOW): gate/guard docstrings overclaim recap observation-artifact pairing; `_observation` is dead code, only score-presence is enforced for finished recap fixtures, and the selected-content guard selftest has no recap case. Documentation-vs-behavior mismatch; core prediction-pairing is unaffected. Patch: enforce `_observation` for recap fixtures or correct the docstrings/selftest.
