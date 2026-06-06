# Giành Cup · MVP 7-Day Loop — Execution Log

_Companion to `docs/MVP_7_DAY_LOOP_PLAN.md`. One section per day; append as the loop runs._

---

## Day 1 — Online Acceptance & Baseline Stability

- **Verification time:** 2026-06-06 ~04:33 UTC
- **Baseline:** main @ `ddf952d` (MVP v0.7)
- **Frontend:** https://worldcup2026-izid.onrender.com
- **Backend:** https://worldcup2026-api-71n6.onrender.com
- **Verification level:** live API (curl), deployment reachability, source-level page/brand/compliance review.
  (Interactive device click-through and pixel-level 390/430px QA are recommended as an operator step;
  structural/responsive checks done at source level — see Mobile section.)

### 1. Frontend pages

| Item | Result | Notes |
|------|--------|-------|
| Deployment reachable | ✅ HTTP 200 | `GET /` returns 200 |
| Home page | ✅ source present | `HomePage.tsx` (signal / list / upset / record) |
| Detail page | ✅ source present | `DetailPage.tsx` (verdict / win-prob / lineup / unlock) |
| Report page | ✅ source present | `ReportPage.tsx` (features / trend / tactics / verdict) |
| Token page | ✅ source present | `TokenPage.tsx` (wallet / check-in / streak / rankings / MTC) |
| Community page | ✅ source present | `CommunityPage.tsx` (channels / flow / storage badge / subscribe) |
| Bottom navigation | ✅ present | `.bottom-nav` in `Layout.tsx` |
| Giành Cup brand (in-app) | ✅ present | header `{BRAND.name} · {BRAND.zhRole}` = "Giành Cup · 世界杯 AI 足球情报社区" |
| Content Studio storage status | ✅ wired | reads `/assets/status`; live badge "素材存储已连接 · 公开素材访问已启用" |

### 2. Backend API (all HTTP 200)

| Endpoint | Result | Key fields |
|----------|--------|-----------|
| `GET /health` | ✅ 200 | `status:ok`, `ai_provider:mock`, betting=false, withdrawal=false |
| `GET /matches` | ✅ 200 | 3 matches (BRA-ARG, MAR-FRA, ESP-GER); shape unchanged |
| `GET /matches/1` | ✅ 200 | detail + `live_correction`; shape unchanged |
| `GET /reports/1` | ✅ 200 | features / trend_history / tactics / verdict; shape unchanged |
| `GET /assets/status` | ✅ 200 | `r2_configured:true`, `public_base_url_set:true`, bucket `giand-cup-assets` |
| `GET /social/channels` | ✅ 200 | 4 channels (zalo/telegram/facebook/tiktok), all `coming_soon`, `public_url:null` |
| `GET /community/heat` | ✅ 200 | empty-safe; top_matches populated |
| `GET /users/1/streak` | ✅ 200 | `current_streak:2`, `best_streak:2`, `mtc_earned:20`; disclaimer present |
| `GET /rankings` | ✅ 200 | `#1 Demo Fan` (streak 2, mtc 20); disclaimer present; non-earnings board |

> Note: streak=2 / mtc=20 / rankings #1 Demo Fan confirm the **Day 6D settlement persisted on Render** —
> validates the prior "Day 6D Render verification: PASS" ruling.

### 3. Behavior event tracking

| Step | Result |
|------|--------|
| heat BEFORE | match1 interactions=2, total=2 |
| `POST /events/track` (click_social_channel, match 1, zalo) | ✅ `{ok:true, message:"recorded"}` |
| `POST /events/track` (view_match, match 2) | ✅ `{ok:true, message:"recorded"}` |
| heat AFTER | match1=3, match2=1, total=4, `updated_at` refreshed |

Event tracking → community heat aggregation verified working end-to-end. No PII captured.

### 4. Render log check

- No Render CLI available locally → full log review is an operator step via the Render dashboard.
- **Proxy signal:** every API call in this run returned HTTP 200; no 500s observed; no secret/token
  values appear in any response body. `health` reports `env:development` (expected on current service).
- **Action for operator:** confirm in Render dashboard logs — no startup errors, no recurring 500s,
  no `API_FOOTBALL_KEY` / `R2_SECRET_ACCESS_KEY` / `ADMIN_API_TOKEN` printed.

### 5. Mobile (390 / 430px)

- App container is **mobile-first**, capped at `--maxw: 430px` with `box-sizing: border-box`
  (`global.css`) → no horizontal page overflow at 390px or 430px.
- `overflow-x: auto` occurrences are **intentional** horizontal chip/tab strips, not page overflow.
- Pixel-level on-device QA recommended as operator step; structure confirms no overflow risk.

### 6. Compliance (per `docs/COMPLIANCE_CHECKLIST.md`)

| Check | Result |
|-------|--------|
| Hard forbidden words (下注/稳赚/必中/跟单/购彩/回报率/返奖/收益承诺/现金奖池/投注/包赢/必赢) | ✅ No real violations |
| `提现` standalone scan | ✅ Clean — only `不可提现` in `frontend/src` |
| MTC statement present | ✅ `MTC 为平台积分 · 不可提现 · 不可转让 · 不可交易 · 不作为金融资产` |
| Disclaimer present | ✅ `历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。` (streak + rankings carry it) |
| Rankings = streak/points board, not earnings | ✅ no cash column; sort current→best→mtc |
| Community = AI intel entries, not gambling | ✅ channel descriptions are intel/discussion framing |
| AI copy = viewpoints, not result promises | ✅ "AI 倾向 / AI 数据观点" framing |

> Forbidden-word grep surfaced 7 lines, **all benign on inspection**:
> (a) policy comments in `derive.ts` / `zh.ts` that *list* the banned words as a negative instruction;
> (b) negation disclaimers containing "现金投注" only inside `不提供现金投注` / `非博彩`
> on Token / Report / Community pages. No line promotes betting. Per checklist this is a
> guidance-style scan requiring human interpretation — interpreted and cleared.

### 7. Issues found

| # | Severity | Issue | Recommendation |
|---|----------|-------|----------------|
| 1 | Minor (non-blocking) | Browser tab `<title>` in `frontend/index.html` is still `世界杯 AI 情报终端` (retired "情报终端" wording; not Giành Cup). In-app header is correct. | Update `<title>` to a Giành Cup line in a later polish PR (not this verification-only round). |
| 2 | Info | Social channels all `coming_soon` with `public_url:null`. | Expected — real Zalo/Telegram links are Day 4 of the loop. |
| 3 | Info | `health` reports `env:development`. | Confirm intended `APP_ENV` for the public service in Render. |

No blocking issues found.

### 8. Day 2 readiness

**✅ Cleared to proceed to Day 2 (Data Source Validation).**
All endpoints healthy, shapes unchanged, event loop working, compliance clean.
Only a minor stale `<title>` and two informational items to carry forward.

---

## Accelerated Day A · Service and Data Verification

_(Per `docs/MVP_ACCELERATED_OPERATION_LOOP.md` — collapses original Day 1 + Day 2 core.)_

- **Verification time:** 2026-06-06 ~07:20–07:21 UTC
- **Baseline:** main @ `43e84cd` (MVP v0.7)
- **Backend:** https://worldcup2026-api-71n6.onrender.com

### 1. Core service

| Endpoint | Result | Notes |
|----------|--------|-------|
| `GET /health` | ✅ 200 | `ai_provider: mock`; `real_money_betting_enabled: false`; `token_withdrawal_enabled: false` |
| `GET /matches` | ✅ 200 | 3 matches; **shape unchanged** |
| `GET /matches/1` | ✅ 200 | detail + `live_correction`; **shape unchanged** |
| `GET /reports/1` | ✅ 200 | features/trend/tactics/verdict; **shape unchanged** |

### 2. Storage / R2

| Field | Value |
|-------|-------|
| `r2_configured` | `true` |
| `public_base_url_set` | `true` |
| `bucket` | `giand-cup-assets` |
| `message` | `R2 ready` |

### 3. Social / community + event

| Step | Result |
|------|--------|
| `GET /social/channels` | ✅ 200 — 4 channels, all `coming_soon`, `public_url: null` |
| `GET /community/heat` (before) | match1=3, match2=1, total=4 |
| `POST /events/track` (`click_social_channel`, **no match_id**) | ✅ `{ok:true,"recorded"}` |
| `GET /community/heat` (after) | **unchanged** (total=4, updated_at same) |

> **Finding (behavior):** community heat aggregation is keyed on `match_id`. A channel-only
> event with **no `match_id`** is accepted and recorded, but does **not** increment match heat
> (Day 1's event included `match_id` and did increment). Not a bug — expected aggregation design.
> For the small-traffic trial, channel-entry attribution must pass a `match_id` to show in heat.

### 4. Streak / rankings

| Endpoint | Result |
|----------|--------|
| `GET /users/1/streak` | ✅ 200 — `current_streak:2`, `best_streak:2`, `mtc_earned:20`; disclaimer present |
| `GET /rankings` | ✅ 200 — `#1 Demo Fan` (streak 2, mtc 20); disclaimer present; **non-earnings board** |

MTC remains platform loyalty points (no cash field anywhere).

### 5. Data source

`GET /data-source/status`:
```json
{ "api_football_configured": true, "connector_status": "ok",
  "mock_mode": true, "plan": "unknown",
  "requests_used": 0, "requests_limit": 100,
  "message": "API-FOOTBALL reachable" }
```

- API-FOOTBALL **key configured** and connector reports **reachable**.
- **`mock_mode: true`** — predictions/matches are still served from **seed/mock data**,
  not live API-FOOTBALL fixtures. `requests_used: 0` confirms no live pulls yet.

**Admin sync (write path) — locked, real run is operator step:**

| Call (no token, from local) | Result |
|------|--------|
| `POST /admin/sync/fixtures` | ✅ `401 "Invalid or missing x-admin-token"` (locked) |
| `POST /admin/sync/results` | ✅ `401 "Invalid or missing x-admin-token"` (locked) |

> Real sync must be run in **Render Shell** with `$ADMIN_API_TOKEN` (never printed).
> Expected per runbook: graceful `inserted/updated/skipped/settled` counts; `0/0/…` when no
> finished fixtures or in mock conditions. Not executed this round (no token locally) —
> **carry to operator** as the one remaining Day A item.

### 6. Predictor refresh

| Check | Result |
|-------|--------|
| `POST /matches/1/refresh` | ✅ 200 |
| win_prob sum | ✅ `49+26+25 = 100.0` |
| confidence | ✅ recomputed `62.0 → 61.0` (reasonable) |
| risk_level | ✅ present; recomputed `medium → high` (risk_note updated) |
| `updated_at` | ✅ refreshed to `2026-06-06T07:21:09Z` |
| response shape | ✅ **unchanged** (same keys) |

### 7. Mock / real boundary (classification)

| Capability | Status | Operational impact |
|-----------|--------|--------------------|
| Core read APIs (health/matches/reports) | **Real** (live service, seed data) | None — usable for trial |
| R2 storage | **Real** (configured, public URL bound) | None |
| Social channels | **Real endpoint**, demo data (all `coming_soon`, no URLs) | Needs Day B admin upsert of real/test links |
| Community heat + events | **Real** (aggregation works; keyed on match_id) | Attribution needs match_id |
| Streak / rankings / MTC | **Real** (Day 6D settlement persisted) | None |
| Baseline predictor / refresh | **Real compute**, on **seed** fixtures | Numbers are model-on-mock, not live results |
| API-FOOTBALL data | **Configured but `mock_mode: true`** | Matches/results are seed; live sync not yet run |
| LLM (`ai_provider`) | **mock** | By design — Day 8 only |

### 8. Issues found

| # | Severity | Issue |
|---|----------|-------|
| 1 | Info / decision | `mock_mode: true` — system runs on seed data despite API-FOOTBALL key configured. Operator must run `admin/sync/fixtures` + `admin/sync/results` in Render Shell to pull live data (or consciously keep mock for the trial). |
| 2 | Info | Channel-only `events/track` (no `match_id`) doesn't move community heat — pass `match_id` for attribution. |
| 3 | Minor (carryover) | Stale browser `<title>` `世界杯 AI 情报终端` (from Day 1). |
| 4 | Info | `health` `env: development` on the public service. |

No blocking bugs. No functional code changed.

### 9. Day B / C readiness

**✅ PASS — cleared to proceed to Day B (content + community承接) and Day C prep.**
Core APIs, R2, heat, streak/rankings all healthy; shapes unchanged; refresh valid;
compliance clean. Mock/real boundary is **clear and documented**. The only open Day A
item is the operator-run live sync in Render Shell (optional for the trial — mock data
is sufficient to test copy attractiveness and community承接).

---

## Accelerated Day B/C · Copy, Community and Retention Trial

_(Per `docs/MVP_ACCELERATED_OPERATION_LOOP.md` — Day B + Day C combined.)_

- **Verification time:** 2026-06-06 ~07:26 UTC
- **Baseline:** main @ `c43773a` (MVP v0.7)

### 1. Social channel current status

| Channel | Status | public_url |
|---------|--------|------------|
| zalo | `coming_soon` | `null` |
| telegram | `coming_soon` | `null` |
| facebook | `coming_soon` | `null` |
| tiktok | `coming_soon` | `null` |

- **No real Zalo / Telegram link or test group available this round.**
  → Recorded as **「待运营建立测试群」**. **No fabricated link configured.**
- `admin/social/channels/upsert` is ready (admin token, Render Shell). When a real
  link / test group exists, set `status:"active"` + `public_url` (Zalo first, then
  Telegram; Facebook/TikTok stay `coming_soon`). **Real links never hardcoded in source.**

### 2. Channel click attribution (with match_id)

| Step | Result |
|------|--------|
| heat BEFORE | total=4, match1=3, match2=1 |
| `POST /events/track` (`click_social_channel`, `channel_name:zalo`, **`match_id:1`**) | ✅ `{ok:true,"recorded"}` |
| heat AFTER | **total=5**, **match1=4**, match2=1, `updated_at` refreshed |

✅ **Confirmed:** with `match_id`, the channel click **does** increment community heat
(Day A finding resolved at the data level). `hot_channels` unchanged (zalo/telegram/facebook/tiktok).
Heat payload contains **no personal info** — only match_id, team names, interaction counts,
channel names. ✅ 不记录个人信息.

### 3. Operating trial messages

- **Path:** `docs/OPERATION_TRIAL_MESSAGES.md` — 3 ready-to-send posts:
  1. 今日 AI 三场速览 (Zalo/Telegram)
  2. 爆冷风险 TOP1 摩洛哥 vs 法国 (TikTok/Telegram)
  3. 临场修正 巴西 vs 阿根廷 (real `live_correction` data; Telegram/Zalo)
- All three pass the forbidden-word self-check; each carries risk note + disclaimer.
- **Source pack:** `docs/OPERATION_COPY_TEST_PACK.md` (4 templates).

### 4. MTC / streak / rankings recheck

| Endpoint | Result |
|----------|--------|
| `GET /tokens/wallet/1` | `balance:160`, `total_earned:550`, `total_spent:390`, `last_checkin_date:2026-06-02` |
| `GET /users/1/streak` | `current_streak:2`, `best_streak:2`, `mtc_earned:20`; disclaimer present |
| `GET /rankings` | `#1 Demo Fan` (streak 2, mtc 20); disclaimer present; non-earnings board |
| `POST /admin/challenges/settle` (no token, local) | ✅ `401` locked |

- MTC remains **平台积分 · 不可提现 · 不可转让 · 不可交易** (no cash field anywhere).
- New challenge settlement (`challenge_id=3`) is an **operator step in Render Shell** with
  `$ADMIN_API_TOKEN` (not run locally — admin route correctly locked). Idempotency already
  proven in the Day 6D PASS log (repeat settle does not re-credit streak/MTC).

### 5. Small-traffic trial status

- **Not yet dispatched.** Reason: no `active` community channel (no real Zalo/Telegram link
  or test group available this round). Messages are **prepared and compliance-checked**, ready
  to send the moment a channel is configured `active` via admin upsert.
- Trial uses **seed/mock match data** by design — validates copy attractiveness + community
  承接, **not** real model accuracy. Dispatch metrics table is in `OPERATION_TRIAL_MESSAGES.md`.

### 6. Minor fix applied

- `frontend/index.html` `<title>` updated `世界杯 AI 情报终端` → `Giành Cup · 世界杯 AI 足球情报社区`
  (index.html only; no business logic touched). Resolves Day 1/Day A carryover issue #3.

### 7. Issues found

| # | Severity | Issue |
|---|----------|-------|
| 1 | Blocking for dispatch only | No real Zalo/Telegram link / test group → trial not yet sent. Operator action: configure an `active` channel via admin upsert. |
| 2 | Info | `mock_mode=true` — trial validates copy/community, not model accuracy. |
| 3 | Carryover | Live `admin/sync/*` + `challenge_id=3` settle still pending operator Render Shell run (optional). |

No blocking bugs in the service itself.

### 8. Day D readiness

**✅ Cleared to proceed to Day D (Unified Review).**
Channel attribution verified (with match_id), 3 compliant trial messages prepared,
MTC/streak/rankings healthy, compliance clean, title fixed. Open operational item:
configure a real/test community channel `active` to actually dispatch the trial — this is
an **operator setup step**, not an engineering blocker, and will be a key input to the
Day D decision on community承接.
