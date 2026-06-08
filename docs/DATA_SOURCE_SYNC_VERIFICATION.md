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
