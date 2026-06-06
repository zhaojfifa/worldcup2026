# Giành Cup Accelerated MVP Review

_Version: MVP v0.7 · Review date: 2026-06-06 · Baseline: main @ `89cdf13`_

Unified review of Accelerated Day A / B / C (see `docs/MVP_7_DAY_LOG.md`).
No new features, no architecture, no LLM — verdict and next-step ruling only.

---

## 1. Executive Verdict

| Item | Ruling |
|------|--------|
| **Overall status** | **GO WITH CONDITIONS** |
| Enter real small-traffic trial? | **Conditional** — only after ≥1 `active` community channel (Zalo or Telegram) is configured |
| Enter Day 8 LLM? | **Not full build** — enter **Day 8 Prep** only |
| **Biggest blocker** | **No `active` community channel** (Zalo/Telegram both `coming_soon`, `public_url=null`) → real user承接 not closed |

**Condition to clear GO:** configure at least one `active` social entry, **Zalo first**,
then re-run the click→heat check and dispatch the 3 prepared messages to a test group.

---

## 2. Day A Review · Service and Data

| Area | Result |
|------|--------|
| Core API (health/matches/reports) | ✅ 200, shapes unchanged |
| R2 storage | ✅ `r2_configured=true`, `public_base_url_set=true`, `R2 ready` |
| Social / community heat | ✅ healthy; heat aggregation keyed on `match_id` |
| Streak / rankings | ✅ healthy; disclaimers present; non-earnings board |
| Data source | ⚠️ `api_football_configured=true`, `connector_status=ok`, **`mock_mode=true`** |
| Predictor refresh | ✅ win_prob sums 100, confidence/risk recomputed, `updated_at` refreshed, shape unchanged |
| Admin sync (write) | ✅ locked 401 without token (real run = Render Shell) |

**Must be explicit:** API-FOOTBALL is **reachable but `mock_mode=true`** — matches/results are
**seed data**, `requests_used=0`. **The small-traffic trial can only validate copy and
community承接 — it does NOT validate real prediction accuracy.**

---

## 3. Day B Review · Copy and Community

| Check | Result |
|-------|--------|
| 3 operating messages produced | ✅ `docs/OPERATION_TRIAL_MESSAGES.md` |
| 3-second scannable | ✅ short lines, emoji anchors, star confidence |
| Strong conclusion | ✅ each has a clear AI 倾向 + 一句话理由 |
| Risk note present | ✅ every message |
| Compliance | ✅ forbidden-word self-check clean; disclaimer included |
| Community entry status | ❌ all `coming_soon`, no real link / test group |

**Key judgment:** **No `active` Zalo / Telegram → real-dispatch承接 NOT completed.**
Messages are prepared and compliant; dispatch is blocked only by missing channel config.

---

## 4. Day C Review · Retention and MTC

| Check | Result |
|-------|--------|
| wallet/1 | `balance:160`, `total_earned:550`, `total_spent:390` |
| streak/1 | `current_streak:2`, `best_streak:2`, `mtc_earned:20` |
| rankings | `#1 Demo Fan`; non-earnings board |
| MTC reward logic | ✅ +10/+20/+80 rules verified in Day 6D PASS |
| disclaimer | ✅ present on streak + rankings |
| 非收益榜 | ✅ no cash column |
| 不可提现声明 | ✅ MTC = 平台积分 · 不可提现 · 不可转让 · 不可交易 |

**Judgment:** MTC retention loop is **trial-ready**, but **no real user feedback has occurred**
(no dispatch yet). Idempotent settlement already proven; new `challenge_id=3` settle is an
optional operator Render-Shell step.

---

## 5. Operational Readiness Scorecard

| Dimension | Score (/5) | Note |
|-----------|-----------|------|
| Service stability | **4.5** | All endpoints 200, shapes frozen, refresh valid |
| Data readiness | **3.0** | Connector ready but `mock_mode=true`; live sync not run |
| Copy attractiveness | **4.0** | 3 strong, compliant, scannable messages; no live feedback yet |
| Community readiness | **2.0** | No `active` channel; no real link / test group |
| Retention loop | **4.0** | MTC/streak/rankings work; awaiting real users |
| Compliance readiness | **4.5** | Scan clean, disclaimers + MTC statement present, checklist in place |
| LLM readiness | **3.0** | Human templates exist; filter/schema not yet designed |

**Weakest link: Community readiness (2.0)** — the single gate to a real trial.

---

## 6. Go / No-Go Conditions

**Must have (to enter real small-traffic trial):**
1. ≥1 `active` social channel, **Zalo first**.
2. ≥3 reviewed messages. ✅ (done)
3. community heat records `click_social_channel` + `match_id`. ✅ (verified)
4. MTC / streak / rankings healthy. ✅ (verified)
5. Compliance scan clean. ✅ (verified)
6. Mock-data boundary stated; no claim of real model hit-rate. ✅ (stated)

→ **Only condition #1 is outstanding.**

**Nice to have:**
1. Telegram test group.
2. Real API-FOOTBALL sync run.
3. Content Studio share-card.
4. Vietnamese short-copy variants.

---

## 7. Day 8 LLM Decision

**Ruling: do NOT full-build LLM yet. Enter Day 8 Prep only.**

**Day 8 Prep (design/archive only — no code into production):**
- LLM output field design.
- Banned-word output filter design.
- Prompt template design.
- Human copy-sample archive (from `OPERATION_COPY_TEST_PACK.md` / `OPERATION_TRIAL_MESSAGES.md`).
- Schema for `reason_bullets` / `social_copy` / `recap_copy`.

**Day 8 Prep does NOT include:** auto-publish · unreviewed auto-generated copy ·
auto-write to production · paid-content automation.

**Enter Day 8 Full Build only when ALL hold:**
- ≥1 real small-traffic trial completed.
- ≥1 `active` community承接.
- Human feedback samples exist.
- Compliance filter process stable.

---

## 8. Immediate Next Actions

1. Operator stands up a **Zalo or Telegram test group**.
2. Configure it `active` via `POST /admin/social/channels/upsert` (Render Shell, `$ADMIN_API_TOKEN`).
3. Re-test `click_social_channel` + `match_id` → confirm heat increments.
4. Dispatch the 3 prepared messages (prefer **vi** for Vietnamese groups) following
   `docs/VI_OPERATION_TRIAL_RUNBOOK.md`; record real feedback in `docs/OPERATION_TRIAL_RESULTS.md`.
5. Prepare the **Day 8 Prep** design doc — **no LLM code**.

---

## 9. Known Risks

- `mock_mode=true` → **must not advertise real prediction accuracy.**
- Community not `active` → conversion funnel not closed.
- Copy has **not reached real users** → no validated attractiveness data.
- **No full Vietnamese version** (zh-CN primary, light EN titles).
- LLM not wired → AI explanations are still templated.
- Payment not wired → commercial conversion unvalidated.

---

## 9b. Localization status (updated 2026-06-06)

- **Vietnamese UI upgraded from trial badge to OPERATIONAL MVP language mode.**
  `/?lang=vi` now renders the core user-visible copy of Home / Detail / Token / Community
  (+ header & nav) in Vietnamese — no longer中越混合. A lightweight `CN | VI` switch in the
  header toggles reactively; choice persists in `localStorage (giandcup_lang)`; default zh.
- **Dynamic match data** (team names, AI tendency, risk level, risk notes, reason bullets,
  live-correction text) is handled by **frontend rule-based mapping** (`i18n/viMapping.ts`)
  for the current seed/demo matches; unmatched text falls back to the original. No backend
  change, no API shape change, no external translation API.
- **i18n structure:** `i18n/useLocale.ts` (`zh | vi | mm`), `i18n/dict.ts`
  (`ZH` source + `VI` override, vi→zh fallback; `mm` reserved → resolves to zh, no button),
  `i18n/viMapping.ts` (dynamic data). Borrows the per-locale copy-map + fallback idea from the
  `apolloveo-auto` i18n reference (structure only).
- **Trial copy** still available: `docs/OPERATION_TRIAL_MESSAGES_VI.md` + dispatch runbook
  `docs/VI_OPERATION_TRIAL_RUNBOOK.md`. **Next blocker remains an `active` Zalo / Telegram channel.**
- **Burmese (my/mm) is deferred** — type slot reserved, no copy, no UI button. The
  `apolloveo-auto` reference (uses `mm`) can be reused later for the `my`/`mm` locale.
- **Full i18n is still deferred** — only operation-trial core surfaces are covered; no
  site-wide framework, no translation of every dynamic field beyond the seed mapping.

---

## 10. Final Recommendation

> **Giành Cup MVP v0.7 已具备工程可运营基础，但尚未完成真实私域承接；建议先补 Zalo/Telegram
> active channel，再执行小流量试跑。LLM 暂进入准备阶段（Day 8 Prep），不直接生产接入。**
