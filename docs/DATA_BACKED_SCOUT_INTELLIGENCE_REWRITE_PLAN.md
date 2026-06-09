# Data-backed Scout Intelligence Rewrite — PLAN (Owner review pending)

_Created 2026-06-08 · Harness-X flow: **PLAN → Owner review → Implementation → Engineer self-verify →
Operator screenshot verify → Final review.** This document is **Stage 1 (Plan only)**. No feature code
is written or pushed in this round._

> **Headline finding (grounds the whole plan):** the rewrite can be done **frontend-only — NO public
> API shape change and NO DB schema change.** The Evidence Strip is localized copy; the per-factor
> Source / Model-impact / Interpretation are **derived on the frontend from the existing finite factor
> label set** (`Match.features[].label`) via new offline mappings; the Scout persona is a copy rename.
> If, during implementation, we find a field that genuinely needs the backend, we will stop and return
> to Owner before touching the API/DB.

---

## 1. Problem Statement
Today's Detail/Report read as a "calm AI analysis page", not an intelligence product:
- **Data sources are invisible.** The user sees probabilities and bars but not *what evidence* drives
  them (Elo, xG, lineup, squad value, travel, community heat). There is no "sources" surface.
- **Model factors look decorative.** `FeatureBars` shows `label + value%` only (see
  `frontend/src/components/FeatureBars.tsx`). No source, no causal interpretation — so "+18%" reads
  like a sticker, not a modelled signal.
- **Copy is flat.** "AI 分析 / AI 判断 / Kết luận AI" is generic; it states a lean but creates no tension.
- **No explicit contrarian/risk angle.** `riskNote`/`tacticsNote` exist but the *upset/contrarian* case
  is not foregrounded; the user never sees "why this could be wrong".
- **No localized Scout persona.** There is no recognizable intelligence voice (a "Scout") in vi/mm.
- **Weak unlock/community motivation.** The user is not shown *why* the full report or the community is
  worth it (what extra evidence/live-correction they get).

## 2. Product Goal
Turn the page into **Giành Cup Scout** — a data-backed football intelligence read:
- A named **Scout** voice (not generic "AI 分析"), with localized vi/mm expression.
- A visible **data evidence chain** (Evidence Strip / Signal Sources).
- **Model factor explanations**: each factor shows Source → Model impact → one-line interpretation.
- An explicit **contrarian / upset risk** line (compliant, non-betting).
- **Live observation points** (what to watch near kickoff) that justify community/unlock.
- Output an operator can **screenshot / forward / post** as-is, in natural vi/mm.

## 3. Page Scope
This round (heavy focus): **DetailPage** + **ReportPage**, plus the **CommunityPage entry copy** that the
unlock/verdict CTA points to. Docs: **`OPERATION_COPY_LIBRARY_VI_MM.md`**, **`LLM_DRAFT_COPY_REVIEW_LOG.md`**.
HomePage is **out of scope** this round (follow-up). No change to Token page.

## 4. Data Evidence Layer (Evidence Strip / Signal Sources)
A compact strip near the top of Detail and Report listing the **signal sources** behind the read.

| Locale | Evidence-strip text |
|--------|---------------------|
| zh | 情报来源：Elo 实力差 · 近期 xG · 伤停/首发 · 身价差 · 旅行/气候 · 社区热度 |
| vi | Nguồn tín hiệu: Elo · xG gần đây · đội hình/chấn thương · giá trị đội hình · di chuyển/khí hậu · độ nóng cộng đồng |
| mm | Signal sources: Elo · recent xG · lineup/injury · squad value · travel/weather · community heat |

**Provenance honesty — each source is tagged, no fabricated real data:**
| Source | Provenance class | Backed by today |
|--------|------------------|-----------------|
| Elo strength diff | **derived signal** | from win_prob/confidence (model) |
| recent xG | **seed/operator preview** | seed factor `近 5 场 xG 表现`; real only after data sync |
| lineup/injury | **seed/operator preview** + **derived** | seed factors + `liveCorrection` |
| squad value | **seed/operator preview** | static/seed; not live |
| travel/weather | **seed/operator preview** | static/seed; not live |
| community heat | **real interaction** | `community/heat`, `events/track` (real) |

- The strip renders **labels only** (it advertises *what kinds of signals* feed the model), and is
  **not** a claim of live data. A small caption states data mode: when `data_mode=mock/seed`, show a
  neutral "preview signals" note; never imply real accuracy/hit-rate.
- **No fabricated numbers** are added. We do not invent Elo/xG values we don't have; the strip is a
  qualitative source list + the factors already present.

## 5. Model Reasoning Layer
Upgrade each factor row (Report `FeatureBars`, and a condensed form on Detail) to a 4-part structure,
**all derived on the frontend from the existing factor `label`** (finite seed set) — no new API fields:

```
Signal:         <factor label>            (exists today: featureLabelLoc)
Source:         <source category>         (NEW: factor-label → source map, per locale)
Model impact:   <+/- value%, direction>   (exists today: f.value; phrased as "lifts/【cuts】 home win prob")
Interpretation: <one-line localized why>  (NEW: factor-label → interpretation map, per locale)
```

Worked example (seed match 1, factor `巴西右路突破` / "Brazil right-flank breaks"):
- **Signal:** Brazil right flank pressure
- **Source:** lineup/injury + tactical signal
- **Model impact:** Brazil win probability lifted (+8%)
- **Interpretation (vi):** Hàng thủ cánh trái của Argentina là điểm chịu áp lực.
- **Interpretation (mm):** Argentina ၏ ဘယ်ခြမ်းခံစစ်သည် ဖိအားခံရသည့်နေရာ ဖြစ်သည်။

**Mapping & fallback:** Source and Interpretation are keyed by the **Chinese factor label** (same keys
already used by `featureLabelViMap`/`featureLabelMmMap`/`featureLabelEnMap`). For any **unmapped** factor:
Source falls back to a generic localized "model signal", Interpretation falls back to a generic localized
line (English for mm/en, Vietnamese for vi) — **never Chinese**. Numbers come from `f.value` only.

## 6. Scout Persona Layer
Soften "AI 分析" into a **Scout** voice (persona name kept in English; explanations localized):

| Element | zh (internal) | vi | mm |
|---------|---------------|----|----|
| Brand voice | Giành Cup 情报官 | Giành Cup Scout | Giành Cup Scout |
| Verdict | Scout 结论 | Scout verdict | Scout verdict |
| Contrarian | 反方哨兵 | Scout risk note | Risk watch |
| Live radar | 临场雷达 | Scout tín hiệu | Risk watch |

- Touch points: the verdict header (`aiVerdict` dict key + `BRAND.verdictTitle` decorative subtitle),
  the section labels on Report (verdict / risk / tactics), and the Detail verdict card.
- **Constraints:** keep vi/mm short (the `.lang-mm` density profile already exists); persona *name* may
  stay English; the *explanation* must be natural vi/mm; **zh internal management wording unchanged** in
  meaning (still the China-team view, just relabelled "情报官/Scout 结论").

## 7. Copy Rewrite Strategy
Replace flat statements with **tension-but-compliant** scout lines.
**Forbidden (unchanged):** 稳赢/必中/下注/购彩/收益/现金/保证命中/跟单 · chắc thắng/đảm bảo thắng/cá cược/
đặt cược/kiếm tiền/lợi nhuận chắc chắn · လောင်းကစား (except negation). Enforced by `compliance.scan`.
**Allowed framing:** risk signal · upset watch · pre-match correction · scout verdict · model viewpoint ·
data-backed watch point.

Example (verdict line):
- ❌ "AI 当前认为巴西更强。"
- ✅ zh: "这场不是看巴西强不强，而是看阿根廷后防能撑多久。"
- ✅ vi: "Không phải câu hỏi Brazil mạnh hơn không. Câu hỏi là hàng thủ Argentina chịu được bao lâu."
- ✅ mm: "မေးခွန်းက Brazil အားကောင်းလား မဟုတ်ပါ။ Argentina ခံစစ် ဘယ်လောက်ကြာကြာ တောင့်ခံနိုင်မလဲ ဆိုတာပါ။"

These become localized copy keys (per-match "hook" lines for the 3 seed matches via the note mapping;
generic scout-framed templates for unmapped matches → English/vi/mm, never Chinese).

## 8. Mini-Agent Harness Integration
Map the 8-stage design (`docs/MINI_AGENT_HARNESS_DESIGN.md`) onto **rules + prompts + copy mapping**
(no runtime, no 300-agent system):
| Stage | This round's realization |
|-------|--------------------------|
| Data Scout | Evidence Strip source list + data_mode caption |
| Baseline Model | existing win_prob/confidence/recommended_score (unchanged) |
| Risk Analyst | foreground existing `riskNote`/`topRisk` as "Risk watch" |
| Contrarian | NEW one-line "why this could be wrong" (per-seed mapping + generic fallback) |
| Explanation | factor Source/Impact/Interpretation rows (§5) |
| Copy Agent | scout-framed copy keys + LLM drafts (DeepSeek/Gemini), draft-only |
| Compliance | `compliance.scan` + new **language-fidelity** review (Han in vi/mm = reject) |
| Human Review | log to `LLM_DRAFT_COPY_REVIEW_LOG.md`; nothing auto-sent |

## 9. LLM / Provider Strategy (from the real comparison)
- **DeepSeek = vi/mm primary** draft candidate · **Gemini = benchmark / co-primary** · **Kimi = zh /
  report / internal research only — not for vi/mm output yet** (it leaked Chinese; see
  `docs/LLM_PROVIDER_COMPARISON_REPORT.md`) · **human template = fallback**.
- This round: LLM stays **draft-only + human review**. No auto-publish. Any rewritten customer-facing
  string that ships is **human-authored copy** (in `dict.ts`/`copy/*`), not raw LLM output; LLM is used
  to *propose* drafts logged for review.

## 10. Implementation Plan (proposed — for Owner approval; not executed this round)
| File | What changes | Why | Risk | Regression |
|------|--------------|-----|------|------------|
| `frontend/src/pages/ReportPage.tsx` | add Evidence Strip; upgrade factor block to Signal/Source/Impact/Interpretation; add Contrarian line; Scout section labels | core of the rewrite | layout density (esp. mm); over-long copy | screenshot vi/mm @390/430; Han scan |
| `frontend/src/pages/DetailPage.tsx` | add condensed Evidence Strip + scout verdict hook line + contrarian teaser above paywall | make Detail feel like intel; drive unlock | crowding near CTAs | screenshot unlock path |
| `frontend/src/components/FeatureBars.tsx` | render Source + Interpretation under each bar | model reasoning | row height ↑ | screenshot Report factors |
| `frontend/src/i18n/dict.ts` | new keys: evidence strip, scout labels, contrarian title, source/impact words, verdict hook (zh/vi/mm/en) | localized persona + structure | missing-key fallback | build + per-locale render |
| `frontend/src/i18n/viMapping.ts` | NEW `factorSourceViMap`, `factorInterpretationViMap` (+ en maps) keyed by factor label | per-factor source/interpretation (vi/en) | unmapped factor | English fallback (never zh) |
| `frontend/src/i18n/mmMapping.ts` | NEW `factorSourceMmMap`, `factorInterpretationMmMap` | mm source/interpretation | unmapped factor | English fallback (never zh) |
| `frontend/src/copy/{zh,vi,mm,en}.ts` | scout persona strings if not in dict | persona rename | — | build |
| `frontend/src/styles/global.css` | styles for `.evidence-strip`, factor sub-rows; `.lang-mm` tuning | compact, no overlap | mm overflow | screenshot @390/430 |
| `docs/OPERATION_COPY_LIBRARY_VI_MM.md` | add scout-framed vi/mm operator copy | operator forwarding | — | — |
| `docs/LLM_DRAFT_COPY_REVIEW_LOG.md` | log scout draft candidates | review trail | — | — |

**Explicitly NOT changed:** `/matches`, `/matches/{id}`, `/reports/{id}` response shapes; DB schema;
backend services; payment; bot. (If implementation reveals a real need, return to Owner first.)

## 11. QA Plan
**Engineer self-verification (L1):**
- `npm run build` (tsc + vite) passes; no console errors (Claude Preview console check).
- DOM Han scan = 0 on the **interactive** vi/mm path: `/detail`, `/report`, `/community`, incl. unlock
  modal → report, action sheets, toasts (reuse `scripts/qa/lang_interaction_shots.mjs` pattern).
- Layout: no overlap / overflow at **390×844 & 430×932** (esp. `.lang-mm`).
- Confirm no backend/API/DB change (git diff scoped to `frontend/` + `docs/`).
- zh/mm/vi isolation + currency unchanged; vi/mm never fall back to Chinese.

**Operator screenshot verification (real device):** `/detail?lang=vi` · `/report?lang=vi` ·
`/community?lang=vi` · `/detail?lang=mm` · `/report?lang=mm` · `/community?lang=mm`. Capture:
Evidence strip · Scout verdict · factor explanation (source/impact/interpretation) · unlock→report path ·
Telegram/Zalo entry · bottom nav · any modal/toast/action sheet.
**Screenshots saved to `docs/qa_screenshots/intelligence_rewrite/`.** No screenshot = no PASS.

## 12. Acceptance Criteria
**PASS:** Report has an Evidence Strip · factor bars show source/impact/interpretation · "AI 分析"
relabelled to Giành Cup Scout/persona · vi/mm have **no Chinese core residual** · vi/mm read naturally
for local operation · no crowding/overlap · no betting/hit-rate/profit wording · screenshots saved ·
build passes · backend/API/DB untouched (unless Owner-approved) · docs updated.
**PASS WITH ISSUES:** engineering complete, but operator real-device finds minor language or
open/redirect compatibility nits.
**FAIL:** vi/mm Chinese core residual · copy still flat · sources still invisible · screenshots missing ·
any betting/guaranteed-hit/profit risk appears.

## 13. Rollback Plan
- The rewrite is one (or few) **frontend commit(s)** → `git revert` restores the previous UI instantly;
  **docs are kept** (plan/comparison/review log remain).
- Restore previous copy by reverting `dict.ts`/`copy/*` (old keys retained in history).
- **Feature-flag option:** gate the Evidence Strip + factor-detail behind a small frontend flag
  (e.g. `VITE_SCOUT_INTEL=1` or a const) so it can be turned off without a revert if copy feels too
  heavy or mm layout is tight — keeping the evidence layer code in place but hidden.
- Backend untouched → nothing to roll back server-side.

---

### Owner review checklist (Stage 2)
1. Plan path: `docs/DATA_BACKED_SCOUT_INTELLIGENCE_REWRITE_PLAN.md`.
2. Files to change: Report/Detail/FeatureBars, dict + vi/mm mappings, copy/*, global.css, 2 docs (see §10).
3. **API/DB change needed? NO** (frontend-only). Will return to Owner if that changes.
4. Affects vi/mm/zh? vi/mm get the new localized scout layer; **zh internal wording unchanged in meaning**;
   isolation + currency preserved.
5. QA screenshots: `docs/qa_screenshots/intelligence_rewrite/` (vi/mm × detail/report/community + interactions).
6. Operator verification: real-device vi/mm path with the shots listed in §11.
7. Risks: mm layout density, copy over-length, factor-mapping coverage (mitigated by English fallback +
   feature flag + screenshot QA).
8. Recommendation: **ready to enter Implementation on Owner approval.**
