# P2 · OPERATIONAL_DAILY_LOOP_SPEC

> Branch `feature/mvp2-p2-operational-daily-loop` off tag
> `mvp2-p1a-p1b-runtime-match-auto-llm-live-baseline-20260615`. Goal: from "live green content
> factory" → "daily operable command loop" the operator runs from ONE workflow. No homepage redesign;
> no auto-send; no auto-publish of LLM drafts; no payment/referral/reward/token runtime.

## The loop (one command per step)
```
status → build-queue → generate-drafts → review-summary → build-artifacts → t30-status
       → recap-status → share-refresh → close-day
```
Driver: `scripts/mvp2_daily_ops.py` — ORCHESTRATES existing builders (content queue, autogen draft,
prediction-artifact apply), it does not replace them. Every command refreshes the consolidated
snapshot `frontend/src/data/dailyOpsState.json` that the `/internal/daily` command center renders.

## Durable queues (one file per date)
- `docs/data_audit/mvp2_operator_review_queue/<date>.json`
- `docs/data_audit/mvp2_t30_queue/<date>.json`
- `docs/data_audit/mvp2_recap_queue/<date>.json`
- `docs/data_audit/mvp2_share_packages/<date>.json`

Each queue item carries: `fixture_id · match · status · source · deadline · owner · next_action ·
guard_status · artifact_path · publish_eligibility`.

## Hard boundaries (enforced by guards)
- LLM drafts NEVER auto-publish — `build-artifacts` applies ONLY from an operator reviewed JSON
  (`check_operator_review_queue.py`: PUBLISHED ⟺ ARTIFACT_READY).
- No auto-send: `send_status=HOLD` everywhere; no send wiring.
- Never invent lineup/event/probability/confidence/recap (win_prob/confidence null; observation when
  data thin; `no_fake_recap`).
- Never hide SOURCE_MISSING / OBSERVATION_READY / REVIEW_REQUIRED — all surfaced on the command center.
- operator_estimated matches never become primary unless source coverage improves (priority rules).

## Verified today (2026-06-15 slate, live)
primary Belgium-Egypt + secondary Saudi-Uruguay/Spain-CapeVerde all ARTIFACT_READY/PUBLISHED; T-30 all
pending (honest); recap: Brazil-Morocco OBSERVATION_READY, Mexico-SA RECAP_READY (full), Sweden-Tunisia
PENDING; share all SHARE_READY; day-close ready=3 blocked=0; next action = confirm lineups at T-30.
Runtime MATCH live.
