# P1 · CONTENT_FACTORY_SPEC

> Branch `feature/mvp2-p1-content-factory-llm-recap-ops` off tag
> `mvp2-r3-content-sla-recap-gate-live-baseline-20260615`. Goal: production CAPACITY — more than one
> match per day, timely updates, strong LLM copy, recap closure, operator console. No UI redesign;
> no auto-send; no weakened compliance.

## Pipeline (what runs each day)

```
daily fixture slate (daily-fixtures.json)
 → priority scoring            scripts/mvp2_build_daily_content_queue.py (priority_score)
 → match selection queue       dailyContentQueue.json {primary_hotspot, secondary_matches[]}
 → model/source lookup         mvp2_build_daily_prediction_artifact.py model_lookup (ScoutScore v0.2)
 → prediction prompt           docs/data_audit/mvp2_predictions/prompts/<date>_<key>_prompt.md
 → reviewed JSON               docs/data_audit/mvp2_predictions/reviewed/<date>_<key>_reviewed.json
 → prediction artifact         frontend/src/data/predictionArtifacts/match_<Home>-<Away>-<date>.json
 → homepage / predict / share  HomeProductLoop (primary + secondary cards) · /predict · ShareBlock
 → T-30 update                 artifact.t30 (pending→ready/skipped) — honest, never faked
 → full-time observation       frontend/src/data/predictionArtifacts/observation_<id>.json
 → recap prompt                docs/data_audit/mvp2_recaps/prompts/<date>_<id>_recap_prompt.md
 → reviewed recap JSON         docs/data_audit/mvp2_recaps/reviewed/<date>_<id>_recap_reviewed.json
 → recap artifact              frontend/src/data/recapArtifacts/recap_<id>.json
 → share copy / card           operations.share_copy + /share/fixture|recap routes
 → internal readiness          /internal/daily content-factory queue console (DailyStatusPage.tsx)
```

## Artifact naming (canonical)

| Artifact | Path | Naming |
|----------|------|--------|
| Content queue | `frontend/src/data/dailyContentQueue.json` | one per day (overwritten) |
| Prediction prompt | `docs/data_audit/mvp2_predictions/prompts/` | `YYYYMMDD_<fixture_key>_prompt.md` |
| Prediction reviewed | `docs/data_audit/mvp2_predictions/reviewed/` | `YYYYMMDD_<fixture_key>_reviewed.json` |
| Prediction artifact | `frontend/src/data/predictionArtifacts/` | `match_<Home>-<Away>-YYYYMMDD.json` |
| Observation artifact | `frontend/src/data/predictionArtifacts/` | `observation_<id>.json` |
| Recap prompt | `docs/data_audit/mvp2_recaps/prompts/` | `YYYYMMDD_<id>_recap_prompt.md` |
| Recap reviewed | `docs/data_audit/mvp2_recaps/reviewed/` | `YYYYMMDD_<id>_recap_reviewed.json` |
| Recap artifact | `frontend/src/data/recapArtifacts/` | `recap_<id>.json` |

## P1 delivered against the acceptance target

1. 1 primary hotspot — Belgium vs Egypt (1489377). ✅
2. 2–4 secondary matches — Saudi Arabia vs Uruguay (1489379), Spain vs Cape Verde Islands (1489380). ✅
3. Prediction artifacts for primary + 2 secondary. ✅ (`check_prediction_artifact` 4 prediction artifacts)
4. Strong LLM prompts for each selected match. ✅ (3 prompt files under mvp2_predictions/prompts/)
5. Reviewed JSON for each selected match. ✅ (3 reviewed files; provider operator_manual)
6. Homepage shows primary hotspot + secondary match cards. ✅ (HomeProductLoop SecondaryMatchCard)
7. /predict works for every selected match. ✅ (getPredictionArtifact resolves 1489377/1489379/1489380)
8. Observation/recap state after finish. ✅ (observation_1489371 + recap_1489371 OBSERVATION_READY)
9. /recap works without raw backend errors. ✅ (R3 gate retained; recap flow guard)
10. /internal/daily shows queue/status/deadlines/missing work/next action. ✅ (content-factory queue console)

## Hard rules carried from R3 (unchanged)
win_prob/confidence stay null; model source is tagged computed/operator_estimated/unavailable, never
mock; no betting/odds vocab; no fake recap; no auto-send (send=HOLD); auto-LLM remains operator-manual
(P1-of-P1 — traceable via content_chain).
