# Giành Cup · MVP 7-Day Public Operating Loop Plan

_Version: Day 7 baseline (MVP v0.7) · Created: 2026-06-06_

Goal: take **Giành Cup MVP v0.7** from "feature-complete" into a **7-day public
operating-validation loop** for the Vietnam-first SEA market.

This is an **execution / validation plan** — no new product features, no LLM,
no payments, no bots, no UGC, no new pricing, no API shape changes.

Live URLs:
- Frontend: https://worldcup2026-izid.onrender.com
- Backend: https://worldcup2026-api-71n6.onrender.com

Compliance floor (carry every day): 不做博彩 · 不做现金投注 · 不承诺命中 · 不承诺收益 ·
MTC 仅平台积分（不可提现/不可转让/不可交易）· 排行榜是连胜/积分榜，不是收益榜。

---

## Day 1 — Online Acceptance & Baseline Stability

**Frontend full click-through:**
- [ ] Home page: 今日 AI 最强信号 / 简表 / 爆冷风险 TOP3 / 战绩状态 render & navigate.
- [ ] Detail page: AI 结论卡, 胜率, LINEUP WATCH, 解锁 CTA.
- [ ] Report page: features / trend / tactics / verdict.
- [ ] Token page: wallet, check-in, FAN STREAK, rankings fallback, MTC statement.
- [ ] Community page: channel matrix, intel flow, Content Studio storage badge, subscribe.

**Backend endpoint verification:**
- [ ] `GET /api/v1/health` → `status: ok`, betting/withdrawal flags `false`.
- [ ] `GET /api/v1/matches` + `GET /api/v1/matches/{id}` → shapes unchanged.
- [ ] `GET /api/v1/assets/status` → r2_configured / public_base_url_set.
- [ ] `GET /api/v1/social/channels` → channel list.
- [ ] `GET /api/v1/rankings` + `GET /api/v1/users/1/streak` → empty-safe + disclaimer.

**Infra & responsive:**
- [ ] Render backend logs reviewed (no recurring 500s, no secret leakage).
- [ ] Mobile 390px (iPhone) layout check.
- [ ] Mobile 430px (iPhone Pro Max) layout check.
- [ ] No horizontal overflow on any page.

**Exit criteria:** all pages reachable, no white screens, no console errors, no overflow.

---

## Day 2 — Data Source Validation

- [ ] `POST /admin/sync/fixtures` (admin token) → fixtures upsert count logged.
- [ ] `POST /admin/sync/results` (admin token, `{league_id, season}`) → finished
      fixtures pulled, `MatchResult` upserted, settlement auto-run.
- [ ] `POST /matches/{id}/refresh` → baseline predictor re-runs, probs sum to 100.
- [ ] `GET /performance/summary` + `GET /performance/daily` → track record populated.
- [ ] Record the **mock vs real mode boundary**: behavior when `API_FOOTBALL_KEY`
      absent (graceful `0/0/0`) vs present; `VITE_USE_MOCK=true/false` frontend behavior.

**Exit criteria:** real-mode sync path verified end-to-end OR documented graceful
degradation when key/fixtures unavailable.

---

## Day 3 — Operating Content Preparation (manual templates, no LLM)

Prepare reusable **human-authored** templates (LLM wiring is Day 8, out of scope):
- [ ] 今日 AI 三场速览模板 (3-match daily brief).
- [ ] 爆冷风险短图文案模板 (upset-risk short graphic copy).
- [ ] 临场修正推送模板 (T-30min lineup correction push).
- [ ] 赛后复盘模板 (post-match review).

Each template must:
- Use「AI 倾向 / AI 数据观点」framing — never result promises.
- Carry the disclaimer where 战绩/命中/连胜 appears.
- Pass the forbidden-word scan.

**Exit criteria:** 4 templates drafted, compliance-checked, ready to fill per match.

---

## Day 4 — Community Configuration

- [ ] Configure real **Zalo** link (if available) via `POST /admin/social/channels/upsert`.
- [ ] Configure real **Telegram** link (if available) via the same endpoint.
- [ ] Facebook / TikTok set as **content distribution entries** (status as appropriate).
- [ ] Verify `click_social_channel` event tracking fires (`POST /events/track`).
- [ ] Check `GET /community/heat` reflects interactions.

Priority order: Zalo → Telegram → Facebook → TikTok. No real tokens in source/docs.

**Exit criteria:** at least primary channel(s) live; click tracking + heat confirmed.

---

## Day 5 — MTC & Retention Validation

- [ ] Check-in flow (`POST /tokens/checkin`) → MTC credited, balance updates.
- [ ] Free challenge join (`POST /challenges/{id}/join`).
- [ ] Admin settle (`POST /admin/challenges/settle`, options `A/B/neutral`).
- [ ] Streak increments on correct, resets on miss, unchanged on neutral.
- [ ] Rankings reflect updated streaks (sort: current → best → mtc_earned).
- [ ] MTC reward credited (+10 correct; +20 at streak 3; +80 at streak 7).
- [ ] 不可提现 / 不可转让 / 不可交易 statement present on Token + Community pages.

**Exit criteria:** full check-in → challenge → settle → streak → rankings loop verified;
MTC remains platform-points-only with compliance statement intact.

---

## Day 6 — Public MVP Compliance Check

Run `docs/COMPLIANCE_CHECKLIST.md` end-to-end:
- [ ] Forbidden-word scan clean (`下注/稳赚/必中/跟单/购彩/回报率/返奖/收益承诺/现金奖池/投注/包赢/必赢`).
- [ ] `提现` scan — only `不可提现` allowed; standalone flagged & fixed.
- [ ] AI copy non-promise framing verified.
- [ ] Rankings confirmed non-earnings board.
- [ ] Community/social entries confirmed non-gambling entries.
- [ ] 战绩/命中/连胜 disclaimer present everywhere required.
- [ ] MTC statement present; health flags `false`.

**Exit criteria:** every checklist item signed off.

---

## Day 7 — Small-Traffic Operating Trial

- [ ] Select **3 matches** and generate operating content from Day 3 templates.
- [ ] Publish to private domain / test group (Zalo / Telegram).
- [ ] Record metrics: clicks, social-channel entries, unlock CTA conversions, user feedback.
- [ ] Summarize issues encountered (UX, content, compliance, performance).
- [ ] Output **Day 8 recommendations**: AI explanation / LLM (Kimi/DeepSeek) integration
      plan — must ship behind a banned-word output filter before any LLM goes live.

**Exit criteria:** trial run completed, metrics + issues logged, Day 8 LLM proposal drafted.

---

## Hard boundaries (entire loop)

- No LLM wiring (Day 8+, behind banned-word filter).
- No real-money payments.
- No bots.
- No UGC / user uploads.
- No new pricing tiers.
- No changes to `/matches`, `/matches/{id}`, `/reports/{id}` response shapes.
- New capability → new tables + new endpoints; admin writes token-protected.
- Never log/commit secrets (`API_FOOTBALL_KEY`, `R2_SECRET_ACCESS_KEY`, `ADMIN_API_TOKEN`).
