# P2 · T30_UPDATE_QUEUE_SPEC

> Durable queue: `docs/data_audit/mvp2_t30_queue/<date>.json`. Guard: `scripts/check_t30_queue.py`.
> T-30 claims are never invented.

## Item status
`T30_PENDING` (pre-lineups — honest checkpoint, NO faked update_text) · `T30_READY` (operator
confirmed the KO-30 re-check) · `T30_SKIPPED` (no change).

## Rule (guarded)
A `T30_PENDING` item must carry the `pending=>no faked update_text` guard marker — the artifact's
`t30.update_text` stays null until the operator confirms lineups at KO-30. No invented lineup/score.

## Deadline
Per fixture: `KO-30` (30 minutes before that fixture's kickoff). The command center lists each
fixture's t30 status so the operator knows which matches need the KO-30 re-check.

## Today (2026-06-15): 3 items, all T30_PENDING (lineups not out) — honest, no faked updates.
