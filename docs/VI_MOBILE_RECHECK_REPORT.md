# Vietnamese Mobile Recheck Report

**Verdict: PASS WITH ISSUES** — one Chinese residual found on the vi customer path and fixed
(frontend copy only); re-verified by screenshot. zh/mm unaffected; build passes; backend untouched.

_Date: 2026-06-08. Standard: same screenshot-driven QA as `docs/MM_MOBILE_QA_REPORT.md`._

---

## 1. Trigger

Based on Myanmar operator feedback, the Myanmar recheck found its real Chinese residual on the
**`/report`** page (reached via detail → unlock) — a page the original QA never opened. By the same
standard, **Vietnamese must be rechecked end-to-end, not just the home page**, with `/report`
explicitly in scope. This round re-scans the full vi customer path to confirm it is truly operable,
not just "home works".

## 2. Scope

- **Pages:** Home (`/`) · Detail (`/detail`) · **Report (`/report`)** · Community (`/community`) · Token (`/token`), all `?lang=vi`.
- **Viewports:** 390×844 and 430×932.
- **Data mode:** `VITE_USE_MOCK` default (mock) — seed matches (BRA-ARG, MAR-FRA, ESP-GER).
- **Method:** Claude Preview at exact viewport — DOM `innerText` residual scans (Han / Burmese /
  currency regex) + screenshots; saved PNGs via `scripts/qa/vi_mobile_recheck_shots.sh` (headless Chrome).
- **Backend / API / DB:** not touched.

## 3. Screenshot paths (`docs/qa_screenshots/vi_mobile_recheck/`)

vi path, both viewports:
`home-vi-390.png` · `detail-vi-390.png` · `report-vi-390.png` · `community-vi-390.png` · `token-vi-390.png`
`home-vi-430.png` · `detail-vi-430.png` · `report-vi-430.png` · `community-vi-430.png` · `token-vi-430.png`

Regression:
`home-mm-regression-390.png` · `report-mm-regression-390.png` · `home-zh-regression-390.png`

The community badge fix (before → after) was screenshot-verified live in Claude Preview at exact
390/430. Saved PNGs are full-page headless captures (tall, scaled); per-viewport framing verified in Preview.

## 4. Findings

| Page | Han | Burmese | VND | RMB/¥/元 | MMK/Ks | CTA/layout | Verdict |
|------|-----|---------|-----|----------|--------|-----------|---------|
| Home `/` | 0 | 0 | — (no price on home) | none | none | clean, no overlap | PASS |
| Detail `/detail` | 0 | 0 | `139.000₫`, `699.000₫/tháng` | none | none | clean | PASS |
| Report `/report` | 0 | 0 | — | none | none | clean | PASS |
| Community `/community` | **10 → 0 (fixed)** | 0 | `699.000₫/tháng` | none | none | clean, 0 overflow @430 | FIXED |
| Token `/token` | 0 | 0 | — (MTC counts) | none | none | clean | PASS |

- **Chinese residual (the one finding):** `/community?lang=vi` "VI TRIAL COPY" badge rendered the
  bilingual operator string **`越南语试跑文案已就绪 · Đã chuẩn bị nội dung thử nghiệm tiếng Việt`** (10 Han)
  on the **public** community page. The Myanmar recheck had already forced this same badge to
  English-only for mm; vi was still leaking Chinese to the customer. **Root cause:** `VI` block in
  `frontend/src/i18n/dict.ts` deliberately kept the bilingual zh·vi value ("operator-facing"), but the
  badge is on the public customer surface — and vi must never show Chinese.
- **English long-form fallback:** none. Only **allowed** decorative English subtitles paired with a
  Vietnamese label (`AI TACTICAL ROOM`, `WIN PROBABILITY`, `KEY FACTORS`, `RISK RADAR`, `TACTICS`,
  `PROB TREND`, `CONTENT STUDIO`, `INTEL FLOW`, `DAILY MISSIONS`, `PREDICTION CHALLENGE`, …) plus product
  terms (`AI`, `MTC`, `VIP`, team names, scores/percentages, `vs`). No English sentences / CTAs.
- **Burmese leakage:** none on any vi page.
- **VND pricing:** correct — `139.000₫` (report unlock) / `699.000₫/tháng` (VIP). No RMB/¥/元, no MMK/Ks.
- **MTC statement (Token & Community):** Vietnamese and complete —
  `MTC … không thể rút tiền, không thể chuyển nhượng, không thể giao dịch và không phải tài sản tài chính`;
  Token adds `không cam kết lợi nhuận · không liên kết cá cược`. **No betting / guaranteed-hit /
  profit-promise wording** (Token explicitly states `không cam kết lợi nhuận`).
- **Disclaimer / compliance footer:** present in Vietnamese on Report/Token/Community
  (`Chỉ phân tích dữ liệu AI · Không phải dịch vụ cá cược · Không nhận cược tiền mặt · MTC không thể rút tiền`).
- **Layout:** no overlap, no text overlap, no button crowding; 0 horizontal overflow at 430.

### Community / Zalo (special check)
- **Zalo card:** Vietnamese, status **`Sắp mở`** (coming soon) — expected; Zalo still pending active.
- **Telegram on vi:** also **`Sắp mở`** — the **active Myanmar Telegram does NOT pollute the vi page**;
  vi does not treat the Myanmar Telegram as a primary entry. ✅
- **Active-channel fallback UX:** `CommunityPage.tsx` already resolves the open/copy sheet strings from
  the locale dict (`tgOpen` "Mở Telegram" / `tgCopy` "Sao chép liên kết" / `tgHint` "Nếu không mở được,
  hãy dán liên kết vào Telegram hoặc trình duyệt." / `tgClose` "Đóng") — so if Zalo/Telegram goes active
  for vi later, a Vietnamese open/copy fallback is already in place and reusable. No code needed now.

## 5. Fixes

Frontend copy only (no mapping/layout change needed; layout already clean):

- **`frontend/src/i18n/dict.ts`** — `VI` block `viBadge` changed from the bilingual
  `'越南语试跑文案已就绪 · Đã chuẩn bị nội dung thử nghiệm tiếng Việt'` to Vietnamese-only
  `'Đã chuẩn bị nội dung thử nghiệm tiếng Việt'`. zh keeps its Chinese value (internal management);
  en/mm keep the English EN value. Re-verified: `/community?lang=vi` → **0 Han**, badge reads
  `Đã chuẩn bị nội dung thử nghiệm tiếng Việt`.
- **`scripts/qa/vi_mobile_recheck_shots.sh`** — new QA helper that captures the full vi path
  **including `/report`** (the gap the original vi sweep had) plus mm/zh regression shots.

No `frontend/src/copy/vi.ts` or `viMapping.ts` change was required — Report factor labels, tactics,
trend, and verdict already resolve to Vietnamese for the seed matches.

## 6. Regression

- **zh:** `/?lang=zh` Chinese (456 Han); `/community?lang=zh` RMB `199 元/月`; no VND/MMK/Burmese.
  zh "VI TRIAL COPY" badge **unchanged** (still bilingual — internal management). ✅
- **mm:** `/community?lang=mm` Burmese (1264), MMK `59,000 Ks/လ`, 0 Han; badge English
  (`Vietnamese trial copy ready`). `/report?lang=mm` 0 Han, Burmese (821) — the Myanmar Report fix holds. ✅
- **Isolation:** the vi edit touched only the `VI` block; zh/mm/en `viBadge` resolution is unchanged.
  Fallback rule intact: **vi/mm → en, never zh.** No console errors.

## 7. Verdict

**PASS WITH ISSUES.** The vi customer path is operable end-to-end (Home/Detail/Report/Community/Token);
the single Chinese residual (community VI-trial badge) is fixed and screenshot-verified; VND pricing,
MTC statements, disclaimers, and Zalo/Telegram coming-soon states are correct; zh/mm unaffected; build
passes; backend untouched.

**Outstanding (non-engineering, unchanged):** Vietnam **Zalo still pending active** (operator upsert);
the active **Myanmar Telegram** remains Myanmar-only and correctly shows `Sắp mở` on vi.

> Rule honored: **no screenshot, no PASS.** Evidence in `docs/qa_screenshots/vi_mobile_recheck/`.
