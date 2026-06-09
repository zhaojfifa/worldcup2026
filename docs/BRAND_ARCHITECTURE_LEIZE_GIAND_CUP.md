# Brand Architecture — LEIZE (company) · Giành Cup (product)

_Created 2026-06-08 · Owner ruling: **Brand cleanup = GO.** Absorbs Vietnam operator feedback._

> **One line:** **LEIZE** is the company-level brand; **Giành Cup** is the football-intelligence
> **product** under **LEIZE AI**. **"Cloud" is NOT the main company brand** — only a future branch.

## 1. Company brand
- **Brand name:** **LEIZE**
- **Vietnamese legal-style name:** `CÔNG TY TNHH CÔNG NGHỆ SỐ LEIZE`
- **English name:** `LEIZE DIGITAL TECHNOLOGY CO., LTD`
  (long form: `LEIZE DIGITAL TECHNOLOGY COMPANY LIMITED`)

## 2. Naming decision (why not "Cloud")
- **Do not use "Cloud" as the main company brand.** "Cloud" is only a future business branch.
- **Reason:** "Cloud" narrows customer perception to **cloud infrastructure / SaaS only**. **LEIZE** is
  broader, more memorable, more international, and easier to expand across business lines.
- Customer-facing company identity = **LEIZE** (not "LEIZE Cloud").

## 3. Brand branches (business lines under LEIZE)
| Branch | Scope |
|--------|-------|
| **LEIZE AI** | AI solutions (incl. **Giành Cup** football intelligence) |
| **LEIZE Academy** | Training / education |
| **LEIZE Media** | MCN / content |
| **LEIZE Commerce** | Commerce |
| **LEIZE Cloud** | SaaS / API / data infrastructure (future branch only) |

## 4. Product relationship
- **Giành Cup is a football-intelligence product under LEIZE AI.**
- **Suggested external expression:**
  - `Giành Cup by LEIZE AI`
  - `A football intelligence product by LEIZE`
- The customer-facing **product** name stays **Giành Cup** (zh: 世界杯 AI 足球情报社区). A small
  "by LEIZE AI" endorsement line MAY later appear in the footer/about — **not implemented this round**
  (docs-only; no frontend rename).

## 5. What NOT to do
- ❌ Do **not** rename Giành Cup into "LEIZE Cloud" (or any Cloud-prefixed name).
- ❌ Do **not** put "Cloud" in the customer-facing **company** name.
- ❌ Do **not** confuse company brand (LEIZE) with product brand (Giành Cup).
- ❌ Do **not** change the product brand `Giành Cup` in the app this round.

## 6. Engineering notes (no code change this round)
- The frontend brand constant (`frontend/src/copy/zh.ts` → `GIAND_CUP_BRAND` / `BRAND`) and the
  product name **remain unchanged**. This document is a **positioning decision**, not a code change.
- If/when Owner approves a customer-facing "by LEIZE AI" endorsement, it would be a small **frontend
  copy** addition (footer/about) — localized vi/mm/zh/en, no API/DB change.

## 7. Summary (carry-forward)
- **LEIZE = company-level brand.** **Giành Cup = product brand** (under LEIZE AI).
- **Cloud = future branch, not the main brand.**
