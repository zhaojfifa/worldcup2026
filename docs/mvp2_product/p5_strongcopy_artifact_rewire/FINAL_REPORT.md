# MVP2-P5 StrongCopy Artifact Rewire — Final Report

1. **Overall decision: READY_TO_DEPLOY** (frontend-only). Send HOLD.

2. **Branch / commit:** `feature/mvp2-p5-strongcopy-artifact-rewire` (base main d542a4c).

3. **What was re-wired from strongcopy (Approach A):** the existing canonical projection
   `growth/strongCallProjection.ts` (`buildStrongCall`) now falls back to a **Prediction Artifact**
   when no `ProductNarrative` exists (new `buildStrongCallFromArtifact`). The narrative path is
   unchanged. The manual hotspot now flows through the SAME strong projection + the same
   `StrongCallCard`/`ShareBlock`/`ShareCardPage` surfaces.

4. **Predict page after fix** (`/predict/manual:Nether-Japan-20260614`): strong tactical room —
   俅哥强判断 · 今日主推判断 · 俅哥主看 (方向待临场确认) · 主比分 / 比分待开球前 30 分钟确认 · 冷门风险 ·
   风险变量 · 最大变量 · 为什么 · 外部预期·公开预测倾向 (safe vocab) · T-30 / 开球前 30 分钟修正 ·
   今日建模关注 · 战术对位 · 复制情报链 · 复制分享文案 · 查看分享卡 (QR) · 加入临场情报群. No invented
   score/probability — nulls render as the pending labels.

5. **Recap page after fix** (`/recap/1489371`): strong observation receipt — Brazil vs Morocco 1-1 ·
   昨日主推回执 · 赛前主推（偏向巴西，参考区间含 1-1）· 实际比分 1-1 · 部分命中 · 赛后校准关注 ·
   下一场影响 · 完整复盘确认后开放 · 复制分享文案 · 查看分享卡 (QR) · 加入情报群看赛后观察. No fake
   recap, no generation wording.

6. **Share/operation after fix:** `shareTemplates.prematchShareCopy` works for the manual hotspot
   (via artifact-aware `buildStrongCall`); `recapShareCopy` falls back to the observation artifact's
   share copy; `ShareBlock` gained `joinLabel`/`joinTo` (artifact join CTAs → /community);
   `ShareCardPage` renders a QR card from the prediction artifact (`/share/fixture/<key>`) and the
   observation artifact (`/share/recap/1489371`) — both previously returned an empty "—". Ref
   tracking preserved (ref-compatible links + recordJoinIntent).

7. **P0 fixed:** P0-1 artifact-backed strong projection; P0-2 strong /predict expression; P0-3 strong
   /recap receipt; P0-4 artifact-aware share layer (copy link / copy share text / QR card / join);
   P0-5 guards (strong tokens + safe external_expectation + artifacts in growth-copy globs).

8. **P1 deferred:** daily artifact scaffolder CLI; real LLM `ProductNarrative` daily generation;
   richer share-card visuals; RescoreBlock/free-vs-full for artifacts; language polish.

9. **Verification:** build PASS · check_prediction_artifact PASS + selftest 8/8 · check_growth_copy
   PASS (23 files) · check_homepage_product_loop PASS · customer-visible 21/21 PASS on the LOCAL
   build · 4 strong surfaces headless-verified (all tokens, QR present, 模型/赔率=0, my Han=0).

10. **Deploy instruction:** frontend only — worldcup2026-izid, this branch (after merge to main).
    Root `frontend`, Build `npm install && npm run build`, Publish `dist`. No backend, no schema,
    no upload. Re-run the live visible scan after deploy.

11. **Send status: HOLD.** No send, no auto-send, no channel GO.
