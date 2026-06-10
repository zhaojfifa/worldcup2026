# Goal-Driven Data Source Strategy

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only.
> Parent: [GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN](GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN.md) ·
> field detail: [FOOTBALL_INTELLIGENCE_DATA_REQUIREMENTS_MATRIX](FOOTBALL_INTELLIGENCE_DATA_REQUIREMENTS_MATRIX.md).
> Organized **by goal, not by website.** Pricing/coverage flagged *(verify)* — operator confirms before purchase.
> Reference sites are **not scraped**; odds **excluded**; any API/paid/DB/backend work is **Owner-gated**.

---

## Update (2026-06-10) — Data Integration Blueprint
Owner adopted the designer's integrated data-source plan → `FOOTBALL_INTELLIGENCE_DATA_INTEGRATION_BLUEPRINT.md`.
**Priority: API-FOOTBALL first** (Level-2 verifier `scripts/verify_api_football_level2.py`, token-gated), TheSports
pending (**no longer blocks Level-2**), Sportmonks/Highlightly alternatives. Direction = Data Source → Feature
Engineering → Model Explanation → UI; **no data, no AI deep analysis**; betting framing downgraded, odds excluded.

## Goal 1 — Historical recap credible  (→ Level 1)
- **Data needs:** `final_score` · `actual_winner` · H2H · recent_form · model baseline.
- **Candidates:** **Kaggle** (martj42, CC0 *confirm*) · **current Render API** (baseline, fixtures).
- **Conclusion:**
  - **Can do MVP-1.** `final_score`/`actual_winner` already aligned 64/64 offline ([kaggle_wc2022_cross_validation.json](data_audit/kaggle_wc2022_cross_validation.json)); matches 8 & 13 shipped.
  - **Still to add:** H2H + recent_form (both **derivable offline** from Kaggle's full 1872→2026 history — no new source).
  - **Blocker:** Kaggle **CC0 license unconfirmed** for customer UI (operator must confirm). Until then: internal/recap only.
  - **Cost:** ~free.

## Goal 2 — Pre-match analysis credible  (→ Level 2)
- **Data needs:** starting/predicted lineup · coach · formation · injuries · suspensions · key_player_availability · tactical_style.
- **Candidates:** **TheSports** · **API-FOOTBALL** (paid) · **Sportmonks** · **Sportradar**.
- **Conclusion:**
  - **Must trial/buy to validate** — none verified yet for WC coverage + lineup/injury depth.
  - **Cheapest paths:** TheSports **15-day trial** (sales pricing) · API-FOOTBALL **Pro $19–Mega $39/mo** · Sportmonks **Starter €29–Pro €249/mo** (14-day trial, WC needs a paid league plan) · Highlightly **free 100/day** (cheap lineup/injury alt). Sportradar = enterprise (defer).
  - **Without this data, pre-match analysis has no operational value.** This is the make-or-break layer.
  - **Action:** run the [TheSports 19-point trial checklist](GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN.md#thesports-15-day-trial--verification-checklist) and an API-FOOTBALL paid coverage check in parallel.

## Goal 3 — Tactical quantification credible  (→ Level 2-3, advanced)
- **Data needs:** xG · xGA · shot_quality · progressive_passes · pressures · passing_network.
- **Candidates:** **FBref / Understat** (reference) · **StatsBomb** / **Opta** / **Sportradar** (licensed route).
- **Conclusion:**
  - **MVP can validate via a manual sample or a licensed source.** **Do not mass-scrape.**
  - **High-value free path:** **StatsBomb Open Data** already publishes **WC2022 events + xG + 360 freeze-frames** (JSON, GitHub) under a **research / non-commercial** license (attribution required). → Excellent for **offline xG calibration** of the WC2022 recaps (like Kaggle for results), but **NOT for commercial customer UI** without a Hudl/StatsBomb commercial license.
  - **Action:** offline-calibrate the model's `advanced_stats` slot against StatsBomb WC2022 (non-commercial, internal); for commercial use, price Opta/Sportradar/StatsBomb licensed.
  - **Cost:** free (offline calibration) → high (licensed commercial).

## Goal 4 — Live intelligence credible  (→ Level 3)
- **Data needs:** live_event · lineup confirmation · substitutions · live_stats · attack_momentum · player_rating.
- **Candidates:** **TheSports** · **API-FOOTBALL** (live) · **Sportradar** · **SofaScore commercial** (if available).
- **Conclusion:**
  - **Requires a paid real-time API.** **No real-time data → no live-correction push** (the current LINEUP WATCH is a demo and must stay hidden on recaps).
  - **Cost:** medium–high (live tiers cost more than historical).
  - **Sequence:** only after Level 2 is validated and operating.

## Goal 5 — Operational content credible
- **Data needs:** the structured data from Goals 1–4 **+ AI summary**.
- **Candidates:** **internal AI** (DeepSeek/Gemini draft-only, existing).
- **Conclusion:**
  - **AI is the explanation layer, not the data layer.** It reads the structured fields and writes a scout summary;
    it must show `missing` for any absent dimension and must not fabricate.
  - **Cost:** ~free (existing draft-only LLM); gated by forbidden-word filter; no auto-publish.

---

## Recommended sequencing (for Owner)
1. **Now (free):** finish **MVP-1** — derive H2H + recent_form from Kaggle (offline), keep recaps internal until CC0
   confirmed. Calibrate xG offline against **StatsBomb WC2022** (non-commercial).
2. **Next (trial, Owner-gated):** validate **Level 2** via **TheSports trial** + **API-FOOTBALL paid coverage check**
   (+ optionally Sportmonks/Highlightly) using the 19-point checklist on matches 8 & 13.
3. **Later (paid):** **Level 3** live via the chosen Level-2 vendor's live tier or Sportradar.
4. **Throughout:** **odds excluded**; reference sites never scraped; AI summary only over real data; `42.2%` internal.

## Cost snapshot (verify before purchase)
| goal | cheapest viable | monthly |
|---|---|---|
| 1 Historical | Kaggle + Render | free |
| 2 Pre-match | API-FOOTBALL Pro / TheSports trial / Highlightly free | $0–$39 |
| 3 Tactical (offline) | StatsBomb WC2022 (non-commercial) | free |
| 3 Tactical (commercial) | Opta / Sportradar / StatsBomb licensed | high |
| 4 Live | API-FOOTBALL/TS live or Sportradar | med–high |
| 5 Content | internal LLM (draft-only) | ~free |

## Sources (checked 2026-06-10)
Sportmonks [pricing](https://www.sportmonks.com/football-api/plans-pricing/) · StatsBomb [open-data](https://github.com/statsbomb/open-data) ·
prior-sprint sources in [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md).
