# P7 — UPDATE_MECHANISM_PAGE_SPEC

> Should we restore/create a visible/internal update-mechanism page? Evaluate options; the page's job is to
> PREVENT DRIFT (no hotspot without artifact, no recap without receipt, no lead without selected_hotspot, no send
> without Owner GO). Today there is no such surface — only `/internal/growth` (ambassador metrics).

## Option A — Internal operator page only (`/internal/daily`)
A new admin-gated route (same `x-admin-token` wall + sessionStorage pattern as `/internal/growth`, no nav link),
a **daily content-readiness panel**:
- **Selected hotspot** — today's `selected_hotspot_<date>.json` (fixture, key, operator_confirmed) + a red flag if it
  disagrees with the runtime homepage lead (`hasPredictionArtifact(leadKey)`).
- **Artifact readiness** — does `manual_<slug>.json` exist? does it pass `check_prediction_artifact.py`? are score_call /
  risk / lean confirmed (not pending)?
- **T-30 status** — is the T-30 slot a placeholder or filled? lineups out yet (lifecycle ≥ T-30)?
- **Recap status** — does an observation artifact exist for yesterday's finished hotspot? `recap_ready`? is it keyed so
  it carries over (numeric-id-gap check)?
- **Share links** — the per-lang send-kit paths + `/share/fixture|recap/:id?ref=<CODE>` + which codes exist in prod.
- **Freshness** — backend manifest `generated_at` / `stale` + which tier (实时/静态备份/内置).
- **Pros:** zero customer-surface risk; the operator finally sees content readiness in one place; cheap (one read-only
  page reading files/manifest the frontend already fetches). **Cons:** internal-only; needs the data exposed (file reads
  or a small read-only endpoint).
- **Recommended.** This is the missing operator surface and the cheapest, highest-leverage anti-drift control.

## Option B — Public lightweight status block
Extend the existing homepage sync line into a small honest status: "今日预测已就绪 / T-30 待确认 / 复盘已就绪",
derived from the same readiness signals (artifact present, lifecycle state, recap_ready).
- **Pros:** sets honest user expectations; reuses the live `⟳ 赛程更新 …` line. **Cons:** must stay strictly
  status-only (no internal generation wording — the exact leakage P3/P6 banned, e.g. 复盘生成中/待生成); easy to get wrong.
- **Conditional.** Acceptable ONLY as a terse, customer-safe status (今日预测已就绪 / 临场待确认 / 今日复盘已就绪).
  Not the place to expose readiness internals.

## Option C — Both
A (internal panel, full readiness) + B (terse public status). The internal page is the control surface; the public
block is a one-line honest expectation-setter.
- **Recommended target** (A first in P0; B as a small, carefully-worded add-on).

## Drift-prevention contract (the page must enforce / surface)
- **No hotspot without artifact** — already enforced at runtime by `hasPredictionArtifact` (P6); the page SHOWS it and
  flags a selected_hotspot that has no artifact.
- **No recap without receipt** — `查看复盘` only when `recap_ready` (live); the page flags a finished hotspot with no
  observation artifact.
- **No homepage lead without selected_hotspot** — P0 wiring: `selectProductLoop` consults `selected_hotspot_<date>.json`
  (then falls back to slate-order + artifact); the page flags a mismatch between the persisted pick and the live lead.
- **No send without Owner GO** — the page shows gate/send status (read-only); it NEVER sends. Sending stays the manual,
  Owner-GO, per-channel runbook path.

## Build note
Either option is **frontend-only if the data is file/manifest-readable**. The internal page can read the runtime manifest
(already fetched) + the bundled artifacts; `selected_hotspot` would need to be either bundled into the frontend (build-time)
or exposed via a tiny read-only endpoint. Prefer build-time bundling for MVP (no backend change) — accept that the readiness
panel refreshes on deploy, which matches the artifact cadence. A backend read-only `GET /internal/daily-status` is a P1 option
if live (no-redeploy) readiness is wanted.
