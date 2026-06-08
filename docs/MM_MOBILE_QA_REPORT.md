# Myanmar Mobile QA Report

**Verdict: PASS** (ready for human re-review)

---

## 2026-06-08 Recheck after operator feedback (BLOCKED_STATE_DIVERGENCE → resolved)

**Verdict: PASS WITH ISSUES** — both reported issues fixed and screenshot-verified; the residual
operator action (real-device Telegram open + live deploy) remains outside engineering.

### 1. Trigger
- Operator (real phone): Telegram link reachable on web but in-app browser → `ERR_CONNECTION_REFUSED`.
- Operator: `/detail?lang=mm` still shows Chinese residual.
- Previous QA said PASS → **state divergence** vs real feedback.

### 2. Blocked state
`BLOCKED_STATE_DIVERGENCE` — re-entered screenshot-driven QA before re-asserting PASS.

### 3. Screenshots (`docs/qa_screenshots/mm_mobile_recheck/`)
`detail-mm-before-390.png`, `community-mm-before-390.png` (before);
`community-mm-after-390.png`, `detail-mm-after-390.png`, `home-mm-after-390.png`,
`community-mm-after-430.png`, `detail-mm-after-430.png` (after);
`detail-vi-regression-390.png`, `home-zh-regression-390.png` (regression).
Telegram open/copy sheet + localized Report page were screenshot-verified live in Claude Preview.

### 4. Findings (root cause)
- **Chinese residual was on the REPORT page** (`/report`, reached via detail → unlock), which was
  **never localized** — hardcoded zh (`低/中/高`, feature labels, tactics, trend, verdict, footer).
  `/detail` itself scanned clean (0 Han) for all 3 matches; the operator's "detail" path includes
  the detail→unlock→report flow. (The live site may also lag the latest deploy.)
- **Telegram:** plain `window.open(t.me)` fails in some mobile in-app browsers (ERR_CONNECTION_REFUSED).

### 5. Fixes (frontend only; copy/mapping/UX)
- **ReportPage.tsx + FeatureBars.tsx** localized (zh/vi/mm/en) via `useCopy`/`useLocale` + loc helpers;
  added report dict keys (zh/vi/en/mm) and mapped report **trend labels + tactics_note** (3 seed
  matches) + feature labels in `viMapping.ts`/`mmMapping.ts` (unmapped → English, never Chinese).
  Verified: `/report?lang=mm` → 0 Han; sections all Burmese (screenshot).
- **CommunityPage.tsx**: active-channel click now opens an **open/copy fallback sheet** instead of a
  bare `window.open`: `Telegram ဖွင့်ရန်` (Open) / `Link ကူးရန်` (Copy, `navigator.clipboard` +
  toast/fallback) / `ပိတ်ရန်` (Close) + Burmese hint. Still uses the **API `public_url`** (not
  hardcoded); `click_social_channel` still tracked. Verified live (API mode) — screenshot shows the
  sheet with all three buttons + hint. vi/en strings added too.

### 6. Regression
- vi `/detail` Vietnamese, VND — unaffected. zh `/` Chinese, RMB — unaffected. Build passes; no console errors.

### 7. Verdict
**PASS WITH ISSUES** — engineering fixes verified by screenshot. Outstanding (non-engineering):
operator to confirm on a real device after deploy, and to validate the Telegram link opens via the
copy path. (Original 2026-06-07 PASS is superseded by this recheck.)

---

> **Re-verified 2026-06-07** alongside the Vietnamese sweep: mm Home/Detail/Token/Community
> re-scanned at 390×844 & 430×932 — Today Matches overlap stays fixed, no Chinese residual,
> no English long-form residual, MMK pricing intact, isolation holds. Still PASS.

## 1. Test time
2026-06-07.

## 2. Test environment
- Frontend dev server (Vite) at `http://localhost:4321` (also Claude Preview at :5173).
- **Data mode: `VITE_USE_MOCK` default (mock)** — seed matches (BRA-ARG, MAR-FRA, ESP-GER).
- Backend: **not touched** this round (no API calls required for layout QA).
- Screenshots: headless Chrome (`scripts/qa/mm_mobile_shots.sh`) + Claude Preview viewport captures.

## 3. Test viewports
- 390 × 844
- 430 × 932

## 4. Screenshot paths (`docs/qa_screenshots/mm_mobile/`)
`home-mm-390.png` · `detail-mm-390.png` · `token-mm-390.png` · `community-mm-390.png`
`home-mm-430.png` · `detail-mm-430.png` · `token-mm-430.png` · `community-mm-430.png`
`home-vi-390.png` · `home-zh-390.png` (regression)

## 5. Initial problems found
| # | Page | Issue |
|---|------|-------|
| 1 | Home · Today Matches | **Match rows overlapped** — long Burmese tendency/heat chips crushed the teams column (`teamsClientW≈28px` vs `scrollWidth≈126px`); chip text rendered on top of team names. |
| 2 | Home · Signal CTA | Right CTA (`ctaUnlock`) wrapped to 2 lines while left was 1 line (minor imbalance). |
| 3 | Community · channels | Channel card descriptions were **English** in mm (fallback), not Burmese. |

(Detail page Why / Risk factors / Premium list / verdict were already Burmese from the prior
"customer copy coverage" commit — confirmed by screenshot this round, no English-core residual.)

## 6. Fixes applied (frontend only)
- **`.lang-mm .simrow`** → `flex-wrap: wrap`; teams take row 1 (full width, `white-space: normal`),
  chips drop to row 2 (`flex: 0 0 100%`, padded to align, `flex-wrap`). Resolves overlap.
- **`copy/mm.ts`** → `ctaUnlock` shortened to `အပြည့်အစုံ ကြည့်ရန်` (one line).
- **`CommunityPage.tsx`** → added `CHANNEL_DESC_MM` (Burmese channel descriptions); `channelDesc()`
  now resolves zh→zh, vi→VI, **mm→MM** (English only as last resort).
- Myanmar density profile (`.lang-mm`) retained and unchanged otherwise.

## 7. Post-fix screenshot results
- **Home:** header (CN·VI·MY all visible) + hero + chips uncrowded; **Today Matches now two-row,
  no overlap** (teams 278px, `overflow:false`); signal CTAs equal height, single line each.
- **Detail:** verdict / win-prob / why / risk factors / lineup watch / premium list + CTAs all
  Burmese; MMK pricing (12,000 Ks / 390 MTC / 59,000 Ks/လ).
- **Token:** wallet / streak / missions / challenge / shop / rankings / MTC compliance all Burmese.
- **Community:** VIP 59,000 Ks/လ; channel descriptions Burmese; intel flow / benefits / Content
  Studio Burmese.

## 8. Chinese-residual check
**None** on mm customer surfaces (Home / Detail / Token / Community). The only bilingual zh·vi
string (operator "VI trial copy" badge) renders **English** in mm.

## 9. English-residual check
Only **allowed** product terms remain in mm: `AI`, `MTC`, `Premium`, `VIP`, team names
(`Brazil`/`Argentina`/…), numbers/percentages/scores, `vs`, `AI signal`, and decorative English
section subtitles (`WIN PROBABILITY`, `INTEL FLOW`, …). **No English long-form sentences or
English CTAs/risk-tags/benefit lists.**

## 10. zh / vi regression
- **zh:** Chinese + RMB (`39 元` / `199 元/月`); chips & copy Chinese; no MMK/₫/Burmese.
- **vi:** Vietnamese + VND (`139.000₫` / `699.000₫/tháng`); no MMK/Burmese.
- Currency isolation holds: vi has no MMK, mm has no ₫/¥/元, zh has no VND/MMK.
- `CN · VI · MY` switch + `localStorage giandcup_lang` persistence working; no console errors.

## 11. Unresolved / notes
- Saved PNGs are full-page headless captures (tall, scaled); per-viewport framing verified via
  Claude Preview at exact 390×844.
- The MTC-unlock CTA on Detail can wrap to 2 lines (full-width button) — acceptable, equal height.
- Dynamic data beyond the seed matches still falls back to **English** (by policy), never Chinese.
- Operational: **active Zalo/Telegram channel remains the trial blocker** (unchanged).

## 12. Sign-off
**PASS** — Myanmar mobile layout is uncrowded, match list overlap fixed, no Chinese residual, no
English long-form residual, MMK pricing correct, zh/vi unaffected, build passes, backend untouched.
Ready for human re-review.
