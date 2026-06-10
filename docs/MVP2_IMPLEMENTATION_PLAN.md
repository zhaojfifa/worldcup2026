# MVP-2 Implementation Plan (Pre-match Scout Pack)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only.
> Trigger: **API-FOOTBALL Real Run = PASS** (WC2022=64, **WC2026=72**, Level-2 core ✓; injuries unresolved).
> Architecture: [MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE](MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE.md). **No app code changed
> this round** — this is the build sequence for a *separate* implementation PR.
>
> **Hard rules for implementation:** frontend never calls the vendor (backend proxy only) · no token/large payload
> committed · no fabricated data · no Level-0 AI deep explanation without data · odds excluded · StatsBomb
> non-commercial (offline) · external operation paused until Operator Review passes.

---

## Phase 0 — Data Contract
- **Evidence Board v2 schema** (architecture §5): one read model; every leaf is `Field<T>` =
  `{ value, available, source, last_checked_at, confidence, license_status, fallback_text }`.
- **`source_ledger` envelope:** per-field provenance + `license_status` ∈ {ok, non_commercial, pending, excluded}.
- **Fallback behavior:** `available=false` → render localized `fallback_text` (e.g. "首发未接入 / source required");
  `license_status ≠ ok` → hidden from customer UI; `ai_explanation` may only cite `available && license_status=ok` fields.
- **Exit criterion:** contract reviewed + approved (Owner) before any backend build. *(deliverable: a JSON-schema doc / TS types)*

## Phase 1 — Backend Prototype
- **Backend proxy** (server-side token; **no frontend vendor direct call**) + Redis cache + `source_request_log`.
- Ingestion endpoints (read-only, cached): **fixtures · lineups · events · statistics · fixture players · coach**
  (+ squad/teams). Each writes to its schema table with `last_checked_at` + source.
- **Budget guard:** 429 backoff (already in the verifier) + request budget; post-match → frozen snapshot.
- **Exit criterion:** match 8 & 13 full packs ingested into the prototype store (no UI), within request budget.

## Phase 2 — Entity Mapping
- `Render match_id ↔ API-FOOTBALL fixture_id` (proven: 8↔855737, 13↔855741, 58↔977345, 67↔979139).
- `Kaggle match result ↔ API-FOOTBALL fixture` (date + canonical team pair; 64/64 already aligned offline).
- **canonical team / player / coach IDs** + `source_*_mapping` with `confidence` + `manual_review_required`.
- **Exit criterion:** every ingested field resolves to a canonical entity; mismatches flagged, not silently joined.

## Phase 3 — Feature Snapshot
- Compute `scout_feature_snapshot` (architecture §4, field sources only — **no model algorithm yet**):
  `lineup_features` · `coach_features` · `formation_features` · `event_context` · `statistics_context` ·
  `missing_evidence` · **`injuries_unresolved` flag** (until injuries resolved).
- Each feature carries `inputs_ref`; any missing required input → feature = `missing` (never AI-guessed).
- **Exit criterion:** match 8 & 13 produce a real feature snapshot with honest `missing` markers.

## Phase 4 — Frontend Evidence Board v2
- **Only after the Phase-0 data contract is approved.** Replace Level-0 surfaces with the provenance-driven board.
- **No fake data · no Level-0 AI deep explanation** — every block renders real data or `source required`.
- Keep the existing Real Result recap (match 8/13) and Evidence Pack; extend with lineup/coach/formation/event/stats
  blocks gated on `available`.
- **Exit criterion:** `/report` renders real Level-2 blocks for a covered fixture; everything else honest-empty.

## Phase 5 — Operator Review
- zh / vi screenshots (real device) · **no Chinese residue in vi (Han=0)** · **no betting wording** · **no 42.2%** ·
  **no unlicensed xG** (StatsBomb non-commercial stays offline).
- **Exit criterion:** operator PASS recorded; only then consider a (still-gated) external trial.

---

## PR strategy (Task E)
- **PR #2 stays a Draft discovery PR** (audits + Evidence-Pack/Real-Recap frontend + all strategy/architecture docs).
  **Do NOT keep stacking implementation on PR #2.**
- **Open a new implementation PR off `main`:** **`feature/mvp2-api-football-ingestion`**.
  - Scope: backend proxy / ingestion prototype · data contract · small **redacted** sample (no token, no large
    payload) · **no frontend UI first** (Phase 4 lands in a later PR or a follow-up commit once the contract is approved).
  - Keep PRs small + reviewable; backend/API/DB changes there are **Owner-gated** and reviewed, not in PR #2.

## Sequencing gate (before opening the implementation PR)
1. Owner approves API-FOOTBALL plan-verification (rate-limit/commercial/injuries — `API_FOOTBALL_PAID_PLAN_DECISION.md`).
2. Operator sets the key on Render (server-side, gitignored).
3. Re-run verifier → confirm injuries (current-season) + rate-limit/budget.
4. Phase-0 data contract approved.
5. → open `feature/mvp2-api-football-ingestion` and start Phase 1.

## Guardrails honored
docs-only this round · no frontend/backend/API/DB change · token/payload never committed · odds excluded ·
StatsBomb non-commercial · operation paused · PR #2 stays Draft.
