# P3A/P3B · DAILY_AUTORUN + T30_SOURCE_SPEC

> Branch `feature/mvp2-p3a-p3b-daily-autorun-t30-source` off tag
> `mvp2-p2-operational-daily-loop-live-baseline-20260615`. Goal: "operable command center" →
> "repeatable daily operation". No auto-send; no auto-publish of LLM drafts; reviewed-JSON gate intact.

## P3A — Daily auto-run (`scripts/mvp2_daily_autorun.py`)
Orchestrates the P2 loop (does NOT duplicate logic). Modes:
- `plan` — print the 10-step sequence + which step mutates.
- `run --dry-run` — run read-only/idempotent steps; **SKIP build-artifacts** (recorded as skipped).
- `run --execute-reviewed-only` — also run build-artifacts (applies ONLY a reviewed JSON — the gate).
- `report` — print the artifact.

Sequence: status → build-queue → generate-drafts → review-summary → t30-source → **build-artifacts
(mutating, reviewed-only)** → t30-status → recap-status → share-refresh → close-day.

Artifact `docs/data_audit/mvp2_daily_autorun/<date>.json`: date · command_sequence ·
steps_executed/skipped/blocked · required_operator_actions · send_status=HOLD · publish_eligibility ·
review_gate_result · runtime_match · last_run · mode · next_run (operator-triggered; no scheduler).

## P3B — T-30 source ingestion (`scripts/mvp2_t30_source.py`)
Writes `docs/data_audit/mvp2_t30_sources/<date>.json`. Per fixture: kickoff · t30_deadline ·
expected/available/missing source fields · lineup_availability · injury_news_availability ·
tactical_variable_availability · source_status · update_eligibility · next_operator_action.

`source_status ∈ SOURCE_READY | SOURCE_MISSING | SOURCE_STALE | SOURCE_PARTIAL | OPERATOR_OVERRIDE_REQUIRED`.

HARD TRUTH: the project does NOT ingest live lineups/injuries/news. So lineup_availability and
injury_news_availability are ALWAYS false; today's three matches are SOURCE_PARTIAL (model baseline +
T-30 checklist present, but no live feed) → update_eligibility = OPERATOR_CONFIRM_REQUIRED. The system
NEVER invents a T-30 update; `t30.update_text` stays null until the operator confirms at KO-30.

## /internal/daily command center (reads dailyOpsState.json)
Adds: Daily auto-run (mode/runtime/last run) · Autorun steps passed/skipped/blocked · Next
scheduled/manual run · T-30 source coverage by match · T-30 source detail (lineup/injury/eligibility) ·
Next operator action · Send HOLD — on top of the P2 review/T-30/recap/share/day-close rows.

## Guards
`check_daily_autorun.py` · `check_t30_source_ingestion.py` · `check_no_fake_t30_claims.py` (each
--selftest). All 22 prior guards still pass (25 total + runtime).
