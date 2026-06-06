# Giành Cup · Operations Runbook

_Version: Day 7 · Last updated: 2026-06-06_

This document is for **operations staff**, not engineers.
All admin API calls require the `x-admin-token` header set to the `ADMIN_API_TOKEN` value
configured in Render (never written in this document).

---

## 1. Daily Prediction Publishing Flow

### Step 1 — Sync latest fixtures

```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/sync/fixtures \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_ADMIN_API_TOKEN" \
  -d '{}'
```

Expected: `{"synced": <N>, "message": "..."}`

### Step 2 — Refresh predictions for key matches

```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/matches/MATCH_ID/refresh \
  -H "Content-Type: application/json" \
  -d '{}'
```

Replace `MATCH_ID` with the numeric match ID from `/api/v1/matches`.

### Step 3 — Sync actual results from API-FOOTBALL

```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/sync/results \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_ADMIN_API_TOKEN" \
  -d '{"league_id":1,"season":2026}'
```

Body accepts only optional `league_id` and `season` (defaults to the configured
`WC_LEAGUE_ID` / `WC_SEASON` when omitted). The endpoint pulls **finished fixtures
from API-FOOTBALL**, upserts `MatchResult`, and automatically runs prediction
settlement.

- **Do NOT pass scores manually** — there is no `match_id` / `home_score` /
  `away_score` field. Results come from API-FOOTBALL finished fixtures only.
- If `API_FOOTBALL_KEY` is unset, or there are no finished fixtures, the call
  degrades gracefully and returns `inserted` / `updated` / `settled` as `0`.
- This is a **write operation** — the `x-admin-token` header is required.

### Step 4 — Settle fan challenges after result is confirmed

```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/challenges/settle \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_ADMIN_API_TOKEN" \
  -d '{"challenge_id":1,"user_id":1,"actual_result":"A","selected_option":"A"}'
```

**Option values** (`selected_option` and `actual_result` use the same set):

| Value | Meaning |
|-------|---------|
| `A` | AI 倾向方向一（主胜偏强 / 略占优 / 主队不败趋势） |
| `B` | AI 倾向方向二（客胜偏强 / 略占优 / 客队不败趋势） |
| `neutral` | 难分胜负，不计入命中 |

**Settlement rules:**
- `selected_option == actual_result` and **not** `neutral` → 命中，`current_streak += 1`，奖励 MTC 积分。
- `selected_option != actual_result` and **not** `neutral` → 未命中，`current_streak` 重置为 0。
- `actual_result == neutral` **或** `selected_option == neutral` → neutral，不改变 streak，不计入命中。

Settlement is idempotent — calling it twice for the same challenge+user pair is safe
(returns "该挑战已结算，未重复计入连胜或积分").

> ⚠️ This is the settlement of a **free fan challenge / streak task** — it is **NOT**
> a cash reward, **NOT** a prize pool, and **NOT** a betting settlement. MTC is
> **platform loyalty points only** (不可提现 · 不可转让 · 不可交易 · 不作为金融资产).

---

## 2. Social Channel Configuration

Channels are configured via the admin API. **Do not hardcode real URLs in source code.**
Use the upsert endpoint to add or update any channel.

### Priority order for Vietnam-first market

1. **Zalo** — primary channel for Vietnamese fans
2. **Telegram** — real-time lineup correction pushes
3. **Facebook** — pre-match analysis & post-match reviews
4. **TikTok** — short-video AI daily highlights

### Upsert a channel

```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/social/channels/upsert \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_ADMIN_API_TOKEN" \
  -d '{
    "channel_name": "zalo",
    "display_name": "Zalo 越南球迷群",
    "description": "每日 AI 情报、临场修正第一时间推送",
    "public_url": "https://zalo.me/YOUR_GROUP_ID",
    "status": "active",
    "locale": "vi",
    "is_enabled": true,
    "sort_order": 1
  }'
```

| Field | Values |
|-------|--------|
| `channel_name` | `zalo` / `telegram` / `facebook` / `tiktok` |
| `status` | `active` (shows link) · `coming_soon` (greyed out) · `disabled` (hidden) |
| `locale` | `vi` (Vietnam) · `zh` (Chinese) · `en` (English) |

### Example: Telegram

```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/social/channels/upsert \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_ADMIN_API_TOKEN" \
  -d '{
    "channel_name": "telegram",
    "display_name": "Telegram 临场情报",
    "description": "首发公布后 30 分钟内 AI 修正观点实时同步",
    "public_url": "https://t.me/YOUR_CHANNEL_NAME",
    "status": "active",
    "locale": "zh",
    "is_enabled": true,
    "sort_order": 2
  }'
```

### Verify channels are live

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/social/channels
```

---

## 3. Performance & Track Record

### Check daily performance

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/performance/daily
```

### Check summary stats

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/performance/summary
```

---

## 4. Fan Streak & Rankings

### Check a user's streak

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/users/USER_ID/streak
```

Expected response (empty-safe for a new user):
```json
{
  "user_id": 1,
  "current_streak": 0,
  "best_streak": 0,
  "mtc_earned": 0,
  "last_participation_date": null,
  "disclaimer": "历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。"
}
```

### Check rankings board

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/rankings
```

Expected response (empty-safe when no settled challenges yet):
```json
{
  "top_users": [],
  "ranking_type": "streak",
  "updated_at": null,
  "disclaimer": "历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。"
}
```

Rankings are sorted by: `current_streak` → `best_streak` → `mtc_earned`.
This is a **streak/points board only — not an earnings board**.

---

## 5. Health Check

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/health
```

Expected fields: `status: "ok"`, `compliance.real_money_betting_enabled: false`,
`compliance.token_withdrawal_enabled: false`.

---

## 6. Content Asset Storage Status

```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/assets/status
```

Expected response (R2 connected, public URL bound):
```json
{
  "r2_configured": true,
  "bucket": "giand-cup-assets",
  "public_base_url_set": true,
  "message": "R2 ready"
}
```

| Field | Meaning |
|-------|---------|
| `r2_configured: true` | R2 bucket connected |
| `public_base_url_set: true` | Public CDN domain bound |
| `public_base_url_set: false` | Public URL not yet bound (bucket still functional) |

---

## 7. Security Notes

- **Never share `ADMIN_API_TOKEN` in plain text** in Slack, docs, or source code.
- All admin routes return `401` if the token is missing or wrong.
- `ENABLE_REAL_MONEY_BETTING` and `ENABLE_TOKEN_WITHDRAWAL` must remain `false` at all times.
- MTC is **platform loyalty points only** — not withdrawable, not transferable, not tradable.
