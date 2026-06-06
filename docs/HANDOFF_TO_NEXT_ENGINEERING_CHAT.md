# Giành Cup Engineering Handoff

_Snapshot for the next Claude engineering chat. Read `CLAUDE.md` first, then this._
_Version: **MVP v0.6D** · origin/main synced · Day 6A–6D complete._

---

## 1. Product Positioning

**Giành Cup** is a **2026 World Cup AI Football Intelligence community** for the
**Vietnam-first** Southeast Asia market. It provides AI data viewpoints, win-probability
changes, risk notes, live (T-30min) lineup corrections, and fan engagement tasks.

It is **NOT a betting product**: no betting, no cash wagering, no guaranteed hits,
no promised returns. MTC is **platform loyalty points only** (not withdrawable /
transferable / tradable; not a financial asset). Rankings are a streak/points board,
never an earnings board.

User-facing brand line: **Giành Cup · 世界杯 AI 足球情报社区** —
副文案「不只看胜率，更看 AI 为什么这样判断。」
(Retired main brand `Nhà Tiên Tri AI` survives only in historical docs.)

---

## 2. Current Deployment

| Item | Value |
|------|-------|
| Frontend | https://worldcup2026-izid.onrender.com (Render) |
| Backend | https://worldcup2026-api-71n6.onrender.com (Render, FastAPI) |
| Database | Render PostgreSQL (local dev uses SQLite via `DATABASE_URL`) |
| R2 bucket | `giand-cup-assets` (configured & ready; `R2_PUBLIC_BASE_URL` empty = OK) |
| Repo | github.com/zhaojfifa/worldcup2026 |
| Branch | `main` (origin synced) |
| Backend version | `0.6.0` (app/main.py) |

Latest commits:
```
e7dcad4 feat(frontend): show fan streak and rankings fallback
0c3f730 feat(backend): add streak challenge and rankings
```

Local dev: Python 3.9; deps in `backend/requirements.txt` (boto3 lazy-imported).
`init_db()` auto-creates all tables on startup (create_all; only missing tables).
Seed: `python backend/scripts/seed.py` (idempotent social channels; demo user id=1, 520 MTC).

---

## 3. Completed Milestones (Day 2 → Day 6D)

**Day 2** — React/Vite frontend, 5 pages (Home / Detail / Report / Token / Community).

**Day 3** — FastAPI backend, PostgreSQL, Render deploy, frontend↔backend API loop.

**Day 4** — API-FOOTBALL connector; fixtures sync; baseline rules predictor;
`POST /matches/{id}/refresh`.

**Day 5** — Operational intelligence home: 今日 AI 最强信号 (C-pick), 今日比赛简表,
今日爆冷风险 TOP3, AI 情报战绩 status; detail AI 结论卡; `frontend/src/ops/derive.ts`.

**Day 5.5** — Giành Cup branding; 社群矩阵; Content Studio; data/social loop design.

**Day 6A** — `MatchResult`, `PredictionSettlement`, `/admin/sync/results`,
`/performance/daily`, `/performance/summary`.

**Day 6B** — R2 storage: bucket `giand-cup-assets`, `ContentAsset`, `/assets/status`,
`/admin/assets/upload`, `/assets/{id}`, `/admin/assets/{id}`.

**Day 6C** — `SocialChannel`, `MatchEngagement`, `/social/channels`,
`/admin/social/channels/upsert`, `/events/track`, `/community/heat`.

**Day 6D** — `UserStreak`, `ChallengeResult`, `/users/{user_id}/streak`, `/rankings`,
`/admin/challenges/settle`; TokenPage fan streak + ranking fallback.

---

## 4. Current API Inventory

**Core (shapes frozen — do not change):**
```
GET  /api/v1/health
GET  /api/v1/matches
GET  /api/v1/matches/{id}
GET  /api/v1/reports/{id}
```
**Data:**
```
GET  /api/v1/data-source/status
POST /api/v1/admin/sync/fixtures        (x-admin-token)
POST /api/v1/matches/{id}/refresh
```
**Performance:**
```
POST /api/v1/admin/sync/results          (x-admin-token)
GET  /api/v1/performance/daily
GET  /api/v1/performance/summary
```
**Assets:**
```
GET    /api/v1/assets/status
POST   /api/v1/admin/assets/upload       (x-admin-token)
GET    /api/v1/assets/{id}
DELETE /api/v1/admin/assets/{id}         (x-admin-token)
```
**Community:**
```
GET  /api/v1/social/channels
POST /api/v1/admin/social/channels/upsert (x-admin-token)
POST /api/v1/events/track
GET  /api/v1/community/heat
```
**Streak / rankings:**
```
GET  /api/v1/users/{user_id}/streak
GET  /api/v1/rankings
POST /api/v1/admin/challenges/settle      (x-admin-token)
```

> All `/admin/*` routes require header `x-admin-token` == `ADMIN_API_TOKEN`.
> If `ADMIN_API_TOKEN` is unset, admin routes are locked (always 401).

---

## 5. Day 6D Details

**New tables**
- `UserStreak` — `user_id` (unique), `current_streak`, `best_streak`,
  `last_participation_date`, `mtc_earned`. No cash fields.
- `ChallengeResult` — unique (`challenge_id`, `user_id`); `selected_option`,
  `actual_result`, `is_correct` (null = neutral/unresolved).

**Settlement rules** (`services/streak/streak_service.py`; label mirrors
`frontend/src/ops/derive.ts`):
- 主胜偏强/略占优 → home (single); 客胜偏强/略占优 → away (single);
  主队不败趋势 → {home,draw}; 客队不败趋势 → {away,draw}; 难分胜负 → neutral (not scored).
- Correct → `current_streak += 1`, `best = max(...)`; miss → reset to 0; neutral → unchanged.

**MTC reward** (platform points only, credited via `wallet_service._credit`,
logged in `TokenLog` as `challenge_reward`): +10 on correct; +20 extra when streak
reaches 3; +80 extra when streak reaches 7.

**Idempotency:** a challenge already settled for a user does NOT re-apply
streak/MTC on repeat calls (returns "该挑战已结算，未重复计入连胜或积分").

**Rankings sort:** `current_streak` desc → `best_streak` desc → `mtc_earned` desc.
Empty-safe; no fabricated users; display name = user nickname or `球迷 NNN`.

**TokenPage fallback:** API mode shows FAN STREAK + RANKINGS from live data;
mock mode / no data shows "连胜挑战建设中" / "排行榜建设中" (no fabricated board).
MTC compliance statement retained. `/matches` & `/reports` shapes unaffected.

---

## 6. Render Verification Needed (DO THIS FIRST next chat)

After backend redeploys (tables auto-create on startup):

```
curl https://worldcup2026-api-71n6.onrender.com/api/v1/users/1/streak
curl https://worldcup2026-api-71n6.onrender.com/api/v1/rankings
```
(Both should be empty-safe with the disclaimer.)

Admin settlement (replace token with the real Render `ADMIN_API_TOKEN`):
```
curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/challenges/settle \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_ADMIN_API_TOKEN" \
  -d '{"challenge_id":1,"user_id":1,"actual_result":"A","selected_option":"A"}'
```
Then re-check:
```
curl https://worldcup2026-api-71n6.onrender.com/api/v1/users/1/streak
curl https://worldcup2026-api-71n6.onrender.com/api/v1/rankings
```
(401 expected without / with wrong token. Seed channels first if needed:
run `python scripts/seed.py` in the Render shell.)

Frontend (after deploy, `VITE_USE_MOCK=false`):
- Token page shows **FAN STREAK** card.
- Token page shows **连胜排行榜**.
- mock mode does NOT fabricate a board.
- MTC compliance statement still present.

---

## 7. Recommended Day 7 — Operational Readiness & Public MVP Polish

Candidate tasks (do NOT wire LLM in Day 7):
1. Update `docs/MVP_STATUS.md` after Day 6D verification (already at v0.6D).
2. **Day 6D Render online verification** (see §6).
3. Giành Cup Vietnamese first-pass key copy.
4. Content Studio reads `/assets/status` → show "素材存储已连接".
5. Configure real Zalo / Telegram links via `/admin/social/channels/upsert`.
6. Real API-FOOTBALL fixtures/results sync verification.
7. Operations manual: daily prediction publishing flow.
8. Compliance checklist.
9. Codex v0.6D review.

**Day 8 (not earlier):** LLM (Kimi / DeepSeek) for AI explanation generation —
must ship behind a banned-word output filter.

---

## 8. Hard Rules (carry forward)

- Standard path `/Users/jackie/code/worldcup2026` (NOT `wordcup2026`).
- Never change `/matches`, `/matches/{id}`, `/reports/{id}` response shapes.
- New capability → new tables + new endpoints; admin writes token-protected.
- Graceful degradation when external services (API-FOOTBALL / R2) unconfigured.
- Never print/log `API_FOOTBALL_KEY`, `R2_SECRET_ACCESS_KEY`, `ADMIN_API_TOKEN`.
- Never commit `.env` / `.db`; keep `VITE_USE_MOCK` dual mode working.
- Forbidden wording + mandatory disclaimer + MTC statement (see CLAUDE.md §0/§8).
