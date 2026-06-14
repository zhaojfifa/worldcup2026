# Growth P1.5c — Agent-led Daily Editorial Selection

> Owner correction (2026-06-13): **we are building an agent product on top of LLMs, not a
> hand-coded sports ranking engine.** P1.5c adds an editorial-selection *workflow*, not a
> scoring engine. Engineering provides facts + a safe prompt; the LLM provides editorial
> judgment; the operator confirms what becomes public; the frontend renders the confirmed
> selection. **First send remains HOLD.**

## ★ Owner product-mechanism correction (2026-06-14)

> **Daily selection must be Agent-led and LLM-assisted. The system should not mechanically
> promote whichever fixture is `recap_ready`. The daily story should be selected from current
> fixtures, match importance, public heat, result surprise, and growth objective by
> DeepSeek/Gemini/Kimi or equivalent LLM, then confirmed by the operator.**

The gap this closes: daily fixtures can update, the homepage can render states, and growth
attribution works — but **featured match / recap priority was not yet driven by the daily
hotspot story.** Mechanically surfacing the only `recap_ready` fixture is wrong: it lets a
lesser match override the real daily story. The hotspot is an editorial judgment (LLM-recommended,
operator-confirmed), not a `recap_ready` flag.

**Concrete rule for 2026-06-13 (the hotspot is Brazil vs Morocco):**
- **Before kickoff** — Brazil vs Morocco is the **featured pre-match** (the daily story).
- **After it finishes** — Brazil vs Morocco becomes the **first recap-priority candidate**.
- Mexico vs South Africa remains **fallback / secondary recap, not the main story** — it must
  not override the Brazil/Morocco story just because it is `recap_ready` first.
- Canada / USA / South Korea remain **completed status only** unless the operator selects one.
- Qatar / Haiti remain **upcoming status only** unless the operator selects one.

This is a product-mechanism rule, not new code: it lives in the prompt wording + operator
confirmation, **not** in a scoring engine or hand-coded weights.

## What this is

A tiny CLI helper — `scripts/mvp2_editorial_agent.py` — that reads today's fixture slate from
existing local daily-fixture data and prints a **copy-paste prompt** for an external LLM
(DeepSeek / Gemini / Kimi). The operator pastes the prompt, reads back a structured JSON
recommendation, and **decides manually** what (if anything) becomes the day's featured
pre-match / featured recap / group-only suggestions — or to hold.

## What it deliberately does NOT do

- ❌ No team-popularity / country-ranking / match-importance / hotspot weights.
- ❌ No complex if/else editorial logic that "decides" the hotspot itself.
- ❌ No external LLM / paid API call (it only prints text to stdout).
- ❌ No production-state write (no daily-fixtures upload, no manifest write).
- ❌ No send, no join-intent confirmation, no contribution value, no auto-publish.

This is why **no scoring engine was added**: the editorial judgment is the LLM's job, gated by
operator confirmation. Engineering only assembles facts and a safe, constrained prompt.

## Usage

```bash
python3 scripts/mvp2_editorial_agent.py prompt --date 2026-06-13 --lang zh
python3 scripts/mvp2_editorial_agent.py prompt --date 2026-06-13 --lang vi
python3 scripts/mvp2_editorial_agent.py --selftest      # 7/7 embedded checks
```

`--lang` ∈ `zh | vi | my | en` (default `zh`). The JSON schema is always English keys; only the
human-readable fields are written in the chosen language (vi/my never fall back to Chinese).

## How the fixture slate is read

First existing source wins (no fetch, no fabrication):

1. `docs/data_audit/mvp2_match_sync/daily_fixtures_YYYYMMDD.json` — richest registry (preferred)
2. `frontend/public/data/daily-fixtures.json` — runtime manifest
3. `frontend/src/data/dailyFixtures.generated.json` — build-time fallback

Both shapes are normalized to: `fixture_id · match · status · lifecycle_state · kickoff_utc ·
score · pre_match_allowed · recap_ready · recap_needed · renderable`. Scores are surfaced ONLY
where present (`scoreHome`/`scoreAway` not null) — the prompt instructs the LLM never to invent one.

## Prompt contents

The generated prompt includes: the day's fixture slate (facts), the product policy (one public
featured pre-match + one public featured recap + everything else lightweight status + extra
service handled inside the group + recommendation is not auto-public), the current homepage
policy (Brazil vs Morocco = daily story until kickoff; Mexico 2-0 South Africa = secondary recap
if no better recap-ready match), hard constraints (pre-match needs `pre_match_allowed=True`;
recap needs `recap_ready=True` else null + explain in `fallback_recap`), and safety rules
(no betting/trading vocabulary, no invented scores, no fake recap, no auto-send, no certainty,
no implying it's already published).

## Required LLM output schema

```json
{
  "date": "YYYY-MM-DD",
  "featured_pre_match": { "fixture_id": "...", "match": "...", "reason": "...", "public_angle": "...", "score_call": "...", "risk_note": "..." },
  "featured_recap":     { "fixture_id": "... or null", "match": "... or null", "reason": "...", "public_angle": "..." },
  "fallback_recap":     { "fixture_id": "... or null", "match": "... or null", "reason": "..." },
  "group_only_suggestions": [ { "fixture_id": "...", "match": "...", "reason": "..." } ],
  "hold_reason": null
}
```

## How the operator confirms a recommendation

1. Run the CLI for the date/lang and copy the printed prompt.
2. Paste it into DeepSeek / Gemini / Kimi; read back the JSON.
3. **Sanity-check against the slate**: featured_pre_match must be a `pre_match_allowed=True`
   fixture; featured_recap (if non-null) must be `recap_ready=True`; no invented score; no
   forbidden vocabulary.
4. If accepted, the operator applies the selection through the **existing** P1.3/P1.4 manual
   path (`mvp2_match_sync.py` slate edit + `daily-fixtures` upload). P1.5c writes nothing.
5. If the LLM returns `hold_reason`, the homepage stays on the current policy.

## Guard note

`scripts/mvp2_editorial_agent.py` is **not** in `check_growth_copy.py`'s scanned globs — like
the other scanner scripts that carry detection word-lists, it intentionally embeds the forbidden
vocabulary (to instruct the LLM to avoid it). The *output* copy the operator publishes still goes
through `check_growth_copy.py` / the live visible-copy scan before any public use.

## Deploy impact

**None.** Docs + one new local-only script. No frontend bundle change, no backend schema, no
endpoint change, no growth-attribution change. `npm run build` not required for this change
(no frontend/runtime source touched).

## First-send gates (unchanged)

- Gate 1 Ambassador codes — ✅ PASS (QG-TEST1 / TT-VN88 / FO-MM21 active)
- Gate 2 Growth smoke — ✅ PASS (no send; 3 pending test join-intents NOT to be confirmed; contribution value = 0)
- Gate 3 — 1489371 Brazil vs Morocco LIVE/FT lifecycle — ⏳ PENDING (KO 2026-06-13 22:00 UTC)
- Gate 4 — Owner per-channel GO — ⏳ PENDING

**Recommendation: First send remains HOLD until Gate 3 lifecycle validation and Gate 4 Owner
per-channel GO pass.** P1.5c is a planning aid for the operator, not a trigger to send.
