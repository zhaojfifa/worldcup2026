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
