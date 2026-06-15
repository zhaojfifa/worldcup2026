# P8 — FIELD_RECONNECTION_PLAN

> How to reconnect the historical content-fact fields into the current P7 daily flow. Five options
> (A–E) evaluated. The compliance floor (no fake probability) constrains the numeric tier throughout.

---

## Option A — Add historical fields directly (flat) onto the prediction artifact

**What changes.** Add `win_prob`, `recommended_score`, `risk_level`, `risk_note`, `confidence` as flat
keys on `PredictionArtifact` (alongside the existing `prediction.*`). Render them on `/predict`.

**Files likely touched.** `frontend/src/data/predictionArtifacts.ts` (interface), the manual artifact
JSON, `ArtifactTacticalRoom.tsx`, the artifact guard.

**Benefit.** Smallest change; one-to-one with the old `MatchListItem` shape.

**Risk.** **High.** Flat fields lose provenance — exactly the gap that makes the current data "thin".
Putting a bare `win_prob`/`confidence` next to operator prose invites a *fake-probability* compliance
breach and re-creates the unprovenanced state. The existing `field_sources` map would have to police it.

**P0 / P1.** Not recommended as the primary shape. **Reject** in favour of B.

---

## Option B — Add a structured `model_fields` / `model_snapshot` object (RECOMMENDED P0 shape)

**What changes.** Fill the **already-declared** `modeling_output` socket (rename/alias to `model_fields`
in the target schema) with a self-describing object: `{ win_prob, recommended_score, risk_level,
risk_note, confidence, source: 'computed'|'seed'|'operator_estimated'|'unavailable', source_refs[] }`.
Numbers stay `null` when `source==='unavailable'`; the UI renders a labelled "model read" block only when
a non-`unavailable` source is present, and **never** renders a bare probability without its source tag.

**Files likely touched.** `frontend/src/data/predictionArtifacts.ts` (formalise `model_fields` on the
interface — the socket already exists), the manual artifact JSON (add the object),
`strongCallProjection.ts` (read `model_fields` first, then operator fields), a new `/predict` data-backed
block component, `check_prediction_artifact.py` (assert `source_facts` + `model_fields.source`).

**Benefit.** Provenance-first; matches the artifact's existing design intent (`data_snapshot`/
`modeling_output`/`generated_judgment` were built for exactly this). Compliance-safe (source tag is
mandatory; `unavailable` is a first-class honest state). Frontend/scripts/docs only.

**Risk.** Low. Needs a clear rule for which sources may surface a number (Owner Q3).

**P0** (object shape + render + guard). The number-*population* is P0 only if a non-LLM source is
authorized; otherwise the object ships with `source:'unavailable'` and is filled in C/P1.

---

## Option C — Restore/adapt a daily prediction-data generator from the old source (RECOMMENDED P1, optionally P0-lite)

**What changes.** Adapt the still-present ScoutScore chain
(`mvp2_build_scoutscore_v0_2_factors.py` → `mvp2_generate_*_narratives.py` → guard) into a **daily
generator** keyed off the daily fixture instead of a hardcoded id: take the slate fixture (home/away) →
build a ScoutScore frame from kaggle (Elo/form/H2H/Poisson) → emit `model_fields`
(`risk_level`/`recommended_score` from `upset_band`/Poisson; `win_prob`/`confidence` only as a
**non-numeric band** unless Owner authorizes) → optionally run DeepSeek/Gemini for `main_lean`/
`risk_factors` with `source_refs` → write into the daily artifact's `model_fields`/`generated_judgment`
sockets. Operator confirms before it goes live (preserves the no-auto-send posture).

**Files likely touched.** A new `scripts/mvp2_build_daily_prediction.py` (composing existing scripts),
`mvp2_match_sync.py` (optional hook to call it), the artifact JSON it writes, the guard.

**Benefit.** Reconnects the **real-data** tier; scales past 1 fixture/day; restores provenance. This is
the actual cure for "content is thin".

**Risk.** Medium. Kaggle name-alias pitfalls (the documented `Bosnia & Herzegovina` bug); LLM run cost;
must keep the operator-confirm gate. Touches scripts (not runtime) so deploy-safe.

**P1** (full generator). A **P0-lite** slice is possible: run only the deterministic ScoutScore
*frame* (no LLM) to populate `model_fields.risk_level`/`recommended_score` with `source:'computed'` +
`source_refs`, leaving prose operator-authored.

---

## Option D — Keep operator-confirmed fallback only when computed fields are unavailable (RECOMMENDED, complements B/C)

**What changes.** Formalise the precedence the code already half-implements: **computed/seed
`model_fields` > operator_estimated > operator_confirmed prose > unavailable**. `field_sources` already
encodes this enum; make the UI + guard honor it (show the highest-provenance source, tag it, never
silently mix).

**Files likely touched.** `strongCallProjection.ts`, the `/predict` block, the guard.

**Benefit.** Zero new data dependency; makes the honest fallback explicit and auditable; keeps P0 shippable
even before the generator exists.

**Risk.** Very low. **Keep regardless of which other options are chosen.**

**P0.**

---

## Option E — Move artifacts to a backend runtime store (P1, later)

**What changes.** Persist daily artifacts (incl. `model_fields`) in a backend table served by the
existing `GET /api/v1/daily-fixtures` family, so updates need no frontend rebuild (extends the P1.3c
runtime source from manifest-only to full content).

**Files likely touched.** Backend (`daily_fixtures_service.py`, a new table, admin upload), frontend
fetch.

**Benefit.** True no-rebuild content updates; aligns with "能更新才是硬道理".

**Risk.** Higher — DB schema + endpoint change → needs its own Owner GO (backend/schema rule). **Not P0.**

**P1.**

---

## Recommended sequence

- **P0 (frontend/scripts/docs only):** **B + D** — add the provenanced `model_fields`/`model_snapshot`
  object to the artifact schema, render a data-backed block on `/predict` that shows it **with its source
  tag** (or "model read pending" when `unavailable`), wire `strongCallProjection` to prefer
  `model_fields`, surface `source_facts`/`model_fields` readiness on `/internal/daily`, and tighten guards
  to require *source presence*, not values. Optionally **C/P0-lite** (deterministic ScoutScore frame, no
  LLM) to populate `risk_level`/`recommended_score` with `source:'computed'` for the current hotspot.
- **P1:** **C (full generator with LLM + provenance) + E (backend runtime store)**, plus generalizing
  `mvp2_project_external_signals.py` and running the A4 recap pipeline.

**Constraint carried through all options:** `win_prob` and numeric `confidence` are the most sensitive —
default is to **keep them `unavailable`/non-numeric** unless the Owner explicitly authorizes a disclosed
seed or estimated band (Owner Q1/Q3). The compliance floor (no fake probability) is non-negotiable.
