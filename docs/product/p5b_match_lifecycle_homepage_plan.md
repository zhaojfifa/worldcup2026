# P5B · Product Plan — Match-Lifecycle Homepage

## Lifecycle-driven homepage sections
1. 今日重点预测 / 下一场重点 — the selector's primary_prediction (earliest upcoming source-qualified,
   reviewed copy; never a finished match). Shows lifecycle state.
2. 最新赛后复盘 — selector's latest_recap (most recent finished tracked match; RECAP_READY or
   OBSERVATION_ONLY label; PENDING if no score — not shown as a completed recap).
3. 今日其他推荐 — selector's 1-2 secondary_predictions (reason + score + risk; operator_estimated allowed
   but labelled, never primary).
4. 临场 30 分钟状态 — T30 pending/ready/source-missing on the primary.
5. CTA.

## Rotation
When the primary match finishes → it leaves primary, routes to latest_recap (observation/recap), and the
next upcoming source-qualified match becomes primary. If none → PRIMARY_REVIEW_REQUIRED (no stale board).

## Internal trace (/internal/daily)
active_date · current_time_basis · primary + why · latest_recap + why · secondary + why · per-fixture
lifecycle_state · blocked items · archive/demo exclusions · operator_next_action · Send HOLD.
