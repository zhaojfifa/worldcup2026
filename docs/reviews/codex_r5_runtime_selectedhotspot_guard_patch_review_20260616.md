# Codex Review — R5 Runtime-selectedHotspot Guard Patch

- Branch: `ops/r5-runtime-selectedhotspot-guard-patch`
- HEAD: `7051fc7` ("fix(r5): runtime-selectedHotspot-aware R2a + consistency/homepage guards")
- Reviewer: Codex (independent adversarial)
- Date: 2026-06-16 (run 06-17)

## Overall verdict: **PASS_WITH_PATCHES**

The three formerly-false-failing guards are now runtime-selectedHotspot-aware and PASS live; the R2a
frontend change is sound and preserves the no-mixed-date invariant; build passes; no UI/product/schema/
backend change; no fake data; no auto-send; send HOLD; no token leak. The only patch needed is a **doc
accuracy fix**: the self-review claims "customer-visible PASS" but the live `check_customer_visible_copy`
currently FAILS on `/join` persona naming (out of this patch's scope — see Check 6). Code is sound.

### Confirmation lines
```
DIFF_SCOPE_OK=yes
RUNTIME_SELECTEDHOTSPOT_SOURCE_OF_TRUTH=yes
BUNDLED_FALLBACK_ONLY=yes
CONSISTENCY_GUARD_FIXED=yes
HOMEPAGE_QUALITY_GUARD_FIXED=yes
R2A_RUNTIME_AWARE=yes
NO_MIXED_DATE_PRESERVED=yes
NO_PRODUCT_UI_REDESIGN=yes
NO_BACKEND_SCHEMA_CHANGE=yes
FAKE_DATA=none
AUTO_SEND=none
SEND_STATUS=HOLD
ADMIN_TOKEN_LEAK=false
BUILD=pass
```

---

## Check 1 — Diff scope
`git diff main...HEAD --stat` touches exactly: `scripts/check_live_source_consistency.py`,
`scripts/check_p5a_homepage_content_quality.py`, `scripts/check_r4_no_mixed_date_runtime.py`,
`frontend/src/data/dailyFixtures.ts` (a DATA file, not a component/page/CSS), the self-review doc, and
2 screenshots + 1 evidence txt under `docs/qa_screenshots/r5_runtime_selectedhotspot_guard_patch/`.
- `git diff main...HEAD -- backend/` = **empty**.
- No frontend component/page/CSS file changed (only `frontend/src/data/dailyFixtures.ts`).
- No schema change.

**DIFF_SCOPE_OK=yes.**

## Check 2 — check_live_source_consistency.py
Source (`scripts/check_live_source_consistency.py:22-37`): fetches `/api/v1/runtime-content`; when
`freshness.stored` AND `stale is not True` AND `selectedHotspot` AND `date` present, it overrides `sel`
with the runtime selectedHotspot (date + fixture_key + home/away) and sets `sel_source="runtime"`; else
the bundled `selectedHotspot.json` is the fallback (`sel_source="bundled"`).

Live run:
```
LIVE SOURCE CONSISTENCY · backend_date=2026-06-16 · active_date=2026-06-16 (sel_source=runtime) · primary=1489383
LIVE SOURCE CONSISTENCY PASS  (exit 0)
```
Matches the required PASS: sel_source=runtime, backend_date=active_date=2026-06-16, primary=1489383.

**CONSISTENCY_GUARD_FIXED=yes.**

## Check 3 — check_p5a_homepage_content_quality.py
Source (`scripts/check_p5a_homepage_content_quality.py:62-92`): with `--backend-url` it fetches
`/api/v1/runtime-content`; when `stored` + not stale + has `predictions`, `src="runtime"` and the primary
fixture + its `copy_v2` are taken from the runtime package (`rlc.primary_prediction.fixture_id` / runtime
`_rcv(rc, fk)`); else the bundled lifecycle/artifact path (`cv()`) is the fallback. It inspects the LIVE
DOM either way.

- Live (runtime): `P5A HOMEPAGE CONTENT QUALITY PASS (... · src=runtime)` exit 0. ✓ required PASS with src=runtime.
- Bogus backend (`--backend-url http://127.0.0.1:1`): falls back gracefully (`src=bundled primary=1489377`),
  **does not crash**, inspects the DOM. It reports FAIL (5) only because the bundled artifact is
  Belgium-Egypt 1489377 (06-15) while the LIVE DOM is serving the **runtime** France slate — an
  environmental mismatch, NOT a code defect. The requested "still PASSES" cannot be observed while the
  live site serves runtime content; the code requirement (graceful bundled fallback, no crash, DOM
  inspected) is met.

**HOMEPAGE_QUALITY_GUARD_FIXED=yes.**

## Check 4 — dailyFixtures.ts R2a change
- `fetchDailyManifest(preferSel?)` (`:137-143`): `const sel = preferSel ?? getSelectedHotspot()` — the
  runtime selectedHotspot anchors `backendAcceptable`'s `containsKey` check when provided; bundled
  `getSelectedHotspot()` remains the fallback anchor.
- `bootstrapRuntime` (`:183-213`): fetches the runtime CONTENT package FIRST (bounded by the Codex-R4 3s
  AbortController, `:188-191`); computes `rcFresh` = stored + not stale + age ≤ 36h + has date + has
  predictions (`:193-196`); derives `runtimeSel` ONLY when `rcFresh && pkg.selectedHotspot` (`:197-199`)
  and passes it to `fetchDailyManifest(runtimeSel)` (`:200`).
- No-mixed-date invariant preserved: runtime content is set ONLY when `rcFresh && dateMatch`
  (`dateMatch = pkg.date === effectiveDate`, `:202-204`); otherwise `setRuntimeContent(null)` (`:206`).
- No new import cycle: `runtimeContent` symbols were already imported (`:12-13`); the new code adds no
  import. `check_r4_frontend_runtime_first --selftest` confirms "runtimeContent module has no import
  statements (no cycle)".
- Build: `cd frontend && npm run build` → **PASS**, bundle `index-3oSlHhzk.js`. This local hash differs
  from the live `index-BsmXWXHz.js`, confirming the frontend change activates only on the NEXT deploy —
  the self-review states this explicitly ("The frontend R2a change activates on the next deploy").

**R2A_RUNTIME_AWARE=yes · NO_MIXED_DATE_PRESERVED=yes · BUILD=pass.**

## Check 5 — R4 guard selftests
```
check_r4_runtime_content_cutover (live)    PASS (stored=True · predictions=1 · send_status=HOLD)
check_r4_frontend_runtime_first --selftest 6/6 PASS
check_r4_no_frontend_deploy_required --selftest 4/4 PASS
check_r4_no_mixed_date_runtime --selftest  6/6 PASS
```
`check_r4_no_mixed_date_runtime` is **non-vacuous**: it splits the real `bootstrapRuntime` source out of
`dailyFixtures.ts` (`:9-11`) and asserts `rcFresh`, `stale`, `setRuntimeContent(null)`, `rcFresh && dateMatch`,
and the new `runtimeSel` + `fetchDailyManifest(runtimeSel)` anchor — all of which match the new bootstrap code.

## Check 6 — Regression
```
check_p5a_predict_content_quality   PASS (exit 0)
check_p5a_recap_content_quality     PASS (exit 0)
check_p5a_share_content_quality     PASS (exit 0)
check_customer_visible_copy         FAIL (exit 1) — /join?lang={zh,vi,my} persona missing
```
**Defect D1 (LOW, out of scope):** `check_customer_visible_copy` FAILS live on `/join` persona naming for
all three locales. This is **not attributable to this patch** — the script is unchanged on this branch,
`/join` is untouched, and the check runs against the currently-deployed bundle (`index-BsmXWXHz.js`, the
prior R4/R5 deploy), not this branch. However, the self-review (`docs/reviews/...self_review.md`) claims
"customer-visible PASS", which is inaccurate against current live state. **Patch:** correct that line in the
self-review and hand the `/join` live persona regression to the operator as a separate item. Does not block
this patch.

## Check 7 — No fake data / compliance
The patch adds no fabricated scores/probabilities (win_prob/confidence untouched; guards only read existing
fields), no betting/odds/handicap wording, no auto-send. Guards only perform GET reads of public live
endpoints; no writes to prod beyond what R5 already did. send_status=HOLD confirmed live by
`check_r4_runtime_content_cutover` and the evidence txt.

**FAKE_DATA=none · AUTO_SEND=none · SEND_STATUS=HOLD.**

## Check 8 — Live state sanity
Live homepage DOM (`_rendered_dom.strip_folds`, `/?lang=zh`): France ×5 / Senegal ×4 in the TODAY-prediction
zone (primary, NOT Belgium); Iran ×2 / New Zealand ×2 in the recap zone. Belgium/Egypt appear ×1 each, only
as a finished match-desk secondary row (`md-row` "Belgium vs Egypt 1 - 1"), not the active prediction. Live
bundle = `index-BsmXWXHz.js` (unchanged) — no frontend deploy was needed for these guard fixes.

## Check 9 — Secret scan
`git grep -lc "<REDACTED_ADMIN_TOKEN — per Owner security boundary; scrubbed 2026-06-16>" -- . ':!*.png'` → exit 1, **no matches** (token VALUE absent from all tracked files
on this branch). Only `.env.example` / `frontend/.env.example` templates are tracked (no real values).
`git diff main...HEAD` introduces no `.env`/token file. `backend/.env` is not tracked. Token scan of the
added evidence txt and self-review doc → no matches.

**ADMIN_TOKEN_LEAK=false.**

---

## Defects
- **D1 (LOW, out of patch scope):** self-review claims "customer-visible PASS" but live
  `check_customer_visible_copy` FAILS on `/join` persona naming (zh/vi/my). Not caused by this branch
  (script + `/join` untouched; runs vs the prior live deploy). Correct the doc line; operator to triage the
  live `/join` regression separately. Non-blocking.
- **Observation (not a defect):** the bundled-path `check_p5a_homepage_content_quality` test reports FAIL
  against a runtime-serving live site — inherent to the current live state, not a code fault. The script
  correctly falls back to bundled and does not crash.
