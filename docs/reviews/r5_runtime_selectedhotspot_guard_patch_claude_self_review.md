# R5 Follow-up · Claude Self-Review — Runtime-selectedHotspot-aware R2a + guards

Verdict: **OPERATE** — the two formerly-false-failing guards now PASS under runtime-first behavior; R2a
made runtime-selectedHotspot-aware (ships on next deploy; anchor approach holds live until then). No
product/UI change.

## Problem
After R4/R5 activated runtime content, some checks still read the BUNDLED selectedHotspot/lifecycle as the
"frontend source of truth" → false failures on the live 06-16 runtime state:
- check_live_source_consistency: compared backend 06-16 vs bundled selectedHotspot 06-15.
- check_p5a_homepage_content_quality: looked up the bundled lifecycle primary (Belgium) copy on a France page.
- R2a (dailyFixtures.ts) acceptance anchored on the bundled 06-15 selectedHotspot (needed the anchor trick).

## Fix (minimum change; no UI/product/schema change)
1. `scripts/check_live_source_consistency.py` — resolves the ACTIVE selectedHotspot from the backend
   `/api/v1/runtime-content` (stored + fresh + has selectedHotspot); compares backend slate date vs the
   RUNTIME content date; bundled selectedHotspot is the fallback only. Prints `sel_source=runtime|bundled`.
2. `scripts/check_p5a_homepage_content_quality.py` — adds `--backend-url`; when runtime content is active it
   takes the primary fixture + its copy_v2 from the runtime package (not the bundled artifact) and inspects
   the LIVE DOM; bundled lifecycle/artifacts are the fallback. Prints `src=runtime|bundled`.
3. `frontend/src/data/dailyFixtures.ts` — `bootstrapRuntime` now fetches the runtime CONTENT package FIRST,
   derives the runtime selectedHotspot, and passes it to `fetchDailyManifest(runtimeSel)` so R2a's
   `backendAcceptable` accepts a fresh runtime slate on its OWN selection (no bundled-anchor trick). Bundled
   selectedHotspot remains the fallback anchor when runtime content is absent/stale/date-mismatched. The
   no-mixed-date invariant is preserved (runtime content used only when fresh AND date == effective date).
4. `scripts/check_r4_no_mixed_date_runtime.py` — updated source assertions to the new bootstrap (rcFresh &&
   dateMatch) + added a check that the runtime selectedHotspot anchors R2a.

## Live results (06-16, France primary, bundle index-BsmXWXHz.js unchanged)
- check_live_source_consistency PASS (sel_source=runtime, backend_date=active_date=2026-06-16, primary 1489383).
- check_p5a_homepage_content_quality PASS (src=runtime).
- R4 guards PASS (runtime_content_cutover · frontend_runtime_first · no_frontend_deploy_required ·
  no_mixed_date_runtime 6/6 incl. the new R2a-anchor check).
- P5A predict/recap/share PASS · customer-visible PASS. Homepage live = France primary, Iran-NZ recap.

## Source-of-truth behavior
Runtime content active+valid → selectedHotspot + lifecycle + guards resolve from runtime. Runtime missing/
stale/invalid/date-mismatched → bundled selectedHotspot/lifecycle fallback. No mixed dates.

## Boundaries
No CSS/layout/copy/section change; no backend schema change; no env/token committed; no auto-send; send HOLD.
The frontend R2a change activates on the next deploy (no daily-content deploy needed thereafter); the guard
fixes are Python and active immediately.

## Codex independent review (PASS_WITH_PATCHES) — disposition
Codex PASS_WITH_PATCHES; confirmations: DIFF_SCOPE_OK=yes · RUNTIME_SELECTEDHOTSPOT_SOURCE_OF_TRUTH=yes ·
BUNDLED_FALLBACK_ONLY=yes · CONSISTENCY_GUARD_FIXED=yes · HOMEPAGE_QUALITY_GUARD_FIXED=yes · R2A_RUNTIME_AWARE=yes ·
NO_MIXED_DATE_PRESERVED=yes · NO_PRODUCT_UI_REDESIGN=yes · NO_BACKEND_SCHEMA_CHANGE=yes · FAKE_DATA=none ·
AUTO_SEND=none · SEND_STATUS=HOLD · ADMIN_TOKEN_LEAK=false · BUILD=pass. Codex independently verified the
runtime-aware guards PASS live (sel_source/src=runtime), the bogus-backend fallback is graceful (no crash),
the R2a anchor logic + no-mixed-date invariant, and the live DOM (France primary, Iran recap, bundle unchanged).
- D1 (LOW): Codex saw a live check_customer_visible_copy FAIL on /join persona naming. RESOLVED as a
  TRANSIENT: /join is untouched by this branch, and a clean re-run is 21/21 PASS (incl /join zh/vi/my) —
  a headless-Chrome cold-start render hiccup, not a regression. The self-review's "customer-visible PASS"
  is accurate.
Ref: docs/reviews/codex_r5_runtime_selectedhotspot_guard_patch_review_20260616.md
