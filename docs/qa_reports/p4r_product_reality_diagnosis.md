# P4R · Product Reality Diagnosis (Phase 0 — no implementation until this exists)

> Branch `fix/mvp2-p4r-product-reality-daily-llm-wiring` off tag
> `mvp2-p4-critical-daily-recap-copy-loop-live-baseline-20260615`. Blocker:
> `BLOCKED_PRODUCT_FRESHNESS_AND_COPY_WIRING`. This doc traces the ACTUAL rendered path before any fix.

## 1. Where does homepage primary content come from?
`HomeProductLoop.tsx` → `selectProductLoop(manifest)` picks `featuredPrediction` from the runtime
**daily-fixtures manifest** (backend→static→bundled via `fetchDailyManifest`), honoring
`selectedHotspot` (P7). The card text comes from `buildStrongCall(leadKey, loc)`
(`strongCallProjection.ts`) → for a manual hotspot it calls `buildStrongCallFromArtifact(art, loc)`,
which reads the bundled **`predictionArtifacts/<match>.json` `i18n.{loc}.prediction`/`analysis`** +
`model_fields.recommended_score` for the score.

## 2. Where does homepage yesterday recap content come from?
`selectProductLoop` → `featuredRecap = finished[0]` (first finished fixture in the manifest). The card
shows `buildRecapCall` (only if a bundled `real_recap` ProductNarrative exists) else the
`HotspotRecap` frame + a link to `/recap/<id>`. It is **manifest-order driven**, NOT tied to a
"yesterday recommendation closure" artifact.

## 3. Where does /predict/1489377 copy come from?
`PredictPage` → `getPredictionArtifact('1489377')` → `ArtifactTacticalRoom`. Strong card =
`buildStrongCallFromArtifact` → **`i18n.zh.prediction`** (main_lean/score/top_variable/why) +
`model_fields` score. Analysis lists = **`i18n.zh.analysis`**. DataBacking = `model_fields`/`source_facts`.

## 4. Where does /recap/1489371 copy come from?
`RecapDetailPage` → `getObservationArtifact('1489371')` (recap_ready=false) → `ObservationReceipt`
rendering **`observation_1489371.json` `i18n.zh`** (operator-authored receipt). No LLM recap artifact
is bundled/rendered for it.

## 5. Which artifact is SUPPOSED to be LLM-generated?
The reviewed judgement in `docs/data_audit/mvp2_predictions/reviewed/<date>_<fk>_reviewed.json`
(operator pastes the auto-generated draft from `…/generated/` into it). `apply` merges it into the
artifact's **`llm_judgment`** + `i18n.zh.operations.share_copy`. For recaps:
`docs/data_audit/mvp2_recaps/reviewed/…` (P1 flow).

## 6. Which artifact is ACTUALLY rendered live?
The bundled `predictionArtifacts/*.json` **`i18n` block** (prediction + analysis) and the bundled
`observation_*.json` `i18n`. The reviewed LLM **`llm_judgment`** block is written by `apply` but
**NOT read by any renderer** — `buildStrongCallFromArtifact` ignores `llm_judgment` entirely. The
recap reviewed JSON is **not bundled** at all.

## 7. Which files are static fallback/demo content?
`dailyFixtures.generated.json` / `public/data/daily-fixtures.json` (fallback slate), and the legacy
demo fixtures (Qatar vs Ecuador, Netherlands vs Japan) that earlier sprints demoted. They are NOT in
today's critical homepage sections (live DOM scan today shows only Belgium/Egypt/Brazil/Morocco/Saudi/
Uruguay/Spain/Cape Verde) — but no guard PROVES this on the rendered page.

## 8. Why did check_daily_freshness pass while live content looked stale?
`check_daily_freshness.py` compares **artifact dates** (queue/selectedHotspot date == backend `date`)
and checks the slate composition in JSON. It never **dumps the rendered homepage DOM**, so a stale
deploy (old bundle still live) or a label/content mismatch passes the artifact check. (Freshness today
is genuinely FRESH, but the guard could not have caught a stale render.)

## 9. Why did check_llm_copy_attractiveness pass while copy looked generic?
It inspects the **artifact JSON `i18n`** fields for structure/vocabulary. It does not (a) dump the
rendered DOM, nor (b) verify the reviewed `llm_judgment` is the thing that renders. Because the i18n
copy is decent, the JSON check passes — even though the reviewed LLM judgment is not what the
projection reads, and a fallback frame (e.g. the manual `HotspotPrediction` FocusBlock) could render
generic `{home}/{away}` template lines without the guard noticing.

## 10. Which guard failed to inspect rendered user-visible content?
ALL of them except `check_customer_visible_copy.py` (which only scans for FORBIDDEN words, not
freshness or copy quality). No guard asserts the rendered homepage primary == active package, the
rendered yesterday recap == prior closure, or that the rendered /predict|/recap copy is the reviewed
LLM content (not a fallback frame). That is the gap P4R closes.

## Root cause (two defects)
1. **Copy-wiring defect:** the reviewed LLM judgment (`llm_judgment`) is written by `apply` but never
   rendered — `buildStrongCallFromArtifact` reads `i18n`, which `apply` does not sync. Fix: `apply`
   must sync the zh `i18n.prediction`/`analysis` from the reviewed JSON (vi/my/en stay translations),
   so the rendered zh copy IS the reviewed LLM copy; and renderers must show COPY_MISSING /
   REVIEW_REQUIRED instead of a silent generic fallback.
2. **Verification defect:** the freshness/copy guards inspect artifacts, not the rendered DOM. Fix:
   add rendered-DOM guards (`check_rendered_daily_freshness`, `check_rendered_llm_prediction_copy`,
   `check_rendered_llm_recap_copy`, `check_homepage_live_content_wiring`) that dump the live/preview
   DOM and assert freshness + LLM-copy presence + no demo content.
