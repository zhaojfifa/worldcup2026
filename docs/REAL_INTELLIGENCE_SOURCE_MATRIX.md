# Real Intelligence — Source Matrix

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Mode:** docs-only. Public docs/pricing, checked 2026-06-10; no source called with a token. *(verify)* = operator
> must re-confirm. Detail: [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md).

**Legend:** `Y`=yes · `N`=no · `P`=partial · `?`=unknown/verify · `paid`=paid tier · `off`=offline · `derive`=computable.
**Recommended-role enum:** `primary` · `secondary` · `offline validation` · `reference-only` · `excluded` · `enterprise future`.

---

## Table 1 — data-field coverage

| Source | Fixture/result | Final score | Actual winner | Player list | Coach | Lineup | Injury | Recent form | H2H | Elo/ranking | Squad value | Media/news | Odds/market † |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Render API** (current) | P (no scoreline) | N (settled only) | N | N | N | N | N | N | N | N | N | N | N |
| **API-FOOTBALL** | Y | Y | Y | paid | paid | paid | paid | Y/derive | Y | rank P | N | N | paid |
| **TheSports** | Y | Y | Y | Y | Y | Y | Y | Y | ? | rank Y | ? | N | Y |
| **Sportradar** | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | ? | N | sep. product |
| **SerpApi** | Y | Y | Y | P | N | N | N | P (last-5) | N | rank P | N | P (highlights) | N |
| **Kaggle** | Y (off) | Y | Y | N (scorers only) | N | N | N | Y (off, full history) | Y (off) | Elo derive | N | N | N |
| **Highlightly** | Y | Y | Y | Y | ? | Y | Y | ? | ? | ? | N | Y (highlights) | Y |
| **TheSportsDB** | Y | Y | Y | Y (roster) | P | P (limited) | N | N | N | N | Y (logos/meta) | N |

## Table 2 — operational profile

| Source | Live update | Historical coverage | 2026 coverage | Cost level | License risk | Recommended role |
|---|---|---|---|---|---|---|
| **Render API** (current) | demo only | Y (WC2022, 64) | N (0 fixtures) | free (own) | low | primary (baseline only) |
| **API-FOOTBALL** | Y (~15s) | Y | Y (when published) | low–med ($19–$39/mo) | low | **primary** |
| **TheSports** | Y | ? *(verify)* | ? *(verify)* | med (sales quote) | med | **secondary** (deep; trial first) |
| **Sportradar** | Y (on-venue) | Y | Y | high (~$500–1,000+/mo) | low (contract) | **enterprise future** |
| **SerpApi** | P | ? (Google) | ? (Google) | low ($25/1k) | med (scraped) | **offline validation** (auxiliary) |
| **Kaggle** | N | Y (1872→2026) | P (as played) | free | low (CC0 *confirm*) | **offline validation — alignment pending** (Render side ready; `manual_download_needed`) |
| **Highlightly** | Y | ? *(verify)* | ? *(verify)* | low (free / from $5.99/mo) | low | **secondary** (cheap; verify) |
| **TheSportsDB** | P | Y | ? *(verify)* | free / Patreon | med (crowd-sourced) | **reference-only** |

† **Odds/market is compliance-EXCLUDED for our product (no betting), regardless of source availability.**

---

## How the matrix maps to the 3 routes
- **Route A (low-cost historical validation):** **Kaggle** (offline `final_score`/`winner`/form/H2H) + **Render API** +
  optional **SerpApi** auxiliary cross-check. Cost: free–$25. **Status (2026-06-10): alignment harness shipped
  (`scripts/audit_kaggle_wc2022.py`); Render side ready; `manual_download_needed` — operator places the 3 CSVs to complete.**
- **Route B (MVP deep intelligence):** **API-FOOTBALL** paid `primary`, with **Highlightly** / **TheSports** trials as
  `secondary` comparisons (lineup/player/coach/injury, live). Cost: ~$19–$39/mo + trials.
- **Route C (enterprise):** **Sportradar** `enterprise future`. Cost: high. Defer.

**Primary gap-closers:** Kaggle (Route A — the cheapest fix for the round-1 result gap) and API-FOOTBALL paid
(Route B — the cheapest path to deep intelligence for real WC2026). SerpApi stays auxiliary; Sportradar deferred.

## Guardrails
docs-only · no code/API/DB · no token calls · odds excluded · pricing/coverage *(verify)* before purchase · PR #2 Draft.
