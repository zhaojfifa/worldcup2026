# P1 · DAILY_OPERATOR_CONSOLE_SPEC

> `/internal/daily` (DailyStatusPage.tsx) becomes the operator command console. Unlinked, read-only,
> no secrets, no send. Guarded by `scripts/check_operator_console.py`.

## What the console shows (delivered)

### Section 1 — daily readiness (R3, retained)
date · selected hotspot · live homepage lead · selection==lead · prediction artifact · score-call
hook · source facts · model fields · win_prob/confidence (null) · operator confirmation · content
chain (prompt/reviewed/provider) · share kit · T-30 status · observation/recap carryover · slate
freshness · backend drift (MATCH/FALLBACK/STALE) · data source validity · content grounding · update
SLA state · recap SLA state · last successful generation · **next operator action** · send HOLD.

### Section 2 — content factory queue (P1, new)
Reads `dailyContentQueue.json`:
- **Queue date**
- **Primary hotspot** — match + content_state + source coverage
- **Secondary matches** — count, then one row per secondary: content_state, prediction readiness,
  prompt/review readiness, source coverage, recommended score, `/predict/<key>` link
- **T-30 queue** — per-match t30 status
- **Recap queue** — per finished match: score → recap_state
- **Source coverage** — flags any `missing` coverage (never hidden)
- **Queue send status** — HOLD

## Console guard requirements (`check_operator_console.py` FAILS if missing)
primary hotspot · secondary queue · prediction readiness · content/LLM grounding readiness · recap
readiness · SLA status · next operator action · send HOLD.

## Compliance
The console NEVER shows betting/odds vocab; NEVER the bare word "LLM" as display copy (uses "Content
grounding"); NEVER a fake probability. It is the single screen the operator reads to know: what is
ready, what is missing, what to do next, and that send is held.
