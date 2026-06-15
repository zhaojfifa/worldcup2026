# R2 — LLM_REVIEW_FLOW_PLAN

> The manual LLM step (no auto-call). Builder generates a prompt embedding the **real computed
> model_fields**; operator pastes into DeepSeek/Gemini/Kimi, reviews, saves reviewed JSON; builder
> merges it. Provider stamped honestly (`operator_manual` if no model was actually run).

## Steps
1. `mvp2_build_daily_prediction_artifact.py prompt --date 20260615 --fixture-key 1489377`
   → runs `model_lookup` (ScoutScore computed) → writes `source_facts` + `model_fields` on the artifact
   → emits `docs/data_audit/mvp2_predictions/prompts/20260615_1489377_prompt.md`.
2. Operator pastes the prompt into DeepSeek (default) — **manually**.
3. Model returns JSON. Operator reviews: facts vs the computed model, compliance (no betting/odds, no
   fabricated win_prob/numeric confidence), language (zh canonical + vi/my Han=0).
4. Save → `docs/data_audit/mvp2_predictions/reviewed/20260615_1489377_reviewed.json`.
5. `… apply --date 20260615 --fixture-key 1489377 --reviewed <file>` → merges into `llm_judgment` +
   `content_chain` (reviewed_applied, llm_provider) + operator_confirmation + safety flags.

## Prompt MUST include
- **fixture identity**: Belgium vs Egypt, id 1489377, KO 2026-06-15 19:00 UTC, WC2026.
- **source_facts**: fixture_source=api_football, data_mode=api, has_model_fields=true.
- **model_fields** (the REAL computed values): recommended_score 1-0, backups 2-0/1-1, risk 中(medium),
  Elo gap +129 (Belgium 1885 / Egypt 1756), form10 7W-3D-0L vs 5W-3D-2L, upset_band=medium.
- **missing_fields**: win_prob, confidence (instruct: do NOT invent a probability/number).
- **tactical context**: Belgium possession/transition strength vs Egypt low block + Salah counters; set
  pieces; whether Egypt can keep it low-scoring (matches the 1-0 Poisson primary).
- **external expectation**: SAFE wording only (public tendency / heat / upset variable). No odds/handicap.
- **T-30 checklist** (5 items) + **share copy** requirement (≤~280 chars, no betting vocab).
- **safety constraints**: no betting/trading vocab, no fake probability, no auto-send.

## Output JSON must include
`main_lean`, `primary_score`, `backup_scores`, `risk_level`, `risk_note`, `top_variable`, `why`,
`tactical_read[]`, `risk_factors[]`, `external_expectation[]`, `t30_checklist[]`, `share_copy`,
`llm_provider`, `safety{no_betting_vocab,no_fake_probability,no_auto_send}`.

## R2 reality for this sprint
Engineering does NOT auto-call an LLM (boundary). The reviewed JSON for 1489377 is **operator-authored
from the real computed model** (Belgium favoured 1-0, medium upset) and stamped
`llm_provider="operator_manual"` — honest: the *model_fields are computed/real*, the *narrative is
operator-reviewed* (real DeepSeek/Gemini auto-generation = P1). The artifact i18n (zh/vi/my/en, vi/my
Han=0) is authored consistently with the reviewed judgement so `/predict` renders the rich room.
