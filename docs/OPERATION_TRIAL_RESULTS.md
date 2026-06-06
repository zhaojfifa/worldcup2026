# Giành Cup · Operation Trial Results (Small-Traffic)

_Version: MVP v0.7 · Created: 2026-06-06 · Status: **PENDING — awaiting operator setup**_

Records the real small-traffic trial dispatch + feedback. **No fabricated links, no
fabricated feedback** — every field below is filled by the operator after real execution.

Gate (from `docs/ACCELERATED_MVP_REVIEW.md`): trial is **GO WITH CONDITIONS** — blocked
only on configuring ≥1 `active` community channel (Zalo first).

---

## Current blocker status (2026-06-06 07:36 UTC)

| Channel | Status | public_url |
|---------|--------|------------|
| zalo | `coming_soon` | `null` |
| telegram | `coming_soon` | `null` |
| facebook | `coming_soon` | `null` |
| tiktok | `coming_soon` | `null` |

→ **No active channel. No real link / test group provided yet. Trial NOT dispatched.**

---

## Operator runbook (run when a real test-group link exists)

All admin calls run in **Render Shell** with `$ADMIN_API_TOKEN` (never printed/committed).

**Step 1 — configure Zalo `active`** (replace `TEST_GROUP_URL` with the real link):
```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/social/channels/upsert \
  -H "Content-Type: application/json" \
  -H "x-admin-token: $ADMIN_API_TOKEN" \
  -d '{"channel_name":"zalo","display_name":"Zalo","status":"active","public_url":"TEST_GROUP_URL","description":"越南球迷主阵地","locale":"vi","is_enabled":true,"sort_order":1}'
```

**Step 2 — verify** (expect `zalo status=active`, `public_url` non-null):
```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/social/channels
```

**Step 3 — verify click heat** (public, no token):
```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/events/track \
  -H "Content-Type: application/json" \
  -d '{"event_type":"click_social_channel","channel_name":"zalo","match_id":1}'
curl https://worldcup2026-api-71n6.onrender.com/api/v1/community/heat
```
Expected: `total_interactions` +1, match1 +1, `updated_at` refreshed.

**Step 4 — dispatch** the 3 messages to the test group:
- **If the Zalo test group is mostly Vietnamese users → use `docs/OPERATION_TRIAL_MESSAGES_VI.md`** (vi copy).
- The Chinese `docs/OPERATION_TRIAL_MESSAGES.md` is for **internal reference** only.
- **Before sending, manually re-check forbidden wording** in both zh and vi
  (vi: `chắc thắng` / `đảm bảo thắng` / `cá cược` / `đặt cược` / `kiếm tiền` / `lợi nhuận chắc chắn`).

**Step 5 — record** results in the tables below.

---

## Trial dispatch records (fill after real dispatch)

| Field | Msg 1 (三场速览) | Msg 2 (爆冷TOP1) | Msg 3 (临场修正) |
|-------|------------------|------------------|------------------|
| 发布时间 | | | |
| 发布渠道 | | | |
| 文案编号 | 1 | 2 | 3 |
| 点击数 | | | |
| 社群入口点击 | | | |
| 用户反馈 | | | |
| 是否有人询问完整分析 | | | |
| 是否有人关注 MTC / 连胜 / 排行榜 | | | |
| 合规问题 | | | |

## Summary (fill after trial)

- **Most attractive message:** _(record)_
- **Total clicks / channel-entry clicks:** _(record)_
- **Notable user feedback:** _(record)_
- **Any compliance issue surfaced:** _(record — must be none; flag immediately if any)_
- **Verdict update:** does this clear the GO WITH CONDITIONS gate? _(record)_

---

## Notes

- Trial uses **seed/mock match data** (`mock_mode=true`) — validates **copy attractiveness +
  community承接**, NOT real model accuracy. Do not advertise hit-rate.
- Heat payload contains **no personal info** (only match_id, team names, counts, channel name).
- If no real link is available, leave this PENDING and do not fabricate. Telegram test group
  is an acceptable alternative to Zalo for clearing the gate.
