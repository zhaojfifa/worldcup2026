# P5A · Gate Spec — Core 1+2 Content Quality (frozen)

## Homepage zones (order)
今日主推 (primary, v2) → 昨日热点复盘 (recap v2) → 今日其他推荐 (2 secondary v2 cards) → 30-min → CTA.

## Copy structures
Prediction v2 / Secondary v2 / Recap v2 per docs/specs/p5a_llm_copy_contract_v2.md.

## Allowed files
predictionArtifacts/*.json (reviewed-synced i18n + copy_v2), observation/recap artifacts,
predictionArtifacts.ts interface, ArtifactTacticalRoom.tsx, HomeProductLoop.tsx, RecapDetailPage/
ObservationReceipt, ShareCardPage projection, DailyStatusPage trace, mvp2_build_daily_prediction_artifact.py
(apply copy_v2 sync), reviewed/closure/recap/share artifacts, guards, screenshots, docs.

## Forbidden
match-count expansion, scheduler, payment/token/referral, backend schema/deploy, betting/odds, fake
probability/confidence/lineup/injury/event/full-recap, auto-send/publish, operator_estimated→primary,
2022/demo as active content, broad redesign.

## Guards (6, rendered-DOM): check_p5a_copy_contract / _homepage_content_quality / _predict_content_quality
/ _recap_content_quality / _share_content_quality / _internal_daily_trace.
## Review: Claude self-review PASS + Codex independent review PASS before merge.
