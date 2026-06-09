# Scout Intelligence Rewrite — Implementation Evidence

**Verdict: PASS** (engineer self-verification). Frontend-only; no backend / API shape / DB change.
Real-device operator screenshot verification still to follow (Harness-X Stage 5).

_Date: 2026-06-08 · Plan: `docs/DATA_BACKED_SCOUT_INTELLIGENCE_REWRITE_PLAN.md` (Owner-approved)._

## 1. What shipped (frontend only)
- **ReportPage**: Evidence Strip (signal sources + data-mode caption) · **Scout verdict** (persona
  rename + hook line) · factor **Source / Impact / Interpretation** rows · **Contrarian** section ·
  **Watch before kickoff** section.
- **DetailPage**: condensed Evidence Strip · Scout verdict hook · **Contrarian teaser** above the paywall.
- **FeatureBars**: each factor now shows Signal (label) · Impact (signed %) · Source (pill) · Interpretation.
- **i18n**: `dict.ts` scout keys (zh/vi/mm/en); `viMapping.ts` + `mmMapping.ts` new
  `factorSource` / `factorInterpretation` maps + `scoutHook` / `contrarian` / `watch` (keyed by zh
  matchup, generic fallback). vi/mm/en fall back to localized generics — **never Chinese**.
- **CSS**: `.evidence-strip`, `.fbar-src`/`.fbar-interp`, `.scout-hook`, `.card.accent-amber`, `.lang-mm` tuning.

**Provenance honesty:** the Evidence Strip lists *kinds* of signals (labels only) with a
"Pre-match preview signals · not a real hit-rate" caption. No fabricated Elo/xG numbers were added;
factor % values come from the existing `Match.features[].value`. No API/DB fields were added.

## 2. Engineer self-verification (all PASS)
- **Build:** `tsc -b && vite build` ✅ (114ms). **Console:** no errors (Claude Preview).
- **Han scan (vi/mm interactive path = 0 Chinese core residual):**
  - `/report?lang=vi` 0 Han · `/detail?lang=vi` 0 Han · unlock modal vi 0 Han.
  - `/report?lang=mm` 0 Han (1243 Burmese) · `/detail?lang=mm` 0 Han · unlock modal mm 0 Han.
- **Scout layer renders:** evidence strip, scout verdict + hook, factor source/interpretation,
  contrarian, watch — verified in DOM + screenshots, vi and mm.
- **Price isolation:** vi `139.000₫` / `699.000₫` · mm `12,000 Ks` / `59,000 Ks` · zh RMB; no cross-leak.
  (Report page shows no price by design.)
- **zh regression:** `/report?lang=zh` scout layer in Chinese (情报来源 / 情报官结论 / 反方哨兵 /
  临场观察点), no Burmese/VND/MMK.
- **Forbidden-phrase scan:** no betting/guaranteed-hit/profit/cash wording in new scout copy
  (only pre-existing negations/disclaimers/comments match the scan).
- **Layout:** 0 horizontal overflow at 390 & 430 on the scout elements.
- **No backend/API/DB change** (git diff scoped to `frontend/` + `docs/` + `scripts/qa/`).

## 3. Screenshots (`docs/qa_screenshots/intelligence_rewrite/`)
`report-vi-390.png` · `report-vi-430.png` · `report-mm-390.png` · `report-mm-430.png` ·
`detail-vi-390.png` · `detail-vi-430.png` · `detail-mm-390.png` · `detail-mm-430.png` ·
`community-vi-390.png` · `community-mm-390.png` · `report-zh-regression-390.png` ·
`detail-vi-unlock-modal-390.png` · `detail-mm-unlock-modal-390.png`.
Captured full-page via `scripts/qa/intel_rewrite_shots.mjs` (zero-dep CDP driver; manual helper).

## 4. Operator verification (Stage 5 — pending, real device)
Operator to confirm on a real phone: `/detail` · `/report` · `/community` for `lang=vi` and `lang=mm` —
evidence strip, scout verdict, factor explanation, unlock→report path, Telegram/Zalo entry, bottom nav,
and any modal/toast/action sheet. Record under this doc; no screenshot = no PASS.

## 5. Boundaries honored
Frontend-only · no backend · no public API shape change · no DB schema change · no payment · no bot ·
no auto-publish · no scaling · no fabricated real data · LLM still draft-only · vi/mm never fall back to Chinese.
