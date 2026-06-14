# MVP2-P3 Implementation Log

## 2026-06-14 — sprint open
Action: created p3 state directory + STATUS/PRODUCT_FLOW/EXECUTION_PLAN/GATE_SPEC, branch
  feature/mvp2-p3-hotspot-prediction-first off main f234531. Completed Phase 1 audit + Phase 2
  P0 classification.
Files changed: docs/mvp2_product/p3_hotspot_prediction_first/*.md (new)
Reason: Owner mandate — persistent state files before implementation.
Checks: n/a (docs)
Result: STATUS/PRODUCT_FLOW/EXECUTION_PLAN/GATE_SPEC exist → implementation unblocked.
Next: Phase 3 implementation.

## 2026-06-14 — Phase 3 implementation
Action: reordered the homepage funnel (prediction first), added always-on tactical-room CTA +
  copy/share to the lead card, added a safe-observation link on the recap card, built the
  /predict manual-fixture fallback tactical room, and added copy/share+join to predict & recap
  detail branches. New shared CopyLink + DetailShareRow components (DRY). Guard extended.
Files changed:
  - frontend/src/components/HomeProductLoop.tsx (order: HotspotPrediction before HotspotRecap;
    进入战术室 CTA always shown → /predict/<id|external_game_id>; copyShare/viewObs labels;
    CopyLink on both featured cards; 查看赛后观察 link when recapReady=false)
  - frontend/src/pages/HomePage.tsx (loop-order comment)
  - frontend/src/components/CopyLink.tsx (NEW — clipboard + flash, ref-compatible URL)
  - frontend/src/components/DetailShareRow.tsx (NEW — copy/share + join for detail pages)
  - frontend/src/pages/PredictPage.tsx (manual-fixture fallback tactical room from runtime
    manifest; DetailShareRow on main/frozen/fallback views)
  - frontend/src/pages/RecapDetailPage.tsx (CopyLink on safe observation; DetailShareRow on
    recap branches)
  - scripts/check_homepage_product_loop.py (checks 8/9: prediction-before-recap order,
    进入战术室 + CopyLink present; selftest 13/13)
Reason: Owner P3 — hotspot prediction must always be first; today's hotspot must never be buried;
  detail routes must work + be shareable without a full narrative; no fake recap.
Checks: build PASS (tsc -b && vite build, index-CBq4zNKh.js) · homepage loop guard PASS +
  selftest 13/13 · growth copy PASS (18 files) · runtime daily-fixtures PASS (1 warn: active_hero
  null — expected, today's hotspot is a manual fixture with no narrative) · customer-visible copy
  PASS 21/21 on the LIVE deployed site (validates the OLD bundle; new bundle not yet deployed).
Result: all gates green at source + build level. P0-1..P0-6 satisfied.
Next: Phase 5 — fill FINAL_REPORT, commit (no deploy, no send).
