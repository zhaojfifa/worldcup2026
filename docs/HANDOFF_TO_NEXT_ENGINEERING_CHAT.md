# MVP-2 Next Engineering Thread Handoff

_Read `CLAUDE.md` first, then this. Date: 2026-06-10. Supersedes the prior v0.8 handoff (baseline kept at the bottom)._

## One-line status
MVP-2 reached **Evidence Board v2 Gate Spec Ready** — real API-FOOTBALL Level-2 data → Scout Pack → ScoutScore v0.1 → a customer-readable historical recap wired into the frontend (`/recap/855737`, zh/vi), reviewed PASS WITH ISSUES (gaps fixed); v2 design closed + Gate Spec drafted. **Docs-only this round. No runtime change. PR #3 Draft. Operation paused.**

## Branch / PR truth
```text
Current implementation branch: feature/mvp2-api-football-ingestion
PR #3: Draft, base main, NOT ready, NOT merged
PR #2 (feature/real-data-zh-vi-verification): discovery Draft, untouched
main: untouched
External operation: paused · public_ready: false
```

## Completed capability chain
```text
API-FOOTBALL Level-2 ingestion PASS (server-side client; key server-only)
4 verified fixtures: 855737 / 855741 / 977345 / 979139 (Scout Pack JSON, redacted/bounded)
source_ledger + missing_evidence present; injuries unresolved (source required, never "no injuries")
ScoutScore v0.1: 7-factor rule-based scoring + post-match accountability (historical replay; not_real_archived_prediction=true)
855737 Argentina 1-2 Saudi Arabia productized (feature snapshot -> model notes -> accountability report zh/vi)
Internal operator preview: /internal/scout-pack (accountability-first; raw + ledger collapsed; noindex; admin-gated in prod)
Frontend product flow: Home "Historical Recap · WC2022" -> /recap/855737 (customer-readable, zh/vi, vi Han=0)
Recap continuation: "更多历史复盘" list + continuation CTA + home narrative bridge (no dead-end, no payment)
Backend recap proxy: GET /api/v1/recap/{fixture_id}?lang=zh|vi (en/mm -> 404 -> frontend bundled)
User Review report (4 personas) = PASS WITH ISSUES, accepted; three gaps closed
Evidence Board v2 design CLOSED (gate-ready) + Gate Spec DRAFT
```

## Key files
All paths verified present on this branch (none missing):
```text
CLAUDE.md                                                  [present]
docs/MVP_STATUS.md                                         [present]
docs/MVP2_SCOUTSCORE_V0_MODEL_CARD.md                      [present]
docs/MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md               [present]
docs/MVP2_USER_REVIEW_REPORT_855737.md                     [present]
docs/MVP2_EVIDENCE_BOARD_V2_DESIGN.md                      [present]
docs/MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md             [present]
docs/MVP2_NEXT_DATA_REQUIREMENTS.md                        [present]
docs/MVP2_OPERATOR_REAL_DATA_REVIEW.md                     [present]
docs/data_audit/mvp2_scout_pack_samples/                  [present: 855737/855741/977345/979139.json]
docs/data_audit/mvp2_scoutscore_v0/                       [present: 855737.factor_scores.json]
docs/data_audit/mvp2_prediction_replay/                   [present: 855737.scoutscore_v0.replay.json]
docs/data_audit/mvp2_prediction_accountability_reports/   [present: 855737.{zh-CN,vi-VN}.json]
docs/qa_screenshots/mvp2_historical_recap_product_flow/   [present: home_recap_entry/bridge + recap_855737(+continuation) zh/vi]
```
Runtime entry points (additive this MVP-2): backend `app/services/api_football_client.py`, `app/services/scout_pack/*`,
`app/services/scoutscore/*`, `app/routers/{internal_scout_pack,recap}.py`; frontend `pages/RecapDetailPage.tsx`,
`data/recapData.ts`, recap route in `App.tsx`, Home recap entry/bridge in `pages/HomePage.tsx`.
Build scripts (offline, no live LLM): `backend/scripts/mvp2_{ingest_scout_pack,build_productized_report,build_scoutscore}.py`.

## Current product judgment
The product is **not** neutral data display — it is a **prediction-accountability** loop: AI pre-match view →
result → hit/miss → factor validation → model correction → operator recap. The 855737 upset (dominant side lost)
is the lead sample: the model honestly shows a **MISS** and what it must up-weight (efficiency / goalkeeper /
event momentum) + what to ingest next (injuries P0, xG P1, Elo/form P1). User Review: operator-PASS,
fan/pre-paid/flow PASS-WITH-ISSUES (now fixed). Concept validated → recommend Evidence Board v2.

## Evidence Board v2 gate status
- **Design CLOSED / gate-ready:** `docs/MVP2_EVIDENCE_BOARD_V2_DESIGN.md` (goals, core pages, IA, data contract, guardrails, v2-not-doing, Owner Q&A answers).
- **Gate Spec DRAFT:** `docs/MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md` (allowed/forbidden paths, UI zones, data sources, API contracts, i18n, screenshot reqs, acceptance criteria, rollback, **Owner GO required**).
- **Not approved for implementation.** No runtime built from the Gate Spec yet.

## Next Owner decisions
```text
1. Approve Evidence Board v2 Gate Spec?
2. Start Evidence Board v2 implementation?
3. Productize 979139 Argentina vs France as a second recap type?
4. Verify real DeepSeek / Gemini reasoning (currently template/mock fallback, draft-only)?
5. Start TheSports trial / injuries second-source verification (P0 data gap)?
6. Keep PR #3 Draft, or split a smaller PR?
```

## Hard guardrails
```text
No public operation · No PR ready without Owner approval · No merge
No payment · No Token · No second-source injuries integration yet
No betting / odds / 盘口 / 竞猜 / 投注 · No fake probability · No fake archived prediction
No SHAP · No xG unless source exists · No injuries inference
No frontend direct vendor call · No token / raw payload commit · vi Han=0 · mm -> English (never Chinese)
```

## Carry-forward baseline (v0.8, still valid)
- **Live URLs:** frontend https://worldcup2026-izid.onrender.com · backend https://worldcup2026-api-71n6.onrender.com
- **Secrets live on Render** (`API_FOOTBALL_KEY`, `ADMIN_API_TOKEN`, `DEEPSEEK/KIMI/GEMINI`, R2_*). Local dev: `backend/.env` holds a working **API-FOOTBALL Pro** key (real ingestion runs locally); to run the full backend under local Python 3.9, `pip install --user eval_type_backport`.
- **Dual mode:** `VITE_USE_MOCK=true` for local frontend screenshots (recap uses bundled `recapData.ts`); never break it.
- **Never change** `/matches`, `/matches/{id}`, `/reports/{id}` response shapes; new capability → new endpoint.
- **Language:** vi primary · mm secondary · zh internal · en system/fallback. vi/mm never fall back to Chinese.
- **git committer is machine-inferred** (user.name/email unset); do NOT amend/force-push.
- Prior v0.8 detail (social/LLM/QA lessons) is in git history of this file and in `docs/` (MM/VI QA reports, LLM_* docs).

## Recommended first command for next Claude thread
```text
Owner has accepted the MVP-2 design-closure handoff. Start by reading CLAUDE.md, docs/MVP_STATUS.md, docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md, docs/MVP2_EVIDENCE_BOARD_V2_DESIGN.md, and docs/MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md.

Do not implement immediately.

First verify:
- PR #3 remains Draft
- branch is feature/mvp2-api-football-ingestion
- external operation remains paused
- Evidence Board v2 Gate Spec is complete

Then ask Owner to choose one path:
A. Start Evidence Board v2 implementation
B. Productize 979139 as second recap sample
C. Verify real DeepSeek / Gemini reasoning
D. Start TheSports / injuries second-source trial
E. Keep PR #3 Draft and split smaller PR
```
