# Giành Cup · Vietnamese Operation Trial Runbook

_Version: MVP v0.7 · Created: 2026-06-06 · Operator-facing._

Step-by-step runbook to execute the **Vietnamese small-traffic trial** once at least one
`active` community channel (Zalo or Telegram) is configured.

Source copy: `docs/OPERATION_TRIAL_MESSAGES_VI.md` (vi) · `frontend/src/copy/vi.ts`.
Record results in: `docs/OPERATION_TRIAL_RESULTS.md`.

> **Data note:** seed/mock match data (`mock_mode=true`). The trial validates **copy
> attractiveness + community承接**, NOT real prediction accuracy. 不可宣传真实命中率。
> All admin calls run in **Render Shell** with `$ADMIN_API_TOKEN` (never printed/committed).

---

## 1. Pre-conditions (all must be true before dispatch)

- [ ] At least one `active` channel: **Zalo** (preferred) or **Telegram**.
- [ ] That channel's `public_url` is configured (real test-group link).
- [ ] `docs/OPERATION_TRIAL_MESSAGES_VI.md` prepared (3 vi messages). ✅ ready
- [ ] Compliance check passed (zh + vi forbidden-word scan). ✅ ready
- [ ] Operator has done a final manual re-read of the vi copy before sending.

If no real link / test group exists → **do not fabricate**. Stay PENDING.

---

## 2. Configure active channel

Render Shell (Zalo first; replace `TEST_GROUP_URL` with the real link):
```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/social/channels/upsert \
  -H "Content-Type: application/json" \
  -H "x-admin-token: $ADMIN_API_TOKEN" \
  -d '{"channel_name":"zalo","display_name":"Zalo","status":"active","public_url":"TEST_GROUP_URL","description":"越南球迷主阵地","locale":"vi","is_enabled":true,"sort_order":1}'
```

Verify (expect `zalo status=active`, `public_url` non-null):
```bash
curl https://worldcup2026-api-71n6.onrender.com/api/v1/social/channels
```

> Telegram alternative: same call with `"channel_name":"telegram"`, `"sort_order":2`.
> Facebook / TikTok stay `coming_soon`. **Never hardcode links in source.**

---

## 3. Dispatch order

Send the 3 vi messages from `docs/OPERATION_TRIAL_MESSAGES_VI.md` in this order:

1. **A. 今日 AI 三场速览** — `🔥 3 trận AI đáng chú ý hôm nay`
2. **B. 爆冷风险：摩洛哥 vs 法国** — `⚠️ Rủi ro bất ngờ số 1: Morocco vs Pháp`
3. **C. 临场修正：巴西 vs 阿根廷** — `📡 Cập nhật sát giờ · Brazil vs Argentina`

> Spacing suggestion: A first (broad hook), B as risk-driven follow-up, C as the
> "why join" live-correction proof. Leave time between each to read engagement.

---

## 4. Per-message record fields (fill into OPERATION_TRIAL_RESULTS.md)

For each message A / B / C:

| Field | 中文 |
|-------|------|
| Publish time | 发布时间 |
| Channel | 发布渠道 |
| Message id (A/B/C) | 文案编号 |
| Views | 浏览量 |
| Site clicks | 点击网站人数 |
| Channel-entry clicks | 点击社群入口人数 |
| User replies | 用户回复 |
| Asked for full analysis? | 是否询问完整分析 |
| Asked about MTC / streak / rankings? | 是否询问 MTC / 连胜 / 排行榜 |
| Compliance issue? | 合规问题（必须为无） |

---

## 5. Heat verification (per channel click)

Channel-click events **must include `match_id`** (channel-only events do not move match heat):
```bash
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/events/track \
  -H "Content-Type: application/json" \
  -d '{"event_type":"click_social_channel","channel_name":"zalo","match_id":1}'

curl https://worldcup2026-api-71n6.onrender.com/api/v1/community/heat
```
Expected: `total_interactions` +1, the match's `interactions` +1, `updated_at` refreshed.
Heat carries **no personal info** (only match_id, team names, counts, channel name).

---

## 6. Trial PASS criteria

- [ ] At least **3 Vietnamese messages dispatched**.
- [ ] At least **one click or reply** recorded.
- [ ] **No betting misunderstanding** from users.
- [ ] **No forbidden wording** used (zh + vi).
- [ ] At least **one user shows interest** in: full analysis / live correction /
      upset board / MTC.

---

## 7. Post-trial review inputs (feed into ACCELERATED_MVP_REVIEW.md)

- Which message performed best (A / B / C)?
- What did users care about most (analysis / live correction / upset / MTC / rankings)?
- Does the CTA need changing?
- Day 8 decision:
  - **Day 8 LLM Prep** (design/schema/filter) — proceed regardless, no LLM code yet.
  - **Day 8 LLM Full Build** — only if: ≥1 real trial completed + ≥1 active 承接 +
    human feedback samples + stable compliance filter.

---

## 8. Boundaries

No new product features · no full i18n · no LLM · no bots · no hardcoded links ·
no fabricated clicks/feedback · admin writes via `$ADMIN_API_TOKEN` in Render Shell only.
