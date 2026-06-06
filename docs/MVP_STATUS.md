# MVP Status — Giành Cup (worldcup2026)

_Last updated: 2026-06-06 (Day 7) · Version: **MVP v0.7**_

Status snapshot only — no functional change in this document.
Full handoff: `docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md`.

---

## Brand & positioning

- **Brand:** Giành Cup · 2026 World Cup AI Football Intelligence.
- **User-facing:** Giành Cup · 世界杯 AI 足球情报社区.
- AI 足球情报社区 for the Vietnam-first SEA market. **Not a betting product.**

## Live deployments

| Tier | URL / value |
|------|-------------|
| Frontend (Render) | https://worldcup2026-izid.onrender.com |
| Backend (Render)  | https://worldcup2026-api-71n6.onrender.com |
| Database | Render PostgreSQL |
| R2 bucket | `giand-cup-assets` (R2 ready; `R2_PUBLIC_BASE_URL` unset = acceptable) |
| Repo / branch | github.com/zhaojfifa/worldcup2026 · `main` (origin synced) |

---

## Day 6D Render Verification: **PASS** (2026-06-06)

| Endpoint | Result | Notes |
|----------|--------|-------|
| `GET /api/v1/health` | ✅ OK | `real_money_betting_enabled: false`, `token_withdrawal_enabled: false` |
| `GET /api/v1/assets/status` | ✅ OK | `r2_configured: true`, `public_base_url_set: true`, `message: "R2 ready"` |
| `GET /api/v1/users/1/streak` | ✅ PASS | No longer 404. Empty-safe initial: `current_streak=0`, `best_streak=0`, `mtc_earned=0`, `last_participation_date=null`; disclaimer present. |
| `GET /api/v1/rankings` | ✅ PASS | No longer 404. Initial `top_users=[]`, empty-safe; disclaimer present. |
| `POST /admin/challenges/settle` | ✅ PASS | Succeeded via Render Shell `$ADMIN_API_TOKEN`. See settlement log below. |

**Settlement verification (Render Shell, `$ADMIN_API_TOKEN`):**

- **challenge_id=1** → `ok=true`, `is_correct=true`, `mtc_reward=10`, `current_streak=1`, `best_streak=1`.
  - Re-check `/users/1/streak` → `current_streak=1`, `best_streak=1`, `mtc_earned=10`.
  - Re-check `/rankings` → `#1 Demo Fan`, `current_streak=1`, `best_streak=1`, `mtc_earned=10`.
- **challenge_id=2** → settled again → `current_streak=2`, `best_streak=2`, `mtc_reward=10`.

**Conclusion: Day 6D Render verification PASS.** PR #1 previous blocker resolved.

---

## Completed milestones

- **Day 2** — React/Vite frontend, 5 pages.
- **Day 3** — FastAPI + PostgreSQL + Render deploy + API loop.
- **Day 4** — API-FOOTBALL connector, fixtures sync, baseline predictor, refresh prediction.
- **Day 5** — Operational intelligence home (今日 AI 最强信号 / 简表 / 爆冷风险 TOP3 /
  战绩状态), detail AI 结论卡; frontend ops derive layer.
- **Day 5.5** — Giành Cup branding, 社群矩阵, Content Studio placeholders, data/social design.
- **Day 6A** — `MatchResult`, `PredictionSettlement`, `/admin/sync/results`,
  `/performance/daily`, `/performance/summary`.
- **Day 6B** — R2 (`giand-cup-assets`), `ContentAsset`, `/assets/status`,
  `/admin/assets/upload`, `/assets/{id}`, `/admin/assets/{id}` (boto3 lazy).
- **Day 6C** — `SocialChannel`, `MatchEngagement`, `/social/channels`,
  `/admin/social/channels/upsert`, `/events/track`, `/community/heat`.
- **Day 6D** — `UserStreak`, `ChallengeResult`, `/users/{id}/streak`, `/rankings`,
  `/admin/challenges/settle`; TokenPage fan streak + rankings fallback.
- **Day 7** — Operational Readiness & Public MVP Polish:
  Content Studio shows live R2 storage readiness status (`/assets/status`);
  `docs/OPERATIONS_RUNBOOK.md` (daily ops flow, social channel config via admin API);
  `docs/COMPLIANCE_CHECKLIST.md` (forbidden words, MTC statement, disclaimers, rankings);
  frontend build passes; forbidden-word scan clean; `/matches`+`/reports` shapes unchanged.

Latest commits:
```
b047953 docs: add v0.6D engineering handoff
e7dcad4 feat(frontend): show fan streak and rankings fallback
0c3f730 feat(backend): add streak challenge and rankings
```

---

## ✅ Deployed / done

- Frontend + backend on Render; PostgreSQL live; API loop verified (CORS OK).
- mock ↔ API dual mode (`VITE_USE_MOCK`) verified.
- Day 6A–6D verified online (Day 6D streak/rankings/admin settle PASS — see table above).
- All new capabilities are **additive**: `/matches`, `/matches/{id}`,
  `/reports/{id}` response shapes unchanged across Day 4→6D.
- Brand unified to Giành Cup across header / hero / signal / verdict.

## ✅ Done in Day 7

- Content Studio section in Community page shows live R2 storage readiness via `/assets/status`.
- `docs/OPERATIONS_RUNBOOK.md` — daily prediction flow, social channel config, admin API examples.
- `docs/COMPLIANCE_CHECKLIST.md` — forbidden words, MTC statement, disclaimers, rankings sign-off.
- Frontend build passes; forbidden-word scan clean; API shapes unchanged.

## Not yet done (by design)

- API-FOOTBALL real fixtures/results sync run in production (connector ready;
  graceful mock-mode when key absent).
- `AI_PROVIDER` still `mock` — no LLM wired (planned Day 8, behind banned-word filter).
- `R2_PUBLIC_BASE_URL` not bound → `public_url` returns null (acceptable).
- i18n (Vietnamese-first) not implemented; UI zh-CN only.
- Real Telegram/Zalo bots, share-card image generation, real UGC — not built.

---

## Compliance status

- No forbidden user-facing wording; `提现` only inside `不可提现`.
- MTC = platform loyalty points · 不可提现 · 不可转让 · 不可交易 · 不作为金融资产.
- Rankings is a streak/points board, **not** an earnings board.
- 战绩 / 命中 / 连胜 surfaces carry the mandatory disclaimer.
- No IP / user-agent / personal data captured in event tracking.

## Environment variables (names only; values in Render)

`APP_ENV` · `DATABASE_URL` · `API_FOOTBALL_BASE_URL` · `API_FOOTBALL_KEY` ·
`WC_LEAGUE_ID=1` · `WC_SEASON=2026` · `ADMIN_API_TOKEN` · `AI_PROVIDER=mock` ·
`DEEPSEEK_API_KEY` · `KIMI_API_KEY` · `GEMINI_API_KEY` · `CORS_ORIGINS` ·
`ENABLE_REAL_MONEY_BETTING=false` · `ENABLE_TOKEN_WITHDRAWAL=false` ·
`R2_ACCOUNT_ID` · `R2_ACCESS_KEY_ID` · `R2_SECRET_ACCESS_KEY` ·
`R2_BUCKET=giand-cup-assets` · `R2_PUBLIC_BASE_URL` (empty) ·
`VITE_API_BASE_URL` · `VITE_USE_MOCK`.

> Day 6 added no new backend env vars beyond the existing R2_* (already set).

---

## Day 7 Status (Operational Readiness & Public MVP Polish)

| Task | Status |
|------|--------|
| Day 6D Render online verification (health + assets/status) | ✅ Verified |
| Day 6D streak/rankings/admin settle Render verification | ✅ PASS |
| Content Studio reads `/assets/status` | ✅ Done |
| Operations manual (daily flow, social channel config) | ✅ `docs/OPERATIONS_RUNBOOK.md` |
| Compliance checklist | ✅ `docs/COMPLIANCE_CHECKLIST.md` |
| Vietnamese first-pass key copy | Deferred — out of scope for Day 7 |
| Real API-FOOTBALL sync in prod | Deferred — connector ready, key in Render |
| Configure real Zalo/Telegram links | Deferred — via admin API per runbook |

## Recommended Day 8

- LLM (Kimi/DeepSeek) AI explanation generation — only after banned-word output filter in place.
- Configure real Zalo/Telegram channels via admin API.
- Trigger API-FOOTBALL real sync in production.

**Do not** wire LLM in Day 7. LLM (Kimi/DeepSeek) for AI explanation generation
is Day 8 — and only after a banned-word output filter is in place.
