# Kaggle — WC2022 Cross-Validation Evaluation

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Mode:** docs-only. **No dataset downloaded** (manual-download-needed). Public dataset metadata, checked 2026-06-10.
> Parent: [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md).

---

## 0. Alignment run status (2026-06-10) — `manual_download_needed`

Ran `python scripts/audit_kaggle_wc2022.py` →
[`docs/data_audit/kaggle_wc2022_cross_validation.json`](data_audit/kaggle_wc2022_cross_validation.json).

| item | value |
|---|---|
| dataset | martj42 "International football results from 1872 to 2026" |
| dataset_url | https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017 |
| **license_status** | **CC0 / Public Domain (per dataset page) — UNCONFIRMED at download; not for customer UI until confirmed** |
| **downloaded?** | **NO → `manual_download_needed`** |
| expected file paths | `data/external/kaggle/{results,goalscorers,shootouts}.csv` (gitignored) |
| Kaggle WC2022 rows | **pending download** |
| Render WC2022 matches | **64** (fetched live) |
| match alignment | **pending CSV** — Render side prepared (64 matches, 32 teams, normalizer ready) |
| final_score / actual_winner | **pending** (backfilled from results.csv once present) |

**Render side is ready.** The script fetched the 64 finished matches and normalized team names
(zh→en: 阿根廷→Argentina · 法国→France · 摩洛哥→Morocco · 巴西→Brazil · 西班牙→Spain · 德国→Germany;
en: USA→United States; verify Iran / South Korea spelling at download). As soon as the operator places the three
CSVs at the expected paths and re-runs the script, it computes `matched_count`, `final_score`, `actual_winner`
and `upset` / `favorite_failed` cases — **offline, no UI, no fabrication**.

- **Fields Kaggle CAN provide:** `final_score`, `actual_winner` (results.csv + shootouts.csv for KO penalties),
  goalscorers, and — via the full 1872→2026 history — real `recent_form_5`, `head_to_head`, Elo derivation.
- **Fields Kaggle CANNOT provide:** lineups, formations, positions/ratings, injuries, suspensions, coach, squad,
  live, odds.
- **Internal use:** once aligned, `final_score`/`actual_winner` are usable for **internal** cross-validation +
  upset/favorite-fail selection. **Customer-UI use requires license (CC0) confirmation + Owner sign-off.**
- **Recommended next step:** operator downloads the 3 CSVs (Kaggle login) → places them at the expected paths →
  re-runs `python scripts/audit_kaggle_wc2022.py` → review the regenerated JSON.

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
