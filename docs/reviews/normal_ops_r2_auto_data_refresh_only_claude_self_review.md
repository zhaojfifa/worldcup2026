# NORMAL OPS R2 · Claude Self-Review — Automated Data Refresh Only

Verdict: **OPERATE (capability)** — auto data refresh delivered + proven; live baseline kept green.
Scope honored: data refresh ONLY. No homepage/product/UI/logic change.

## What changed (scripts only — no frontend/src, no backend, no schema)
- NEW `scripts/_api_football_slate.py` — fetches the WC season fixtures once from API-FOOTBALL and
  returns ONE date's rows in the shape evaluate() consumes (home/away/score/status/kickoff/api id).
  Honest status mapping (NS→scheduled, FT/AET/PEN→finished, live shorts→live, PST→postponed,
  CANC/ABD/AWD/WO→cancelled, else unknown). Score recorded ONLY for finished+reported matches; else
  null. No events/lineups/injuries read.
- `scripts/mvp2_match_sync.py`:
  * evaluate() now carries an API fixture's own id + kickoff when KNOWN has no hand-mapping (the API id
    IS our internal id space, e.g. Belgium=1489377 both); KNOWN kickoff/group/flags still win. Manual
    raws are unchanged (backward compatible — selftest 8/8).
  * `--source api-football` builds the registry from the API with NO manual file required.
  * manual_scores_<date>.md is now an OPTIONAL operator override (parse_manual_optional + apply_manual_
    override): corrects score/status on a fixture the API returned, tags it operator_override, and NEVER
    invents a fixture the API didn't return. Absent file = no failure.
  * new `refresh` one-shot = sync(api-football) + upload.

## Commands
- `python3 scripts/mvp2_match_sync.py sync --date 2026-06-16 --source api-football`
- `python3 scripts/mvp2_match_sync.py upload --target production --date 2026-06-16`
- (or) `python3 scripts/mvp2_match_sync.py refresh --date 2026-06-16 --target production --source api-football`

## Proof
- sync for 2026-06-16 with NO manual_scores file → generated daily_fixtures_20260616.json: Iran vs New
  Zealand FINISHED 2-2 (real score), France vs Senegal SCHEDULED (null), Iraq vs Norway SCHEDULED (null).
  No invented score/status/event.
- The generated (api-football) registry UPLOADS to production: `{stored:true, fixture_count:3,
  source_mode:api-football}`.

## Manual-scores dependency
manual_scores file is NO LONGER required: api-football sync runs and generates the registry without it
(check_r2_manual_scores_optional PASS). When present, it is override-only.

## Production decision (honest finding)
Uploading the 06-16 slate to production showed LIVE SOURCE CONSISTENCY **FAIL** ("frontend primary 1489377
not in backend slate") — because the 06-16 slate has NO reviewed prediction content / selectedHotspot yet
(that is content-factory / R1 work, explicitly OUT of R2's data-only scope). I therefore RESTORED the
accepted green 06-15 baseline (re-upload, stored=true) so production stays green and existing homepage/
prediction/recap logic still works. The data-refresh CAPABILITY is fully proven; the day-cutover to a new
slate must be a paired run (data refresh + prediction content + selectedHotspot).

## Compliance
No fake score/status/event/lineup/injury/probability/confidence; no betting/odds/handicap language; no
auto-send; no auto-publish; send HOLD. No env/secret committed; token loaded from untracked backend/.env,
never printed (redacted in all evidence). No frontend/src/backend/schema change.

## Guards
check_r2_auto_data_refresh (selftest 9/9 + registry) PASS · check_r2_manual_scores_optional (selftest 5/5
+ date) PASS · match-sync selftest 8/8 (manual path regression) · live: API daily source / source
consistency / p5b lifecycle-rendering / p5b no-finished-primary / Belgium 1-1 / p5b recap-handoff(06-16)
all PASS post-restore.

## Evidence
docs/qa_screenshots/normal_ops_r2_auto_data_refresh_only/ (01 sync-without-manual-file · 02 generated
registry · 03 upload-success-and-restore · 04 internal-daily source state · 05 homepage existing logic).
