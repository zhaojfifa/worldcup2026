# P1B · AUTO_LLM_PROMPT_CONTRACT

> The prompt the generator sends (live or simulated in dry-run). Implemented in
> `mvp2_autogen_prediction_draft.py strong_prompt`. Output validated by `guard_draft` +
> `check_auto_llm_factory.py` + `check_llm_copy_quality.py` + `check_recap_seed_grounding.py`.

## Prompt MUST include
- fixture facts (home/away/role)
- model_fields (source, recommended_score, backup_scores, risk_level)
- source coverage (data_mode) + the data/source basis (source_refs)
- missing fields ("DO NOT INVENT: win_prob, numeric confidence")
- priority role: primary | secondary
- language (zh canonical; vi/my/en derived downstream)
- strong-copy requirements (headline, score call, top variable, why, ≥2 tactical beats, data basis,
  safe external expectation, 5-item T-30 checklist)
- safety rules + forbidden vocabulary (odds/handicap/盘口/赔率/投注/让球/betting/kèo; win-rate;
  win-guarantee 稳赢/必胜/chắc thắng)
- no fake win_prob / no fake confidence / no fake event claims
- T-30 checklist
- recap_seed request

## Output JSON MUST include
`strong_headline`, `main_lean`, `primary_score`, `backup_scores`, `risk_level`, `top_variable`,
`why`, `tactical_beats`, `data_source_basis`, `external_expectation_safe`, `t30_checklist`,
`homepage_short`, `predict_medium`, `share_copy`, `recap_seed`, `safety_flags`
(`{no_betting_vocab, no_fake_probability, no_fake_events, no_auto_send}` all true).

## Grounding rule
`primary_score` is seeded from `model_fields.recommended_score` and must not contradict it;
`recap_seed` must reference `primary_score` (so the recap verifies the actual call). Enforced by
`check_recap_seed_grounding.py`.

## Live evidence (this sprint, DeepSeek)
- 1489377 Belgium-Egypt (primary): headline "比利时碾压式进攻，埃及防线难挡", primary_score 1-0 (== computed),
  recap_seed references 1-0, safety_flags all true, GUARD_PASSED.
- 1489379 Saudi-Uruguay (secondary): GUARD_PASSED, grounded in computed 0-1.
Drafts at `docs/data_audit/mvp2_predictions/generated/` — DRAFTS for review, NOT published.
