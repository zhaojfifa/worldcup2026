# R2 — ACCEPTANCE_CHECKLIST

> Owner's 12 non-negotiables, mapped to evidence. Marked at implementation close.

| # | Criterion | Plan / evidence |
|---|---|---|
| 1 | Fresh hotspot, not stale 06-14 NL–Japan | Belgium vs Egypt 1489377 (06-15), selected_hotspot repointed, 06-14 dropped from slate |
| 2 | /internal/daily shows selected fixture date + key | DailyStatusPage Date row + Selected hotspot row (date 2026-06-15, key 1489377) |
| 3 | model_fields.source not merely operator_estimated if a lookup exists | `source="computed"` (ScoutScore kaggle Elo+form+Poisson) |
| 4 | If no computed model, explain why + show fallback | model_lookup returns `unavailable`→operator_estimated for cold-start teams; /internal/daily states the reason (computed for 1489377; documented for Cape Verde) |
| 5 | LLM prompt file exists | `docs/data_audit/mvp2_predictions/prompts/20260615_1489377_prompt.md` |
| 6 | reviewed LLM JSON exists | `docs/data_audit/mvp2_predictions/reviewed/20260615_1489377_reviewed.json` |
| 7 | artifact updated from prompt/review chain | `match_Belgium-Egypt-20260615.json`, content_chain.prompt_generated+reviewed_applied |
| 8 | Homepage shows new hotspot first | fresh manifest + selected_hotspot → HotspotPrediction(1489377); screenshot (backend bypassed) |
| 9 | /predict shows strong call/score/risk/why/tactical/data-model-basis/T-30/share | ArtifactTacticalRoom + 数据与建模依据 block (source=computed) + ShareBlock; screenshot |
| 10 | /recap works for previous hotspot | /recap/1489371 observation receipt (carryover); screenshot |
| 11 | Screenshots provided | mvp2_r2_recovery/ (homepage, predict, internal-daily, share, recap) |
| 12 | Send remains HOLD | DailyStatusPage Send row + artifact safety.no_auto_send; no send performed |

## Guard gates (must all PASS)
- check_daily_content_flow (incl. NEW staleness check) · check_daily_readiness (incl. staleness) ·
  check_prediction_artifact · check_homepage_product_loop · check_growth_copy · npm run build.
- Live-dependent (check_customer_visible_copy / check_runtime_daily_fixtures): run against the deployed
  bundle; state clearly that R2 is on a branch (not deployed) so those reflect the live (pre-R2) site.

## HOLD triggers (return HOLD if any true)
stale hotspot · no fresh fixture · missing prompt/review/artifact · missing screenshots · hidden
source/model status · fake model_fields · homepage not showing the selection · thin /predict · blank
share card · missing T-30 slot.
