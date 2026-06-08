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

---

## 10. Modeling formalization run — all 3 matches (2026-06-08)

**Verdict: PASS.** `POST /matches/{1,2,3}/refresh` then read; **response shape unchanged** (same
key set across all three). win_prob normalizes to 100 in every case.

| Match | win_prob (H/D/A) | sum | conf | risk | recommended_score | risk_note (zh source) |
|-------|------------------|-----|------|------|-------------------|------------------------|
| 1 巴西 vs 阿根廷 | 49 / 26 / 25 | **100** | 61 | high | 2:1 / 1:1 | 双方实力接近，结果高度依赖临场阵容与战术对位，不确定性较高。 |
| 2 摩洛哥 vs 法国 | 50 / 19 / 31 | **100** | 80 | low | 2:0 / 2:1 | 模型判断方向较为明确，主要因子一致，临场变量影响有限。 |
| 3 西班牙 vs 德国 | 52 / 19 / 29 | **100** | 86 | low | 2:0 / 2:1 | 模型判断方向较为明确，主要因子一致，临场变量影响有限。 |

- `updated_at` refreshed on all three (~04:30 UTC).
- **Frontend impact:** none破坏 — display reads existing fields; new `risk_note` for m2/m3 added to
  vi/mm/en note maps (`i18n/viMapping.ts`, `i18n/mmMapping.ts`) so vi/mm show translated text
  instead of the English generic fallback. **No API shape change.**
- **Usable as operation material?** Yes as **AI viewpoint** (倾向 / risk signal / pre-match update).
  **Not** as real accuracy — `performance.hit_rate=null` (0 settled); still seed-driven (`mock_mode=true`).
