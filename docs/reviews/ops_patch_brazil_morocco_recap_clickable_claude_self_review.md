# OPS Patch · Claude Self-Review — Brazil 1-1 Morocco recap clickable + prediction/recap alignment

Verdict: **PASS** (pending Codex independent review + Owner merge/deploy).

## Honest finding first
The core behavior the Owner described as missing was ALREADY working on this branch AND on live
(index-BjSoLp6M.js): the homepage yesterday-recap card already showed a clickable `查看赛后观察` CTA and
`/recap/1489371` already rendered the full OBSERVATION_ONLY receipt (verified by rendered DOM on
https://worldcup2026-izid.onrender.com before this patch). This patch therefore HARDENS and CLARIFIES that
path and adds a regression guard, rather than fixing a dead button. Evidence: live DOM scan returned Brazil/
Morocco/1-1/赛后观察/部分命中/赛前主推/实际比分 on /recap/1489371 and 查看赛后观察 on the homepage.

## What this patch changes (frontend copy/logic only)
- `HomeProductLoop.tsx` HotspotRecap badge now uses the Owner's exact state label
  **比赛已结束 · 赛后观察 / 复盘校准中** (zh; vi/my/en parallels) instead of the generic FROZEN.pending,
  so the finished-but-not-full-recap state reads clearly.
- `OtherRecaps` (Zone 5) hardened: a finished match with a score-only OBSERVATION receipt is now
  CLICKABLE (`查看赛后观察` → /recap/id) instead of a dead 已完赛 chip. `查看复盘` still appears ONLY when a
  real recap exists (recapReady=true). This honours "Do not require recapReady=true for score-only
  observation recap" for the secondary list too.
- No change to the `/recap/:id` page logic (it already routes recapReady=false finished fixtures with an
  observation artifact to `<ObservationReceipt>`), no change to lifecycle selection, no scheduler, no match
  count change, no backend/schema change. Belgium vs Egypt 1-1 correction untouched.

## Required behaviors (all met, screenshot-verified)
1. Homepage recap card clickable — YES (查看赛后观察 button, not disabled).
2. CTA text clear — 查看赛后观察 (Owner-listed option).
3. Click target /recap/1489371 — YES (recapKeyFor → f.id "1489371"; SPA onClick navigate).
4. /recap/1489371 renders OBSERVATION_ONLY — YES (ObservationReceipt).
5. Shows Brazil vs Morocco · final 1-1 · prediction baseline (赛前主推 2-1 / 备选 1-1) · actual 1-1 ·
   result判断 部分命中(PARTIAL) · 看对了什么 · 看错了什么 · 判断修正 · 下一场要带走的 · 来源
   OBSERVATION_ONLY(完整事件数据未接入) — all present.
6. recapReady=true NOT required for the observation page — confirmed.
7/8. No fabricated event data; no full-recap claim (source label says event data missing).
9. Send HOLD — unchanged.

## Prediction/recap alignment
The observation artifact (observation_1489371.json) states pre-match baseline 主比分 2-1 / 备选 1-1, actual
1-1 → 主比分未完全命中、备选/比分区间命中 → 按 PARTIAL 处理. The recap page renders this real baseline (not
invented); homepage recap card and recap page draw from the same observation artifact.

## Compliance
No betting/odds/handicap/probability wording; no fake event/full recap; Belgium vs Egypt remains 1-1
(check_ops_prediction_score_override PASS); no env/secret committed.

## Guards
- NEW `check_ops_brazil_morocco_recap_clickable.py` (selftest 5/5; rendered) PASS.
- check_ops_prediction_score_override (Belgium 1-1) PASS · P5A homepage/recap PASS · P5B recap-handoff/
  no-finished-primary/lifecycle-rendering PASS · growth-copy/content-queue/customer-visible PASS · build PASS.

## Screenshots
docs/qa_screenshots/ops_patch_brazil_morocco_recap_clickable/local/ (01 home recap card clickable + new
state label, 02 observation page, 03 predicted-vs-actual, 04 correction/next-learning, 05 Belgium still 1-1).
