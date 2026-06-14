# MVP-2 Next Engineering Thread Handoff

_Read `CLAUDE.md` first, then this. Date: 2026-06-13. Supersedes the prior v0.8 handoff (baseline kept at the bottom)._

## ★★★★★★ P1.5c merged + product-mechanism correction (2026-06-14, supersedes ★★★★★ below)

```text
main = 6bc4c0d. P1.5c (agent-led daily editorial selection) is merged: scripts/mvp2_editorial_agent.py
prints a copy-paste LLM prompt from the local daily fixture slate — NO scoring engine, NO team/
popularity/importance weights, NO external API call, NO production write, NO send. Operator runs
DeepSeek/Gemini/Kimi, reads back a structured JSON recommendation, and confirms the daily selection
through the existing P1.3/P1.4 manual path. Detail: docs/mvp2_growth/GROWTH_P15C_EDITORIAL_AGENT.md.

OWNER PRODUCT-MECHANISM CORRECTION (2026-06-14):
  "Daily selection must be Agent-led and LLM-assisted. The system should not mechanically promote
   whichever fixture is recap_ready. The daily story should be selected from current fixtures,
   match importance, public heat, result surprise, and growth objective by DeepSeek/Gemini/Kimi or
   equivalent LLM, then confirmed by the operator."
The gap: fixtures update / homepage renders states / growth attribution works, but featured match
and recap priority were not yet driven by the daily hotspot story. The hotspot is an editorial
judgment (LLM-recommended, operator-confirmed), NOT a recap_ready flag.

Concrete rule (2026-06-13, hotspot = Brazil vs Morocco):
  - before kickoff → Brazil vs Morocco = featured pre-match (daily story)
  - after finish   → Brazil vs Morocco = first recap-priority candidate
  - Mexico vs South Africa = fallback/secondary recap, NOT the main story
  - Canada/USA/SK = completed status only unless operator selects
  - Qatar/Haiti = upcoming status only unless operator selects

DO NOT (Owner): build a scoring engine · hand-code team popularity / match weight · add complex
frontend selection rules · add backend schema · auto-call external LLM APIs · auto-send · fake recap.
Any minimal note stays as prompt wording only.

First send STILL HOLD on Gate 3 (1489371 LIVE/FT lifecycle) + Gate 4 (Owner per-channel GO).
The product is one daily featured pre-match + one daily featured recap + lightweight status for the
rest + more service inside the group; Agent/LLM recommends, operator confirms, frontend renders.
```

## ★★★★★ Current handoff state — Growth P1.5b LIVE · first-send Gates 1+2 PASS · HOLD on Gate 3+4（2026-06-13, supersedes ★★★★ below）

**Growth P1.2→P1.5b is on main AND deployed live. First-send Gate 1 (codes) + Gate 2 (smoke) are CLOSED.
The only remaining gates are Gate 3 (1489371 LIVE/FT validation tonight) and Gate 4 (Owner per-channel GO).
The next thread is NOT new features — it is tonight's 1489371 match-day operation, then the first send on Owner GO.**

```text
Frozen state (A):
  main = d67c5e1 (origin + local). Latest = P1.5b Daily Featured Copy Policy (copy-only, frontend-only;
  backup tag main-backup-pre-p15b-daily-featured-copy-20260613). Full promoted chain this day:
  P1.2 · P1.2b · P1.3 · P1.3b · P1.3c · P1.4 · P1.5a · P1.5b. Operation paused · small private trial
  only · sends manual + Owner GO per fixture · engineering holds NO prod ADMIN_API_TOKEN · no betting/
  odds/auto-send anywhere.

What is LIVE (B) — verified 2026-06-13:
  - Backend deployed + populated: GET /api/v1/daily-fixtures → stored=true, 7 fixtures, P1.4 buckets,
    active_hero Brazil vs Morocco SCHEDULED, recap_queue 4, freshness.stale=false. 能更新 PROVEN.
  - FRONTEND P1.5b DEPLOYED: live bundle index-TTpDdcCl.js (P1.5a) → index-Dz95Uq3Y.js (P1.5b).
    Homepage = Daily Featured Copy Policy: 🔮今日复盘 = Mexico 2-0 ONLY (查看复盘 button) · 🗂️今日赛况 =
    Canada/USA/SK 已完赛 (no button) · 📋即将开赛 = Qatar/Haiti · bottom CTA 更多场次临场判断，进群后
    按比赛补充 · realtime sync line present · legacy 复盘生成中/待生成复盘/待生成赛前判断 REMOVED.
    zh/vi/my consistent. Live visible scan 21/21; runtime/match-sync/growth scanners PASS.

FIRST-SEND GATES (C):
  1. Codes — ✅ PASS. Operator created QG-TEST1 / TT-VN88 / FO-MM21 in prod (active). Live re-probe
     POST /api/v1/growth/click → attached:true ×3.
  2. Growth smoke — ✅ PASS. click+join-intent attached:true ×3; /internal/growth shows 3 active codes,
     counts visible, 3 PENDING test join-intents; contribution value=0; NO send. Test join-intents
     left UNCONFIRMED (no MTC credit).
  3. 1489371 Brazil vs Morocco LIVE/FT lifecycle validation — ⏳ TONIGHT (KO 22:00 UTC). Pre-kickoff
     half already PASS (SCHEDULED, /predict not frozen, hero Brazil). Operator runs at the match window.
  4. Owner explicit per-channel GO — ⏳ pending, e.g. `GO zh_internal_group QG-TEST1 fixture 1489371`.
  NO send until Gate 3 LIVE/FT passes AND Gate 4 GO is given.
  Gate doc docs/mvp2_growth/GROWTH_P15_FIRST_SEND_GATE.md · runbook docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md
  (both now on main). First-send material staged: docs/data_audit/mvp2_growth_packages/today_1489371_zh_QG-TEST1.md.
```

**Next Engineer Start Command（copy-paste）**

> Working branch is main (d67c5e1). Growth P1.2→P1.5b promoted + deployed; do NOT start new features.
> Gates 1+2 are CLOSED. Confirm live: `curl -s …/api/v1/daily-fixtures | python3 -m json.tool` (stored=true,
> 7 fixtures, hero Brazil SCHEDULED) and bundle = index-Dz95Uq3Y.js (P1.5b). Run the four scanners (visible
> 21/21, runtime --base-url, match-sync, growth copy). Then TONIGHT's Gate 3: 1489371 Brazil vs Morocco KO
> 22:00 UTC — at kickoff verify the pre-match freezes (status-refresh → LIVE, refresh → NO_VALID_TODAY_FIXTURE,
> /predict & /share freeze), at FT → FINISHED/RECAP_PENDING, no fake recap. Then first send only on Owner Gate-4
> per-channel GO. Engineering holds no prod token (codes/smoke/send are operator steps).

## ★★★★ Handoff state — Growth P1.2→P1.5a on main · 能更新 LIVE · FIRST-SEND GATE（2026-06-13, superseded by ★★★★★ above）

**The whole Growth P1.2→P1.5a chain is on main and the daily slate now updates live without a frontend rebuild.**
The next thread is NOT new features — it is: operator deploys the P1.5a frontend, then closes the four
first-send gates, then the 1489371 match-day operation tonight.

```text
Frozen state (A):
  main = a26b03d (origin + local). Promoted this thread, each with a backup tag:
  P1.2 status-refresh gate · P1.2b runtime freshness guard · P1.3 match sync & daily registry ·
  P1.3b runtime manifest · P1.3c backend daily-fixtures source · P1.4 orchestration · P1.5a lean landing.
  Operation paused · small private trial only · sends manual + Owner GO per fixture ·
  engineering holds NO prod ADMIN_API_TOKEN · no betting/odds/auto-send anywhere.

What is LIVE (B) — verified 2026-06-13 ~11:30 UTC:
  - Backend DEPLOYED + POPULATED: GET https://worldcup2026-api-71n6.onrender.com/api/v1/daily-fixtures
    → stored=true, 7 fixtures, P1.4 buckets (completed_matches/upcoming_needs_narrative/product_status),
    active_hero Brazil vs Morocco, recap_queue 4, freshness.stale=false. runtime_manifests table live.
    (Operator uploaded 10:13Z via `mvp2_match_sync.py upload --target production`.)
  - 能更新 PROVEN: backend empty→7 fixtures via upload; homepage flipped 静态备份→实时; frontend bundle
    hash UNCHANGED → live slate updates with NO frontend redeploy.
  - SPA deep links 200. Live visible scan 21/21. runtime/match-sync/growth scanners PASS.
  - ⚠️ FRONTEND live bundle = index-DBnoe6Hq.js = P1.4 build. **P1.5a (a26b03d) NOT deployed yet** —
    operator must Manual Deploy worldcup2026 from main (backend NOT needed). Until then the live homepage
    still shows the pre-lean layout (Strong Calls etc.); the lean version is verified on the build only.

Match states on the live registry (C): Brazil vs Morocco = hero/SCHEDULED · Canada 1-1 Bosnia =
  RECAP_PENDING (复盘生成中) · USA 4-1 Paraguay = RECAP_PENDING (待生成复盘, unmapped) · Mexico 2-0
  South Africa = RECAP_READY (查看复盘, the ONLY recap-ready) · South Korea 2-1 Czechia = RECAP_PENDING ·
  Qatar/Haiti = SCHEDULED upcoming-needs-narrative (待生成赛前判断). No fake recap; no invented scores.

FIRST-SEND GATES still open (D) — none sendable until ALL clear:
  1. Codes: operator creates QG-TEST1 / TT-VN88 / FO-MM21 via /internal/growth (prod token).
     Live probe: POST /api/v1/growth/click ref=QG-TEST1 → attached:false ⇒ NOT created yet.
  2. Growth smoke: /join?ref=QG-TEST1 → click+join-intent counters increment, attached:true, dashboard shows it.
  3. 1489371 LIVE/FT lifecycle validation TONIGHT (KO 22:00 UTC) — see runsheet + first-send gate doc.
  4. Owner explicit per-channel GO, e.g. `GO zh_internal_group QG-TEST1 fixture 1489371`.
  Runbook: docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md · gate status: docs/mvp2_growth/GROWTH_P15_FIRST_SEND_GATE.md.
```

**Next Engineer Start Command（copy-paste）**

> Working branch is main (a26b03d). The Growth P1.2→P1.5a chain is promoted; do NOT start new features.
> First confirm the live state: `curl -s https://worldcup2026-api-71n6.onrender.com/api/v1/daily-fixtures | python3 -m json.tool`
> (expect stored=true, 7 fixtures) and check the live frontend bundle hash — if it is still
> index-DBnoe6Hq.js, the P1.5a frontend deploy is pending (operator action). Then run the scanners
> (`check_runtime_daily_fixtures.py --base-url …`, `check_customer_visible_copy.py …` 21/21,
> `check_match_sync_freshness.py`, `check_growth_copy.py`). Then progress the four first-send gates:
> codes (operator+prod token) → smoke (attached:true) → tonight's 1489371 LIVE/FT validation → Owner GO.
> Engineering holds no prod token, so code-creation/smoke/send are operator steps. Tonight: 1489371
> Brazil vs Morocco KO 22:00 UTC — at kickoff verify the pre-match freezes (status-refresh → LIVE,
> refresh → NO_VALID_TODAY_FIXTURE, /predict & /share freeze), at FT → FINISHED/RECAP_PENDING, no fake recap.

**Key P1.2–P1.5a tooling (all on main)**
- `scripts/mvp2_fixture_lifecycle.py` — canonical lifecycle (SCHEDULED..ARCHIVED); selftest.
- `backend/app/services/lifecycle.py` — backend runtime normalization (additive MatchListItem fields).
- `frontend/src/lib/freshness.ts` — frontend defensive guard (computeFreshness/pickActiveFixture).
- `scripts/mvp2_match_sync.py` — sync / upload --target production / recap-queue (manual_scores → registry).
- `backend/app/{models/runtime_manifest.py,services/daily_fixtures_service.py,routers/daily_fixtures.py}` — P1.3c store + GET/upload.
- `frontend/src/data/dailyFixtures.ts` — three-tier fetch (backend 实时 → static 静态备份 → bundled 内置).
- `frontend/src/components/MatchDesk.tsx` — P1.4 recap desk / upcoming / operator status.
- Scanners: `check_fixture_freshness.py` · `check_match_sync_freshness.py` · `check_runtime_daily_fixtures.py` (`--base-url` for live).
- Cron + operator flow: `docs/mvp2_growth/GROWTH_P11B_SCHEDULED_REFRESH.md` §3b/3c/3d (sync+upload, no auto-send).

## ★★★ Prior handoff state — main promoted through Growth P1.1c-fix · MATCH DAY 1489371（2026-06-13, superseded by ★★★★ above）

**This supersedes the ★★ section below.** The 2026-06-12 thread ran 18 rounds past that handoff:
deploy gate cleared, main promoted (PR #3 MERGED), Growth P0→P1→P1.1→P1.1b→P1.1c all accepted and
promoted. The next thread starts from **one pending frontend deploy + first zh send + the 1489371
match-day runsheet (TODAY)** — not from new features.

```text
Frozen state (A) — as of 2026-06-12 ~15:35 UTC (round 18):
  Working branch = MAIN @ 89235b0 (docs evidence head; code head 0a73ee6 = Growth P1.1c-fix
  canonical strong-call projection). PR #3 = MERGED-closed (accepted side effect of main
  fast-forward; backup tags main-backup-pre-*-20260612 series exist; never force-push).
  feature/mvp2-api-football-ingestion fully landed. Public operation still paused · small private
  trial only · sends manual + Owner GO per fixture · no payment/token · no betting/odds/handicap/
  casino wording · engineering holds NO prod ADMIN_API_TOKEN (by design).

What is LIVE (B) — last verified 2026-06-12:
  - SPA rewrite configured: all deep links 200.
  - Backend: Growth P1 live (5 growth tables, /growth/* endpoints, admin 401 wall verified).
  - Frontend: live bundle index-Dc5TM6Ba.js = d97894a build (P1.1c risk-label fix live; share
    layer + /join + /share routes live; live scan 21/21 at that build).
  - NOT live yet: 0a73ee6 canonical projection (markers to verify after deploy:
    `sc-primary-score` / `比分为什么偏离`). Owner round-17 HELD the first send over
    predict/share semantic drift; 0a73ee6 is the fix and main carries it.

Trial/send state (C):
  - Growth packages regenerated on main: 9/9, summary 1534Z, under
    docs/data_audit/mvp2_growth_packages/ (first zh send material =
    today_1489371_zh_QG-TEST1.md, regenerate after any copy change).
  - First send sequence (Owner GO framework already given in P1.1b round-14 verdict §5, but
    BLOCKED until): operator deploys main frontend → live 4-surface strong-call consistency
    check PASS (home hero / predict StrongCallCard / share card / package copy must show the
    SAME 主比分/备选/中高 risk label) → operator creates codes QG-TEST1/TT-VN88/FO-MM21 via
    /internal/growth with real ADMIN_API_TOKEN → growth smoke drill → first zh send
    (zh today-package → zh_internal_group, MANUAL).

Match day (D) — 1489371 Brazil–Morocco, TODAY 2026-06-13:
  T-2h check 20:00 UTC · T-90 lineup watch 20:30 UTC · kickoff 22:00 UTC · A4 recap from
  ~00:45 UTC 06-14. Procedure: docs/mvp2/TRACKA_1489371_A3A4_RUNSHEET.md. Latest watch probe
  r20260612T1535Z-watch: fixture NS, lineups 0/0 (T-1825min). A3 group_update_message usable
  ONLY after guard_passed + queue approve; A4 must cite archived prematch artifact
  path+sha256+timestamp (guard enforces). No send after kickoff.
```

**Next Engineer Start Command（copy-paste）**

> Working branch is main (~89235b0, code head 0a73ee6). PR #3 is merged; do not look for the old
> feature branch. Do not start new features. First: confirm whether the operator has deployed
> main (0a73ee6+) to worldcup2026-izid — check the live bundle for the `sc-primary-score` marker
> and run `python3 scripts/check_customer_visible_copy.py https://worldcup2026-izid.onrender.com`
> (21/21 required). Then run the live 4-surface strong-call consistency check (home hero /
> /predict/1489371 strong card / /share/fixture/1489371 / growth package copy). Only after that
> passes: operator code creation + growth smoke + first zh send. Today is 1489371 match day —
> follow docs/mvp2/TRACKA_1489371_A3A4_RUNSHEET.md (T-90 20:30 UTC, kickoff 22:00 UTC, A4 ~00:45
> UTC 06-14) and report in the 12-section evidence format.

**Next execution checklist**
1. Verify `git status` clean on main; HEAD ≥ 89235b0; `main-backup-pre-p11cfix-20260612` tag exists.
2. Operator: frontend manual deploy of main (frontend-only; backend already live).
3. Verify live bundle ≠ index-Dc5TM6Ba.js and contains `sc-primary-score` / `比分为什么偏离`; deep links 200.
4. Live visible scan 21/21 (`scripts/check_customer_visible_copy.py`) + growth copy guard surfaces.
5. Live 4-surface strong-call consistency check (same 主比分/备选/harmonized 中高 everywhere); retake live screenshots.
6. Operator: create QG-TEST1/TT-VN88/FO-MM21 (real ADMIN_API_TOKEN; placeholder tokens 401 by design) + growth smoke drill.
7. First zh send: `today_1489371_zh_QG-TEST1.md` content, manual, before kickoff only, record time/group/screenshot.
8. 1489371 runsheet: T-90 watch (`scripts/mvp2_ops.py watch`) → A3 rescore (guard → queue approve → manual send) → kickoff stop → A4 recap FT+45 (provenance enforced) → recap package refresh (`mvp2_growth_cli.py refresh`).
9. Evidence report per the 12-section format (section G below still applies).

**Standing lessons (carry forward)**
- Check the current branch BEFORE committing after promotion rounds (round-17 slip).
- Live scan vs local scan diverge wherever the frontend renders backend-fetched strings (mock mode hides backend copy).
- DeepSeek does not converge on guard retries alone — banned n-grams must be in the PROMPT.
- `.py` docstrings are NOT stripped by the comment-stripper guards.
- Quota ledger under-counts subprocess API calls (open P1).

## ★★ Prior handoff state — Track A P0 accepted · deploy-verification handoff（closed 2026-06-12, superseded by ★★★ above）

**Owner verdict: Track A P0 = PASS WITH CONDITIONS.** Engineering baseline accepted; the small
private trial CANNOT proceed until the trial frontend is manually deployed at `b458fd5`+ and the
Render SPA rewrite is configured. This thread is closed docs-only; the next thread starts from
**deploy verification + real match trial execution**, NOT from new product features.

```text
Frozen state (A):
  branch feature/mvp2-api-football-ingestion @ b458fd5 (latest accepted; P0 acceptance base 54026ad) ·
  PR #3 OPEN + Draft · main untouched · public operation paused · small private trial only ·
  Track A P0 IMPLEMENTED + dry-run verified (scan/prematch/watch/rescore/recap/bundle/queue/status;
  file review queue w/ sha256 tamper-reject; A1 real scans; first FULL A2 done on 1539000) ·
  Track B remains DESIGN-ONLY — MUST NOT be implemented yet (no referral tables/routes/UX/QR/rewards) ·
  no auto-send · no payment · no betting/odds/handicap/casino wording anywhere customer-facing.

Owner conditions (B):
  1. Operator manually deploys b458fd5+ to the trial frontend (worldcup2026-izid).
  2. Operator configures Render SPA rewrite: Settings -> Redirects/Rewrites -> /* -> /index.html -> Rewrite.
  3. After deploy, the LIVE visible-copy scan must PASS before any trial links are sent.
  4. All trial sends remain MANUAL and require Owner GO per fixture.

Live deployment truth (C) — recorded honestly, last verified 2026-06-11 ~16:05 UTC:
  - b458fd5 is NOT live until verified after an operator deploy — do not claim otherwise.
  - The live bundle (assets/index-HLZD2ZGB.js) still contained OLD wording (今日AI观点 ×1) in the
    last verification window = pre-54026ad content on customer pages.
  - Deep links (/predict/*, /recap/*) still 404 until the SPA rewrite is configured.
  - render.yaml alone may NOT affect the manually created Render static service — the dashboard
    rewrite rule is required; no auto-deploy materialized after pushes (operator deploys only).
  - Clean evidence pre-staged: 54026ad+ production-build fingerprint (今日AI观点 ×0), prod-build
    15-surface scan 15/15 PASS, shots in docs/qa_screenshots/mvp2_tracka_deploy_verify/.

Next engineering objective (D):
  Deploy verification -> live visible-copy scan -> fixture A2/A3/A4 execution (1539000, 1489371)
  -> operator review -> manual-send readiness -> evidence report.
```

**Next Engineer Start Command（copy-paste · E）**

> Owner has accepted Track A P0 with conditions. Start by verifying branch
> feature/mvp2-api-football-ingestion at b458fd5 or later, PR #3 Draft, main untouched, and
> Track B runtime absent. Do not implement new features first. First verify whether b458fd5+ is
> deployed to the trial frontend and whether SPA rewrite is configured. Then run live
> visible-copy scan on home / predict / recap pages across zh / vi / my. Only after live scan
> passes, continue Track A fixture operations for 1539000 and 1489371 according to the runsheet.

**Next execution checklist (F)**
1. Operator deploys `b458fd5`+ to the worldcup2026-izid trial frontend (manual deploy).
2. Operator configures SPA rewrite: `/*` → `/index.html` → Rewrite (Render dashboard).
3. Run: `python3 scripts/check_customer_visible_copy.py https://worldcup2026-izid.onrender.com`
4. Verify all 15 surfaces (/, /predict/1489369, /predict/1489371, /recap/855737, /recap/979139 × zh/vi/my).
5. Verify NO visible old AI/model/process wording on customer surfaces (outside disclaimer/internal folds).
6. Verify the four deep links load directly (no 404).
7. For 1539000: verify A2 artifacts + the Bosnia kaggle-alias fix — **Elo gap must read 188, not 314**.
8. For 1489371: follow `docs/mvp2/TRACKA_1489371_A3A4_RUNSHEET.md` (T-90 watch → A3 rescore → review →
   manual send → kickoff sweep → FT+45 recap; kickoff 2026-06-13 22:00 UTC).
9. A3 `group_update_message` is usable ONLY after guard_passed + review approved (queue enforces).
10. A4 recap must cite the archived prematch artifact path + sha256 + timestamp (guard enforces).

**Required report format for the next engineer (G)**
1 Branch/commit/PR Draft status · 2 whether b458fd5+ is deployed · 3 live bundle proof + screenshots ·
4 SPA rewrite status · 5 live visible-copy scan result · 6 1539000 A2 result · 7 1489371 A3/A4
execution or readiness · 8 generated artifacts · 9 guard/build/visible scan results ·
10 blocked_by_time_or_data records · 11 operator actions still required · 12 GO/NO-GO recommendation.

Track A operating docs: `docs/MVP2_TRACK_A_AUTOMATED_OPERATION_DESIGN.md` (design) ·
`docs/MVP2_TRACK_A_P0_DRYRUN_REPORT.md` (dry-run + findings) ·
`docs/mvp2/TRACKA_1489371_A3A4_RUNSHEET.md` (match-day procedure) ·
GO/NO-GO §4b (Track A ops checklist) · tools `scripts/mvp2_ops.py` / `scripts/mvp2_ops_queue.py`.

## ★ Prior handoff state — MVP-2 small private trial（closed 2026-06-11, superseded by the section above）

**Owner verdict: PASS WITH CONDITIONS for small private trial.** This thread is closed for feature
work; the next thread starts from trial feedback, not from code.

```text
Frozen state:
  branch feature/mvp2-api-football-ingestion @ d03fdf5 (de-model customer voice) · PR #3 Draft/OPEN ·
  main untouched (e372616) · build PASS · narrative guard 36/36 + trial 8/8 + rescore 4/4 PASS ·
  customer visible-copy scan 10/10 PASS (scripts/check_customer_visible_copy.py) · vi visible Han=0 ·
  betting/guarantee wording 0.
Trial scope (hard): internal operators · a few trusted fans · ONE private test group ·
  Mexico vs South Africa (1489369) only · send window closes at kickoff 2026-06-11 19:00 UTC ·
  NO public launch · NO payment/token/public subscription.
Live URLs: home https://worldcup2026-izid.onrender.com/ (HTTP 200, trial shell live);
  deep links /predict/1489369 · /predict/1489371 · /recap/855737 · /recap/979139 = HTTP 404 direct
  (Render dashboard SPA rewrite STILL PENDING — render.yaml rule exists; in-app navigation from home works).

Product path: Home → 俅哥战术室 (/predict/1489369) → 俅哥临场30分钟修正 (#rescore) → 入群 CTA → feedback.
Core product hypothesis: users join NOT for a prediction result, but because they want the
  30-minute-before-kickoff re-check once lineups and late variables appear.

Trial docs (new, docs/mvp2/): TRIAL_SEND_PACKAGE.md (zh/vi messages, teaser, screenshot rec,
  30-min template, stop rule, operator say/don't-say) · TRIAL_FEEDBACK_FORM.md (fan/operator/
  compliance questions) · TRIAL_GO_NO_GO_CHECKLIST.md (pre-send / 30-min / stop / feedback /
  PASS·PASS-WITH-ISSUES·FAIL·BLOCKED decision).

Known weaknesses (carry into next sprint):
  - brand naming still needs final unification (俅哥说球 zh vs Giành Cup global vs LEIZE hierarchy);
  - vi persona name (Tiên Tri Bóng Đá) still temporary — needs Owner/operator confirmation;
  - some "AI" remains in global brand/footer/legacy internal places (allowed zones, but unify later);
  - public launch still paused; payment/token untouched;
  - 30-minute rescore is a MANUAL pipeline rerun (mvp2_generate_rescore_models.py), not scheduled automation;
  - SPA rewrite may still require Render dashboard operation (deep links 404 until then);
  - /predict/2026-brazil-argentina (hypothetical sample, out of trial scope) still uses pre-de-model wording.

Next heavy engineering direction: feedback-driven Product Trial Iteration Sprint.
```

**Next Engineer Start Command（copy-paste）**

> Start by reading CLAUDE.md, docs/MVP_STATUS.md, docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md,
> docs/mvp2/TRIAL_SEND_PACKAGE.md, docs/mvp2/TRIAL_FEEDBACK_FORM.md,
> docs/mvp2/TRIAL_GO_NO_GO_CHECKLIST.md, and the latest screenshots in
> docs/qa_screenshots/mvp2_june11_trial/. Do not start coding. First summarize trial feedback,
> classify issues into copy / product flow / data / LLM prompt / guard / deployment, then propose
> the next heavy engineering sprint.

## ★ 2026-06-11 (latest) — June 11 Real Match Trial Prediction Sprint: SHIPPED (Owner trial-send review)

De-Modeling sprint (same day, Owner: customer voice cleanup): visible customer copy now speaks ONLY as
the persona — no 模型/mô hình/盲区/AI/ScoutScore/process words on /, /predict/*, /recap/* (zh+vi).
Regenerated v2 narratives (trial 4 + recap 4 + rescore 4, voice=qiuge_v2/tientri_v2; guard hard-bans
model/process words for v2 files; scoreline = 俅哥给出的赛前参考区间 / khoảng tham khảo trước trận).
UI labels: 赛前参考区间/冷门风险/参考 badge/俅哥赛前抓对了什么/Tiên Tri dict layer de-AI'd (header/ticker/
caps/hero). NEW scripts/check_customer_visible_copy.py: headless DOM scan of 10 surfaces, strips
details-folds/footer/EN-line, fails on model/process words — 10/10 PASS. Guard 36/36 + trial 8/8 PASS.
Two label-only post-edits recorded in internal_notes (「AI 观点」->「俅哥观点」; rescore 盲区 word swap).

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
