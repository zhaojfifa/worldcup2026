# Day 6 — Real Data & Storage Integration Plan

> **Planning document only — no functional code in this phase.** Defines the
> execution plan to turn the current "数据能力建设中 / 真实赛果回灌后开放 / 即将开放"
> placeholders into real engineering capabilities.
>
> Read alongside: `CLAUDE.md`, `docs/MVP_STATUS.md`, `docs/DAY4_DATA_AUTOMATION.md`,
> `docs/PRODUCT_OPERATION_ALIGNMENT_V1.md`, `docs/DAY5_FRONTEND_BACKEND_ALIGNMENT.md`,
> `docs/DAY5_5_DATA_SOCIAL_LOOP_PLAN.md`.

---

## 0. Brand sync — Giành Cup (final ruling)

**Current official brand: `Giành Cup`.**

- Positioning: 2026 世界杯 AI 足球情报社区 / World Cup AI Football Intelligence Community
- 中文解释: 赢杯 / 夺杯 · 世界杯 AI 足球情报官
- User-facing standard copy:
  - `Giành Cup`
  - `2026 World Cup AI Football Intelligence`
  - `Giành Cup · 世界杯 AI 足球情报社区`
  - 副文案：「不只看胜率，更看 AI 为什么这样判断。」
- **`Nhà Tiên Tri AI` is retired as the main brand** — it may remain in docs as a
  prior naming option, but **all user-facing surfaces must show `Giành Cup`.**
- Giành Cup 是 AI 数据观点 / 风险提示 / 临场修正 / 足球情报社区品牌，**不是结果承诺品牌**。
  禁用「必中神 / 稳赚神 / 跟单大神 / 包赢」等表达。

### Positions to replace in a later brand-sync commit
Header · Hero · 今日 AI 最强信号卡 · 详情页 AI 结论卡 · 社群页 · Content Studio ·
`CLAUDE.md` · `PRODUCT_OPERATION_ALIGNMENT_V1.md`（后续修订）·
`DAY5_5_DATA_SOCIAL_LOOP_PLAN.md`（后续修订）· 社交媒体文案模板 ·
Telegram / Zalo / Facebook / TikTok 占位文案.

**Current code touch-points (from Day 5.5):** `frontend/src/copy/zh.ts`
(`BRAND` constants — single source), `components/Layout.tsx`, `pages/HomePage.tsx`,
`pages/DetailPage.tsx`, `pages/CommunityPage.tsx`. Because brand strings were
centralized in `copy/zh.ts`, the rename is mostly a one-file edit + a few
inline `NHÀ TIÊN TRI AI` literals in `HomePage.tsx`.

### Naming convention
- **Code identifiers / env / ASCII:** `GIAND_CUP` or `GIAND_CUP_BRAND`.
- **User-facing display:** must be `Giành Cup` (with diacritics).

### Risk & ruling
- Day 6 (this plan) does **not** modify frontend code — only records scope + risk.
- A dedicated brand-sync commit can follow:
  `feat(frontend): rename brand to Giành Cup`.
- Risk: low (centralized copy); main risk is missing an inline literal — mitigated
  by a repo grep for `Nhà Tiên Tri` / `NHÀ TIÊN TRI` before that commit.

---

## 1. Day 6 overall goal

Day 6 is **not** more UI. It is the real **data + storage** layer. Two tracks:

- **A — Real Result Loop / 真实赛果闭环**
- **B — R2 Content Asset Storage / 内容素材存储**

**Recommended order (and why):**
1. **A first (Real Result Loop)** — real results + 战绩 are the trust asset; the
   home「AI 情报战绩」placeholder is the highest-value thing to make real.
2. **B next (R2 Content Asset Storage)** — content assets are the operations
   foundation (share cards, recap images).
3. **Social publishing / bots last** — real channel publishing depends on both
   A (something credible to post) and B (assets to post).

Constraint: every Day 6 step is **additive** — existing endpoints
(`/api/v1/matches`, `/matches/{id}`, `/reports/{id}`) and `VITE_USE_MOCK`
dual-mode must stay intact.

---

## 2. Track A — Real Result Loop / 真实赛果闭环

Goal: turn「AI 情报战绩：真实赛果回灌后开放」into a real, computable module
fully traceable to stored data.

### 2.1 Table: `MatchResult`
| field | type | notes |
|-------|------|-------|
| `id` | PK | |
| `match_id` | FK matches | |
| `external_id` | str | API-FOOTBALL fixture id (`AF-<id>`), for idempotent upsert |
| `full_time_home_score` | int nullable | |
| `full_time_away_score` | int nullable | |
| `outcome` | enum | `home` / `draw` / `away` |
| `result_source` | str | e.g. `api-football` |
| `result_synced_at` | datetime | |
| `status` | enum | `pending` / `final` / `postponed` / `cancelled` / `abandoned` |
| `created_at` / `updated_at` | datetime | |

Only `status=final` results feed settlement & 战绩.

### 2.2 Table: `PredictionSettlement`
| field | type | notes |
|-------|------|-------|
| `id` | PK | |
| `match_id` | FK | |
| `prediction_id` | FK predictions | which prediction was settled |
| `predicted_label` | str | from ops `ai_pick_label` |
| `actual_outcome` | enum | home / draw / away |
| `is_hit` | bool | per settlement rule below |
| `confidence_bucket` | str | e.g. `high(≥72)` / `mid(60–72)` / `low(<60)` |
| `risk_level` | str | low / medium / high |
| `settled_at` | datetime | |
| `created_at` / `updated_at` | datetime | |

### 2.3 Settlement rules (label → result) — avoid 战绩口径混乱
`ai_pick_label` maps to a settlement predicate evaluated against `actual_outcome`:

| `ai_pick_label` | predicted target | `is_hit` when actual_outcome ∈ |
|-----------------|------------------|-------------------------------|
| 主胜偏强 / 主胜略占优 | `home` | {home} |
| 客胜偏强 / 客胜略占优 | `away` | {away} |
| 主队不败趋势 | `home_or_draw` | {home, draw} |
| 客队不败趋势 | `away_or_draw` | {away, draw} |
| 难分胜负 | `draw_or_uncertain` | **excluded from hit-rate** (counted as `unsettled_label`, reported separately) |

- "不败趋势" labels are **double-chance style** outcomes (not betting markets —
  purely a settlement bucket for an analytical lean); they hit on win-or-draw.
- "难分胜负" is **not** scored as hit/miss (no directional claim); it is reported
  as a separate "neutral" count so hit-rate is not inflated or deflated.
- This keeps the public hit-rate honest and reproducible.

### 2.4 API: results sync (admin)
`POST /api/v1/admin/sync/results`
- **Admin-token protected** (`x-admin-token`, same as `/admin/sync/fixtures`).
- Pull finished fixtures from API-FOOTBALL → upsert `MatchResult` by
  `external_id` (update, never duplicate).
- For matches that already have a `Prediction`, run settlement → upsert
  `PredictionSettlement`.
- Returns: `{ inserted, updated, settled, skipped, errors[] }`.

### 2.5 API: performance queries (public, read-only)
`GET /api/v1/performance/daily` · `GET /api/v1/performance/summary`
Returns:
- `date`
- `total_settled`
- `hit_count`
- `hit_rate`
- `high_confidence_hit_rate`
- `live_correction_uplift`  (hit-rate delta on matches that had a LiveCorrection)
- `risk_breakdown`  (per risk_level hit-rate)
- `neutral_count`  (难分胜负 labels excluded from hit-rate)
- `disclaimer`: 「历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。」

### 2.6 Compliance & integrity (mandatory)
- **不允许展示未标注虚假战绩** — until real `MatchResult` exists, the UI keeps the
  「真实赛果回灌后开放 / 数据能力建设中」status surface.
- 不允许伪造命中率；不允许把历史战绩包装成未来承诺。
- 所有战绩必须可追溯到 `MatchResult` + `PredictionSettlement`。
- Every 战绩/命中/连胜 surface carries the disclaimer above.

---

## 3. Track B — R2 Content Asset Storage / 内容素材存储

Goal: storage for Content Studio share cards, live-correction screenshots,
post-match recaps, social materials. **Day 6 plan only — no R2 code.**

### 3.1 R2 usage
今日 AI 最强信号分享卡 · 今日爆冷风险短图 · 临场修正截图 · 赛后复盘长图 ·
社交媒体素材 · （后置）用户头像 / 社区素材.

### 3.2 Environment variables (names only, no real values)
```
R2_ACCOUNT_ID
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
R2_BUCKET_NAME
R2_PUBLIC_BASE_URL
```
> `.env.example` currently has `R2_BUCKET` / `R2_PUBLIC_BASE_URL` placeholders;
> when R2 lands, align to `R2_BUCKET_NAME`. Read only from env; never logged/committed.

### 3.3 Backend storage service (future)
`backend/app/services/storage/r2_client.py`
- `upload_asset(file_bytes, key, content_type) -> key`
- `get_public_url(key) -> str`  (via `R2_PUBLIC_BASE_URL`)
- `delete_asset(key) -> None`
- `asset_exists(key) -> bool`
- S3-compatible (boto3 / aioboto3) to Cloudflare R2 endpoint; lazy client;
  graceful no-op + clear message when unconfigured (mirrors api_football pattern).

### 3.4 Table: `ContentAsset`
| field | type | notes |
|-------|------|-------|
| `id` | PK | |
| `asset_type` | enum | `top_signal_card` / `upset_card` / `live_correction_card` / `post_match_recap` / `social_material` |
| `storage_key` | str | R2 object key |
| `public_url` | str | derived from `R2_PUBLIC_BASE_URL` |
| `content_type` | str | e.g. image/png |
| `size_bytes` | int | |
| `related_match_id` | FK nullable | |
| `created_by` | str | admin actor |
| `created_at` | datetime | |
| `status` | enum | `active` / `archived` / `deleted` |

### 3.5 API
`POST /api/v1/admin/assets/upload`  — **admin-token protected**
`GET /api/v1/assets/{id}`  — public read, only `status=active` public assets
`DELETE /api/v1/admin/assets/{id}`  — **admin-token protected** (soft delete → `deleted`)
- No user upload, no real UGC, no sensitive personal data.

### 3.6 Content Studio alignment (future)
复制运营文案 / 生成分享卡 / 临场修正截图 / 赛后复盘图 → first produce a
`ContentAsset` (rendered server-side or client-side then uploaded), then used for
Zalo / Telegram / Facebook / TikTok distribution. **Day 6 plan only.**

---

## 4. Community heat & social config (designed, deferred)

### 4.1 Table: `MatchEngagement`
`match_id` · `views_count` · `detail_clicks` · `unlock_clicks` · `favorite_count`
· `share_clicks` · `community_clicks` · `social_channel_clicks` · `last_updated_at`.

### 4.2 API
`POST /api/v1/events/track` (in-app behaviour only) · `GET /api/v1/community/heat`.
- Phase 1: in-app behaviour only. No comments, no posting, no 晒单, no real UGC —
  light social proof only.

### 4.3 Table: `SocialChannel` config
`channel_name` · `display_name` · `status` · `public_url` · `description` ·
`locale` · `is_enabled`.
- Channels: Zalo · Telegram · Facebook · TikTok.
- May hold **real community links** in config without bots in phase 1.
- Priority: **Zalo first, Telegram second**, Facebook/TikTok as content
  distribution entries.

---

## 5. Streak & rankings (designed, deferred)

### 5.1 Table: `UserStreak`
`user_id` · `current_streak` · `best_streak` · `last_participation_date` ·
`mtc_earned` · `updated_at`.

### 5.2 Table: `ChallengeResult`
`challenge_id` · `user_id` · `selected_option` · `actual_result` · `is_correct`
· `settled_at`. (Settled against `MatchResult`.)

### 5.3 API
`GET /api/v1/rankings` · `GET /api/v1/users/{id}/streak`.
- **MTC platform points only** — no cash reward, no cash pool.
- MTC 不可提现 · 不可转让 · 不可交易 · 不作为金融资产.
- Streak/命中 surfaces carry the 战绩 disclaimer.

---

## 6. Future `GET /api/v1/home/summary` alignment (not implemented in Day 6)

```
{
  "brand": "Giành Cup",
  "top_pick":        …,
  "today_matches":   …,
  "upset_alerts":    …,
  "performance":     …,
  "community_heat":  …,
  "fan_zone":        …,
  "social_channels": …,
  "content_studio":  …
}
```

| field | source |
|-------|--------|
| `brand` | static config (`GIAND_CUP_BRAND`) |
| `top_pick` / `today_matches` / `upset_alerts` | Match / Prediction / Report |
| `performance` | **MatchResult** + **PredictionSettlement** |
| `community_heat` | **MatchEngagement** |
| `fan_zone` | **TokenWallet** + **UserStreak** / **ChallengeResult** |
| `social_channels` | **SocialChannel** config |
| `content_studio` | **ContentAsset** (+ derived capability list) |

Additive endpoint; does not change existing response shapes.

---

## 7. Step-by-step implementation plan

### Day 6A — Real result loop
- **Goal:** real 战绩 from real results.
- **Scope:** `MatchResult`, `PredictionSettlement` tables;
  `POST /api/v1/admin/sync/results`; `GET /api/v1/performance/daily|summary`;
  settlement rules (§2.3). Frontend later swaps the status surface for real data.
- **Risk:** medium — new tables + settlement correctness (label mapping). Mitigate
  with unit tests on settlement rules and idempotent upsert by `external_id`.
- **Acceptance:** results upsert idempotent; settlement matches §2.3; hit-rate
  reconciles to stored settlements; admin write 401 without token; existing
  endpoints byte-identical; disclaimer present.
- **Affects live?** Additive; no change to current flows until frontend opts in.

### Day 6B — R2 content asset storage
- **Goal:** store and serve content assets.
- **Scope:** `r2_client.py`; `ContentAsset` table; `POST /admin/assets/upload`;
  `GET /assets/{id}`; `DELETE /admin/assets/{id}`; env vars wired.
- **Risk:** medium — external storage creds, public-read exposure. Mitigate: env
  only, admin-protected writes, active-only public read, soft delete, no PII.
- **Acceptance:** upload→public_url round-trip; unconfigured R2 degrades
  gracefully; admin writes 401 without token; only active public assets readable.
- **Affects live?** Additive; no impact when unused/unconfigured.

### Day 6C — Social config + community heat
- **Goal:** real channel config + light in-app heat.
- **Scope:** `SocialChannel` config (Zalo/Telegram/Facebook/TikTok, Zalo-first);
  `POST /events/track`; `GET /community/heat`; `MatchEngagement`.
- **Risk:** low–medium — event volume/write rate. Mitigate: batch/throttle, no PII.
- **Acceptance:** channels configurable + render; events recorded; heat derived;
  no UGC surfaces; disclaimers where relevant.
- **Affects live?** Additive; channel links can go live independently.

### Day 6D — Streak & rankings
- **Goal:** retention loop made real.
- **Scope:** `UserStreak`, `ChallengeResult`; challenge settlement against
  `MatchResult`; `GET /rankings`, `GET /users/{id}/streak`.
- **Risk:** medium — settlement correctness + MTC accounting integrity.
- **Acceptance:** streak/ranking reconcile to settlements + TokenLog; MTC-only,
  no cash; non-withdrawable/transferable/tradable enforced; disclaimer present.
- **Affects live?** Additive.

---

## 8. Compliance boundary (unchanged)

**Forbidden (user-facing):** 下注 · 稳赚 · 必中 · 跟单 · 购彩 · 回报率 · 返奖 ·
收益承诺 · 现金奖池 · Token 提现/转让/交易.

`提现` only inside `不可提现`.

战绩 / 命中 / 连胜 must always carry:
「历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。」

MTC = 平台积分 · 不可提现 · 不可转让 · 不可交易 · 不作为金融资产.

---

## 9. Phase boundary

- **Day 6 (this doc):** design/execution plan only — no code.
- Implementation proceeds 6A → 6B → 6C → 6D, each additive and behind the
  existing admin-token / feature gating, never breaking current online version.
