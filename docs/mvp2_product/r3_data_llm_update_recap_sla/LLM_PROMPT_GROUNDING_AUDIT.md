# R3 · LLM_PROMPT_GROUNDING_AUDIT

> Phase A — audit only. Audited 2026-06-15.
> Pipeline: `scripts/mvp2_build_daily_prediction_artifact.py` (`prompt` → operator pastes into
> DeepSeek/Gemini/Kimi MANUALLY → reviewed JSON → `apply`). No auto-LLM call in the daily build
> (P1). `llm_provider="operator_manual"` is the honest current state.

## Is the LLM copy actually grounded?

YES — for the current selected fixture the chain is traceable end to end. The grounding check
below confirms each link for **Belgium vs Egypt (1489377)** and the next manual fixture
(**Netherlands vs Japan**, operator_estimated).

| Prompt field | Present in prompt? | Source | Preserved in reviewed JSON? | Used on page? | Gap |
|--------------|--------------------|--------|-----------------------------|----------------|-----|
| fixture facts (key, kickoff, status, source) | ✓ | artifact | ✓ (consistent) | ✓ (/predict meta) | — |
| model_fields (recommended_score, risk_level, source) | ✓ | ScoutScore/operator | ✓ (`primary_score`, `risk_level` echo) | ✓ (DataBacking) | — |
| missing_fields (win_prob, confidence) | ✓ ("DO NOT INVENT") | builder | ✓ (no numbers emitted) | ✓ ("暂无自动胜率") | — |
| tactical variables (tempo, wings, set-pieces, lineup, fitness, motivation) | ✓ | prompt template | ✓ (`tactical_read`, `risk_factors`) | ✓ (analysis cards) | — |
| safety / compliance vocabulary | ✓ (FORBIDDEN list) | prompt template | ✓ (`safety.*=true`) | guarded | — |
| source_refs (Elo/form/Poisson provenance) | partial (in model facts block) | builder | preserved in `_note` | internal/daily only | refs not echoed verbatim into reviewed JSON (acceptable — internal) |
| T-30 checklist | ✓ | prompt | ✓ (`t30_checklist`) | ✓ (/predict) | — |
| recap requirement | ✗ (prompt is pre-match only) | — | — | — | **GAP: no recap prompt contract — recap is built separately, not from this prompt** |

### Traceability evidence

- Prompt file exists on disk: `docs/data_audit/mvp2_predictions/prompts/20260615_1489377_prompt.md`
  (carries `recommended_score: 1-0`, `risk_level: 中`, `model_fields.source: computed`,
  `UNAVAILABLE / DO NOT INVENT: win_prob, confidence`).
- Reviewed JSON exists: `docs/data_audit/mvp2_predictions/reviewed/20260615_1489377_reviewed.json`
  (`main_lean`, `primary_score:"1-0"`, `risk_level:"中"`, `tactical_read[]`, `risk_factors[]`,
  `t30_checklist[]`, `safety{no_betting_vocab,no_fake_probability,no_auto_send}`; `_note` records
  that model_fields are ScoutScore-computed and `llm_provider=operator_manual`).
- Artifact records both paths in `content_chain` (`prompt_path`, `reviewed_path`,
  `reviewed_applied:true`, `llm_provider:"operator_manual"`, `model_lookup:"computed"`).
- Page copy traces back: `ArtifactTacticalRoom.tsx` renders `i18n.{locale}.prediction` +
  `analysis`, and `DataBacking` renders `model_fields`/`source_facts` directly. `strongCallProjection`
  prefers `model_fields` score → homepage hook.

## Required prompt contract (R3 target — formalize what exists + close the recap gap)

**Input the prompt MUST carry:**
1. fixture facts (key, home/away, kickoff, status, fixture_source)
2. model facts (recommended_score, backup_scores, risk_level, risk_note, source tag)
3. missing fields (explicit "DO NOT INVENT: win_prob, confidence")
4. source_refs (Elo/form/Poisson provenance, internal)
5. public expectation wording (safe-vocab external expectation seed)
6. tactical variables (the 6 fixed topics)
7. T-30 checklist seed
8. recap requirements (for the post-match prompt — see gap)
9. compliance vocabulary (forbidden betting/odds/fake-probability list)

**Output the reviewed JSON MUST carry:**
`main_lean`, `primary_score`, `backup_scores`, `risk_level`, `risk_note`, `top_variable`, `why`,
`tactical_read[]`, `risk_factors[]`, `external_expectation[]`, `t30_checklist[]`, `share_copy`,
`recap_seed` (new — links the pre-match call to the eventual recap), `safety_flags`.

## Verdict

- **Pre-match grounding: PROVEN.** Prompt → reviewed JSON → artifact → page is traceable, model
  facts are preserved, and no fake numbers leak. `check_llm_grounding.py` (Phase B) automates this.
- **Auto-LLM: P1.** The daily build never auto-calls an LLM; `operator_manual` is honest and
  guarded. Real DeepSeek/Gemini wiring (`mvp2_generate_*.py`) exists but is trial-only.
- **Recap grounding: GAP (P1).** The pre-match prompt has no `recap_seed` and there is no recap
  prompt contract; the recap/observation is authored separately. R3 records this and adds a
  `recap_seed` placeholder so a future recap can cite the archived pre-match call — but does NOT
  fake an auto recap.
