# P4 · CRITICAL DAILY-RECAP-COPY LOOP SPEC

> Branch `feature/mvp2-p4-critical-daily-recap-copy-loop` off tag
> `mvp2-p3a-p3b-daily-autorun-t30-source-live-baseline-20260615`. The three fatal product needs:
> (1) daily timely update, (2) yesterday→today closed-loop recap, (3) LLM copy quality. No auto-send;
> no auto-publish; reviewed-JSON gate; no fake events/lineup/confidence/odds.

## P4A — Daily Freshness Gate (`scripts/check_daily_freshness.py`)
Builds + verifies `docs/data_audit/mvp2_daily_freshness/<date>.json` (date, runtime_date, artifact_date,
homepage_primary_fixture, secondary_fixtures, freshness_status, stale_reason, next_operator_action,
send_status). FRESH only when an artifact date exists, primary is in today's scheduled slate, ≥2
secondary, and runtime/backend date == artifact date. A date mismatch → **BLOCKED_DAILY_FRESHNESS**.
Stale content is FLAGGED, never silently shown. Today: FRESH (runtime 2026-06-15 == artifact).

## P4B — Yesterday Recommendation Closure (`scripts/mvp2_recommendation_closure.py`)
`build`/`report` → `docs/data_audit/mvp2_recommendation_closure/<date>.json`. Per fixture: predicted vs
actual, result_status (HIT/MISS/PARTIAL/OBSERVATION_ONLY/PENDING), reason, correction note, recap
eligibility (FULL_RECAP/OBSERVATION_ONLY/PENDING), share status, next action. RULES: no actual score →
PENDING; score but no event data → OBSERVATION_ONLY; full recap needs an event source; never fakes
events. Today: 1489371 PARTIAL (2-1→1-1, OBSERVATION_ONLY), 1489369 FULL_RECAP, 1539002 PENDING.

## P4C — LLM Copy Upgrade (`scripts/check_llm_copy_attractiveness.py`)
Prediction copy must have: strong headline · exact score call · primary reason · hidden risk ·
tactical variable · share line · source basis. Recap copy: hit/miss judgment · predicted-vs-actual ·
what-missed · correction · share line. REJECTS generic filler, weak phrase without a reason, fake
certainty, betting, fake confidence/probability, fabricated events, missing score/risk/share.

## P4D — /internal/daily Critical Ops View
New TOP card (🚨 今日关键运营 / Critical ops) reading dailyOpsState (freshness + recommendation_closure
folded in by mvp2_daily_ops.py): 今日内容是否新鲜 · 今日主推 · 今日次级推荐 · 昨日推荐闭环 · 命中/偏差/
待观察 · 文案复核状态 · 分享物料状态 · 今天能不能发(HOLD) · 下一步运营动作. Operator answers in 10s.

## Homepage
Hierarchy already prioritizes 今日热点预测 → 昨日热点复盘 → 今日其他推荐(secondary cards) → 30-min
update → group CTA (HomeProductLoop). No broad redesign.

## Guards (4 new + 25 prior = 29 + runtime)
check_daily_freshness · check_recommendation_closure · check_llm_copy_attractiveness · check_critical_ops_view.
