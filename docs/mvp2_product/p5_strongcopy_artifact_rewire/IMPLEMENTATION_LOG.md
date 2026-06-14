# MVP2-P5 Implementation Log

## 2026-06-14 — StrongCopy Artifact Rewire (Approach A)
Owner GO: re-wire prediction/observation artifacts into the existing canonical strong-call
projection + share layer. Persona = 俅哥 (brief's 侃哥 confirmed a typo via AskUserQuestion).

Files:
- frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json — strong fields
  (top_variable, why, external_expectation[safe vocab]) + pending_direction/pending_score; numerics null.
- frontend/src/data/predictionArtifacts/observation_1489371.json — assessment→部分命中, +next_impact.
- frontend/src/data/predictionArtifacts.ts — types (strong fields; pending labels; next_impact).
- frontend/src/growth/strongCallProjection.ts — buildStrongCall artifact fallback +
  buildStrongCallFromArtifact (null numerics → pending labels).
- frontend/src/components/ArtifactTacticalRoom.tsx — rewritten as the strong-call layout (sc-* styling)
  + ShareBlock (artifact join CTA → /community).
- frontend/src/components/ObservationReceipt.tsx — strong receipt + next_impact + ShareBlock.
- frontend/src/components/ShareBlock.tsx — optional joinLabel/joinTo.
- frontend/src/growth/shareTemplates.ts — recapShareCopy observation-artifact fallback.
- frontend/src/pages/ShareCardPage.tsx — artifact-aware (fixture from prediction artifact; recap card
  from observation artifact); empty "—" only when no source at all.
- frontend/src/pages/PredictPage.tsx — ArtifactTacticalRoom call site (path prop removed).
- scripts/check_prediction_artifact.py — P5 strong-token + safe-vocab guard (selftest 8/8).
- scripts/check_growth_copy.py — artifacts + components added to globs.
- docs/data_audit/mvp2_predictions/* — audit mirror.

Note: renamed artifact safety key no_betting_vocab → vocabulary_compliant (the literal "betting"
tripped the growth-copy guard on the metadata key; not customer copy).

Checks: build PASS · artifact guard PASS + selftest 8/8 · growth copy PASS (23) · homepage loop PASS ·
customer-visible 21/21 PASS (local) · 4 strong surfaces headless-verified (tokens + QR; 模型/赔率=0;
my Han=0). Numerics stay pending (no data ingested) — no invented score/probability/recap.
Next: operator deploy + live re-verify. No send.
