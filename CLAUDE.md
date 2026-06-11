# CLAUDE.md — worldcup2026 Engineering Entry Point

> **Read this file first** at the start of every Claude engineering session for
> this project, before executing any task. It is the source of truth for
> identity, baseline, rules, and guardrails.

---

## ★ Current Project State / Handoff (read this first)

> Full handoff for a new chat: **`docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md`** (read after this).
> Engineering status snapshot: **`docs/MVP_STATUS.md`** (v0.8).

## Current Project Status — MVP-2 LLM-Guided Product Narrative Refactor

**★ 2026-06-11 (latest) — June 11 Real Match Trial Prediction Sprint SHIPPED (Owner trial-send review pending)**
```text
Small-Scale Trial Readiness (same day, Owner verdict: PASS WITH CONDITIONS for small private trial):
customer path fully de-AI'd (ticker/caps/lean/header-sub/cta/community labels -> 俅哥情报/俅哥赛前判断/
俅哥倾向/俅哥判断; AI kept only in footer disclaimer, EN brand line, internal folds); predict labels per
Owner C (风险等级/免费版 vs 群内完整版/PRE-MATCH READ); rescore block = trial core (现在俅哥怎么看/
哪三个变量会改判断/开球前30分钟会重算什么 + group 5-question checklist); package adds §12 small-scale
rules + §13 feedback checklist. SMALL-SCALE PRIVATE TRIAL AUTHORIZED (internal ops / few trusted fans /
1 test group; before kickoff only); public operation still paused.

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

Heavy trial for the June-11 opening window. Personas now front the football product: zh 中文先知 ·
vi Tiên Tri Bóng Đá (company LEIZE / product Giành Cup / engine ScoutScore; NO Cloud on football
surfaces — customer <title> de-sinified to the English brand line; legal names docs-only).
Fixture truth re-verified from API-FOOTBALL (league=1 season=2026, 72 fixtures) ->
docs/data_audit/mvp2_june11_real_fixture_verification.json: 1489369 Mexico-South Africa (opener,
19:00 UTC TODAY, Azteca) + 1489371 Brazil-Morocco (06-13). Trial frames (12 factors with
data_status/customer_visible/internal_note + what_could_flip + recheck_30min) ->
mvp2_trial_prediction_frames/. Persona narratives 8/8 real LLM (DeepSeek chosen, Gemini benchmark),
new required tactical_read, guard extended (Cloud / AI 分析 / 缺数据-thiếu dữ liệu bans + persona
checks); 6 legacy vi narratives regenerated to the same bar -> all 28 GUARD PASS.
Home rebuilt per Owner hierarchy: persona status strip -> TrialHeroCard (opener + LLM hook + 进入
中文先知战术室 / 加入赛前情报群) -> secondary fixture -> recap visible -> OLD MOCK DEMOTED into a
collapsed internal-demo fold. /predict/:id = persona tactical room + tactical_read card + ?ops=1
operator fold. 6 screenshots docs/qa_screenshots/mvp2_june11_trial/. Operator package
docs/MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md (copy-paste zh/vi group messages, [群链接由运营填写],
send checklist, do-not-send incl. kickoff-window expiry) + review docs/MVP2_JUNE11_TRIAL_PRODUCT_REVIEW.md.
vi visible-text Han=0; build PASS; PR #3 Draft; main untouched; OPERATION STILL PAUSED — any send
requires explicit Owner GO before 19:00 UTC kickoff.
```

**★ 2026-06-11 (later) — Real-Match AI Tactical Room round SHIPPED (send-to-group READY, Owner GO pending)**
```text
Pipeline extended to REAL upcoming fixtures on WC2026 opening day: API-FOOTBALL /fixtures (league=1,
season=2026) -> picked 1489369 Mexico-South Africa (opener, Estadio Azteca, TODAY) + 1489371
Brazil-Morocco (06-13) -> Level-2 ingest (squads/coach real; lineups/stats/injuries pre-match empty ->
missing_evidence, never faked) -> ScoutScore v0.2 prematch_real_frame (fixture_basis=real_scheduled;
Elo gap 256 / 65, Morocco 7W-3D-0L unbeaten, Morocco beat Brazil 2023 — all real Kaggle data) ->
DeepSeek/Gemini tactical-room narratives (8/8 real, 0 mock; in-loop guard again caught vi cửa trên) ->
Home "World Cup 2026 · 真实赛程 AI TACTICAL ROOM" strip (today/upcoming chips -> /predict/:id; existing
home sections untouched) -> /predict/{1489369,1489371} (real kickoff/venue meta card + LLM narrative)
-> screenshots docs/qa_screenshots/mvp2_realmatch_tactical_room/ -> send-readiness review
docs/MVP2_REAL_MATCH_TACTICAL_ROOM_REVIEW.md: READY TO SEND pending Owner GO (operation still paused,
nothing posted). Guard total 20/20 PASS. Frontend still never calls vendor/LLM (bundled).
```

**★ 2026-06-11 — LLM-Driven Product Proof Sprint SHIPPED (Owner review pending)**
```text
The 2026-06-10 next-sprint was executed as the LLM-Driven Product Proof Sprint. 3 product samples live
on this branch: /recap/855737 (upset recap) · /recap/979139 (Argentina 3-3 France final recap) ·
/predict/2026-brazil-argentina (pre-match 2026 modeling; hypothetical knockout, disclosed).
Pipeline: ScoutScore v0.2 factor frames (kaggle-derived Elo + last-10 form + H2H + Scout Pack; gaps =
flagged assumption_context, never dressed as fact) -> v2 product contract -> DeepSeek/Gemini ->
product guard -> pages. 12/12 narratives real LLM (zero mock), GUARD PASS; DeepSeek default on pages
(re-validated), Gemini benchmark. Guard now also bans vi 盘口黑话 (kèo/cửa trên/cửa dưới) and URLs in
customer prose (both providers tried both — guard is a mandatory layer).
Scripts: mvp2_build_scoutscore_v0_2_factors.py · mvp2_generate_product_proof_narratives.py ·
check_mvp2_product_narrative_guard.py. Acceptance: docs/MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md
(16/16 self-verify PASS; final PASS = Owner review). Screenshots: docs/qa_screenshots/mvp2_product_proof/.
PR #3 still Draft · no merge · operation still paused · no payment/Token/TheSports runtime.
```

**Current phase**
```text
MVP-2 = LLM-Guided Product Narrative Refactor.
Rule pivot: the product narrative (model judgement / recap / operator copy / zh+vi) must be GENERATED BY THE LLM
(DeepSeek/Gemini), NOT hand-written in frontend/backend templates. Engineering builds the stage; the LLM writes
the football intelligence. The prior hand-written product voice (/evidence, /recap) is the stage to be filled by
LLM narrative JSON. mock allowed ONLY as fallback, marked llm_provider=mock.
Owner verdict (2026-06-10): LLM pipeline PASS (contract/generator/guard/DeepSeek+Gemini); current customer-facing
narrative FAIL (reads like post-match journalism, not a ScoutScore model judgement).
NEXT SPRINT = MVP-2 Betting-Logic Model Narrative Prompt Revision (prediction first-principles, NOT gambling/odds/
盘口/竞猜/投注): rewrite prompt + contract + guard so output = pre-match judgement -> risk factors -> actual result
-> factor validation -> what the model got right / under-weighted -> what the user watches next.
[EXECUTED 2026-06-11 as the LLM-Driven Product Proof Sprint — see ★ block above; Owner review pending.]
```

**★ LLM-Guided Narrative — hard rules (non-negotiable this phase)**
```text
Engineering builds the stage. The LLM writes the football intelligence.

Do NOT hand-write product narrative in frontend/backend templates.
Do NOT compose football analysis by engineering string concatenation.
Engineering may define schema, prompts, guards, and rendering only.
DeepSeek/Gemini must generate the narrative / model explanation / operator copy / zh+vi expression.
If the LLM is unavailable, use mock ONLY as fallback and mark llm_provider=mock.

产品规定流程、结构和边界；建模、内容组织和表达必须由大模型完成。
工程不能替代大模型写分析。工程只能组织输入、调用模型、校验输出、渲染结果。

Engineering owns: real data ingestion · Scout Pack · source_ledger · missing_evidence · feature extraction ·
  prompt contract · LLM input JSON · LLM output schema · guard checks · cache/fallback · page rendering.
LLM owns: multi-factor reasoning · football narrative · customer judgement · post-match recap · operator copy ·
  zh/vi expression · reasonable default context · self-consistent explanation · multimodal-ready expression.
Refs: docs/MVP2_LLM_NARRATIVE_ARCHITECTURE.md · docs/MVP2_LLM_NARRATIVE_CONTRACT.md ·
  docs/prompts/mvp2_scoutscore_narrative_{zh,vi}.md · docs/MVP2_LLM_NARRATIVE_PROVIDER_REVIEW.md
```

**Branch / PR truth**
```text
Current implementation branch: feature/mvp2-api-football-ingestion
PR #3: Draft, base main, not ready, not merged
PR #2: discovery Draft, untouched
main: untouched
External operation: paused
Public ready: false
```

**Completed chain**
```text
API-FOOTBALL Level-2 ingestion PASS
4 verified fixtures loaded (855737, 855741, 977345, 979139)
Scout Pack JSON generated (redacted/bounded)
source_ledger / missing_evidence present
ScoutScore v0.1 created (rule-based factors + LLM-ready reasoning, historical replay)
855737 Argentina 1-2 Saudi Arabia productized as historical replay
Homepage historical recap flow connected
/recap/855737 detail page created
zh / vi support (vi Han = 0)
User Reviewer report completed (PASS WITH ISSUES, accepted)
Continuation CTA added
More recap placeholders added
Homepage recap narrative bridge added
Evidence Board v2 design closed (gate-ready)
Gate Spec draft created
Evidence Board v2 minimal implementation built (Owner GO Path A, 2026-06-10): additive /evidence/855737 zh/vi —
AI-lean + tier(★,no %) + 7 factor cards + 5 evidence cards + missing-data + AI-boundary; ledger/raw collapsed;
recap entry link; homepage untouched; build PASS; vi Han=0; review PASS WITH ISSUES (internal); operator review pending
Evidence Board v2 reworked to CUSTOMER PRODUCT VOICE (2026-06-10): first screen = the answer (title/subtitle/4 cards/
lead); 3 decisive factors expanded + rest folded; data gaps -> "下一版需补强的变量"; MISS/boundary/ledger in collapsed
internal block; operator copy de-charged; build PASS; vi Han=0; engineering PASS / prior copy FAIL -> reworked; operator product-voice re-review pending
Live deploy diagnostic (2026-06-10): live bundle WAS current (Product Voice present) but /recap main view was never reworked
(only /evidence) + no SPA fallback (deep links 404). Verdict LIVE FAIL — RECAP NOT UPDATED. Owner 二次 GO -> /recap/855737
synced to Product Voice (answer-led, MISS/replay folded); render.yaml SPA rewrite added (operator must also set Render dashboard rewrite). Frontend + render.yaml only.
RULE PIVOT (2026-06-10): MVP-2 LLM-Guided Product Narrative Refactor — narrative must be LLM-generated (DeepSeek/Gemini),
NOT hand-written in templates. Engineering = stage (data/schema/prompts/guards/rendering); LLM = football intelligence.
Prior hand-written /evidence + /recap voice becomes the stage to be filled by LLM narrative JSON.
```

**Core product logic**
```text
Home prediction -> historical recap -> prediction accountability -> model correction -> user trust -> Evidence Board v2
```

**Current guardrails**
```text
No public operation
No PR ready without Owner approval
No merge
No payment flow
No Token
No betting / odds / 盘口 / 竞猜 / 投注
No fake probability
No fake archived prediction
No SHAP
No xG unless source exists
No injuries inference
No frontend direct vendor call
No token / raw payload commit
No hand-written product narrative in templates (LLM generates; mock only as a marked fallback)
No engineering string-concatenated football analysis
No LLM-fabricated facts (every conclusion carries source_refs or an assumption_flag)
```

**Next Owner decisions**
```text
1. [DONE 2026-06-11] Prompt revision executed as the LLM-Driven Product Proof Sprint (3 samples shipped).
   NEW: review docs/MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md + screenshots -> grant/deny final PASS.
2. Confirm DeepSeek as default narrative provider (re-validated on 3 samples; Gemini benchmark).
3. Operator: set Render dashboard SPA rewrite (/* -> /index.html) + redeploy; verify /recap + /predict live (deep links 404 now).
4. [PARTIAL] 979139 productized this sprint (recap). TheSports / second-source injuries — still gated.
5. Keep PR #3 Draft or split a smaller PR.
```

> MVP-2 detail docs: `docs/MVP2_SCOUTSCORE_V0_MODEL_CARD.md` · `docs/MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md` ·
> `docs/MVP2_USER_REVIEW_REPORT_855737.md` · `docs/MVP2_EVIDENCE_BOARD_V2_DESIGN.md` ·
> `docs/MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md` · `docs/MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2.md` ·
> `docs/MVP2_EVIDENCE_BOARD_V2_OPERATOR_REVIEW.md` · `docs/MVP2_PRODUCT_VOICE_GUIDE.md` ·
> `docs/MVP2_NEXT_DATA_REQUIREMENTS.md`.
> Below this is the prior v0.8 baseline (still valid for environment / language / social / hard rules).

1. **Brand / Product:** **Company = LEIZE** (`CÔNG TY TNHH CÔNG NGHỆ SỐ LEIZE` / `LEIZE DIGITAL
   TECHNOLOGY CO., LTD`); **product = `Giành Cup`** (football intelligence, under **LEIZE AI**).
   **"Cloud" is a future branch, NOT the company brand.** External: "Giành Cup by LEIZE AI". Do NOT
   rename the product or put Cloud in the company name. Details: `docs/BRAND_ARCHITECTURE_LEIZE_GIAND_CUP.md`.
   Product is `Giành Cup` · **2026 World Cup AI Football Intelligence Community**.
   User-facing: **Giành Cup · 世界杯 AI 足球情报社区**. (Retired: Nhà Tiên Tri AI — docs only.)
   **Language roles:** `vi` = primary customer (Vietnam) · `mm` = secondary customer
   (Myanmar/Burmese) · `zh` = internal China-team management · `en` = system / fallback /
   API / admin / schema. vi/mm fall back to **English, never Chinese**.

2. **Live URLs:**
   - Frontend: https://worldcup2026-izid.onrender.com
   - Backend:  https://worldcup2026-api-71n6.onrender.com

3. **Stage:** **MVP v0.8 — real data/model/LLM-draft + multilingual operation** (origin/main synced).
   - **Historical Recap separation (2026-06-09, frontend-only, shipped):** WC-2022 synced (64/64/64) mixed
     historical into `/matches`. Fixed **without backend/API/DB change**: `Match.status` carried through
     `transform.ts`; Home current surfaces filter `status !== 'finished'`; finished matches show only under
     a labelled **Historical Recap · WC2022** surface; Detail/Report show a recap banner when finished.
     **`hit_rate=42.2%` is NOT in any customer UI** (docs-only backtest metric). vi/mm Han=0, zh regression OK,
     build passes. Evidence: `docs/HISTORICAL_RECAP_MODE_PROPOSAL.md` §9 + `docs/qa_screenshots/historical_recap_separation/`.
     **Verdict PASS (frontend separation).** **Operator real-device screenshots can RESUME** (Home un-polluted);
     **final PASS still pending operator review** (`SCOUT_INTELLIGENCE_REWRITE_EVIDENCE.md` §4,
     `VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md`). Recap-row→detail link = optional polish, **not blocking**.
   - **Fast Real Data Gate (2026-06-09):** baseline tagged **`v0.8-real-data-gate`** (`d4feb6c`).
     **Selected matchup mapping is intentionally BLOCKED** until the Render sync confirms a real `match_id`
     (avoid second-seed / fake-real). Next path = **operator runs the Fast Gate** sync order (friendlies
     `10/2026` → WC `1/2026` → WC `1/2022`), then `/matches` → `match_id` → `refresh`
     (`docs/DATA_SOURCE_SYNC_VERIFICATION.md` §13). No mapping/code change until then.
   - **Harness-X Real Match Intelligence Sprint (2026-06-09): real fixtures selected (docs).** Recon found
     real matches (sourced): **upcoming RMI-01 Mexico v South Africa** (WC opener 2026-06-11); **finished
     RMI-02 Brazil 2-1 Egypt, RMI-03 Argentina 2-0 Honduras** (June friendlies). `api_available=unknown`
     (Claude has no token → `BLOCKED_OPERATOR_RENDER_SHELL`, sync NOT run/faked). **model_status=pending_api_sync**
     (no fake numbers); vi operation copy human-authored (no Chinese, no betting). Docs:
     `REAL_MATCH_INTELLIGENCE_SELECTION.md` · `REAL_MATCH_MODELING_REVIEW.md` · `VI_REAL_MATCH_OPERATION_COPY.md`
     · `DATA_SOURCE_SYNC_VERIFICATION.md` §12. Real matches **not yet in the app** → operator screenshots pending.
   - **Harness-X Vietnam Market Heavy Sprint (2026-06-08): PLAN written, Owner review pending.**
     3 roles (Engineering data/modeling · Product flow · Operation vi screenshots). **vi = first priority;
     warm-ups/friendlies (`league_id=10,season=2026`) = first data priority.** No backend/API/DB change
     proposed (sync override already exists). Compliance: AI-intelligence + fan **prediction-game**, **not
     betting**. Plan: `docs/HARNESSX_VIETNAM_MARKET_HEAVY_SPRINT_PLAN.md`; operator review template:
     `docs/VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md`. **Not yet in Implementation.**
   - **Scout Intelligence Rewrite (2026-06-08, Owner-approved, frontend-only):** Report/Detail upgraded to
     a data-backed **Giành Cup Scout** read — Evidence Strip (signal sources, provenance-tagged), Scout
     verdict + hook, factor **Source/Impact/Interpretation**, Contrarian + Watch sections. All derived on
     the frontend (dict + viMapping/mmMapping); **no API/DB change.** vi/mm 0 Han, zh regression OK, build
     passes, no console errors, no forbidden phrases. Evidence: `docs/SCOUT_INTELLIGENCE_REWRITE_EVIDENCE.md`
     + `docs/qa_screenshots/intelligence_rewrite/`. **Engineer self-verify PASS; Stage 5 operator
     real-device verification PENDING** (checklist in the evidence doc §4; shots →
     `docs/qa_screenshots/intelligence_rewrite_operator/`). **Final PASS not granted until operator
     screenshots are reviewed + `final_owner_decision` recorded.**
   - **Language gate CLOSED.** vi mobile QA PASS; mm mobile QA PASS (after screenshot-driven recheck).
     Report-page localization residual **fixed**; Telegram **open/copy fallback UX** added.
   - **vi recheck (2026-06-08, Myanmar standard)** PASS WITH ISSUES — full path incl. `/report` re-scanned;
     one Chinese residual (community "VI TRIAL COPY" badge) **fixed** (`dict.ts` VI `viBadge` → vi-only);
     zh/mm unaffected, build passes, backend untouched. Evidence: `docs/VI_MOBILE_RECHECK_REPORT.md` +
     `docs/qa_screenshots/vi_mobile_recheck/`.
   - **Interaction-state recheck (2026-06-08)** PASS WITH ISSUES — operator hit a **Chinese unlock modal**
     on mm (`已解锁，可直接查看完整报告` / `继续查看报告`). Root cause: `Modal.tsx` hardcoded button +
     `DetailPage` rendering the store/API `res.message` (Chinese) as body. **Fixed** via i18n keys
     `unlockedBody`/`unlockFailedBody`/`continueToReport` (zh/vi/mm/en); store messages neutralized.
     **Interaction-state language QA (modal/toast/action-sheet) is now MANDATORY.** mm/vi modal/sheet/toast
     all screenshot-verified; zh + price isolation unaffected. Evidence: `docs/LANG_INTERACTION_RECHECK_REPORT.md`
     + `docs/qa_screenshots/lang_interaction_recheck/`.
   - **Social:** Myanmar **Telegram active** (`https://t.me/GianhCupMMAIFootball`); **Vietnam Zalo pending active**
     (vi page correctly shows Zalo + Telegram as `Sắp mở`; Myanmar Telegram does not pollute vi).
     **Telegram direct-open may fail in some mobile WebViews — Copy Link is the accepted operating path**
     (open/copy fallback sheet, all locales; ruling: PASS WITH ISSUES, do not block trial on direct-open).
   - **Data:** API-FOOTBALL configured & reachable but **`mock_mode=true`** (last known); **real
     fixtures/results sync NOT run by Claude** — needs `$ADMIN_API_TOKEN` in Render Shell (operator).
   - **Real Data Calibration (2026-06-08, Owner GO):** before WC2026, calibrate with **real competitions**.
     `admin/sync/fixtures` + `admin/sync/results` **already accept optional `?league_id=&season=`**
     (default WC `1`/`2026`) → **no code/DB change needed**. First pick: **La Liga (140)**, fallback
     friendlies (10) / WC-2022 (1/2022). Runbook: `docs/REAL_DATA_CALIBRATION_PLAN.md`. Operator-run on
     Render (Claude has no token → not fabricated). No scaling/payment/bot; LLM still draft-only.
   - **Modeling:** baseline + refresh OK (win_prob sums 100); usable as **AI viewpoint only**, NOT hit-rate.
   - **LLM:** **draft-only** admin endpoint `POST /api/v1/admin/llm/generate-copy` (DeepSeek/Kimi,
     forbidden-filter, human-template fallback, `status:draft_only`). **Real provider call pending
     Render verification** (`AI_PROVIDER=mock` now → fallback). No auto-publish.
   - **LLM draft verification (2026-06-08):** endpoint contract + auth gate + forbidden filter +
     fallback **locally verified** (`backend/scripts/llm_draft_verify.py`, mock → fallback, throwaway
     local token — NOT a real secret). All drafts `draft_only`/`publishable=false`/`forbidden_hits=[]`;
     filter catches dirty (zh/vi/mm/en), allows clean + negations. **Backend harden:** vi/mm/en drafts
     now use **English** team names (zh keeps Chinese) — `copy_service._localized_team_names`.
     **Real DeepSeek/Kimi call still operator-pending on Render (no token for Claude; never fabricated).**
     Evidence: `docs/LLM_DRAFT_COPY_REVIEW_LOG.md`, `docs/LLM_RENDER_VERIFICATION.md`. Human review = pending.
   - **Data-first loop + Mini-Agent + provider comparison (2026-06-08):** Owner GO for data-first model/copy
     loop. **`provider_override`** added (admin/draft-only, `deepseek|kimi|gemini`, backward compatible;
     unknown/unavailable → fallback). **Real 3-provider comparison run locally** (keys already in dev `.env`,
     pre-existing; **never printed/committed**): **DeepSeek + Gemini clean for vi/mm; Kimi leaks Chinese for
     vi/mm** (assumed "Kimi primary" not borne out — empirical: DeepSeek primary, Gemini benchmark). Prompt
     hardened (respond-only-in-target-language) + Gemini `thinkingBudget=0`. **Mini-Agent Harness = lightweight
     DESIGN only** (no runtime). Draft-only; no auto-publish/payment/scaling. Docs: `MINI_AGENT_HARNESS_DESIGN.md`,
     `LLM_PROVIDER_COMPARISON_REPORT.md`. Note: `backend/scripts/llm_draft_verify.py` is a **manual** helper
     (no make/npm target).
   - **NO** payment · **NO** bot auto-publish · **NO** resource scaling.

3b. **Harness-X work protocol (now the project standard):**
   - L0/L1 tasks → Claude self-validation OK. **L2 / high-risk → Owner decision required.**
   - **No screenshot = no PASS** for customer-facing language / mobile QA.
   - **Docs are the source of truth**, not chat/terminal output.
   - **Owner approval required for:** LLM production beyond draft-only · bot auto-publish · payment ·
     deployment scaling · API-shape change · DB-schema expansion · release decisions.
   - Never fake a Render-Shell sync or an LLM provider result; never write "PASS" without evidence.

3c. **Current blockers:** (a) Vietnam Zalo not active; (b) real fixtures/results sync needs operator
   Render Shell (no token for Claude); (c) real LLM provider call must be verified on Render, not local;
   (d) Myanmar Telegram mobile fallback needs operator true-device confirmation after deploy.

3d. **git committer note (do NOT amend history):** commits show a machine-inferred committer because
   `git user.name`/`user.email` are unset locally. Recommended local config (human runs it):
   `git config user.name "Jackie"` · `git config user.email "zhaojifa@gmail.com"`. Do not force-push.

4. **Compliance floor (non-negotiable):**
   不做博彩 · 不做现金投注 · 不承诺命中 · 不承诺收益 ·
   MTC 仅平台积分（不可提现 / 不可转让 / 不可交易）·
   排行榜是积分/连胜榜，不是收益榜。

5. **Forbidden user-facing wording:**
   下注 · 稳赚 · 必中 · 跟单 · 购彩 · 回报率 · 返奖 · 收益承诺 · 现金奖池 ·
   Token 提现/转让/交易。 `提现` 只允许出现在 `不可提现`。

6. **Mandatory disclaimer (战绩/命中/连胜 must carry it):**
   「历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。」

---

## ★ Language & Operation Policy (read before any multilingual/operation work)

> Full baseline: **`docs/MULTILINGUAL_OPERATION_POLICY.md`** (authoritative).

- **Brand:** Giành Cup.
- **Current MVP version:** v0.7 — multilingual operation preparation.
- **Default system / fallback language:** **English** (`en`).
- **Internal management language:** **Chinese** (`zh`; also default UI when no locale chosen).
- **Primary customer operation language:** **Vietnamese** (`vi`) — MVP UI **ready**, pricing **VND / ₫**.
- **Secondary customer operation language:** **Burmese / Myanmar** (`mm`) — MVP UI **ready &
  acceptance-verified** (core Burmese, rest → English; no Chinese residual; no ¥/元/₫), pricing
  **MMK (Ks)** = "MM MVP operation test pricing" (12,000 Ks / 59,000 Ks/လ, matches page).
  Trial URL: `https://worldcup2026-izid.onrender.com/?lang=mm`.
  - **Myanmar density profile:** Burmese glyphs are taller / words longer, so mm uses a
    **separate, shorter copy set** and a `.lang-mm` CSS density profile (root carries
    `data-lang` + `lang-${locale}` in `Layout.tsx`). **Burmese copy must stay shorter than
    Vietnamese**; concise English product terms (AI / Risk / Update / MTC / Premium / VIP /
    team names) are allowed in mm UI. zh / vi / en are unaffected (rules scoped to `.lang-mm`).
  - **Burmese translation accepted by operation team (2026-06-06).** mm upgraded from
    "framework + English fallback" to **customer-ready Burmese**: core UI (Home/Detail/Token/
    Community), dynamic data (team outcomes, AI tendency, risk level/tags, notes, reason bullets,
    live-correction) all Burmese via `copy/mm.ts` + `i18n/mmMapping.ts`. **English remains the
    system fallback** for unmapped dynamic data only; **Chinese is never a customer-side fallback.**
  - **Myanmar mobile QA passed (2026-06-07).** Screenshot-verified at 390×844 & 430×932 →
    `docs/MM_MOBILE_QA_REPORT.md` (PASS), shots in `docs/qa_screenshots/mm_mobile/`. Fixed Today
    Matches row overlap (mm `.simrow` two-row), shortened signal CTA, Burmese channel descriptions.
  - **Vietnamese mobile QA passed (2026-06-07).** Same screenshot method → `docs/VI_MOBILE_QA_REPORT.md`
    (PASS), shots in `docs/qa_screenshots/vi_mobile/`; no residual found (vi already customer-ready).
  - **Screenshot-driven QA is MANDATORY for customer languages (vi/mm)** before declaring a layout
    PASS (QA script: `scripts/qa/lang_mobile_shots.sh`, headless Chrome — not a prod dependency).
  - **Language gate CLOSED.** Next phase plan: `docs/NEXT_PHASE_DATA_MODEL_SOCIAL_LLM_PLAN.md`
    (Data / Modeling / Social / LLM-prep / deployment / go-live gate). LLM stays in prep, not
    full build.
  - **Harness-X L1 + P-flow Prep (2026-06-08):** verified data-source (connector ok, `mock_mode=true`,
    0 settled → no real hit-rate claimable) → `docs/DATA_SOURCE_SYNC_VERIFICATION.md`; baseline
    predictor + refresh (win_prob=100) → `docs/MODELING_BASELINE_VERIFICATION.md`; vi/mm copy library
    → `docs/OPERATION_COPY_LIBRARY_VI_MM.md`; LLM prep schema+guardrails (design only) →
    `docs/LLM_PREP_SCHEMA_AND_GUARDRAILS.md`. **Channels: Myanmar Telegram ACTIVE (verified live),
    Vietnam Zalo pending.** LLM Full Build remains Owner-gated.
  - **Data+Model Formalization (2026-06-08, Owner-approved bounded L2-lite, NO scaling):**
    refreshed matches 1/2/3 (all `win_prob`=100; m1 high/conf61, m2 low/conf80, m3 low/conf86;
    **response shape unchanged**); added m2/m3's new `risk_note` to vi/mm/en note maps so vi/mm
    stay non-Chinese; copy library filled from real model output (AI-viewpoint, no hit-rate).
    **Real `admin/sync/fixtures|results` BLOCKED for Claude** (needs `$ADMIN_API_TOKEN` in Render
    Shell — operator step; data stays `mock_mode=true` until then). Myanmar Telegram trial
    `ready_to_send`; Vietnam Zalo pending. **No backend/API/DB/scaling change.**
  - **Real LLM integration — DRAFT-ONLY (2026-06-08, Owner GO WITH CONDITIONS).** New
    `app/services/llm/` (compliance filter, prompts, deepseek/kimi client, copy_service) + admin
    endpoint `POST /api/v1/admin/llm/generate-copy` (x-admin-token, `status:draft_only`,
    `publishable:false`). Forbidden-phrase filter (zh/vi/mm/en, allows negations) + human-template
    fallback (LLM fail → rules copy) + `AI_PROVIDER=mock` rollback. **NO auto-publish, NO DB write,
    NO payment, NO scaling, NO public API-shape change.** `httpx` already present (no new dep).
    Real provider call to be exercised on Render with key (currently `AI_PROVIDER=mock` → fallback).
    Plan: `docs/LLM_REAL_INTEGRATION_PLAN.md`. **Unreviewed LLM output is NO-GO** (human review gate).
  - **BLOCKED_STATE_DIVERGENCE recheck (2026-06-08):** operator (real phone) reported Telegram
    `ERR_CONNECTION_REFUSED` + `/detail?lang=mm` Chinese residual. Root cause: the **Report page**
    (`/report`, via detail→unlock) was never localized (hardcoded zh). Fixed: ReportPage +
    FeatureBars localized (zh/vi/mm/en) incl. trend/tactics/feature mappings; CommunityPage active
    channel now shows an **open/copy fallback sheet** (uses API `public_url`, still tracks
    `click_social_channel`). Screenshot-verified (`docs/qa_screenshots/mm_mobile_recheck/`,
    `docs/MM_MOBILE_QA_REPORT.md`). zh/vi unaffected. **Lesson: screenshot-driven QA must cover the
    full unlock→report flow, not just /detail.** No backend/API/DB/scaling change.
- **API / admin / config / schema / data contract language:** **English** (ASCII identifiers).
- **Fallback chains:** `zh→[zh]`, `en→[en,zh]`, `vi→[vi,en]`, `mm→[mm,en]`.
  **vi/mm must NEVER fall back to Chinese** — English is their fallback.
- **Pricing localization** (`frontend/src/i18n/pricing.ts`; never hardcode ¥ in pages):
  zh = RMB, en = USD, vi = VND, mm = MMK. MVP operational prices, not real-time FX. MTC constant.
- **Full i18n:** deferred. **LLM translation/generation:** deferred until after a real
  operation trial (then behind a banned-word output filter).
- **UI language buttons:** `CN · VI · MY` (`en` is the internal fallback layer, no button).
- **Operational blocker:** an `active` Zalo/Telegram channel remains the gate to the real trial.
- **i18n code:** `frontend/src/i18n/{useLocale,dict,pricing,viMapping}.ts`,
  `frontend/src/copy/{zh,en,vi,mm}.ts`.
- **Operation copy docs:** `docs/OPERATION_TRIAL_MESSAGES_VI.md`,
  `docs/MM_OPERATION_TRIAL_MESSAGES.md`, `docs/VI_OPERATION_TRIAL_RUNBOOK.md`.

---

### Key design docs (read after this file when doing product work)
- `docs/PRODUCT_OPERATION_ALIGNMENT_V1.md` — **formal** product/operation plan
  (positioning upgrade, home/detail IA, API & modeling output layer, ops,
  compliance, phased roadmap). Authoritative for product scope.
- `docs/_drafts/product_operation_alignment_brainstorm.md` — exploratory draft
  behind the formal plan (background only).
- `docs/MVP_STATUS.md`, `docs/DAY4_DATA_AUTOMATION.md` — engineering baseline.

---

## 1. Project Identity

- **Name:** worldcup2026
- **Brand (final):** **Giành Cup**（中文：赢杯 / 夺杯 · 世界杯 AI 足球情报官）。
  用户侧标准文案：`Giành Cup` · `2026 World Cup AI Football Intelligence` ·
  `Giành Cup · 世界杯 AI 足球情报社区`；副文案「不只看胜率，更看 AI 为什么这样判断。」
  代码标识符用 ASCII `GIAND_CUP` / `GIAND_CUP_BRAND`，显示必须为 `Giành Cup`。
  人设是 AI 数据观点 / 风险提示 / 临场修正解释，**不是结果承诺品牌**；禁用
  「必中神 / 稳赚神 / 跟单大神 / 包赢」等称谓。
  _曾用命名方案：Nhà Tiên Tri AI（已弃用为主品牌；用户侧 UI 已于 Day 6B 全部替换为
  Giành Cup，仅保留于历史文档说明）。代码品牌常量集中在 `frontend/src/copy/zh.ts`
  的 `GIAND_CUP_BRAND`（`BRAND` 为兼容别名）；R2 资产 key 统一使用 `giand-cup`。_
- **Positioning:** 2026 世界杯 **AI 足球情报社区**（formalized in
  `PRODUCT_OPERATION_ALIGNMENT_V1.md`；前身表述「AI 情报终端」），面向越南、缅甸
  及东南亚球迷。**不做博彩，不提供现金投注，不承诺收益。**
  用户侧使用「AI 足球情报社区 / AI 赛事情报 / AI 数据观点 / AI 倾向」；避免「决策社区」。
- **Core selling points:**
  - AI 赛前预测
  - 高可信 AI 解释
  - 临场 30 分钟修正
  - MTC 平台积分闭环
  - 39 元单场解锁
  - 199 元/月社群订阅

---

## 2. Current Baseline

**MVP v0.4 · Auto Data Source + Baseline Predictor Baseline**

**Active theme — Day 6: Real Data & Storage Integration** (plan:
`docs/DAY6_REAL_DATA_STORAGE_PLAN.md`). Order: 6A Real Result Loop
(MatchResult / PredictionSettlement / admin sync results / performance) →
6B R2 Content Asset Storage → 6C social config + community heat →
6D streak / rankings. Day 6 plan is design-only; implementation is additive
and must not break existing API shapes or `VITE_USE_MOCK` dual mode.

Done:
- Frontend Render 部署
- Backend Render 部署
- Render PostgreSQL seed
- 前后端 API 联调
- UI / Copy Enhancement
- API-FOOTBALL connector
- data-source status
- admin protected fixtures sync
- baseline predictor
- match refresh API

Live URLs:
- Frontend: https://worldcup2026-izid.onrender.com
- Backend:  https://worldcup2026-api-71n6.onrender.com

---

## 3. Repository Rules

- **Standard path:** `/Users/jackie/code/worldcup2026`
- **Do NOT use the wrong path:** `/Users/jackie/code/wordcup2026` ❌
- **GitHub:** https://github.com/zhaojfifa/worldcup2026

Commit rules:
- 小步提交（small, focused commits）
- 每个阶段必须 push
- 不提交 `.env`、`.env.local`、`node_modules`、`.claude`、真实 API key
- 修改环境变量时同步 `.env.example` 或 `docs`，但**不能写真实值**

---

## 4. Architecture

Pipeline:
```
DataSource
→ Feature Builder
→ Prediction Engine
→ Explanation Engine
→ Report Generator
→ Frontend API
```

Current implementation:
- **DataSource:** API-FOOTBALL connector + seed fallback
- **Prediction Engine:** baseline rules model
- **Explanation Engine:** mock / structured copy
- **AI_PROVIDER:** `mock`
- **R2:** not enabled

---

## 5. Frontend Rules

Path: `frontend/`

Must preserve:
- `VITE_USE_MOCK=true / false` 双模式
- `VITE_API_BASE_URL`
- `client.ts`
- `transform.ts`
- snake_case API → camelCase frontend isolation
- mobile-first UI
- 世界杯权威蓝白金风格 + Sports App 视觉增强

Must NOT break:
- Home / Detail / Report / Token / Community 页面
- MatchCard
- LINEUP WATCH
- MTC Fan Mission Center
- AI Tactical Room

---

## 6. Backend Rules

Path: `backend/`

Render config:
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Core API:
```
GET  /api/v1/health
GET  /api/v1/matches
GET  /api/v1/matches/{id}
GET  /api/v1/reports/{id}
GET  /api/v1/data-source/status
POST /api/v1/admin/sync/fixtures
POST /api/v1/matches/{id}/refresh
POST /api/v1/tokens/checkin
POST /api/v1/tokens/unlock-report
POST /api/v1/challenges/{id}/join
POST /api/v1/community/subscribe
```

- Admin 接口必须使用 `x-admin-token`。
- `ADMIN_API_TOKEN` 未配置时 admin 路由必须锁住（401），**不得开放公网**。

---

## 7. Environment Variables

Record variable **names only — never real values**.

```
APP_ENV
DATABASE_URL
API_FOOTBALL_BASE_URL
API_FOOTBALL_KEY
WC_LEAGUE_ID
WC_SEASON
ADMIN_API_TOKEN
AI_PROVIDER
DEEPSEEK_API_KEY
KIMI_API_KEY
GEMINI_API_KEY
CORS_ORIGINS
ENABLE_REAL_MONEY_BETTING
ENABLE_TOKEN_WITHDRAWAL
VITE_API_BASE_URL
VITE_USE_MOCK
```

Current Render backend (non-secret):
- `AI_PROVIDER=mock`
- `WC_LEAGUE_ID=1`
- `WC_SEASON=2026`

---

## 8. Compliance Rules

Forbidden in marketing/copy:
- 下注
- 稳赚
- 必中
- 跟单
- 购彩
- 回报率
- 返奖
- 收益承诺

`提现` is allowed **only** inside: **不可提现**.

MTC must always be described as **平台积分 / platform loyalty points**, and must declare:
- 不可提现
- 不可转让
- 不可交易
- 不作为金融资产
- 不承诺收益
- 不接入博彩

---

## 9. Day 4 Result

- `backend/app/services/modeling/baseline.py`
- `backend/app/routers/data_source.py`
- `backend/app/routers/admin.py`
- `docs/DAY4_DATA_AUTOMATION.md`
- API-FOOTBALL `get_fixtures` + `status`
- fixtures sync Team/Match upsert（by `api_id` / `external_id`，update 不重复 insert）
- `refresh_prediction`
- `POST /matches/{id}/refresh`
- 概率归一化通过 2000 次随机测试（0 例 sum≠100）
- admin sync：无 token / 错误 token → 401，正确 token → 200

---

## 10. Next Milestones

Suggested order:
- **Day 4.5:** Render 部署验证 Day 4 新接口
- **Day 5:** 前端增加数据源状态 / refresh 管理入口，或后台轻量 admin panel
- **Day 6:** `AI_PROVIDER` 从 mock 切到 DeepSeek/Kimi 的 report generator
- **Day 7:** R2 / 分享卡 / 多语言 / 运营验收

**Guardrails until Day 5:**
- Day 5 前不要大改 UI。
- Day 5 前不要破坏现有 API shape。
- Day 5 前不要引入复杂 ML 训练。
- Day 5 前不要启用真实支付。
- Day 5 前不要接链上 Token。
