# R1 — LLM_ENHANCEMENT_FLOW

> How DeepSeek/Gemini/Kimi are used in the daily chain. **MVP rule: NO automatic API call.** The builder
> generates a prompt file; the operator pastes it into the model, reviews the JSON, and saves it; the
> builder merges the reviewed JSON into the artifact. (DeepSeek/Gemini keys exist locally, but R1 P0
> does NOT auto-invoke them — that is P1.)

## Steps
1. `mvp2_build_daily_prediction_artifact.py prompt --date YYYYMMDD` builds the prompt from the daily
   fixture facts + model_fields (or "unavailable") and writes
   `docs/data_audit/mvp2_predictions/prompts/YYYYMMDD_<fixture_key>_prompt.md`.
2. Operator pastes the prompt into DeepSeek (default; Gemini/Kimi benchmark) — **manually**.
3. Model returns JSON. Operator reviews for correctness, compliance (no betting/odds, no fabricated
   probability), and language quality (zh canonical + vi/my Han=0).
4. Operator saves it to `docs/data_audit/mvp2_predictions/reviewed/YYYYMMDD_<fixture_key>_reviewed.json`.
5. `mvp2_build_daily_prediction_artifact.py apply --reviewed <file>` validates + merges it into the
   artifact's `llm_judgment` (+ derives i18n display), sets `content_chain.reviewed_applied=true` and
   `llm_provider`.

## Prompt MUST include
- **fixture facts**: home/away, kickoff (or "TBA"), status, competition.
- **model_fields**: `recommended_score`, `risk_level` (+ `win_prob`/`confidence` ONLY if the lookup
  produced a genuine computed/seed value); otherwise the prompt states they are **unavailable** and
  instructs the model NOT to invent a probability or numeric confidence.
- **missing fields**: explicit list (e.g. win_prob, confidence) so the model does not fabricate them.
- **tactical variables**: the matchup framing to reason over (tempo/control, wings, set-pieces, etc.).
- **market / public expectation**: SAFE wording only — public tendency / heat focus / upset variable.
  Forbidden: odds, handicap, kèo, cửa trên/dưới, betting, 盘口/赔率/投注.
- **T-30 checklist** format (5 items: XI, formation, key-player status, live heat, re-confirm).
- **recap-receipt format** (pre-match call → actual → assessment → deviation → calibration → next).

## Output JSON schema (the model must return exactly)
```json
{
  "main_lean": "string (persona voice; zh canonical)",
  "primary_score": "e.g. 2-1",
  "backup_scores": ["1-1", "2-2"],
  "risk_level": "中高 (or low/medium/high band word)",
  "risk_note": "string",
  "top_variable": "string",
  "why": "string",
  "tactical_read": ["...", "..."],
  "risk_factors": ["...", "..."],
  "external_expectation": ["safe wording only", "..."],
  "t30_checklist": ["首发阵容与位置", "...", "开球前再确认方向"],
  "share_copy": "string (no betting vocab; ≤ ~280 chars)",
  "safety": { "no_betting_vocab": true, "no_fake_probability": true, "no_auto_send": true }
}
```

## Guard / review gate
- The reviewed JSON is checked by `check_mvp2_product_narrative_guard.py`-style rules + the R1
  `check_daily_content_flow.py` before merge: no betting/odds vocab, no fabricated win_prob/numeric
  confidence, vi/my Han=0 on display slices, `safety.no_fake_probability=true`.
- `llm_provider` is recorded honestly: `deepseek`/`gemini`/`kimi` when a model was actually run;
  `operator_manual` when the content is operator-authored and no model was run (current
  Netherlands–Japan case). The builder NEVER stamps an LLM provider that was not actually used.
