# P8 — HISTORICAL_PREDICT_PAGE_FLOW

> The old page flow, before the daily-refresh (P1.3+) rework, with exact files and data-source paths.
> There were **two historical eras** of `/predict` and one even older `/matches` home list. All still
> exist on `main`; the daily-refresh path was layered ON TOP, not in place.

---

## Era 0 — the original MVP-1 `/matches` model-field list (still wired, now demoted)

**Homepage list selection.** `HomePage.tsx` → `useAppStore` → `api.getMatches()`
(`GET /api/v1/matches`) → `listItemToMatch()` (`transform.ts`). Each card was a `Match` with **the full
numeric model layer**: `winProb {home,draw,away}`, `recommendedScore`, `riskLevel`, `riskNote`,
`confidence`. The home tiles rendered `WinBar` (the win-prob bar), an AI pick, a risk badge, a note —
all from these fields.

**Source of the numbers.** Backend: `match_service.py` joined `Match` → `Prediction`; `Prediction` was
produced by `baseline.predict(build_input_for_match(match))` in
`backend/app/services/modeling/baseline.py`. **`build_input_for_match` derived strengths from a seed
hash** (`_stable_strength(team.name)` ∈ [40,72]) — so the numbers were *deterministic placeholders*,
honestly `ai_provider="mock"`, `model_version="baseline-rules-v1"`. `win_prob` summed to exactly 100;
`confidence` ∈ [45,88]; `risk_level` ∈ {low,medium,high}; `risk_note` was one of three canned strings;
`recommended_score` was a band string. They were **DB-persisted per match** and refreshed by
`POST /matches/{id}/refresh` and `fixtures_sync.py`.

**On screen.** `/detail` → unlock → `/report` rendered the deeper fields (features, trend, tactics) via
`mergeDetail`/`mergeReport`. The win bar + risk badge were the visible "model" content.

**Status today:** this path is **still imported and still runs** (`useAppStore.ts:64`), but the
homepage product loop no longer leads with it — the mock tiles are demoted/folded behind the daily
hotspot loop. **This is the structured model-field layer the owner is asking to recover** — it was never
removed, only un-surfaced and never joined to the daily slate.

---

## Era 1 — the MVP-2 ScoutScore + LLM `/predict/:id` (still live for 5 fixtures)

**How `/predict/:id` resolved a match** (current `PredictPage.tsx`, unchanged for this era):
1. `predictSlugToId(slug)` → `getProductNarrative(id, loc)` (`productNarrativeData.ts`). If a bundled
   `ProductNarrative` exists for that id+locale → render `StrongCallCard` + `ProductPredictView` +
   `ShareBlock`.
2. else `getUpcomingFixture(id)` (`upcomingFixtures.ts`) for the kickoff/venue meta card.

**Where the fields came from.** `getProductNarrative` reads a **build-time-bundled JSON**
(`frontend/src/data/productNarratives/{id}.{zh-CN,vi-VN,my-MM}.json`) produced by
`scripts/mvp2_generate_product_proof_narratives.py` / `mvp2_generate_trial_prediction_narratives.py`,
which consumed a **ScoutScore v0.2 factor frame** (`mvp2_build_scoutscore_v0_2_factors.py`: real kaggle
Elo + last-10 form + H2H + Poisson bands) and called DeepSeek/Gemini, then passed
`check_mvp2_product_narrative_guard.py`. **`win_prob`/`recommended_score`/numeric `confidence` were NOT
in this JSON** — the call was expressed as `main_lean` (prose), `scoreline_view` (a band string like
"2-1、1-1、2-2"), `risk_level` (a word), and `risk_factors[]` (each a `ProductFactor` carrying
`source_refs` + `assumption_flag`).

**On screen.** `main_lean`/`scoreline_view`/`risk_level`/`risk_factors`/`tactical_read` rendered through
`ProductPredictView` and (the strong hook) through `StrongCallCard`, which reads
`buildStrongCall()` (`strongCallProjection.ts`): `splitScoreband(scoreline_view)` →
`{primary, alts}`, `harmonizedRisk(main_lean, risk_level)`, `top_variable` =
`watch_next_signals[0] || risk_factors[0]`.

**StrongCall vs ProductNarrative.** StrongCall is a **projection** of the ProductNarrative (it parses
and merges narrative fields), not a separate store. It deliberately carries **no win_prob/confidence** —
score/lean/risk-label only.

**Share card.** `/share/{prematch}/:id` → `shareTemplates.ts` → the SAME `buildStrongCall` projection
(primary/backup scores, lean, risk label, top variable, external expectation line). Recap share used
`buildRecapCall` (result → what-was-right → deviation → calibration → next hook).

**Recap.** `/recap/:id` rendered `ProductNarrative.mode === 'real_recap'` (or, for the daily hotspot,
the observation artifact). Recap **did not use the numeric model fields** — it used the LLM
`validated_factors`/`screenshot_line`/`short_title` and the archived pre-match receipt.

---

## Era 2 — the daily-refresh `/predict` for an `id=null` manual hotspot (current default)

`PredictPage.tsx` resolution when there is **no narrative and no upcoming fixture** (`needsFallback`):
1. `getPredictionArtifact(slug)` (`predictionArtifacts.ts`, by `fixture_key`). If found →
   `ArtifactTacticalRoom` — renders the **operator** artifact (`prediction.*`, `analysis.*`,
   `operations.*`). `win_prob`/`confidence` are `unavailable`; numbers shown only if the operator typed
   them (`score_call`, `risk_level`).
2. else generic `FALLBACK` shell (question-framed bullets + 30-min checklist, no numbers).

**There is no data-backed model block on this path** — that is the gap P8 targets. The artifact already
declares the empty sockets (`data_snapshot`/`modeling_output`/`generated_judgment`,
`field_sources.win_prob="unavailable"`), so the stage is built; only the bridge that fills them is
missing.

---

## Summary diagram (data → screen)

```
ERA 0 (numbers, seed-grade, DEMOTED):
  baseline.predict(seed strengths) → Prediction(DB) → match_service → /api/v1/matches
    → client.ts → transform.listItemToMatch → useAppStore → HomePage mock tiles (WinBar/risk badge)

ERA 1 (qualitative, real-kaggle ScoutScore + LLM, 5 FIXTURES ONLY):
  ScoutScore v0.2 frame (kaggle Elo/form/H2H/Poisson) → DeepSeek/Gemini → guard
    → productNarratives/{id}.{lang}.json → getProductNarrative → buildStrongCall (projection)
    → /predict StrongCallCard + ProductPredictView + /share cards + /recap

ERA 2 (operator, daily manual hotspot id=null — CURRENT LEAD):
  operator → manual_<H-A-date>.json (field_sources=operator_confirmed; model blocks null)
    → getPredictionArtifact → ArtifactTacticalRoom / buildStrongCallFromArtifact
    → /predict (no model block) + /share + /recap (observation receipt)
```

The daily hotspot (Era 2) **does not touch Era 0's numbers or Era 1's ScoutScore frame** — it is a
parallel third lane. Recovery = build a generator that feeds the Era-2 artifact from the Era-1 frame
(and, where Owner allows, an Era-0-style seed band), filling the already-declared empty sockets.
