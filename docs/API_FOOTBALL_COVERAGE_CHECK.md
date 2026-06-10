# API-FOOTBALL — Level-2 Coverage Check (Real Run)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only execution.
> Runner: `scripts/verify_api_football_level2.py` → [`docs/data_audit/api_football_level2_coverage.json`](data_audit/api_football_level2_coverage.json).
> **Token read internally from gitignored `backend/.env`; never printed/committed.** No third-party payload committed. No fabrication.
> **Supersedes the earlier FREE-plan / WC2026-locked caveat** — the latest operator run returns WC2026 fixtures.

---

## Verdict — `PASS` (API-FOOTBALL Real Run)

> **Owner decision (2026-06-10):** API-FOOTBALL **confirmed MVP-2 primary-source candidate**; Level-2 feasibility
> **PASS**. State = *Internal Level-2 feasibility proven · Commercial MVP-2 not ready.* **MVP-2 implementation
> planning can start** (design/prototype only — see `MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE.md` /
> `MVP2_IMPLEMENTATION_PLAN.md`). External operation stays paused.

API-FOOTBALL serves the Level-2 pre-match scout core for World Cup 2022 **and returns WC2026 fixtures**: lineups
(+formation), events, statistics, fixture players, squad, coach, teams all return real data; all four test matches
map to API-FOOTBALL fixture ids (incl. **8 → 855737 = our Render `external_id` AF-855737**). **One open gap:
`injuries` returned 0 (empty) and is unresolved.**

## Run status
| item | value |
|---|---|
| run | `python3 scripts/verify_api_football_level2.py` (operator, 2026-06-10) → `status=probed`, `verdict=pass` |
| token | **present** — gitignored `backend/.env` (`API_FOOTBALL_KEY`); **never printed/committed** |
| base_url | `https://v3.football.api-sports.io` |
| WC2026 access | ✅ **returned (72)** — the earlier FREE-plan WC2026 lock no longer applies (plan tier not explicitly captured this run) |

## Per-field result (Task C 1–15)
| # | field | result |
|---|---|---|
| 1 | World Cup league id / season | ✅ **league_id = 1** |
| 2 | WC2022 fixtures queryable | ✅ **64** |
| 3 | match 8 Argentina vs Saudi Arabia → fixture_id | ✅ **855737** (= Render AF-855737 ✓) |
| 4 | match 13 Germany vs Japan → fixture_id | ✅ **855741** |
| 5 | match 58 Morocco vs Spain → fixture_id | ✅ **977345** |
| 6 | match 67 Argentina vs France → fixture_id | ✅ **979139** |
| 7 | fixtures/lineups has data | ✅ (2 teams) |
| 8 | fixtures/events has data | ✅ (20 events) |
| 9 | fixtures/statistics has data | ✅ (2 teams) |
| 10 | fixtures/players has data | ✅ (2 teams) |
| 11 | injuries has data | ❌ **0 results (HTTP 200, no error) — UNRESOLVED gap** (see below) |
| 12 | team players / squad has data | ✅ (1 squad) |
| 13 | coachs has data | ✅ (1) |
| 14 | formation readable from lineups | ✅ **true** |
| 15 | WC2026 fixtures has data | ✅ **72** (no longer locked) |

**Coverage:** leagues ✓ · fixtures2022 (64) ✓ · **fixtures2026 (72) ✓** · lineups ✓ · events ✓ · statistics ✓ ·
players ✓ · squad ✓ · coachs ✓ · teams (32) ✓ · formation ✓ · **injuries ✗ (0)**.

## Open gap — injuries unresolved
`/injuries?league=1&season=2022` returns **HTTP 200 with 0 results** (no error). Interpretation is **unresolved**:
historical WC2022 injuries may simply not be populated, or the query needs a fixture-level/current-season form.
→ **Requires a second-source or current-season verification** before any "key absence" feature ships. Until then,
`injuries / suspensions` renders `missing / source required` (no AI-filled impact).

## Remaining production considerations (not coverage blockers)
- **Rate limit / request budget:** a full fixture pack is ~6–8 calls; match-day load across many fixtures must be
  sized against the plan's req/min + req/day (verifier has 429 backoff). Confirm the production budget.
- **Commercial-use terms** of the current plan must be confirmed for a paid product.
- **2026 fixtures update SLA** + (if Level-3) live/event latency to be confirmed.

## Recommended next path (PASS branch)
1. **Adopt API-FOOTBALL as the MVP-2 primary data source** — Level-2 core verified, WC2022 + WC2026 fixtures
   present, fixture ids mapped.
2. **MVP-2 implementation planning starts** (design/prototype): backend schema + ingestion + Evidence Board v2
   (`MVP2_IMPLEMENTATION_PLAN.md`). **Open a separate implementation PR off `main`** (not PR #2).
3. **Resolve injuries** via a current-season check or a second source (TheSports/Sportmonks/Highlightly).
4. **Paid-plan considerations** are now rate-limit/commercial/injuries/stability/SLA — **not** WC2026 access
   (`API_FOOTBALL_PAID_PLAN_DECISION.md`).
5. **External operation stays paused** until a minimal Level-2 surface + license confirmations.

## Guardrails honored
docs-only · no frontend/backend/API/DB change · token read from gitignored `backend/.env`, never printed/committed ·
`worldcup2026-api.env` gitignored, never committed · no third-party payload committed · odds excluded · `42.2%` internal · PR #2 stays Draft.
