# P7 — OPERATIONS_RECOVERY_SPEC

> The operator workflow, tied to the SELECTED HOTSPOT, with the existing tools and the compliance floor.
> Nothing here auto-sends. All sends are manual, one channel, on explicit Owner per-channel GO.

## What link to share before the match
- Tactical room: `/predict/<fixture_key>?ref=<CODE>` (e.g. `/predict/manual%3ANether-Japan-20260614?ref=QG-TEST1`).
- Share card: `/share/fixture/<fixture_key>?ref=<CODE>&lang=<zh|vi|my>` (renders the strong call + QR → `/join?ref=<CODE>`).
- The card/link MUST resolve to the selected hotspot's artifact (P0 wiring ensures the lead == selected_hotspot).

## What copy to send before the match
- The lifecycle-gated send-kit: `mvp2_growth_cli.py package today --fixture <key> --lang <l> --ref <CODE>` →
  `docs/data_audit/mvp2_growth_packages/today_<key>_<l>_<CODE>.md` (paste-ready 俅哥主看 / 主比分 / 备选 / 冷门风险 /
  最大变量 / why + group link line). Replace ONLY `[群链接由运营填写]`. Copy verbatim; no manual judgement rewrite.
- The kit is REFUSED automatically if the lifecycle gate says the pre-match window is closed (proven:
  `today_1489371_zh_QG-TEST1.md` = "REFUSED — DO NOT SEND" because 1489371 finished).

## What to send at T-30
- The T-30 slot copy (P0: the artifact's `thirty_minute_checklist` framed as "开球前 30 分钟，首发出来后群内更新"; P1:
  the generated rescore update once lineups drop). If no confirmed update exists, send the honest pending line
  (方向待临场确认 / 比分待开球前 30 分钟确认) — never fabricate a final call.
- Manual, in the same channel; the group message IS the T-30 product moment.

## What to send after full time
- The observation receipt link `/recap/<fixture_key>?ref=<CODE>` + the recap send-kit
  (`mvp2_growth_cli.py package recap --fixture <key> …`). Content = pre-match call → actual → 部分命中/偏差原因 →
  赛后校准关注 → 下一场影响 → 完整复盘确认后开放. No fake recap; `recap_ready` stays false until a real recap exists.
- (Fix the CLI recap branch so the "next match" hook is not the stale hardcoded "Brazil vs Morocco".)

## What to show in the internal page (`/internal/daily`, proposed)
Selected hotspot · artifact readiness (exists / guard-pass / confirmed-not-pending) · T-30 status · recap status ·
per-lang send-kit + share-card links · which ambassador codes exist in prod · manifest freshness. Read-only; never sends.

## What is forbidden
No auto-send / bots / schedulers / bulk-forward · no betting/odds/盘口/投注/竞猜/跟单/串关/让球/大小球 (zh) and the
vi/my/en equivalents · no win-guarantee · no commission/payout/recharge/withdrawal (提现 only inside 不可提现) · no agent
hierarchy · no process/model leakage (模型/sha256/guard/mock) in customer copy · no fake recap · no invented score/probability
· no send after kickoff (pre-match card freezes) · no send without explicit Owner per-channel GO.

## How ref codes fit
Per-lang default codes live in `shareTemplates.ts`: `{zh:QG-TEST1, vi:TT-VN88, my:FO-MM21}`. Every share link/card/QR is
stamped `?ref=<stored ref | DEFAULT_REF>`; `/join?ref=<CODE>` records an attention-only join-intent. Attribution is
channel/code level, never per-user; rewards are MTC platform points, manual-review, capped (100/day, 1000/month), no money
fields exist. The three codes must be created in prod (first-send Gate 1) before any real attribution; engineering holds no
prod token.

## Current send status
HOLD. First-send gates: Gate 1 (create prod codes) + Gate 2 (smoke) + Gate 3 (1489371 LIVE/FT lifecycle) + Gate 7
(Owner per-channel GO). Per the runbook, first controlled send = `zh_internal_group` / fixture 1489371 / ref QG-TEST1,
verbatim, one channel — only on Owner GO. (See `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md`.)
