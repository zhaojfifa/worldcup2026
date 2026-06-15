> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# DAILY_UPDATE_FLOW.md — How a Match Day Updates the Product

This document answers, for one match day, **what happens at each phase** and **which artifacts are
required** before the product surfaces a match. It marks each step **manual (MVP today)** vs
**automatable later (Owner-gated)**. It is the day-to-day operating spine: `mvp2_match_sync.py` →
registry/manifest → `dailyFixtures.ts` → homepage loop, gated by `mvp2_fixture_lifecycle.py`.

**Headline reality.** Only the **daily-fixtures manifest** is runtime-updatable (backend upload, no
rebuild — the "能更新才是硬道理" path). **Any new artifact or narrative** (a prediction strong call, an
observation receipt, a full recap) is **bundled at build time** and therefore requires a **frontend
redeploy**. Today, depth exists for at most ~2 carried-over fixtures + 1 hand-authored artifact per
day; everything else is a lightweight status row.

---

## 1. Phase-by-phase: what happens, when

### Before match day
- **Operator hand-writes** `docs/data_audit/mvp2_match_sync/manual_scores_<date>.md` — the slate as
  Owner-stated facts (finished `a-b` / scheduled `vs`). **No invented scores.**
  → **MANUAL.**

### Morning of match day
- `scripts/mvp2_match_sync.py sync --date` reads the manual slate and writes the **daily registry**:
  `daily_fixtures_<date>.json` (lifecycle `decide()` / `gates()` + hero/next/recap candidate flags),
  `recap_queue_<date>.json`, `frontend/src/data/dailyFixtures.generated.json`, and the runtime manifest
  `frontend/public/data/daily-fixtures.json`.
- `scripts/mvp2_fixture_lifecycle.py` writes a timestamped
  `docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_<date>_<hhmm>.json` — time-inference defeats a
  stale `NS` past kickoff (P1.2b: no finished/live match shown as an active pre-match).
  → **AUTOMATED** (scripts; operator runs them).

### After hotspot selection
- `scripts/mvp2_editorial_agent.py` builds a **copy-paste LLM prompt** (slate facts + product policy +
  current editorial line + safety) for DeepSeek/Gemini/Kimi. It is a **prompt builder ONLY**: prints to
  stdout, **writes nothing, calls no API**. The operator pastes it into an LLM, reads back the JSON
  (`featured_pre_match` / `featured_recap` / `fallback_recap` / `group_only` / `hold_reason`), and
  confirms **manually**. The decision then lives in operator memory + hand-edited manifest flags.
  → **MANUAL** (Agent-led, LLM-assisted, operator-confirmed). **Gap:** the selection is **not
  persisted** (no `selected_hotspot_<date>.json`); a re-run of `sync` wipes the hand-edited flags.

### Artifact required before the homepage points to a match
The bar depends on how the match is surfaced:
- **A lightweight status row** (`即将开赛` chip / status line) needs **only manifest presence** — runtime,
  **no rebuild**.
- **A featured / hero card with DEPTH** needs **either**:
  - a bundled `frontend/src/data/productNarratives/{id}.{lang}.json` (`renderable=true`; today only
    `1489369` / `1489371` qualify), **or**
  - for a manual `id=null` hotspot, a `frontend/src/data/predictionArtifacts/manual_<slug>.json`
    registered in `predictionArtifacts.ts` + validated by `check_prediction_artifact.py`,
  - **plus a frontend redeploy** in either case (artifacts/narratives are build-bundled).
- **Today's structural trap:** `selectProductLoop` promotes the first scheduled fixture even when it is
  a non-renderable `id=null` manual entry (NL vs JP), so the lead can only be a frame card. A renderable
  lead must be guaranteed for any homepage score-call hook to render.
  → **MANUAL** (hand-author + register the artifact, then redeploy).

### T-30 (kickoff − 30, lineups out)
- The placeholder renders from `pending_direction` / `pending_score` + `thirty_minute_checklist` + the
  canonical `T30_HOOK`. The **actual re-confirm / rescore is MANUAL**; `RescoreBlock` data
  (`rescoreData.ts`, `getRescore`) exists for `1489369` / `1489371` only.
  → **MANUAL** (placeholder auto; rescore regen manual, and only for fixtures with bundled rescore data).

### After full time
- `scripts/mvp2_growth_cli.py refresh` neutralizes stale pre-match packages to **REFUSED** stubs
  (lifecycle gate; a finished fixture can never emit a pre-match package).
- The day's finished hotspot renders as an **`ObservationReceipt`**
  (`observation_<fid>.json`, `recap_ready=false`) — a real trust receipt (pre-match call → actual →
  partial/miss → deviation → calibration → next impact), **never a fake recap** — until an A4 full recap
  is generated, bundled, and redeployed.
  → **AUTOMATED** (package neutralization) + **MANUAL** (hand-author the observation receipt + redeploy).

### Tomorrow's recap (the full recap)
- A **real full recap** (`productNarratives` with `mode == real_recap`) requires **A4 LLM generation +
  bundle + redeploy**. Until then the surface stays an observation receipt (and `recap_queue` lists the
  missing one as `NEEDS_A4_RECAP`).
  → **MANUAL / not-yet-wired** (A4 generation is Owner-gated; no generator runs daily).

### Manual in MVP vs automated later
- **Manual today:** the `manual_scores` md; the LLM editorial paste / read-back; the manifest-flag hero
  override (a re-sync **wipes** it); hand-authoring + registering the prediction / observation artifacts
  (trilingual + en); the **frontend redeploy**; the prod manifest upload (operator token — engineering
  holds none); the per-channel send GO.
- **Automatable but not yet wired (Owner-gated):** per-fixture prediction-artifact generation via the
  existing scoutscore v0.2 → narrative → guard → bundle pipeline; a daily external-signal refresh with
  provenance; A4 recap generation; persisting the editorial selection.

---

## 2. Where rich content is lost day-to-day (why "daily" reads thin)

1. **Strong-call depth is not regenerated per fixture.** Bundled `productNarratives` exist for **only**
   `1489369` / `1489371` (LLM-generated 06-11). Every new daily hotspot has no narrative → depends on a
   **hand-authored** `predictionArtifacts/manual_<slug>.json`, and **no generator script exists** (only
   validators). Does not scale past ~1 hand-written fixture/day.
2. **The homepage featured card is generic boilerplate.** `HotspotPrediction` renders static
   `predWhy` / `predBullets` with `{home}`/`{away}` substitution + a fixed 30-min line — **not** the
   artifact's `score_call` / `top_variable` / `tactical_matchup`. The real strong call surfaces only one
   click deeper at `/predict/{key}` (`ArtifactTacticalRoom`); a non-clicking reader never sees the daily
   judgement.
3. **Only 2 fixtures can carry depth.** Today only Mexico / Brazil are `renderable=true`; the other 5
   are `renderable=false` (id=null, kickoff=null) → lightweight status rows forever.
4. **External signals are not refreshed.** Frames exist only for 4 fixtures dated **06-12**; new
   hotspots get `external_expectation` **hand-typed into the artifact**, bypassing
   `mvp2_project_external_signals.py` → no provenance. (That script is also not generalized — its
   `TEAMS` dict + several literal lines are `1489371`-only.)
5. **Full recap degrades to an observation receipt.** Brazil 1-1 has `recap_ready=false`; no A4
   `real_recap` is bundled.
6. **The editorial decision is not persisted.** No `selected_hotspot_<date>.json`; it lives in
   `mvp2_editorial_agent.py` **stdout** (prompt-builder only) + operator memory + hand-edited manifest
   flags that a re-sync **wipes**.

---

## 3. Required daily artifacts

For each artifact: the **filename / path pattern** (current or proposed) and whether it is **manual or
auto** today. Status legend: ✓ exists · ✗ missing · ⚠ exists but limited.

1. **Daily fixture slate (registry).** ✓
   - Path: `docs/data_audit/mvp2_match_sync/daily_fixtures_<date>.json`
     (+ runtime `frontend/public/data/daily-fixtures.json`, `frontend/src/data/dailyFixtures.generated.json`,
     `docs/data_audit/mvp2_match_sync/recap_queue_<date>.json`).
   - **AUTO** — written by `mvp2_match_sync.py sync` from the hand-written
     `manual_scores_<date>.md` (the `.md` itself is **MANUAL**). The runtime manifest is uploadable to
     backend with no rebuild (operator prod token required).

2. **Selected hotspot fixture key.** ✗ **MISSING (ephemeral).**
   - Proposed path: `docs/data_audit/mvp2_match_sync/selected_hotspot_<date>.json` (or written by
     `mvp2_editorial_agent.py` / `mvp2_match_sync.py`).
   - **MANUAL today** — exists only as `mvp2_editorial_agent.py` stdout + operator memory + a
     hand-edited manifest flag that a re-sync wipes. **Recovery proposal:** persist it (script/docs
     only, no backend) so the editorial decision is durable and auditable.

3. **Prediction artifact with a strong call.** ✓ but **hand-authored (no generator).**
   - Path: `frontend/src/data/predictionArtifacts/manual_<slug>-<date>.json`, registered in
     `frontend/src/data/predictionArtifacts.ts`, validated by `scripts/check_prediction_artifact.py`.
   - Schema: per-locale `prediction{primary_direction, score_call, backup_score, confidence, risk_level,
     risk_note, top_variable, why}` + `analysis{modeling_focus[], tactical_matchup[], risk_variables[],
     external_expectation[], thirty_minute_checklist[]}` + `operations{share_title, share_copy,
     join_cta}`. Numerics nullable → pending labels, never invented.
   - **MANUAL** — written by a human (today `manual_Nether-Japan-20260614.json`,
     `source=operator_confirmed`, `confidence=null`, disclosed as a qualitative call). Bundled at build →
     **frontend redeploy required**; `check_prediction_artifact.py` paths are currently **hardcoded** to
     today's filenames (must be generalized to a glob). **Automatable later:** generate via the
     scoutscore v0.2 → narrative → guard → bundle pipeline (P0 ships a scaffolder + validator
     generalization, not the full generator).

4. **Share copy.** ✓ for narrative fixtures; embedded for manual.
   - Path: `docs/data_audit/mvp2_growth_packages/{today,next,recap}_{fid}_{lang}_{REF}.md`
     (+ `refresh_summary_*.json`). For a manual hotspot, share copy is embedded in the artifact's
     `operations.share_*`.
   - **AUTO** — `mvp2_growth_cli.py refresh` assembles paste-ready packages **only** from bundled
     guard-passed narratives, lifecycle-gated (a finished fixture is refused as pre-match; stale files
     overwritten with REFUSED stubs). **Limitation:** works only for fixtures that already have a
     bundled narrative (`1489369` / `1489371`); strong-call assembly is **duplicated** with
     `strongCallProjection.ts` (drift risk).

5. **T-30 correction placeholder / update.** ⚠ placeholder auto; rescore regen manual.
   - Path: placeholder renders from the artifact's `pending_direction` / `pending_score` +
     `thirty_minute_checklist` + canonical `T30_HOOK`. The rescore model layer is
     `frontend/src/data/rescoreData.ts` (`getRescore`), wired for `1489369` / `1489371` only.
   - **MANUAL** — the actual re-confirm / rescore is hand-done; rescore JSON is per-fixture LLM content
     that must be regenerated + bundled + redeployed for each new fixture.

6. **Observation artifact (post-match receipt).** ✓ hand-authored.
   - Path: `frontend/src/data/predictionArtifacts/observation_<fid>.json`, loaded via
     `predictionArtifacts.ts` (OBSERVATION map), validated by `check_prediction_artifact.py`.
   - Fields: `pre_match_call → actual_line → assessment (hit/partial/miss) → deviation →
     calibration_points → next_impact`, `recap_ready=false`, `safety.no_fake_recap=true`. 4 langs.
   - **MANUAL** — hand-authored (today `observation_1489371.json`, Brazil 1-1, explicit
     `部分命中`). Bundled at build → **redeploy required**. This is the degraded recap tier when no A4
     full recap exists.

7. **Full recap artifact (when ready).** ✗ **MISSING for the day's finished hotspot.**
   - Path: `frontend/src/data/productNarratives/{id}.{lang}.json` with `mode == real_recap`.
   - **MANUAL / not-yet-wired** — requires **A4 LLM generation + guard + bundle + frontend redeploy**.
     Until it exists, `recap_queue` flags it `NEEDS_A4_RECAP` and the surface stays an
     `ObservationReceipt` (never a synthesized result). **Automatable later** (Owner-gated A4 generation).

---

## 4. Summary table (daily artifacts)

| # | Artifact | Path pattern (current / proposed) | Today | Runtime-updatable? |
|---|----------|------------------------------------|-------|--------------------|
| 1 | Daily fixture slate | `daily_fixtures_<date>.json` (+ `public/data/daily-fixtures.json`) | AUTO (from manual `.md`) | Manifest: yes (backend upload, no rebuild) |
| 2 | Selected hotspot key | `selected_hotspot_<date>.json` (proposed) | MANUAL — ✗ not persisted | n/a (script/docs) |
| 3 | Prediction artifact (strong call) | `predictionArtifacts/manual_<slug>-<date>.json` | MANUAL hand-authored (no generator) | No — build-bundled, needs redeploy |
| 4 | Share copy | `mvp2_growth_packages/{today,next,recap}_{fid}_{lang}_{REF}.md` | AUTO (narrative fixtures); embedded for manual | File only |
| 5 | T-30 placeholder / rescore | artifact `pending_*` + `rescoreData.ts` (`getRescore`) | Placeholder AUTO; rescore MANUAL | No — build-bundled |
| 6 | Observation artifact (receipt) | `predictionArtifacts/observation_<fid>.json` | MANUAL hand-authored | No — build-bundled, needs redeploy |
| 7 | Full recap artifact | `productNarratives/{id}.{lang}.json` (`mode==real_recap`) | MANUAL / not wired — ✗ missing | No — build-bundled, needs redeploy |

**Key takeaways.**
- Only artifact **#1's manifest** updates live; **#3, #5, #6, #7** are build-bundled and each new
  instance requires a **frontend redeploy** + (for #3/#6) a code edit to `predictionArtifacts.ts` and
  the validator paths.
- The two **missing** artifacts are **#2 (persisted editorial selection)** and **#7 (full recap)**;
  **#3 / #6** exist but are hand-authored one-offs with no generator.
- The recovery (P6) targets: persist #2 (script/docs only), add a scaffolder/validator-generalization
  for #3/#6, and keep #7 / the daily external-signal refresh as Owner-gated P1 automation — all
  frontend/docs/script only, **no backend or schema change**.
