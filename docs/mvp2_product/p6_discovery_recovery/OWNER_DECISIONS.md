> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# P6 Owner Decisions

Each item below is a yes/no or option question the Owner **must** decide before P6
implementation begins. Options are listed; the recommendation is one line. Nothing is
implemented until the Owner signs these off. No-send / no-betting / MTC-non-withdrawable
posture is preserved regardless of choices.

---

### 1. Re-add a score-call hook to the HOMEPAGE lead?

**Question:** Re-add a score-call hook (主看 lean + 主比分 / 备选 + 冷门风险) to the **homepage**
hotspot lead card, reversing the **P1.5a** decision that cut Strong Calls from the landing?

**Options:**
- **A)** Yes — surface `buildStrongCall` on the lead when the featured prediction is renderable.
- **B)** No — keep the generic question-frame lead.
- **C)** Compromise — show only the lean + a single primary-score teaser (not the full strong
  call) above the fold.

**Recommendation:** **C then A** — ship the compromise teaser first (lean + 主比分 only) to raise
information scent with minimal landing weight, with a clear path to the full hook once a
renderable lead is guaranteed. The strong-call asset already exists and is reused on `/predict`
and `/share`; the homepage is the only high-traffic surface missing it, and the guard blind spot
proves the weak hook is the single biggest product-expression gap.

---

### 2. Force the homepage lead to be a RENDERABLE fixture?

**Question:** Force the homepage lead to be a **renderable** fixture (has a bundled narrative or
registered prediction artifact), instead of `selectProductLoop` promoting the first scheduled
fixture even when it is a non-renderable `id=null` manual entry?

**Options:**
- **A)** Yes — `selectProductLoop` picks the first **renderable** scheduled fixture as the lead,
  falling back to the lightweight frame only if none.
- **B)** No — keep slate-order-first selection and accept a frame-only lead.

**Recommendation:** **A** — a non-renderable lead guarantees a frame-only card (today's
Netherlands–Japan) and makes any homepage score-call hook return null. Renderable-first
selection is a pure frontend selection-logic change, preserves operator slate control, and
unlocks the hook (decision #1 depends on this).

---

### 3. Allow operator-confirmed daily SCORE CALLS, and scaffold them?

**Question:** Allow operator-confirmed daily **score calls** (hand-authored
`predictionArtifacts`) to continue backing the strong call, as a disclosed exception to the
LLM-owns-narrative rule, **and** add a generator/scaffolder so it scales?

**Options:**
- **A)** Yes — keep operator-confirmed artifacts (`source=operator_confirmed`, `confidence=null`,
  disclaimer) **AND** build a daily scaffolder/generator.
- **B)** Yes but manual-only — keep hand-authoring, no generator.
- **C)** No — require an LLM-generated narrative for every featured fixture (no manual artifact).

**Recommendation:** **A** — the artifact tier is what gives today's manual hotspot real depth and
is already guard-validated + disclosed as a qualitative call (`note`: "a qualitative scout call
with a reference scoreline — not a precise probability"); without a scaffolder/generator it
cannot scale past ~1 fixture/day. Keep the LLM pipeline as the **preferred** source and the
operator artifact as the **validated fallback**.

---

### 4. External-expectation block on HOMEPAGE or detail-only?

**Question:** Show the external-expectation / public-consensus block
(🌐 外部预期 · 公开倾向) on the **homepage** lead, or keep it **detail-only**
(`/predict`, `/share`)?

**Options:**
- **A)** Detail-only (current) — homepage stays lean.
- **B)** Add the first external line to the homepage lead as part of the hook.

**Recommendation:** **A** — keep it detail-only for now. The external-signal layer is generalized
for only **one** fixture (1489371) and is engineering-authored prose (soft-judgement tension);
surfacing it on the lead would amplify a not-yet-scaled, hand-written layer. Revisit once
`mvp2_project_external_signals.py` is generalized off its 1489371-only `TEAMS` dict (P1).

---

### 5. Persist the daily editorial hotspot selection?

**Question:** Persist the daily editorial hotspot selection as a tracked artifact
(`selected_hotspot_<date>.json`), replacing the current **ephemeral** stdout-prompt + operator
memory + hand-edited-manifest-flag override (which a re-sync wipes)?

**Options:**
- **A)** Yes — `mvp2_editorial_agent` / `mvp2_match_sync` writes a persisted
  `selected_hotspot_<date>.json` that drives the manifest override **durably** (script/docs only,
  no backend).
- **B)** No — keep the manual one-shot hand-edit.

**Recommendation:** **A** — the hand-edited `renderable`/`hero` flags are **reset by any re-sync**
(documented in `REFRESH_20260614.md`), so the true editorial decision is fragile and untraceable.
Persisting it is a **script/docs-only** change with no backend impact and makes the daily hotspot
durable and auditable.

---

### 6. Scope P6 to ARTIFACTS/UI only, or also consolidate workflow/operations docs?

**Question:** Scope P6 to **artifacts/UI only**, or also **consolidate the workflow/operations
docs** (move the design-branch SOP / CTA / compliance onto a main-tracked `OPERATIONS_FLOW.md`)?

**Options:**
- **A)** UI/artifacts + docs consolidation.
- **B)** UI/artifacts only.
- **C)** Docs only.

**Recommendation:** **A** — the canonical operator SOP, group-CTA pack, and compliance note live
on `feature/mvp2-growth-p0-design`, **NOT** on main (main carries only the fixture-specific
runbook + gate doc). Consolidating them onto a main-tracked operations doc is **zero-runtime**,
keeps the no-auto-send / no-betting / MTC posture visible, and the `FIRST_SEND_RUNBOOK` is now
**stale on its pre-match half** (1489371 finished), so the live target must roll forward anyway.

---

### 7. Tighten the homepage + artifact guards?

**Question:** Tighten `check_homepage_product_loop.py` to **require a score-call hook** on the
renderable lead, and **generalize** `check_prediction_artifact.py` off its two hardcoded
filenames?

**Options:**
- **A)** Yes to both — add the score-call assertion + glob the artifact dir.
- **B)** Only generalize the artifact validator.
- **C)** Leave guards as-is.

**Recommendation:** **A** — the homepage guard's documented blind spot (asserts only TITLE + CTA +
share, nothing about a score-call) is exactly why the weak hook passed green; and the artifact
validator's hardcoded paths force a validator edit **every new day**. Both are stateless scanner
changes — but **sequence the homepage assertion to land WITH the UI hook** so the build does not
break.

---

## Decision dependency note

- #2 (renderable-first lead) is a **prerequisite** for #1 (homepage hook) — without it the hook
  returns null on a non-renderable lead.
- #7 (guard tightening) must be **sequenced with** the #1 UI hook, never ahead of it.
- #3 and #5 together unlock the **daily scaling** path (scaffolder + persisted selection).
- #6 is **zero-runtime** and independent.

All recommendations keep the **no backend / no schema** default (copy / UI / artifact / validator
only) and preserve the **no-auto-send / no-betting / MTC-non-withdrawable** posture.
