# P1 · MATCH_PRIORITY_QUEUE

> How the content factory ranks and selects matches. Implemented in
> `scripts/mvp2_build_daily_content_queue.py` (`priority_score`). Transparent, editorial — NEVER an
> odds/betting signal.

## Inputs (per fixture)

| Input | Source | Used how |
|-------|--------|----------|
| match date / kickoff time | slate | scheduled fixtures score +10; primary must be current |
| team popularity | static `POPULAR` set (Brazil, Spain, Belgium, Uruguay, …) | +25 per popular team |
| market relevance (vi/my fan pull) | static `MARKET` set (Japan, Saudi Arabia, …) | +20 per market team |
| host relevance 2026 | static `HOST` set (USA, Canada, Mexico) | +15 per host team |
| model uncertainty / upset potential | `model_fields.risk_level` (中/中高/高) | +10 narrative-upset |
| source coverage | `model_fields.source` | computed +20 · operator_estimated/seed +8 · missing +0 |
| operational timing | `status == scheduled` | +10 |

## Output

```json
{
  "date", "generated_at", "scoring": { weights, note },
  "primary_hotspot": { fixture_key, home, away, status, content_state, source_coverage, priority_score, ... },
  "secondary_matches": [ up to 4, ranked ],
  "recap_queue": [ finished fixtures, recap_state ],
  "t30_queue": [ scheduled fixtures with an artifact ],
  "send_status": "HOLD"
}
```

## Selection rules (enforced + guarded by `check_content_queue.py`)

- **primary_hotspot** = the `selectedHotspot` (P7 P0-1 AUTHORITY) when it is active, in today's slate,
  scheduled, and CURRENT (selection date not older than the slate date). Otherwise the top-scored
  scheduled fixture. **A stale fixture can never be primary** (it can only appear as a carryover recap).
- **secondary_matches** = remaining scheduled fixtures, ranked by `priority_score`, capped at 4.
- **recap_queue** = finished fixtures; each carries a `recap_state` (WAITING_FT / FT_READY /
  OBSERVATION_READY / RECAP_READY) derived from score + observation/recap presence.
- **t30_queue** = scheduled fixtures that already have a prediction artifact (a `t30` slot to confirm
  at KO−30).
- **source coverage missing** is stated on every row (`source_coverage: missing`) and surfaced on
  /internal/daily — never hidden, never faked.
- A selected secondary match must still get a `/predict` route — it does, because its artifact's
  `fixture_key`/`id` resolves in `getPredictionArtifact`.

## Today's queue (2026-06-15, real)

| Role | Match | priority_score | source | content_state |
|------|-------|----------------|--------|---------------|
| primary | Belgium vs Egypt (1489377) | — (selectedHotspot authority) | computed | PUBLISHED |
| secondary | Saudi Arabia vs Uruguay (1489379) | 85 (Uruguay popular+market, computed, upset, scheduled) | computed | PUBLISHED |
| secondary | Spain vs Cape Verde Islands (1489380) | 53 (Spain popular, operator_estimated, scheduled) | operator_estimated | PUBLISHED |
| recap | Brazil 1-1 Morocco (1489371) | — | — | OBSERVATION_READY |
| recap | Mexico 2-0 South Africa (1489369) | — | — | RECAP_READY |
| recap | Sweden vs Tunisia (1539002) | — | — | WAITING_FT (no score) |
