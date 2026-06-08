# CLAUDE.md — worldcup2026 Engineering Entry Point

> **Read this file first** at the start of every Claude engineering session for
> this project, before executing any task. It is the source of truth for
> identity, baseline, rules, and guardrails.

---

## ★ Current Project State / Handoff (read this first)

> Full handoff for a new chat: **`docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md`**.
> Engineering status snapshot: **`docs/MVP_STATUS.md`** (v0.6D).

1. **Brand:** `Giành Cup` · `2026 World Cup AI Football Intelligence`.
   User-facing: **Giành Cup · 世界杯 AI 足球情报社区**.
   (Retired main brand: Nhà Tiên Tri AI — historical docs only.)

2. **Live URLs:**
   - Frontend: https://worldcup2026-izid.onrender.com
   - Backend:  https://worldcup2026-api-71n6.onrender.com

3. **Stage:** **MVP v0.7 — multilingual operation preparation** (origin/main synced).
   Day 6A–6D done & Render-verified PASS. Day 7 ops-readiness + accelerated operation
   loop done. Multilingual (zh/en/vi/mm) operation mode in place. **Operational blocker:
   no `active` Zalo/Telegram channel yet** (real customer trial cannot dispatch until set).
   Day 8 LLM = Prep only, not Full Build.

4. **Compliance floor (non-negotiable):**
   不做博彩 · 不做现金投注 · 不承诺命中 · 不承诺收益 ·
   MTC 仅平台积分（不可提现 / 不可转让 / 不可交易）·
   排行榜是积分/连胜榜，不是收益榜。

5. **Forbidden user-facing wording:**
   下注 · 稳赚 · 必中 · 跟单 · 购彩 · 回报率 · 返奖 · 收益承诺 · 现金奖池 ·
   Token 提现/转让/交易。 `提现` 只允许出现在 `不可提现`。

6. **Mandatory disclaimer (战绩/命中/连胜 must carry it):**
   「历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。」

---

## ★ Language & Operation Policy (read before any multilingual/operation work)

> Full baseline: **`docs/MULTILINGUAL_OPERATION_POLICY.md`** (authoritative).

- **Brand:** Giành Cup.
- **Current MVP version:** v0.7 — multilingual operation preparation.
- **Default system / fallback language:** **English** (`en`).
- **Internal management language:** **Chinese** (`zh`; also default UI when no locale chosen).
- **Primary customer operation language:** **Vietnamese** (`vi`) — MVP UI **ready**, pricing **VND / ₫**.
- **Secondary customer operation language:** **Burmese / Myanmar** (`mm`) — MVP UI **ready &
  acceptance-verified** (core Burmese, rest → English; no Chinese residual; no ¥/元/₫), pricing
  **MMK (Ks)** = "MM MVP operation test pricing" (12,000 Ks / 59,000 Ks/လ, matches page).
  Trial URL: `https://worldcup2026-izid.onrender.com/?lang=mm`.
  - **Myanmar density profile:** Burmese glyphs are taller / words longer, so mm uses a
    **separate, shorter copy set** and a `.lang-mm` CSS density profile (root carries
    `data-lang` + `lang-${locale}` in `Layout.tsx`). **Burmese copy must stay shorter than
    Vietnamese**; concise English product terms (AI / Risk / Update / MTC / Premium / VIP /
    team names) are allowed in mm UI. zh / vi / en are unaffected (rules scoped to `.lang-mm`).
  - **Burmese translation accepted by operation team (2026-06-06).** mm upgraded from
    "framework + English fallback" to **customer-ready Burmese**: core UI (Home/Detail/Token/
    Community), dynamic data (team outcomes, AI tendency, risk level/tags, notes, reason bullets,
    live-correction) all Burmese via `copy/mm.ts` + `i18n/mmMapping.ts`. **English remains the
    system fallback** for unmapped dynamic data only; **Chinese is never a customer-side fallback.**
  - **Myanmar mobile QA passed (2026-06-07).** Screenshot-verified at 390×844 & 430×932 →
    `docs/MM_MOBILE_QA_REPORT.md` (PASS), shots in `docs/qa_screenshots/mm_mobile/`. Fixed Today
    Matches row overlap (mm `.simrow` two-row), shortened signal CTA, Burmese channel descriptions.
  - **Vietnamese mobile QA passed (2026-06-07).** Same screenshot method → `docs/VI_MOBILE_QA_REPORT.md`
    (PASS), shots in `docs/qa_screenshots/vi_mobile/`; no residual found (vi already customer-ready).
  - **Screenshot-driven QA is MANDATORY for customer languages (vi/mm)** before declaring a layout
    PASS (QA script: `scripts/qa/lang_mobile_shots.sh`, headless Chrome — not a prod dependency).
  - **Language gate CLOSED.** Next phase plan: `docs/NEXT_PHASE_DATA_MODEL_SOCIAL_LLM_PLAN.md`
    (Data / Modeling / Social / LLM-prep / deployment / go-live gate). LLM stays in prep, not
    full build.
  - **Harness-X L1 + P-flow Prep (2026-06-08):** verified data-source (connector ok, `mock_mode=true`,
    0 settled → no real hit-rate claimable) → `docs/DATA_SOURCE_SYNC_VERIFICATION.md`; baseline
    predictor + refresh (win_prob=100) → `docs/MODELING_BASELINE_VERIFICATION.md`; vi/mm copy library
    → `docs/OPERATION_COPY_LIBRARY_VI_MM.md`; LLM prep schema+guardrails (design only) →
    `docs/LLM_PREP_SCHEMA_AND_GUARDRAILS.md`. **Channels: Myanmar Telegram ACTIVE (verified live),
    Vietnam Zalo pending.** LLM Full Build remains Owner-gated.
- **API / admin / config / schema / data contract language:** **English** (ASCII identifiers).
- **Fallback chains:** `zh→[zh]`, `en→[en,zh]`, `vi→[vi,en]`, `mm→[mm,en]`.
  **vi/mm must NEVER fall back to Chinese** — English is their fallback.
- **Pricing localization** (`frontend/src/i18n/pricing.ts`; never hardcode ¥ in pages):
  zh = RMB, en = USD, vi = VND, mm = MMK. MVP operational prices, not real-time FX. MTC constant.
- **Full i18n:** deferred. **LLM translation/generation:** deferred until after a real
  operation trial (then behind a banned-word output filter).
- **UI language buttons:** `CN · VI · MY` (`en` is the internal fallback layer, no button).
- **Operational blocker:** an `active` Zalo/Telegram channel remains the gate to the real trial.
- **i18n code:** `frontend/src/i18n/{useLocale,dict,pricing,viMapping}.ts`,
  `frontend/src/copy/{zh,en,vi,mm}.ts`.
- **Operation copy docs:** `docs/OPERATION_TRIAL_MESSAGES_VI.md`,
  `docs/MM_OPERATION_TRIAL_MESSAGES.md`, `docs/VI_OPERATION_TRIAL_RUNBOOK.md`.

---

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
