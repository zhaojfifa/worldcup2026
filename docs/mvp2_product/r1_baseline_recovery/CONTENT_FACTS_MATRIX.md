# R1 — CONTENT_FACTS_MATRIX

> Per field: historical source · current source · used today for the daily manual hotspot · missing? ·
> recovery action. Nature legend (historical): **api** (API-FOOTBALL) · **seed** (seeded DB) · **model**
> (computed) · **mock** (placeholder) · **operator** (hand-authored) · **LLM** (DeepSeek/Gemini, guarded)
> · **unavailable**. Compliance floor unchanged: `win_prob`/numeric `confidence` are NEVER faked.

| Field | Historical source (nature) | Current source | Used today (daily hotspot)? | Missing? | Recovery action |
|---|---|---|---|---|---|
| **fixture_id** | `mvp2_match_sync.KNOWN` / DB `Match.id` (api/seed) | manifest `id` | manual hotspot = `null` | partial | keep `external_game_id` key; map id only if a real fixture exists (P1 API expansion) |
| **external_game_id** | match_sync slug (api/operator) | manifest/artifact `fixture_key` | ✅ (`manual:Nether-Japan-20260614`) | no | OK (route key) |
| **home / away** | match_sync / slate (api/operator) | manifest + artifact | ✅ | no | OK |
| **kickoff_time** | `Match.kickoff_time` / KNOWN (api/seed) | manifest `kickoffUtc` / artifact | `null` for manual | partial | operator fills, or P1 API map |
| **status** | `Match.status` (api) | manifest `status` + `lifecycle_state` | ✅ | no | OK |
| **win_prob** | `baseline.predict()` seed-strength (model/mock) | `/api/v1/matches`→ demoted tiles only; artifact `model_fields.win_prob=null` | ❌ (deliberately null) | by design | **DO NOT fake.** P1: only if a real model source backs it; else stays `unavailable` |
| **recommended_score** | `baseline._recommended_score()` (model/mock) | P8 `model_fields.recommended_score` (operator_estimated) | ✅ "2-1" (operator) | provenance | **R1: builder fills from model-lookup if found, else operator_estimated (tagged)** |
| **risk_level** | `baseline` margin / ScoutScore `upset_band` (model) → LLM word | P8 `model_fields.risk_level` (operator_estimated) | ✅ "中高" (operator) | provenance | **R1: builder model-lookup → else operator_estimated** |
| **risk_note** | `baseline` canned / ScoutScore→LLM (model/LLM) | `model_fields.risk_note` / artifact i18n (operator) | ✅ (operator) | provenance | **R1: LLM prompt field → reviewed JSON → artifact** |
| **confidence** | `baseline.predict()` 45–88 (model/mock) | `model_fields.confidence=null` | ❌ null | by design | **DO NOT show a number** unless computed/seed (Owner P8 Q3) |
| **lifecycle_state** | `mvp2_fixture_lifecycle.decide()` (computed) | canonical (manifest+schema+freshness) | ✅ | no | KEEP (healthy) |
| **pre_match_allowed** | `lifecycle.py` (computed) | manifest `preMatchAllowed` / schema | ✅ | no | KEEP |
| **today_package_allowed** | `lifecycle.py` (computed) | schema gate | ✅ | no | KEEP |
| **recap_needed** | lifecycle / recap_queue (computed) | manifest `recapNeeded` | ✅ | no | KEEP |
| **recap_ready** | lifecycle + recap artifact (computed) | manifest `recapReady` / observation | ✅ | no | KEEP |
| **freshness_reason** | `lifecycle.py` (computed) | schema / `freshness.ts` | ✅ | no | KEEP |
| **main_lean** | ScoutScore Elo `favoured` → LLM (model+LLM) | narrative (5 fixtures) / artifact `llm_judgment.main_lean` (operator) | ✅ (operator) | LLM not run | **R1: prompt → reviewed LLM JSON → `llm_judgment`** |
| **scoreline_view** | ScoutScore Poisson band → LLM (model+LLM) | narrative / artifact `model_fields.recommended_score` | ✅ (operator) | LLM not run | **R1: model-lookup band → LLM; else operator** |
| **tactical_read** | LLM (required field) | narrative / artifact i18n + `llm_judgment.tactical_read` (operator) | ✅ (operator) | LLM not run | **R1: prompt → reviewed JSON** |
| **risk_factors** | LLM `ProductFactor` w/ `source_refs`+`assumption_flag` (LLM) | narrative / artifact i18n + `llm_judgment.risk_factors` (operator, no source_refs) | ✅ (operator) | provenance + LLM | **R1: prompt → reviewed JSON; guard should want source_refs when model-backed (P1)** |
| **external_expectation** | operator enums → projection → safe lines (operator→static) | projection (1489371 only) / artifact (operator, safe vocab) | ✅ (operator) | thin | **R1: prompt includes safe-wording rule; P1 generalize projector** |
| **t30_checklist** | rescore skeleton → LLM (`rescoreModels/*.json`) (model+LLM) | artifact `llm_judgment.t30_checklist` (operator static) | ✅ (operator) | rescore not run | KEEP slot; **R1: prompt includes it; P1 rescore generator** |
| **recap_receipt** | recap_frame + LLM `real_recap` w/ sha256 (model+LLM) | observation artifact (operator, `recap_ready=false`) | ✅ (operator receipt) | A4 not run | KEEP receipt; **P1 A4 pipeline** |
| **share_copy** | LLM lines + Owner framing (LLM/operator) | `shareTemplates` / artifact `operations.share_copy` | ✅ | no | KEEP; **R1: builder ensures it from `llm_judgment`/operator** |

## Reading
- **Identity + lifecycle + share = healthy** for the daily hotspot (the slate/update backbone works).
- **Every judgement field is OPERATOR-authored** for the daily hotspot today, with no model/LLM provenance — even though the model (ScoutScore/baseline) and LLM (full contract+guard) that historically produced them still exist on main, just not wired to the daily fixture.
- **win_prob / numeric confidence intentionally absent** (compliance) — not a loss to recover.
- **R1 closes the gap** by building the production chain (model-lookup → prompt → reviewed-LLM → artifact), with `operator_estimated` as the disclosed fallback when the lookup/LLM is unavailable.
