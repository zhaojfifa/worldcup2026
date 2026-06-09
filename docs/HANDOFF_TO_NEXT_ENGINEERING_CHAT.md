# Giành Cup Engineering Handoff

_Snapshot for the next Claude engineering chat. Read `CLAUDE.md` first, then this._
_Version: **MVP v0.8** · origin/main synced · multilingual + real data/model/LLM-draft phase._

> **Fast Real Data Gate (2026-06-09):** baseline **tag `v0.8-real-data-gate`** (`d4feb6c`) pushed.
> **Do NOT extend selected matchup mapping** (Mexico/SA, Brazil/Egypt, Argentina/Honduras) — intentionally
> blocked until the Render sync confirms a real `match_id` (avoids second-seed/fake-real). Next execution =
> operator Fast Gate: friendlies `10/2026` → WC `1/2026` → WC `1/2022`, then `/matches` → `match_id` →
> `/refresh`; fill `DATA_SOURCE_SYNC_VERIFICATION.md` §13. If none return real matches → mark `blocked`,
> return to Owner, do not fabricate.

> **Harness-X Real Match Intelligence Sprint (2026-06-09): real fixtures selected (docs-only).** Recon
> (web sources) picked **upcoming Mexico v South Africa** (WC opener 06-11) + **finished Brazil 2-1 Egypt /
> Argentina 2-0 Honduras** (June friendlies). `api_available=unknown` → **`BLOCKED_OPERATOR_RENDER_SHELL`**
> (Claude has no token; sync NOT run or faked). `model_status=pending_api_sync` (no fake numbers); vi copy
> human-authored (no Chinese/betting). Operator: run the league=10/1 sync on Render, then `/matches` →
> `match_id` → `refresh`, fill `DATA_SOURCE_SYNC_VERIFICATION.md` §12 + `REAL_MATCH_MODELING_REVIEW.md`.
> Real matches not yet in the app → operator screenshots pending. Docs:
> `REAL_MATCH_INTELLIGENCE_SELECTION.md`, `REAL_MATCH_MODELING_REVIEW.md`, `VI_REAL_MATCH_OPERATION_COPY.md`.

> **Harness-X Vietnam Market Heavy Sprint (2026-06-08): PLAN only, Owner review pending** — do NOT start
> coding until approved. 3 roles (Engineering data/modeling · Product flow · Operation vi screenshots);
> vi first; **warm-ups/friendlies first data** (`league_id=10,season=2026`); **no backend/API/DB change
> proposed**; prediction-game/entertainment framing (not betting). Key risk flagged: seed-keyed
> viMapping/mmMapping → real matches use generic fallback + LLM drafts (human review). Plan:
> `docs/HARNESSX_VIETNAM_MARKET_HEAVY_SPRINT_PLAN.md`; operator template: `docs/VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md`.

> **Brand (2026-06-08): LEIZE = company brand · Giành Cup = product (under LEIZE AI) · "Cloud" = future
> branch, not the company brand.** No product rename, no code change. See
> `docs/BRAND_ARCHITECTURE_LEIZE_GIAND_CUP.md`.
> **Real Data Calibration (2026-06-08, Owner GO):** `admin/sync/{fixtures,results}` already accept optional
> `?league_id=&season=` (default WC 1/2026) → **no code/DB change needed**. First pick La Liga (140),
> fallback friendlies (10) / WC-2022 (1/2022); operator-run on Render (not fabricated). Runbook:
> `docs/REAL_DATA_CALIBRATION_PLAN.md`. Any DB schema change (competition/source fields) = Owner-gated.

> **Latest (2026-06-08): Scout Intelligence Rewrite shipped (frontend-only).** Report/Detail now show an
> Evidence Strip, Scout verdict + hook, factor Source/Impact/Interpretation, Contrarian + Watch — all
> frontend-derived (dict + viMapping/mmMapping), **no API/DB change**, vi/mm 0 Han, draft-only LLM
> unchanged. **Engineer self-verify PASS; Stage 5 operator real-device verification PENDING**
> (checklist: evidence doc §4; `operator_verification_status: pending`; shots →
> `docs/qa_screenshots/intelligence_rewrite_operator/`). **Final PASS not granted until operator
> screenshots reviewed + `final_owner_decision` recorded.** See
> `docs/SCOUT_INTELLIGENCE_REWRITE_EVIDENCE.md` + `docs/qa_screenshots/intelligence_rewrite/`.

---

## 1. One-page summary

- **State:** Giành Cup MVP v0.8 — multilingual (zh/en/vi/mm) UI is **language-gate CLOSED & QA-PASS**;
  a **draft-only LLM** copy endpoint exists; data/model are **real-capable but still on seed
  (`mock_mode=true`)**; Myanmar **Telegram is active**, Vietnam **Zalo pending**.
- **Next chat's first goal:** deploy latest `main`, then **(operator) true-device retest of the
  Telegram open/copy fallback + send the 3 Burmese trial messages**, and **verify the real LLM draft
  call on Render** (`AI_PROVIDER=deepseek|kimi` + key). Do NOT start new features; finish the
  operate/verify loop. LLM production beyond draft-only / payment / bot / scaling are **Owner-gated**.

---

## 2. Product & language state

- **Brand:** Giành Cup · 2026 World Cup AI Football Intelligence Community (Vietnam-first SEA).
- **Language roles:** `vi` primary customer · `mm` secondary customer · `zh` internal China-team
  management · `en` system/fallback/API/admin/schema. **vi/mm fall back to English, never Chinese.**
- **Currency by locale:** zh RMB · en USD · vi VND(₫) · mm MMK(Ks). No RMB shown to vi/mm customers.
- **Switcher:** header `CN · VI · MY`; persists in `localStorage giandcup_lang`; `?lang=` param honored.
- **Verify URLs:** `/?lang=vi` · `/?lang=mm` · `/community?lang=mm` · `/report?lang=mm` · `/detail?lang=mm`.
- **i18n code:** `frontend/src/i18n/{useLocale,dict,viMapping,mmMapping,pricing}.ts`,
  `frontend/src/copy/{zh,en,vi,mm}.ts`. `.lang-mm` density profile in `global.css` (Burmese is longer).

## 3. Deployment / environment

- Frontend: https://worldcup2026-izid.onrender.com · Backend: https://worldcup2026-api-71n6.onrender.com
- DB: Render PostgreSQL (local dev = SQLite). R2 bucket `giand-cup-assets` (configured; `/assets/status` ok).
- **Render env is the source of truth for secrets** (`ADMIN_API_TOKEN`, `API_FOOTBALL_KEY`,
  `DEEPSEEK_API_KEY`/`KIMI_API_KEY`, R2_*). **Local does NOT need real keys** — LLM falls back to
  human templates; admin routes are 401 locally without a token.
- Local QA dev server: `npm run dev --prefix frontend`; screenshot helper `scripts/qa/lang_mobile_shots.sh`.

## 4. Social status

- **Myanmar Telegram ACTIVE:** `https://t.me/GianhCupMMAIFootball` (live `GET /social/channels` →
  telegram `status=active`, `public_url` set).
- **Operator reported `ERR_CONNECTION_REFUSED`** opening t.me in a mobile in-app browser → fixed with
  a **community open/copy fallback sheet** (Open Telegram / Copy link / hint; uses API `public_url`,
  still tracks `click_social_channel`). Needs operator **true-device confirmation after deploy**.
- `events/track` + `community/heat` verified earlier (clicks need `match_id` to register).
- **Vietnam Zalo pending active** — operator sets it via `POST /admin/social/channels/upsert` (Render Shell).

## 5. Data status

- Last known `GET /api/v1/data-source/status`: `api_football_configured=true`, `connector_status=ok`,
  **`mock_mode=true`**, `requests_used=0`. `performance/summary` all 0 / `hit_rate=null`.
- **Real sync is operator-only (Render Shell, `$ADMIN_API_TOKEN`); Claude has no token → do NOT fake it.**
  ```bash
  curl -X POST .../api/v1/admin/sync/fixtures -H "x-admin-token: $ADMIN_API_TOKEN"
  curl -X POST .../api/v1/admin/sync/results  -H "x-admin-token: $ADMIN_API_TOKEN" -d '{"league_id":1,"season":2026}'
  curl .../api/v1/data-source/status   # expect mock_mode=false, requests_used>0 after a real pull
  ```
  Details: `docs/DATA_SOURCE_SYNC_VERIFICATION.md`.

## 6. Modeling status

- `POST /matches/{1,2,3}/refresh` verified: win_prob sums to **100**; m1 high/conf61, m2 low/conf80,
  m3 low/conf86; **response shape unchanged**. Details: `docs/MODELING_BASELINE_VERIFICATION.md`.
- **Allowed operating language:** AI viewpoint / risk signal / pre-match update.
  **Forbidden:** real hit-rate / guaranteed accuracy / betting language (no settled results yet).

## 7. LLM status

- **Draft-only** admin endpoint: `POST /api/v1/admin/llm/generate-copy` (x-admin-token) →
  `{generated_text, provenance, data_mode, warnings, forbidden_hits, status:"draft_only", publishable:false}`.
  Body: `{match_id, language: vi|mm|zh|en, copy_type: preview|upset|live|recap}`.
- Providers: **DeepSeek / Kimi** (via `AI_PROVIDER` + key). Local/`mock` → **human-template fallback**.
  Forbidden-phrase filter (zh/vi/mm/en, allows negations). `AI_PROVIDER=mock` = instant rollback.
- **Real provider call NOT yet verified on Render** — see `docs/LLM_RENDER_VERIFICATION.md` for the steps.
- **No auto-publish, no DB write, no payment, no bot.** Code: `backend/app/services/llm/*`,
  `backend/app/routers/llm.py`. Plan: `docs/LLM_REAL_INTEGRATION_PLAN.md`.

## 8. QA lessons (do not repeat)

- **`/detail` alone was insufficient** — the real residual was on the **`/report`** page reached via
  detail → unlock. Always QA the **full detail → unlock → report flow**.
- **Screenshot-driven QA is mandatory** for customer-facing language/mobile. **No screenshot = no PASS.**
- **Static DOM scan is NOT enough — interaction states leak too.** The operator hit a **Chinese unlock
  modal** on mm (`已解锁，可直接查看完整报告` / `继续查看报告`) that every static scan missed because the
  modal/toast/action-sheet were never opened. Source: `Modal.tsx` hardcoded button + `DetailPage` showing
  the store/API `res.message` (Chinese) as the body. **Always QA modal / toast / unlock dialog / action-sheet
  states** (helper `scripts/qa/lang_interaction_shots.mjs` clicks into them and captures). Fixed via i18n
  `unlockedBody`/`unlockFailedBody`/`continueToReport`; never render raw store/API message text.
- **Telegram direct-open may fail in mobile WebViews; Copy Link is the accepted operating path** — do not
  block the trial on direct-open (ruling: PASS WITH ISSUES). The open/copy fallback sheet is localized.
- **vi recheck (2026-06-08, Myanmar standard):** full vi path incl. `/report` re-scanned; residual was the
  **community "VI TRIAL COPY" badge** leaking Chinese (`越南语试跑文案已就绪`) on the public page — the
  bilingual zh·vi badge that mm had already been switched to English. **Lesson:** operator-labelled badges
  on public customer pages still count as customer surface — vi must be Chinese-free. Fixed: `dict.ts` VI
  `viBadge` → Vietnamese-only.
- Recheck artifacts: `docs/qa_screenshots/mm_mobile_recheck/`, `docs/qa_screenshots/vi_mobile_recheck/`,
  `docs/qa_screenshots/lang_interaction_recheck/` (+ `mm_mobile/`, `vi_mobile/`). Reports:
  `docs/MM_MOBILE_QA_REPORT.md`, `docs/VI_MOBILE_QA_REPORT.md`, `docs/VI_MOBILE_RECHECK_REPORT.md`,
  `docs/LANG_INTERACTION_RECHECK_REPORT.md`.

## 8b. LLM provider comparison + Mini-Agent (2026-06-08)

- **`provider_override`** on `POST /api/v1/admin/llm/generate-copy` (admin, draft-only, backward compatible):
  `deepseek|kimi|gemini`; unknown/unavailable → human-template fallback with warning. Providers in
  `client.py`: deepseek/kimi (OpenAI-compatible) + gemini (generateContent, `thinkingBudget=0`).
- **Real 3-provider comparison run locally** (provider keys already in the dev `.env`, **pre-existing**;
  **never printed/committed**; all draft-only). Empirical finding (contradicts assumed "Kimi primary"):
  **DeepSeek + Gemini are clean for vi/mm (0 Han, compliant); Kimi leaks full Chinese for vi/mm.**
  → **Use DeepSeek (primary) / Gemini (benchmark) for vi/mm; not Kimi yet.** `forbidden_hits=[]` everywhere,
  but note **compliant ≠ correct-language** → add a Han-ratio language-fidelity check at review.
- **Mini-Agent Harness:** lightweight **design only** (8 stages, `docs/MINI_AGENT_HARNESS_DESIGN.md`); no
  runtime built. Stages 2/6/7 already exist in code; 3–5 are prompt drafts.
- **Data-first:** Operator Action Checklist in `docs/DATA_SOURCE_SYNC_VERIFICATION.md` §11 (operator runs
  real fixtures/results/performance sync on Render — **not fabricated**; data still seed until then).
- Reports: `docs/LLM_PROVIDER_COMPARISON_REPORT.md`, `docs/LLM_DRAFT_COPY_REVIEW_LOG.md` (Batch 2 = real).
  `backend/scripts/llm_draft_verify.py` is a **manual** helper (no make/npm target, by Owner ruling).

## 9. Harness-X rule set

- **Self-validation OK:** L0/L1 (read-only checks, docs, small frontend copy/mapping with screenshots).
- **Owner decision required (blocked transitions):** LLM production beyond draft-only · bot auto-publish ·
  payment · deployment scaling · API-shape change · DB-schema expansion · release decisions.
- **Required artifacts:** screenshots for UI PASS; real curl output (never fabricated) for API/data;
  docs updated every round. **Docs are the source of truth, not chat memory.**

## 10. Immediate next actions

1. **Deploy latest `main`** to Render (frontend + backend).
2. **Operator:** true-device retest of the Telegram open/copy fallback (`/community?lang=mm`).
3. **Operator:** send the 3 Burmese trial messages (`docs/MM_OPERATION_TRIAL_MESSAGES.md`); record in
   `docs/OPERATION_TRIAL_RESULTS.md` (no fabricated metrics).
4. **Operator (Render Shell):** run real `admin/sync/fixtures` + `admin/sync/results`; paste counts into
   `docs/DATA_SOURCE_SYNC_VERIFICATION.md`.
5. **Verify the Render LLM draft endpoint** with `AI_PROVIDER=deepseek|kimi` + key; record in
   `docs/LLM_RENDER_VERIFICATION.md`.
6. **Activate Vietnam Zalo** when a real link is available (admin upsert), then run the vi trial.

## 11. Hard rules (carry forward)

- Standard path `/Users/jackie/code/worldcup2026` (NOT `wordcup2026`).
- Never change `/matches`, `/matches/{id}`, `/reports/{id}` response shapes. New capability → new
  endpoint + token-protected admin writes. Graceful degradation when API-FOOTBALL/R2/LLM unconfigured.
- Never log/commit secrets; never commit `.env*` / `.db`. Keep `VITE_USE_MOCK` dual mode working.
- Forbidden wording + mandatory disclaimer + MTC statement (CLAUDE.md). vi/mm never fall back to Chinese.
- **git:** committer is machine-inferred (user.name/email unset). Do **not** amend/force-push;
  recommend human run `git config user.name "Jackie"` / `git config user.email "zhaojifa@gmail.com"`.
