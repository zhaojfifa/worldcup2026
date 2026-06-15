# P2 · INTERNAL_DAILY_COMMAND_CENTER_SPEC

> `/internal/daily` (DailyStatusPage.tsx) reads `frontend/src/data/dailyOpsState.json` (written by
> mvp2_daily_ops.py) and answers: "what is ready, what is blocked, what do I do next?".
> Guard: `scripts/check_internal_daily_command_center.py`.

## Command-center rows (the new 🛰️ section, in addition to the existing readiness + content-queue cards)
- **Runtime / 运行时** — drift = MATCH / FALLBACK / BLOCKED (from the live backend, R2a logic)
- **Today queue / 今日队列** — primary + secondary fixture ids
- **Review queue / 复核队列** — per-fixture status + publish_eligibility
- **Artifact readiness / 产物就绪** — published vs review-required counts
- **T-30 queue / 临场队列** — per-fixture T30 status
- **FT observation+recap / 复盘队列** — per-fixture recap publish_eligibility
- **Share package / 分享物料队列** — per-fixture SHARE_READY/MISSING
- **Day close / 收日** — status + ready/blocked counts
- **Next operator action / 下一步** — the single most important next step
- **Send status / 发送状态** — HOLD (manual only; Owner per-channel GO; no auto-send)

## Visibility rule (guarded)
The queues must be VISIBLE (rendered from the imported dailyOpsState.json), not just files on disk.
SOURCE_MISSING / OBSERVATION_READY / REVIEW_REQUIRED are shown, never hidden.
