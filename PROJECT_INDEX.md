# PROJECT_INDEX — worldcup2026 (Giành Cup)

> Top-level navigation for a new engineering thread. **Read `CLAUDE.md` first.** Date: 2026-06-12.
> Status: **Track A P0 ACCEPTED (PASS WITH CONDITIONS) — deploy-verification handoff.** Trial product
> is trilingual zh/vi/my; Track A ops tooling implemented + dry-run verified @ `b458fd5`; trial sends
> BLOCKED until operator deploys `b458fd5`+ to the trial frontend, sets the Render SPA rewrite, and
> the LIVE visible-copy scan passes. Track B = design-only (do NOT implement). Next thread start
> command: `docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md` ★★ section.

## Active branch / PR
- **Branch:** `feature/mvp2-api-football-ingestion`
- **PR #3:** Draft · base `main` · not ready · not merged
- **PR #2** (`feature/real-data-zh-vi-verification`): discovery Draft · untouched
- **main:** untouched · **external operation:** paused · **public_ready:** false

## Core docs (read order)
1. `CLAUDE.md` — engineering entry point + current status + guardrails
2. `docs/MVP_STATUS.md` — status snapshot (MVP-2 block at top)
3. `docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md` — full handoff + first-command for next thread
4. `docs/MVP2_EVIDENCE_BOARD_V2_DESIGN.md` — v2 design (CLOSED / gate-ready)
5. `docs/MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md` — v2 boundary-freeze (Owner GO required)
5b. **LLM narrative (current focus):** `docs/MVP2_LLM_NARRATIVE_ARCHITECTURE.md` · `docs/MVP2_LLM_NARRATIVE_CONTRACT.md` ·
   `docs/MVP2_LLM_NARRATIVE_PROVIDER_REVIEW.md` · `docs/prompts/mvp2_scoutscore_narrative_{zh,vi}.md` · `docs/MVP2_PRODUCT_VOICE_GUIDE.md`
6. `docs/MVP2_SCOUTSCORE_V0_MODEL_CARD.md` · `docs/MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md` ·
   `docs/MVP2_USER_REVIEW_REPORT_855737.md` · `docs/MVP2_NEXT_DATA_REQUIREMENTS.md` ·
   `docs/MVP2_OPERATOR_REAL_DATA_REVIEW.md`

## Runtime entry points
- **Backend (FastAPI):** `backend/app/main.py`
  - `app/services/api_football_client.py` (Level-2 client) · `app/services/scout_pack/*` (contract/builder/features/model_notes/report) · `app/services/scoutscore/*` (factors/accountability/recap_view)
  - `app/routers/internal_scout_pack.py` (`/internal/scout-pack`, internal preview) · `app/routers/recap.py` (`/api/v1/recap/{id}`)
- **Frontend (Vite/React):** `frontend/src/App.tsx` (routes) · `pages/RecapDetailPage.tsx` · `pages/HomePage.tsx` (recap entry + bridge) · `data/recapData.ts` · `styles/global.css`
- **Offline build scripts (no live LLM):** `backend/scripts/mvp2_{ingest_scout_pack,build_productized_report,build_scoutscore}.py`
- **QA screenshot helpers:** `scripts/qa/mvp2_{scout_pack,recap_flow,evidence_board}_shots.mjs`
- **EBv2 + LLM narrative (additive):** frontend `pages/EvidenceBoardPage.tsx` · `components/{EvidenceBoard,NarrativeView,FactorCard,EvidenceCard,AiBoundaryCard,NextVariablesCard}.tsx` · `data/{evidenceData,narrativeData}.ts` · `data/narratives/855737.{zh-CN,vi-VN}.json`; LLM `scripts/mvp2_generate_scoutscore_narrative.py` + `scripts/check_mvp2_llm_narrative_guard.py`; artifacts `docs/data_audit/mvp2_llm_narratives/`; `render.yaml` (SPA fallback)

## Data artifacts (real, redacted)
- `docs/data_audit/mvp2_scout_pack_samples/` (855737/855741/977345/979139)
- `docs/data_audit/mvp2_scoutscore_v0/` · `docs/data_audit/mvp2_prediction_replay/` · `docs/data_audit/mvp2_prediction_accountability_reports/`

## QA screenshots
- `docs/qa_screenshots/mvp2_real_data_operator_review/` (internal preview + productized + accountability, zh/vi)
- `docs/qa_screenshots/mvp2_historical_recap_product_flow/` (home entry/bridge + recap detail/continuation, zh/vi)

## ★ Track A P0 — automated operation tooling (2026-06-11/12, latest)
- **Operator CLI:** `scripts/mvp2_ops.py` (scan / prematch / watch / rescore / recap / bundle / queue / status) ·
  queue/registry lib `scripts/mvp2_ops_queue.py` (selftest: `--selftest`)
- **Builders:** `scripts/mvp2_daily_scan.py` (A1) · `scripts/mvp2_build_rescore_diff.py` (A3, facts-only skeleton) ·
  `scripts/mvp2_build_recap_frame_real.py` (A4 real_recap frame w/ archived-prediction provenance)
- **Guard additions:** real_recap rules + trial_rescore_update checker (`--selftest-tracka`) · hardened
  standalone-AI regex (CJK-boundary) in narrative guard + visible scan · kaggle team aliases
  (`KAGGLE_TEAM_ALIASES` in the v0.2 builder — Bosnia/USA/Curacao/Türkiye…)
- **Registry/queue artifacts:** `docs/data_audit/mvp2_{daily_scan,ops_registry,ops_runs,review_queue,rescore_runs,send_kits}/`
- **Docs:** design `docs/MVP2_TRACK_A_AUTOMATED_OPERATION_DESIGN.md` · dry-run
  `docs/MVP2_TRACK_A_P0_DRYRUN_REPORT.md` · match-day runsheet `docs/mvp2/TRACKA_1489371_A3A4_RUNSHEET.md` ·
  Track B (design-only) `docs/MVP2_TRACK_B_SCOUT_REFERRAL_DESIGN.md` · review `docs/MVP2_TRACKAB_ENGINEERING_REVIEW.md`
- **Deploy gate evidence:** `docs/qa_screenshots/mvp2_tracka_deploy_verify/` (54026ad prod-build proof);
  live scan command: `python3 scripts/check_customer_visible_copy.py https://worldcup2026-izid.onrender.com`

## ★ June 11 Real Match Trial (2026-06-11)
- **Persona surfaces:** zh 中文先知 · vi Tiên Tri Bóng Đá (Giành Cup; engine ScoutScore; **no Cloud on football surfaces**; `<title>` → English brand line)
- **Trial pipeline:** `scripts/mvp2_verify_june11_fixtures.py` → `docs/data_audit/mvp2_june11_real_fixture_verification.json` · `scripts/mvp2_build_trial_prediction_frame.py` → `docs/data_audit/mvp2_trial_prediction_frames/{1489369,1489371}.json` · `scripts/mvp2_generate_trial_prediction_narratives.py` → `docs/data_audit/mvp2_trial_prediction_narratives/` (8/8 real LLM, guard PASS, `tactical_read` + persona enforced)
- **Frontend:** Home = persona status strip + TrialHeroCard (1489369 Mexico–South Africa opener) + secondary strip; **old mock demoted into `home-demo-fold`**; `/predict/:id` = persona tactical room (+`?ops=1` opens the operator fold) — `components/UpcomingTacticalStrip.tsx` · `pages/PredictPage.tsx` · `components/ProductProofViews.tsx` · `data/{productNarrativeData,upcomingFixtures}.ts`
- **Operator:** `docs/MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md` (copy-paste zh/vi group messages, [群链接由运营填写], send checklist, do-not-send) · review `docs/MVP2_JUNE11_TRIAL_PRODUCT_REVIEW.md` · shots `docs/qa_screenshots/mvp2_june11_trial/` · **send requires Owner GO; operation paused**

## Next decisions / actions (Owner + operator)
1. **Operator: manual deploy `b458fd5`+ to worldcup2026-izid** + Render SPA rewrite (`/* → /index.html → Rewrite`) — blocking all trial sends ·
2. After deploy: live visible-copy scan must PASS (15 surfaces zh/vi/my) before any link is sent ·
3. Per-fixture send GO (Owner): 1539000 (06-12 19:00 UTC) · 1489371 (06-13 22:00 UTC, A3/A4 first real run per runsheet) ·
4. Track A P1 items (each needs its own GO): dual-mode narrative endpoint · import.meta.glob bundling · queue-to-backend mirror ·
5. Track B: design-only, awaits B-GO-1 · 6. Myanmar persona final name (temp Football Oracle) · 7. Keep PR #3 Draft or split smaller PR.

## Hard guardrails
No public operation · no PR ready w/o Owner approval · no merge · no payment · no Token · no betting/odds/盘口/竞猜/投注 ·
no fake probability / archived prediction / SHAP / xG (unless source) / injuries inference · no frontend direct vendor call ·
no token/raw payload commit · vi Han=0 · mm → English. **No hand-written product narrative in templates (LLM generates; mock only as a marked fallback) · no engineering string-concatenated football analysis · no LLM-fabricated facts (source_refs or assumption_flag).**
