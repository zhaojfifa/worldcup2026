# ScoutScore v0.1 — Model Card

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Mode:** implementation (backend transform + internal preview; **no public surface, no frontend change**).
> First product model loop for a prediction-accountability product. Reference fixture: **855737 — Argentina 1–2
> Saudi Arabia** (historical replay).

## Model identity
| field | value |
|---|---|
| `model_name` | **ScoutScore v0.1** |
| `model_type` | `hybrid_factor_scoring_with_llm_reasoning` |
| `purpose` | generate a **pre-match view** (replay) and a **post-match accountability report** |
| `backbone_future` | **XGBoost / LightGBM** (training backbone — reserved, **not trained yet**) |
| `reasoning_models` | **DeepSeek + Gemini** (production reasoning — draft-only, forbidden-filtered, pending Render) |
| `current_mode` | **`historical_replay`** |
| `not_real_archived_prediction` | **true** |

## Hard constraints (non-negotiable)
- **no betting advice** · **no fake probability** (no win-rate/odds) · **no SHAP** / feature-importance ·
  **no xG** unless a licensed source exists · **no injuries inference** · no odds / market / 盘口 / 竞猜.
- **Not a real archived prediction.** Everything is a *historical replay* used to validate the product flow —
  never presented as "we called it pre-match".
- Every conclusion carries **`source_refs`** or an explicit **`assumption`** flag.
- vi output = **0 Han**. Mandatory disclaimer on recap copy: 历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。

## Architecture (4 layers)
1. **Factor Scoring Layer** — rule-based scoring of 7 structured factors (`scoutscore/factors.py`). Deterministic.
2. **LLM Reasoning Layer** — multi-dimensional explanation. **Currently deterministic/template** (the
   `AI_PROVIDER=mock` fallback) so artifacts are reproducible and filter-safe; **DeepSeek/Gemini** are the
   designated production reasoners behind the existing draft-only, forbidden-filtered path (`app/services/llm/`) —
   **real call pending Render verification** (per project LLM gate). No live LLM call in this round.
3. **Post-match Accountability Layer** — hit / miss / partial, factor validation, missed factors, model correction
   (`scoutscore/accountability.py`).
4. **Operator Copy Layer** — zh / vi operator recap + customer hook copy (localized; filter-clean).

## 7 factors (orientation: + favours HOME, − favours AWAY)
`team_strength` · `recent_form` · `lineup_formation` · `match_control` · `efficiency` · `event_momentum` ·
`missing_risk`. Each: `direction / weight / score / interpretation_pre_match / post_match_validation /
source_refs / data_status (available|missing|replay_only) / assumption`. A factor a real pre-match model could
not have had is `missing`/`replay_only` (never faked as a pre-match input). `score` is the pre-match weighting;
`post_match_validation` is where blind spots surface (efficiency & event_momentum were scored 0 pre-match and
revealed decisive post-match → the model-correction targets).

## Inputs / outputs
- **Input:** a cached, redacted Scout Pack (`docs/data_audit/mvp2_scout_pack_samples/<fid>.json`) — real
  API-FOOTBALL Level-2 data. No live API, no live LLM.
- **Outputs:**
  - `docs/data_audit/mvp2_scoutscore_v0/<fid>.factor_scores.json`
  - `docs/data_audit/mvp2_prediction_replay/<fid>.scoutscore_v0.replay.json`
  - `docs/data_audit/mvp2_prediction_accountability_reports/<fid>.{zh-CN,vi-VN}.json`
- **Build:** `backend/scripts/mvp2_build_scoutscore.py` (offline). **Preview:** `/internal/scout-pack?fixture_id=&lang=`
  renders the accountability report first (raw pack + ledger collapsed); `noindex`, admin-token gated in prod,
  `public_ready=false`, `operation_status=paused`.

## Known limitations
- Pre-match view rests heavily on a **paper-strength assumption** (Elo / squad value / recent form **not
  ingested**) → confidence is deliberately **low**.
- Single-fixture replay (855737); not a validated accuracy claim across matches.
- Next data to graduate from replay → real pre-match scouting: **injuries (P0)**, **xG (P1)**, **Elo / form
  (P1)** — see [MVP2_NEXT_DATA_REQUIREMENTS](MVP2_NEXT_DATA_REQUIREMENTS.md).

## Future backbone (reserved, not built)
XGBoost / LightGBM trained on accumulated fixtures + the factor/feature store, with the same source_refs and
compliance constraints. **Not trained this round.** Real LLM reasoning (DeepSeek/Gemini) graduates only after
Render verification + human review (Owner-gated).

## Guardrails honored
historical replay only · no real archived prediction · no fake probability / SHAP / xG / injury inference /
betting · every conclusion sourced or flagged assumption · vi 0 Han · backend + internal preview only · no
frontend change · external operation paused · PR #2 untouched.
