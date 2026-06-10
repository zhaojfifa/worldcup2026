# ScoutScore v0.2 — Modeling Frame (Model Designer)

> **Date:** 2026-06-11 · **Supersedes:** `MVP2_SCOUTSCORE_V0_MODEL_CARD.md` (v0.1, single-fixture replay).
> v0.2 is a **prediction-product frame**, not post-match commentary: the same factor set drives
> historical recaps (pre-match read → validation) and 2026 pre-match modeling (lean → risk → live update).
> Engineering computes the factor frame; **the LLM writes the judgement on top of it.**

## 1. Factor set (per fixture, both modes)

| Factor | What it measures | Data feed (real → ref / gap → assumption) |
|---|---|---|
| `baseline_strength` | long-run team strength gap | **Kaggle-derived Elo** (49k internationals, K=32, +60 home when not neutral, through match eve) — `derived:elo_kaggle`; official FIFA rank not ingested → noted |
| `recent_form` | last-10 W/D/L + goal diff, weighted to recency | Kaggle results through match eve — real |
| `lineup_integrity` | starters available vs expected spine | recap: Scout Pack `lineups`/`formation` (replay); 2026: **assumption_context** (no lineups yet) |
| `finishing_efficiency` | shots → goals conversion trend | recap: Scout Pack `team_statistics` (real); 2026: Kaggle goals-for trend (proxy, flagged) |
| `goalkeeper_delta` | GK performance gap | recap: Scout Pack `player_statistics` GK rating/saves (real); 2026: assumption_context |
| `event_momentum` | in-match swing risk (comeback windows, set pieces, pens) | recap: Scout Pack `events_summary` timeline (real); 2026: H2H volatility + shootout history (Kaggle) |
| `tactical_matchup` | formation/style collision | recap: Scout Pack `formation`+`coach` (real); 2026: recent formations unknown → assumption_context |
| `travel_environment` | venue, travel, climate, altitude | 2026 US summer venues — **assumption_context** (no fixture scheduled); recap: Qatar neutral (real, low impact) |
| `missing_data_risk` | how blind the model is (injuries, xG, market value not ingested) | always real (it lists OUR gaps) |
| `upset_risk` | composite: efficiency vs control divergence + GK delta + missing-data exposure vs strength gap | derived from the above |
| `live_30min_update_trigger` | what re-computes when lineups drop ~30' before kickoff | rule list: lineup_integrity / goalkeeper_delta / tactical_matchup re-score; lean + scoreline band re-issued |

Factor objects carry: `value/direction`, `pre_match_interpretation`, (recap) `post_match_validation`,
`source_refs[]`, `assumption: bool`, `data_status`. **No invented numbers:** anything without a feed is
`assumption_context` for the LLM, marked as such all the way to the page's internal fold.

## 2. Per-mode outputs (the frame the LLM receives)

Both modes: `pre_match_main_lean` (side + strength of lean, **no fake probability**) · `risk_factors`
(top factor risks) · `user_watch_next` · `subscription_hook_basis` (which locked layers exist).
Recap adds: `validated_factors` / `underweighted_factors` (factor → what the result proved/exposed).
2026 adds: `scoreline_band_basis` (Elo gap + form goals → plausible bands, labelled `model_estimate`) ·
`risk_level` (low/medium/high from upset_risk) · `live_30min_update_trigger` rules.

## 3. Kaggle-derived Elo (engineering, reproducible)

Standard Elo over `data/external/kaggle/results.csv` ordered by date: start 1500, K=32 (W/D/L = 1/0.5/0),
+60 pre-match home bonus when `neutral=FALSE`. Snapshot taken **at match eve** (855737/979139: 2022 date;
2026 sample: latest available rows, 2026-06). This is a **derived baseline**, labelled
`derived:elo_kaggle` — it is real data lawfully derived, never presented as official FIFA ranking.

## 4. Sample-specific notes

- **855737 (upset recap):** v0.1 said "paper strength assumption — Elo NOT ingested". v0.2 closes that:
  baseline_strength + recent_form now real (Kaggle). The story the factors must support: control ≠
  result; efficiency + GK delta + 2nd-half momentum decided it.
- **979139 (final recap):** strong-vs-strong → small Elo gap, both in form; event_momentum (80' double,
  108'/118', pens), goalkeeper_delta (decisive save + shootout), star dependence visible in
  `player_statistics`; upset_risk reframed as **volatility risk** (draw/pens likelihood).
- **2026_brazil_argentina (pre-match):** NOT a scheduled fixture — hypothetical knockout meeting,
  flagged `assumption_context: hypothetical_knockout_2026` internally; customer view says 若淘汰赛相遇.
  Real feeds: Elo snapshot 2026-06, last-10 form, H2H (incl. 2026-03 Brazil 1–2 France etc.), WC group
  schedules (Kaggle has the real 2026-06 fixtures). Gaps (squad value, injuries, lineups, venue) →
  assumption_context + live_30min triggers.

## 5. Boundaries & compliance

- Win/draw/loss **lean** + scoreline **band**, both labelled `model_estimate`; no percent claims, no
  hit-rate, no odds/handicap language anywhere.
- v0.2 is a modeling **frame** for product proof — not a trained/backtested model; no accuracy claim.
- The LLM may reason beyond the factors but may not contradict them or invent facts (injuries/xG);
  unknowns become "赛前需重点跟踪的变量" + live-30min triggers.
- Disclaimer rendered by every page: 历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。

## 6. Artifacts

`scripts/mvp2_build_scoutscore_v0_2_factors.py` →
`docs/data_audit/mvp2_scoutscore_v0_2/{855737,979139,2026_brazil_argentina}.factor_frame.json`
(consumed by `scripts/mvp2_generate_product_proof_narratives.py`).
