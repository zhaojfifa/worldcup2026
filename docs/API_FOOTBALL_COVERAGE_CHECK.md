# API-FOOTBALL — Level-2 Coverage Check (Day-2)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only execution.
> Runner: `scripts/verify_api_football_level2.py` → [`docs/data_audit/api_football_level2_coverage.json`](data_audit/api_football_level2_coverage.json).
> **No token committed. No third-party payload committed. No fabrication.**

---

## Verdict — `BLOCKED_BY_TOKEN`

The Day-2 run could **not** assess real coverage: **no API-FOOTBALL token is present** in this environment under any
accepted variable name, and no local gitignored `.env` holds one. Per the rules, the verifier made **ZERO network
calls** and did not fabricate any result. **This is a token/provisioning block, not a plan or coverage finding.**

---

## Run status

| item | value |
|---|---|
| run | `python3 scripts/verify_api_football_level2.py` (2026-06-10) |
| status | `token_required` · **verdict `blocked_by_token`** |
| token present | **NO** |
| accepted token vars (checked) | `API_FOOTBALL_KEY` · `API_KEY` · `API_TOKEN` · `API_SPORTS_KEY` (all unset) |
| local `.env` checked | `.env`, `backend/.env`, `backend/.env.local` — none contain a key |
| base_url | `https://v3.football.api-sports.io` (default; override via `API_FOOTBALL_BASE_URL`) |
| network calls made | **0** |
| token leaked | **no** (token never printed/committed; never enters the JSON) |

## Tested endpoints (planned; not executed — blocked)
`/status` · `/leagues?id=1` · `/fixtures?league=1&season=2022` · `/fixtures?league=1&season=2026` ·
`/fixtures/lineups` · `/fixtures/events` · `/fixtures/statistics` · `/fixtures/players` ·
`/injuries?league=1&season=2022` · `/players/squads` · `/coachs` · `/teams?league=1&season=2022`.

## Per-field result (Task C 1–15) — all PENDING TOKEN
| # | field | result |
|---|---|---|
| 1 | World Cup league id / season confirmed | ⏳ pending token |
| 2 | WC2022 fixtures queryable | ⏳ pending token |
| 3 | match 8 Argentina vs Saudi Arabia → fixture_id | ⏳ pending token |
| 4 | match 13 Germany vs Japan → fixture_id | ⏳ pending token |
| 5 | match 58 Morocco vs Spain → fixture_id | ⏳ pending token |
| 6 | match 67 Argentina vs France → fixture_id | ⏳ pending token |
| 7 | fixtures/lineups has data | ⏳ pending token |
| 8 | fixtures/events has data | ⏳ pending token |
| 9 | fixtures/statistics has data | ⏳ pending token |
| 10 | fixtures/players has data | ⏳ pending token |
| 11 | injuries has data | ⏳ pending token |
| 12 | team players / squad has data | ⏳ pending token |
| 13 | coachs has data | ⏳ pending token |
| 14 | formation readable from lineups | ⏳ pending token |
| 15 | WC2026 fixtures has data | ⏳ pending token |

The verifier already resolves items 3–6 (test-match fixture ids) and 14 (formation from the lineups `formation`
field) automatically once a token is present.

## Blocking issue
**Token, not plan.** No API-FOOTBALL key is provisioned to this environment, so the run cannot even reach `/status`
to read the plan tier. We therefore **cannot** yet distinguish `blocked_by_plan` (e.g. historical-season lock) from a
real coverage `pass/partial/fail`. The verifier is **ready** — the moment the operator sets any accepted token var
(or adds it to gitignored `backend/.env`) and re-runs, it auto-produces the full verdict + per-match fixture ids.

## Recommended next path
1. **Owner/operator action:** provision a paid-plan API-FOOTBALL key as `API_FOOTBALL_KEY` (or `API_KEY` /
   `API_TOKEN` / `API_SPORTS_KEY`) in this env or `backend/.env`, then re-run the verifier → commit the resulting
   `api_football_level2_coverage.json` + update this doc's verdict.
2. **Then branch on the result** (per blueprint §6/§7):
   - **PASS** → adopt API-FOOTBALL as the MVP-2 primary source; design backend schema + feature store; keep
     TheSports as the live/Level-3 candidate.
   - **PARTIAL** → keep API-FOOTBALL as the base source; in parallel validate Sportmonks / TheSports / Highlightly to
     fill lineup/injury/coach gaps.
   - **FAIL / blocked_by_plan (historical lock)** → switch Level-2 to Sportmonks / Highlightly / TheSports; stop
     depending on API-FOOTBALL for Level-2.
3. **External operation stays paused** until Level-2 is validated.

## Guardrails honored
docs-only · no frontend/backend/API/DB change · token never committed/printed · no third-party payload committed ·
odds excluded · `42.2%` internal · PR #2 stays Draft.
