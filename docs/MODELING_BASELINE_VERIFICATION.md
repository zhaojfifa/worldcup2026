# Modeling Baseline Verification (Harness-X · L1)

**Verdict: PASS** — baseline predictor + refresh work; probabilities normalize to 100; no real
hit-rate claimed (no settled results yet).

## 1. Input / boundary
Verify the baseline rules predictor + `refresh` path, read-only/idempotent. No model retraining,
no LLM, no backend change, no API shape change.

## 2. Role path used
L1 verification (curl + arithmetic check).

## 3. Changed files
Docs only. No code.

## 4. Verification commands & results (2026-06-08)
```
POST /api/v1/matches/1/refresh
→ win_prob {home:49, draw:26, away:25}  sum = 100.0   ✅ normalized
  confidence 61.0 · risk_level "high" · updated_at refreshed (2026-06-08T03:56:23Z) ✅
```
(Prior runs across the session consistently normalize to 100; confidence/risk recompute on refresh.)

## 5. Current capability
- **Baseline predictor:** rules model over existing features; outputs win_prob (home/draw/away),
  `recommended_score`, `confidence`, `risk_level`, `risk_note`.
- **Refresh:** `POST /matches/{id}/refresh` recomputes and updates `updated_at`; win_prob sums 100.
- **`risk_note`:** rule/seed text; surfaced as "AI viewpoint", not a guarantee.
- **Frontend ops layer** (`ops/derive.ts`): `aiPickLabel`, confidence stars, upset score, risk tags,
  reason bullets — all derived from existing fields, localized (zh/vi/mm + en) via `i18n/*Mapping`.

## 6. Future enhancements (NOT this phase)
Calibrated confidence, better feature weights, richer rule-based `risk_note`. Any LLM-generated
explanation is **Day-8 prep only**, behind a banned-word filter (see LLM prep doc).

## 7. Risk / blocker
- **Hard compliance rule:** `performance/summary.hit_rate = null` (0 settled). **Do not advertise
  real accuracy / hit-rate until real results are back-filled.** Everything stays "AI 倾向 / viewpoint".
- No blocker for the baseline itself.

## 8. Verdict
**PASS** — baseline + refresh verified; normalization correct; compliance gating on hit-rate intact.

## 9. Next Owner decision needed?
No. (Model enhancement + LLM explanation remain Owner-gated future phases.)
