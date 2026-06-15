# P8 P0 — Implementation Note (Data-backed Artifact Recovery)

> Owner GO 2026-06-15. Scope: **frontend / scripts / docs only.** No backend, no schema migration, no
> external LLM/API calls, no auto-send. `win_prob` and numeric `confidence` are **never** invented.

## What this restores (and what was actually wrong)

The historical content facts were **not deleted** — the old data/model fields still exist on `main`
(backend `baseline.py` → `/api/v1/matches`; the ScoutScore + LLM `ProductNarrative` layer). The
daily-refresh path **bypassed** them: a daily hotspot becomes an `id=null` manual fixture → no backend
`Prediction` → no bundled `ProductNarrative` → an operator-only artifact with the structured model
sockets left null. Root cause = **mapping / route-resolution / generation-wiring loss**, not data
absence. P8 P0 reconnects the **provenance + model-field structure** into the existing
`selected_hotspot → prediction artifact` flow.

## Chain delivered

`selected_hotspot → prediction artifact → source_facts → model_fields → llm_judgment /
operator_confirmation → homepage score hook → /predict strong tactical room + data block →
/internal/daily readiness`.

## Changes

| Area | File | Change |
|---|---|---|
| Schema (frontend) | `frontend/src/data/predictionArtifacts.ts` | Added `ArtifactSourceFacts`, `ArtifactModelFields`, `ArtifactLlmJudgment`, `ArtifactOperatorConfirmation` interfaces + optional fields on `PredictionArtifact`. Back-compat: legacy `i18n`/`field_sources` still drive render. |
| Data | `frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json` | Added `source_facts` (data_mode=manual, has_model_fields=true, missing_fields=[win_prob,confidence]), `model_fields` (recommended_score "2-1", backup ["1-1","2-2"], risk_level "中高", **win_prob=null, confidence=null**, source `operator_estimated`, no_fake_probability=true), `llm_judgment`, `operator_confirmation`. |
| /predict | `frontend/src/components/ArtifactTacticalRoom.tsx` (+ `global.css`) | New customer-safe **数据与建模依据** block (`DataBacking`): fixture-fact source, data mode + source tag, recommended score + backup, risk level, missing items (no auto win-rate / numeric confidence), judgement source — persona voice, no model/AI/probability/betting words; vi/my Han=0; win_prob/confidence never shown. |
| Projection | `frontend/src/growth/strongCallProjection.ts` | `buildStrongCallFromArtifact` now prefers source-tagged `model_fields.recommended_score`/`backup_scores` (locale-neutral) when `source != unavailable`; localized risk word kept (model_fields.risk_level is the canonical mirror); unavailable numerics never enter `StrongCall`. |
| /internal/daily | `frontend/src/pages/DailyStatusPage.tsx` | Added readiness rows: source_facts, model_fields (source/status/score/risk), win_prob/confidence (na = unavailable acceptable), no-fake-probability, source-tag legend, operator confirmation. |
| Guard | `scripts/check_prediction_artifact.py` | New `scan_model_provenance`: requires `source_facts` + `model_fields` + valid `model_fields.source`; **rejects non-null win_prob/confidence**; requires `no_fake_probability=true`; a presented score/risk must be source-tagged (not `unavailable`); `has_model_fields` must agree with the source tag. |
| Guard | `scripts/check_daily_readiness.py` | Selected-hotspot artifact must carry `source_facts` + `model_fields`; win_prob/confidence acceptable only as null; `no_fake_probability` true. Selftest fixture updated. |
| Guard | `scripts/check_growth_copy.py` | Documented that the existing artifact/component globs cover the P8 blocks; engineering docs intentionally excluded (they discuss model/LLM as internal terms). |

## What P0 does NOT claim

- **No real `win_prob` / numeric `confidence`.** They stay `null` (`model_fields`) and are listed in
  `source_facts.missing_fields`; the UI shows "暂无自动胜率 / 数值置信度".
- The current hotspot's model fields are **`operator_estimated`** (a disclosed qualitative call), not
  computed — surfaced with their source tag everywhere.
- `selected_hotspot` (P7) and `/internal/daily` are **preserved**; no auto-send.

## P1 (deferred, each its own GO)

Real model computation for new fixtures (adapt the existing ScoutScore frame builder → `source:"computed"`),
automated DeepSeek/Gemini/Kimi generation with `source_refs`, API-FOOTBALL expansion (shrink the `id=null`
case), backend runtime artifact store (Option E), external-signal generalization, A4 full recap pipeline.
