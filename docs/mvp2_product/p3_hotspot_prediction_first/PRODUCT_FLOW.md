# MVP2-P3 Product Flow

The product is an AI football-intelligence funnel around ONE daily hotspot:

```
今日热点预测 (homepage lead)
  → 战术室 / 预测详情 (/predict/:id)
  → 开球前 30 分钟修正
  → 复制 / 分享 (operator forwarding, ref links)
  → 加入情报群 (/community, /join)
  → 同一场比赛的赛后复盘 / 观察 (/recap/:id)
  → 下一个每日热点
```

Homepage is only the funnel entrance. Prediction detail and recap detail are the
trust-building pages.

## 1. Homepage role (entrance)
- Lead with **今日热点预测** (today's hotspot), ABOVE 昨日热点复盘.
- Lead card shows clear CTA into the tactical room, a copy/share entry, and a join CTA.
- Yesterday's hotspot recap is SECOND (trust receipt, not the lead hook).
- Today's schedule and other recaps are secondary, lightweight.
- Order is editorial (slate order via `selectProductLoop`), never a hardcoded popularity rank.

## 2. Prediction detail / tactical room (`/predict/:fixtureId`)
- Never blank. If a full LLM narrative exists, render it (existing ProductPredictView).
- If no full narrative exists (manual fixture, id=null), render a **lightweight tactical-room
  fallback** from the manifest fixture/team data: 今日热点预测 label, match title, kickoff/status,
  今日建模关注 (analysis variables), 风险变量, 开球前 30 分钟修正 checklist, join CTA, copy/share.
- No invented score, no invented data source, no fake certainty.

## 3. Recap detail / post-match observation (`/recap/:fixtureId`)
- Trust receipt: predicted match → actual result → calibration focus.
- If `recapReady=false`: **safe observation page** (actual score, yesterday-hotspot receipt,
  比赛已结束 · 赛后校准中, calibration focus, full recap not yet confirmed, join CTA, copy/share).
- If `recapReady=true`: full recap.
- Never a fake recap; never internal generation wording.

## 4. Share / operator forwarding
- Operator can copy/forward prediction and recap/observation links.
- Links are ref-compatible (`?ref=` via shareTemplates.shareLink), first-touch attribution only.
- No auto-send. No dedicated complex share system required — copy the detail URL (ref-compatible).

## 5. Join / group conversion
- Every lead card and detail page exposes a join CTA → /community (records join-intent against
  the stored ref). The growth CTA is tied to the lead product promise (临场修正 + 赛后校准).

## 6. Daily refresh role
- Operator picks today's hotspot (first scheduled in the slate), keeps/creates its tactical room.
- After the match, the SAME fixture becomes the recap candidate (first finished in the slate).
- Operator picks the next hotspot. The frontend renders the confirmed slate order; it does not rank.
