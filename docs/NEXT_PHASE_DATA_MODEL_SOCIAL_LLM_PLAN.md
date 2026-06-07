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
