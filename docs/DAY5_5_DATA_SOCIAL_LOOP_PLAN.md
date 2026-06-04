# Day 5.5 — Data & Social Loop Plan

> **Scope of Day 5.5 in code:** frontend brand exposure (Nhà Tiên Tri AI) +
> social/community **placeholders** + content-studio **placeholder** + this
> design document. **No backend, no new tables, no real bots/webhooks, no R2,
> no LLM, no real UGC, no real payment.** Everything below under "future" is
> design only.
>
> **Brand:** Nhà Tiên Tri AI（越南语完整名 Nhà Tiên Tri Bóng Đá，中文：足球先知 /
> 世界杯 AI 情报官）。人设是 **AI 数据观点 / 风险提示 / 临场修正 / 足球情报解释**，
> **不是结果承诺人设**。标准副文案：「不是告诉你一定会赢，而是告诉你 AI 为什么这样看。」

---

## 1. AI 情报战绩闭环 (future)

**Future tables**

`MatchResult`
- `id`
- `match_id` (FK matches)
- `full_time_home_score`
- `full_time_away_score`
- `outcome`  (home / draw / away)
- `result_source`  (e.g. api-football)
- `result_synced_at`
- `status`  (pending / final)

`PredictionSettlement`
- `match_id`
- `predicted_label`  (来自运营输出层 ai_pick_label)
- `actual_outcome`
- `is_hit`
- `confidence_bucket`
- `risk_level`
- `settled_at`

**Future API**
- `GET /api/v1/performance/daily`
- `GET /api/v1/performance/summary`
- `POST /api/v1/admin/sync/results`  — **admin token protected** (`x-admin-token`)

**Rules**
- 写操作必须经 `ADMIN_API_TOKEN` 保护（与现有 `/admin/sync/fixtures` 一致）。
- 战绩**必须来自真实赛果回灌**（`MatchResult` ← API-FOOTBALL finished fixtures），
  不得展示未标注的虚假战绩。
- 任何展示战绩 / 命中 / 连胜处必须附：
  「历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。」
- 现阶段前端为状态占位（「真实赛果回灌后开放 / 数据能力建设中」）。

---

## 2. 社区热度闭环 (future)

**Future table**

`MatchEngagement`
- `match_id`
- `views_count`
- `detail_clicks`
- `unlock_clicks`
- `favorite_count`
- `share_clicks`
- `community_clicks`
- `last_updated_at`

**Future API**
- `POST /api/v1/events/track`  — 站内行为埋点
- `GET /api/v1/community/heat`

**Rules**
- 先记录**站内行为**（浏览/点击/解锁/收藏/分享），用于轻社交证明。
- 不做评论区、不做晒单上传、不做用户发帖、不做真实 UGC。
- 现阶段前端为「社区热度即将上线」状态占位。

---

## 3. 连胜挑战与排行榜 (future)

**Future tables**

`UserStreak`
- `user_id`
- `current_streak`
- `best_streak`
- `last_participation_date`
- `mtc_earned`

`ChallengeResult`
- `challenge_id`
- `user_id`
- `selected_option`
- `actual_result`
- `is_correct`
- `settled_at`

**Future API**
- `GET /api/v1/rankings`
- `GET /api/v1/users/{id}/streak`

**Rules**
- 仅使用 **MTC 平台积分**；不出现现金奖励、不出现现金奖池。
- MTC **不可提现、不可转让、不可交易，不作为金融资产**。
- 连胜 / 命中展示处必须附战绩免责声明（同 §1）。

---

## 4. 社交媒体与社群对接 (future)

**Future channels:** Zalo · Telegram · Facebook · TikTok。

**Future capabilities:**
- 复制运营文案
- 生成分享卡
- 临场修正截图
- 今日 AI 三场速览
- 社群推送文案

**This phase:** 仅 UI 占位（disabled / 即将开放）+ 本设计文档。真实机器人、
Webhook、分享卡存储、R2 上传**后置**。渠道入口当前不跳真实外链。

未来对接形态（设计参考，不实现）：
- Telegram：Bot + channel push（首发修正实时同步）。
- Zalo：Official Account / group（越南主阵地，每日情报）。
- Facebook：Page + 长图复盘。
- TikTok：短视频脚本来源（今日三场 / 爆冷 / 最高信心 / 临场修正）。

---

## 5. R2 / 存储后续设计 (future)

**未来 R2 用途：**
- 分享卡图片
- 临场修正截图
- 赛后复盘长图
- 社交媒体素材
- 用户头像 / 社区素材（后置）

**未来环境变量（仅规划，本阶段不接入）：**
```
R2_ACCOUNT_ID
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
R2_BUCKET_NAME
R2_PUBLIC_BASE_URL
```
> 注：现有 `.env.example` 已预留 `R2_*` 占位（含 `R2_BUCKET` / `R2_PUBLIC_BASE_URL`）。
> 未来正式接入时统一命名（`R2_BUCKET_NAME` 对齐），生成资产存 R2 并以
> `R2_PUBLIC_BASE_URL` 对外。本阶段不接入。

---

## 6. Future `GET /api/v1/home/summary` 对齐

未来单次聚合返回（**本阶段不实现**）：
```
{
  "top_pick":        …,   // Match + Prediction (+运营输出层派生)
  "today_matches":   …,   // Match + Prediction
  "upset_alerts":    …,   // Match + Prediction (derived upset_score)
  "performance":     …,   // MatchResult + PredictionSettlement
  "community_heat":  …,   // MatchEngagement
  "fan_zone":        …,   // TokenWallet + UserStreak
  "social_channels": …,   // SocialChannel config (static/admin)
  "content_studio":  …    // 运营内容能力清单 (static/admin + 派生)
}
```

**字段来源对照：**

| summary 字段 | 数据来源 | 现状 |
|--------------|----------|------|
| `top_pick` | Match / Prediction / Report | 现可派生（前端 ops 层） |
| `today_matches` | Match / Prediction | 现有 `/matches` |
| `upset_alerts` | Match / Prediction（派生 upset_score） | 现可派生 |
| `performance` | **MatchResult** + **PredictionSettlement** | 待真实赛果回灌 |
| `community_heat` | **MatchEngagement** | 数据能力建设中 |
| `fan_zone` | **TokenWallet** + **UserStreak** | Token 现有；连胜后置 |
| `social_channels` | SocialChannel config（静态/admin） | 本阶段前端静态占位 |
| `content_studio` | 运营内容能力清单（静态/admin + 派生） | 本阶段前端静态占位 |

**非破坏保证：** `home/summary` 为新增聚合端点；不改变
`/api/v1/matches`、`/api/v1/matches/{id}`、`/api/v1/reports/{id}` 的响应结构。

---

## 7. 阶段边界

- **Day 5.5（本阶段）：** 品牌露出 + 社群/内容占位 + 本文档。前端 only。
- **Phase B：** `home/summary`、`MatchResult` + 赛果回灌、`performance/*`、
  `community/heat`、`events/track`。
- **Phase C：** `rankings` / `UserStreak`、LLM 文案、复制文案 / 分享卡生成、
  R2 接入、Telegram / Zalo / Facebook / TikTok 真实对接、i18n（越南语优先）。
