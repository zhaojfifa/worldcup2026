# MVP-2 Track A+ Evidence Expansion Sprint — Review

> Owner verdict 2026-06-12: A4 loop works but recap quality too thin (missed red-card impact on
> 1489369; 979139 flat; modeling too narrow). This sprint upgrades Track A to a multi-dimensional
> football evidence + recap intelligence pipeline. Branch `feature/mvp2-api-football-ingestion` ·
> PR #3 Draft · main untouched · operation paused · small private trial only · Track B untouched.

## 1. What was built (engineering = facts/schema/prompt/guard only)

| Layer | Implementation |
|---|---|
| Event impact (facts-only) | NEW `scripts/mvp2_build_event_impact.py` — phase timeline (0-15/16-30/31-45+/46-60/61-75/76-90+/91-105/106-120+), halftime/final score, decisive events (red cards, penalty goals, goals; VAR-ready) each with minute / team / player / score_before→after / men-on-pitch / man-advantage flag / rule-derived `changed_risk_interpretation` + `prematch_judgement_relation` (reason strings, not narrative); substitutions with off/on (forced-by-injury = "unknown", never inferred); GK signal from player stats |
| Extended dimensions | 17 dimensions per recap frame, each `{value, source, confidence, customer_visible_summary, internal_note, missing_evidence}`. Sourced now: key_player_load, extra_time_fatigue, substitution_depth, bench_quality, goalkeeper_reliability, penalty_history (kaggle shootouts), red_card_sensitivity, game_state_resilience, set_piece_threat, knockout/tournament_pressure (context). Honest gaps (named source needed, NEVER invented): age_profile, defensive_line_age, squad_experience, captain_core_stability, coach_adjustment_pattern, attacking_transition_speed |
| Frame wiring | `recap_frame()` in the v0.2 builder attaches both layers → 979139 historical + 1489369 real_recap frames carry them; generator passes them to the LLM with mandatory-engagement notices |
| External expectation signals | `docs/MVP2_EXTERNAL_EXPECTATION_SIGNALS_DESIGN.md` + stub frames `docs/data_audit/mvp2_external_signals/{1489369,1489371,1539000,979139}.external_signals.json` — 8 signals (media_heat, expert_consensus, social_buzz, public_prediction_bias, market_expectation, odds_implied_expectation, lineup_rumor_signal, injury_rumor_signal), ALL `missing_evidence:true` until an operator records them with named sources. **Internal-only**: market consensus recorded as direction+band, no prices, no bookmaker names; customer-safe vocabulary fixed (外部预期/市场共识/公开预测倾向); guard bans the betting vocabulary in 4 languages |
| Prompts | zh/vi/my prompts + generator notices: decisive events mandatory with minute+score+man-count; strength-validation vs event-driven distinction; direction-right ≠ scoreline-right; no event foresight; numbers only from non-missing dimensions; vi got an explicit final-self-check trap list |
| Guard (new checks) | red-card/penalty **mention requirement** when the frame records them · **PHANTOM event check** (mentioning a red card/penalty the frame does NOT record = fabricated fact) · predicted-red-card/penalty **foresight overclaim** bans (negation-aware: 无法预判… stays legal) · extended hindsight bans (全都料到/一切尽在掌握/knew everything…) · unsupported exact age (X岁/X tuổi) and workload (X km) claims when the source is missing · external-expectation claims without a recorded signal · handicap vocabulary additions (亚盘/让球盘/大小球/tài xỉu/chấp bóng/handicap) · my ဒေတာမရှိ aligned with the visible scanner. Selftests: guard 6/6 · queue 12/12 |

## 2. 1489369 red-card recap result (Owner questions answered by the regenerated narratives)

Frame facts: SA red 49' (score 1-0, 11v10) · Mexico's 2nd goal 67' **with man advantage** · SA red 84' (9 men) · Mexico red 90+2'. All three languages now guard-passed AND engage the events:
- zh hero: 「俅哥复盘：墨西哥2-0南非——方向对了，但比分被红牌放大」; judgement states the 67' goal came 11v10 after the 49' red, "比分被事件放大，不是纯实力碾压".
- Scoreline honesty kept: 2-0 explicitly outside the archived band (1-1/1-0/0-1), with the red card named as what pushed it out.
- Cold-risk-high validity: narrative keeps the risk framing as validated by structure (efficiency gap) while attributing scoreline inflation to the event.
- 30-min rescore distinction: what a pre-kickoff check could see (XI/GK) vs what no pre-match view could know (in-match red cards) — and the foresight ban guarantees no "predicted the red card" claim (first run actually tried「预判南非会吃两张红牌」in a NEGATED honest form; guard's negation-aware check keeps that legal).

## 3. 979139 historical recap upgrade result

Now sourced and used: Messi 120' + 2 goals + 9.3 rating vs Mbappé 120' + 3 goals (star burden, REAL minutes); 6 players ≥110' (extra-time fatigue); France's 41' double substitution; Lloris 7 saves vs Martínez 2; HT 2-0 → 80'+81' Mbappé swing → 108' Messi → 118' pen (momentum facts); Argentina/France shootout records from the kaggle archive (penalty history). Ages/caps remain `missing_evidence` — narratives reference them only as pre-match blind spots, no invented numbers (guard-enforced). The phantom-event check caught and killed a zh draft that blamed a nonexistent red card in this final.

## 4. Known source gaps (named, not papered over)

age_profile / defensive_line_age (needs squad birthdates feed) · squad_experience (caps) ·
captain_core_stability · coach_adjustment_pattern · attacking_transition_speed (possession-sequence
data) · injuries (endpoint returns 0 rows for these fixtures) · xG (still not ingested) · all 8
external signals (stub only — operator manual recording with named sources is the P0 path).

## 5. Verification

Guard 6/6 narratives PASS (1489369 zh/vi/my real_recap + 979139 zh/vi/my historical_recap) ·
guard selftest 6/6 · queue selftest 12/12 · build PASS · visible-copy scan 18/18 PASS ·
queue: 3 guard_passed per fixture-language for 1489369 with full supersede chains (incl. one
transient vi mock, superseded, unapprovable by design) · screenshots
`docs/qa_screenshots/mvp2_evidence_expansion/` · send-kit refreshed (quotes current guard-passed
fields only).

## 6. Compliance

No Track B code. No payment/referral/QR/reward runtime. No betting features; odds/market data is
design + internal stub only, with direction+band recording rules and 4-language customer bans.
Nothing sent; sends remain operator-manual behind queue approve + Owner GO. Engineering wrote zero
customer narrative.

## 7. Verdict (engineering self-assessment)

Evidence depth upgrade = **PASS pending Owner review**. The two target recaps now engage decisive
events with facts, the guard makes both omission (missing red card) and fabrication (phantom red
card) hard failures, and every new dimension is either sourced or honestly missing. Trial GO still
blocked on the Render SPA rewrite (unchanged operator action).
