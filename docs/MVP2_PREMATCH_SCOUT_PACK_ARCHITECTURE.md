# MVP-2 Pre-match Scout Pack — Architecture (design only)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only.
> Trigger: **API-FOOTBALL Day-2 Real Run = PASS** ([API_FOOTBALL_COVERAGE_CHECK](API_FOOTBALL_COVERAGE_CHECK.md)). This
> designs the backend data structure + cache architecture for MVP-2. **No DB/backend/frontend/ingestion/model/odds
> work this round.** Companions: [FOOTBALL_INTELLIGENCE_DATA_INTEGRATION_BLUEPRINT](FOOTBALL_INTELLIGENCE_DATA_INTEGRATION_BLUEPRINT.md) ·
> [API_FOOTBALL_PAID_PLAN_DECISION](API_FOOTBALL_PAID_PLAN_DECISION.md).
>
> **State: Internal Level-2 feasibility proven · Commercial MVP-2 not yet ready.**
> **Caveats carried (must stay visible):** (1) **WC2026 fixtures now return (72)** — the prior FREE-plan lock is
> lifted; (2) **injuries empty on WC2022 historical → unresolved** (second-source / current-season verify); (3)
> production rate-limit / commercial-use / SLA need **plan-verify**; (4) **frontend never calls API-FOOTBALL
> directly**; (5) **no token / no large payload committed**; odds excluded.

---

## 0. The evidence chain (product foundation)

The Day-2 run proved the chain links up — `match 8 fixture_id 855737` == Render `external_id AF-855737`:

```
Render match_id → API-FOOTBALL fixture_id → Kaggle final_score / actual_winner
  → API-FOOTBALL lineups / events / statistics / players / coach
  → scout feature snapshot (model + explanation)
  → Report Evidence Board v2
```

`match_mapping` + `source_ledger` (below) are the spine that keeps every field traceable to a real source.

---

## 1. MVP-2 goal — minimum credible Pre-match Scout Pack

A pre-match read is "credible" only when these are real (or explicitly `missing`):
`fixture` · `team` · `lineup` (confirmed/predicted) · `formation` · `coach` · `events history` (recent) ·
`fixture statistics` · `fixture players` · `squad / players` · `injuries (if available)` · `model baseline` ·
`feature explanation` · `missing evidence notice`. **No data, no AI deep analysis** — every absent field renders
`source required`, never AI-filled.

---

## 2. API-FOOTBALL source contract

Verification status from Day-2 (FREE plan): ✅ verified · ⚠️ empty/uncertain · 🔒 plan-locked.

| endpoint | purpose | required params | expected fields | status | rate-limit risk | cache | UI usage | fallback if missing |
|---|---|---|---|---|---|---|---|---|
| `/leagues` | confirm WC league/season | `id=1` | league, seasons | ✅ id=1 | low | static (days) | none (internal) | block |
| `/fixtures` | fixtures/results | `league=1&season=` | fixture id, teams, date, venue, status, score | ✅ 2022=64 · ✅ 2026=72 | low | season: long; live: short | match_core | "fixtures unavailable" |
| `/fixtures/lineups` | lineup + formation | `fixture=` | XI, subs, **formation**, coach, positions | ✅ | med (per fixture) | pre-match: T-60 refresh; post: frozen | lineup_board, formation_context | "首发未接入" |
| `/fixtures/events` | events history | `fixture=` | minute, type, team, player, detail | ✅ (20) | med | live: short; post: frozen | event_context | hide events |
| `/fixtures/statistics` | team match stats | `fixture=` | shots, possession, corners… | ✅ | med | live: short; post: frozen | team_statistics | hide stats |
| `/fixtures/players` | per-match player stats | `fixture=` | minutes, rating, goals, passes… | ✅ | med-high | post: frozen | player_statistics | hide player stats |
| `/injuries` | injuries/suspensions | `fixture=` or `league&season` | player, type, reason | ⚠️ empty (WC2022) | med | pre-match refresh | player_availability | "伤停未接入" |
| `/players` (`/players/squads`) | squad / player profile | `team=` / `season=` | player id, position, number | ✅ squad | high (paged) | season: long | player_availability, squad | "球员未接入" |
| `/teams` | team profile | `league=1&season=` | team id, name, country, venue | ✅ | low | season: long | match_core | name+flag only |
| `/coachs` | coach | `team=` | coach id, name, career | ✅ | low | season: long | coach_context | "教练未接入" |

**Note:** FREE plan ≈ 10 req/min, 100/day → MVP-2 is **impossible without aggressive caching + a paid plan**. The
per-fixture endpoints (lineups/events/statistics/players) are the budget hot-spots.

---

## 3. Backend schema proposal (design — NO DB change this round)

| table | purpose | key fields | source | refresh | license/commercial | MVP-2 required |
|---|---|---|---|---|---|---|
| `data_source` | vendor registry | id, name, base_url, license, commercial_flag | static | static | flag per vendor | **yes** |
| `source_request_log` | every vendor call (budget/rate audit) | source, endpoint, params_hash, status, results, cost, ts | runtime | append | — | **yes** |
| `canonical_team` | one true team | id, fifa_name, country, aliases | derived | rare | — | **yes** |
| `canonical_player` | one true player | id, full_name, dob, nationality, position | derived | rare | — | **yes** |
| `canonical_coach` | one true coach | id, name, dob, nationality | derived | rare | — | **yes** |
| `source_team_mapping` | vendor→canonical team | source, source_team_id, canonical_id, confidence | derived | rare | — | **yes** |
| `source_player_mapping` | vendor→canonical player | source, source_player_id, canonical_id, confidence, manual_review | derived | rare | — | **yes** |
| `source_coach_mapping` | vendor→canonical coach | source, source_coach_id, canonical_id, confidence | derived | rare | — | **yes** |
| `match_mapping` | the evidence-chain spine | render_match_id, af_fixture_id, kaggle_key, canonical_home/away | derived | rare | — | **yes** |
| `match_lineup_snapshot` | lineup at a time | fixture_id, team, status(confirmed/predicted), captured_at, players[], formation | AF lineups | pre-match T-60; freeze post | AF commercial flag | **yes** |
| `match_formation` | formation (or in snapshot) | fixture_id, team, formation, source | AF lineups | with lineup | AF | **yes** |
| `match_event` | events | fixture_id, minute, type, team, player, detail | AF events | live short; freeze post | AF | **yes** |
| `match_statistics` | team stats | fixture_id, team, stat, value | AF statistics | live short; freeze post | AF | **yes** |
| `match_player_statistics` | per-match player stats | fixture_id, player, minutes, rating, … | AF players | freeze post | AF | yes (depth) |
| `injury_report` | injuries/suspensions | player, team, type, reason, season/fixture, captured_at | AF injuries | pre-match | AF | partial (empty historical) |
| `coach_profile` | coach context | coach, team, formation_pref, career | AF coachs | season | AF | **yes** |
| `scout_feature_snapshot` | computed features + explanation | fixture_id, feature_key, value, inputs_ref, generated_at, explanation | internal | on data change | — | **yes** |
| `source_ledger` | per-field provenance/compliance | field, source, last_checked_at, confidence, license_status | runtime | per fetch | **license gate** | **yes** |

Kaggle (`final_score`/`actual_winner`, CC0 *confirm*) and StatsBomb (xG, **non-commercial → offline only**) feed
`match_mapping` / offline calibration — **not** commercial customer rows until license-confirmed.

---

## 4. Feature store design (fields + generation condition; NO algorithm)

| group | example fields | source | generation condition |
|---|---|---|---|
| `match_features` | stage, venue, both_lineups_present, days_rest, travel_distance | fixtures + manual geo | always (fixture); travel needs venue geo |
| `team_features` | recent_form_5, recent_xg(offline), style_tags | Kaggle(form) + AF stats + StatsBomb(offline) | form needs results; style needs stats/lineups |
| `player_features` | per90 stats, minutes_share, key_player_flag | AF players/squads | **requires fixture players + squad** |
| `coach_features` | formation_pref, coach_h2h | AF coachs + Kaggle(h2h) | h2h derivable offline |
| `availability_features` | injuries, suspensions, missing_key_player, squad_loss_index | AF injuries + lineup | **requires injuries (empty now) + lineup** |
| `tactical_features` | formation_matchup, set_piece, pressing | AF lineups/stats + manual | **requires formation + stats** |
| `risk_features` | upset_risk, overperformance_flag | derived (win_prob + xG offline) | needs xG(offline) for sustainability |

Each feature carries `inputs_ref` (which raw rows) → if any required input is `missing`, the feature is `missing`
(not AI-guessed). Algorithms are **out of scope** until paid-plan data + Owner approval.

---

## 5. Evidence Board v2 — frontend data contract

The backend serves a single read model; **every field is wrapped in a provenance envelope** so the UI can render
`available` data and an honest `source required` for the rest.

```jsonc
EvidenceBoardV2 = {
  match_core, lineup_board, coach_context, player_availability, formation_context,
  event_context, team_statistics, player_statistics, missing_evidence, source_ledger,
  ai_baseline, ai_explanation
}
// every leaf field:
Field<T> = {
  value: T | null,
  available: boolean,
  source: "api-football" | "kaggle" | "statsbomb" | "internal" | null,
  last_checked_at: string | null,
  confidence: number | null,        // 0–1 (entity-resolution / freshness)
  license_status: "ok" | "non_commercial" | "pending" | "excluded",
  fallback_text: string             // localized (zh/vi/en/mm); shown when !available
}
```

**Rules:** `available=false` → render `fallback_text` (e.g. "首发未接入 / source required"), never AI prose.
`license_status` ∈ {`non_commercial`,`pending`,`excluded`} → **hide from customer UI** (e.g. StatsBomb xG, odds).
`ai_explanation` may only reference fields whose `available=true && license_status=ok`.

---

## 6. Caching & rate-limit architecture

- **Frontend never calls API-FOOTBALL** — all vendor traffic via the **backend proxy** (token server-side only).
- **Redis cache, fixture-level:** `season`/`teams`/`coach` long TTL; `lineups` cached after the **pre-match
  refresh window** (poll ~T-60→kickoff); `events`/`statistics` short TTL live; **post-match → frozen snapshot**
  (immutable). Recap matches (WC2022) are **always frozen**.
- **Request budget:** FREE ≈ 10/min, 100/day. A single fixture's full pack ≈ 6–8 calls → **a handful of fixtures
  exhausts FREE/day**. MVP-2 needs a **paid plan** + cache-first reads + a nightly batch for static data.
- **Rate-limit guard:** 429 backoff (shipped in the verifier) + a server-side token-bucket + `source_request_log`
  to track spend and prevent runaway bills. **JWT + IP rate-limit** on our own API to stop scraping.
- **API key isolation:** key only in backend env (Render); never in frontend bundle, logs, or git.

---

## 7. Paid-plan verification gate (must pass before MVP-2 implementation)

| check | FREE result | paid re-verify target |
|---|---|---|
| WC2026 fixtures | ✅ **returned (72)** | resolved (confirm refresh SLA as tournament nears) |
| injuries | ⚠️ empty (WC2022) | non-empty on a current/upcoming fixture **or second source** |
| current-season availability | unknown | current season endpoints return data |
| rate limit | ~10/min, 100/day (429s) | req/min + req/day sufficient for fixture-day load |
| commercial usage | unconfirmed | commercial use permitted by plan terms |
| Render env | n/a | `API_FOOTBALL_KEY` set on Render (server-side) |
| production request budget | n/a | fixtures × endpoints × refresh ≤ plan/day with cache |

→ Detailed in [API_FOOTBALL_PAID_PLAN_DECISION](API_FOOTBALL_PAID_PLAN_DECISION.md).

---

## What this round does NOT do
No DB change · no app backend · no frontend · no UI polish · no auto-ingestion · no model algorithm · no odds · no
external operation. **Design only.**

## Next executable steps (5)
1. **Owner approves API-FOOTBALL paid plan** (low tier first).
2. **Operator** sets the key on Render / local env (server-side; gitignored).
3. **Re-run the verifier** → confirm WC2026 + injuries + rate limit (paid-plan gate §7).
4. If **PASS** → open a **new implementation PR** (off `main`, small/reviewable).
5. New PR builds **backend schema + ingestion prototype + Evidence Board v2** (still no public UI until verified).

## Guardrails honored
docs-only · no frontend/backend/API/DB change · token never committed/printed · no large payload · odds excluded ·
StatsBomb non-commercial · `42.2%` internal · external operation paused · PR #2 stays Draft.
