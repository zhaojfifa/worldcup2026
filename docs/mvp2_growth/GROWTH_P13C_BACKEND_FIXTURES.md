# Growth P1.3c — Backend Daily Fixtures Source (live-updatable)

> Owner verdict 2026-06-13: **能更新才是硬道理.** P1.3b made the frontend FETCH the slate at
> runtime, but on a static Render site the JSON is still a deployed file — local cron updating
> the repo does not update the live site without a rebuild. P1.3c hosts the manifest on the
> BACKEND so an operator upload refreshes the live homepage with no frontend redeploy.
> No auto-send · no betting/trading vocab · no payment/attribution data.

## Backend

- **Storage**: new additive table `runtime_manifests` (key TEXT pk · value_json TEXT · updated_at ·
  updated_by). Created by `create_all` on deploy (same pattern as the growth tables). value_json is
  TEXT (cross-DB: sqlite dev + postgres prod). NO user/payment/attribution columns.
- `GET /api/v1/daily-fixtures` — public read. Returns
  `{generated_at, source_mode, date, fixtures, recap_queue, active_hero, freshness}`. Empty-but-valid
  (200, `freshness.stored=false`) when nothing uploaded yet — never 500s.
- `POST /api/v1/admin/daily-fixtures/upload` (and `/refresh`) — admin (x-admin-token, same
  `require_admin` pattern). Accepts the match-sync manifest in EITHER docs shape
  (`internal_fixture_id`/`home_team`) or frontend shape (`id`/`home`); normalizes to frontend shape
  and stores. No score invented — stores what match-sync produced.

## Frontend — three-tier fetch (`dailyFixtures.ts`)

1. **backend** `${VITE_API_BASE_URL || prod}/api/v1/daily-fixtures` (3.5s timeout) → `实时`
2. **static** `/data/daily-fixtures.json` (deployed file, 2.5s) → `静态备份`
3. **bundled** build-time import → `内置`

Each tier validates `fixtures.length>0`; any failure falls through (never throws, never crashes).
HomePage shows the subtle source label; no raw external source links.

## Operator update flow (live, no frontend redeploy)

```bash
python3 scripts/mvp2_match_sync.py sync --date 2026-06-13
ADMIN_API_TOKEN=… python3 scripts/mvp2_match_sync.py upload --target production
# or:
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/daily-fixtures/upload \
  -H "x-admin-token: $ADMIN_API_TOKEN" -H "Content-Type: application/json" \
  --data-binary @docs/data_audit/mvp2_match_sync/daily_fixtures_20260613.json
```
The `upload` command is OPERATOR-triggered, token from `$ADMIN_API_TOKEN` (never hardcoded/printed);
it is an admin manifest POST to OUR backend — **not** a customer send.

## Verification (2026-06-13, branch feature/mvp2-growth-p1-3c-backend-fixtures)

Backend (file-sqlite TestClient): GET empty → 200 `stored=false`; upload no-token → **401**; upload
with token (docs-shape) → 200, 7 fixtures; GET after → 7 fixtures, **active_hero Brazil vs Morocco**,
recap_queue 4, source_mode manual; **Canada RECAP_PENDING 1-1** (not hero), **USA RECAP_PENDING 4-1**.
Local uvicorn round-trip: `upload --target local` → live GET reflects the upload.

Frontend (real browser, fetch-mocked): tier A backend → `实时`; tier B backend-fail+static → `静态备份`;
tier C both-fail → `内置`, **no crash**, warn-only, **0 console errors**. Hero = Brazil in all tiers.

Guards: backend imports OK · backend lifecycle 7/7 · match-sync 8/8 · runtime scanner PASS (+ live
probe `--base-url`) · match-sync scanner PASS · growth copy guard PASS · build PASS · visible 21/21 ·
no betting vocab · no customer auto-send · no payment/attribution data · no DB shape change (additive table).

## Required behavior (Owner)
1 Canada finished/recap_pending on live endpoint ✅ · 2 USA finished/recap_pending ✅ · 3 Brazil
scheduled/hero until kickoff ✅ · 4 homepage reflects upload without frontend rebuild ✅ (backend
tier) · 5 finished cannot become today package ✅ (lifecycle gate) · 6 recap_queue includes finished
needing A4 ✅.

## Deploy & remaining limitation
P1.3c needs **backend deploy** (new table via create_all + endpoints) and a **frontend deploy** (fetch
priority changed). After deploy: live `GET /api/v1/daily-fixtures` + operator `upload` → homepage
updates with NO further frontend redeploy. **This closes the 能更新 gap** for the daily slate.
Remaining: the static `/data/daily-fixtures.json` is still build-time (it is the tier-2 fallback only);
recap NARRATIVES for Canada/USA/SK are still a separate guard-gated A4 step (recap_queue lists them,
no fabrication). Render free-tier backend cold-start (~30s) is covered by the 3.5s timeout → graceful
fall to static; not a failure.
