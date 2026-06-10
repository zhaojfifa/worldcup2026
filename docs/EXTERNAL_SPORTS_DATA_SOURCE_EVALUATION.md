# External Sports Data Source Evaluation (Sprint v1)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Sprint:** External Sports Data Source Evaluation · **Mode:** docs-only (no code, no API calls with tokens).
> **Method:** read-only research of public docs/pricing pages (checked 2026-06-10). **No source was called with a
> token.** Pricing/coverage marked *(verify)* must be re-confirmed by the operator before any purchase.
> **Companions:** [SERPAPI_SPORTS_RESULTS_EVALUATION](SERPAPI_SPORTS_RESULTS_EVALUATION.md) ·
> [KAGGLE_WC2022_CROSS_VALIDATION](KAGGLE_WC2022_CROSS_VALIDATION.md) ·
> [THESPORTS_API_COVERAGE_VALIDATION](THESPORTS_API_COVERAGE_VALIDATION.md) ·
> [REAL_INTELLIGENCE_SOURCE_MATRIX](REAL_INTELLIGENCE_SOURCE_MATRIX.md)

---

## 0. Gap this sprint must close (from round 1)

Confirmed from [WC2022_HISTORICAL_DATA_COMPLETENESS_REPORT](WC2022_HISTORICAL_DATA_COMPLETENESS_REPORT.md) +
[wc2022_historical_completeness.json](data_audit/wc2022_historical_completeness.json):
WC2022 `finished=64`, `report available=0/64`, **no per-match `final_score`/`actual_winner` exposed**,
player/coach/lineup/injury/media/odds **missing**, `42.2%` internal-only, Evidence Pack honesty correct.
So an external source must add: **(a) per-match real result** (cheap, unblocks upset/form/H2H) and/or
**(b) deep intelligence** (lineup/player/coach/injury) for real WC2026.

---

## 1. Source evaluations

### 1. Kaggle — international football results datasets
- **official_url:** https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017 (now "1872 to 2026")
- **data_type:** static community CSV dataset (downloadable), not an API
- **key_fields_available:** `date, home_team, away_team, home_score, away_score, tournament, city, country, neutral` (results.csv); plus `goalscorers.csv`, `shootouts.csv` (~49k matches, 1872→2026)
- **WC2022 coverage:** **yes** (tournament = "FIFA World Cup", 2022 Qatar matches) *(verify exact rows on download)*
- **WC2026 coverage:** forward-only — populated as matches are played (WC2026 not yet played)
- **player/coach/lineup/injury:** **no** (results + goalscorers only)
- **final_score / actual_winner:** **yes** (home_score/away_score → winner) — fills the round-1 gap
- **live update:** **no** (static; manual re-download)
- **historical data:** **yes** (1872→2026)
- **pricing / trial:** **free** (Kaggle account download)
- **authentication required:** Kaggle account to download (no runtime token)
- **sample payload available:** yes (CSV preview on the dataset page) — full rows need manual download
- **commercial_use_risk:** depends on license — martj42 widely documented **CC0 / Public Domain** *(confirm on the dataset page at download)*
- **scraping / ToS risk:** **low** (official dataset download, not scraping)
- **short_term_fit:** **high** — offline backfill of `final_score`/`actual_winner` → unblocks H2H, recent_form, upset/favorite-fail for the 64 WC2022 matches
- **long_term_fit:** offline validation/calibration dataset; **not** live, no player depth
- **recommended_action:** operator manual-downloads results+goalscorers+shootouts, offline-aligns the 64 WC2022 matches; **do not commit large CSVs**; license check before any customer-UI use. See [KAGGLE_WC2022_CROSS_VALIDATION](KAGGLE_WC2022_CROSS_VALIDATION.md).

### 2. TheSports (thesports.com) — football data API
- **official_url:** https://www.thesports.com/api
- **data_type:** native sports-data REST API (real-time + historical)
- **key_fields_available:** single-match lineups, formations, player positions/stats/ratings, **injuries**, transfers, coach, squad, standings, live text broadcast, season team/player stats, FIFA/club rankings
- **WC2022 coverage:** **unknown** ("Historical Compensation" listed) — confirm via trial
- **WC2026 coverage:** referenced ("World Cup 2026 solution") — confirm via trial
- **player/coach/lineup/injury:** **yes** (all advertised)
- **final_score / actual_winner:** yes
- **live update:** yes
- **historical data:** yes (advertised)
- **pricing / trial:** **15-day free trial**; pricing **not published → sales/contact** *(verify)*
- **authentication required:** yes (API token)
- **sample payload available:** via trial / sales request
- **commercial_use_risk:** **medium** — pricing/contract terms unpublished; provider coverage/reliability unverified
- **scraping / ToS risk:** low (official API)
- **short_term_fit:** trial to **verify deep fields + WC2022/2026 coverage** before committing
- **long_term_fit:** **MVP deep-intelligence candidate** (likely cheaper than Sportradar)
- **recommended_action:** operator applies for the 15-day trial, requests a sample payload, confirms WC2022/2026 + lineup/injury coverage. See [THESPORTS_API_COVERAGE_VALIDATION](THESPORTS_API_COVERAGE_VALIDATION.md).

### 3. SerpApi — Google Sports Results API
- **official_url:** https://serpapi.com/sports-results · pricing https://serpapi.com/pricing
- **data_type:** **Google Search (SERP) scraper** for sports results — **not** a native football DB
- **key_fields_available:** title, thumbnail, league, tournament, stage, status, date, `teams{name,score}`, `game_spotlight`, `games`, `standings` (position/points/GF/GA/last-5), `goal_summary`, `red_cards_summary`, `penalty_score`, `video_highlights`, `team_stats` (W/L)
- **WC2022 coverage:** likely (Google indexes WC2022 results) — **unknown until probed**
- **WC2026 coverage:** likely for fixtures/scores once Google surfaces them — **unknown**
- **player/coach/lineup/injury:** **no lineups/injuries/coach documented** → no/unknown
- **final_score / actual_winner:** **yes** (score + goal_summary) — good for **cross-validation**
- **live update:** partial (`in_game_time`, live scores via Google)
- **historical data:** whatever Google still surfaces — recent > deep historical (**unknown**)
- **pricing / trial:** Free 250/mo · Starter $25/1k · Developer $75/5k · Production $150/15k · Big Data $275/30k · Enterprise custom. **No free trial** (Free tier is the entry). *(official pricing page, 2026-06-10)*
- **authentication required:** yes (API key)
- **sample payload available:** yes (JSON examples in docs); live probe needs a key (operator)
- **commercial_use_risk:** **medium** — data is scraped from Google; SerpApi advertises a "US Legal Shield" but downstream reuse of Google-sourced content carries provenance risk
- **scraping / ToS risk:** **medium** (SerpApi handles the scrape on their side; provenance is Google SERP)
- **short_term_fit:** **auxiliary** cross-check of `final_score`/`actual_winner` + standings
- **long_term_fit:** **not a primary source** — auxiliary validation only
- **recommended_action:** if Owner approves, Free/Starter, probe **only the 4 WC2022 matches**, output field coverage, **no UI**. See [SERPAPI_SPORTS_RESULTS_EVALUATION](SERPAPI_SPORTS_RESULTS_EVALUATION.md).

### 4. API-FOOTBALL (api-football.com / api-sports.io)
- **official_url:** https://www.api-football.com/ · pricing https://www.api-football.com/pricing
- **data_type:** native football REST API (already this project's connector, currently `mock_mode`)
- **key_fields_available:** fixtures, results, livescore, standings, events, **lineups, players, injuries**, odds, predictions, statistics, coachs, transfers, venues (1,200+ leagues)
- **WC2022 coverage:** **yes** (league 1, season 2022) — paid plans unlock historical seasons (free = limited seasons) *(verify our plan's season access)*
- **WC2026 coverage:** **yes** when fixtures are published — note round-1 gate returned **0 fixtures for 2026** (not yet published by provider)
- **player/coach/lineup/injury:** **yes** (paid)
- **final_score / actual_winner:** yes
- **live update:** yes (~15s)
- **historical data:** yes
- **pricing / trial:** **Free 100 req/day** (limited seasons) · Pro **$19/mo** 7,500/day · Ultra **$29/mo** 75,000/day · Mega **$39/mo** 150,000/day *(per official/search; verify)*
- **authentication required:** yes (API key; direct or via RapidAPI)
- **sample payload available:** yes (full public docs)
- **commercial_use_risk:** **low** (licensed commercial API)
- **scraping / ToS risk:** **low** (official API)
- **short_term_fit:** **primary** for fixtures/results; paid unlock for players/lineups/injuries
- **long_term_fit:** **strong MVP-grade primary source**
- **recommended_action:** operator obtains a paid plan + sets `$API_FOOTBALL_KEY`/`$ADMIN_API_TOKEN` on Render; verify WC2022 historical-season access + WC2026 fixture availability. **API/DB wiring is Owner-gated.**

### 5. Sportradar — enterprise soccer data
- **official_url:** https://developer.sportradar.com/soccer/reference/soccer-api-overview
- **data_type:** enterprise native sports data (on-venue scouts)
- **key_fields_available:** full — lineups, formations, player/team profiles, win probabilities, live timelines, standings, summaries (650–900+ competitions)
- **WC2022 / WC2026 coverage:** **yes** (FIFA World Cup covered)
- **player/coach/lineup/injury:** **yes** (deep; lineups ~1h pre-kickoff)
- **final_score / actual_winner:** yes
- **live update:** yes (on-venue)
- **historical data:** yes
- **pricing / trial:** **enterprise / B2B, not published → signed commercial agreement**; **30-day developer trial**; 3rd-party reference ≈ **$500–$1,000+/mo** *(verify via sales)*
- **authentication required:** yes
- **sample payload available:** via trial / docs
- **commercial_use_risk:** low data risk, but **contract + long sales cycle**
- **scraping / ToS risk:** low (licensed)
- **short_term_fit:** **no** (procurement cycle too long for MVP)
- **long_term_fit:** **enterprise future** (formal commercialization)
- **recommended_action:** **defer**; revisit when commercializing at scale.

### 6. Optional candidates (discovered)
- **Highlightly** (https://highlightly.net/football-api/) — **Basic free 100 req/day** incl. live scores, standings, **lineups (formations/starters/bench), player data + season stats + transfers + injuries**; paid **from $5.99/mo**; 950+ leagues. **Strong low-cost secondary** for lineups/injuries — worth a trial alongside API-FOOTBALL. WC coverage *(verify)*.
- **TheSportsDB** (https://www.thesportsdb.com) — free tier (30 req/min; lineups limited to 5 req free / 100 premium) + Patreon premium; rosters/players/events/historical; **crowd-sourced → reliability caution**. Role: **reference-only / metadata/logos**.

---

## 2. Cost Assessment

| Source | Entry | Paid tiers (monthly) | Trial | Notes |
|---|---|---|---|---|
| **Kaggle** | free | — | — | manual download, offline only; license CC0 *(confirm)* |
| **API-FOOTBALL** | Free 100 req/day | Pro $19 · Ultra $29 · Mega $39 (up to 1.5M/day higher) | — (free tier) | current plan/coverage must be checked *(verify)* |
| **SerpApi** | Free 250/mo | Starter $25/1k · Developer $75/5k · Production $150/15k · Big Data $275/30k | no trial | per-search billing; auxiliary only |
| **TheSports** | — | sales/contact (unpublished) | **15-day free** | request quote + sample |
| **Sportradar** | — | enterprise, ≈$500–1,000+/mo *(ref)* | **30-day dev** | signed agreement; long cycle |
| **Highlightly** *(bonus)* | Free 100/day | from $5.99/mo | — | cheap lineup/injury alt |

All figures **checked 2026-06-10 via public pages**; **operator must re-verify before purchase** (pricing changes).

---

## 3. Final recommendation — 3 routes

**Route A — Low-cost historical validation (recommended FIRST):**
Kaggle + current Render API. Use Kaggle to backfill `final_score`/`actual_winner` → unblock H2H, `recent_form_5`,
upset/favorite-fail for the 64 WC2022 matches (offline cross-validation against our predictions).
**Cost: low (free).** Cons: no live, no player depth. *(Offline/docs only; any UI use needs license + Owner sign-off.)*

**Route B — MVP deep intelligence:**
API-FOOTBALL **paid** (primary) — or a **TheSports 15-day trial** / **Highlightly** as cheaper alternatives — for
lineup / player / coach / injury / live stats on **real WC2026**. **Cost: medium ($19–$39/mo API-FOOTBALL; TheSports
via sales).** Cons: needs token, coverage verification, payment. **Code/API/DB wiring is Owner-gated.**

**Route C — Enterprise data:**
Sportradar for formal commercial deep data. **Cost: high (~$500–1,000+/mo).** Cons: long sales cycle. **Defer.**

**SerpApi role:** **auxiliary cross-check / Google-Sports display validation only — NOT a primary data source.**

**ClaudeT suggestion (for Owner decision):** start **Route A** now (free, closes the exact round-1 gap), evaluate
**Route B** for real WC2026 (API-FOOTBALL paid as primary, Highlightly/TheSports trials as comparison), keep
**SerpApi** as an optional auxiliary cross-check, and **defer Route C**.

---

## 4. Guardrails honored
docs-only · no frontend/backend/API/DB change · no source called with a token · no fabricated pricing/fields
(*(verify)* flags where unconfirmed) · `42.2%` stays internal · PR #2 Draft.

## Sources (checked 2026-06-10)
SerpApi [pricing](https://serpapi.com/pricing) · [sports-results](https://serpapi.com/sports-results) ·
API-FOOTBALL [pricing](https://www.api-football.com/pricing) · Kaggle [martj42 dataset](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) ·
TheSports [api](https://www.thesports.com/api) · Sportradar [soccer overview](https://developer.sportradar.com/soccer/reference/soccer-api-overview) ·
Highlightly [football-api](https://highlightly.net/football-api/) · TheSportsDB [pricing](https://www.thesportsdb.com/pricing)
