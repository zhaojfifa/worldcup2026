# PROJECT_INDEX — worldcup2026 (Giành Cup)

> Top-level navigation for a new engineering thread. **Read `CLAUDE.md` first.** Date: 2026-06-10.
> Status: **MVP-2 Evidence Board v2 Gate Spec Ready** · docs-only closure · runtime unchanged this round.

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
6. `docs/MVP2_SCOUTSCORE_V0_MODEL_CARD.md` · `docs/MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md` ·
   `docs/MVP2_USER_REVIEW_REPORT_855737.md` · `docs/MVP2_NEXT_DATA_REQUIREMENTS.md` ·
   `docs/MVP2_OPERATOR_REAL_DATA_REVIEW.md`

## Runtime entry points
- **Backend (FastAPI):** `backend/app/main.py`
  - `app/services/api_football_client.py` (Level-2 client) · `app/services/scout_pack/*` (contract/builder/features/model_notes/report) · `app/services/scoutscore/*` (factors/accountability/recap_view)
  - `app/routers/internal_scout_pack.py` (`/internal/scout-pack`, internal preview) · `app/routers/recap.py` (`/api/v1/recap/{id}`)
- **Frontend (Vite/React):** `frontend/src/App.tsx` (routes) · `pages/RecapDetailPage.tsx` · `pages/HomePage.tsx` (recap entry + bridge) · `data/recapData.ts` · `styles/global.css`
- **Offline build scripts (no live LLM):** `backend/scripts/mvp2_{ingest_scout_pack,build_productized_report,build_scoutscore}.py`
- **QA screenshot helpers:** `scripts/qa/mvp2_{scout_pack,recap_flow}_shots.mjs`

## Data artifacts (real, redacted)
- `docs/data_audit/mvp2_scout_pack_samples/` (855737/855741/977345/979139)
- `docs/data_audit/mvp2_scoutscore_v0/` · `docs/data_audit/mvp2_prediction_replay/` · `docs/data_audit/mvp2_prediction_accountability_reports/`

## QA screenshots
- `docs/qa_screenshots/mvp2_real_data_operator_review/` (internal preview + productized + accountability, zh/vi)
- `docs/qa_screenshots/mvp2_historical_recap_product_flow/` (home entry/bridge + recap detail/continuation, zh/vi)

## Next decisions (Owner)
1. Approve Evidence Board v2 Gate Spec · 2. Start v2 implementation · 3. Productize 979139 as 2nd recap type ·
4. Verify real DeepSeek/Gemini reasoning · 5. Start TheSports / injuries second-source trial · 6. Keep PR #3 Draft or split smaller PR.

## Hard guardrails
No public operation · no PR ready w/o Owner approval · no merge · no payment · no Token · no betting/odds/盘口/竞猜/投注 ·
no fake probability / archived prediction / SHAP / xG (unless source) / injuries inference · no frontend direct vendor call ·
no token/raw payload commit · vi Han=0 · mm → English.
