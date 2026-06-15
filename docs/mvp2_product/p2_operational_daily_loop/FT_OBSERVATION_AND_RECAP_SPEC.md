# P2 · FT_OBSERVATION_AND_RECAP_SPEC

> Durable queue: `docs/data_audit/mvp2_recap_queue/<date>.json`. Guard: `scripts/check_recap_queue.py`
> (+ existing `check_recap_generation_flow.py` / `check_recap_seed_grounding.py`). No fake recap.

## States → publish_eligibility
`WAITING_FT → FT_READY → OBSERVATION_READY → RECAP_READY` (+ `RECAP_ERROR`).
- `RECAP_READY` (full recap artifact OR bundled real_recap narrative) → **PUBLISHED**.
- `OBSERVATION_READY` (receipt; full recap blocked by missing event data) → **OBSERVATION_READY**
  (never relabelled PUBLISHED — observation is not a full recap).
- otherwise → **PENDING** (build observation/recap).

## Rules
- Every item carries the `no_fake_recap` guard marker.
- Full recap requires real event data; when lineups/events are not ingested, stay OBSERVATION_READY
  and say so (the blocked reason is recorded). Never fabricate turning points / player events.
- `recap_seed` (from the prediction draft) links the pre-match call to the recap check (grounding).

## Today (2026-06-15): Brazil-Morocco OBSERVATION_READY (full recap blocked — no event data),
Mexico-SA RECAP_READY (full recap live), Sweden-Tunisia PENDING.
