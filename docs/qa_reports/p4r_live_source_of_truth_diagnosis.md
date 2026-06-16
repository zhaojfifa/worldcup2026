# P4R++ · Live Source-of-Truth Diagnosis

> Branch `fix/mvp2-p4r-live-source-of-truth`. Admin-authenticated live verification.
> `ADMIN_TOKEN_USED=true` · `ADMIN_TOKEN_REDACTED=true` (token never committed/printed/screenshotted).

## Endpoints checked
- Public read: `GET https://worldcup2026-api-71n6.onrender.com/api/v1/daily-fixtures` → 200.
- Admin write (authenticated): `POST /api/v1/admin/daily-fixtures/upload`, header `x-admin-token`
  (validated against the backend's configured `ADMIN_API_TOKEN`). Driven by
  `scripts/mvp2_match_sync.py upload --target production` (reads `$ADMIN_API_TOKEN`, never prints it).

## Token acceptance
The admin upload was attempted with the provided token and **ACCEPTED** — response
`{"stored":true,"fixture_count":6,"source_mode":"manual"}`. So the protected runtime-update path works
and engineering can now self-verify the live update (previous BLOCKED_BY_OPERATOR_TOKEN is removed).

## Current live state (post-authenticated-upload)
- runtime manifest date (`date`): **2026-06-15**.
- active content date (dailyContentQueue / selectedHotspot): **2026-06-15** → MATCH.
- freshness: `stale=false` (within the 36h threshold).
- expected fixture 1489377 present; `check_runtime_daily_fixtures … --expected-date 2026-06-15
  --expected-fixture 1489377` → PASS.
- active slate fixtures: 1489377 Belgium-Egypt (SCHEDULED), 1489379 Saudi-Uruguay, 1489380
  Spain-CapeVerde, 1489371 Brazil-Morocco (RECAP_PENDING), 1489369 Mexico-SA (ARCHIVED), 1539002
  Sweden-Tunisia. **No Germany/Japan/Qatar/Ecuador (WC-2022 archive teams) in the active slate.**

## Does `/daily-fixtures` include 2022 history? Does the active package filter it?
The PUBLIC `/daily-fixtures` active slate does **NOT** include 2022 history — it is the curated daily
slate only. The WC-2022 historical recaps (e.g. 德国 vs Japan, Qatar vs Ecuador 2022 opener) render in
a SEPARATE frontend "历史复盘 / Historical Recap · WC2022" archive section, which is NOT today's active
content and is correctly labelled as history. The active package (selectedHotspot + dailyContentQueue)
drives the critical homepage sections; the archive is below and labelled.

## Page source-of-truth (live)
- Homepage primary → active package (selectedHotspot Belgium-Egypt) + reviewed LLM lean (i18n synced). ✅
- Homepage yesterday recap → manifest finished[0] (Brazil-Morocco) + observation receipt. ✅
- `/predict/1489377` & `/predict/1489379` → reviewed LLM copy (i18n synced from reviewed JSON). ✅
- `/recap/1489371` → observation receipt, labelled OBSERVATION (recap_ready=false), no fake event. ✅
- Share cards → strong-call projection (lean+score) / observation share copy. ✅
- `/internal/daily` → dailyOpsState source-trace rows (active content date, copy source, freshness). ✅

## Verdict
Source-of-truth is EXPLICIT and CORRECT: backend active slate == frontend active package (date
2026-06-15, primary 1489377); 2022 history is archive-only, not today's active content; reviewed LLM
copy renders. Admin token verified the protected update path. Send remains HOLD.
