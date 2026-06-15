# R1 — R1_IMPLEMENTATION_SPEC

> P0 = scripts / frontend / docs only. No backend, no schema migration, no auto-LLM, no auto-send,
> no faked win_prob/confidence/recap, no betting vocab. Preserves the P7 `selected_hotspot` mechanism.

## P0-1 — Daily prediction artifact builder
`scripts/mvp2_build_daily_prediction_artifact.py` with subcommands:
- `prompt --date YYYYMMDD [--fixture-key KEY]`
  1. read `frontend/src/data/selectedHotspot.json` (+ daily manifest for facts).
  2. `model_lookup(fixture)` → currently returns `unavailable` for an `id=null` manual fixture (hook
     left for P1: backend `Prediction` / bundled ScoutScore frame). Records the result + note.
  3. build/refresh the artifact's `source_facts` + `model_fields` (operator_estimated when lookup
     unavailable; win_prob/confidence stay null; `no_fake_probability=true`).
  4. write `docs/data_audit/mvp2_predictions/prompts/YYYYMMDD_<fixture_key>_prompt.md` (the LLM prompt
     per LLM_ENHANCEMENT_FLOW), set `content_chain.prompt_generated=true` + `prompt_path`.
- `apply --date YYYYMMDD --reviewed <file>`
  1. load + validate the reviewed JSON (schema + safe-vocab + no fake numerics).
  2. merge into the artifact `llm_judgment` (+ derive/refresh the zh i18n display fields used by the
     existing render), set `content_chain.reviewed_applied=true`, `llm_provider`,
     `operator_confirmation`.
- `--selftest` (embedded fixtures; no network, no LLM).

**It NEVER calls an external LLM.** `model_lookup` is offline-only.

## P0-2 — LLM prompt artifact path
`docs/data_audit/mvp2_predictions/prompts/YYYYMMDD_<fixture_key>_prompt.md` — generated for the current
hotspot (`20260614_manual:Nether-Japan-20260614`). Slugified filename (`:`→`_`).

## P0-3 — Reviewed output path
`docs/data_audit/mvp2_predictions/reviewed/YYYYMMDD_<fixture_key>_reviewed.json`. For the current
fixture, the reviewed JSON is the operator-authored judgement (`llm_provider="operator_manual"` —
honest; no LLM was run). The mechanism supports a real reviewed LLM JSON for any future fixture.

## P0-4 — Prediction artifact update (merge)
Final artifact merges: `fixture_identity` + `source_facts` + `model_fields` + `llm_judgment` +
`operator_confirmation` + `operations`(share_copy) + `safety` + **NEW `content_chain`** provenance.
Back-compat: the existing flat `i18n` + P8 blocks keep driving render; `content_chain` is additive.

## P0-5 — /internal/daily content readiness
`DailyStatusPage.tsx` adds a "Content chain / 内容生产链" group reading `art.content_chain` +
`source_facts` + `model_fields` + `t30` + observation: model-lookup found/unavailable · LLM prompt
exists · reviewed JSON applied · artifact ready · share kit ready · T-30 status · recap status · plus
the P8 rows. (Browser reads the artifact's recorded flags — no filesystem access needed.)

## P0-6 — Guard: `scripts/check_daily_content_flow.py`
Fails if, for the selected hotspot's prediction artifact:
- selected_hotspot present but no artifact;
- artifact lacks `source_facts`;
- artifact lacks `model_fields` (or invalid `model_fields.source`, or non-null win_prob/confidence);
- artifact lacks LLM/operator judgement (`llm_judgment` or i18n `prediction`);
- `content_chain.prompt_generated` not true / no prompt recorded;
- `share_copy` missing;
- `t30` slot missing/invalid;
- `content_chain` cannot express `/internal/daily` readiness (missing the flags the page needs);
- betting/trading vocabulary anywhere; `safety.no_auto_send`/`no_fake_probability` not true.
`--selftest` with embedded good/bad fixtures.

## Interfaces touched
- `frontend/src/data/predictionArtifacts.ts` — add `ArtifactContentChain` interface + optional
  `content_chain` field (additive).
- artifact JSON `manual_Nether-Japan-20260614.json` — add `content_chain`.
- `frontend/src/pages/DailyStatusPage.tsx` — content-chain readiness rows.
- (no change needed to render of homepage/predict/recap/share — they already read the artifact.)

## P1 (deferred, each its own GO)
- `model_lookup` real implementation (backend `Prediction` join / ScoutScore frame for the daily
  fixture → `source:"computed"` with `source_refs`).
- Auto-run DeepSeek/Gemini/Kimi (currently manual paste).
- `mvp2_generate_rescore_models.py` wired for the daily T-30 live diff.
- `mvp2_build_recap_frame_real.py` → LLM `real_recap` (A4) for the daily recap.
- API-FOOTBALL expansion (shrink the `id=null` manual case); backend runtime artifact store; external-
  signal projector generalization.
