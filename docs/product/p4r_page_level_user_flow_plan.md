# P4R+ · Product Planner — Page-Level User Flow

## Homepage (order unchanged; real artifacts)
1. 今日热点预测 — active primary (selectedHotspot) card: reviewed lean + 主比分 + 冷门风险 + 进入战术室 + 复制/分享
2. 昨日热点复盘 — manifest finished[0] + observation receipt link (查看赛后观察)
3. 今日其他推荐 — secondary artifact-backed cards (score hook + 进入战术室)
4. 临场 30 分钟状态 — T-30 hook on the lead card
5. 进群 / 分享 CTA

## /predict (primary + secondary)
reviewed LLM headline (main_lean) · exact score (model_fields.recommended_score) · main reason (why) ·
hidden risk (risk_note / 冷门风险) · tactical variable (top_variable) · source basis (DataBacking:
source_facts + model_fields source tag) · share line (operations.share_copy). Missing → COPY_MISSING.

## /recap
observation/full/pending label · predicted vs actual · judgment (assessment) · what was right · what
was missed (deviation) · correction note (next_impact) · next hook · share line. Event data missing →
OBSERVATION_ONLY, never a fabricated turning point.

## /internal/daily
active_content_date · runtime_date · homepage_primary_fixture · homepage_yesterday_recap_fixture ·
prediction_copy_source · recap_copy_source · rendered_freshness_status · stale_reason · next operator
action · Send HOLD.
