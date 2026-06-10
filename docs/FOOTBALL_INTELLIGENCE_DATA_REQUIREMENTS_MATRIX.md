# Football Intelligence — Data Requirements Matrix

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only.
> Parent: [GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN](GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN.md).
> Per-field requirements across 7 data domains. **No source is scraped; odds excluded; AI never fabricates.**

**Legend** — value (user/model/content): `H`/`M`/`L`. available_now: `Y`/`N`/`P`(partial/offline).
MVP_level: minimum level the field belongs to (0/1/2/3). must_have = must_have_for_credible_analysis.
ai_gen = can_ai_generate_without_data (`N` = must come from data; `summary` = AI may summarize *existing* data only).
**source_candidate** abbreviations: `existing`=Render API · `KG`=Kaggle · `AF`=API-FOOTBALL · `TS`=TheSports ·
`SM`=Sportmonks · `SR`=Sportradar · `SB`=StatsBomb(non-commercial WC2022) · `ref`=reference-only site · `manual`=operator input.

---

## A. Match Result Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| fixture | H | H | M | existing/AF/KG | Y | 0 | Y | N | hide match |
| kickoff | H | M | L | existing | Y | 0 | Y | N | "—" |
| final_score | H | H | H | KG/AF/TS | P (8,13 shown; 64 aligned offline) | 1 | Y | N | "settled, no scoreline" |
| actual_winner | H | H | H | KG/AF/TS | P (8,13) | 1 | Y | N | upset tag hidden |
| competition_stage | M | M | M | existing/AF/KG | P (derivable) | 1 | N | N | omit |

## B. Team & Tactical Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| tactical_style | H | M | H | TS/SM/AF · WhoScored ref | N | 2 | Y | N | "Team Style: source required" |
| strengths | H | M | H | TS/SM/manual | N | 2 | Y | N | source required |
| weaknesses | H | M | H | TS/SM/manual | N | 2 | Y | N | source required |
| formation | H | H | H | AF/TS/SM/SR | N | 2 | Y | N | missing |
| attacking_side_preference | M | M | M | TS/manual · FBref ref | N | 2 | N | N | omit |
| set_piece_strength | M | M | M | manual · FBref/SB ref | N | 2 | N | N | omit |
| pressing_style | M | M | H | SB/FBref ref · SR | N | 2-3 | N | N | omit |
| defensive_vulnerability | M | H | H | TS/SM/manual | N | 2 | N | N | omit |

## C. Player & Squad Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| squad_list | H | M | M | AF(paid)/TS/SM/SR | N | 2 | Y | N | missing |
| starting_lineup | H | H | H | AF/TS/SM/SR (near KO) | N | 2 | Y | N | "unavailable" |
| predicted_lineup | H | H | H | TS/SM · WhoScored ref | N | 2 | Y | N | missing |
| substitutes | M | M | M | AF/TS/SM | N | 2 | N | N | omit |
| injuries | H | H | H | AF(paid)/TS/SM · Transfermarkt ref | N | 2 | Y | N | no "squad intact" claim |
| suspensions | H | H | M | AF/TS · Transfermarkt ref | N | 2 | Y | N | missing |
| player_rating | M | M | M | TS/SM · SofaScore ref | N | 2-3 | N | N | omit |
| player_position | M | M | M | AF/TS/SM | N | 2 | N | N | omit |
| key_player_availability | H | H | H | derived (injuries+lineup) | N | 2 | Y | N | missing |
| market_value / squad_value | M | L | M | TS · Transfermarkt ref | N | 2 | N | N (reference) | omit / reference |

## D. Coach Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| coach_name | M | L | M | AF(coachs,paid)/TS · Transfermarkt ref | N | 2 | Y | N | missing |
| preferred_formation | M | M | H | TS/SM/manual | N | 2 | N | N | omit |
| coach_win_rate | M | M | M | TS/derived · SofaScore ref | N | 2 | N | N | omit |
| coach_H2H | M | M | M | derived(KG)/TS · Transfermarkt ref | P (derivable offline) | 2 | N | N | omit |
| tactical_history | L | M | H | manual · The Analyst ref | N | 2-3 | N | N | omit |
| substitutions_pattern | L | M | M | SR/manual | N | 3 | N | N | omit |

## E. Advanced Stats Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| xG | H | H | H | SB(WC2022 free, non-comm) · Understat/FBref ref · Opta/SR licensed | P (offline calib only) | 2-3 | Y (for quant) | N | missing; offline-calib only |
| xGA | H | H | H | SB · Opta/SR | P (offline) | 2-3 | Y | N | missing |
| shot_quality | M | H | M | SB/Opta | P (offline) | 3 | N | N | omit |
| shot_location | M | M | M | SB/Opta | P (offline) | 3 | N | N | omit |
| possession | M | M | M | AF/TS/SM | N | 2-3 | N | N | omit |
| progressive_passes | M | H | M | SB/FBref ref/Opta | P (offline) | 3 | N | N | omit |
| pressures | M | H | M | SB/FBref ref | P (offline) | 3 | N | N | omit |
| defensive_actions | M | M | M | SB/FBref ref | P (offline) | 3 | N | N | omit |
| goalkeeper_advanced | L | M | M | SB/FBref ref | P (offline) | 3 | N | N | omit |

## F. Live Intelligence Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| live_events | H | H | H | AF(live)/TS/SR · SofaScore comm | N | 3 | Y (for live) | N | hide live |
| attack_momentum | M | M | H | SR · SofaScore ref | N | 3 | N | N | omit |
| heatmap | M | M | M | SR/SB · SofaScore ref | N | 3 | N | N | omit |
| substitutions_live | M | M | M | AF/TS/SR | N | 3 | N | N | omit |
| cards_live | M | M | M | AF/TS/SR | N | 3 | N | N | omit |
| live_shots | M | M | M | AF/TS/SR | N | 3 | N | N | omit |
| live_xG | M | H | H | SR/Opta · SB comm | N | 3 | N | N | omit |
| live_player_rating | M | M | M | TS/SR · SofaScore ref | N | 3 | N | N | omit |

## G. Content / Scout Layer
| field | user | model | content | source_candidate | now | lvl | must | ai_gen | if_missing_ui |
|---|---|---|---|---|---|---|---|---|---|
| scout_summary | H | L | H | internal AI (on real data) | P (generic now → real after data) | 1-2 | Y | summary-only | data-status if no data |
| tactical_matchup | H | M | H | internal AI (on tactical data) | N | 2 | Y | N (needs B/C/D) | source required |
| model_explanation | M | M | M | internal (on features) | P (baseline only) | 1-2 | N | summary-only | baseline-only |
| risk_explanation | M | M | M | internal (on factors) | P | 1-2 | N | summary-only | generic label |
| missing_evidence_notice | H | L | H | frontend (Evidence Pack — **DONE**) | Y | 1 | Y | Y (it *is* the no-data UI) | always show |
| zh_copy | H | L | H | internal | Y | 0-3 | Y | Y (localization) | "—" |
| vi_copy | H | L | H | internal | Y | 0-3 | Y | Y (localization) | **0 Han** |

---

## Reading
- **Available now (Y):** only Layer A (fixture/kickoff), partial final_score/winner (matches 8 & 13), and Layer G's
  Evidence Pack + localization. **Everything in B/C/D/E/F is `N` (not connected).**
- **Offline-only (P):** `coach_H2H`, full `final_score`/`winner` (Kaggle, 64 aligned), and the xG/advanced cluster
  (StatsBomb WC2022, **non-commercial → calibration only, not customer UI**).
- **must_have for credible analysis & still N:** tactical_style, formation, starting/predicted lineup, injuries,
  suspensions, key_player_availability, coach_name, xG/xGA, live_events, tactical_matchup. → These define the gap to
  Level 2/3.
- **`ai_gen` is `N` for every data field** — the core principle. AI only *summarizes* real data (Layer G).
