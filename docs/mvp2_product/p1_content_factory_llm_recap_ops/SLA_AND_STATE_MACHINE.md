# P1 · SLA_AND_STATE_MACHINE

> The two state machines (prediction + recap) and the operating SLA. Prediction states are derived
> from the bundled artifact by `mvp2_build_daily_content_queue.py content_state`; recap states by the
> queue builder + `recapState()` (frontend). Times are UTC, relative to a match's kickoff (KO).

## Prediction state machine
```
FIXTURE_READY → MODEL_READY → PROMPT_READY → REVIEW_READY → ARTIFACT_READY → PUBLISHED
                                                                              ↘ T30_PENDING → T30_READY
```
| State | Meaning (derived from artifact) |
|-------|---------------------------------|
| FIXTURE_READY | fixture in slate, no artifact |
| MODEL_READY | artifact + model_fields present |
| PROMPT_READY | content_chain.prompt_generated |
| REVIEW_READY | content_chain.reviewed_applied |
| ARTIFACT_READY | model_fields + reviewed + judgement present |
| PUBLISHED | ARTIFACT_READY + prediction_confirmed (renders on /predict + homepage) |
| T30_PENDING / T30_READY | artifact.t30.status (pending until lineups; ready/skipped after) |

Today: Belgium-Egypt, Saudi-Uruguay, Spain-CapeVerde all PUBLISHED; t30 = pending (honest, pre-lineups).

## Recap state machine
```
WAITING_FT → FT_READY → OBSERVATION_READY → RECAP_PROMPT_READY → RECAP_REVIEW_READY → RECAP_READY
                                                                                      ↘ RECAP_ERROR
```
| State | Meaning |
|-------|---------|
| WAITING_FT | finished fixture, no confirmed score yet |
| FT_READY | final score present, no observation yet |
| OBSERVATION_READY | observation receipt built (recap_ready=false) — the safe customer tier |
| RECAP_PROMPT_READY / RECAP_REVIEW_READY | recap prompt generated / reviewed JSON applied |
| RECAP_READY | full recap artifact with real tactical_review (recap_ready=true) |
| RECAP_ERROR | no local source AND no backend recap → safe generic page, never a raw error string |

Today: 1489371 = OBSERVATION_READY (full recap blocked, data thin); 1489369 = RECAP_READY.

## SLA (operator targets — surfaced on /internal/daily, not a clock-enforced gate)
| Stage | Target |
|-------|--------|
| Morning slate sync | by local morning (≈10:00 UTC) |
| Primary + secondary prediction | before each match's day window |
| T-30 update | within KO−30 → KO |
| FT observation | 30–60 min after the result |
| Full recap | within the next-day window |

`check_daily_update_sla.py` (R3) + `check_content_queue.py` (P1) assert the STATES are represented
and honest; the operator console shows the next required action and the send-HOLD posture.
