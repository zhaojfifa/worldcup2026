# MVP Status — Giành Cup (worldcup2026)

_Last updated: 2026-06-11 · Version: **MVP v0.8 — real data/model/LLM-draft + multilingual operation**_

Status snapshot only — no functional change in this document.
Full handoff: `docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md`.
Language baseline: `docs/MULTILINGUAL_OPERATION_POLICY.md`.

## ★ MVP-2 status (2026-06-11, latest) — June 11 Real Match Trial Prediction Sprint

```text
Persona product trial for the opening window (Owner naming rules applied): 中文先知 / Tiên Tri Bóng Đá
front the football product; engine=ScoutScore; NO Cloud on customer surfaces; <title> -> English.
Pipeline: re-verified fixtures (mvp2_june11_real_fixture_verification.json; 1489369 opener TODAY 19:00
UTC + 1489371) -> trial frames (12 factors, data_status/customer_visible, what_could_flip,
recheck_30min) -> persona narratives 8/8 real LLM + tactical_read (guard extended: Cloud/AI 分析/
thiếu dữ liệu bans + persona enforcement; 6 legacy vi regenerated; 28/28 PASS) -> Home replaced
(status strip + TrialHeroCard + secondary; mock demoted to internal-demo fold; recap kept) ->
/predict/:id persona tactical room (+?ops=1 operator fold) -> 6 screenshots mvp2_june11_trial/ ->
operator package (copy-paste zh/vi messages, link placeholder, checklist, do-not-send) + product review.
vi visible-text Han=0 · build PASS · git diff --check clean · PR #3 Draft · main untouched ·
operation paused — group send ONLY on explicit Owner GO before kickoff.
```

## MVP-2 status (2026-06-11, later) — Real-Match AI Tactical Room (2 real fixtures SHIPPED)

```text
Real-fixture round (WC2026 opening day): /fixtures league=1 season=2026 -> 1489369 Mexico-South Africa
(opener, today) + 1489371 Brazil-Morocco (06-13). Ingest: squads/coach/teams real; lineups/events/stats/
injuries empty pre-match -> missing_evidence. v0.2 prematch_real_frame (fixture_basis=real_scheduled):
Elo 1880v1624 (gap 256, risk high, blind-favourite trap) / 1964v1899 (gap 65, Morocco 10-match unbeaten,
beat Brazil 2023, risk medium). Narratives 8/8 real LLM (0 mock), guard 20/20 PASS (in-loop guard again
intercepted vi handicap slang). Home strip "World Cup 2026 · 真实赛程 AI TACTICAL ROOM" (today/upcoming
chips) -> /predict/:id with real kickoff/venue meta card; existing home logic untouched; build PASS;
0 console errors; 8 screenshots -> docs/qa_screenshots/mvp2_realmatch_tactical_room/.
Send-to-group judgement: READY pending Owner GO — docs/MVP2_REAL_MATCH_TACTICAL_ROOM_REVIEW.md
(operation still paused; nothing posted; payment/Token untouched). PR #3 still Draft.
```

## MVP-2 status (2026-06-11) — LLM-Driven Product Proof Sprint (3 samples SHIPPED)

```text
Sprint:                 MVP-2 LLM-Driven Product Proof (Owner: heavy engineering GO). Engineering = stage;
                        LLM = football intelligence. Fixes the 2026-06-10 "post-match journalism" FAIL via
                        prediction-first prompt v2 + product contract v2 + product guard.
Samples:                A /recap/855737 Argentina 1-2 Saudi Arabia (upset recap)
                        B /recap/979139 Argentina 3-3 France, pens (final recap; 855741 fallback NOT needed)
                        C /predict/2026-brazil-argentina (pre-match 2026 modeling, hypothetical knockout — disclosed)
ScoutScore v0.2:        factor frames (scripts/mvp2_build_scoutscore_v0_2_factors.py): kaggle-derived Elo
                        (K=32,+60 home; 855737 gap 369 / 979139 gap 68 / 2026 ARG 2064 vs BRA 1964) + last-10
                        form + H2H + shootouts + Scout Pack stats/GK/momentum; gaps -> assumption_context.
Narratives:             12/12 REAL LLM (DeepSeek 6 + Gemini 6, zero mock), v2 product contract, GUARD PASS
                        (scripts/check_mvp2_product_narrative_guard.py). Guard caught: vi 盘口黑话 kèo/cửa trên/
                        cửa dưới (5 files), invented t.me URL (1), missing factor provenance (2), AI-filler tone.
Pages:                  /recap/{855737,979139} + /predict/2026-brazil-argentina render the DeepSeek narrative
                        (zh/vi bundled; en/mm deterministic fallback); group/subscribe/today CTA = LLM copy;
                        free-vs-full frame on predict; internal fold = notes/ops-kit/source map/provider.
QA:                     build PASS (tsc+vite); 6 screenshots 390x844 -> docs/qa_screenshots/mvp2_product_proof/;
                        DOM checks: CTA/disclaimer/fold/est-badge present x6; 0 console errors; vi narrative Han=0
                        (pre-existing 22-char shell chrome residual logged, not a sprint surface).
Provider review:        DeepSeek default / Gemini benchmark RE-VALIDATED on 3 samples (provider review 2026-06-11).
Acceptance:             docs/MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md (16/16 self-verify PASS; Owner review pending).
Branch / PR:            feature/mvp2-api-football-ingestion · PR #3 Draft (not ready, not merged) · main untouched.
External operation:     paused · public_ready: false · no payment/Token/TheSports runtime.
```

## MVP-2 status (2026-06-10) — LLM-Guided Product Narrative Refactor (superseded by 2026-06-11 above)

```text
MVP-2 status:           Evidence Board v2 — Product Voice rework done (engineering PASS, copy reworked; internal)
API-FOOTBALL ingestion: PASS (Level-2; 4 fixtures: 855737/855741/977345/979139)
ScoutScore v0.1:        PASS (rule-based factors + historical-replay accountability)
Historical recap flow:  PASS WITH ISSUES, continuation fixed (more-recaps + CTA + home bridge)
Evidence Board v2 design: CLOSED / gate-ready (+ Gate Spec draft)
Evidence Board v2 impl:  /evidence/855737 (zh/vi, vi Han=0), bundled, additive, homepage untouched.
                        Product Voice rework: first screen = the answer (title/subtitle/4 cards/lead; NO MISS /
                        source-required / assumption up top); 3 decisive factors expanded + 3 folded; data gaps ->
                        "下一版需补强的变量"; MISS / AI-boundary / ledger in a collapsed internal block; operator
                        copy de-charged (no 稳赢). Build PASS. Engineering PASS; prior copy FAILED -> reworked.
Recap sync + SPA fix:    Live diag: deploy was CURRENT (Product Voice in live bundle), but /recap main view was never
                        reworked (only /evidence was) + no SPA fallback (deep links 404). Owner 二次 GO -> /recap/855737
                        reworked to Product Voice (answer-led, MISS/replay folded into internal block); render.yaml SPA
                        rewrite added (operator must also set the Render dashboard rewrite rule). Verdict was LIVE FAIL — RECAP NOT UPDATED.
RULE PIVOT:              MVP-2 = LLM-Guided Product Narrative Refactor. Narrative (judgement/recap/operator/zh+vi) must be
                        LLM-generated (DeepSeek/Gemini), NOT hand-written in templates. Engineering = stage; LLM = intelligence;
                        mock only as marked fallback (llm_provider=mock). See MVP2_LLM_NARRATIVE_{ARCHITECTURE,CONTRACT} + prompts.
LLM layer (impl):        scripts/mvp2_generate_scoutscore_narrative.py (REAL DeepSeek + Gemini) + check_mvp2_llm_narrative_guard.py.
                        Narrative JSON -> frontend bundles DeepSeek (default) -> /recap + /evidence main view = LLM narrative
                        (NarrativeView); deterministic fallback for en/mm. Guard PASS (all 4); vi Han=0; build PASS.
                        Provider review: DeepSeek default (punchier), Gemini benchmark. llm_provider shown in internal block.
Owner verdict (closure):  LLM pipeline PASS; current customer-facing narrative FAIL (post-match journalism tone, not a
                        ScoutScore model judgement). NEXT SPRINT = MVP-2 Betting-Logic Model Narrative Prompt Revision
                        (prediction first-principles, NOT gambling): rewrite prompt/contract/guard so output =
                        pre-match judgement -> risk factors -> validation -> what model got right/under-weighted -> next-match watch. Thread closed docs-only.
Branch:                 feature/mvp2-api-football-ingestion
PR #3:                  Draft (base main, not ready, not merged) · PR #2 untouched · main untouched
External operation:     paused · public_ready: false
Next:                   Operator product-voice re-review (does the customer want to continue?); 979139 / live-LLM / TheSports still gated
```

MVP-2 docs: `MVP2_SCOUTSCORE_V0_MODEL_CARD.md` · `MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md` ·
`MVP2_USER_REVIEW_REPORT_855737.md` · `MVP2_EVIDENCE_BOARD_V2_DESIGN.md` ·
`MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md` · `MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2.md` ·
`MVP2_EVIDENCE_BOARD_V2_OPERATOR_REVIEW.md` · `MVP2_PRODUCT_VOICE_GUIDE.md` ·
`MVP2_NEXT_DATA_REQUIREMENTS.md` · `MVP2_OPERATOR_REAL_DATA_REVIEW.md`.
EBv2 impl files: `frontend/src/pages/EvidenceBoardPage.tsx`, `frontend/src/components/{EvidenceBoard,FactorCard,
EvidenceCard,NextVariablesCard,AiBoundaryCard}.tsx`, `frontend/src/data/evidenceData.ts`; QA shots (before + product_voice):
`docs/qa_screenshots/mvp2_evidence_board_v2/`. Full handoff: `HANDOFF_TO_NEXT_ENGINEERING_CHAT.md`.

---

## v0.8 current-state summary (2026-06-08)

- **Historical Recap separation SHIPPED (2026-06-09, frontend-only):** `/matches` mixing fixed without
  backend/API/DB change — `Match.status` carried through transform; Home current surfaces filter
  `status !== 'finished'`; finished WC-2022 matches show only under a labelled **Historical Recap · WC2022**
  surface; Detail/Report show a recap banner when finished. **42.2% not in any customer UI.** vi/mm Han=0,
  zh regression OK, build passes. Evidence: `docs/HISTORICAL_RECAP_MODE_PROPOSAL.md` §9 +
  `docs/qa_screenshots/historical_recap_separation/`. **Verdict PASS (frontend separation).**
  **Operator real-device screenshots can RESUME** (Home un-polluted); **final PASS still pending operator
  review.** Recap-row→detail link = optional polish, not blocking.
- **Fast Real Data Gate RESULT (2026-06-09, operator):** friendlies `10/2026`=0; **WC `1/2026`=0
  (2026 fixtures unavailable from provider)**; **WC `1/2022`=64 fixtures/results/settled** (usable for
  **backtest/recap only**). `hit_rate=42.2%` is a **technical backtest metric — NOT marketed**; 2022 ≠ live.
  `/matches` now mixes historical (id 4–67) + seed (id 1–3) → separation plan
  `docs/HISTORICAL_RECAP_MODE_PROPOSAL.md` (frontend filter by status/date + labelled Recap; **no API/DB
  change**). **Selected matchup mapping stays BLOCKED** (2026 not in system). Plan-only this round.
- **Fast Real Data Gate (2026-06-09):** baseline **tag `v0.8-real-data-gate`** (`d4feb6c`) pushed.
  **Selected matchup mapping intentionally BLOCKED until API sync confirms `match_id`.** Next = operator
  Fast Gate sync (friendlies `10/2026` → WC `1/2026` → `1/2022`) → `/matches` → `refresh`
  (`DATA_SOURCE_SYNC_VERIFICATION.md` §13). No code change.
- **Harness-X Real Match Intelligence Sprint (2026-06-09): real fixtures selected (docs-only).**
  Sourced real matches: **upcoming Mexico v South Africa** (WC opener 06-11); **finished Brazil 2-1 Egypt,
  Argentina 2-0 Honduras** (June friendlies). `api_available=unknown` (`BLOCKED_OPERATOR_RENDER_SHELL` —
  Claude has no token, sync not run/faked); `model_status=pending_api_sync` (no fake numbers); vi copy
  human-authored (no Chinese/betting). Real matches not yet in the app → operator screenshots pending.
  Docs: `REAL_MATCH_INTELLIGENCE_SELECTION.md`, `REAL_MATCH_MODELING_REVIEW.md`, `VI_REAL_MATCH_OPERATION_COPY.md`.
- **Harness-X Vietnam Market Heavy Sprint (2026-06-08): PLAN only, Owner review pending.** 3-role plan
  (Engineering/Product/Operation); **vi first priority**, **warm-ups/friendlies first data priority**
  (`league_id=10,season=2026`); **no backend/API/DB change proposed**; prediction-game/entertainment
  framing, not betting. `docs/HARNESSX_VIETNAM_MARKET_HEAVY_SPRINT_PLAN.md` +
  `docs/VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md` (pending). Not yet implemented.
- **Brand architecture (2026-06-08):** **LEIZE = company brand**; **Giành Cup = product** (under LEIZE
  AI); **"Cloud" = future branch, not the company brand.** No product rename / no code change this round.
  Details: `docs/BRAND_ARCHITECTURE_LEIZE_GIAND_CUP.md`.
- **Real Data Calibration (2026-06-08, Owner GO):** calibrate with real competitions before WC2026.
  `admin/sync/{fixtures,results}` **already accept optional `?league_id=&season=`** → **no code/DB change**;
  first pick **La Liga (140)**, fallback friendlies (10) / WC-2022 (1/2022). Operator-run on Render
  (not fabricated). Runbook: `docs/REAL_DATA_CALIBRATION_PLAN.md`. No scaling/payment/bot; LLM draft-only.
- **Scout Intelligence Rewrite (2026-06-08, frontend-only):** Report/Detail now a data-backed **Giành
  Cup Scout** read — Evidence Strip · Scout verdict + hook · factor Source/Impact/Interpretation ·
  Contrarian · Watch. Derived on frontend (dict + viMapping/mmMapping); **no API/DB change.** vi/mm 0 Han,
  zh regression OK, build passes, no forbidden phrases. Evidence:
  `docs/SCOUT_INTELLIGENCE_REWRITE_EVIDENCE.md` + `docs/qa_screenshots/intelligence_rewrite/`.
  **Engineer self-verify PASS; Stage 5 operator real-device verification PENDING** (checklist in
  evidence doc §4; `operator_verification_status: pending`; shots →
  `docs/qa_screenshots/intelligence_rewrite_operator/`). **Final PASS withheld until operator
  screenshots reviewed + `final_owner_decision` recorded.**


- **Latest commits:** `3343475` (mm recheck screenshots), `3a05ba3` (Telegram fallback + Report
  localization), `822f3ac` (LLM integration policy), `0cd76bd` (draft-only LLM backend).
- **Language QA:** vi PASS · mm PASS (after screenshot-driven recheck). Report-page Chinese residual
  **fixed**; Telegram **open/copy fallback UX** added. Isolation holds (zh/RMB · vi/VND · mm/MMK).
- **vi recheck (2026-06-08, Myanmar standard):** **PASS WITH ISSUES** — full vi path incl. **`/report`**
  re-scanned at 390/430; one Chinese residual (community "VI TRIAL COPY" badge) **fixed** (frontend
  `dict.ts` VI `viBadge` → Vietnamese-only); zh/mm regression clean; build passes; backend untouched.
  See `docs/VI_MOBILE_RECHECK_REPORT.md` + `docs/qa_screenshots/vi_mobile_recheck/`.
- **Interaction-state recheck (2026-06-08):** **PASS WITH ISSUES** — operator-reported **Chinese unlock
  modal** on mm (`Modal.tsx` button + store `res.message` body) **fixed** via i18n keys
  `unlockedBody`/`unlockFailedBody`/`continueToReport` (zh/vi/mm/en); store Chinese neutralized.
  **Modal/toast/action-sheet language QA now mandatory.** mm/vi interaction states screenshot-verified;
  zh + price isolation unaffected; build passes; backend untouched. See
  `docs/LANG_INTERACTION_RECHECK_REPORT.md` + `docs/qa_screenshots/lang_interaction_recheck/`.
- **Social:** Myanmar **Telegram active** (`t.me/GianhCupMMAIFootball`); **Vietnam Zalo pending**.
  **Telegram direct-open may fail in mobile WebViews → Copy Link is the accepted operating path** (PASS WITH ISSUES).
- **Data-source:** `api_football_configured=true`, `connector_status=ok`, **`mock_mode=true`**
  (last known); **real sync pending operator** (Render Shell). No real hit-rate claimable.
- **Modeling:** matches 1/2/3 refresh PASS (win_prob sums 100); baseline usable as **AI viewpoint**,
  not hit-rate proof; shape unchanged.
- **LLM:** **draft-only** admin endpoint (`status=draft_only`, `publishable=false`); forbidden filter
  + local human-template fallback work; **Render real-provider verification pending**
  (`docs/LLM_RENDER_VERIFICATION.md`).
- **LLM draft verification (2026-06-08):** auth gate (401/401), 7 drafts (vi/mm/zh × types) all
  `draft_only`/`publishable=false`/`forbidden_hits=[]`, filter dirty-caught + clean/negation-allowed —
  **locally verified** (`backend/scripts/llm_draft_verify.py`, mock→fallback). Backend harden: vi/mm/en
  drafts now use **English** team names (zh Chinese). **Real DeepSeek/Kimi on Render still operator-pending
  (no token; not fabricated).** Drafts logged pending human review: `docs/LLM_DRAFT_COPY_REVIEW_LOG.md`.
- **Provider comparison + Mini-Agent (2026-06-08):** `provider_override` (deepseek|kimi|gemini, admin/
  draft-only, backward compatible) added. **Real 3-provider comparison** (local keys, pre-existing, never
  committed): **DeepSeek + Gemini clean for vi/mm; Kimi leaks Chinese for vi/mm.** Prompt hardened +
  Gemini `thinkingBudget=0`. **Mini-Agent Harness = lightweight design only** (no runtime). Draft-only;
  no auto-publish/payment/scaling. Docs: `docs/MINI_AGENT_HARNESS_DESIGN.md`,
  `docs/LLM_PROVIDER_COMPARISON_REPORT.md`. **Data-first** Operator Action Checklist added to
  `docs/DATA_SOURCE_SYNC_VERIFICATION.md` (operator runs real sync on Render; not fabricated).
- **Resource:** **no scaling · no payment · no bot auto-publish.**
- **Harness-X:** docs are source of truth; no screenshot = no PASS; high-risk transitions Owner-gated.

---

## Latest state (2026-06-06)

- **main** synced to origin; frontend multilingual operation mode shipped.
- **Vietnamese lightweight UI:** ✅ done (Home/Detail/Token/Community + nav).
- **VND pricing:** ✅ done (139.000₫ / 699.000₫/tháng / 390 MTC).
- **English fallback:** ✅ done — non-Chinese locales fall back to English, never Chinese.
- **Burmese (mm) MVP language mode:** ✅ **ready & acceptance-verified** — core Burmese UI +
  **MM MVP operation test pricing** (12,000 Ks / 59,000 Ks/လ / 390 MTC; matches page exactly);
  unmapped copy & dynamic data → English; **no Chinese residual, no ¥/元/₫** on mm pages.
  Trial URL: `https://worldcup2026-izid.onrender.com/?lang=mm`.
- **Language isolation verified (2026-06-06):** zh→RMB only · vi→VND only (no MMK) · mm→MMK only
  (no ¥/元/₫); CN·VI·MY switch + localStorage persist OK; non-Chinese locales fall back to English.
- **Myanmar density profile (2026-06-06):** mm uses a **separate shorter copy set** + `.lang-mm`
  CSS density profile (root `data-lang`/`lang-mm`). Header/Hero/chips/Signal CTA/risk-note(2-line
  clamp)/bottom-nav verified uncrowded at 375px; CTAs equal height. **zh/vi/en unaffected.**
  Concise English product terms (AI/Risk/Update/MTC) allowed in mm UI.
- **Burmese customer copy coverage (2026-06-06, op-team accepted):** mm upgraded from English
  fallback to **customer-ready Burmese** across Home/Detail/Token/Community + dynamic data
  (team outcomes, AI tendency, risk level/tags, notes, reason bullets, live-correction) via
  `copy/mm.ts` + new `i18n/mmMapping.ts`. Acceptance-verified: **no English-core residual**
  (only allowed AI/MTC/Premium/VIP/team names/numbers); MMK pricing intact; English fallback only
  for unmapped dynamic data; **Chinese never a customer-side fallback.** zh/vi unaffected.
- **Myanmar mobile QA: PASS (2026-06-07)** — `docs/MM_MOBILE_QA_REPORT.md`; screenshots at
  390×844 & 430×932 in `docs/qa_screenshots/mm_mobile/`. Fixed: Today Matches **row overlap**
  (mm two-row `.simrow`), signal CTA shortened, Burmese channel descriptions. Re-verified 2026-06-07.
- **Vietnamese mobile QA: PASS (2026-06-07)** — `docs/VI_MOBILE_QA_REPORT.md`; screenshots in
  `docs/qa_screenshots/vi_mobile/` (4 pages × 390/430). No residual found (vi already customer-ready).
- **Language gate CLOSED. Isolation verified:** zh→Chinese/RMB · vi→Vietnamese/VND · mm→Burmese/MMK;
  vi/mm fall back to English (never Chinese). Screenshot-driven QA mandatory for vi/mm.
  **Next phase:** `docs/NEXT_PHASE_DATA_MODEL_SOCIAL_LLM_PLAN.md` (Data/Modeling/Social/LLM-prep).
- **Harness-X L1 + P-flow Prep (2026-06-08):**
  - Data source: connector `ok`, **`mock_mode=true`**, `requests_used=0`, `performance.total_settled=0`
    (`hit_rate=null`) → **no real hit-rate claimable yet** · `docs/DATA_SOURCE_SYNC_VERIFICATION.md` (PASS WITH ISSUES).
  - Modeling: baseline + `refresh` verified (`win_prob` sums 100, confidence/risk recompute) ·
    `docs/MODELING_BASELINE_VERIFICATION.md` (PASS).
  - Copy library: `docs/OPERATION_COPY_LIBRARY_VI_MM.md`. LLM prep: `docs/LLM_PREP_SCHEMA_AND_GUARDRAILS.md` (design only).
  - **Channels (live-verified): Myanmar Telegram `active` (url set); Vietnam Zalo `coming_soon` (pending).**
  - Admin sync endpoints 401-locked (operator Render-Shell). LLM Full Build Owner-gated.
- **Data+Model Formalization (2026-06-08, Owner-approved L2-lite, no scaling):** matches 1/2/3
  refreshed (win_prob=100; m1 high/61, m2 low/80, m3 low/86; **shape unchanged**); vi/mm/en note
  maps extended for the new low-risk `risk_note`; copy library filled from model output
  (`OPERATION_COPY_LIBRARY_VI_MM.md`); LLM prep deepened (mapping/queue/rollback). **Real
  fixtures/results sync NOT run by Claude** — needs `$ADMIN_API_TOKEN` in Render Shell (operator);
  `mock_mode=true` until then. Myanmar Telegram trial `ready_to_send`; Vietnam Zalo pending.
  No backend/API/DB/scaling change.
- **Real LLM integration — DRAFT-ONLY (2026-06-08, Owner GO WITH CONDITIONS):** added
  `backend/app/services/llm/*` + admin endpoint `POST /api/v1/admin/llm/generate-copy`
  (x-admin-token; `status:draft_only`, `publishable:false`). DeepSeek/Kimi client + forbidden-phrase
  filter (zh/vi/mm/en) + human-template fallback; `AI_PROVIDER=mock` rollback. Verified locally:
  import OK, auth 401/400, filter clean/dirty/negation, vi+mm drafts via fallback. **No auto-publish /
  DB write / payment / scaling / public API-shape change**; `httpx` already present. Real provider call
  pending Render key (currently mock → fallback). Plan: `docs/LLM_REAL_INTEGRATION_PLAN.md`.
- **BLOCKED_STATE_DIVERGENCE recheck (2026-06-08):** operator reported Telegram mobile
  `ERR_CONNECTION_REFUSED` + mm detail Chinese residual. Root cause = the **Report page** was never
  localized (hardcoded zh). Fixed ReportPage + FeatureBars (zh/vi/mm/en) + report trend/tactics/feature
  mappings; added a **Telegram open/copy fallback sheet** (API `public_url`, still tracks click).
  Screenshot-verified at 390/430 (`docs/qa_screenshots/mm_mobile_recheck/`, `docs/MM_MOBILE_QA_REPORT.md`).
  Previous PASS → **PASS WITH ISSUES** (operator to confirm on device post-deploy). zh/vi unaffected;
  build passes; no backend/API/DB/scaling change.
- **UI language buttons:** CN · VI · MY (en = internal fallback layer).
- **Operational blocker:** ⛔ no `active` Zalo/Telegram channel yet → real customer trial
  (vi & mm) cannot dispatch until one is configured via admin upsert.
- **Day 8 LLM Full Build:** deferred (Prep only; behind banned-word filter when started).
- **Next step:** configure an `active` social channel → run Vietnamese/Burmese operation trial.

---

## Brand & positioning

- **Brand:** Giành Cup · 2026 World Cup AI Football Intelligence.
- **User-facing:** Giành Cup · 世界杯 AI 足球情报社区.
- AI 足球情报社区 for the Vietnam-first SEA market. **Not a betting product.**
- **Languages:** zh (internal/default) · en (fallback) · vi (primary customer) ·
  mm (secondary customer). Copy docs: `OPERATION_TRIAL_MESSAGES_VI.md`,
  `MM_OPERATION_TRIAL_MESSAGES.md`.

## Live deployments

| Tier | URL / value |
|------|-------------|
| Frontend (Render) | https://worldcup2026-izid.onrender.com |
| Backend (Render)  | https://worldcup2026-api-71n6.onrender.com |
| Database | Render PostgreSQL |
| R2 bucket | `giand-cup-assets` (R2 ready; `R2_PUBLIC_BASE_URL` unset = acceptable) |
| Repo / branch | github.com/zhaojfifa/worldcup2026 · `main` (origin synced) |

---

## Day 6D Render Verification: **PASS** (2026-06-06)

| Endpoint | Result | Notes |
|----------|--------|-------|
| `GET /api/v1/health` | ✅ OK | `real_money_betting_enabled: false`, `token_withdrawal_enabled: false` |
| `GET /api/v1/assets/status` | ✅ OK | `r2_configured: true`, `public_base_url_set: true`, `message: "R2 ready"` |
| `GET /api/v1/users/1/streak` | ✅ PASS | No longer 404. Empty-safe initial: `current_streak=0`, `best_streak=0`, `mtc_earned=0`, `last_participation_date=null`; disclaimer present. |
| `GET /api/v1/rankings` | ✅ PASS | No longer 404. Initial `top_users=[]`, empty-safe; disclaimer present. |
| `POST /admin/challenges/settle` | ✅ PASS | Succeeded via Render Shell `$ADMIN_API_TOKEN`. See settlement log below. |

**Settlement verification (Render Shell, `$ADMIN_API_TOKEN`):**

- **challenge_id=1** → `ok=true`, `is_correct=true`, `mtc_reward=10`, `current_streak=1`, `best_streak=1`.
  - Re-check `/users/1/streak` → `current_streak=1`, `best_streak=1`, `mtc_earned=10`.
  - Re-check `/rankings` → `#1 Demo Fan`, `current_streak=1`, `best_streak=1`, `mtc_earned=10`.
- **challenge_id=2** → settled again → `current_streak=2`, `best_streak=2`, `mtc_reward=10`.

**Conclusion: Day 6D Render verification PASS.** PR #1 previous blocker resolved.

---

## Completed milestones

- **Day 2** — React/Vite frontend, 5 pages.
- **Day 3** — FastAPI + PostgreSQL + Render deploy + API loop.
- **Day 4** — API-FOOTBALL connector, fixtures sync, baseline predictor, refresh prediction.
- **Day 5** — Operational intelligence home (今日 AI 最强信号 / 简表 / 爆冷风险 TOP3 /
  战绩状态), detail AI 结论卡; frontend ops derive layer.
- **Day 5.5** — Giành Cup branding, 社群矩阵, Content Studio placeholders, data/social design.
- **Day 6A** — `MatchResult`, `PredictionSettlement`, `/admin/sync/results`,
  `/performance/daily`, `/performance/summary`.
- **Day 6B** — R2 (`giand-cup-assets`), `ContentAsset`, `/assets/status`,
  `/admin/assets/upload`, `/assets/{id}`, `/admin/assets/{id}` (boto3 lazy).
- **Day 6C** — `SocialChannel`, `MatchEngagement`, `/social/channels`,
  `/admin/social/channels/upsert`, `/events/track`, `/community/heat`.
- **Day 6D** — `UserStreak`, `ChallengeResult`, `/users/{id}/streak`, `/rankings`,
  `/admin/challenges/settle`; TokenPage fan streak + rankings fallback.
- **Day 7** — Operational Readiness & Public MVP Polish:
  Content Studio shows live R2 storage readiness status (`/assets/status`);
  `docs/OPERATIONS_RUNBOOK.md` (daily ops flow, social channel config via admin API);
  `docs/COMPLIANCE_CHECKLIST.md` (forbidden words, MTC statement, disclaimers, rankings);
  frontend build passes; forbidden-word scan clean; `/matches`+`/reports` shapes unchanged.

Latest commits:
```
b047953 docs: add v0.6D engineering handoff
e7dcad4 feat(frontend): show fan streak and rankings fallback
0c3f730 feat(backend): add streak challenge and rankings
```

---

## ✅ Deployed / done

- Frontend + backend on Render; PostgreSQL live; API loop verified (CORS OK).
- mock ↔ API dual mode (`VITE_USE_MOCK`) verified.
- Day 6A–6D verified online (Day 6D streak/rankings/admin settle PASS — see table above).
- All new capabilities are **additive**: `/matches`, `/matches/{id}`,
  `/reports/{id}` response shapes unchanged across Day 4→6D.
- Brand unified to Giành Cup across header / hero / signal / verdict.

## ✅ Done in Day 7

- Content Studio section in Community page shows live R2 storage readiness via `/assets/status`.
- `docs/OPERATIONS_RUNBOOK.md` — daily prediction flow, social channel config, admin API examples.
- `docs/COMPLIANCE_CHECKLIST.md` — forbidden words, MTC statement, disclaimers, rankings sign-off.
- Frontend build passes; forbidden-word scan clean; API shapes unchanged.

## Not yet done (by design)

- API-FOOTBALL real fixtures/results sync run in production (connector ready;
  graceful mock-mode when key absent).
- `AI_PROVIDER` still `mock` — no LLM wired (planned Day 8, behind banned-word filter).
- `R2_PUBLIC_BASE_URL` not bound → `public_url` returns null (acceptable).
- i18n (Vietnamese-first) not implemented; UI zh-CN only.
- Real Telegram/Zalo bots, share-card image generation, real UGC — not built.

---

## Compliance status

- No forbidden user-facing wording; `提现` only inside `不可提现`.
- MTC = platform loyalty points · 不可提现 · 不可转让 · 不可交易 · 不作为金融资产.
- Rankings is a streak/points board, **not** an earnings board.
- 战绩 / 命中 / 连胜 surfaces carry the mandatory disclaimer.
- No IP / user-agent / personal data captured in event tracking.

## Environment variables (names only; values in Render)

`APP_ENV` · `DATABASE_URL` · `API_FOOTBALL_BASE_URL` · `API_FOOTBALL_KEY` ·
`WC_LEAGUE_ID=1` · `WC_SEASON=2026` · `ADMIN_API_TOKEN` · `AI_PROVIDER=mock` ·
`DEEPSEEK_API_KEY` · `KIMI_API_KEY` · `GEMINI_API_KEY` · `CORS_ORIGINS` ·
`ENABLE_REAL_MONEY_BETTING=false` · `ENABLE_TOKEN_WITHDRAWAL=false` ·
`R2_ACCOUNT_ID` · `R2_ACCESS_KEY_ID` · `R2_SECRET_ACCESS_KEY` ·
`R2_BUCKET=giand-cup-assets` · `R2_PUBLIC_BASE_URL` (empty) ·
`VITE_API_BASE_URL` · `VITE_USE_MOCK`.

> Day 6 added no new backend env vars beyond the existing R2_* (already set).

---

## Day 7 Status (Operational Readiness & Public MVP Polish)

| Task | Status |
|------|--------|
| Day 6D Render online verification (health + assets/status) | ✅ Verified |
| Day 6D streak/rankings/admin settle Render verification | ✅ PASS |
| Content Studio reads `/assets/status` | ✅ Done |
| Operations manual (daily flow, social channel config) | ✅ `docs/OPERATIONS_RUNBOOK.md` |
| Compliance checklist | ✅ `docs/COMPLIANCE_CHECKLIST.md` |
| Vietnamese first-pass key copy | Deferred — out of scope for Day 7 |
| Real API-FOOTBALL sync in prod | Deferred — connector ready, key in Render |
| Configure real Zalo/Telegram links | Deferred — via admin API per runbook |

## Recommended Day 8

- LLM (Kimi/DeepSeek) AI explanation generation — only after banned-word output filter in place.
- Configure real Zalo/Telegram channels via admin API.
- Trigger API-FOOTBALL real sync in production.

**Do not** wire LLM in Day 7. LLM (Kimi/DeepSeek) for AI explanation generation
is Day 8 — and only after a banned-word output filter is in place.
