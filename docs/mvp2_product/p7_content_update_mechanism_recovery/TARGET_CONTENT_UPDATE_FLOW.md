# P7 — TARGET_CONTENT_UPDATE_FLOW

> The target daily content+update flow that reconnects the engine to the loop. Phase-by-phase, with the
> field/source/artifact at each step and the compliance invariants. "P0" = MVP recovery (operator-confirmed +
> wiring); "P1" = reconnect the model/LLM engine (Owner-gated). No auto-send anywhere.

## Before match day
- **Slate sync** — `mvp2_match_sync.py sync --date` from `manual_scores_<date>.md` → registry + recap_queue +
  runtime json (already works). No score invented.
- **Shortlist hotspot candidates** — `mvp2_editorial_agent.py prompt` prints the LLM selection prompt from the slate
  (already works; prompt-only). Operator runs the LLM, gets a ranked shortlist.
- **Pull available data fields** *(P1 reconnect)* — for each shortlisted fixture, run the model frame builder
  (Elo gap / last-10 form / H2H / Poisson scoreline bands / upset_band) → a factor frame with `source_ref` /
  `assumption_flag`. Needs only team names + the kaggle CSV (no Scout Pack required for Elo/form/H2H).
- **Prepare LLM prompt** — the frame + the existing ProductNarrative contract + guard wordlists.

## Match-day morning
- **Select hotspot** — operator confirms ONE fixture; **persist `selected_hotspot_<date>.json`** (date, fixture_key,
  home/away, source, prediction_artifact_path, operator_confirmed, status) AND make the runtime read it (P0 wiring).
- **Produce prediction artifact** — `manual_<slug>.json` with the structured shape:
  `data_snapshot` (model fields + source_refs, P1) · `modeling_output` (score band / lean / risk, P1) ·
  `llm_judgment` (tactical/why/external/t30 copy, P1) · `operator_confirmation` (the confirmed score call + any
  override, P0). For MVP-P0, `operator_confirmation` may stand alone (disclosed qualitative call, `confidence:null`).
- **Confirm score call and risk** — operator confirms `score_call` / `backup_score` / `risk_level` / `main_lean`
  (model-suggested in P1, operator-typed in P0). Never a probability/%.
- **Homepage points to the artifact-backed hotspot** — the lead resolves through `selected_hotspot` → artifact
  (`hasPredictionArtifact`), not slate order alone. No artifact ⇒ no lead prediction (P6 gate, kept).

## Pre-match
- **User sees the homepage score hook** — compact 俅哥主看 + 主比分/备选 + 冷门风险 teaser (P6, live).
- **User enters `/predict`** — ArtifactTacticalRoom: strong call + tactical depth + external expectation + T-30 +
  calibration line + `#live30` + ShareBlock (live).
- **Operator shares** — `/share/fixture/<key>?ref=<CODE>` card + QR + the send-kit copy (`mvp2_growth_cli.py package`),
  on Owner per-channel GO.

## T-30 (kickoff − 30, lineups out)
- **Update the T-30 correction artifact** — a persisted T-30 slot on the prediction artifact (placeholder pre-lineups;
  filled when lineups drop). P1: run `mvp2_build_rescore_diff` (announced XI/GK) + the rescore generator for the hotspot.
- **If no update, show the pending checkpoint honestly** — `方向待临场确认` / `比分待开球前 30 分钟确认`; never fabricate.
- **Operator sends the group update manually** — from the T-30 slot copy; no auto-send.

## Full time
- **Create the observation artifact** — `observation_<key>.json` keyed by the **same key** the slate uses (fix the
  numeric-id-only gap so manual fixtures carry over). `recap_ready:false` until a full recap exists.
- **Record the actual score** — from the manifest/manual slate (never invented).
- **Compare the prediction receipt** — pre_match_call → actual → hit / partial-hit / miss → deviation reason →
  calibration points → next_impact (the trust receipt; P5b shape).
- **Prepare recap or observation page** — `/recap/<key>` shows the observation receipt; P1: run the A4 model+LLM recap
  (archived-prediction sha256 provenance) to flip `recap_ready:true`.

## Next day
- **Yesterday's hotspot becomes the recap lead** — `featuredRecap` = first FINISHED fixture; its observation resolves
  by key (after the carryover fix).
- **New hotspot becomes the prediction lead** — the new `selected_hotspot` → artifact → homepage teaser. The loop closes.

## Invariants (every phase)
No auto-send · no betting/odds/盘口/投注 vocabulary · no fake recap (查看复盘 only when `recap_ready`) · no invented
score/probability (null → pending labels) · `external_expectation` only when a recorded signal exists · MTC = platform
points 不可提现/不可转让/不可交易 · every model-derived field carries a `source_ref` / `assumption_flag`; every
operator-confirmed field is disclosed as a qualitative scout call.
