# MVP2-P3 Execution Plan

Minimal, focused engineering route. No backend schema, no LLM API, no broad redesign.

## Phase 1 — Product flow audit (DONE)
- Mapped HomePage.tsx → HomeProductLoop.tsx (render order recap-first), dailyFixtures.ts
  (`selectProductLoop` slate-order selection), PredictPage.tsx, RecapDetailPage.tsx (safe
  observation already present, f234531), check_homepage_product_loop.py guard, ShareBlock /
  shareTemplates / refCapture (existing share + ref machinery).
- Confirmed slate: Brazil recap-pending (1489371), Netherlands scheduled (manual, id=null),
  Mexico recap-ready (1489369). 1489371 narrative mode = pre_match_2026_modeling (so /recap
  hits the safe observation branch, never a fake recap).

## Phase 2 — P0 blocker classification (DONE)
See GATE_SPEC.md. Root causes:
1. Render order in HomeProductLoop renders featuredRecap before featuredPrediction.
2. HotspotPrediction enter-CTA gated on `id && renderable` → hidden for the manual hotspot.
3. No copy/share entry on lead cards or detail pages.
4. PredictPage has no manual-fixture fallback (renders "sample not available").
5. Recap card has no observation link when recapReady=false.

## Phase 3 — Minimal implementation
1. `HomeProductLoop.tsx`: render 今日热点预测 BEFORE 昨日热点复盘; prediction enter-CTA always
   shown → `/predict/<id|external_game_id>` labelled 进入战术室; add copy/share entry to both
   featured cards; add 查看赛后观察 link on the recap card when recapReady=false.
2. New `CopyLink.tsx` (clipboard mechanism + flash, ref-compatible URL) and `DetailShareRow.tsx`
   (copy/share + join) — reused, DRY.
3. `PredictPage.tsx`: manual-fixture tactical-room fallback (resolve from runtime manifest by
   id/external_game_id) + share row on detail views.
4. `RecapDetailPage.tsx`: copy/share entry on the safe observation page and recap branches.
5. `check_homepage_product_loop.py`: guard the new invariants (prediction before recap,
   进入战术室, copy/share present) — keep all prior checks + selftest green.

## Phase 4 — Verification
- `npm run build`
- `python3 scripts/check_homepage_product_loop.py` (+ `--selftest`)
- `python3 scripts/check_growth_copy.py`
- `python3 scripts/check_customer_visible_copy.py <live>` (scans DEPLOYED site — pre-deploy here)
- `python3 scripts/check_runtime_daily_fixtures.py --base-url <backend>`

## Phase 5 — Deploy readiness report
Fill FINAL_REPORT.md. Decision READY_TO_DEPLOY / READY_WITH_P1_ISSUES / HOLD. No deploy, no send.
