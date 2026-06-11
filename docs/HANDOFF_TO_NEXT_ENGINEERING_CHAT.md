# MVP-2 Next Engineering Thread Handoff

_Read `CLAUDE.md` first, then this. Date: 2026-06-11. Supersedes the prior v0.8 handoff (baseline kept at the bottom)._

## ★ 2026-06-11 (latest) — June 11 Real Match Trial Prediction Sprint: SHIPPED (Owner trial-send review)

QiuGe sprint (same day, Owner Brand+HotReads+ReScore): zh persona -> 俅哥说球 (俅哥战术室/俅哥今日看点/
俅哥判断/俅哥临场30分钟修正; hero+nav+status+labels swapped; 中文先知 0 residue; vi keeps Tiên Tri temp;
ScoutScore stays engine). zh trial narratives regenerated as 俅哥 (guard enforces 俅哥 for zh trial; new
bans 数据缺失/模型自证; tactical_read must be a plain string). NEW 30-Min ReScore layer:
scripts/mvp2_generate_rescore_models.py -> mvp2_rescore_models/{id}.{lang}.json (6 required triggers w/
free/subscriber copy + >=3 decision rules + public_teaser + group_join_hook + reminder_message; 4/4
guard_clean) -> /predict/:id 俅哥临场30分钟修正 block (free 3 triggers + group tier + rules + CTA
加入赛前情报群，等俅哥临场修正; #rescore anchor). Hot reads rebuilt: ONLY current hooks (2 rooms +
rescore teaser -> /predict/1489369#rescore + group hook -> /community); recap stays bottom calibration.
Operator package §6b = 俅哥 final send kit (group msg/social/screenshot rec/30min reminder/kickoff rule).
Guard 36/36 + rescore 4/4; build PASS; vi Han=0.

Shell v2 (same day, Owner Trial Homepage+Detail sprint): home hierarchy v2 (persona hero line, 今日
status, 中文先知今日热点 = 4 LLM short_title entries, legacy mock/heat/record/MTC tiles all folded);
CTA deep routes (查看中文先知判断 -> /predict/1489369, 临场修正逻辑 anchor; nav AI预测 -> 中文先知);
/detail -> TrialDetailGate redirect to the tactical room (Qatar vs Ecuador OUT of trial flow, ?demo=1
internal escape); predict = top-3 variables + more-fold + free-vs-full tier card. Path review:
docs/MVP2_TRIAL_PRODUCT_PATH_REVIEW.md. Guard 36/36 PASS; build PASS; vi visible Han=0.

```text
What changed on top of the tactical-room round:
PERSONA: 中文先知 (zh) / Tiên Tri Bóng Đá (vi) now front all football product surfaces (labels, CTAs,
  narrative voice — guard-enforced); brand hierarchy LEIZE > LEIZE AI > Giành Cup > persona > ScoutScore
  (engine); NO Cloud on football surfaces; customer <title> switched to the English brand line.
TRIAL PIPELINE (new scripts): mvp2_verify_june11_fixtures.py (fixture truth JSON) ·
  mvp2_build_trial_prediction_frame.py (12-factor frames, customer_visible/data_status per factor,
  what_could_flip, recheck_30min) · mvp2_generate_trial_prediction_narratives.py (persona prompts via
  addenda in docs/prompts/, required tactical_read, full guard in retry loop) -> 8/8 real LLM PASS;
  guard new bans: cloud / ai 分析 / 我们没有数据 / thiếu dữ liệu / 缺数据 + persona presence; 6 legacy
  vi narratives regenerated to the same bar (28/28 PASS).
FRONTEND: Home = TrialStatusStrip + TrialHeroCard(1489369) + secondary strip + recap; legacy mock
  signal/list/upsets DEMOTED into <details class=home-demo-fold>; PredictPage persona bars + tactical
  card + ?ops=1 opens InternalFold (operator screenshots).
OPERATOR: MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md = copy-paste zh/vi group messages ([群链接由运营填写]),
  send checklist, do-not-send (kickoff expiry!), Owner-GO gate. Review: MVP2_JUNE11_TRIAL_PRODUCT_REVIEW.md.
TIME-SENSITIVE: opener kicks off 2026-06-11 19:00 UTC — trial send must happen BEFORE kickoff or fall
  back to the 06-13 Brazil-Morocco warm-up message. 30-min re-score is a MANUAL pipeline rerun this
  round (automation = Owner decision). Operation paused; nothing sent.
```

## ★ 2026-06-11 (later) — Real-Match AI Tactical Room: SHIPPED, send-READY (Owner GO pending)

WC2026 opened today; the proof pipeline now runs on REAL upcoming fixtures end-to-end:
home strip → real fixture → API-FOOTBALL ingest → v0.2 `prematch_real_frame` (`fixture_basis=
real_scheduled`) → DeepSeek/Gemini tactical room → ops preview → screenshots → send-readiness verdict.

```text
Fixtures: 1489369 Mexico-South Africa (opener, Estadio Azteca, 2026-06-11 19:00 UTC) · 1489371 Brazil-
          Morocco (06-13 MetLife). Real: squads(26)/coach/kickoff/venue + Kaggle Elo/form/H2H/pens
          (Morocco 7W-3D-0L, beat Brazil 2023). Pre-match unknowns (XI/GK/injuries/xG) = assumption_context
          + live-30min triggers; guard real_scheduled branch forces "lineups pending" internal disclosure.
Output:   8/8 narratives real LLM (0 mock); guard 20/20; home strip (today/upcoming chips, zero changes to
          existing home sections); /predict/{id} real-meta card; 8 screenshots; 0 console errors.
Ops:      zh/vi group copy + social posts + join/today CTAs all LLM-written (no URLs in prose — links are
          page/context-injected). Send judgement: READY pending Owner GO; OPERATION STILL PAUSED — nothing
          was posted. Review: docs/MVP2_REAL_MATCH_TACTICAL_ROOM_REVIEW.md.
Watch:    opener kicks off today — pre-match send window closes at kickoff (then it becomes recap material);
          1489371 internal_notes echo an English engineering instruction (internal fold only, cosmetic);
          subscription layer remains CTA-only (no payment/Token).
```

## ★ 2026-06-11 — LLM-Driven Product Proof Sprint: SHIPPED (Owner review pending)

The 2026-06-10 next-sprint (betting-logic prompt revision) was executed as the **LLM-Driven Product
Proof Sprint** and is complete on `feature/mvp2-api-football-ingestion` (PR #3 **still Draft**):

```text
3 product samples LIVE (dev):  /recap/855737 (upset) · /recap/979139 (final, pens) · /predict/2026-brazil-argentina
Pipeline: ScoutScore v0.2 factor frames (kaggle-derived Elo + last-10 + H2H + Scout Pack stats; gaps =
          flagged assumption_context) -> v2 product contract -> DeepSeek/Gemini -> product guard -> pages.
Narratives: 12/12 real LLM (zero mock), GUARD PASS. DeepSeek default on pages; Gemini benchmark in docs.
New scripts: mvp2_build_scoutscore_v0_2_factors.py · mvp2_generate_product_proof_narratives.py (full guard
          in retry loop) · check_mvp2_product_narrative_guard.py.
New docs: MVP2_LLM_DRIVEN_PRODUCT_PROOF_PLAN.md · MVP2_SCOUTSCORE_V0_2_MODELING_FRAME.md ·
          MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md (16-item acceptance) · prompts/mvp2_scoutscore_product_narrative_{zh,vi}.md;
          contract + provider review updated (v2 section; DeepSeek default re-validated).
QA: build PASS · 6 screenshots in docs/qa_screenshots/mvp2_product_proof/ · 0 console errors · vi narrative Han=0.
Guard lessons (now codified): both providers wrote vi betting slang (kèo/cửa trên/cửa dưới) and one invented
          t.me link -> banned in guard; links are page-injected only. DeepSeek vi needs max_tokens>=4500.
Next:     (1) Owner reviews MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md + screenshots -> final PASS decision;
          (2) optional polish: evidence pages for 979139/2026, recap<->home bridge for 979139/predict,
              main_lean/risk_level consistency constraint in prompt;
          (3) pre-existing items unchanged: Render dashboard SPA rewrite (deep links in prod), internal-preview
              shell vi chrome residual (22 Han chars, layout backlog), TheSports/payment still gated.
Rules unchanged: PR #3 Draft · no merge · operation paused · no payment/Token/TheSports · LLM never hand-replaced.
```

## One-line status (2026-06-10, superseded above)
MVP-2 = **LLM-Guided Product Narrative Refactor** (rule pivot, 2026-06-10). **New hard rule: the product narrative — model judgement, recap, operator copy, zh+vi — must be GENERATED BY THE LLM (DeepSeek/Gemini), NOT hand-written in frontend/backend templates. Engineering builds the stage; the LLM writes the football intelligence.** Engineering owns data / Scout Pack / source_ledger / missing_evidence / feature-extraction / prompt-contract / LLM-input-JSON / output-schema / guards / cache / rendering; the LLM owns multi-factor reasoning / narrative / customer judgement / recap / operator copy / zh+vi. The prior hand-written `/evidence` + `/recap` product voice is now the **stage** to be filled by LLM narrative JSON; mock allowed ONLY as a marked fallback (`llm_provider=mock`). Docs: `MVP2_LLM_NARRATIVE_ARCHITECTURE.md`, `MVP2_LLM_NARRATIVE_CONTRACT.md`, `docs/prompts/mvp2_scoutscore_narrative_{zh,vi}.md`, `MVP2_LLM_NARRATIVE_PROVIDER_REVIEW.md`. _(Prior state: EBv2 minimal impl + product-voice rework + /recap sync + render.yaml SPA fallback — all shipped to PR #3 Draft; operator must still set the Render dashboard rewrite + verify live.)_ **PR #3 Draft. Operation paused. public_ready=false. No merge.** · **Owner verdict (2026-06-10):** LLM pipeline **PASS** (contract / generator / guard / DeepSeek+Gemini), but the **current customer-facing narrative FAILS the product angle** — it reads like post-match journalism, not a Giành Cup AI ScoutScore model judgement. **Next sprint = MVP-2 Betting-Logic Model Narrative Prompt Revision** (prediction first-principles: pre-match judgement → risk factors → actual result → factor validation → what the model got right / under-weighted → what to watch next; **NOT betting/odds/盘口/竞猜/投注**). See "★ Current Owner verdict + next sprint" below.

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
Evidence Board v2 MINIMAL IMPLEMENTATION (Owner GO Path A): additive /evidence/855737 (zh/vi); factor + evidence + missing-data + AI-boundary cards; tier+stars (no %); recap entry link; build PASS; review PASS WITH ISSUES (internal); bundled-only; operator real-device review pending
Product Voice rework of /evidence + /recap sync + render.yaml SPA fallback (operator must add Render dashboard rewrite + redeploy; deep links currently 404)
LLM-Guided Narrative layer: MVP2_LLM_NARRATIVE_{ARCHITECTURE,CONTRACT} + zh/vi prompts + scripts/mvp2_generate_scoutscore_narrative.py + scripts/check_mvp2_llm_narrative_guard.py
REAL DeepSeek + Gemini narratives for 855737 zh/vi; guard FAILED raw output (factor-key leak / schema drift / missing fields) then PASSED after prompt+input tightening; provider review = DeepSeek default, Gemini benchmark
/recap + /evidence main view now render the LLM narrative (NarrativeView) with deterministic fallback (en/mm); llm_provider shown in the internal block
```

## ★ Current Owner verdict + next sprint (2026-06-10)
**LLM Narrative Layer: PASS** · **DeepSeek / Gemini integration: PASS** · **Guard pipeline: PASS** ·
**Current customer-facing narrative: FAIL (product angle).**

Why FAIL: the real LLM output reads like **post-match journalism / a media article / a result explainer**. The
product needs the **Giành Cup AI ScoutScore model read** on prediction first-principles:
`pre-match judgement → risk factors → actual result → factor validation → what the model got right → what it
under-weighted → what the user should watch next`. (This is the "betting-logic" first-principle of a *prediction*
product — **NOT** betting / odds / 盘口 / 竞猜 / 投注 / 赔率.)

### Next sprint = MVP-2 Betting-Logic Model Narrative Prompt Revision (prompt + contract + guard only; no new runtime path)
Rewrite the LLM **prompt + contract + guard** so DeepSeek/Gemini output the ScoutScore model judgement, not news.
- **A. Prompt** — add hard constraints: "You are not a football journalist. You are not writing a post-match
  article. You are the reasoning layer of Giành Cup AI ScoutScore. Explain the model judgement, risk factors,
  validation, and next-match watch signals."
- **B. Output must answer:** (1) ScoutScore pre-match main judgement? (2) based on which factors? (3) did it flag
  upset risk? (4) which risk factors were validated post-match? (5) which factors show the model has value?
  (6) which were under-weighted? (7) what should the user watch next match? (8) why is this better than generic AI copy?
- **C. hero_title** must include **"Giành Cup AI"** or **"ScoutScore"**; **ban journalism-style titles** (e.g.
  "Argentina 1-2 Saudi Arabia: Khi kẻ yếu hóa người hùng"); recommended e.g. "Giành Cup AI ScoutScore：这场爆冷验证了 3 个冷门信号".
- **D. customer_takeaway** must be **user-facing** (what to watch next match), NOT model-optimization
  ("用于校准下一版模型" ❌ → "下次强队明显占优时，别只看控球率和名气，重点看门将状态、射门转化率、下半场动量" ✅).
- **E. Guard additions:** hero_title must include Giành Cup AI/ScoutScore · model_judgement must state a pre-match
  judgement · output must include risk factors + validated factors + next-match watch signals · customer_takeaway
  user-facing (not internal model-optimization) · no journalism-only title · no generic post-match article tone.

Current LLM narratives to revise: `docs/data_audit/mvp2_llm_narratives/855737.{zh-CN,vi-VN}.{deepseek,gemini}.json`.
Touch only: `docs/prompts/mvp2_scoutscore_narrative_{zh,vi}.md`, `MVP2_LLM_NARRATIVE_CONTRACT.md`,
`scripts/check_mvp2_llm_narrative_guard.py`, then regenerate + re-guard + re-screenshot. **No new runtime path; PR #3 stays Draft.**

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
**EBv2 (additive, 2026-06-10):** frontend `pages/EvidenceBoardPage.tsx`, `components/{EvidenceBoard,FactorCard,EvidenceCard,MissingDataCard,AiBoundaryCard}.tsx`,
`data/evidenceData.ts`, `/evidence/:fixtureId` route + recap entry link in `App.tsx`/`RecapDetailPage.tsx`, `.eb-*`/`.factor-*` CSS in `styles/global.css`;
QA shots `docs/qa_screenshots/mvp2_evidence_board_v2/`; QA driver `scripts/qa/mvp2_evidence_board_shots.mjs`. No backend change this cut.
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
- **Implemented (minimal, internal) — 2026-06-10:** Owner GO (Path A) → additive `/evidence/855737` built per the Gate Spec. Acceptance criteria met (build PASS, vi Han=0, every conclusion has `source_refs` or an `assumption` flag, additive-only diff, no vendor ref, no %/SHAP/xG/injury-inference). Review **PASS WITH ISSUES** (internal) — `docs/MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2.md`. **Operator real-device review + commit-to-Draft = Owner-pending. Bundled-only; backend `GET /api/v1/evidence/{id}` NOT built this cut (forward-compatible).**

## Next Owner decisions
```text
1. Run the next sprint — MVP-2 Betting-Logic Model Narrative Prompt Revision (rewrite prompt/contract/guard so LLM output is a ScoutScore model judgement, not journalism).
2. Confirm DeepSeek stays the default narrative provider (vs Gemini benchmark).
3. Operator: set the Render dashboard SPA rewrite (/* -> /index.html) + redeploy, then verify /recap + /evidence live (deep links currently 404).
4. Productize 979139 as a second sample — only if Owner asks.
5. Start TheSports / second-source injuries — still gated.
6. Keep PR #3 Draft, or split a smaller PR?
```

## Hard guardrails
```text
No public operation · No PR ready without Owner approval · No merge
No payment · No Token · No second-source injuries integration yet
No betting / odds / 盘口 / 竞猜 / 投注 · No fake probability · No fake archived prediction
No SHAP · No xG unless source exists · No injuries inference
No frontend direct vendor call · No token / raw payload commit · vi Han=0 · mm -> English (never Chinese)
No hand-written product narrative in templates (LLM generates; mock only as a marked fallback, llm_provider=mock)
No engineering string-concatenated football analysis · No LLM-fabricated facts (source_refs or assumption_flag per conclusion)
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
Owner has accepted the LLM-guided narrative handoff. Start by reading CLAUDE.md, docs/MVP_STATUS.md, docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md, docs/MVP2_LLM_NARRATIVE_ARCHITECTURE.md, docs/MVP2_LLM_NARRATIVE_CONTRACT.md, and docs/MVP2_LLM_NARRATIVE_PROVIDER_REVIEW.md (plus docs/prompts/mvp2_scoutscore_narrative_{zh,vi}.md and docs/data_audit/mvp2_llm_narratives/).

Do not implement immediately.

First verify:
- PR #3 remains Draft; branch feature/mvp2-api-football-ingestion
- external operation remains paused; public_ready=false
- LLM narrative artifacts exist (855737 zh/vi, deepseek+gemini)
- DeepSeek/Gemini outputs passed the guard
- current Owner verdict: LLM pipeline PASS, narrative product angle FAIL

Then prepare the next sprint:
MVP-2 Betting-Logic Model Narrative Prompt Revision
(prediction first-principles — pre-match judgement -> risk factors -> actual result -> factor validation -> what the model got right / under-weighted -> what to watch next; NOT betting/odds/盘口/竞猜/投注).
Rewrite only prompt + contract + guard; regenerate + re-guard. PR #3 stays Draft; no merge; no public operation.
```
