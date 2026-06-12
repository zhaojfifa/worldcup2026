# MVP-2 Deploy Gate Closure Note (2026-06-12)

> Owner verdict: Deploy Gate CLEARED on Product Closure P1. This note records the verified live
> state. One follow-up deploy is pending (vi screenshot_line fact fix, see §4).

## 1. Verified live state (2026-06-12 ~04:16 UTC)

| Item | Value |
|---|---|
| Live frontend | https://worldcup2026-izid.onrender.com |
| Live bundle asset | `assets/index-uZpVXhZZ.js` |
| P1 marker counts in live bundle | 俅哥强判断 ×2 · 外部预期偏向巴西 ×1 · 俅哥复盘档案 ×1 · 赛前看方向，临场看变量 ×2 (carry: 比分被红牌放大 ×6) |
| Live visible-copy scan | **18/18 PASS** (zh/vi/my × 6 surfaces; betting/odds/handicap/bookmaker + model/process/missing/source/audit leakage all banned in the scanner) |
| Deep links (hard load) | `/` `/predict/1489371` `/recap/1489369` `/recap/855737` `/recap/979139` → all **200** (SPA rewrite active) |
| Branch HEAD at verification | `9aff21e` (docs-only audit on accepted `4f7ee72`) |
| Track B runtime | **absent** (grep: zero referral/reward/campaign/recharge/commission/payout in backend+frontend) |
| Auto-send | none exists; queue mark-sent requires channel+group+screenshot |
| Remaining send gate | per-fixture **Owner GO → queue approve → manual send → mark-sent** |

## 2. What is live
Product Closure P1: home active-2026 loop (main match → strong calls → 30-min rescore hook →
1489369 recap anchor → join CTA; WC2022 archived), /predict strong-judgment card with customer-safe
外部预期 projection, hardened visible scanner.

## 3. Operational windows (1489371 Brazil vs Morocco)
T-2h status check 2026-06-13 20:00 UTC · T-90 watch 20:30 UTC · kickoff sweep 22:00 UTC ·
A4 recap from ~2026-06-14 00:45 UTC. Official XI only; lineups=0 = blocked_by_time; customer
surface keeps conditional 锋线核心是否首发 until the official XI.

## 4. Post-closure fact fix (pending one deploy)
Deploy verification of the trial package exposed a REAL content bug: the vi 1489369 recap
`screenshot_line` claimed BOTH goals came against 10 men (the 9' opener was 11v11). Fixed
pipeline-level: new guard rule (all-goals-with-man-advantage claim vs frame facts), vi regenerated
guard-clean (run r20260612T0432Z-recap, supersede), re-bundled, local scan 18/18. The corrected vi
line reaches live on the **next operator deploy**; until then the live vi recap-anchor line carries
the old wording (zh/my unaffected, all guard gates pass).
