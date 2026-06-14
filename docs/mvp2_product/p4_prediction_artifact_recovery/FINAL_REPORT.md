# MVP2-P4 Final Report — Prediction Artifact Recovery

1. **Overall decision: READY_TO_DEPLOY** (frontend-only). Send HOLD.

2. **Root cause:** rich prediction fields live only in bundled `ProductNarrative` JSONs keyed by
   numeric id; the manual daily hotspot (Netherlands vs Japan, id=null) resolved none, so /predict
   showed a generic shell and /recap had no recovered receipt. No data is ingested for this fixture,
   so numeric calls cannot be produced honestly.

3. **Artifact recovery (files):**
   - frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json (+ audit mirror
     docs/data_audit/mvp2_predictions/prediction_artifact_20260614_netherlands_japan.json)
   - frontend/src/data/predictionArtifacts/observation_1489371.json (+ audit mirror
     docs/data_audit/mvp2_predictions/observation_artifact_1489371_brazil_morocco.json)
   - loader frontend/src/data/predictionArtifacts.ts; views ArtifactTacticalRoom.tsx, ObservationReceipt.tsx

4. **Route behavior:** homepage 今日热点预测 → `/predict/<fixture_key>` resolves: (1) bundled rich
   narrative → (2) Prediction Artifact (rich tactical room: identity + direction/score/confidence/
   risk + 建模关注 + 战术对位 + 风险变量 + 开球前 30 分钟 + 复制/分享 + 加入临场情报群) → (3) generic
   fallback. `/recap/1489371` resolves the Observation Artifact (Brazil 1-1 Morocco · 昨日主推回执 ·
   pre-match call → actual 1-1 → partial-read assessment · 赛后校准 · 完整复盘确认后开放 · 复制/分享 ·
   加入情报群), never a fake recap. Share/copy + join on both.

5. **P0 fixed:** /predict manual hotspot is artifact-level not generic; /recap/1489371 is a recovered
   receipt; numerics stay 方向待临场确认 (no invented score); no fake recap; share/copy + join on both
   detail pages; de-model regression (模型/mô hình) removed from homepage + predict copy.

6. **P1 deferred:** real LLM-generated tactical narrative for the manual hotspot (needs ingested
   data/lineups); confirmed numeric win-prob/score (needs a model run); richer share-card visuals;
   automated artifact generation; language polish.

7. **Verification:** build PASS (local index-OCJTO5Cc.js) · check_prediction_artifact PASS + selftest
   8/8 · check_growth_copy PASS · check_homepage_product_loop PASS · check_runtime_daily_fixtures
   PASS (1 warn active_hero null) · check_customer_visible_copy 21/21 PASS on the LOCAL build · new
   surfaces headless-verified (tokens present, 模型=0, my Han=0). NOTE: the same scan against the LIVE
   deployed site FAILS — the deployed bundle is P3 (index-pvsjX_SJ.js) which carries the de-model
   regression; this P4 build fixes it. Re-run after deploy.

8. **Deploy:** frontend only — worldcup2026-izid, this branch HEAD (after merge to main). Root
   `frontend`, Build `npm install && npm run build`, Publish `dist`. No backend, no schema, no upload.

9. **Send status: HOLD.** No send, no auto-send, no channel GO until Owner says
   `GO <channel> <ambassador-code> <fixture>`.
