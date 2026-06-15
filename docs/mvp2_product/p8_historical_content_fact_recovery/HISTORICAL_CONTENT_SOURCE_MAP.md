# P8 — HISTORICAL_CONTENT_SOURCE_MAP

> Per field: where it came from historically, the file/script/API, its **real / API / mock-seed /
> computed-model / static-bundled / operator** nature, the current equivalent, where it was lost, and a
> recovery decision. Legend for nature:
> **API** = real API-FOOTBALL data · **SEED** = seeded/placeholder DB value · **MODEL(seed)** = computed by
> `baseline.py` rule model from *placeholder seed strengths* (deterministic, not real form) ·
> **MODEL(scout)** = computed by ScoutScore v0.2 from *real kaggle* Elo/form/H2H/Poisson · **LLM** =
> DeepSeek/Gemini guard-passed prose · **STATIC** = bundled constant · **OPERATOR** = hand-authored.

| Field | Historical source | Historical file/script/API | Nature | Current equivalent | Lost where? | Recovery decision |
|---|---|---|---|---|---|---|
| **fixture_id** (internal numeric) | `mvp2_match_sync.KNOWN` map / DB `Match.id` | `scripts/mvp2_match_sync.py`, `backend models` | API/SEED | `DailyFixtureRow.id` (null for manual) | manual hotspots are `id=null` (only 3 fixtures mapped) | keep `external_game_id` as the key; map an id only when a real fixture exists |
| **external_game_id** | match_sync slug (`af:<id>` / `manual:<H6-A6-date>`) | `mvp2_match_sync.py` | OPERATOR/API | `DailyFixtureRow.external_game_id` / `fixture_key` | **not lost** (it is the artifact key) | OK — canonical route key |
| **home / away** | match_sync KNOWN / manual slate | `mvp2_match_sync.py`, artifact | API/OPERATOR | manifest + artifact `home/away` | not lost | OK |
| **kickoff_time** | DB `Match.kickoff_time` / KNOWN map | `match_service.py`, `mvp2_match_sync.py` | API/SEED | `DailyFixtureRow.kickoffUtc` (null for manual) | manual fixture has no KNOWN entry → `null` | operator fills artifact, or add to slate |
| **status** | DB `Match.status` | `schemas/match.py`, `match_service.py` | API | `DailyFixtureRow.status` + `lifecycle_state` | not lost (lifecycle layer healthy) | OK |
| **win_prob** (home/draw/away) | `baseline.predict()` → `Prediction` → `/api/v1/matches` | `backend/app/services/modeling/baseline.py`, `schemas/match.py`, `transform.ts` | **MODEL(seed)** — placeholder strengths, `ai_provider=mock` | `transform.ts`→store→**legacy mock tiles ONLY**; artifact `win_prob="unavailable"` | **manifest boundary** — `dailyFixtures`/`daily_fixtures_service` carry no model fields; manual hotspot has no `Prediction` row | **DO NOT surface as a probability** (compliance floor). P1: only if Owner authorizes a non-numeric band or a disclosed seed value. |
| **recommended_score** | `baseline._recommended_score()` → `Prediction` | `baseline.py`, `prediction.py`, `seed.py`, `fixtures_sync.py`, `transform.ts` | MODEL(seed) | OPERATOR `score_call` in artifact (hand-typed "2-1") | manifest boundary + no narrative for manual | P1: run a model/Poisson band for the hotspot; P0: operator-confirmed allowed (disclosed) |
| **risk_level** | `baseline.predict()` (margin+volatility) **and/or** ScoutScore `upset_band` → LLM word | `baseline.py`; `mvp2_build_scoutscore_v0_2_factors.py`; narrative JSON | MODEL(seed) / MODEL(scout)+LLM | artifact `risk_level` (hand-typed "中高") / narrative `risk_level` word | manifest boundary | P1: run `upset_band`/rule model; P0: operator-confirmed allowed |
| **risk_note** | `baseline.predict()` hand-mapped text **or** ScoutScore frame→LLM | `baseline.py` (3 canned strings); narrative JSON | MODEL(seed) / LLM | artifact `risk_note` (→ `why` fallback) | manifest boundary | P0: operator; P1: model/LLM |
| **confidence** | `baseline.predict()` 45–88 numeric | `baseline.py`, `Prediction`, `transform.ts` | MODEL(seed) | artifact `confidence=null`; `field_sources.confidence="unavailable"` | manifest boundary + deliberate null (a bare number reads as a probability promise) | keep `null`/non-numeric band unless Owner asks; never invent |
| **lifecycle_state** | `mvp2_fixture_lifecycle.decide()` / `lifecycle.py` | `scripts/mvp2_fixture_lifecycle.py`, `backend/app/services/lifecycle.py` | computed (deterministic) | same — canonical, 3 mirrors (backend schema + manifest + freshness.ts) | **NOT lost — healthy** | OK |
| **pre_match_allowed** | `lifecycle.py` runtime freshness | `schemas/match.py`, `lifecycle.py`, `freshness.ts` | computed | `DailyFixtureRow.preMatchAllowed` / schema field | not lost | OK |
| **today_package_allowed** | `lifecycle.py` | `schemas/match.py`, `lifecycle.py` | computed | schema field (gate) | not lost | OK |
| **recap_needed** | `lifecycle.py` / match_sync recap_queue | `schemas/match.py`, `mvp2_match_sync.py` | computed | `DailyFixtureRow.recapNeeded` | not lost | OK |
| **recap_ready** | `lifecycle.py` + recap artifact presence | `schemas/match.py`, observation artifact | computed | `DailyFixtureRow.recapReady` / observation `recap_ready` | not lost | OK |
| **freshness_reason** | `lifecycle.py` | `schemas/match.py`, `lifecycle.py`, `freshness.ts` | computed | schema field / freshness.ts | not lost | OK |
| **main_lean / primary_direction** | ScoutScore Elo `favoured` → LLM prose | `mvp2_build_scoutscore_v0_2_factors.py` → narrative JSON | MODEL(scout)+LLM | narrative `main_lean` (5 fixtures) / artifact `primary_direction` (operator) | fixture-locked; manual → operator | P1: Elo→lean generator; P0: operator-confirmed |
| **scoreline_view** | ScoutScore Poisson bands → LLM band string | scoutscore script → narrative JSON | MODEL(scout)+LLM | narrative `scoreline_view` / artifact `score_call` | fixture-locked | P1: Poisson band; P0: operator |
| **tactical_read / tactical_matchup** | LLM (required trial-narrative field) | `mvp2_generate_trial_prediction_narratives.py` | LLM | narrative `tactical_read` / artifact `analysis.tactical_matchup[]` (operator) | fixture-locked; no generator for manual | P1: run trial-narrative generator for the hotspot |
| **risk_factors / risk_variables** | LLM `ProductFactor` with **`source_refs` + `assumption_flag`** | narrative JSON | LLM (provenanced) | narrative `risk_factors[]` / artifact `analysis.risk_variables[]` (**no source_refs**) | fixture-locked; manual loses provenance | P1: LLM/model; guard should require provenance on reconnect |
| **external_expectation** | OPERATOR enums → projection → safe lines | `mvp2_project_external_signals.py` → `externalSignalData` | OPERATOR→STATIC | projection (`externalSignals/{id}.json`, only 1489371) / artifact `analysis.external_expectation[]` | hardcoded TEAMS map; thin | P1: generalize projector; guard: require a recorded signal |
| **strong call** (the projection) | `buildStrongCall` over narrative | `frontend/src/growth/strongCallProjection.ts` | derived | same (narrative → artifact fallback) | **not lost** — already canonical | OK; should read a `model_fields` block when present |
| **share copy / card title / join cta** | LLM lines + Owner framing → `shareTemplates` | `shareTemplates.ts`, artifact `operations` | LLM/OPERATOR | same | not lost | OK |
| **recap receipt** (pre_match_call/actual/assessment) | ScoutScore recap_frame + LLM `real_recap` (sha256 provenance) | `mvp2_build_recap_frame_real.py` → narrative `real_recap` | MODEL(scout)+LLM | OPERATOR observation artifact (recovered, `recap_ready=false`) | A4 pipeline not run for daily | P0: keep observation receipt; P1: run A4 recap pipeline |

## Three historical provenance tiers (the key structural fact)

1. **MODEL(seed) numeric tier — the OLD `/matches` API path.** `win_prob`, `recommended_score`,
   `risk_level`, `risk_note`, `confidence` as **structured/numeric** fields, computed by `baseline.py` from
   **placeholder seed strengths** (`_stable_strength`, `ai_provider=mock`), DB-persisted on `Prediction`,
   served by `/api/v1/matches`, mapped by `transform.ts`. **Still wired into `useAppStore`, but only feeds
   the demoted mock tiles.** *This is the "structured prediction/model fields" the owner remembers.*
2. **MODEL(scout)+LLM qualitative tier — the MVP-2 ProductNarrative path.** `main_lean`,
   `scoreline_view` (band string), `risk_level` (word), `risk_factors` (with `source_refs`),
   `tactical_read`, `validated_factors`, recap. From **real kaggle** ScoutScore frames → DeepSeek/Gemini →
   guard. **Hard-mapped to 5 fixture ids; no generator for a new daily fixture.** Note: this tier never
   carried numeric `win_prob`/`confidence` — it always expressed the call qualitatively.
3. **OPERATOR tier — the current daily artifact.** Hand-authored judgement, `win_prob`/`confidence` =
   `unavailable`, `data_snapshot`/`modeling_output`/`generated_judgment` = `null`.

**The recovery is to rebuild a bridge from tier 1 (numbers, honestly seed-grade) and tier 2 (real
ScoutScore frame + LLM) into the tier-3 daily artifact — not to un-delete anything.**
