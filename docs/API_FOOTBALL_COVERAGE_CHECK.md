# API-FOOTBALL — Level-2 Coverage Check (Day-2)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only execution.
> Runner: `scripts/verify_api_football_level2.py` → [`docs/data_audit/api_football_level2_coverage.json`](data_audit/api_football_level2_coverage.json).
> **Token never printed/committed** (read internally from gitignored `backend/.env`). **No third-party payload committed. No fabrication.**

---

## Verdict — `PASS` (Level-2 core verified on WC2022) · plan caveats apply

> **Owner decision (2026-06-10):** API-FOOTBALL **confirmed MVP-2 primary-source candidate**; Level-2 feasibility
> **PASS**. State = *Internal Level-2 feasibility proven · Commercial MVP-2 not ready.* Next: **paid plan = GO
> (recommended)** → re-verify WC2026/injuries/rate-limit, then design backend schema (see
> `MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE.md` / `API_FOOTBALL_PAID_PLAN_DECISION.md`). Operation stays paused.

API-FOOTBALL **does** serve the Level-2 pre-match scout core for World Cup 2022: **lineups (+ formation), match
events, match statistics, per-match player stats, squad, coach, teams** all returned real data, and **all four test
matches mapped to API-FOOTBALL fixture ids.** → API-FOOTBALL is a **viable MVP-2 primary source.**
**Caveat:** the configured key is the **FREE plan** — **WC2026 season is locked** and **rate limits are tight**
(per-minute 429s, needed a 65s backoff to resolve coach/teams). A **paid plan is required to operate for WC2026.**

---

## Run status
| item | value |
|---|---|
| run | `python3 scripts/verify_api_football_level2.py` (2026-06-10), 429-backoff |
| token | **present** — read from gitignored `backend/.env` (var `API_FOOTBALL_KEY`); **never printed/committed** |
| plan | **FREE** (revealed by the WC2026 error: "Free plans do not have access to this season, try from 2022 to 2024") |
| base_url | `https://v3.football.api-sports.io` |
| /status | HTTP 200 — **account reachable** (verifier's `results>0` heuristic flags it false; not a real failure) |

## Per-field result (Task C 1–15)
| # | field | result |
|---|---|---|
| 1 | World Cup league id / season | ✅ **league_id = 1** (`/leagues?id=1` → 1 result) |
| 2 | WC2022 fixtures queryable | ✅ **64 fixtures** (`/fixtures?league=1&season=2022`) |
| 3 | match 8 Argentina vs Saudi Arabia → fixture_id | ✅ **855737** (= Render `external_id` AF-855737 ✓) |
| 4 | match 13 Germany vs Japan → fixture_id | ✅ **855741** |
| 5 | match 58 Morocco vs Spain → fixture_id | ✅ **977345** |
| 6 | match 67 Argentina vs France → fixture_id | ✅ **979139** |
| 7 | fixtures/lineups has data | ✅ (2 teams) |
| 8 | fixtures/events has data | ✅ (20 events) |
| 9 | fixtures/statistics has data | ✅ (2 teams) |
| 10 | fixtures/players has data | ✅ (2 teams) |
| 11 | injuries has data | ⚠️ **0 results** (HTTP 200, no error — empty for WC2022 historical; re-verify on a current/live fixture or paid plan) |
| 12 | team players / squad has data | ✅ (`/players/squads` → 1 squad) |
| 13 | coachs has data | ✅ (resolved after 429 backoff) |
| 14 | formation readable from lineups | ✅ **true** (lineups `formation` field present) |
| 15 | WC2026 fixtures has data | ❌ **0 — plan-locked** ("Free plans … try from 2022 to 2024"); also may be unpublished |

**Coverage summary:** leagues ✓ · fixtures2022 ✓ · lineups ✓ · events ✓ · statistics ✓ · players ✓ · squad ✓ ·
coachs ✓ · teams ✓ · formation ✓ · **injuries empty · fixtures2026 plan-locked**.

## Blocking issues (now plan/coverage, not token)
1. **Plan tier = FREE** → **WC2026 season locked** (only 2022–2024). Operating for WC2026 **requires a paid plan**.
2. **Rate limit** (free ≈ 10/min) → 429s; verifier now backs off 65s and retries. Production needs a paid plan's
   higher limits + a Redis-cached backend proxy (blueprint §5).
3. **injuries empty** for the WC2022 historical query — unconfirmed; re-verify on a current fixture / paid plan.

## Recommended next path (PASS branch)
1. **Adopt API-FOOTBALL as the MVP-2 primary data source** — Level-2 core (lineup/formation/events/stats/players/
   squad/coach) is verified available, with fixture ids mapped to our matches.
2. **Upgrade to a paid plan (Pro $19+/mo)** to unlock the **WC2026 season**, raise rate limits, and re-verify
   **injuries** + WC2026 fixtures. **Owner action needed.**
3. **Design the backend schema + feature store** (blueprint §3 entity-resolution + §5 architecture) — Owner-gated;
   frontend never calls the vendor (backend proxy + Redis + CDN).
4. Keep **TheSports** as the **live / Level-3** candidate (trial pending); odds remain excluded.
5. **External operation stays paused** until the paid-plan re-verify + a minimal Level-2 surface ship.

## Guardrails honored
docs-only · no frontend/backend/API/DB change · token read from gitignored `backend/.env`, never printed/committed ·
no third-party payload committed · odds excluded · `42.2%` internal · PR #2 stays Draft.
