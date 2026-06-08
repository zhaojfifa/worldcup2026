# Giành Cup · Next Phase Plan — Data / Modeling / Social / LLM Closed Loop

_Created: 2026-06-07 · Baseline: MVP v0.7, multilingual (zh/vi/mm + en fallback) QA PASS._

Language work is now closed (vi & mm screenshot-QA PASS, isolation verified). This plan opens the
next phase. **No backend change, no API shape change, no payment, no bot, no UGC, no direct LLM
production** is authorized by this document — it is a plan and gating spec only.

Compliance floor stays: 不做博彩 · 不承诺命中/收益 · MTC 仅平台积分（不可提现/转让/交易）·
排行榜非收益榜 · vi/mm 客户侧不回退中文.

---

## 1. Data closed loop

| Step | Endpoint / action | Notes |
|------|-------------------|-------|
| Fixtures sync | `POST /admin/sync/fixtures` (Render Shell, `$ADMIN_API_TOKEN`) | Upsert by api_id/external_id; no dup inserts |
| Results sync | `POST /admin/sync/results` `{league_id,season}` | Pulls finished fixtures from API-FOOTBALL, upserts `MatchResult`, auto-settles |
| Performance settlement | `GET /performance/daily`, `/performance/summary` | Track record after real results |
| mock/real boundary | `GET /data-source/status` | Currently `mock_mode=true` (key set, no live pull yet) |
| Data-credibility marker | UI must show "mock/demo" vs "real" provenance | **Do not present mock numbers as real accuracy** |
| Admin trigger commands | documented in `docs/OPERATIONS_RUNBOOK.md` | Render Shell only; token never printed |

**Exit:** one real fixtures+results sync run in prod (or a conscious documented decision to stay
on seed for the trial), with a clear mock-vs-real label in the UI/data.

## 2. Modeling closed loop

- **Baseline predictor** (current): rules model; `POST /matches/{id}/refresh` recomputes;
  win-prob normalized to 100 (verified). `risk_note` is rule/seed text.
- **Near-term enhancements** (additive, no API shape change): better feature weights, calibrated
  confidence, richer `risk_note` generation rules.
- **Hard rule:** **do not advertise real hit-rate / accuracy until real results have been
  back-filled** and a track record exists. Until then everything is "AI viewpoint", not a promise.

## 3. Social closed loop

- Configure **active Zalo / Telegram** via `POST /admin/social/channels/upsert` (Render Shell).
  **This is the current operational blocker** for both vi and mm trials.
- `click_social_channel` events **must carry `match_id`** to register in `community/heat`.
- Run **per-language trials** (vi to Vietnamese groups, mm to Myanmar groups) using
  `OPERATION_TRIAL_MESSAGES_VI.md` / `MM_OPERATION_TRIAL_MESSAGES.md`.
- Record operator feedback + metrics in `OPERATION_TRIAL_RESULTS.md`.

## 4. LLM prep (NOT full build)

- **No direct LLM production wiring this phase.** Day-8-prep deliverables only:
  - Prompt schema design.
  - **Banned-word output filter** (zh + vi + mm) — must run before any generated text ships.
  - vi/mm copy-generation guard (English fallback, never Chinese on customer side).
  - Human review queue for generated copy.
  - Output field schema: `reason_bullets` / `social_copy` / `recap_copy` / `risk_copy`.
- LLM **Full Build** gate: ≥1 real trial done + active social承接 + human feedback samples +
  stable banned-word filter.

## 5. Deployment resource plan

- **Current Render Starter is sufficient for the MVP / language trial.**
- Re-evaluate scaling **only after** a real operation trial begins. Scale-up triggers:
  - API latency rising under load.
  - Traffic growth.
  - LLM request load introduced.
  - Image / share-card generation introduced.
  - R2 content-asset growth.

## 6. Go-live gate (all must hold)

1. vi & mm mobile QA **PASS** (✅ done 2026-06-07).
2. ≥1 **active** social channel (Zalo first). ⛔ outstanding blocker.
3. Data source verified (fixtures/results sync run or documented mock decision).
4. Admin sync flow documented (`OPERATIONS_RUNBOOK.md`). ✅
5. Compliance scan clean (zh/vi/mm forbidden words; MTC statement; disclaimers). ✅
6. One small operation trial completed with recorded feedback. ⛔ pending active channel.

**Current status:** language gate cleared; **next action = stand up an active Zalo/Telegram
channel**, then run the small-traffic vi/mm trial. LLM stays in prep until the gate is met.

---

## 7. Harness-X progress (2026-06-08, L1 + P-flow Prep)

| Track | Status | Reference |
|-------|--------|-----------|
| Data source verification | ✅ PASS WITH ISSUES — connector ok, `mock_mode=true`, 0 settled | `DATA_SOURCE_SYNC_VERIFICATION.md` |
| Modeling refresh verification | ✅ PASS — win_prob=100, refresh ok | `MODELING_BASELINE_VERIFICATION.md` |
| vi/mm copy library | ✅ built | `OPERATION_COPY_LIBRARY_VI_MM.md` |
| LLM prep schema + guardrails | ✅ design only (no prod) | `LLM_PREP_SCHEMA_AND_GUARDRAILS.md` |
| Social — Myanmar Telegram | ✅ **active (live-verified)** | `OPERATION_TRIAL_RESULTS.md` |
| Social — Vietnam Zalo | ⏳ pending active | `OPERATION_TRIAL_RESULTS.md` |
| LLM Full Build | ⛔ Owner-gated | — |

**Go-live gate update:** items 1,4,5 met; #2 = **Myanmar trial can dispatch now (Telegram active)**;
Vietnam trial pending Zalo. Real data sync (#3) is an operator decision. Owner decisions outstanding:
(a) run real data sync now or stay seed; (b) activate Zalo; (c) approve LLM Full Build (later).

## 8. Data+Model formalization (2026-06-08, bounded L2-lite, NO scaling)
- **Modeling:** matches 1/2/3 refreshed — all `win_prob` sum 100; m1 high/conf61, m2 low/conf80,
  m3 low/conf86; **API shape unchanged**. vi/mm/en note maps extended for the refreshed low-risk
  `risk_note`. Copy library filled from real model output (AI-viewpoint only). PASS.
- **Data:** `mock_mode=true` still; **real `admin/sync/*` is BLOCKED for Claude** (token only in
  Render Shell) → operator must run it. Until then no real hit-rate may be advertised.
- **Social:** Myanmar Telegram `active` (verified) → 3 mm messages `ready_to_send`; Vietnam Zalo pending.
- **LLM:** prep only (mapping / review queue / fallback / rollback designed); Full Build Owner-gated.
- **No** resource scaling, payment, bot, API/DB schema change.
- **Owner actions outstanding:** (a) run real data sync in Render Shell; (b) activate Zalo;
  (c) dispatch the Myanmar trial + record feedback; (d) approve LLM Full Build later.

## 9. Real LLM integration — DRAFT-ONLY (2026-06-08, Owner GO WITH CONDITIONS)
- Built `backend/app/services/llm/*` + admin endpoint `POST /api/v1/admin/llm/generate-copy`
  (x-admin-token, `status:draft_only`). DeepSeek/Kimi client + forbidden-phrase filter (zh/vi/mm/en)
  + human-template fallback; `AI_PROVIDER=mock` rollback. Output: reason/risk/social(vi,mm)/recap.
- **Conditions enforced:** draft-only (no auto-publish), human review gate, no DB write, no payment,
  no bot, no scaling, no public API-shape change. `httpx` already present (no new dep).
- **Pending (ops):** set `AI_PROVIDER=deepseek|kimi` + key on Render to exercise the real call;
  then human-review drafts before manual send. LLM **Full auto-publish remains NO-GO**.
- Plan/details: `docs/LLM_REAL_INTEGRATION_PLAN.md`.

## 10. Social link UX fix + Report localization (2026-06-08, BLOCKED_STATE_DIVERGENCE)
- Operator real-device feedback: Telegram `ERR_CONNECTION_REFUSED` + mm detail Chinese residual.
- Fixed: **Report page localized** (zh/vi/mm/en; the true residual — never localized before) and a
  **Telegram open/copy fallback sheet** added (uses API `public_url`, still tracks click_social_channel).
- Screenshot-verified; `docs/MM_MOBILE_QA_REPORT.md` (recheck, PASS WITH ISSUES). No backend change.
- Social trial can continue after deploy; operator confirms Telegram open via copy path on device.

## 11. Handoff scribe (v0.8, 2026-06-08)
Context handed off — see `docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md` (one-page + next actions) and
`CLAUDE.md` (state/Harness-X/blockers). Pending owner/operator items: real data sync (Render Shell),
real LLM call on Render (`docs/LLM_RENDER_VERIFICATION.md`), Telegram true-device retest, Zalo activation.
No new feature code this round; docs-only scribe pass.

## 12. LLM draft-only verification (2026-06-08, Owner GO — draft-only)
Owner ruling: **link the real LLM for copy optimization, but draft-only — no auto-publish.** Status:
- **Local verification done** (`backend/scripts/llm_draft_verify.py`, mock→fallback): contract
  (`draft_only`/`publishable=false`), auth gate, and forbidden filter (dirty caught; clean + negation
  allowed) all PASS. Backend harden: vi/mm/en drafts use English team names (zh Chinese).
- **Real DeepSeek/Kimi call on Render remains operator-pending** — Render holds the LLM env/keys; local
  needs no real key; Claude has no token and does **not** fabricate a provider result.
- LLM output stays **draft-only + human-review-required**. Auto-publish / payment / bot / scaling remain
  **NO-GO**. Drafts: `docs/LLM_DRAFT_COPY_REVIEW_LOG.md`; candidates: `docs/OPERATION_COPY_LIBRARY_VI_MM.md`.
