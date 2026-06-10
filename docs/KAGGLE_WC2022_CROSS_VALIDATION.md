# Kaggle — WC2022 Cross-Validation Evaluation

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Mode:** docs-only. **No dataset downloaded** (manual-download-needed). Public dataset metadata, checked 2026-06-10.
> Parent: [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md).

---

## 1. Candidate dataset
- **Primary:** martj42 — "International football results from 1872 to 2026"
  (https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017), ~49k men's full
  internationals, actively maintained (GitHub PRs).
- **Files:** `results.csv` (`date, home_team, away_team, home_score, away_score, tournament, city, country, neutral`),
  `goalscorers.csv` (scorers + minute + own-goal/penalty), `shootouts.csv` (penalty-shootout winners).
- **Backups if needed:** dedicated WC2022 datasets (e.g. `die9origephit/fifa-world-cup-2022-complete-dataset`,
  `swaptr/fifa-world-cup-2022-match-data`) for richer per-match stats.

## 2. Can it backfill `final_score` / `actual_winner` offline? — **YES**
`home_score`/`away_score` give the real scoreline → `actual_winner` derivable. This is **exactly** the field our
Render API does not expose per match (round-1 `unknown`). It is **offline** (static CSV), not live.

## 3. Can it align to our 64 WC2022 matches? — **YES (with name normalization)**
Join key = **kickoff date + team names**, filtered to `tournament == "FIFA World Cup"`, season 2022 (Nov–Dec).
Caveat: our DB mixes Chinese (`阿根廷`) and English (`Saudi Arabia`) team names; Kaggle uses English
(`Argentina`, `Saudi Arabia`). A **zh→en team-name map** is required to align (the frontend `viMapping` already
has many of these). 64 matches is a small, tractable join.

## 4. Derived capabilities it unblocks (offline)
| capability | with Kaggle |
|---|---|
| `final_score` / `actual_winner` | **yes** (results.csv) |
| `upset_cases` / `favorite_failed_cases` | **yes** — compare our predicted favorite vs real winner (was blocked in round 1) |
| `recent_form_5` | **yes — real**, using the **full 1872→2026 history** (not limited to the 64-match tournament) |
| `head_to_head_summary` | **yes — real**, full international history per pair |
| `elo_delta` | **derivable** (compute Elo offline from the full result history) |
| goalscorers | yes (goalscorers.csv) — but **not** lineups/positions/injuries |

So Kaggle alone turns round-1's "blocked" derivations (upset/favorite/form/H2H) into **offline-computable** ones.

## 5. Can it enter customer UI?
**Not directly / not yet.** Conditions: (a) **license permits** — martj42 is widely documented **CC0 / Public
Domain** *(operator confirm on the dataset page at download)*; (b) **Owner sign-off** for any customer-facing use;
(c) it stays a **backfill/validation** layer, not a live feed. Default: **offline / internal calibration first.**

## 6. What it does NOT provide
Players' lineups, formations, positions, ratings, injuries, suspensions, coach, squad, live updates, odds. → Kaggle
is **Route A (low-cost historical validation)**, not deep intelligence.

## 7. Operator actions (Owner-gated)
1. **manual-download-needed** — operator downloads `results.csv` + `goalscorers.csv` + `shootouts.csv` (Kaggle login).
2. Confirm the **license** (CC0) on the dataset page.
3. Offline-align the 64 WC2022 matches (date + normalized team names) → produce a `final_score`/`actual_winner`
   table for internal cross-validation vs our predictions.
4. **Do NOT commit large CSVs** to the repo (data stays local/operator-side; only a small derived summary, if any,
   after Owner approval).
5. Any customer-UI use → separate Owner decision.

## Sources
[martj42 dataset](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) ·
[WC2022 complete dataset](https://www.kaggle.com/datasets/die9origephit/fifa-world-cup-2022-complete-dataset)
