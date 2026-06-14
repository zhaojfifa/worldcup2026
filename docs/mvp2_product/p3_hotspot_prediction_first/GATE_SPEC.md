# MVP2-P3 Gate Spec

## P0 gates (all must pass to deploy)

1. Homepage lead block is **今日热点预测** (renders before 昨日热点复盘).
2. Netherlands vs Japan lead card has: **进入战术室** · **加入临场情报群** · **复制/分享入口**.
3. **Brazil 1-1 Morocco** appears SECOND as 昨日热点复盘 / 赛后观察 (links to safe observation).
4. `/predict/:fixtureId` for today's hotspot works even without a full generated narrative
   (lightweight tactical-room fallback, not blank).
5. `/recap/:fixtureId` for Brazil works as a safe observation page when `recapReady=false`.
6. Prediction detail and recap detail both include share/copy AND a join CTA.
7. No fake recap (查看复盘 only when recapReady=true; no fabricated score).
8. No internal generation wording (复盘生成中 / 待生成复盘 / 生成中 / 自动生成 / AI 正在生成).
9. No betting / trading vocabulary (赔率/盘口/下注/投注/让球/跟单/odds/handicap/kèo/...).
10. No auto-send, no auto-recap, no external LLM call.

## Automated coverage
- `check_homepage_product_loop.py` enforces gates 1, 2 (进入战术室 + copy/share marker),
  3 (Brazil first finished, Mexico secondary), 7, 8, 9, and prediction-before-recap order.
- `check_customer_visible_copy.py` enforces 8/9 on the live DOM (deployed site).
- `npm run build` enforces the fallbacks compile and render.

## P1 deferred (NOT gating)
richer tactical narrative · advanced model visualization · automated LLM generation ·
share-card visual polish · language polish · scoring/ranking automation.

## Send gate
Send remains HOLD. No channel GO until Owner explicitly says:
`GO <channel> <ambassador-code> <fixture>`.
