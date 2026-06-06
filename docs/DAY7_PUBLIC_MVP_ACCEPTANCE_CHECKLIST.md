# Giành Cup · Public MVP Acceptance Checklist (Day 7)

_Version: MVP v0.7 · Created: 2026-06-06_

Sign-off checklist before declaring the public MVP ready for the 7-day operating loop.
Pair with `docs/MVP_7_DAY_LOOP_PLAN.md` (execution) and `docs/COMPLIANCE_CHECKLIST.md` (compliance detail).

Live: Frontend https://worldcup2026-izid.onrender.com · Backend https://worldcup2026-api-71n6.onrender.com

---

## 1. Frontend Pages

- [ ] Home — signal / match list / upset TOP3 / track record render; navigation works.
- [ ] Detail — AI verdict card, win probability, LINEUP WATCH, unlock CTA.
- [ ] Report — features, trend history, tactics note, verdict summary.
- [ ] Token — wallet balance, check-in, FAN STREAK card, rankings, MTC statement.
- [ ] Community — channel matrix, intel flow, benefits, Content Studio storage badge, subscribe.
- [ ] Responsive 390px / 430px; no horizontal overflow; no white screens; no console errors.

## 2. Backend API

- [ ] `GET /health` → `status: ok`; `real_money_betting_enabled: false`; `token_withdrawal_enabled: false`.
- [ ] `GET /matches`, `GET /matches/{id}`, `GET /reports/{id}` → shapes unchanged.
- [ ] `GET /data-source/status` → connector/mock status reported.
- [ ] `GET /performance/daily`, `GET /performance/summary` → respond.
- [ ] All `/admin/*` routes → `401` without/with wrong `x-admin-token`.

## 3. Data Source

- [ ] `POST /admin/sync/fixtures` → fixtures upsert (no duplicate inserts).
- [ ] `POST /admin/sync/results` (`{league_id, season}`) → finished fixtures → MatchResult + settlement.
- [ ] `POST /matches/{id}/refresh` → baseline predictor; probabilities sum to 100.
- [ ] Graceful degradation when `API_FOOTBALL_KEY` absent (returns `0/0/0`, no crash).
- [ ] `VITE_USE_MOCK=true` and `=false` both work.

## 4. R2 / Content Storage

- [ ] `GET /assets/status` → `r2_configured` / `public_base_url_set` / `bucket` / `message`.
- [ ] Content Studio badge reflects live status (connected / pending / checking).
- [ ] No frontend upload path, no UGC, no R2 write from client.

## 5. Community / Social Entries

- [ ] `GET /social/channels` → channel list.
- [ ] `POST /admin/social/channels/upsert` (admin) → configures Zalo/Telegram/Facebook/TikTok.
- [ ] `click_social_channel` event tracked via `POST /events/track`.
- [ ] `GET /community/heat` → reflects interactions; empty-safe.
- [ ] No real channel links hardcoded in source.

## 6. MTC (Platform Loyalty Points)

- [ ] `POST /tokens/checkin` → MTC credited; balance updates.
- [ ] MTC statement「不可提现 · 不可转让 · 不可交易 · 不作为金融资产」present on Token + Community.
- [ ] No withdrawal / transfer / trading path anywhere.

## 7. Streak / Rankings

- [ ] `GET /users/{id}/streak` → empty-safe; includes disclaimer.
- [ ] `GET /rankings` → empty-safe; sort current → best → mtc_earned; includes disclaimer.
- [ ] `POST /admin/challenges/settle` (`A/B/neutral`) → correct increments, miss resets, neutral unchanged.
- [ ] Settlement idempotent (no double-credit on repeat).
- [ ] No fabricated users; no cash/earnings column.

## 8. Compliance

- [ ] Forbidden-word scan clean (see `docs/COMPLIANCE_CHECKLIST.md`).
- [ ] `提现` only inside `不可提现`.
- [ ] AI copy = data viewpoints, not result promises.
- [ ] Rankings = streak/points board, not earnings board.
- [ ] Community = AI intel entries, not gambling entries.
- [ ] 战绩/命中/连胜 surfaces carry the mandatory disclaimer.
- [ ] Brand unified to Giành Cup; no `Nhà Tiên Tri AI` in user-facing copy.

## 9. Operating Content

- [ ] 3-match daily brief template ready.
- [ ] Upset-risk short graphic template ready.
- [ ] T-30min lineup correction push template ready.
- [ ] Post-match review template ready.
- [ ] All templates compliance-checked; no LLM dependency.

## 10. Known Limitations (by design)

- `AI_PROVIDER=mock` — no LLM wired (Day 8+, behind banned-word filter).
- API-FOOTBALL real prod sync pending operator run (connector ready).
- Real Telegram/Zalo bots, share-card image generation, real UGC — not built.
- i18n (Vietnamese-first) not implemented; UI zh-CN with optional English subtitles.
- `R2_PUBLIC_BASE_URL` may be unbound → `public_url` null (acceptable).
- No real-money payments; no on-chain token.

---

## Sign-off

| Section | Status | Verified by | Date |
|---------|--------|-------------|------|
| 1. Frontend Pages | | | |
| 2. Backend API | | | |
| 3. Data Source | | | |
| 4. R2 / Storage | | | |
| 5. Community | | | |
| 6. MTC | | | |
| 7. Streak / Rankings | | | |
| 8. Compliance | | | |
| 9. Operating Content | | | |
| 10. Known Limitations reviewed | | | |
