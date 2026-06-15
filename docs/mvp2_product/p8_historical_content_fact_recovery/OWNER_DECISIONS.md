# P8 — OWNER_DECISIONS

> Only the decisions that actually change what P8 builds. Each carries an engineering recommendation and
> the compliance consideration. **No implementation until these are answered.**

---

### Q1 — If the historical numeric fields were seed/placeholder (not real), can we still use them as demo `model_fields`?

Context: `baseline.py`'s `win_prob`/`confidence` were computed from a **seed hash strength**, honestly
`ai_provider="mock"`. They are placeholder-grade, not real form/xG.

- **Recommendation:** **No for `win_prob`/`confidence` as numbers** (a placeholder probability shown to a
  customer reads as a real prediction → fake-probability risk). **Yes for `recommended_score`/`risk_level`
  as a disclosed qualitative band** with `source:"seed"`. Keep `win_prob`/numeric `confidence`
  `unavailable` until a real (ScoutScore) source exists.
- **Compliance:** the floor (no fake probability) is the binding constraint.

### Q2 — Should P0 allow `operator_estimated` model_fields for manual fixtures?

- **Recommendation:** **Yes**, for qualitative fields (`risk_level`, `risk_note`, `recommended_score`)
  with `source:"operator_estimated"` and a visible tag. This is the honest scalable fallback when no
  computed source is available.
- **Compliance:** acceptable — these are qualitative calls, not probabilities; the source tag prevents
  them being mistaken for model output.

### Q3 — Should the homepage show `confidence` only if computed/seed, or also if operator_estimated?

- **Recommendation:** **Only if `computed`** (real ScoutScore). **Never** render a numeric `confidence`
  whose source is `seed`, `operator_estimated`, or `unavailable`. If the operator wants to express
  certainty, use a **non-numeric band word** ("把握度：中"), not a number.
- **Compliance:** a number implies precision the data doesn't have.

### Q4 — Should `/internal/daily` expose `data_mode` / `source_facts`?

- **Recommendation:** **Yes.** It is an internal/operator surface; showing `data_mode`,
  `has_model_fields`, and per-field `source` is exactly the readiness signal the operator needs and never
  leaks to customers.

### Q5 — Should we preserve the current P7 `selected_hotspot` mechanism while reconnecting fields?

- **Recommendation:** **Yes — preserve it unchanged.** P8 only fills the artifact that `selected_hotspot`
  already points to; selection authority stays with P7. (Owner premise explicitly asks to keep it.)

### Q6 — Should P8 implement only schema/data display, or also adapt a generator script if one exists?

Context: the ScoutScore frame generator (`mvp2_build_scoutscore_v0_2_factors.py` + the narrative
generators) still exists and runs locally; it was simply never wired to the daily slate.

- **Recommendation:** **P0 = schema + provenance display + guards** (frontend/scripts/docs). **Add the
  optional P0-lite deterministic frame builder** (ScoutScore frame only, no LLM) if you want the current
  hotspot to carry a real `source:"computed"` `risk_level`/`recommended_score` immediately. **Full
  LLM generator = P1** (its own GO). This keeps P0 deploy-safe (bundle only) while reconnecting real-data
  provenance as fast as you authorize.

---

## Decision summary the implementation will read

| # | Question | Recommended default if no answer |
|---|---|---|
| Q1 | seed numerics as demo model_fields? | win_prob/confidence: **no**; score/risk band: yes (disclosed) |
| Q2 | operator_estimated model_fields? | **yes**, qualitative only, tagged |
| Q3 | show confidence when? | **computed only**; else non-numeric band |
| Q4 | /internal/daily expose source_facts? | **yes** |
| Q5 | preserve selected_hotspot? | **yes**, unchanged |
| Q6 | schema-only or also generator? | **schema+display+guards P0**; optional P0-lite frame; full generator P1 |

**Cross-cutting guardrails (not up for decision):** no betting/odds vocab; no fake `win_prob`; no
auto-send; numbers only with a source tag; `unavailable` is a valid honest state; backend/DB/schema
changes (Option E, full generator-in-runtime) each require a separate GO.
