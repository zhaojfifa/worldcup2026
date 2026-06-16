# P4R+ · Page-Level Source Trace (diagnosis — before new code)

> Branch `fix/mvp2-p4r-page-level-product-reality` (off the clean P4R fix branch). Per page: the real
> source artifact, the rendered field, the fallback path, and how a guard detects stale/demo content
> and proves the reviewed LLM copy actually rendered. The P4R fix already synced reviewed JSON → zh
> i18n; this doc freezes the trace and motivates the 5th guard (`check_page_level_source_trace.py`).

| # | Page / element | Source artifact | Rendered field | Fallback path | Detect stale/demo | Prove LLM copy rendered |
|---|----------------|-----------------|----------------|---------------|-------------------|--------------------------|
| 1 | Homepage primary card | runtime manifest (backend→static→bundled) + `predictionArtifacts/<primary>.json` | `HotspotPrediction` → `buildStrongCall` → `i18n.zh.prediction.primary_direction` (synced from reviewed `main_lean`) + `model_fields.recommended_score` | manual FocusBlock frame if NO artifact | primary teams (Belgium/Egypt) must be in DOM; no Qatar/Ecuador/Netherlands/Japan | reviewed `main_lean[:14]` substring in DOM |
| 2 | Homepage yesterday recap card | manifest `finished[0]` + `observation_<id>.json` | `HotspotRecap` (teams+score) + link to `/recap/<id>` | safe recap frame | recap teams (Brazil/Morocco) in DOM | observation assessment text in `/recap` (page 6) |
| 3 | Homepage secondary cards | manifest scheduled (non-primary) + `predictionArtifacts/*` | `SecondaryMatchCard` → `buildStrongCall` score hook + `进入战术室` | lightweight status row if no artifact | secondary teams (Saudi/Uruguay, Spain/Cape Verde) in DOM | score hook + lean rendered on the card |
| 4 | `/predict/1489377` | `match_Belgium-Egypt-20260615.json` | `ArtifactTacticalRoom` → `buildStrongCallFromArtifact` (`i18n.zh` synced) + `DataBacking` (`model_fields`/`source_facts`) | pending labels (方向待临场确认) | fixture teams in DOM | reviewed `main_lean`/score/risk/variable/share rendered |
| 5 | `/predict/1489379` | `match_SaudiArabia-Uruguay-20260615.json` | same as #4 | same | same | same |
| 6 | `/recap/1489371` | `observation_1489371.json` (recap_ready=false) | `ObservationReceipt` → `i18n.zh` (receipt/pre_match_call/actual_line/assessment/deviation/next_impact/share) | safe OBSERVATION page (no content) | observation teams + score in DOM | assessment/deviation/next_impact rendered + OBSERVATION label |
| 7 | `/share/fixture/1489377` | `match_*.json` `i18n.zh.operations.share_copy` (synced from reviewed `share_copy`) | `ShareCardPage` | observation share fallback | fixture teams | reviewed share_copy substring |
| 8 | recap share card `/share/recap/1489371` | `observation_1489371.json` `i18n.zh.share_copy` | `ShareCardPage` (recap) → `recapShareCopy` | observation `share_copy` | teams + score | observation share_copy substring |
| 9 | `/internal/daily` critical ops | `dailyOpsState.json` (freshness + recommendation_closure folded in) + the primary artifact `rendered_copy_source` | `DailyStatusPage` Critical ops + source-trace rows | warn labels | freshness FRESH/STALE; runtime vs artifact date | `prediction_copy_source = operator_reviewed_llm_judgment` row |

## BLOCKED / honest states (must be shown, never silently bypassed)
`COPY_MISSING` · `REVIEW_REQUIRED` · `OBSERVATION_ONLY` · `PENDING` · `SOURCE_MISSING` ·
`BLOCKED_DAILY_FRESHNESS`.

## Why the 5th guard (`check_page_level_source_trace.py`)
The four existing rendered guards each verify ONE concern (freshness / prediction copy / recap copy /
homepage wiring). The Owner wants a single page-level trace gate that, for the canonical set of pages
(#1–#9), proves each rendered page carries its source artifact's content (teams + the reviewed-copy
substring) and carries NO demo fixture — a one-shot "the visible product == the source of truth" check.

## Out of scope (frozen)
backend schema, auto-send, auto-publish, scheduler, payment/referral/token, fake event/full recap,
broad redesign. vi/my/en prediction copy stay authored translations (reviewed JSON is zh-canonical).
