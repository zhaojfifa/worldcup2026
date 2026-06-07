# Vietnamese Mobile QA Report

**Verdict: PASS** (ready for human re-review)

## 1. Test time
2026-06-07.

## 2. Test environment
- Frontend dev server (Vite) at `http://localhost:4321`; spot-checks via Claude Preview (:5173).
- **Data mode: `VITE_USE_MOCK` default (mock)** — seed matches (BRA-ARG, MAR-FRA, ESP-GER).
- Backend: **not touched**.
- Screenshots: headless Chrome (`scripts/qa/lang_mobile_shots.sh`); residual checks via DOM `innerText` scans in Preview.

## 3. Test viewports
- 390 × 844
- 430 × 932

## 4. Screenshot paths (`docs/qa_screenshots/vi_mobile/`)
`home-vi-390.png` · `detail-vi-390.png` · `token-vi-390.png` · `community-vi-390.png`
`home-vi-430.png` · `detail-vi-430.png` · `token-vi-430.png` · `community-vi-430.png`

## 5. Checks & results (all four pages)

| Check | Home | Detail | Token | Community |
|-------|------|--------|-------|-----------|
| Chinese residual | none | none | none | none |
| English long-form fallback | none | none | none | none |
| Price currency | — | `139.000₫` / `390 MTC` | `MTC` counts | `699.000₫/tháng` |
| RMB / ¥ / 元 | absent | absent | absent | absent |
| MMK / Ks | absent | absent | absent | absent |
| CTA Vietnamese, not crowded | ✅ | ✅ | ✅ | ✅ |
| Bottom nav (Trang chủ / Dự đoán AI / Điểm MTC / Cộng đồng) | ✅ | ✅ | ✅ | ✅ |

- **Detail:** verdict (`Kết luận AI`, `Chủ nhà có xu hướng bất bại`), win-prob
  (`Brazil thắng / Hòa / Argentina thắng`), why bullets, risk factors, lineup watch, premium
  list + CTAs — all Vietnamese; `Mở khóa lá bài chiến thuật AI · 139.000₫`.
- **Token:** wallet / streak / missions / challenge / shop / rankings / MTC compliance — Vietnamese.
- **Community:** `699.000₫/tháng`, channels, intel flow, benefits, Content Studio — Vietnamese.
- `localStorage giandcup_lang` switch (CN · VI · MY) works; no console errors.

## 6. Issues found / fixed
**None.** Vietnamese was already customer-ready from prior commits; this sweep is a confirmation
pass. No code change required for vi.

## 7. Language isolation (cross-check)
- **zh:** Chinese + RMB; no VND, no MMK, no Burmese.
- **vi:** Vietnamese + VND (₫); no Chinese, no MMK, no Burmese.
- **mm:** Burmese + MMK (Ks); no Chinese, no VND.
- Fallback: vi/mm unmapped → **English**, never Chinese.

## 8. Sign-off
**PASS** — Vietnamese mobile UI clean across Home/Detail/Token/Community at 390 & 430; VND pricing
correct; no Chinese/English-long-form residual; isolation holds; build passes; backend untouched.
