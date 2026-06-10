# MVP-2 — Next Data Requirements (product model gap)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Mode:** requirements doc (no integration this round). Companion to
> [MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN](MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md) and the four-match operator review.

The productized report proves the pipeline works on **currently available** Level-2 data. The gaps below are what
the product needs next to move from *post-match explanation* toward *credible pre-match scouting*. **This is a
requirements list only — no vendor is committed, no integration is started this round** (Owner-gated). Odds /
betting / market data is **out of scope by policy** and intentionally excluded.

Each item: **product use · already have? · gap · candidate sources · commercial/license risk · priority.**

---

## 1. Injuries / suspensions — **P0 (highest)**
- **Product use:** absence risk, squad completeness, expected lineup changes, and *why a side is weakened* — the
  one explanation the current report explicitly cannot make.
- **Already have?** No. API-FOOTBALL `/injuries` returns HTTP 200 / **0 results** for the WC2022 fixtures
  (verified, all four). Marked `injuries_unresolved=true`, rendered "source required".
- **Gap:** no injury/suspension feed for the target competitions.
- **Candidate sources:** API-FOOTBALL **current-season re-check** (injuries are often populated for live/upcoming
  fixtures, not historical) · Sportmonks · TheSports · Transfermarkt (scrape/licensed).
- **Commercial/license risk:** API-FOOTBALL paid plan covers it if current-season returns data; Transfermarkt
  scraping is **license-risky** (confirm terms). Medium.
- **Priority:** **P0** — unblocks availability features; do **not** start integration until Owner GO.

## 2. xG / advanced stats — **P1**
- **Product use:** explain "possession/shots dominance but lost" (855737), chance quality, and the luck/efficiency
  dimension the report currently must omit.
- **Already have?** No. API-FOOTBALL 2022 statistics contain **no `expected_goals`**; xG is excluded by policy this round.
- **Gap:** no validated xG / shot-quality data.
- **Candidate sources:** **StatsBomb Open Data** (internal/offline calibration only) · FBref (Opta-derived, license-bound) ·
  a commercial xG provider.
- **Commercial/license risk:** **High** — StatsBomb is **non-commercial / offline only**; FBref/Opta require a
  commercial license. Keep offline until license confirmed.
- **Priority:** **P1**.

## 3. Elo / team strength — **P1**
- **Product use:** pre-match strength baseline, a principled **definition of "upset"**, and matchup framing.
- **Already have?** Partial — Kaggle historical results are downloaded locally (`data/external/kaggle/`, gitignored),
  but no Elo/strength model is built.
- **Gap:** no team-strength rating in the pipeline.
- **Candidate sources:** **World Football Elo Ratings** · an internal Elo computed from Kaggle results (CC0 — confirm).
- **Commercial/license risk:** Low (World Football Elo / self-computed). Confirm attribution terms.
- **Priority:** **P1**.

## 4. Squad / transfer value — **P2**
- **Product use:** paper strength, squad depth, "favourite vs underdog" context for the upset narrative.
- **Already have?** No.
- **Gap:** no squad valuation.
- **Candidate sources:** **Transfermarkt** (squad/transfer values).
- **Commercial/license risk:** **High** — Transfermarkt scraping/commercial use is license-restricted. Confirm before use.
- **Priority:** **P2**.

## 5. Recent form / H2H — **P1**
- **Product use:** pre-match state (last-N form), head-to-head history, momentum framing.
- **Already have?** Partial — API-FOOTBALL fixtures history is reachable; Kaggle results held locally; not yet derived.
- **Gap:** no computed form/H2H features.
- **Candidate sources:** **API-FOOTBALL fixtures history** (`/fixtures?team=&last=`) · Kaggle results · Elo deltas.
- **Commercial/license risk:** Low–Medium (API-FOOTBALL plan covers fixtures; Kaggle CC0 — confirm).
- **Priority:** **P1**.

## 6. Venue / travel / weather — **P2**
- **Product use:** 2026 USA/Canada/Mexico environment variables (travel distance, altitude, heat) — a real
  differentiator for the 2026 tournament.
- **Already have?** Partial — fixture venue name/city is in the pack; no geo/travel/weather.
- **Gap:** no venue geo, travel-distance model, or weather feed.
- **Candidate sources:** **FIFA venue list** · a weather API · an internal travel-distance model from venue geo.
- **Commercial/license risk:** Low–Medium (weather APIs vary; confirm commercial tier).
- **Priority:** **P2**.

---

## Priority summary
| # | data | priority | already? | top license risk |
|---|---|---|---|---|
| 1 | injuries / suspensions | **P0** | no | Transfermarkt scrape (med) |
| 2 | xG / advanced stats | P1 | no | StatsBomb non-commercial / Opta license (high) |
| 3 | Elo / team strength | P1 | partial | low |
| 5 | recent form / H2H | P1 | partial | low–med |
| 4 | squad / transfer value | P2 | no | Transfermarkt (high) |
| 6 | venue / travel / weather | P2 | partial | low–med |

## Out of scope (policy)
Odds / market / betting lines / 盘口 / 竞猜 — **excluded**, not a data gap to fill.

## Guardrails honored
requirements only · no integration started · no vendor committed · odds/market excluded · external operation paused ·
PR #2 untouched · Owner GO required before any source is integrated.
