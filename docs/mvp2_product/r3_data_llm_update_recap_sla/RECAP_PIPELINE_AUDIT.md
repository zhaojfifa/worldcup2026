# R3 · RECAP_PIPELINE_AUDIT

> Phase A — audit only. Audited 2026-06-15. Fixes the Owner-reported live issue:
> `/recap/1489371` shows the observation receipt, but the network STILL hits the backend and gets
> `404 {"detail":"no recap for fixture 1489371 (zh)"}` — confirmed live via curl.

## Where /recap gets its data

- Route: `frontend/src/App.tsx:36` → `<Route path="recap/:fixtureId" element={<RecapDetailPage/>} />`.
- `RecapDetailPage.tsx`:
  - L88: initial state = `getBundledRecap(fixtureId, loc)` (bundled fallback).
  - **L90–100: useEffect calls `api.getRecap(fixtureId, loc)` UNCONDITIONALLY** (unless `VITE_USE_MOCK`),
    `.catch()` → bundled. **This is the bug: it fires even when the page will render from a local
    observation artifact.**
  - L105–137: if a bundled product narrative recap exists (`historical_recap`/`real_recap`) → render it.
  - **L141–144: if `getObservationArtifact(fixtureId)` exists and `!recap_ready` → render
    `<ObservationReceipt/>`** (this is what 1489371 hits — renders correctly).
  - L149–168: generic safe OBSERVATION page (no content).
  - L170+: deterministic bundled recap render (855737).
- `api.getRecap` = `GET /api/v1/recap/{id}?lang=` (`client.ts:71`).

## Why the backend returns "no recap"

- `backend/app/routers/recap.py:19–26`: calls `build_recap_view(fixture_id, lang)`; if `None` →
  `raise HTTPException(404, f"no recap for fixture {fixture_id} ({lang})")`.
- `backend/app/services/scoutscore/recap_view.py:25–31`: looks for
  `docs/data_audit/mvp2_prediction_accountability_reports/{id}.{zh-CN|vi-VN}.json`; returns `None`
  if absent.
- For 1489371 **no such file exists** (only 855737 has one) → 404 is *correct backend behavior*.
  1489371 is an observation-only fixture; its content is bundled in the FRONTEND, not the backend.

## So the bug is purely the unconditional frontend call

The page already falls back gracefully (ObservationReceipt renders). The defect is that the
**unnecessary backend call leaks a 404 in the network tab** — it reads as a product failure even
though the rendered page is fine. "Copy not fully expanded" is the same symptom: the 404 makes the
observation page look like a degraded/error state to a reviewer.

## Should the frontend call the backend first?

No — not when a local source already determines the render. Correct precedence (no behavior change to
what users SEE, only stop the wasted/erroring call):
1. bundled product-narrative recap present → render it, **skip backend**.
2. observation artifact present (recap_ready=false) → render receipt, **skip backend**.
3. otherwise (e.g. 855737, backend-served recap) → call backend, fall back to bundled.

## Required recap states (R3 contract)

| State | Meaning | Customer behavior |
|-------|---------|-------------------|
| `OBSERVATION_READY` | finished + observation artifact, no full recap | show receipt with clear "完整复盘确认后开放" label; NO backend error |
| `RECAP_PENDING` | finished, observation not yet built | safe post-match page (calibration focus); NO error |
| `RECAP_READY` | full recap artifact/narrative bundled OR backend serves it | full expanded recap |
| `RECAP_ERROR` | genuinely no content of any kind | safe generic observation page; **never** raw backend error string |

Today's lifecycle enum (`freshness.ts:11`, `lifecycle.py`) has SCHEDULED…RECAP_PENDING, RECAP_READY,
ARCHIVED but **no explicit `OBSERVATION_READY`**; an observation-only finished fixture is modelled as
RECAP_PENDING. R3 introduces a derived `recapState(fixtureId)` helper in the frontend (does not change
the backend lifecycle enum) so the route and `/internal/daily` can name the state precisely.

## Full recap content requirements (when a full recap IS built)

pre-match call · actual score · hit/miss/partial-hit judgment · deviation reason · tactical review ·
key turning points · player/team variable (if available) · next-match impact · what the model should
recalibrate · share copy. (Today only 855737 satisfies this via the backend report + bundled recap.)

## Fix surface (Phase B)

1. `RecapDetailPage.tsx` useEffect — gate `api.getRecap` so it is skipped when a bundled product
   narrative recap OR an observation artifact drives the page. **No raw backend error reaches the UI.**
2. `predictionArtifacts.ts` — add `recapState(key)` returning one of the four states (derived from
   bundled product narrative + observation artifact).
3. `1489371` — keep as **explicit observation-only** (`recap_ready=false`); do NOT fabricate a full
   recap (insufficient archived pre-match narrative data to author one honestly).
4. `/internal/daily` — add a "Recap SLA state" row showing the derived state for the carryover fixture.
5. `check_recap_pipeline.py` (R3) — verify: observation artifacts never claim recap_ready=true; the
   route does not unconditionally call the backend; each finished tracked fixture resolves to a state
   that is not RECAP_ERROR; backend 404 is tolerated (frontend fallback proven), not a product failure.
