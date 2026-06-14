# MVP2-P4 Status — Prediction Artifact Recovery

Sprint: Prediction Artifact Recovery (restore the prediction/recap detail chain)
State: READY_TO_DEPLOY · FRONTEND_DEPLOY_PENDING_OPERATOR
Branch: feature/mvp2-p4-prediction-artifact-recovery (base main d7a7735, post-P3)
Send status: HOLD

## Root cause (why detail pages were weak)
Rich prediction fields (main_lean / scoreline_view / risk_level / risk_factors / tactical_read)
live ONLY in bundled `ProductNarrative` JSONs keyed by numeric fixture id. The 2026-06-14 daily
hotspot Netherlands vs Japan is a MANUAL fixture (id=null, kickoffUtc=null, renderable=false) with
no narrative, so `/predict/manual:Nether-Japan-20260614` resolved nothing → P3's generic shell.
No real data is ingested for this fixture (no kickoff/lineups/Elo) → numeric calls cannot be
produced honestly.

## Recovery
- Prediction Artifact for Netherlands vs Japan: fixture identity + per-locale pre-match read
  (modeling_focus / tactical_matchup / risk_variables / 30-min checklist + risk_note + operator
  share/join). Numeric direction/score/confidence = null → shown as 方向待临场确认 (NOT invented).
- Observation Artifact for Brazil 1489371: RECOVERED from the real bundled pre-match narrative
  (lean 偏向巴西, reference band includes 1-1) + the actual score 1-1 → receipt + partial-read
  assessment + calibration focus. recap_ready=false (no fake recap).

## Compliance fix folded in
P3's `predWhy` homepage/predict copy shipped 模型 (zh) / mô hình (vi) — banned customer-visible
de-model words now live on the deployed bundle (index-pvsjX_SJ.js). Fixed to 建模判断 / phân tích.
Live visible-copy scan FAILS until this is deployed; local build scan PASSES 21/21.

## Verification (local build)
build PASS (index-OCJTO5Cc.js) · prediction artifact guard PASS + selftest 8/8 · growth copy PASS ·
homepage loop PASS · runtime daily-fixtures PASS (1 warn active_hero null) · customer-visible scan
21/21 PASS against the LOCAL build (vite preview) · new surfaces headless-verified:
/predict/manual:Nether-Japan-20260614 (artifact room, all tokens, 模型=0, my Han=0) and
/recap/1489371 (receipt, 1-1, 昨日主推回执, 赛后校准, 完整复盘确认后开放, 复制/分享, 加入情报群, my Han=0).

## Next action
Operator deploys this branch to worldcup2026-izid (frontend only); then live re-verify the visible
scan + the two detail surfaces. No backend, no upload, no send.

Last updated: 2026-06-14 (engineering, MVP2-P4 thread)
