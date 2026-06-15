# P7 — OWNER_DECISIONS

> Decisions only the Owner can make. Each has options + a recommendation. No implementation until these are answered.

### 1. Restore/create an internal update-mechanism page?
- **A) Yes — `/internal/daily` operator content-readiness panel (admin-gated, no nav link).** *(Recommended)*
- B) Yes, plus a terse public status line on the homepage.
- C) No — keep CLI + docs only.
- **Recommendation: A (then B as a small, carefully-worded add-on).** There is currently no surface where an operator can
  see whether today's hotspot has an artifact, T-30 is confirmed, or the recap is ready — this is the single biggest
  anti-drift gap. The page is frontend-only (reads the manifest + bundled artifacts).

### 2. Should the homepage read the `selected_hotspot` artifact rather than slate order?
- **A) Yes — `selectProductLoop` prefers `selected_hotspot_<date>.json`, falling back to slate-order + `hasPredictionArtifact`.** *(Recommended)*
- B) No — keep slate-order + artifact-gate (the persisted file stays audit-only).
- **Recommendation: A.** Today the persisted editorial decision is read by NO code; the lead is bound only indirectly, so
  the official pick and the live lead can silently drift. Wiring it (with a guard that the lead == selected_hotspot) makes
  the daily decision authoritative and auditable.

### 3. Should T-30 have its own artifact / persisted slot?
- **A) Yes — a `t30` block on the prediction artifact (placeholder pre-lineups, `t30_update` filled at T-30).** *(Recommended)*
- B) No — keep the static checklist + in-group manual update.
- **Recommendation: A.** The T-30 correction is the core conversion moment and is currently persisted nowhere. A placeholder
  slot makes the pending checkpoint honest and gives the operator/page something concrete to track and send.

### 4. Should operator-confirmed modeling fields be allowed when computed fields are missing?
- **A) Yes — operator-confirmed score/lean/risk are allowed for MVP, disclosed as a qualitative scout call (`confidence:null`,
  disclosed note), with a structured artifact that can later be backed by model output.** *(Recommended)*
- B) Yes, but only until P1; require a model frame for every featured fixture thereafter.
- C) No — no featured fixture without a model+LLM frame.
- **Recommendation: A (with B as the P1 direction).** This is the current reality and it keeps the daily loop running; the
  honesty guardrail is the `operator_confirmation` block + null confidence + no invented probability. The guard must keep
  these clearly disclosed (not dressed as model output).

### 5. Should artifacts stay frontend-bundled for MVP or move to backend runtime later?
- **A) Bundled for MVP-P0 (no backend change; content updates on redeploy, matching the artifact cadence); backend runtime
  store as a P1 option (the artifact analogue of the P1.3c slate store, for no-redeploy content updates).** *(Recommended)*
- B) Move artifacts to a backend runtime store now (P0).
- **Recommendation: A.** P0 stays frontend-only and low-risk; the slate already updates without redeploy, and depth content
  changes ~once/day, so bundling is acceptable until the operation scales.

### 6. Should P7 implement a simple daily operator checklist UI?
- **A) Yes — the `/internal/daily` panel IS that checklist (readiness booleans + send-kit links, read-only, never sends).** *(Recommended)*
- B) Keep the checklist as a doc/runbook only.
- **Recommendation: A.** Folding the daily SOP into the internal page (as read-only readiness + links) is the operator surface
  that prevents drift and makes "what to send today / T-30 / FT" answerable at a glance — without ever sending.

---
**Cross-cutting:** P0 (decisions 1–6 "A") is frontend/scripts/docs only — no backend, no schema, no send. P1 (reconnect the
model/LLM engine, generalize external signals, backend artifact store) is a separate Owner GO with its own API-budget and
compliance review. Send remains HOLD regardless.
