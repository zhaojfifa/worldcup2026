# MVP-2 — Evidence Board v2 Gate Spec (DRAFT)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Status:** **DRAFT boundary-freeze — NOT an implementation authorization.** Pairs with
> [MVP2_EVIDENCE_BOARD_V2_DESIGN](MVP2_EVIDENCE_BOARD_V2_DESIGN.md). It defines *where a future v2 implementation
> may and may not go*, and the bar it must clear. **Implementation status (2026-06-10): Owner GO granted (Path A) —
> minimal additive implementation built (`/evidence/855737`, zh/vi); acceptance criteria §8 met (build PASS, vi Han=0,
> every conclusion has source_refs or assumption flag, additive-only, no vendor ref); review PASS WITH ISSUES (internal).
> Operation paused, PR #3 Draft; operator real-device review + commit-to-Draft Owner-pending; backend `/evidence/{id}` not built this cut.**

---

## 1. Allowed files / paths (future implementation may touch — ADDITIVE only)
- **Frontend pages:** `frontend/src/pages/RecapDetailPage.tsx` (exists), an upgraded `DetailPage.tsx` **or** a new
  `EvidenceBoardPage.tsx`; `frontend/src/App.tsx` (add route only).
- **Frontend components:** new `frontend/src/components/` cards (e.g. `EvidenceCard`, `FactorCard`,
  `AiBoundaryCard`, `MissingDataCard`) — additive.
- **Frontend data/i18n/style:** `frontend/src/data/recapData.ts` + new evidence data module;
  `frontend/src/i18n/{dict,viMapping,mmMapping}.ts` (new labels); `frontend/src/styles/global.css`.
- **Backend (read-only, server-side proxy):** `backend/app/routers/recap.py` + a new
  `backend/app/routers/evidence.py`; `backend/app/services/scoutscore/*` (new view builders);
  `backend/app/main.py` (mount only).
- **Docs / QA:** `docs/MVP2_*`, `docs/data_audit/*` (additive samples), `docs/qa_screenshots/*`, `scripts/qa/*`.

## 2. Forbidden files / paths (must NOT change)
- **Home prediction MAIN logic** — the today-signal card, today-matches simrow, upset-TOP3 core in
  `HomePage.tsx` may only be **read/linked**, never re-architected. Bridge/links are additive only.
- **Payment / Token:** no unlock-to-pay flow, no `tokens`/wallet changes for v2, no on-chain.
- **Day-4 vendor connector** `backend/app/services/data_sources/api_football.py` — do not disturb.
- **No direct API-FOOTBALL call from `frontend/`** (grep `api-sports|apisports|v3.football|API_FOOTBALL` must stay empty).
- **No injuries second-source integration**; **no real LLM auto-publish / production provider call** without Render verification.
- **No secrets** (`.env`, keys) committed or printed; **no raw vendor payload** committed.
- **No hand-written product narrative in templates** (2026-06-10 rule): the customer narrative / judgement /
  recap / operator copy / zh+vi must be **LLM-generated** (DeepSeek/Gemini) per `MVP2_LLM_NARRATIVE_CONTRACT.md`;
  engineering may define schema / prompts / guards / rendering only; mock is allowed ONLY as a marked fallback
  (`llm_provider=mock`). No engineering string-concatenated football analysis.

## 3. UI zones (fixed)
- **First glance:** customer-language verdict / AI lean + confidence **tier** (no %); never a table first.
- **Evidence band (screenshot zone):** evidence cards (possession/shots/keeper) + (recap) MISS badge + operator copy.
- **Source ledger:** always present, **collapsed** at the foot (`<details>`).
- **Raw Scout Pack:** **collapsed**, secondary.
- **AI boundary / missing data:** always visible (allowed vs forbidden fields; injuries = source required).
- **Language:** `?lang=` + top bar `CN · VI · MY`; vi Han=0; mm→English.

## 4. Data sources (backend only)
- ScoutScore v0.1 artifacts (`mvp2_feature_snapshots`, `mvp2_model_notes`, `mvp2_prediction_replay`,
  `mvp2_prediction_accountability_reports`); served via backend.
- **Frontend fetches backend endpoints only** (mock in `VITE_USE_MOCK`); never the vendor.
- Future data (injuries/xG/Elo/form/squad value) only after Owner GO; until then rendered as honest gaps.

## 5. API contracts
- **Exists:** `GET /api/v1/recap/{fixture_id}?lang=zh|vi` → RecapContent (zh/vi; en/mm → 404 → frontend bundled).
- **Proposed (v2):** `GET /api/v1/evidence/{fixture_id}?lang=` → board payload (AI lean tier, factors[w/ source_refs],
  evidence cards, missing_evidence, ai_allowed/ai_forbidden). Read-only; no auth for historical public-safe data;
  internal/preview stays admin-token gated. **No write endpoints. No payment endpoints.**

## 6. i18n requirements
- **vi Han = 0** (verified by scan); **mm → English** fallback (never Chinese); zh internal; en system fallback.
- Confidence rendered as tier + stars only; **no numeric probability / no `42.2%`**.

## 7. Screenshot requirements (per surface, before any PASS)
- zh + vi full-page captures for every new surface → `docs/qa_screenshots/...`.
- Checks: vi Han=0 · no betting/odds/market/盘口/竞猜/投注 · no `42.2%` · evidence + source ledger visible.

## 8. Acceptance criteria (implementation gate)
1. `npm run build --prefix frontend` PASS; `git diff --check` CLEAN; backend route/contract checks PASS.
2. **vi Han=0**; forbidden-wording scan clean (customer-facing).
3. **Every conclusion has `source_refs` or an `assumption` flag.**
4. **No** fake probability · SHAP · xG · injuries inference · fake archived prediction.
5. Home prediction MAIN logic unchanged (diff shows additive only).
6. Frontend has **no vendor reference**.
7. zh + vi screenshots captured; **operator review PASS** recorded.
8. `public_ready=false` until full sign-off; no payment/Token/public launch.

## 9. Rollback conditions
- Any guardrail breach (forbidden wording, vi Han>0, fake data, fake archived prediction, vendor leak) → **revert
  the v2 surface** (it is additive + behind existing pages; the route can be unmounted/hidden).
- Operator review = FAIL → hold at design; do not ship.
- Because v2 is additive and `public_ready=false`, rollback is "unmount route + revert commit" — no data/payment to unwind.

## 10. Owner approval required before implementation
- **This draft is NOT approval.** A v2 build starts only after an explicit Owner GO that confirms: scope (which
  core pages), confidence representation (Q1), recap matrix (Q2), CTA landing (Q3), and that operation stays paused.
- Until GO: **no runtime code, no frontend/backend change, PR #3 stays Draft, no merge, no public operation.**

## Guardrails honored (this doc)
draft spec only · no implementation · additive-only boundary · no payment/token/public · odds/betting excluded ·
injuries source-required · vi Han=0 rule · external operation paused · PR #2 untouched · PR #3 Draft.
