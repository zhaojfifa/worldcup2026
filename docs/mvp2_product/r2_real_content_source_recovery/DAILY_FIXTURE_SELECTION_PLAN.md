# R2 — DAILY_FIXTURE_SELECTION_PLAN

## Today's date according to the slate
System date **2026-06-15**. Local + live manifests are **stale** (`generated_for_date=2026-06-14`).
Fresh slate must come from API-FOOTBALL (league=1 season=2026), date 2026-06-15.

## Fixtures scheduled / pre-match allowed today (06-15)
- 1489380 Spain vs Cape Verde Islands — NS 16:00 UTC
- **1489377 Belgium vs Egypt — NS 19:00 UTC**
- 1489379 Saudi Arabia vs Uruguay — NS 22:00 UTC
- (1539002 Sweden vs Tunisia — FT 02:00 UTC → recap candidate, not a hotspot)

## Which one is the hotspot, and why
**Belgium vs Egypt (1489377).** Reasons:
1. **Real computed model maps cleanly** — both teams in kaggle; Elo gap +129, full form10 → an honest
   data-backed lean (Spain–Cape Verde fails: Cape Verde not in kaggle → no honest model).
2. **Best product story** — a clear favourite (Belgium, Elo 1885, GF37/GA6) with a genuine upset angle
   (Egypt 5W-3D-2L, solid GA6) → lean + medium risk + tactical contrast.
3. **Scheduled today with runway** (19:00 UTC) — pre-match window for the prediction → T-30 → FT loop.

## How `selected_hotspot` is persisted
- `docs/data_audit/mvp2_match_sync/selected_hotspot_20260615.json` — durable dated record.
- `frontend/src/data/selectedHotspot.json` — the bundled pointer the frontend reads. Set:
  `date=2026-06-15`, `fixture_key="1489377"` (= the manifest `leadKey`: numeric id), `home="Belgium"`,
  `away="Egypt"`, `source="api_football_scoutscore"`, `prediction_artifact_path=…`, `status="active"`.
  (`fixture_key` MUST equal `leadKey(row)=id` so `selectProductLoop` matches the slate row.)

## How to prevent stale 06-14 content remaining the lead
1. **Rewrite the fresh slate** (`frontend/public/data/daily-fixtures.json` + `dailyFixtures.generated.json`)
   to `generated_for_date=2026-06-15` with the 06-15 fixtures (hotspot scheduled) + the carryover recap
   (1489371 Brazil–Morocco, has an observation artifact). The 06-14 Netherlands–Japan entry is dropped.
2. **Repoint `selectedHotspot.json`** to 1489377 (was `manual:Nether-Japan-20260614`).
3. **Guard (`check_daily_content_flow.py` + `check_daily_readiness.py`): FAIL if the selected hotspot is
   stale** — i.e. `selected_hotspot.date` older than the manifest `generated_for_date`, or older than
   the newest scheduled fixture's date. This makes "stale lead" a hard guard failure, not a silent pass.
4. **Deployed flip caveat:** the runtime homepage is backend-first; the live backend still serves 06-14.
   The deployed homepage flips to 06-15 only when the operator uploads the fresh manifest to the backend
   (`mvp2_match_sync … upload --target production`, runtime data = operator). Until then, the fresh
   content is in the bundle/static and verified locally with the backend bypassed.
