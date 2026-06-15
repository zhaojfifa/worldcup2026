# P8 Discovery — STATUS

> Historical Content-Fact Recovery Before Daily Refresh. **Read-only discovery. NO implementation,
> NO product-code change, NO commit, NO push, NO deploy.** Only the 9 docs in this directory were written.

## Git state

| Item | Value |
|---|---|
| Current branch | `main` |
| Current HEAD | **be09770** (`be09770b9a035e4c605470eca757a3fcbaece5fe`) — "docs(qa): P7 P0 live post-deploy screenshots" |
| Inspected reference tag | **`main-backup-pre-p15b-daily-featured-copy-20260613`** = `e3c73a36ac8ea46eccfccac47bd61d362b2921c8` |
| Inspected current main | `be09770` (same as HEAD) |
| Working tree changed by P8? | **No.** The only pre-existing untracked file (`docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_20260613_1255.json`) was present before P8 and was NOT touched. P8 added only `docs/mvp2_product/p8_historical_content_fact_recovery/*.md`. |
| Inspection method | `git log`, `git diff --stat`, `git grep` against both refs + direct `Read` of current-main source. No worktree needed (no checkout of the tag — `git grep <rev>` reads blobs in place, working tree untouched). |

## Headline correction to the premise

The owner's premise — "those historical fields were lost between the reference tag and now" — is **only
half right**. `git grep` shows the model fields appear in **MORE** files on `main` than on the tag
(`win_prob` 29 vs 21, `confidence` 102 vs 80, `recap_ready` 59 vs 18). **Nothing was deleted.** The
historical content-fact layer is **bypassed, not removed**:

- The **backend rule-model field layer** (`win_prob`, `recommended_score`, `risk_level`, `risk_note`,
  `confidence`) still exists end-to-end — `baseline.py` → `Prediction` model → `/api/v1/matches` →
  `transform.ts` → `useAppStore.getMatches()`. It is **still wired into the store**, but only feeds the
  **legacy mock match tiles** (now demoted/folded on the homepage), NOT the daily hotspot product loop.
- The **ScoutScore-v0.2 + LLM `ProductNarrative` layer** (`scoreline_view`, `main_lean`, `risk_level`
  word, `risk_factors`, `tactical_read`, `validated_factors`) still exists and still drives `/predict`,
  `/recap`, `/share` — but **only for the 5 hard-wired fixtures** (1489369, 1489371, 855737, 979139,
  2026_brazil_argentina). It is fixture-locked; there is **no generator** for a new daily fixture.
- The **daily-refresh path** (P1.3 `mvp2_match_sync.py` → `dailyFixtures.generated.json` /
  `daily-fixtures.json` manifest → `predictionArtifacts/*.json`) is a **NEW, third path** whose manifest
  schema (`DailyFixtureRow`) carries **only identity + lifecycle + score** and **never joins** to either
  historical model-field layer. The daily manual hotspot is `id=null`, so it can resolve **neither** a
  backend `Prediction` **nor** a bundled `ProductNarrative`, and falls through to an **operator
  hand-authored artifact** with `win_prob`/`confidence` = `unavailable`.

So this is a **mapping / route-resolution loss**, not a data-deletion loss. (Full diagnosis:
`CURRENT_DAILY_REFRESH_BREAKAGE.md`.)

## Discovery status

**COMPLETE.** All 9 P8 files exist. Source-of-truth files read directly on current main: backend
(`baseline.py`, `schemas/match.py`, `models/prediction.py`, `match_service.py`, `seed.py`,
`daily_fixtures_service.py`), frontend (`transform.ts`, `client.ts`, `useAppStore.ts`,
`predictionArtifacts.ts` + manual artifact, `dailyFixtures.ts`, `selectedHotspot.json/.ts`,
`productNarrativeData.ts`, `strongCallProjection.ts`, `PredictPage.tsx`, `HomePage.tsx`), scripts
(`mvp2_match_sync.py`, `mvp2_build_scoutscore_v0_2_factors.py` family). Prior P6/P7 discovery packs
were read and reused (the P7 `DATA_CONTENT_FIELD_MAP.md` already mapped per-field provenance; P8
extends it with the **route-resolution** dimension the owner asked for).

## Overall finding

**CLEAR CONTENT RECOVERY PATH (frontend/scripts/docs-first).** The historical fields are not gone; the
recovery is to **reconnect** them into the P7 daily artifact (a `model_fields`/`model_snapshot` object,
populated by a small daily generator that runs the still-present ScoutScore frame + an operator-confirmed
fallback), surface a data-backed block on `/predict`, and tighten guards to assert *source/provenance*
rather than fake numbers. **No backend route or schema change is required for P0** (win_prob/confidence
stay honestly `unavailable` unless the Owner authorizes seed/estimated bands).

## Next recommended action

Owner reviews `OWNER_DECISIONS.md` (6 questions) and `P8_IMPLEMENTATION_PLAN.md`. **No implementation
until GO.** The pivotal decision is Q1/Q2: whether seed/placeholder-grade historical fields and/or
`operator_estimated` model fields may be displayed as a "model_fields" block for a manual fixture (the
compliance floor — no fake probability — must be preserved; `win_prob`/`confidence` remain the most
sensitive).
