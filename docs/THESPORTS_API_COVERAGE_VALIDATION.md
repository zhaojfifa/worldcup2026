# TheSports API — Coverage Validation Evaluation

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Mode:** docs-only. **TheSports was NOT called** (no token). Public site, checked 2026-06-10.
> Parent: [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md).

---

## 1. What it is
TheSports (thesports.com) is a **native sports-data API** (real-time + historical), positioned as a deep football
feed — the kind of source that could close our **deep-intelligence** gap (lineup/player/coach/injury).

## 2. Deep-field coverage (advertised — must be trial-verified)
| field | advertised | verify in trial |
|---|---|---|
| football lineups / team lineups | **yes** | confirm starting XI + bench |
| formations / player positions | **yes** (single-match lineups, positions) | confirm formation string |
| player ratings / stats | **yes** ("player ability technology", match player stats) | confirm rating scale |
| **injuries** | **yes** (injury data) | confirm freshness + per-fixture |
| suspensions | **unknown** | ask sales |
| coach | **yes** (coach data referenced) | confirm per-team |
| squad | **yes** (season player stats, transfers) | confirm full squad |
| standings / rankings | **yes** (season rankings, FIFA/club rankings) | — |
| live | **yes** (real-time text broadcast) | — |

## 3. WC coverage (must be confirmed)
- **WC2022 historical:** **unknown** — site lists "Historical Compensation" (suggesting historical fill exists) but
  does not confirm FIFA WC 2022 specifically. **Verify in trial.**
- **WC2026:** **referenced** ("World Cup 2026 solution") — **verify** fixtures/lineups availability in trial.

## 4. Trial & pricing
- **15-day free trial** — advertised as automatic on signup.
- **Pricing: not published** → **sales/contact** required for a quote *(verify)*.
- **Commercial use:** presumably yes under a paid contract — **terms via sales** (medium commercial risk: unknown
  pricing/SLAs/coverage until confirmed).

## 5. Capability verdict vs. our gap
If WC coverage is confirmed, TheSports could supply the entire **deep-intelligence** layer that round 1 found
missing (lineup/player/coach/injury) — i.e. a **Route B** candidate, likely cheaper than Sportradar (enterprise).
**Risk:** unpublished pricing + unverified WC2022/2026 coverage + unverified data reliability.

## 6. Operator actions (Owner-gated)
1. **Apply for the 15-day free trial** (operator; needs a TheSports account/token).
2. **Request a sample payload** for: one WC2022 match (lineup + injuries) and one WC2026 fixture (if available).
3. **Confirm** WC2022 historical + WC2026 coverage, lineup/injury/coach depth, and per-fixture freshness.
4. **Request a written quote** (commercial terms, rate limits, SLA, allowed commercial use).
5. Compare against **API-FOOTBALL paid** and **Highlightly** before choosing a Route B primary.
6. **No code/API/DB wiring** until Owner approves a provider + budget.

## Sources
[thesports.com/api](https://www.thesports.com/api) · [football lineups widget](https://www.thesports.com/widgets/football/9)
