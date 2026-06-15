# P1 · RECAP_GENERATION_CONTRACT

> Full recap generation contract. Prompt → reviewed → recap artifact. Enforced by
> `scripts/check_recap_generation_flow.py`. No fake full recap; observation-only when data is thin.

## Input
- archived pre-match artifact (pre_match_call, model_fields, tactical_read, t30 state)
- predicted score + actual score + match status
- observation receipt (if already built)
- event data (lineups/events/player stats) — IF ingested

## Output (reviewed recap JSON → recap artifact)
```json
{
  "hit_status": "hit | partial_hit | miss | pending",
  "recap_state": "OBSERVATION_READY | RECAP_READY | RECAP_ERROR | ...",
  "recap_ready": false,
  "headline": "strong recap headline",
  "deviation_reason": "why the result deviated from the call",
  "tactical_review": "tactical review (FULL recap only; '(pending …)' when data thin)",
  "turning_points": [],
  "model_calibration": "what the model should recalibrate",
  "next_match_impact": "string",
  "customer_summary": "string",
  "share_copy": "recap share copy",
  "internal_notes": "string",
  "llm_provider": "deepseek|gemini|kimi|operator_manual",
  "safety": { "no_fake_recap": true, "no_fake_probability": true, "no_auto_send": true }
}
```

## Rules (guarded)
- **No fake full recap.** A `RECAP_READY` artifact MUST carry a real `tactical_review` (not "pending").
- **If actual data is insufficient → OBSERVATION_READY only** (receipt: pre-match call → actual score
  → partial-hit/miss → deviation → calibration → next impact). `recap_ready=false`.
- **No raw backend errors** — the /recap route is gated (R3): observation-driven fixtures never call
  the backend recap endpoint, so no `no recap for fixture …` 404 leaks.
- **No invented player events** unless a source exists. `turning_points=[]` when no event feed.
- An OBSERVATION_READY artifact must NOT set `recap_ready=true` (no mislabeling).
- Recap share copy must be present (homepage/share card fall back to the observation `share_copy`).

## Recap states (see SLA_AND_STATE_MACHINE.md)
`WAITING_FT → FT_READY → OBSERVATION_READY → RECAP_PROMPT_READY → RECAP_REVIEW_READY → RECAP_READY`
plus `RECAP_ERROR` (no local source AND no backend recap → safe generic page, never an error string).

## Today's recap (1489371 Brazil 1-1 Morocco) — honest OBSERVATION_READY
- Full recap is BLOCKED: lineups/events/player stats are not ingested for this fixture → a full
  tactical review / turning points cannot be authored honestly.
- Delivered: `recap_1489371.json` (recap_state=OBSERVATION_READY, hit_status=partial_hit,
  recap_ready=false, full_recap_blocked_reason recorded), backed by `observation_1489371.json` (the
  customer receipt the /recap route already renders) + the recap prompt + reviewed JSON (the flow).
- 1489369 Mexico 2-0 South Africa is RECAP_READY (full recap exists via the backend report + bundled
  recap data) — demonstrating the full-recap tier alongside the observation tier.
