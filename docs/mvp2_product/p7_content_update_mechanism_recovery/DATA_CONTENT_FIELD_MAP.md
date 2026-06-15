# P7 — DATA_CONTENT_FIELD_MAP

> Every prediction/recap field: historical production source vs current source, which surfaces consume it,
> whether it is produced for a DAILY MANUAL hotspot (e.g. Netherlands–Japan) today, and the recovery option.
> Production source legend: **DATA/MODEL** (ScoutScore: kaggle Elo/form/H2H/Poisson) · **LLM** (DeepSeek/Gemini,
> guard-passed) · **OPERATOR** (hand-authored artifact) · **— none** (intentionally absent).
> "Daily-manual today" = how the field is actually produced right now for a new id=null hotspot.

| Field | Historical source (sample fixtures) | Current source | home | predict | recap | share | Daily-manual today | Missing today? | Recovery option |
|---|---|---|---|---|---|---|---|---|---|
| **fixture_id** (internal numeric) | DATA — `mvp2_match_sync.KNOWN` map | same | – | route | route key | route key | **null** (only 3 fixtures mapped) | yes for manual | keep external_game_id key; map an id only if/when a real fixture exists |
| **external_game_id** | DATA — match_sync (`af:<id>` or `manual:<H6>-<A6>-<date>`) | same | key | route resolve | – | – | **OPERATOR-named** in slate; e.g. `manual:Nether-Japan-20260614` | no | OK (it is the artifact key) |
| **home / away** | DATA — match_sync KNOWN / manual slate | same / artifact | ✓ | ✓ | ✓ | ✓ | OPERATOR (slate + artifact) | no | OK |
| **kickoffUtc** | DATA — KNOWN map | same / artifact | ✓ | ✓ | – | – | **null** for manual (no KNOWN entry) | partial | operator fills in artifact, or add to slate |
| **lifecycle_state** | DATA/MODEL — `mvp2_fixture_lifecycle.decide()` | same (canonical, 3 mirrors) | ✓ | freeze | gate | freeze | computed from slate (works for manual) | no | OK — canonical, healthy |
| **win_prob** (prob_home/draw/away) | DATA/MODEL — backend rule predictor | `backend/prediction.py` only | – | – | – | – | **— none** (deliberate: no fake probability) | by design | DO NOT surface (compliance floor) |
| **recommended_score / score_call** | DATA/MODEL `poisson_bands` → LLM `scoreline_view` → `splitScoreband` | LLM band **or** artifact `score_call` | teaser 主比分 | card | – | card+copy | **OPERATOR hand-typed** "2-1" (no Poisson) | provenance lost | P1: run Poisson for the hotspot; P0: operator-confirmed allowed (disclosed) |
| **primary_score** | derived `splitScoreband[0]` | derived **or** artifact `score_call` | ✓ | ✓ | – | ✓ | OPERATOR (from score_call) | provenance lost | as above |
| **backup_scores** | derived `splitScoreband` alts | derived **or** artifact `backup_score.split('/')` | ✓ | ✓ | – | ✓ | OPERATOR "1-1 / 2-2" | provenance lost | as above |
| **risk_level / risk_label** | DATA/MODEL `upset_band(elo_gap,missing)` → LLM word → `harmonizedRisk` | LLM **or** artifact `risk_level` | ✓ | ✓ | – | ✓ | **OPERATOR hand-typed** "中高" (no upset_band) | provenance lost | P1: run upset_band; P0: operator-confirmed allowed |
| **risk_note** | DATA/MODEL frame → LLM | artifact `risk_note` (→ `why` fallback) | – | ✓ | – | – | OPERATOR | provenance lost | as above |
| **confidence** | DATA/MODEL rule (0–100) | artifact `confidence` | – | – | – | – | **null** (operator choice; a number reads as a probability promise) | by choice | keep null unless Owner asks for a non-numeric band |
| **main_lean / primary_direction** | DATA/MODEL Elo `favoured` → LLM prose | LLM **or** artifact `primary_direction` | teaser 俅哥主看 | card | – | card+copy | **OPERATOR** "赛前倾向荷兰，但冷门风险不低" | provenance lost | P1: Elo gap → lean; P0: operator-confirmed |
| **top_variable** | LLM (`watch_next_signals[0]` / `risk_factors[0]`) | LLM **or** artifact `top_variable` | – | ✓ | – | card | OPERATOR | provenance lost | LLM when reconnected |
| **why** | LLM `hero_subtitle` | LLM **or** artifact `why`/`risk_note` | – | ✓ | – | copy | OPERATOR | provenance lost | LLM when reconnected |
| **tactical_read / tactical_matchup** | LLM (trial narrative required field) | LLM **or** artifact `analysis.tactical_matchup[]` | – | ✓ (tactical room) | – | – | **OPERATOR** (3 hand bullets) | yes (no LLM) | P1: run trial narrative generator for the hotspot |
| **risk_factors / risk_variables** | LLM ProductFactor w/ **source_refs / assumption_flag** | LLM **or** artifact `analysis.risk_variables[]` (NO source_refs) | – | ✓ | – | – | **OPERATOR** (no source_refs) | provenance lost | LLM/model when reconnected; guard should require provenance |
| **external_expectation** | OPERATOR-recorded enums → `mvp2_project_external_signals` → fixed safe lines | projection (`externalSignals/{id}.json`, only 1489371) **or** artifact `analysis.external_expectation[]` | – (not on home) | ✓ | – | card line[0] | **OPERATOR** hand lines (guard checks only SAFE_EXT words, not that a real signal exists) | thin | P1: generalize `mvp2_project_external_signals` off the hardcoded TEAMS map; guard: require a recorded signal |
| **t30_checklist** | DATA/MODEL skeleton (squads/GK triggers) → LLM copy → `rescoreModels/{id}.{lang}.json` | LLM rescore model **or** artifact `analysis.thirty_minute_checklist[]` (static) | – | ✓ | – | – | **OPERATOR** static list (no rescore model, no live diff) | yes | P1: run rescore generator; P0: static checklist OK as placeholder |
| **t30_update** (live 30-min re-score) | DATA `mvp2_build_rescore_diff` (announced XI/GK) → LLM `trial_rescore_update` | not produced for daily fixtures | – | (#live30 anchor) | – | group msg | **— none persisted** (operator sends in-group manually) | yes | P0: a T-30 placeholder slot in the artifact; P1: rescore-diff for the hotspot |
| **recap_receipt** (pre_match_call/actual/assessment) | DATA/MODEL recap_frame + LLM real_recap (sha256 provenance) | OPERATOR observation artifact (recovered) | recap row | – | ✓ | card | **OPERATOR** "recovered_from_bundled_pre_match_receipt + manifest_score", `recap_ready:false` | A4 pipeline not run | P0: keep observation receipt; P1: run A4 recap pipeline |
| **calibration_points** | LLM recap | OPERATOR observation `calibration_points[]` | – | – | ✓ | – | OPERATOR | OK (present) | OK |
| **deviation** | LLM recap | OPERATOR observation `deviation` | – | – | ✓ | card | OPERATOR | OK (present, P5b) | OK |
| **next_impact** | LLM recap | OPERATOR observation `next_impact` (match-specific) | – | – | ✓ | – | OPERATOR | OK (P6 de-hardcoded NEXT_HOOK) | OK |
| **share_copy** | LLM judgement lines + Owner framing | `shareTemplates` (canonical projection) **or** artifact `operations.share_copy` | – | – | – | ✓ | OPERATOR (artifact) / projection (narrative) | OK | OK (CLI mirror has a stale "Brazil vs Morocco" hardcode to fix) |
| **share_card** | P0 screenshot → P1.1 runtime ShareCardPage + QR | same (projection + artifact fallback, kickoff-freeze) | – | (open) | (open) | ✓ QR | works for manual (renders artifact) | no | OK |
| **join / ref** | refCapture first-touch + DEFAULT_REF (QG/TT/FO) | same | ✓ | ✓ | ✓ | ✓ | works (codes need prod creation) | no (attribution) | OK |

## Reading of the table
- **Identity + lifecycle + slate + share/join = healthy** for daily manual fixtures (the slate-update backbone works).
- **Every "judgement" field (score_call, risk_level, main_lean, top_variable, why, tactical, risk_factors, external_expectation, t30) is produced by OPERATOR hand-authoring for the daily hotspot, with NO model/LLM provenance** — even though the model (Poisson/Elo/upset_band) and LLM (the full contract + guard) that historically produced them still exist on main, just fixture-locked.
- **win_prob / confidence are intentionally absent** (compliance: no fake probability) — not a loss to recover.
- **recap is operator-recovered** (observation receipt), not the A4 model+LLM recap.
