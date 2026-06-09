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

## 4. Stage 5 — Operator Verification Checklist (real device)

**Status:** `operator_verification_status: pending`. Engineer self-verification (§2) is PASS, but the
**Final PASS is NOT granted until the operator screenshots below are captured and reviewed.**
Rule: **no screenshot = no PASS.** Save all shots to `docs/qa_screenshots/intelligence_rewrite_operator/`.

> **Operator gate UNBLOCKED (2026-06-09):** the **Historical Recap separation is complete** (PASS,
> frontend-only — `docs/HISTORICAL_RECAP_MODE_PROPOSAL.md` §9). **Home is no longer polluted by finished
> WC-2022 matches** (current surfaces filter `status !== 'finished'`; finished show only under a labelled
> Historical Recap · WC2022 surface). **Operator real-device verification may now proceed** on the
> un-polluted Home. `hit_rate` (42.2%) is **not in any customer UI**. The **recap-row → detail/report
> link is optional polish, NOT blocking** Stage 5 (banner-labelled flow is sufficient).

### 4.1 Paths to open on a real phone
**Vietnam (vi):** `/detail?lang=vi` · `/report?lang=vi` · `/community?lang=vi`
**Myanmar (mm):** `/detail?lang=mm` · `/report?lang=mm` · `/community?lang=mm`
(Live: `https://worldcup2026-izid.onrender.com/...` after deploy, or the local dev server.)

### 4.2 Required screenshots (each, for vi AND mm → save to `…/intelligence_rewrite_operator/`)
Suggested filenames: `{area}-{vi|mm}-{device}.png` (device = the operator's phone, e.g. `iphone13`).

| # | Capture | Where |
|---|---------|-------|
| 1 | Evidence Strip / Signal Sources | Detail + Report (top) |
| 2 | Scout verdict (persona + hook line) | Detail + Report |
| 3 | Factor source / impact / interpretation | Report (Key factors) |
| 4 | Contrarian / Risk watch | Detail (teaser) + Report |
| 5 | Watch before kickoff | Report |
| 6 | Unlock modal | Detail → tap unlock (MTC) |
| 7 | Report after unlock | after tapping "continue to report" |
| 8 | Telegram / Zalo entry | Community → tap channel |
| 9 | Bottom nav | any page |
| 10 | Any toast / modal / action sheet | check-in, copy-link, coming-soon |

### 4.3 Operator judgement criteria (answer per language)
- [ ] **Understandable?** (能不能看懂)
- [ ] **Reads like match intelligence, not generic "AI analysis"?** (是否像赛事情报)
- [ ] **Data sources + model basis visible?** (是否看到数据来源和模型依据)
- [ ] **Language natural for local operation?** (语言是否自然)
- [ ] **Page not crowded / no overlap?** (页面是否拥挤)
- [ ] **No Chinese residual on vi/mm?** (是否有中文残留)
- [ ] **No betting / 稳赚 / 必中 / 收益 / 现金 hints?** (博彩/收益暗示)
- [ ] **Willing to forward a screenshot to the group?** (是否愿意发群)
- [ ] **Willing to tap full report / join community?** (是否愿意解锁/进社群)

### 4.4 Result fields (operator fills, then Owner reviews)
```
operator_verification_status: pending   # pending | pass | pass_with_issues | fail
operator_feedback_vi: ""                # operator's words (vi path)
operator_feedback_mm: ""                # operator's words (mm path)
issues_found: ""                        # concrete problems (language / layout / redirect)
required_fix: ""                        # frontend-only fixes, if any
final_owner_decision: ""                # Owner's call after reviewing screenshots
```

> If issues are found, fixes stay **frontend-only** (copy / mapping / layout); any API/DB need must
> stop and return to Owner. Until `operator_verification_status` is `pass`/`pass_with_issues` **and**
> `final_owner_decision` is recorded, the sprint remains **PASS pending Stage 5**.

## 5. Boundaries honored
Frontend-only · no backend · no public API shape change · no DB schema change · no payment · no bot ·
no auto-publish · no scaling · no fabricated real data · LLM still draft-only · vi/mm never fall back to Chinese.
