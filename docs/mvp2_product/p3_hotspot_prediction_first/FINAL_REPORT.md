# MVP2-P3 Final Report

## 1. Overall decision
**READY_TO_DEPLOY** (frontend-only; no backend change). Send remains HOLD.

## 2. Commit hash
Branch `feature/mvp2-p3-hotspot-prediction-first`, HEAD **f5697b9**.
- 182000a docs(product): add P3 hotspot prediction first state files
- f2c593d feat(product): lead homepage with hotspot prediction
- 97f3d55 feat(product): add tactical and observation fallbacks
- f5697b9 test(product): guard hotspot prediction product path

## 3. Files changed
- frontend/src/components/HomeProductLoop.tsx
- frontend/src/pages/HomePage.tsx
- frontend/src/components/CopyLink.tsx (new)
- frontend/src/components/DetailShareRow.tsx (new)
- frontend/src/pages/PredictPage.tsx
- frontend/src/pages/RecapDetailPage.tsx
- scripts/check_homepage_product_loop.py
- docs/mvp2_product/p3_hotspot_prediction_first/*.md (new)

## 4. Product order after fix
Homepage: **1) 今日热点预测 (Netherlands vs Japan)** → 2) 昨日热点复盘 (Brazil 1-1 Morocco,
赛后观察) → 3) 今日赛程 (Germany/Curacao, Ivory Coast/Ecuador, Sweden/Tunisia, Australia/Turkey)
→ 4) 其他复盘 (Mexico 2-0 South Africa) → 5) Growth CTA. Archive WC2022 + mock demo stay folded.
Route flow: lead card → `/predict/<id|external_game_id>` (tactical room or fallback) → 30-min
correction + copy/share + join → `/recap/<id>` observation/recap → next hotspot.

## 5. P0 fixed
- P0-1 homepage lead is 今日热点预测 (renders before 昨日热点复盘).
- P0-2 Netherlands lead card: 进入战术室 + 加入临场情报群 + 复制/分享入口 (CTA no longer gated
  on id/renderable).
- P0-3 Brazil recap is second; 查看赛后观察 links to the safe observation page; recap link copyable.
- P0-4 /predict/<manual fixture> renders a lightweight tactical-room fallback (manifest-resolved,
  analysis/risk variables + 30-min checklist + join + copy/share), never blank, no invented score.
- P0-5 /recap/1489371 (Brazil) is a safe observation page (recapReady=false; narrative mode is
  pre_match, so no fake recap) with copy/share + join.
- P0-6 no fake recap (查看复盘 only when recapReady=true), no generation wording, no betting vocab
  (guard + live visible-copy scan confirm).

## 6. P1 deferred
richer generated tactical narrative · advanced model visualization · automated LLM generation ·
share-card visual polish · language polish · scoring/ranking automation.

## 7. Verification
- `npm run build` — PASS (tsc -b && vite build → index-CBq4zNKh.js).
- `check_homepage_product_loop.py` — PASS; `--selftest` 13/13.
- `check_growth_copy.py` — PASS (18 files).
- `check_runtime_daily_fixtures.py` — PASS (1 warn: active_hero null — expected, today's hotspot
  is a manual fixture with no bundled narrative).
- `check_customer_visible_copy.py <live>` — PASS 21/21. NOTE: this scans the DEPLOYED site, i.e.
  the OLD bundle (P1.5b). The new bundle is not deployed; live re-verify after the operator deploys.

## 8. Deploy instruction
Frontend-only. Operator deploys `feature/mvp2-p3-hotspot-prediction-first` @ f5697b9 (or after
merge to main) to worldcup2026-izid. No backend redeploy needed (runtime daily-fixtures unchanged;
Render SPA rewrite `/* -> /index.html` already required for deep links). After deploy: re-run
`check_customer_visible_copy.py https://worldcup2026-izid.onrender.com` and visually confirm the
homepage order (prediction first) + /predict/<Netherlands> fallback + /recap/1489371 observation
across zh/vi/my.

## 9. Send status
**HOLD.** No send, no auto-send, no channel GO. Sends remain HOLD until Owner explicitly says
`GO <channel> <ambassador-code> <fixture>`.
