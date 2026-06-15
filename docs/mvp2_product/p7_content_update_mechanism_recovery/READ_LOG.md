# P7 — READ_LOG

> Every file inspected during P7 discovery (read-only). Branches read via `git show <ref>:<path>`;
> current-main files read directly. Format: Branch | File | Reason | Key finding | Reuse/discard/uncertain.

## P0 design (feature/mvp2-growth-p0-design 5535c61) — original intent

- **p0-design | GROWTH_P0_SHARE_CARD_DESIGN.md** | original share-card intent | Card A = pre-match strong call; Card B = recap accountability ("archived judgement vs honest outcome — differentiates us from pick-selling"); P0 cards were screenshots, no QR, every string a guard-passed LLM field | **reuse** (now runtime ShareCardPage)
- **p0-design | GROWTH_P0_GROUP_CTA_COPY.md** | CTA/group copy intent | every fan-read string verbatim from a guard-passed artifact; operator replaces only `[群链接由运营填写]`; fixed send order; frame line 赛前看方向，临场看变量，赛后看校准 | **reuse**
- **p0-design | GROWTH_P0_MANUAL_INVITATION_FLOW.md** | invite intent | P0 = zero runtime; manual screenshot+link share, mark-sent + SEND_LOG; hard limits (no per-user link/QR/reward) | **reuse** as compliance ceiling (P1 lifted limits under Owner GO)
- **p0-design | GROWTH_P0_OPERATOR_SOP.md** | per-fixture send discipline | before-send live-scan PASS, queue=approved, Owner GO per fixture+channel, manual paste, mark-sent+screenshot, T-30 watch, A4 recap follow-up | **reuse** (governs first-send gate)
- **p0-design | GROWTH_P0_CHANNEL_TAGGING_DESIGN.md** | attribution intent | know channel never user; fixed 6-tag set; no UTM/per-user codes/QR in P0 | **reuse** (ported into P1 ALLOWED_CHANNELS)
- **p0-design | GROWTH_P0_GUARD_SPEC.md** | guard intent | 5 forbidden classes × 4 langs; §8 names a future check_growth_material.py | **reuse** (became check_growth_copy.py)
- **p0-design | GROWTH_P0_COMPLIANCE_NOTE.md** | posture | P0 not a referral/reward system; 6 conditions before any runtime growth feature | **reuse** (P1 satisfied them)

## P1 ambassador automation (feature/mvp2-growth-p1-automation a701eaa)

- **p1-automation | backend/app/models/growth.py** | ambassador tables | 5 additive tables (Ambassador/Click/JoinIntent/Contribution/AuditLog); NO money/odds/parent-child columns | **reuse** — byte-identical on main
- **p1-automation | backend/app/services/growth/growth_service.py** | mechanism logic | join=10pts/share=2pts, caps 100/day 1000/mo, CODE_RE ^(QG|TT|FO)-…, confirm/review → MTC via wallet rails, audit row per mutation | **reuse** — byte-identical on main
- **p1-automation | backend/app/routers/growth.py** | endpoints | public click/join-intent (rate-limited, no PII); admin x-admin-token CRUD/dashboard/export | **reuse** — wired main.py:49
- **p1-automation | frontend/src/pages/JoinPage.tsx** | /join landing | ref capture + persona value-prop + group-link CTA; no QR/code echo to visitor | **reuse** (+1 ShareBlock line from P1.1)
- **p1-automation | frontend/src/growth/refCapture.ts** | attribution | first-touch ?ref= (30-day localStorage), posts /click, no PII, never breaks product | **reuse**
- **p1-automation | frontend/src/pages/GrowthAdminPage.tsx** | operator dashboard | /internal/growth, x-admin-token wall, code create + channel-contribution table + intent/contribution review + QR preview (operator-only); no nav link | **reuse**
- **p1-automation | scripts/mvp2_growth_cli.py, check_growth_copy.py** | CLI + guard | same service layer; 4-lang forbidden wordlists | **reuse** (guard globs extended for later surfaces)
- **p1-automation | GROWTH_P1_AUTOMATION_DESIGN.md, APP_FEASIBILITY_ASSESSMENT.md** | mechanism spec + channel strategy | full ambassador journey; hybrid community-first + PWA-lite, native deferred | **reuse** (docs)

## Share / refresh / strongcopy (cd8d35d / 7fe23bb / 0a73ee6) + current projection

- **p1-1-share cd8d35d | App.tsx, ShareCardPage.tsx, ShareBlock.tsx** | /share + /join routes, QR card | share-as-projection, kickoff-freeze | **reuse** (all routes on main, evolved)
- **p1-1-share | growth/shareTemplates.ts** | share copy | judgement lines from LLM fields; recap nextFixtureId hardcoded '1489371' | **discard old** (superseded by canonical projection)
- **main | growth/shareTemplates.ts** | current share copy | delegates to buildStrongCall/buildRecapCall + observation fallback | **reuse**
- **p1-1b-refresh 7fe23bb | scripts/mvp2_growth_cli.py refresh/package** | refresh wrapper | emits {today,next,recap}_<fid>_<lang>_<ref>.md + refresh_summary.json | **reuse** (evolved with lifecycle gate + registry source)
- **p1-1c-strongcopy 0a73ee6 | growth/strongCallProjection.ts** | canonical projection | buildStrongCall/buildRecapCall, splitScoreband, harmonizedRisk; ONE source for all surfaces | **reuse** — extended by P5 (artifact) + P6 (NEXT_HOOK de-hardcode)
- **0a73ee6 | components/StrongSignalCard.tsx** | /predict strong card | full projection render incl external_expectation + T-30 + #live30 | **reuse**
- **main | data/externalSignalData.ts + scripts/mvp2_project_external_signals.py** | external_expectation | fixed Owner-safe lines from operator-recorded enums; only 1489371 has a projection JSON; TEAMS map hardcoded to that fixture | **reuse** (per-fixture re-run needed)
- **main | backend/app/models/prediction.py** | legacy model fields | prob_home/draw/away, recommended_score, risk_level, confidence (rule baseline); NOT read by any MVP2 surface | **disconnected/legacy** — keep out (no fake probability)

## Sync / lifecycle / runtime / backend (65f2202 / 7e9703b / 8a6215b / 69e7c5b)

- **main | scripts/mvp2_fixture_lifecycle.py** | canonical lifecycle | SCHEDULED..ARCHIVED, decide()/gates(), time-inference defeats stale NS; selftest 14 | **reuse** (canonical)
- **main | backend/app/services/lifecycle.py, frontend/src/lib/freshness.ts** | P1.2b mirrors | same states/thresholds; freshness.ts pickActiveFixture/heroEntries now unused (superseded by selectProductLoop) | **reuse** (flag dead helpers)
- **main | scripts/mvp2_match_sync.py** | daily slate sync | manual_scores_<date>.md → registry + recap_queue + dual manifests; KNOWN maps only 3 fixtures; never builds frames / calls LLM | **reuse** — THE disconnect point
- **main | frontend/src/data/dailyFixtures.ts** | three-tier fetch + selection | backend→static→bundled; selectProductLoop + hasPredictionArtifact lead-gate (P6) | **reuse**
- **main | backend/app/{models/runtime_manifest,services/daily_fixtures_service,routers/daily_fixtures}** | backend runtime store | runtime_manifests table, GET + admin upload, P1.4 buckets; no user/payment/attribution columns | **reuse** — wired main.py:50
- **main | frontend/public/data/daily-fixtures.json** | runtime source | 7 fixtures dated 2026-06-14 | **reuse**
- **main | frontend/src/components/MatchDesk.tsx** | P1.4 orchestration UI | RecapDesk/UpcomingNeedsNarrative/OperatorStatusLine; shows 复盘生成中/待生成 internal chips | **discard** — DEAD CODE (never imported; superseded by HomeProductLoop)

## Orchestration / gate / P3–P6 evolution

- **p1-4 051926c | scripts/mvp2_match_sync.py recap-queue, backend buckets** | match→product orchestration | recap_queue classification (NEEDS_A4_RECAP…), backend completed/upcoming/product_status buckets | **reuse** (backend live)
- **p1-5 5eacae6 | GROWTH_P15_FIRST_SEND_GATE.md, FIRST_SEND_RUNBOOK_1489371.md** | first-send gate | 7 gates; Gate 4/7 pending | **reuse** (ops source of truth; both on main)
- **main | components/HomeProductLoop.tsx** | P3/P6 homepage loop | HotspotPrediction first (P6 score-call teaser) → HotspotRecap → schedule → other recaps → CTA | **reuse**
- **main | data/predictionArtifacts.ts + predictionArtifacts/manual_Nether-Japan-20260614.json + observation_1489371.json** | P4/P5 artifact tier | operator-confirmed strong call + observation receipt; hasPredictionArtifact gates the lead | **reuse**
- **main | components/ArtifactTacticalRoom.tsx, ObservationReceipt.tsx** | P5 detail views | strong call + #live30 + calibration; trust-receipt | **reuse**
- **main | scripts/mvp2_editorial_agent.py + GROWTH_P15C_EDITORIAL_AGENT.md** | editorial selection | PROMPT BUILDER ONLY (no API, no state write, no ranking — Owner decree) | **reuse** (not a content producer)
- **main | docs/data_audit/mvp2_predictions/selected_hotspot_20260614.json** | persisted editorial pick | fixture_key + artifact_path + operator_confirmed; **grep proves NO code reads it** | **uncertain** — audit-only, disconnected from runtime
- **main | docs/mvp2_product/{HOMEPAGE_PRODUCT_LOOP_GATE,P6_DAILY_WORKFLOW}.md + p3/p4/p5/p5b/p6 reports** | gate + SOP + phase reports | 7-step daily MVP; each phase frontend-only, Send HOLD | **reuse** (DAILY_UPDATE_FLOW.md slightly stale: calls selected_hotspot "missing" though now shipped)

## Data-source + modeling + LLM pipeline (current main)

- **main | scripts/mvp2_build_scoutscore_v0_2_factors.py** | core modeling frame | Elo(1500/K32/+60home)/last-10 form/H2H/Poisson bands from kaggle CSV + Scout Pack JSON; hardcoded to 5 fixtures; requires a Scout Pack sample | **reuse** — fixture-locked, never invoked by daily loop
- **main | scripts/mvp2_build_trial_prediction_frame.py** | A2 frame | scoutscore_output {primary_lean, score_range bands, risk_level, what_could_flip, recheck_30min}; default 1489369/1489371 | **reuse**
- **main | scripts/mvp2_generate_product_proof_narratives.py + check_mvp2_product_narrative_guard.py** | LLM narrative gen + guard | DeepSeek default (Gemini benchmark); fills ~25 ProductNarrative fields; 5-retry guard loop; SAMPLES hardcoded | **reuse**
- **main | scripts/mvp2_generate_{trial_prediction_narratives,rescore_models}.py, mvp2_build_{rescore_diff,recap_frame_real,event_impact}.py** | tactical_read / t30 / A3 diff / A4 recap | all keyed to the same sample set; A3/A4 gated on archived artifacts + live API | **reuse**
- **main | frontend/src/data/{productNarrativeData,rescoreData,narrativeData}.ts + productNarratives/ + rescoreModels/ + narratives/** | bundled LLM data | maps ONLY the sample ids; getProductNarrative(manual fixture) = null | **reuse**
- **main | scripts/check_prediction_artifact.py** | the only guard for manual artifacts | validates structure + safe vocab + Han=0 + confirmed-strong-call; does NOT validate data/model provenance or that external_expectation corresponds to a real signal | **reuse** (provenance gap)
- **main | frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json** | the daily manual hotspot content | ALL rich fields hand-authored, source=operator_confirmed, no model/LLM provenance | **reuse** — central evidence of the content-production loss
