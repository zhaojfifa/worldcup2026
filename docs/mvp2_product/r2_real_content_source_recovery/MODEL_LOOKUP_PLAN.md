# R2 — MODEL_LOOKUP_PLAN

> Source precedence for `model_fields`, implemented in `mvp2_build_daily_prediction_artifact.model_lookup`.
> The compliance floor overrides everything: **win_prob and numeric confidence are NEVER surfaced**
> (stay `null`), regardless of source.

## Precedence
| # | Source | When | Fields produced | `source` tag | Customer-visible | Internal (/internal/daily) | Guard rule |
|---|---|---|---|---|---|---|---|
| 1 | **Exact backend/API fixture-id model** (DB `Prediction` for this id) | a seeded/synced Prediction exists | recommended_score, risk_level, risk_note | `computed` (if real) / `seed` | score/risk only | shown + source | win_prob/confidence must stay null |
| 2 | **ProductNarrative / ScoutScore by fixture id** | an LLM narrative or ScoutScore frame already exists for the id | full judgement | `computed` | yes | yes | must carry source_refs |
| 3 | **ScoutScore v0.2 computed from kaggle** (Elo + form + Poisson) | both teams resolve in `data/external/kaggle/results.csv` | recommended_score (Poisson), risk_level (upset_band), risk_note, lean, source_refs | **`computed`** | recommended_score/risk/lean | Elo gap, form, bands shown | reject if a team is cold-start (Elo None) → fall to #5 |
| 4 | **Deterministic baseline/seed model** (`baseline.py`) | allowed only as an explicit seed reference | recommended_score, risk_level | `seed` | **only if Owner allows**; default NOT customer-surfaced (name-hash) | shown labelled "seed/baseline (placeholder, not real form)" | never tagged `computed`; win_prob/confidence null |
| 5 | **operator_estimated** fallback | no honest computed source (e.g. Cape Verde cold-start) | operator-authored | `operator_estimated` | yes (qualitative) | shown + **reason why no computed model** | win_prob/confidence null; must be disclosed |
| — | **unavailable** | nothing | — | `unavailable` | hidden | shown as missing | — |

## R2 decision for today (Belgium vs Egypt)
**Precedence #3 (ScoutScore computed) applies.** model_fields:
- `recommended_score="1-0"`, `backup_scores=["2-0","1-1"]` (Poisson 1.9/0.8)
- `risk_level="中"` (upset_band(129)=medium)
- `risk_note` = Elo+form derived
- `source="computed"`, `model_status="scoutscore_v0_2_elo_form"`
- `source_refs=["kaggle Elo Belgium 1884.9 / Egypt 1755.6 gap 129","form10 7W-3D-0L vs 5W-3D-2L","upset_band=medium","poisson 1-0/2-0/1-1"]`
- `win_prob=null`, `confidence=null` (floor)

## Implementation notes
- `model_lookup` imports the ScoutScore builder's `load_results`/`elo_snapshot`/`recent_form`/
  `upset_band`/`poisson_bands` (offline, no network), routed through `kname()` aliases (the documented
  Bosnia/Curaçao/USA fix) to avoid cold-start fakes.
- A team absent from kaggle (Elo `None`) → **not** `computed`; returns `unavailable` so the builder uses
  `operator_estimated` and `/internal/daily` states the reason.
- baseline.py (#4) is intentionally NOT wired as a customer source in R2 — it is name-hash noise; using
  it would violate "do not fake". Documented here as available-but-rejected.
