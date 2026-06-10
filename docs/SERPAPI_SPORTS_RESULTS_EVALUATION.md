# SerpApi — Google Sports Results API Evaluation

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Mode:** docs-only. **SerpApi was NOT called** (no key). Fields/pricing from public docs (checked 2026-06-10).
> Parent: [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md).

---

## 1. What it is (and is not)
SerpApi's Google Sports Results API is a **Google Search (SERP) scraper** — it parses the sports box that Google
renders for a query and returns it as JSON. It is **not** a native football database; it has **no schema
guarantees** beyond what Google chooses to display, and coverage varies by query/region/time.

## 2. Available fields (per official docs)
- **Match/result:** `title`, `thumbnail`, `league`, `tournament`, `stage`, `status`, `date`,
  `teams{name, score, kgmid, thumbnail}`, `game_spotlight`, `games`, `penalty_score`, `in_game_time` (live)
- **Soccer extras:** `goal_summary`, `red_cards_summary`, `video_highlights`/`video_highlight_carousel`
- **Standings:** `standings`/`tables` (division, position, points, GF/GA, **last-5**), `team_stats` (W/L)
- **Athlete:** some `tables` for athlete stats (matches, goals, assists, cards)

## 3. Can it get standings / players / league stats?
- **Standings:** **yes** (Google standings box).
- **League/athlete stats:** **partial** — only what Google surfaces (top scorers, basic player lines), not a full DB.
- **Starting XI / formations / injuries / coach / squad:** **no** (not part of the Google sports box) → **no/unknown**.

## 4. WC-specific reliability (hypotheses — must be probed)
- **WC2022 single match:** *likely* retrievable (Google still indexes 2022 results) — **unknown until tested**.
- **WC2026 fixture:** *likely* once Google shows the fixture — **unknown**; not a guaranteed structured feed.
- **Stability:** SERP scraping is inherently **less stable** than a native API (layout/locale changes).

## 5. Capability verdict vs. our gap
| need | SerpApi |
|---|---|
| per-match `final_score` / `actual_winner` | **yes** (`teams.score`, `goal_summary`) → **cross-validation use** |
| standings / last-5 | yes |
| starting XI / formation | **no** |
| injuries / suspensions | **no** |
| coach / squad | **no** |
| primary deep-intelligence source | **no** |
| auxiliary verification source | **yes** |

## 6. Pricing (official page, 2026-06-10 — verify before purchase)
| Plan | Price/mo | Searches/mo | Throughput |
|---|---|---|---|
| Free | $0 | 250 | 50/hr |
| **Starter** | **$25** | **1,000** | 200/hr |
| **Developer** | **$75** | **5,000** | 1,000/hr |
| **Production** | **$150** | **15,000** | 3,000/hr |
| Big Data | $275 | 30,000 | 6,000/hr |
| Enterprise | custom | custom | custom |

Month-to-month, cancel anytime. **No free trial** (Free tier is the entry). Only successful searches are billed.

## 7. Recommended trial plan (Owner-gated — do NOT buy a large tier)
1. **Do not** buy Production/Big Data. Start on **Free (250/mo)** or **Starter ($25)**.
2. Probe **only these 4 WC2022 matches** (cross-check vs our predictions; aligns with recap candidates):
   - Argentina vs Saudi Arabia (2022)
   - Germany vs Japan (2022)
   - Morocco vs Spain (2022)
   - Argentina vs France (2022)
3. Output a **fields-coverage** table (which of `score`/`goal_summary`/`standings`/players actually returned).
4. **No UI wiring.** Result feeds the cross-validation note only.
5. Operator runs it (needs `$SERPAPI_KEY`); Claude will not call it without a key + Owner approval.

## 8. Role
**Auxiliary cross-check / Google-Sports display validation. NOT a primary data source.** Best used to
**independently confirm `final_score`/`actual_winner`** that our Render API does not expose — a second opinion
alongside the free **Kaggle** offline result data (Route A).

## Sources
[serpapi.com/sports-results](https://serpapi.com/sports-results) · [serpapi.com/pricing](https://serpapi.com/pricing)
