# P7 — Content + Update Mechanism Recovery · STATUS

> Read-only discovery/review. NO implementation. NO product-code commit. NO deploy.
> Generated 2026-06-15.

## State
- **Current branch:** `main`
- **Current HEAD:** `89ccc2d5bddd7e1b4a7579b1e1a78f022cfcf170` (P6 product recovery deployed; live bundle `index-DBEkHr_r.js`)
- **Working tree:** clean except one pre-existing untracked file `docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_20260613_1255.json` (not touched).
- **Branches inspected (read-only via `git show`/`git log`/`git diff`, no checkout):**
  `feature/mvp2-growth-p0-design` 5535c61 · `p1-automation` a701eaa · `p1-1-share` cd8d35d · `p1-1b-refresh` 7fe23bb · `p1-1c-strongcopy` 0a73ee6 · `p1-2-status-refresh` 65f2202 · `p1-3-match-sync` 7e9703b · `p1-3b-runtime-fixtures` 8a6215b · `p1-3c-backend-fixtures` 69e7c5b · `p1-4-orchestration` 051926c · `p1-5-first-send-gate` 5eacae6 · current main.
  (All eleven feature branches are ANCESTORS of main — promoted, then extended.)

## Headline finding
**CLEAR RECOVERY PATH** — but the loss is real and split in two:
1. **Slate / share / ambassador / projection mechanisms = NOT lost.** The daily slate-update backbone (`manual_scores → mvp2_match_sync → registry → runtime json → backend runtime_manifests → GET /api/v1/daily-fixtures → HomeProductLoop`) is fully connected and live; the ambassador automation, share layer, and canonical strong-call projection are all on main, wired, and (P1 runtime) byte-identical to their branches.
2. **The original CONTENT-PRODUCTION mechanism IS disconnected.** The data/model frame builders (ScoutScore Elo/form/H2H/Poisson) and the LLM narrative generators exist on main but are **locked to ~5 sample fixtures** and are **never invoked by the daily loop**. A new daily manual hotspot (e.g. Netherlands–Japan) is **100% operator hand-authored** with no model/LLM provenance and **no generator script**. There is also **no visible/internal update-mechanism page** (only `/internal/growth` for the ambassador layer), and `selected_hotspot_<date>.json` is **persisted but read by no code**.

## Discovery state
Context pack complete (10 files in this directory). 5 read-only subagents covered: P0 design + P1 automation · share/refresh/strongcopy + field map · sync/lifecycle/runtime/backend pipeline · orchestration/gate + P3–P6 evolution · data-source + modeling + LLM pipeline.

## Next action
Owner reviews `OWNER_DECISIONS.md` and `P7_IMPLEMENTATION_PLAN.md`. No implementation until an Owner GO. Send remains HOLD (Gate 3 1489371 LIVE/FT + Gate 4 Owner per-channel GO).
