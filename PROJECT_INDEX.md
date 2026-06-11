# PROJECT_INDEX — worldcup2026 (Giành Cup)

> Top-level navigation for a new engineering thread. **Read `CLAUDE.md` first.** Date: 2026-06-10.
> Status: **MVP-2 LLM-Guided Product Narrative Refactor** · LLM pipeline PASS / customer narrative product-angle FAIL · next = **Betting-Logic Model Narrative Prompt Revision** (prediction first-principles, NOT gambling) · thread closed docs-only, runtime unchanged this round.

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

## ★ June 11 Real Match Trial (2026-06-11, latest)
- **Persona surfaces:** zh 中文先知 · vi Tiên Tri Bóng Đá (Giành Cup; engine ScoutScore; **no Cloud on football surfaces**; `<title>` → English brand line)
- **Trial pipeline:** `scripts/mvp2_verify_june11_fixtures.py` → `docs/data_audit/mvp2_june11_real_fixture_verification.json` · `scripts/mvp2_build_trial_prediction_frame.py` → `docs/data_audit/mvp2_trial_prediction_frames/{1489369,1489371}.json` · `scripts/mvp2_generate_trial_prediction_narratives.py` → `docs/data_audit/mvp2_trial_prediction_narratives/` (8/8 real LLM, guard PASS, `tactical_read` + persona enforced)
- **Frontend:** Home = persona status strip + TrialHeroCard (1489369 Mexico–South Africa opener) + secondary strip; **old mock demoted into `home-demo-fold`**; `/predict/:id` = persona tactical room (+`?ops=1` opens the operator fold) — `components/UpcomingTacticalStrip.tsx` · `pages/PredictPage.tsx` · `components/ProductProofViews.tsx` · `data/{productNarrativeData,upcomingFixtures}.ts`
- **Operator:** `docs/MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md` (copy-paste zh/vi group messages, [群链接由运营填写], send checklist, do-not-send) · review `docs/MVP2_JUNE11_TRIAL_PRODUCT_REVIEW.md` · shots `docs/qa_screenshots/mvp2_june11_trial/` · **send requires Owner GO; operation paused**

## Next decisions (Owner)
1. **June-11 trial-send review:** read `MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md` + screenshots → GO / NO-GO before 19:00 UTC kickoff ·
2. Confirm DeepSeek default provider (re-validated again on trial) · 3. Operator: Render SPA rewrite (`/* → /index.html`) + verify live ·
4. TheSports / second-source injuries — gated · 5. Keep PR #3 Draft or split smaller PR · 6. Live 30-min re-score automation (currently manual rerun).

## Hard guardrails
No public operation · no PR ready w/o Owner approval · no merge · no payment · no Token · no betting/odds/盘口/竞猜/投注 ·
no fake probability / archived prediction / SHAP / xG (unless source) / injuries inference · no frontend direct vendor call ·
no token/raw payload commit · vi Han=0 · mm → English. **No hand-written product narrative in templates (LLM generates; mock only as a marked fallback) · no engineering string-concatenated football analysis · no LLM-fabricated facts (source_refs or assumption_flag).**
