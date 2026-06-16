# Codex Adversarial Review — NORMAL OPS R2 · Automated Data Refresh ONLY

- Branch: `ops/r2-auto-data-refresh` · HEAD `556b6bd`
- Reviewer: Codex (independent adversarial)
- Date: 2026-06-16

## Overall verdict: **PASS**

R2 delivers the automated daily-slate capability exactly within scope: `--source api-football`
pulls the day's WC fixtures from API-FOOTBALL and generates the existing daily_fixtures registry +
recap_queue with NO manually-authored manual_scores file required; manual_scores becomes an
optional override. Data is honest (no invented score/status/event). No frontend/backend/schema
change, no homepage/product/UI/prediction/recap/share logic change, no scheduler, no
auto-send/auto-publish. Live production is green on the restored 06-15 baseline. One LOW-severity
design observation (FE manifest side-write footgun) — not blocking.

---

## Check 1 — Diff scope (DATA/SCRIPTS ONLY)
`git diff main...HEAD --stat` — exactly 7 tracked files, all in scope:
- `scripts/_api_football_slate.py` (new)
- `scripts/mvp2_match_sync.py`
- `scripts/check_r2_auto_data_refresh.py` (new guard)
- `scripts/check_r2_manual_scores_optional.py` (new guard)
- `docs/reviews/normal_ops_r2_auto_data_refresh_only_claude_self_review.md`
- `docs/data_audit/mvp2_match_sync/daily_fixtures_20260616.json` (generated)
- `docs/data_audit/mvp2_match_sync/recap_queue_20260616.json` (generated)

`git diff main...HEAD -- frontend/` = **empty**. `git diff main...HEAD -- backend/` = **empty**.
`git diff main...HEAD -- frontend/src/data/dailyFixtures.generated.json frontend/public/data/daily-fixtures.json`
= **empty** (bundled homepage build artifacts unchanged vs main). No `frontend/src`, `backend/`,
schema, or migration file touched. Untracked entries are only pre-existing screenshot dirs
(`docs/qa_screenshots/normal_ops_r1_*`, `normal_ops_r2_*`, `ops_live_consolidated_main/`).

**DIFF_SCOPE_DATA_ONLY=yes · HOMEPAGE_BUILD_UNCHANGED=yes**

## Check 2 — Source review (`_api_football_slate.py`, `mvp2_match_sync.py`)
- (a) Honest status mapping — `_api_football_slate.py:25-43`: `_FINISHED={FT,AET,PEN}→finished`,
  live shorts `{1H,2H,HT,ET,BT,P,LIVE,INT}→live`, `PST→postponed`,
  `{CANC,ABD,AWD,WO}→cancelled`, `NS/TBD→scheduled`, else `unknown`. Matches spec.
- (b) Score only when finished+reported — `_api_football_slate.py:74-77`: score set ONLY if
  `status=="finished" AND goals.home/away not None`, else `None`. No invention.
- (c) No events/lineups/injuries fetched — only `fixture`, `teams`, `goals`, `status.short` read
  (`_api_football_slate.py:64-72`). Confirmed.
- (d) `evaluate()` preserves registry shape — `mvp2_match_sync.py:185-232`: for unmapped fixtures it
  uses `known.get("internal") or str(api_id)` (`:193`) and `known.get("kickoff") or raw.kickoff_utc`
  (`:194`). The API fixture id IS the internal id space (documented), so no faked id. Manual raws
  (no `api_fixture_id`/`kickoff_utc`) → `internal=None`, slug external id — manual path unchanged.
- (e) manual optional — `parse_manual_optional` (`:126-132`) returns `[]` when file absent (no
  raise); the api-football branch (`cmd_sync :329`) calls `parse_manual_optional`, NOT the raising
  `parse_manual`. `apply_manual_override` (`:135-152`) only mutates fixtures already in `by_key`
  (API-returned); an override for a matchup the API didn't return is skipped (`:144-145`) — corrects,
  never invents.

LOW-severity note (operator-driven, by design): `apply_manual_override` applies a `status` override
independently of score (`:148-149`), so an operator could set `status=finished` with no score → a
finished row with null score; and the auto-refresh honesty guard only flags
`scheduled/unknown`-with-score (not `finished`-with-null-score). This is operator override territory,
not the automated path, and is not score fabrication. No change required.

## Check 3 — Guards & selftests (non-vacuous)
- `check_r2_auto_data_refresh.py --selftest` → 9/9 PASS. Non-vacuous: builds a real `evaluate()`
  finished fixture (Iran/NZ id 1489378, score 2-2 kept, id+kickoff carried) and a scheduled fixture
  asserted null score (`:60-77`).
- `check_r2_auto_data_refresh.py --date 2026-06-16` → PASS (required fields present, scores honest).
  The honesty scan would FAIL a scheduled/unknown row carrying a score, a half-null score, or a
  non-integer score (`:43-48`).
- `check_r2_manual_scores_optional.py --selftest` → 5/5 PASS. Non-vacuous: a "Ghost vs Phantom"
  override is asserted ignored (`applied==1`, `len(out)==2`) and the api-football code block is
  string-checked to use `parse_manual_optional` and NOT `parse_manual(compact)` (`:40-43`).
- `check_r2_manual_scores_optional.py --date 2026-06-16` → PASS (registry generated, manual ABSENT).
- `mvp2_match_sync.py --selftest` → 8/8 PASS (manual-path regression intact, incl. "no invented
  score for scheduled").

## Check 4 — Generated registry `daily_fixtures_20260616.json`
`source_mode=api-football`, 3 fixtures. Iran vs New Zealand `finished` score `2-2`
(`lifecycle_state=RECAP_PENDING`, recap_needed=true); France vs Senegal `scheduled` null/null;
Iraq vs Norway `scheduled` null/null. No fabricated finished status, no invented score. All required
snake_case fields present per fixture (external_game_id, internal_fixture_id, home_team, away_team,
kickoff_time_utc, status, score_home, score_away, lifecycle_state, pre_match_allowed, recap_ready,
recap_needed, package_today_allowed, narrative_renderable, hero_candidate, recap_candidate,
next_candidate, reason). recap_queue_20260616.json lists only Iran vs NZ (2-2, recap_needed,
priority 2). (Prompt referenced "France/Iraq scheduled" — confirmed as the home teams of the two
scheduled rows.)

**API_SOURCE_GENERATES_REGISTRY=yes · FAKE_DATA=none**

## Check 5 — Manual not required
`docs/data_audit/mvp2_match_sync/manual_scores_20260616.md` does NOT exist (only 06-13/06-14/06-15
manual files present). The 06-16 registry was generated anyway. Capability does not depend on a
manual file.

**MANUAL_SCORES_OPTIONAL=yes**

## Check 6 — Live API path exercised (different date)
Sourced `backend/.env` (token/key never printed) and ran
`sync --date 2026-06-17 --source api-football` with no manual file → generated 5 real WC fixtures
(Argentina/Algeria, Austria/Jordan, Portugal/Congo DR, England/Croatia, Ghana/Panama), all
`scheduled` with null/null scores, `source_mode=api-football`. Honest, no invention. Then restored
the bundled FE manifest (`git checkout -- frontend/src/data/dailyFixtures.generated.json
frontend/public/data/daily-fixtures.json`) and removed the stray 06-17 registry/recap_queue.
`git status` left clean (only pre-existing untracked screenshot dirs). Did NOT upload to production
per instruction. Upload code (`cmd_upload :434-456`, requires `$ADMIN_API_TOKEN`, reads env only,
never hardcodes/prints) is unchanged accepted P1.3c; implementer reports the 06-16 upload returned
`stored:true` — not re-exercised here (no prod upload).

**UPLOAD_WORKS=yes** (implementer-proven; code reviewed, not re-run to avoid prod write)

## Check 7 — Product/UI unchanged + live green
`git diff main...HEAD --name-only | grep frontend/src/components|frontend/src/pages|schema|migration`
= empty. Live consistency:
`LIVE SOURCE CONSISTENCY · backend_date=2026-06-15 · active_date=2026-06-15 · primary=1489377` →
**PASS** (backend runtime == frontend active package; restored green 06-15 baseline).

**PRODUCT_UI_UNCHANGED=yes**

## Check 8 — Compliance
No betting/odds/handicap/盘口/投注/竞猜/下注/稳赚/必中/跟单/stake/wager/bookmaker wording in the new
code or generated registry/recap_queue (grep RC=1, no match). `win_prob`/`confidence`/`probability`
appear ONLY in the self-review's compliance prose ("No fake … probability/confidence") — not
introduced into any data structure. `auto-send`/`auto-publish` appear ONLY in the self-review prose
("no auto-send; no auto-publish; send HOLD"). No auto-send/auto-publish code added.

**BETTING_VOCAB=none · AUTO_SEND=none · SEND_STATUS=HOLD**

## Check 9 — Secret scan
`git ls-files | grep backend/.env` = empty (backend/.env NOT tracked). No `.env` in the diff.
`git diff main...HEAD` contains no token-like assignment (count 0) and no `ADMIN_API_TOKEN` literal
(the only token handling is `os.environ.get("ADMIN_API_TOKEN")` in pre-existing upload code, not in
this diff). Token value never read, echoed, or quoted in this review. backend/.env defines
ADMIN_API_TOKEN locally but is untracked.

**ADMIN_TOKEN_LEAK=false**

---

## Defects
- **LOW (design observation, non-blocking):** Every `sync --source api-football` run side-writes
  `frontend/src/data/dailyFixtures.generated.json` AND `frontend/public/data/daily-fixtures.json`
  (`write_frontend_manifest :282-312`, called unconditionally in `cmd_sync :356`). This is inherited
  P1.3 behavior, but R2 makes it trivial to mutate the homepage build for ANY arbitrary date; an
  operator who forgets to restore would dirty the FE build. The implementer correctly restored the
  baseline. Recommend (future) gating the FE-manifest write behind a flag or only on the production
  cutover step so a pure data-refresh dry-run can't touch the homepage artifacts.
- **LOW (operator-driven):** `apply_manual_override` can set `status` without a score; the
  auto-refresh honesty guard does not flag a `finished` row with null score. Not in the automated
  path, not score fabrication. No action required.

## Confirmation lines
- DIFF_SCOPE_DATA_ONLY=yes
- PRODUCT_UI_UNCHANGED=yes
- HOMEPAGE_BUILD_UNCHANGED=yes
- MANUAL_SCORES_OPTIONAL=yes
- API_SOURCE_GENERATES_REGISTRY=yes
- UPLOAD_WORKS=yes
- FAKE_DATA=none
- BETTING_VOCAB=none
- AUTO_SEND=none
- SEND_STATUS=HOLD
- ADMIN_TOKEN_LEAK=false
- BACKEND_SCHEMA_CHANGE=no
