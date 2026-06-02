# MVP Status — Frontend ↔ Backend API Loop Baseline

_Last updated: 2026-06-02_

This document records the current verified state of the WorldCup 2026 AI
Match Intelligence MVP. It is a status snapshot only — no functional change.

---

## Live deployments

| Tier | URL |
|------|-----|
| Frontend (Render Static Site) | https://worldcup2026-izid.onrender.com |
| Backend (Render Web Service)  | https://worldcup2026-api-71n6.onrender.com |
| Database | Render PostgreSQL (seeded) |

Quick health checks:

```
GET https://worldcup2026-api-71n6.onrender.com/api/v1/health
GET https://worldcup2026-api-71n6.onrender.com/api/v1/matches
```

---

## ✅ Passing / Done

- **Frontend Render deployment** — built and serving.
- **Backend Render deployment** — FastAPI live, `/api/v1/health` OK.
- **PostgreSQL seed** — teams, matches, predictions, reports, challenges,
  demo user (id=1, 520 MTC) loaded successfully.
- **`/api/v1/matches`** — returns 3 matches (BRA–ARG, MAR–FRA, ESP–GER).
- **Frontend → Backend API loop** — with `VITE_USE_MOCK=false` the frontend
  fetches the live Render API; CORS preflight (`OPTIONS`) and `GET` both 200,
  no CORS errors.
- **Page navigation** — Home / Detail / Report / Token / Community all click
  through and render correctly online.
- **UI / Copy Enhancement** — intelligence-terminal look shipped (ticker, hero,
  capability bar, date scroller, LiveScore-style match cards, LINEUP WATCH,
  模型战术室 tactical room, 球迷任务中心, 临场情报 VIP).
- **mock ↔ API toggle** — `VITE_USE_MOCK=true/false` both verified.
- **Compliance** — no forbidden words; "提现" appears only in the
  "不可提现" disclaimer. MTC defined as platform loyalty points:
  **不可提现 · 不可转让 · 不可交易**.

---

## ⚠️ Current limitations / Not yet done

- **API-FOOTBALL fixtures auto-sync** — not implemented (connector stub only;
  `jobs/fixtures_sync.py` is a placeholder).
- **Baseline predictor** — not implemented; predictions are seed/mock data
  (`ai_provider = mock`, `model_version = mock-v1`).
- **Cloudflare R2** — not configured (env vars reserved only).
- **AI_PROVIDER** — still `mock` (DeepSeek / Kimi / Gemini keys configured
  but not wired into a real inference path).
- **Internationalization (multi-language)** — not implemented; UI is zh-CN only.

---

## Verified configuration

| Setting | Local dev | Render |
|---------|-----------|--------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://worldcup2026-api-71n6.onrender.com` |
| `VITE_USE_MOCK` | `true` | `false` |
| `DATABASE_URL` | `sqlite:///./worldcup2026.db` | Render PostgreSQL internal URL |
| `AI_PROVIDER` | `mock` | `mock` |
| `ENABLE_REAL_MONEY_BETTING` | `false` | `false` |
| `ENABLE_TOKEN_WITHDRAWAL` | `false` | `false` |

---

## Next milestones (planned)

1. API-FOOTBALL fixtures sync job (WC 2026, league/season) → upsert matches.
2. Pre-match lineup fetch (T-35 min) → auto-trigger `LiveCorrection`.
3. Baseline rules predictor in `services/modeling/` to replace seed predictions.
4. Switch `AI_PROVIDER` to a live provider for explanation text.
5. Cloudflare R2 wiring for media assets.
6. i18n scaffolding (zh-CN / en).
