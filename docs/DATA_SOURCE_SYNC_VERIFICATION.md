# Data Source Sync Verification (Harness-X · L1)

**Verdict: PASS WITH ISSUES** — connector reachable, but still `mock_mode=true` (no live pull
yet) and admin sync is Owner/operator-gated (Render Shell). No engineering blocker.

## 1. Input / boundary
Verify the data-source connector + sync endpoints, read-only from local. No backend change, no
API shape change, no DB schema change. Admin writes are token-gated (Render Shell only).

## 2. Role path used
L1 verification (curl). Admin sync = P-flow operator step (not executed locally; no token).

## 3. Changed files
Docs only (this file + status syncs). No code.

## 4. Verification commands & results (2026-06-08 ~03:56 UTC)
```
GET /api/v1/data-source/status
→ api_football_configured=true, connector_status=ok, mock_mode=true,
  requests_used=0, requests_limit=100, message="API-FOOTBALL reachable"

GET /api/v1/performance/summary
→ total_settled=0, hit_rate=null, last7d_hit_rate=null, high_confidence_hit_rate=null,
  live_correction_uplift=null, neutral_count=0; disclaimer present

GET /api/v1/performance/daily
→ date=2026-06-08, total_settled=0, hit_count=0, hit_rate=null

POST /api/v1/admin/sync/fixtures   (no token) → 401 "Invalid or missing x-admin-token"
POST /api/v1/admin/sync/results    (no token) → 401 "Invalid or missing x-admin-token"
```

## 5. mock/real boundary
- **Current state: MOCK.** Matches/results are seed data; `mock_mode=true`, `requests_used=0`
  (no live API-FOOTBALL pull has happened). `performance/*` is all zero/null → **no real track
  record exists yet.**
- **Real-data path is operator-run (Render Shell, `$ADMIN_API_TOKEN`):**
  ```bash
  curl -X POST .../api/v1/admin/sync/fixtures -H "x-admin-token: $ADMIN_API_TOKEN"
  curl -X POST .../api/v1/admin/sync/results  -H "x-admin-token: $ADMIN_API_TOKEN" \
       -d '{"league_id":1,"season":2026}'
  ```
  Expected graceful counts (`inserted/updated/skipped/settled`); `0/0/…` when no finished fixtures.

## 6. Risk / blocker
- **Compliance risk if mock is mistaken for real:** until a real `sync/results` runs and
  `performance.*` is non-null, **do not present any hit-rate as real**. UI already gates this
  ("real results sync" pending state).
- Blocker: live sync requires operator Render Shell action (Owner/ops), not engineering.

## 7. Verdict
**PASS WITH ISSUES** — endpoints healthy & locked correctly; mock/real boundary clear and
documented; real pull pending operator action.

## 8. Next Owner decision needed?
**Yes (operator):** decide whether to run real fixtures/results sync now, or stay on seed for the
small-traffic trial (copy/community validation does not require real accuracy).

---

## 9. Data formalization run (2026-06-08, Owner-approved bounded L2-lite)

**Verdict: BLOCKED (on operator Render-Shell step)** — engineering verified everything reachable
from local; the actual `admin/sync/*` writes require `$ADMIN_API_TOKEN` which lives only in the
Render Shell. **Claude cannot reach Render Shell and must not fabricate sync results.**

| Item | Result (2026-06-08 ~04:30 UTC) |
|------|-------------------------------|
| `data-source/status` | `api_football_configured=true`, `connector_status=ok`, **`mock_mode=true`**, `requests_used=0`, `requests_limit=100` |
| `admin/sync/fixtures` (local, no token) | `401 Invalid or missing x-admin-token` (lock correct) |
| `admin/sync/results` (local, no token) | `401` (lock correct) |
| `performance/summary` | `total_settled=0`, `hit_rate=null` (still all zero) |
| fixtures inserted/updated/skipped/errors | **N/A — not executed (operator step)** |
| results inserted/updated/settled/skipped/errors | **N/A — not executed (operator step)** |

**Operator action required (Render Shell):**
```bash
curl -X POST .../api/v1/admin/sync/fixtures -H "x-admin-token: $ADMIN_API_TOKEN"
curl -X POST .../api/v1/admin/sync/results  -H "x-admin-token: $ADMIN_API_TOKEN" -d '{"league_id":1,"season":2026}'
curl .../api/v1/data-source/status      # expect mock_mode=false, requests_used>0 after a real pull
curl .../api/v1/performance/summary     # expect total_settled>0 after results settle
```
Paste the returned counts back into this table.

**Data provenance (current):**
- **Real:** service uptime, R2 storage, community heat/events, streak/rankings, MTC ledger,
  baseline compute, refresh.
- **Seed/mock:** match fixtures, results, win-prob inputs (`mock_mode=true`, 0 live pulls).
- **Operator may use:** AI-viewpoint copy, risk signals, pre-match updates, community CTAs.
- **Forbidden to advertise:** any real hit-rate / accuracy (none exists; `performance.*` all null/0).

## 10. Owner GO for real data (2026-06-08) — still operator-gated for Claude
Owner approved real data integration. Re-checked live: `mock_mode=true`, `requests_used=0`;
`admin/sync/fixtures` still `401` from local (no token). **Claude cannot run the real sync (no
Render Shell / token) and will not fabricate counts.** The real pull remains the operator step in
§9. Status unchanged: data still seed until operator runs sync on Render.

## 11. Operator Action Checklist (data-first — highest priority)
Run on **Render Shell** (operator + `$ADMIN_API_TOKEN`). **Do not fabricate results** — paste real output.

- [ ] **Fixtures sync** — `curl -X POST .../api/v1/admin/sync/fixtures -H "x-admin-token: $ADMIN_API_TOKEN"`
      → record inserted/updated counts.
- [ ] **Results sync** — `curl -X POST .../api/v1/admin/sync/results -H "x-admin-token: $ADMIN_API_TOKEN" -d '{"league_id":1,"season":2026}'`
      → record settled count.
- [ ] **Performance summary** — `curl .../api/v1/performance/summary` → record `total_settled`, `hit_rate`.
- [ ] **Data-source status** — `curl .../api/v1/data-source/status` → record `mock_mode`, `requests_used`.
- [ ] **Record real-vs-seed:** state explicitly whether match/fixture/result data is **real** or **seed**.
- [ ] **What can be used in operation copy:** if real → AI-viewpoint + pre-match + risk signals; results recap only once settled.
- [ ] **What must NOT be marketed:** **no hit-rate / accuracy / guaranteed-result claims** while
      `total_settled` is 0 or `hit_rate` is null. (Compliance floor — unchanged.)

| Field | Value (operator fills) |
|-------|------------------------|
| fixtures inserted/updated |  |
| results settled |  |
| performance.total_settled |  |
| performance.hit_rate |  |
| data-source.mock_mode |  |
| data-source.requests_used |  |
| real or seed? |  |
| usable in copy |  |
| must-not-market |  |

> **Until this checklist is filled with real Render output, treat all match data as seed.** LLM drafts
> already carry `data_mode=mock` + "do not present as real accuracy" warnings (see
> `docs/LLM_DRAFT_COPY_REVIEW_LOG.md`).

## 12. Real Match Intelligence Sprint — per-competition sync (2026-06-09)

**Claude status: `BLOCKED_OPERATOR_RENDER_SHELL`** — Claude has no `$ADMIN_API_TOKEN`, so the syncs below
were **NOT run by Claude and are NOT fabricated.** Selected real matches: `docs/REAL_MATCH_INTELLIGENCE_SELECTION.md`
(RMI-01 Mexico v South Africa upcoming; RMI-02 Brazil-Egypt, RMI-03 Argentina-Honduras finished).

**Operator runs on Render (warm-ups/friendlies first):**
```bash
BASE=https://worldcup2026-api-71n6.onrender.com
curl -X POST "$BASE/api/v1/admin/sync/fixtures?league_id=10&season=2026" -H "x-admin-token: $ADMIN_API_TOKEN"
curl -X POST "$BASE/api/v1/admin/sync/results?league_id=10&season=2026"  -H "x-admin-token: $ADMIN_API_TOKEN"
curl "$BASE/api/v1/data-source/status";  curl "$BASE/api/v1/performance/summary"
# then league_id=1&season=2026 for the WC opener (RMI-01)
```

| run_at | operator | competition_name | league_id | season | fixtures_inserted | fixtures_updated | fixtures_skipped | results_inserted | results_updated | results_settled | errors | requests_used_before | requests_used_after | data_mode_after | selected_matches_count | usable_for_operation | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | friendlies (P1) | 10 | 2026 |  |  |  |  |  |  |  |  |  |  |  |  | RMI-02/03/04/05 — confirm key covers league 10 |
|  |  | World Cup (P2) | 1 | 2026 |  |  |  |  |  |  |  |  |  |  |  |  | RMI-01 opener (upcoming → no result yet) |
|  |  | World Cup backtest | 1 | 2022 |  |  |  |  |  |  |  |  |  |  |  |  | optional settled-result validation |

> If the API-FOOTBALL key plan does **not** return a league, mark that row `api_available=no` in
> `REAL_MATCH_INTELLIGENCE_SELECTION.md` and treat those matches as **public_source** only —
> **never relabel news data as API data; never fabricate counts.**

## 13. Fast Real Data Gate (2026-06-09) — execute on Render, fill ONE row per run

Baseline tagged **`v0.8-real-data-gate`** (commit `d4feb6c`) before any real sync. **Claude cannot run
this (no `$ADMIN_API_TOKEN`) → do NOT fabricate.** Operator runs the order below and stops at the first
that returns real matches.

**Order:** (1) friendlies `league_id=10&season=2026` → (2) WC `1&2026` → (3) WC backtest `1&2022`.
```bash
BASE=https://worldcup2026-api-71n6.onrender.com
# 1) friendlies
curl -X POST "$BASE/api/v1/admin/sync/fixtures?league_id=10&season=2026" -H "x-admin-token: $ADMIN_API_TOKEN"
curl -X POST "$BASE/api/v1/admin/sync/results?league_id=10&season=2026"  -H "x-admin-token: $ADMIN_API_TOKEN"
curl "$BASE/api/v1/matches"                       # → are there real matches? note ids
# 2) if league 10 empty/failed → WC 2026
curl -X POST "$BASE/api/v1/admin/sync/fixtures?league_id=1&season=2026" -H "x-admin-token: $ADMIN_API_TOKEN"
curl "$BASE/api/v1/matches"
# 3) else → WC 2022 backtest
curl -X POST "$BASE/api/v1/admin/sync/fixtures?league_id=1&season=2022" -H "x-admin-token: $ADMIN_API_TOKEN"
curl -X POST "$BASE/api/v1/admin/sync/results?league_id=1&season=2022"  -H "x-admin-token: $ADMIN_API_TOKEN"
curl "$BASE/api/v1/performance/summary"
# then, if real matches exist: pick 1-3, refresh each
curl -X POST "$BASE/api/v1/matches/{match_id}/refresh"
```

| gate_run_at | operator | command_run | league_id | season | fixtures_inserted | fixtures_updated | fixtures_skipped | results_inserted | results_updated | results_settled | errors | requests_used_before | requests_used_after | matches_returned_count | selected_match_ids | selected_matches | decision (use/fallback/blocked) | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | sync/fixtures+results | 10 | 2026 |  |  |  |  |  |  |  |  |  |  |  |  |  | step 1 — friendlies |
|  |  | sync/fixtures | 1 | 2026 |  |  |  |  |  |  |  |  |  |  |  |  |  | step 2 — WC if step1 empty |
|  |  | sync/fixtures+results | 1 | 2022 |  |  |  |  |  |  |  |  |  |  |  |  |  | step 3 — backtest if step2 empty |

**Per-match refresh (fill after a real match_id is confirmed):**
| match_id | home | away | win_prob (H/D/A) | confidence | risk_level | risk_note | updated_at |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

> **Decision rule:** `use` (real matches present → proceed to per-match copy / LLM draft / screenshots) ·
> `fallback` (next league in the order) · `blocked` (none return real matches → mark blocked, return to
> Owner, **do not fabricate and do not extend matchup mapping**).
