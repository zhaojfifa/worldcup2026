# Growth P1.3b — Runtime Daily Fixtures Source

> Owner verdict 2026-06-13: **能更新才是硬道理.** P1.3 made the daily registry a BUILD-TIME static
> import — a cron that rewrites the file does nothing to the live site without a rebuild+redeploy.
> P1.3b makes the registry readable at RUNTIME so the live slate can refresh from a hosted writable
> source. No auto-send · no betting/trading vocab · no payment · no DB schema change.

## What changed

`scripts/mvp2_match_sync.py sync` now writes a THIRD output:
- `frontend/public/data/daily-fixtures.json` — the **runtime source**, fetched by the browser at
  `/data/daily-fixtures.json`. It carries the FULL slate (all 7 fixtures, incl. completed
  Canada/USA) + `generated_at` + `source_mode`, so the runtime frontend KNOWS about finished matches.
- `frontend/src/data/dailyFixtures.generated.json` stays as the **build-time fallback**.

Frontend (`HomePage` + `frontend/src/data/dailyFixtures.ts`):
- `fetchDailyManifest()` fetches `/data/daily-fixtures.json` (`cache: no-store`) on mount; on ANY
  failure it falls back to the bundled import and logs a `console.warn` — never throws, never crashes.
- Hero is selected from the fetched manifest (`heroEntries` → `pickActiveFixture`): live → earliest
  pre-match → latest recap-ready → recap-pending → empty. recapReady recomputed live from the narrative.
- A subtle freshness line shows sync time + source: `⟳ 赛程更新 06/13 12:25 · 实时` (runtime) /
  `· 内置` (bundled fallback) / `· 数据较旧，请运营刷新` when the manifest is >24h old. No raw
  external source links are ever shown to customers.

Package refresh (`mvp2_growth_cli.py refresh`) already sources today/next/recap from the same daily
registry (P1.3); a synced fixture with no narrative → `needs_narrative` + `operator_next_step`
(never fabricated), and it appears in the recap queue.

Scanner (`scripts/check_match_sync_freshness.py`) extended — FAIL if: HomePage does not
`fetchDailyManifest` (build-time-only insufficient) · runtime manifest missing · a completed known
match is absent from the runtime manifest · a finished fixture is a hero/next candidate in the
runtime manifest · the hero is hardcoded · the runtime manifest is stale beyond `--max-age-hours`
(default 36h).

## Verification (2026-06-13, branch feature/mvp2-growth-p1-3b-runtime-fixtures)

- Real browser (dev server): runtime fetch succeeds → hero **Brazil vs Morocco 2-1**, sync line
  `⟳ 赛程更新 … · 实时`. Simulated fetch failure → falls back to bundled (`· 内置`), hero still
  renders, **no crash**, one `console.warn` (no error). Zero console errors.
- match-sync selftest 8/8 · lifecycle CLI 14 / backend 7 / frontend 8.
- match-sync scanner PASS (+ negatives: stale `--max-age-hours 0` → FAIL; missing runtime manifest
  → FAIL; finished-as-candidate → FAIL; hardcoded-hero → FAIL).
- runtime manifest served at `/data/daily-fixtures.json` (200); build copies it into `dist/data/`.
- build PASS; visible scan **21/21**; growth copy guard PASS; no betting vocab; no auto-send.
- Canada 1-1 Bosnia & USA 4-1 Paraguay present in the runtime manifest as RECAP_PENDING /
  recap_needed; never hero/today candidates.

## ⚠️ Honest limitation (Owner-acknowledged)

`frontend/public/data/daily-fixtures.json` is copied into `dist/` at BUILD time. On the current
Render **static site**, the live `/data/daily-fixtures.json` only changes on a rebuild+redeploy —
local cron rewriting the file updates the operator machine, NOT the live site. P1.3b delivers the
runtime-FETCH architecture (decoupled from build-time import); to make the live slate update
without redeploy we still need a **hosted writable source** — a backend endpoint
(`GET /api/v1/daily-fixtures` serving the registry), object storage (R2/S3), or an approved
Render/GitHub scheduled workflow that commits + redeploys. That hosted source is the P1.3c decision
(needs Owner GO on key custody / endpoint). Until then: cron keeps the repo manifest fresh, and a
deploy publishes it.

## Acceptance
runtime manifest exists ✅ · frontend fetches at runtime ✅ · fallback safe (no crash) ✅ ·
Canada/USA visible as finished/recap-needed ✅ · hero registry/runtime-sourced ✅ · completed never
today ✅ · scanner extended + passing ✅ · guards pass ✅ · no auto-send ✅ · limitation documented ✅.
