# R1 — BASELINE_MATRIX

> Old vs current, across the four reference baselines. **Key finding (verified):** the old branches
> are strictly *behind* main — `git diff --stat main..feature/mvp2-growth-{p0-design,p1-1c-strongcopy}`
> shows them DELETING the scripts main now has (5,579 / 7,647 net deletions vs main). **Nothing of value
> lives only on an old branch.** The rich content machinery (ScoutScore frame + LLM narrative generators
> + guards + prompt contracts) is ALL on current main; it is simply **not wired into the daily-refresh
> manual-hotspot flow**. R1 is a *wiring* recovery, not a port.

| Refs | Commit |
|---|---|
| tag `main-backup-pre-p15b-daily-featured-copy-20260613` | `e3c73a3` |
| `feature/mvp2-growth-p0-design` | `5535c61` |
| `feature/mvp2-growth-p1-1c-strongcopy` | `0a73ee6` |
| current main | `f94895a` (R1 branched from here) |

## Capability matrix

| Capability | Old (tag / branches) | Current main | Verdict |
|---|---|---|---|
| **Rich prediction content** (main_lean, scoreline band, risk word, tactical_read, risk_factors w/ source_refs) | LLM `ProductNarrative` JSON for 5 fixed fixtures (855737/979139/1489369/1489371/2026_ba) | SAME 5 fixtures, fixture-locked; daily manual hotspot uses operator artifact | **KEEP** main's; **RECOVER** by wiring a generator for the daily fixture |
| **Structured prediction data** (win_prob/recommended_score/risk_level/risk_note/confidence) | backend `baseline.predict()` (seed-strength rule model) → `Prediction` → `/api/v1/matches` → `transform.ts` | SAME path exists, still imported by `useAppStore`, but feeds only the demoted mock tiles | **KEEP**; **RECOVER** by surfacing as source-tagged `model_fields` (P8 P0 did this for the artifact) |
| **ScoutScore model frame** (kaggle Elo/form/H2H/Poisson) | `mvp2_build_scoutscore_v0_2_factors.py` (+ `mvp2_build_trial_prediction_frame.py`) | SAME scripts present, runnable locally; produce frames for the 5 fixtures only | **KEEP**; **RECOVER** as the model-lookup step of a daily builder (P1 for new fixtures) |
| **LLM narrative generators** | `mvp2_generate_trial_prediction_narratives.py` / `mvp2_generate_product_proof_narratives.py` / `mvp2_generate_scoutscore_narrative.py` | SAME, present on main | **KEEP**; **RECOVER** by feeding the daily fixture's frame + prompt |
| **Prompt contracts** | `docs/prompts/mvp2_scoutscore_*` + `docs/MVP2_LLM_NARRATIVE_CONTRACT.md` | SAME | **KEEP** as the prompt-file template for the daily builder |
| **Strongcopy detail** (`buildStrongCall` projection, scoreband split, risk harmonize) | `frontend/src/growth/strongCallProjection.ts` | SAME + P5 artifact fallback + P8 `model_fields` precedence | **KEEP** main's (richer) |
| **Homepage score hook** | (added P6) lean + 主比分 + 备选 + 冷门风险 teaser | SAME; P8a fixed the contrast bug | **KEEP** |
| **Rich /predict tactical room** | `ArtifactTacticalRoom` (P4/P5) + ProductNarrative `ProductPredictView` | SAME + P8 数据与建模依据 block | **KEEP** |
| **T-30 update slot** | rescore generator `mvp2_generate_rescore_models.py` (LLM) → `#live30`; artifact `t30` slot (P7) | SAME; daily artifact carries a `t30` pending slot, no rescore model wired for the daily fixture | **KEEP** slot; **RECOVER** rescore-model wiring (P1) |
| **/recap receipt + full recap** | `ObservationReceipt` (receipt) + `mvp2_build_recap_frame_real.py` → LLM `real_recap` (A4) | SAME; daily uses observation receipt; A4 not run for the daily fixture | **KEEP** receipt; **RECOVER** A4 (P1) |
| **Share/copy/join operations** | `ShareBlock` + `shareTemplates` + `/share` cards + `/join` ref | SAME | **KEEP** |
| **Update/status logic** (lifecycle/freshness) | `mvp2_fixture_lifecycle.py` + `lifecycle.py` + `freshness.ts` | SAME, canonical, healthy | **KEEP** |
| **Daily slate + selected_hotspot** | (added P1.3/P6/P7) `mvp2_match_sync.py` + manifest + `selectedHotspot.json` | SAME | **KEEP** |
| **source_facts / model_fields on artifact** | — (did not exist) | **NEW in P8 P0** (source-tagged, win_prob/confidence null) | **KEEP** — R1 builds the *producer* for these |
| **Daily content PRODUCTION chain** (facts → prompt → review → artifact) | — never existed; artifacts hand-authored one-offs | — still hand-authored | **MISSING → R1 P0 BUILDS THIS** |

## What to keep / recover / discard / missing

- **KEEP (current main):** the entire rendering + projection + lifecycle + share + P8 `model_fields`/`source_facts` schema. Do not re-render or re-port.
- **RECOVER (wire existing main assets):** a **daily content production chain** that runs the model-lookup + prompt-generation + reviewed-LLM-merge into the daily prediction artifact, so the daily hotspot gets the SAME rich, source-tagged content the 5 fixed fixtures have — instead of a hand-authored one-off.
- **DISCARD:** nothing from old branches (they are behind main). `MatchDesk.tsx` remains dead code (P6 finding) — out of R1 scope.
- **STILL MISSING (the R1 gap):** (1) a builder that produces the daily artifact from facts+prompt+review (no auto-LLM); (2) prompt + reviewed-output file artifacts; (3) `content_chain` provenance on the artifact + `/internal/daily` readiness for it; (4) a `check_daily_content_flow.py` guard. **Until (1)-(4) exist, the product is UI-only and NOT recovered.**
