# Giành Cup · Multilingual Operation Policy

_Version: MVP v0.7 · Created: 2026-06-06 · **Authoritative language-strategy baseline for all future engineering.**_

This document is the source of truth for language, fallback and pricing policy.
Engineers must follow it; deviations require an explicit ruling recorded here and in `CLAUDE.md`.

---

## 1. Language roles

| Role | Language | Notes |
|------|----------|-------|
| **Default system / fallback language** | **English (`en`)** | All non-Chinese locales fall back to English, never Chinese. |
| **Internal management language** | **Chinese (`zh`)** | Engineering, ops planning, internal docs. Default UI when no locale chosen. |
| **Primary customer operation language** | **Vietnamese (`vi`)** | Vietnam-first market; full MVP UI ready. |
| **Secondary customer operation language** | **Burmese / Myanmar (`mm`)** | MVP language mode started; core UI in Burmese, rest → English. |
| **API / admin / config / schema / data contract** | **English** | Field names, enums, admin payloads, env vars stay English/ASCII. |

User-selectable UI buttons today: **CN · VI · MY**. `en` is the internal fallback layer
(not exposed as its own button).

---

## 2. Fallback chains

Defined in `frontend/src/i18n/useLocale.ts`:

```
zh: ['zh']
en: ['en', 'zh']
vi: ['vi', 'en']
mm: ['mm', 'en']
```

- **Customer locales (vi, mm) must NOT fall back to Chinese.** They fall back to English.
- `en` may fall back to `zh` only as a last-resort safety (the EN layer is complete, so this
  should never trigger in practice).
- Static copy resolution: `frontend/src/i18n/dict.ts` (`ZH` source + `EN` complete layer +
  `VI`/`MM` overrides).
- Dynamic data (team names, AI tendency, risk notes, etc.): `frontend/src/i18n/viMapping.ts`
  — `zh`→original, `vi`→Vietnamese (English generic if unmapped), `en`/`mm`→English.

---

## 3. Pricing localization

Defined in `frontend/src/i18n/pricing.ts`. **Never hardcode a currency symbol in a page.**

| Locale | Currency | Single unlock | Monthly VIP | Token |
|--------|----------|---------------|-------------|-------|
| zh | RMB | 39 元 | 199 元/月 | 390 MTC |
| en | USD | US$5.5 | US$28/month | 390 MTC |
| vi | VND (₫) | 139.000₫ | 699.000₫/tháng | 390 MTC |
| mm | MMK (Ks) | 12,000 Ks | 59,000 Ks/လ | 390 MTC |

- **RMB / ¥ is never shown to vi or mm customers.** vi shows only VND; mm shows only MMK/Ks.
- **MM pricing is "MM MVP operation test pricing"** — 12,000 Ks / 59,000 Ks/လ matches the live
  page exactly (`frontend/src/i18n/pricing.ts`). It is a test figure, **not** a real-time FX rate
  and **not** a final commercial price; revisit before any payment integration.
- These are **MVP operational prices, not real-time exchange rates.** Payment is out of scope / deferred.
- MTC is a platform point count — identical across all locales (390 MTC).

---

## 4. Compliance across languages

Every locale must preserve the compliance floor:
- MTC = platform points only (non-withdrawable / non-transferable / non-tradable / not a financial asset).
- Mandatory disclaimer on 战绩 / 命中 / 连胜 surfaces.
- No betting / guaranteed-profit wording. Forbidden terms per language:
  - zh: 下注 / 稳赚 / 必中 / 跟单 / 购彩 / 回报率 / 返奖 / 收益承诺 / 现金奖池 (提现 only in 不可提现)
  - vi: chắc thắng / đảm bảo thắng / cá cược / đặt cược / kiếm tiền / lợi nhuận chắc chắn
    (negation form "Không phải dịch vụ cá cược" is allowed)
  - en/mm: no betting / guaranteed-win / cash-wager wording.

---

## 5. Deferred (do NOT build yet)

- **Full professional localization** (every dynamic field, marketing-grade copy review).
- **LLM translation / generation** — deferred until after a real manual operation trial
  produces feedback. When enabled, it must ship behind a banned-word output filter.
- **Real payment** integration in any currency.
- Burmese **full** translation (only MVP core surfaces are Burmese today; rest is English).

---

## 6. Related files & docs

- Code: `i18n/useLocale.ts`, `i18n/dict.ts`, `i18n/pricing.ts`, `i18n/viMapping.ts`,
  `copy/zh.ts`, `copy/en.ts`, `copy/vi.ts`, `copy/mm.ts`.
- Operation copy: `docs/OPERATION_TRIAL_MESSAGES_VI.md`, `docs/MM_OPERATION_TRIAL_MESSAGES.md`,
  `docs/VI_OPERATION_TRIAL_RUNBOOK.md`.
- State: `CLAUDE.md` (Language & Operation Policy), `docs/MVP_STATUS.md`,
  `docs/ACCELERATED_MVP_REVIEW.md`.

> **Operational blocker (unchanged):** no `active` Zalo / Telegram channel yet — the real
> customer trial (vi and mm) cannot dispatch until one is configured via admin upsert.

## 7. Readiness (acceptance 2026-06-06)

- **Vietnamese (vi):** ready for MVP customer trial. UI + VND verified across Home/Detail/Token/Community.
- **Burmese (mm):** ready for MVP customer trial. UI (core Burmese, rest English) + MMK verified
  across Home/Detail/Token/Community; **no Chinese residual; no ¥/元/₫.** Trial URL:
  `https://worldcup2026-izid.onrender.com/?lang=mm`.
- **Language isolation verified:** zh→RMB only, vi→VND only (no MMK), mm→MMK only (no ¥/元/₫);
  CN·VI·MY switch + localStorage persistence working; missing keys fall back to English.

## 8. Myanmar density profile (policy)

- **Burmese cannot use the same copy density as Vietnamese.** Myanmar glyphs are taller and
  words longer, so `mm` uses a **separate, shorter copy set** (`frontend/src/copy/mm.ts`) and a
  dedicated **`.lang-mm` CSS density profile** (`frontend/src/styles/global.css`). The root node
  carries `data-lang` + `lang-${locale}` (`Layout.tsx`) so CSS can scope by locale.
- **Rule:** Burmese copy must stay **shorter than Vietnamese**; long explanation belongs on the
  detail page, not home cards. **Concise English product terms (AI / Risk / Update / MTC) are
  allowed** in the Myanmar customer UI.
- **zh / vi / en must not be affected** — all density rules are scoped to `.lang-mm`.

## 9. Burmese translation acceptance (2026-06-06)

- **Operation team accepted the Burmese translation** (clear, no mojibake). mm is upgraded from
  "framework + English fallback" to **customer-ready Burmese**: core UI uses Burmese; dynamic
  data (team outcomes, AI tendency, risk level/tags, risk/free notes, reason bullets,
  live-correction text) mapped to Burmese in `frontend/src/i18n/mmMapping.ts`.
- **English remains the system fallback** only for unmapped dynamic data; **Chinese is never a
  customer-side fallback.** Concise English product terms (AI / MTC / Premium / VIP / Update /
  team names / numbers) are intentionally kept.
- Burmese trial URL: `https://worldcup2026-izid.onrender.com/?lang=mm` — page copy is
  customer-ready for trial after deployment. Active social channel remains the shared blocker.
- **Screenshot-driven mobile QA is mandatory for BOTH customer languages (vi & mm) before PASS:**
  any vi/mm layout change must be **screenshot-verified at 390×844 and 430×932** (helper
  `scripts/qa/lang_mobile_shots.sh`, headless Chrome, not a prod dependency) and recorded in
  `docs/VI_MOBILE_QA_REPORT.md` / `docs/MM_MOBILE_QA_REPORT.md`. The `.lang-mm` density profile is
  mandatory; zh/vi/mm isolation remains mandatory.
- **Final policy summary:** English = system / fallback / API / admin / schema language ·
  Chinese = China-team internal management · Vietnamese = primary customer operation language ·
  Burmese = secondary customer operation language · vi/mm fall back to **English**, never Chinese ·
  pricing separated by locale (zh RMB · en USD · vi VND · mm MMK).
- **2026-06-07: vi & mm mobile QA PASS; language gate CLOSED.** Next phase:
  `docs/NEXT_PHASE_DATA_MODEL_SOCIAL_LLM_PLAN.md`. Active Zalo/Telegram channel remains the blocker.
- **2026-06-08: vi recheck (Myanmar standard) — PASS WITH ISSUES → fixed.** Full vi path incl. `/report`
  re-scanned at 390/430. Found one Chinese residual: the community **"VI TRIAL COPY" badge** rendered the
  bilingual zh·vi string on the public page. **Reinforced rule: operator-labelled badges on public
  customer pages are still customer surface — vi must never show Chinese.** Fixed by making the VI
  `viBadge` Vietnamese-only (`dict.ts`); zh keeps its internal bilingual value, en/mm stay English.
  vi/mm → en fallback (never zh) re-confirmed. Evidence: `docs/VI_MOBILE_RECHECK_REPORT.md` +
  `docs/qa_screenshots/vi_mobile_recheck/`. Recheck helper: `scripts/qa/vi_mobile_recheck_shots.sh`.
