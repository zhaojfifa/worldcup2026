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

- **RMB / ¥ is never shown to vi or mm customers.**
- These are **MVP operational prices, not real-time exchange rates.** Revisit before any
  real payment integration (payment is out of scope / deferred).
- MTC is a platform point count — identical across all locales.

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
