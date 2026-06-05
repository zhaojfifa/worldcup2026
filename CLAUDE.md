# CLAUDE.md — worldcup2026 Engineering Entry Point

> **Read this file first** at the start of every Claude engineering session for
> this project, before executing any task. It is the source of truth for
> identity, baseline, rules, and guardrails.

### Key design docs (read after this file when doing product work)
- `docs/PRODUCT_OPERATION_ALIGNMENT_V1.md` — **formal** product/operation plan
  (positioning upgrade, home/detail IA, API & modeling output layer, ops,
  compliance, phased roadmap). Authoritative for product scope.
- `docs/_drafts/product_operation_alignment_brainstorm.md` — exploratory draft
  behind the formal plan (background only).
- `docs/MVP_STATUS.md`, `docs/DAY4_DATA_AUTOMATION.md` — engineering baseline.

---

## 1. Project Identity

- **Name:** worldcup2026
- **Brand (final):** **Giành Cup**（中文：赢杯 / 夺杯 · 世界杯 AI 足球情报官）。
  用户侧标准文案：`Giành Cup` · `2026 World Cup AI Football Intelligence` ·
  `Giành Cup · 世界杯 AI 足球情报社区`；副文案「不只看胜率，更看 AI 为什么这样判断。」
  代码标识符用 ASCII `GIAND_CUP` / `GIAND_CUP_BRAND`，显示必须为 `Giành Cup`。
  人设是 AI 数据观点 / 风险提示 / 临场修正解释，**不是结果承诺品牌**；禁用
  「必中神 / 稳赚神 / 跟单大神 / 包赢」等称谓。
  _曾用命名方案：Nhà Tiên Tri AI（已弃用为主品牌；用户侧 UI 已于 Day 6B 全部替换为
  Giành Cup，仅保留于历史文档说明）。代码品牌常量集中在 `frontend/src/copy/zh.ts`
  的 `GIAND_CUP_BRAND`（`BRAND` 为兼容别名）；R2 资产 key 统一使用 `giand-cup`。_
- **Positioning:** 2026 世界杯 **AI 足球情报社区**（formalized in
  `PRODUCT_OPERATION_ALIGNMENT_V1.md`；前身表述「AI 情报终端」），面向越南、缅甸
  及东南亚球迷。**不做博彩，不提供现金投注，不承诺收益。**
  用户侧使用「AI 足球情报社区 / AI 赛事情报 / AI 数据观点 / AI 倾向」；避免「决策社区」。
- **Core selling points:**
  - AI 赛前预测
  - 高可信 AI 解释
  - 临场 30 分钟修正
  - MTC 平台积分闭环
  - 39 元单场解锁
  - 199 元/月社群订阅

---

## 2. Current Baseline

**MVP v0.4 · Auto Data Source + Baseline Predictor Baseline**

**Active theme — Day 6: Real Data & Storage Integration** (plan:
`docs/DAY6_REAL_DATA_STORAGE_PLAN.md`). Order: 6A Real Result Loop
(MatchResult / PredictionSettlement / admin sync results / performance) →
6B R2 Content Asset Storage → 6C social config + community heat →
6D streak / rankings. Day 6 plan is design-only; implementation is additive
and must not break existing API shapes or `VITE_USE_MOCK` dual mode.

Done:
- Frontend Render 部署
- Backend Render 部署
- Render PostgreSQL seed
- 前后端 API 联调
- UI / Copy Enhancement
- API-FOOTBALL connector
- data-source status
- admin protected fixtures sync
- baseline predictor
- match refresh API

Live URLs:
- Frontend: https://worldcup2026-izid.onrender.com
- Backend:  https://worldcup2026-api-71n6.onrender.com

---

## 3. Repository Rules

- **Standard path:** `/Users/jackie/code/worldcup2026`
- **Do NOT use the wrong path:** `/Users/jackie/code/wordcup2026` ❌
- **GitHub:** https://github.com/zhaojfifa/worldcup2026

Commit rules:
- 小步提交（small, focused commits）
- 每个阶段必须 push
- 不提交 `.env`、`.env.local`、`node_modules`、`.claude`、真实 API key
- 修改环境变量时同步 `.env.example` 或 `docs`，但**不能写真实值**

---

## 4. Architecture

Pipeline:
```
DataSource
→ Feature Builder
→ Prediction Engine
→ Explanation Engine
→ Report Generator
→ Frontend API
```

Current implementation:
- **DataSource:** API-FOOTBALL connector + seed fallback
- **Prediction Engine:** baseline rules model
- **Explanation Engine:** mock / structured copy
- **AI_PROVIDER:** `mock`
- **R2:** not enabled

---

## 5. Frontend Rules

Path: `frontend/`

Must preserve:
- `VITE_USE_MOCK=true / false` 双模式
- `VITE_API_BASE_URL`
- `client.ts`
- `transform.ts`
- snake_case API → camelCase frontend isolation
- mobile-first UI
- 世界杯权威蓝白金风格 + Sports App 视觉增强

Must NOT break:
- Home / Detail / Report / Token / Community 页面
- MatchCard
- LINEUP WATCH
- MTC Fan Mission Center
- AI Tactical Room

---

## 6. Backend Rules

Path: `backend/`

Render config:
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Core API:
```
GET  /api/v1/health
GET  /api/v1/matches
GET  /api/v1/matches/{id}
GET  /api/v1/reports/{id}
GET  /api/v1/data-source/status
POST /api/v1/admin/sync/fixtures
POST /api/v1/matches/{id}/refresh
POST /api/v1/tokens/checkin
POST /api/v1/tokens/unlock-report
POST /api/v1/challenges/{id}/join
POST /api/v1/community/subscribe
```

- Admin 接口必须使用 `x-admin-token`。
- `ADMIN_API_TOKEN` 未配置时 admin 路由必须锁住（401），**不得开放公网**。

---

## 7. Environment Variables

Record variable **names only — never real values**.

```
APP_ENV
DATABASE_URL
API_FOOTBALL_BASE_URL
API_FOOTBALL_KEY
WC_LEAGUE_ID
WC_SEASON
ADMIN_API_TOKEN
AI_PROVIDER
DEEPSEEK_API_KEY
KIMI_API_KEY
GEMINI_API_KEY
CORS_ORIGINS
ENABLE_REAL_MONEY_BETTING
ENABLE_TOKEN_WITHDRAWAL
VITE_API_BASE_URL
VITE_USE_MOCK
```

Current Render backend (non-secret):
- `AI_PROVIDER=mock`
- `WC_LEAGUE_ID=1`
- `WC_SEASON=2026`

---

## 8. Compliance Rules

Forbidden in marketing/copy:
- 下注
- 稳赚
- 必中
- 跟单
- 购彩
- 回报率
- 返奖
- 收益承诺

`提现` is allowed **only** inside: **不可提现**.

MTC must always be described as **平台积分 / platform loyalty points**, and must declare:
- 不可提现
- 不可转让
- 不可交易
- 不作为金融资产
- 不承诺收益
- 不接入博彩

---

## 9. Day 4 Result

- `backend/app/services/modeling/baseline.py`
- `backend/app/routers/data_source.py`
- `backend/app/routers/admin.py`
- `docs/DAY4_DATA_AUTOMATION.md`
- API-FOOTBALL `get_fixtures` + `status`
- fixtures sync Team/Match upsert（by `api_id` / `external_id`，update 不重复 insert）
- `refresh_prediction`
- `POST /matches/{id}/refresh`
- 概率归一化通过 2000 次随机测试（0 例 sum≠100）
- admin sync：无 token / 错误 token → 401，正确 token → 200

---

## 10. Next Milestones

Suggested order:
- **Day 4.5:** Render 部署验证 Day 4 新接口
- **Day 5:** 前端增加数据源状态 / refresh 管理入口，或后台轻量 admin panel
- **Day 6:** `AI_PROVIDER` 从 mock 切到 DeepSeek/Kimi 的 report generator
- **Day 7:** R2 / 分享卡 / 多语言 / 运营验收

**Guardrails until Day 5:**
- Day 5 前不要大改 UI。
- Day 5 前不要破坏现有 API shape。
- Day 5 前不要引入复杂 ML 训练。
- Day 5 前不要启用真实支付。
- Day 5 前不要接链上 Token。
