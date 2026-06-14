# MVP2-P5b StrongCopy Final Recovery — Final Report

1. **Overall decision: READY_TO_DEPLOY** (frontend-only). Send HOLD. Screenshots confirm.

2. **Branch / commit:** `feature/mvp2-p5b-strongcopy-final-recovery` (base 20ee7c9).

3. **Reference branch findings (feature/mvp2-growth-p1-1c-strongcopy):** the strong expression
   is `StrongCallCard` (俅哥强判断 / 主比分+备选 / 冷门风险 / 最大变量 / 为什么 / 外部预期 / T-30 + ShareBlock)
   driven by `buildStrongCall`. P5 had already re-wired the artifact INTO that projection/UI — the
   gap was DATA: the artifact carried null numerics, so the page showed weak pending labels. P5b fills
   the artifacts with the Owner-confirmed strong call (no engineering invention) and adds the deviation
   line; the same strong UI now renders real content.

4. **Prediction page visual result** — `docs/qa_screenshots/mvp2_p5b/predict_manual_zh.png`:
   strong direction (赛前倾向荷兰，但冷门风险不低) ✓ · main score 2-1 ✓ · backup 1-1 / 2-2 ✓ ·
   risk 中高 ✓ · 为什么 ✓ · external expectation (公开预测倾向偏向荷兰…) ✓ · T-30 ✓ ·
   share/copy/join (复制情报链 / 复制分享文案 / 查看分享卡 / 加入临场情报群) ✓. No weak default, no
   invented probability.

5. **Recap page visual result** — `docs/qa_screenshots/mvp2_p5b/recap_1489371_zh.png`:
   昨日主推回执 ✓ · 赛前主推 偏向巴西 主比分参考 2-1 备选含 1-1 ✓ · 实际比分 1-1 ✓ · 部分命中 ✓ ·
   偏差原因 ✓ · 赛后校准关注 ✓ · 下一场影响 ✓ · 完整复盘确认后开放 ✓ · 复制/分享/加入情报群看赛后观察 ✓.
   No fake full recap.

6. **Share-card result** — `share_fixture_zh.png` (2-1 / 备选 / 中高 / 最大变量 / 公开预测倾向 / QR +
   ref=QG-TEST1) and `share_recap_zh.png` (Brazil 1-1 Morocco / 昨日主推回执 / 部分命中 / QR). Both
   render, no blank "—".

7. **Verification:** build PASS · check_prediction_artifact PASS + selftest 8/8 · check_growth_copy
   PASS (23) · check_homepage_product_loop PASS · customer-visible 21/21 PASS (local) · headless:
   new surfaces banned-words=0 (模型/赔率/生成中…), my Han=0 · 4 screenshots above.

8. **Remaining P1 only:** daily artifact scaffolder CLI; real LLM ProductNarrative daily generation;
   richer share-card visuals; RescoreBlock/free-vs-full for artifacts; language polish.

9. **Deploy instruction (if accepted):** frontend only — worldcup2026-izid, this branch after merge to
   main. Root `frontend`, Build `npm install && npm run build`, Publish `dist`. No backend/schema/upload.

10. **Send status: HOLD.**

## Owner Harness-X questions — answered
- Does /predict look like the old strongcopy product again? **YES** (predict_manual_zh.png).
- Score call + backup score? **YES** — 2-1, backup 1-1 / 2-2.
- Risk, why, external expectation, T-30? **YES** — 中高 · 为什么 · 公开预测倾向 · T-30.
- Share/copy/join exposed? **YES** — 复制情报链 / 复制分享文案 / 查看分享卡 / 加入临场情报群.
- /recap reads like a trust receipt? **YES** (recap_1489371_zh.png) — receipt → actual → partial hit
  → deviation → calibration → next impact.
- Any fake recap or forbidden vocabulary? **NO** — recap_ready=false (完整复盘确认后开放); banned-words=0.
