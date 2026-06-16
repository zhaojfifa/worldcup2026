# Codex Adversarial Review — P5B Match Lifecycle Homepage Orchestration

- **Reviewer:** Codex (independent adversarial)
- **Date:** 2026-06-16
- **Branch / HEAD:** `feature/mvp2-p5b-match-lifecycle-homepage-orchestration` @ `2840523`
- **Scope:** homepage now FOLLOWS match progress via a lifecycle selector artifact read by the frontend.

## OVERALL VERDICT: PASS_WITH_PATCHES

All hard rules hold on the committed state: primary is never finished / operator_estimated / archive /
demo; secondary cap 2; latest_recap is finished; send HOLD; no fake probability; no backend/schema/cron;
no token leak; scope contained. Two robustness/process defects (1 MEDIUM foot-gun, several LOW) keep this
from a clean PASS but none is a runtime rule violation.

### Confirmation lines
- `BETTING_VOCAB=none` (only prohibition statements in the gate-spec / decision docs; no betting copy)
- `FAKE_DATA=none` (no fake score/event/lineup/injury; no fake numeric probability)
- `AUTO_SEND=none` (send_status HOLD; no scheduler/cron in diff)
- `FINISHED_PRIMARY_POSSIBLE=no`
- `ARCHIVE_DEMO_LEAK=no`
- `ADMIN_TOKEN_LEAK=false`
- `SEND_STATUS=HOLD`
- `SCOPE_EXPANSION=no`

---

## Check 1 — `scripts/mvp2_homepage_lifecycle_selector.py`

PASS (with observations). Read in full.

- Primary selection (lines 126-127): `next(r for r in upcoming if r["model_source"] in SOURCE_QUALIFIED
  and r["lifecycle_state"] in (UPCOMING_PREDICTION_READY, T30_WINDOW_PENDING, T30_READY))`. `upcoming` is
  ko-sorted ascending (line 120), so the earliest upcoming source-qualified match wins. Finished
  (`FINISHED`/`RECAP_*`/`ARCHIVED`) and `LIVE_OR_LOCKED` states are excluded from `upcoming` and thus from
  primary. operator_estimated is excluded because `model_source` must be in `SOURCE_QUALIFIED` (line 34).
- Archive/demo (lines 69-72) classified to `ARCHIVE_ONLY` / `EXCLUDED_DEMO` before any other state → never
  upcoming → never primary/secondary.
- No primary → `blocked_items` carries `PRIMARY_REVIEW_REQUIRED` (lines 136-137); never stale fixed content.
- `validate` (lines 211-235) re-asserts all five invariants. Ran:
  - `validate --date 2026-06-15` → PASS
  - `validate --now 2026-06-15T12:00:00Z` (editorial basis) → PASS
  - `validate --now 2026-06-15T20:00:00Z` (after Belgium KO) → PASS
- Rotation proof: `build --now 2026-06-15T20:00:00Z` → primary rotates Belgium → **Saudi Arabia vs Uruguay**
  (Belgium is past kickoff → `LIVE_OR_LOCKED` → dropped; next source-qualified upcoming = Saudi). Rotation
  via time basis works as designed.

**Observation D3 (LOW):** `SOURCE_QUALIFIED = {"computed", "operator_confirmed", "seed"}` (line 34) admits
`seed` as primary-qualified, but the stated hard rule is "model computed | operator_confirmed". `seed` is
real seed data (not operator_estimated), so this is a broadening, not a fake-data path; no current fixture
uses `seed` so there is no live impact. Recommend Owner confirm `seed` is intentionally primary-eligible.

**Defect D1 (MEDIUM — foot-gun / determinism):** `cmd_build` writes the **committed** bundled file
`frontend/src/data/homepageLifecycle.json` by default (`write_fe=True`, lines 194-199) using whatever
`--now` is passed (default = wall clock). There is no guard that the committed bundled artifact uses the
editorial noon basis. During this review, running `build --now …T20:00:00Z` (to verify rotation) silently
overwrote the bundled primary to Saudi; I restored it via `git checkout`. Deploy determinism therefore
relies on the operator remembering to pass the editorial basis, and a stray `build` (e.g. for inspection)
clobbers the editorial board. Recommend: make `build` not write FE by default (separate `--write-fe`), or
add a guard asserting the bundled `current_time_basis` equals the editorial noon for the active date.

## Check 2 — `frontend/src/data/dailyFixtures.ts`

PASS. `selectProductLoop` (lines 197-253) reads `HOMEPAGE_LIFECYCLE` (imported at line 9). `featuredPrediction`
is assigned only via three paths, all of which exclude finished matches:
- lifecycle primary (lines 222-224): guarded by `!FINISHED_STATES.has(lcPrimary.lifecycle_state)` **and**
  `hasPredictionArtifact(...)`.
- legacy fallback (lines 228-233) only when `!lc.primary_prediction`; uses `scheduled.find(...)` and
  `scheduled` excludes `FINISHED_STATES` (lines 200-202).
`featuredRecap` (line 238) requires `FINISHED_STATES.has(...)`. Secondary set filters out finished (line 242).
**FINISHED_PRIMARY_POSSIBLE=no.**

**Defect D2 (LOW — scope limitation, disclose):** the lifecycle artifact is **bundled** (compile-time import,
line 9), not fetched at runtime like the manifest (`fetchDailyManifest`). So the homepage roles are frozen at
build/deploy time — it "follows match progress" only at each rebuild. At runtime, if the bundled primary has
actually kicked off/finished AND `lc.primary_prediction` is non-null, the first `if` fails and the `else if
(!lc.primary_prediction)` is also false → `featuredPrediction` stays `null` (no rotation to next upcoming;
homepage shows no prediction lead until a redeploy). This is SAFE (never shows a finished primary) but not
self-healing. The runtime finished-guard does its job; the rotation claim should be scoped to deploy-time.

## Check 3 — bundled `frontend/src/data/homepageLifecycle.json`

PASS. `primary_prediction` = **Belgium vs Egypt** (`1489377`, `UPCOMING_PREDICTION_READY`, `model_source:
computed`, basis `2026-06-15T12:00:00+00:00`) — the editorial noon basis, **NOT** Saudi (the rotation-proof
basis). secondary = Spain vs Cape Verde (operator_estimated, labelled) + Saudi vs Uruguay (computed), cap 2.
latest_recap = Brazil vs Morocco (`FINISHED_OBSERVATION_READY`). `send_status: HOLD`. No archive/demo in
active roles. Correct.

## Check 4 — `frontend/src/pages/DailyStatusPage.tsx`

PASS. The `🔁 比赛生命周期 / Match lifecycle (LIFECYCLE)` card exists with rows: active date/time basis,
primary + reason_for_role, latest recap, secondary, next upcoming, finished pending recap, excluded
archive/demo, blocked, next action, and send status (`HOLD — no auto-send`). Primary row verdict is `fail`
when no primary (PRIMARY_REVIEW_REQUIRED), `warn`/`ok` otherwise.

## Check 5 & 6 — the six P5B guards + p5a copy contract

All `--selftest` PASS and are non-vacuous (each has at least one true negative-case assertion):
- `check_p5a_copy_contract` 4/4 · `check_p5b_homepage_lifecycle_selector` 5/5 (catches finished/op_est
  primary, >2 secondary) · `check_p5b_homepage_lifecycle_rendering` 2/2 · `check_p5b_no_finished_primary`
  3/3 (catches finished state AND manifest-status finished) · `check_p5b_recap_handoff` 2/2 ·
  `check_p5b_internal_daily_lifecycle_trace` 3/3 · `check_p5b_archive_demo_exclusion` 3/3 (incl. precise
  `demo_pair_leak`: "德国 vs Japan" not flagged, "荷兰 vs Japan" flagged).
- JSON-mode runs against the committed artifact: selector PASS, recap-handoff PASS, internal-daily-trace
  (source) PASS.
- `mvp2_homepage_lifecycle_selector.py validate` PASS at default, editorial, and post-kickoff bases.

**Minor (INFO):** `check_p5b_recap_handoff` selftest's first assertion
(`scan(lc)==[] or all("not routed" not in x ...)`) is near-tautological; its second assertion (non-finished
recap caught) is real, so the guard is not vacuous.

## Check 7 — secret / token leak

`ADMIN_TOKEN_LEAK=false`. `git grep -nE "<REDACTED_ADMIN_TOKEN — per Owner security boundary; value scrubbed 2026-06-16>|ADMIN_API_TOKEN *="` returns only placeholder/doc
references (`<prod token>`, prior review docs describing the search, `llm_draft_verify.py` comment). The
literal token value does not appear in any tracked file. Tracked env files are `.env.example` /
`frontend/.env.example` only, both with `replace_with_…` placeholders — no real values. No `.env` with a
real value is staged.

## Check 8 — win_prob / confidence / send_status

- `send_status: "HOLD"` in `homepageLifecycle.json` (line 172). Confirmed.
- Prediction artifacts: `win_prob` / `confidence` carry the honest string `"unavailable"` (inside
  `model_fields` provenance) — **not** a numeric/fake probability anywhere. **FAKE_DATA=none.**
- **Observation D4 (LOW/INFO, out of P5B scope):** the literal value is the string `"unavailable"`, while
  the artifacts' own `note` says "win_prob/confidence stay null". These files are **not** in the P5B diff
  (pre-existing P8/R2), so not a P5B regression; honesty intent holds. Flag for consistency cleanup.

## Check 9 — diff scope

`git diff main...HEAD --stat`: only `scripts/`, `frontend/src/{data,pages}`, and `docs/` change. **No
backend/, no schema, no cron/scheduler, no .yaml.** Active roles = 1 primary + 2 secondary + 1 latest recap
(cap enforced in code and guard). **SCOPE_EXPANSION=no.**

---

## Defect summary

| ID | Sev | Area | Issue | Hard-rule violation? |
|----|-----|------|-------|----------------------|
| D1 | MEDIUM | selector tooling | `build` overwrites the committed bundled artifact by default with no editorial-basis guard; a stray/wrong-basis build clobbers the noon board (reproduced + restored during review) | No (process/determinism) |
| D2 | LOW | frontend | Lifecycle artifact is bundled, not runtime-fetched → "follows match progress" is deploy-time only; at runtime a kicked-off bundled primary yields a null lead with no rotation | No (safe, not self-healing) |
| D3 | LOW | selector | `seed` admitted as primary-qualified beyond the stated computed/operator_confirmed rule (no live fixture uses it) | No (needs Owner confirm) |
| D4 | LOW/INFO | pre-existing artifacts | win_prob/confidence are string `"unavailable"` vs the note's "null" (not in P5B diff) | No |

## Recommended patches before merge
1. **D1:** gate `build`'s FE write behind an explicit `--write-fe` flag, or add a guard asserting the
   committed bundled `current_time_basis` is the editorial noon for `active_date`.
2. **D3:** Owner-confirm whether `seed` is intentionally primary-eligible; if not, drop it from
   `SOURCE_QUALIFIED`.
3. **D2:** document the deploy-time-only rotation limitation in the gate spec (and consider a runtime
   fallback to the next upcoming when the bundled primary has kicked off).
