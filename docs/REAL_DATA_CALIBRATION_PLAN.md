# Real Data Calibration Plan (pre–World Cup 2026)

_Created 2026-06-08 · Owner ruling: **Real data calibration = GO** · Scaling/Payment/Bot/Auto-publish = **NO-GO** · LLM stays **draft-only / human review**._

**Goal:** use **real football data** to calibrate product value **before** World Cup 2026 starts.

> **Key engineering finding (this round):** the admin sync endpoints **already accept an optional
> competition override** — `POST /api/v1/admin/sync/fixtures?league_id=<id>&season=<yr>` and
> `…/sync/results?league_id=<id>&season=<yr>` (defaults → `wc_league_id=1`, `wc_season=2026`; chain:
> `admin.py` → `jobs/fixtures_sync` / `services/results/result_sync` → `data_sources/api_football`).
> **No code change and no DB change are required** to pull a real competition. This plan is therefore
> a **runbook + calibration protocol**, not a refactor.

## 1. Why
- Seed/mock is enough for **UI testing**, not for **operation value validation**.
- Real data lets us verify: **data sync · model refresh · risk notes · LLM explanations · community
  copy · user trust** — i.e. whether the Scout product *feels* real to operators and customers.

## 2. Data options
**A. Current live competitions** (real-time feel): La Liga · Champions League · international
friendlies · club friendlies · World Cup qualifiers / warm-ups (whatever the API-FOOTBALL key supports).
**B. Historical World Cup**: 2022 World Cup fixtures/results — for **settlement / recap / backtest**-style
validation (finished matches → real results exist).
**C. 2026 World Cup**: keep as the **campaign target**; use official fixtures when available; until then
**do not rely only on seed/mock**.

## 3. Recommended priority
1. **Current live competitions** → real-time sync / model / operation trial.
2. **Historical World Cup (2022)** → result settlement + recap validation (it has settled results now).
3. **2026 World Cup** seed/preview → until official live data matures.

## 4. Implementation options
**Option A — no schema change first (THIS ROUND):** reuse existing `Match / Team / Prediction /
MatchResult` tables; sync a **small number** of real matches via the existing `league_id`/`season`
override; **tag the source in docs + operation log**; **no public API shape change.**
**Option B — later, only if needed:** add `competition / season / source` fields. **Requires Owner
approval (DB schema change).** Not in scope now.

## 5. Minimal first test (operator-run on Render)
Pick **one** competition. API-FOOTBALL league ids (verify against the active key):
- **La Liga = 140** · Champions League = 2 · International friendlies = 10 · World Cup = 1 (e.g. season 2022).

**Recommended first competition: La Liga (`league_id=140`, current `season`)** if the key supports it —
it is live, well-covered, and gives a real-time feel. **Fallback:** international friendlies
(`league_id=10`) or World Cup qualifiers if La Liga is not in the key's plan; **2022 World Cup
(`league_id=1`, `season=2022`)** for settled-result/recap validation.

## 6. Operator Runbook (Render Shell · `$ADMIN_API_TOKEN` · do NOT fake results)
```bash
BASE=https://worldcup2026-api-71n6.onrender.com
LEAGUE_ID=140      # e.g. La Liga; or 1 + SEASON=2022 for historical World Cup
SEASON=2024        # competition season

# 0) baseline
curl "$BASE/api/v1/data-source/status"                         # note mock_mode, requests_used

# 1) fixtures (competition override — optional params already supported)
curl -X POST "$BASE/api/v1/admin/sync/fixtures?league_id=$LEAGUE_ID&season=$SEASON" \
  -H "x-admin-token: $ADMIN_API_TOKEN"                          # → {inserted, updated, skipped, errors, total, mock_mode}

# 2) results (for finished matches → settlement)
curl -X POST "$BASE/api/v1/admin/sync/results?league_id=$LEAGUE_ID&season=$SEASON" \
  -H "x-admin-token: $ADMIN_API_TOKEN"

# 3) verify
curl "$BASE/api/v1/data-source/status"                          # expect mock_mode=false, requests_used>0
curl "$BASE/api/v1/performance/summary"                         # expect total_settled>0 after results

# 4) refresh model for the synced matches (ids from the fixtures response)
curl -X POST "$BASE/api/v1/matches/<MATCH_ID>/refresh"

# 5) draft copy (admin, draft-only, human review)
curl -X POST "$BASE/api/v1/admin/llm/generate-copy" -H "x-admin-token: $ADMIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"match_id":<MATCH_ID>,"language":"vi","copy_type":"preview"}'   # repeat language:"mm"
```
**Record (real numbers only):** `inserted · updated · skipped · settled · errors · requests_used ·
whether data is real (real|seed)` → paste into `docs/DATA_SOURCE_SYNC_VERIFICATION.md` and the operation log.

## 7. Model calibration (per selected real match)
- Refresh prediction; if the match is **finished**, compare model direction vs the **actual result**.
- Record: **model direction · risk_level · whether the explanation was useful.**
- **Do not market hit-rate** until enough settled data exists (`performance.total_settled` meaningful,
  `hit_rate` not null) — and even then framed as AI-viewpoint, not a guarantee.

## 8. Operation use (real matches → reviewable drafts)
Generate, for real matches: **daily preview · upset watch · pre-match update · post-match recap ·
model-miss / model-hit explanation.** All via the draft-only endpoint → **human review** → operator
sends manually (DeepSeek primary / Gemini benchmark for vi/mm; not Kimi). Nothing auto-published.

## 9. Boundaries
No scaling · no payment · no auto-publish · no bot · **no public API shape change** · **no DB schema
change** (Option B needs Owner approval) · **no fake real data** · **no hit-rate marketing**.

## 10. This round's outcome
- **Runbook ready** (override already supported → no code change).
- **First competition recommendation:** La Liga (`140`), fallback friendlies (`10`) / WC-2022 (`1`/2022).
- **Pending operator action** on Render (Claude has no token → will not fabricate). Results land in
  `docs/DATA_SOURCE_SYNC_VERIFICATION.md` §11 (Operator Action Checklist, now extendable per-competition).

## 11. Update (2026-06-09) — priority shifted to warm-ups; specific matches selected
Owner correction: produce **specific real matches**, not league-level guidance. **Priority is now
warm-ups/friendlies first** (`league_id=10, season=2026`), then WC-2026 (`1/2026`), then WC-2022 backtest.
Selected real fixtures are listed in **`docs/REAL_MATCH_INTELLIGENCE_SELECTION.md`** (upcoming Mexico v
South Africa; finished Brazil-Egypt, Argentina-Honduras) with sources; per-competition sync table in
`DATA_SOURCE_SYNC_VERIFICATION.md` §12. Claude is `BLOCKED_OPERATOR_RENDER_SHELL` (no token) — match
selection proceeded anyway, no fabricated sync/results.

## 12. Gate result (2026-06-09, operator-run)
- **Friendlies `10/2026` = 0; WC `1/2026` = 0** → **2026 fixtures currently unavailable from the provider.**
- **WC `1/2022` = 64 fixtures / 64 results / 64 settled** → **usable for backtest/recap/calibration only.**
  `hit_rate=42.2%` is a **technical backtest metric, NOT marketable accuracy.** 2022 ≠ live.
- `/matches` now mixes historical (id 4–67) + seed (id 1–3) → data/product separation needed:
  **`docs/HISTORICAL_RECAP_MODE_PROPOSAL.md`** (frontend filter by status/date + labelled Recap surface;
  no API/DB change). Priority order updated: warm-ups/2026 remain target but **currently unavailable** →
  use **WC-2022 historical** for calibration in the meantime.
