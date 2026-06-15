> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# P6 Discovery — STATUS

## Overall finding

**CLEAR RECOVERY PATH.** The OLD product strength is **NOT lost** — it is on `main` but **under-surfaced**. Every strong OLD asset already lives on `main` and is reused on `/predict`, `/share`, and `/recap`. P5b is thinner only because:

- the strong-call hook is **not surfaced on the homepage lead**;
- the in-page **T-30 rescore ladder + calibration-frame line** were dropped from the new artifact tactical room;
- the `real_recap` recap tier **lacks the full share kit**; and
- rich per-fixture content is **hand-authored one-offs** (no generator) with a **hardcoded `NEXT_HOOK` "Brazil vs Morocco"**.

P6 is therefore a **copy/UI-first, frontend-only** recovery: surface `StrongCallCard` on a renderable homepage lead, restore the rescore/calibration affordances + `ShareBlock` to all recap/predict surfaces, de-hardcode `NEXT_HOOK`, complete the daily prediction/observation artifact schema, and tighten the three guards to require a score-call hook — with **NO backend or schema change required**.

---

## Git state

| Item | Value |
|---|---|
| Current branch | `main` |
| Current HEAD | **b9b362a** (main, P5b) — full hash `b9b362aad4b6cf94bc5470a3b84b401344b99f13` |
| Old branch inspected | `feature/mvp2-growth-p0-design` = **5535c61** |
| Old branch inspected | `feature/mvp2-growth-p1-1c-strongcopy` = **0a73ee6** |

**Merge truth:** every OLD asset is **ALREADY MERGED TO MAIN** (`git log main..strongcopy` is empty). Two files were extended **further on main** for the P5 artifact fallback:

- `frontend/src/growth/strongCallProjection.ts` (+87 lines on main)
- `scripts/check_growth_copy.py` (+28 lines on main)

> **Reuse `main`'s version of both, never re-implement from the branch snapshot.** The branch copies are stale.

---

## Live bundle (as last recorded — re-verify)

- Live frontend bundle: **`index-Dz95Uq3Y.js`** (P5b) — *as last recorded in the memory index; re-verify against the live deploy before any send/scan.*
- DEFAULT_REF growth codes (`QG-TEST1` / `TT-VN88` / `FO-MM21`) are **not yet created in prod** (live probe showed `attached:false`) — operational gate, not a code defect.

---

## Current product status

**P5b artifact-based product loop on `main`.** The product narrative loop (homepage → `/predict` → `/recap` → `/share` → `/join`) is live and compliance-clean:

- **Homepage** (`HomeProductLoop.tsx`): hotspot-first funnel (`HotspotPrediction` → `HotspotRecap` → secondary schedule → other recaps → growth), never shows a fake recap, never exposes generation state. The lead card is a **generic question-frame**, not a score-call hook.
- **`/predict`**: two strong paths — bundled LLM `ProductNarrative` → `StrongCallCard + ProductPredictView` (unchanged old-strongcopy path); or manual hotspot with no narrative → `ArtifactTacticalRoom` (the P4/P5 net-new recovery tier). Today's live surface (Netherlands vs Japan) renders the artifact room from **hand-authored operator JSON** (`manual_Nether-Japan-20260614.json`, `source=operator_confirmed`, `confidence=null`).
- **`/recap`**: flagship 1489371 Brazil 1-1 Morocco renders via `ObservationReceipt` (artifact `recap_ready=false`) — a full trust receipt (pre-match call → actual → partial-hit assessment + deviation → calibration points → next impact), never a synthesized result.
- **Share / growth**: `/share/{fixture,recap}/:id` branded cards + QR to `/join?ref=CODE`; first-touch `?ref=` capture survives copy-link → visit → join and share-card → QR-scan → join, attribution-only (no money/identity fields).

**Operations posture (unchanged):** operation paused; small private trial only; all sends manual, one channel, per Owner GO; engineering holds NO prod `ADMIN_API_TOKEN`. First-send gate: Gates 1–3/5/6 closed, Gate 4 (match-day LIVE/FT lifecycle) operator, **Gate 7 (Owner per-channel GO) PENDING** — nothing sent. 1489371 pre-match window is now **CLOSED** (today/next packages auto-REFUSED after the 06-14 manual refresh); `recap_1489369_zh_QG-TEST1.md` is available but `approval_status=guard_passed` (must clear queue approve + Owner GO).

---

## Discovery state

**Context pack COMPLETE.** This P6 discovery has exhaustively read and mapped:

- the OLD growth intent (7 `GROWTH_P0_*` design docs on `feature/mvp2-growth-p0-design`, all also on main);
- the OLD strongcopy frontend + external-signal + guard layer (`feature/mvp2-growth-p1-1c-strongcopy`);
- the current `main` homepage, predict, recap, share, daily-flow, and operations/compliance surfaces.

Full read log: see **`READ_LOG.md`** (this directory). Per-asset reuse/discard map and the Owner decision set are captured in the P6 analysis. Key structural findings:

- **Homepage guard blind spot:** `check_homepage_product_loop.py` (13 checks, live PASS) asserts a TITLE + 进入战术室 CTA + CopyLink exist on the lead but asserts **NOTHING** about a score-call / lean / primary-score / win-prob hook → the weak-hook gap passes green.
- **Structural root cause of the weak lead:** today's manifest promotes a **non-renderable `id=null`** manual fixture (Netherlands–Japan, `renderable=false`) to the lead via `selectProductLoop` `scheduled[0]`, so even `StrongCallCard` would return `null` there.
- **`NEXT_HOOK` hardcoded** to `下一场 Brazil vs Morocco` in `strongCallProjection.ts` → stale for any other recap.
- **No generator** for per-fixture prediction artifacts (only validators) → hand-authoring does not scale past ~1 fixture/day.
- **`MatchDesk.tsx` is dead code** (P1.4 orchestration, not imported anywhere) — discard candidate.
- **Strong-call assembly is DUPLICATED** in `scripts/mvp2_growth_cli.py` and `frontend/src/growth/strongCallProjection.ts` → changes must touch both or drift.

---

## Next action

**Owner reviews `OWNER_DECISIONS.md`** (the 7-question decision set). **No implementation until GO.**

The decision set, in brief (recommendations shown):
1. **Re-add a score-call hook to the homepage hotspot lead** (reverses the P1.5a "cut Strong Calls from landing" decision)? → **C then A** (ship a lean + 主比分 teaser first, path to full hook once a renderable lead is guaranteed).
2. **Force the homepage lead to be a renderable fixture** (not slate-order-first even when it is a non-renderable `id=null` manual entry)? → **A** (renderable-first selection).
3. **Allow operator-confirmed daily score calls + add a generator/scaffolder**? → **A** (keep the validated, disclosed artifact fallback AND build a daily scaffolder).
4. **Show the external-expectation block on the homepage lead**? → **A** (keep it detail-only until `mvp2_project_external_signals.py` is generalized).
5. **Persist the daily editorial selection as `selected_hotspot_<date>.json`**? → **A** (script/docs-only, durable + auditable).
6. **Scope P6 to artifacts/UI only, or also consolidate operations docs onto a main-tracked `OPERATIONS_FLOW.md`**? → **A** (UI/artifacts + docs consolidation).
7. **Tighten `check_homepage_product_loop.py` to require a score-call hook + generalize `check_prediction_artifact.py` off its hardcoded filenames**? → **A** (both; sequence the homepage assertion to land WITH the UI hook).

**P6 P0 scope (frontend/copy/UI + validator only — NO backend, NO schema):** homepage score-call hook; restore dropped tactical affordances (calibration frame line + rescore CTA / `#live30`); richer recap receipt (propagate match-specific calibration/next-impact, de-hardcode `NEXT_HOOK`); share/operator completeness (`ShareBlock` on real_recap + predict; consolidate SOP onto a main-tracked doc); daily artifact schema completeness (scaffolder + persisted `selected_hotspot_<date>.json`).

**Deploy impact:** FRONTEND-ONLY for all rendered changes; DOCS/SCRIPT-ONLY for the operations-doc consolidation, editorial-selection persistence, and guard updates. **No backend route, no DB table, no schema migration.** No-send posture preserved throughout; rollback is a frontend revert + prior-bundle redeploy (no data migration to undo).
