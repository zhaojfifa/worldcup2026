# MVP Status — Giành Cup (worldcup2026)

_Last updated: 2026-06-06 · Version: **MVP v0.6D**_

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

Latest commits:
```
e7dcad4 feat(frontend): show fan streak and rankings fallback
0c3f730 feat(backend): add streak challenge and rankings
```

---

## ✅ Deployed / done

- Frontend + backend on Render; PostgreSQL live; API loop verified (CORS OK).
- mock ↔ API dual mode (`VITE_USE_MOCK`) verified.
- Day 6A–6C verified online (per prior human PASS rulings).
- All new capabilities are **additive**: `/matches`, `/matches/{id}`,
  `/reports/{id}` response shapes unchanged across Day 4→6D.
- Brand unified to Giành Cup across header / hero / signal / verdict.

## ⚠️ Awaiting deploy verification

- **Day 6D Render online verification** (streak / rankings / admin settle) —
  **first task of the next chat.** Commands in the handoff doc §6.

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

## Recommended Day 7 (Operational Readiness & Public MVP Polish)

1. Day 6D Render online verification.
2. Vietnamese first-pass key copy.
3. Content Studio reads `/assets/status` (show storage connected).
4. Configure real Zalo / Telegram channel links via admin upsert.
5. Real API-FOOTBALL fixtures/results sync verification.
6. Operations manual: daily prediction publishing flow.
7. Compliance checklist.
8. Codex v0.6D review.

**Do not** wire LLM in Day 7. LLM (Kimi/DeepSeek) for AI explanation generation
is Day 8 — and only after a banned-word output filter is in place.
