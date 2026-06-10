# Football Intelligence — Data Integration Blueprint

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-first.
> Unifies data sources, product modules, model factors, engineering architecture and compliance into one plan.
> Companions: [GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN](GOAL_DRIVEN_FOOTBALL_INTELLIGENCE_REDESIGN.md) ·
> [FOOTBALL_INTELLIGENCE_DATA_REQUIREMENTS_MATRIX](FOOTBALL_INTELLIGENCE_DATA_REQUIREMENTS_MATRIX.md) ·
> [GOAL_DRIVEN_DATA_SOURCE_STRATEGY](GOAL_DRIVEN_DATA_SOURCE_STRATEGY.md) · [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md)
>
> **⚠️ Compliance reframing (mandatory).** The design input contained gambling framing (竞猜/盘口/走地/滚球/大小球/
> 让球/"反向买入"). Per Owner instruction + the project compliance floor, **all such terms are downgraded** to:
> 赛前情报 · 风险判断 · 模型解释 · 情报提示 · 比赛走势观察. **Odds/market data is EXCLUDED** unless Owner separately
> approves. No betting/staking advice anywhere. Mapping table in §8.
> **Guardrails:** reference sites (WhoScored/SofaScore/FotMob/Understat/Transfermarkt/FBref/Total Football Analysis/
> The Analyst) are **structure/field/UX references only — never scraped**; **frontend never calls a third-party
> vendor API directly**; tokens never committed; any API/paid/DB/backend wiring is **Owner-gated**.

---

## 0. First principles — what we are building

A **World Cup 2026 AI football-intelligence product** whose value is **concrete detail backed by real data**, not
fluent copy. The build chain is one-directional:

```
Data Source → Entity Resolution → Feature Engineering → Model + Explanation → UI
```

**Core law: No data, no AI deep analysis.** Every dimension without data renders `missing / source required`. AI is
the **explanation layer only** — it reads structured fields, identifies variables, explains conflicts, and writes a
scout summary; it never invents players, lineups, injuries, tactics, xG or live events.

**Eight questions this blueprint answers:** (1) the end-state product; (2) per-module data needs; (3) which sources
supply them; (4) what we already have; (5) what must be vendor-verified (API-FOOTBALL/TheSports/Sportmonks/
Highlightly/Sportradar); (6) what is reference-only; (7) which model factors need data before AI can explain; (8)
which modules must be hidden/downgraded now.

---

## 1. Product Module → Data Requirement → Source Candidate

Sources: `AF`=API-FOOTBALL · `TS`=TheSports · `SM`=Sportmonks · `HL`=Highlightly · `SR`=Sportradar ·
`SB`=StatsBomb(non-commercial) · `ref`=reference-only site · `manual`=operator. **Status now:** what we actually have.

### Module 1 — Matchup Dashboard  *(ref: SofaScore/FotMob — structure only, no UI copy)*
- **Fields:** fixture · team · status · current_score · win_probability · live_events · live_statistics ·
  attack_momentum *(reframed: 比赛走势观察)* · possession · dangerous_attacks · shots · cards · substitutions.
- **Sources:** AF · TS · SM · HL · SR.
- **Status now:** fixture + baseline win_prob = **have**; live_events / momentum / live_statistics = **unverified**.
- **Rule:** MVP-2 → **static** Matchup Dashboard first; MVP-3 → real-time momentum. **No live API → no "live correction".**

### Module 2 — Starting Lineup + Formation Board
- **Fields:** starting_lineup · substitutes · formation · player_position · jersey_number · team_coach ·
  lineup_timestamp · confirmed/predicted status.
- **Sources:** AF `fixtures/lineups` · TS · SM · HL · SR.
- **Status now:** **not connected**; **API-FOOTBALL has a base URL already → verify first.**
- **Rule:** no lineup → show "首发数据未接入"; **never write "formation counter / 阵型克制".**

### Module 3 — Player Intelligence Board
- **Fields:** player_id · nationality · position · club · minutes · player_rating · goals/assists · pressures/90 ·
  interceptions · progressive_passes · defensive_actions · injury_status · suspension_status · market_value(if licensed).
- **Sources:** AF `players`/`squads` · TS · SM · HL · advanced via FBref/SB/Opta/SR · Transfermarkt (field ref / licensed only).
- **Status now:** **not connected.**
- **Rule:** **no deep player card now**; design the **schema only — no fake UI.**

### Module 4 — Tactical Matchup Tags  *(ref: WhoScored styles — must be real data or human scout input)*
- **Fields:** tactical_style · strengths · weaknesses · attacking_preference · defensive_vulnerability ·
  set_piece_strength · pressing_style · formation_matchup.
- **Sources:** TS/SM/AF (if available) · internal scout note · manual · WhoScored ref only.
- **Status now:** **not connected.**
- **Rule:** no real tactical tags → **no "tactical counter" copy**; show `source_required`.

### Module 5 — Missing-Player Impact  *(ref: Transfermarkt full data)*
- **Fields:** injuries · suspensions · player_importance · minutes_share · goals/assists · xG_contribution ·
  expected_starter_status · squad_depth · replacement_quality.
- **Sources:** AF `injuries` · TS · SM · SR · Transfermarkt (ref/licensed).
- **Status now:** **not connected.**
- **Rule:** **never write "key absence impact X%" without a model + data**; define a `squad_loss_index` schema;
  **`impact_score` must cite its algorithm source**; result is a **risk/intelligence note, NOT a betting line**
  (the design's "→ 盘口/大小球竞猜提示" is dropped → "→ 风险判断 / 情报提示").

### Module 6 — xG / Shot-Quality Board  *(ref: Understat — strip the luck component)*
- **Fields:** xG · xGA · shot_quality · shot_location · shot_time · big_chances · post_shot_xG(if available).
- **Sources:** **StatsBomb Open Data** (WC2022, **non-commercial → internal calibration only**) · Opta/SR/StatsBomb
  licensed (commercial) · Understat/FBref ref only.
- **Status now:** StatsBomb = **offline internal calibration OK; non-commercial → NOT in customer UI**; commercial UI
  needs a licensed source.
- **Rule:** **do not publicly show xG** until a compliant licensed source is confirmed; build an internal
  calibration doc. Won-but-low-xG / lost-but-high-xG → a **model-explanation/risk note** ("结果可能不可持续"), **not** a betting prompt.

### Module 7 — Live Lineup & Tactical Shift
- **Fields:** live_events · substitutions · red/yellow_cards · lineup_changes · formation_changes ·
  live_player_positions · live_momentum.
- **Sources:** TS · AF live · SM live · SR · SofaScore commercial (if available).
- **Status now:** **unverified**; the current LINEUP WATCH is a **demo** and is already hidden on recaps.
- **Rule:** no live API → **hide live correction / tactical shift** entirely.

---

## 2. Data Source Priority Plan

| # | Source | Why | Verify fields | Constraint |
|---|---|---|---|---|
| **P1** | **API-FOOTBALL** | base URL + service env already exist; lowest eng cost; verify Level 2 immediately | fixtures · lineups · events · statistics · fixture players · injuries · teams · players · coachs · WC2022 · WC2026 | paid plan + operator token |
| **P2** | **TheSports** | closest to low-latency live scores/lineups/events (mainland CDN); strong **live** base | lineups · injuries · events · player stats · coach · formations · WC2022 historical · WC2026 fixtures | 15-day trial pending; sales pricing |
| **P3** | **Sportmonks** | first TheSports alternative; WC/lineups/squads/coaches/stats | same Level-2 set | €29+/mo; WC needs paid league plan; 14-day trial |
| **P4** | **Highlightly** | low-cost lightweight backup | national-team / World Cup coverage; lineups/injuries | free 100/day; verify WC coverage |
| **P5** | **StatsBomb Open Data** | WC2022 xG / 360 internal calibration | xG · events · freeze-frames | **non-commercial → not in commercial UI** |
| **P6** | **Sportradar / Opta / Stats Perform** | enterprise long-term route | full deep + live | high cost + long sales cycle → **MVP defer** |
| **P7** | **SerpApi** | Google-Sports cross-check | final_score / standings | not a primary source; no Level-2 depth |

**Designer note reconciled:** the designer proposed **TheSports as the full real-time base** (valid for the **live**
layer — low latency, CDN). Owner's stated priority is **API-FOOTBALL first** (cheapest Level-2 validation, existing
env). → **P1 API-FOOTBALL for Level-2 now; P2 TheSports as the live base candidate (Level 3), trial pending.**
**TheSports no longer blocks Level-2 validation.**

---

## 3. Entity Resolution / ID Alignment

TheSports / API-FOOTBALL / FBref / Transfermarkt / Kaggle / StatsBomb use **inconsistent IDs and name spellings**
(multilingual, small-nation players). Without a **canonical ID layer**, the model will mis-join players/teams.

**Canonical tables:** `canonical_team` · `canonical_player` · `canonical_coach` · `match_mapping` ·
`competition_mapping`, plus `source_{team,player,coach}_mapping`.

**Join keys (multi-factor composite):** FIFA official name · source name · country/nationality · date_of_birth ·
shirt_number · club · position · source_id → produce a `confidence_score` and a `manual_review_required` flag.

**Proven precedent:** the Kaggle alignment already built a small team normalizer (zh→en + USA→United States) and
matched 64/64 ([kaggle_wc2022_cross_validation.json](data_audit/kaggle_wc2022_cross_validation.json)) — the same
pattern scales to players/coaches across vendors. **Entity resolution is the first engineering prerequisite** before
any multi-source feature is trustworthy.

---

## 4. Feature Engineering for World Cup 2026

Each factor: `required_data · current_status · source_candidate · can_build_now · ui_explanation · compliance_risk`.
**All are intelligence/risk explanations — never betting lines.**

| Factor | required_data | current_status | source_candidate | can_build_now | ui_explanation | compliance |
|---|---|---|---|---|---|---|
| **Formation Matchup** → `formation_advantage_score` | coach preferred formation · confirmed lineup formation · opponent formation · midfield overload · wing-back exposure | none | AF/TS/SM | **no** | "阵型对位:中场人数/边路暴露" | low |
| **Missing-Player Impact** → `squad_loss_index` | starter absence · player importance · replacement quality · xG contribution · defensive action share | none | AF injuries + TS/SM + SB(xG, offline) | **no** | "核心缺阵减损(模型指数,标注算法)" | low (no odds) |
| **Fatigue / Travel** → `fatigue_score` | previous venue · current venue · travel distance · rest days · timezone shift | **partial** (venues/dates derivable; WC2026 hosts US/CA/MX) | fixtures (AF) + manual venue geo | **partial** | "体能/旅行:飞行距离+休息日差" | low |
| **Chemistry** → `chemistry_score` | same-club connections · repeated NT starts · club-teammate links · minutes together | none | squads (AF/TS/SM) + lineups history | **no** | "默契:同俱乐部连线/同首发次数" | low |
| **xG Sustainability** → over/under-performance flag | recent goals · recent xG · xGA · shot quality | **partial** (StatsBomb WC2022 offline, non-commercial) | SB(offline) · Opta/SR(commercial) | **partial (internal only)** | "运气成分:结果可能不可持续(模型解释)" | med (license) |
| **Live Momentum** → `live_shift_score` | live events · attack momentum · shot volume · cards · subs | none | TS/AF live/SR | **no** | "比赛走势观察(实时)" | low |

**Reading:** only **Fatigue/Travel** (partly) and **xG Sustainability** (internal/offline) are buildable now; the
rest need Level-2/3 vendor data. **AI cannot explain a factor that has no data.**

---

## 5. Data Architecture

1. **Ingestion layer** — scheduled REST pull (pre/post, minute-level) · live websocket/push **if the vendor
   supports it** (TheSports/SR) · manual operator import · offline CSV/JSON import (Kaggle/StatsBomb).
2. **Normalization layer** — entity alignment (§3) · schema validation · deduplication · `source_confidence`.
3. **Feature store** — `match_features` · `team_features` · `player_features` · `coach_features` · `live_features` ·
   `advanced_stats` (slot reserved).
4. **Model layer** — baseline probability → feature-adjusted probability → calibration → explanation generator
   (AI draft-only, forbidden-word filter, no auto-publish).
5. **Serving layer** — **backend proxy only; the frontend NEVER calls a vendor directly** · Redis cache (second-level
   TTL for live scores/events; pub/sub) · CDN / static snapshot (SSR/ISR for squads/coach/tactics white-papers) →
   survives the 90-minute peak.
6. **Compliance layer** — token isolation (server-side only) · source attribution · license flags ·
   commercial-use status · rate-limit + JWT guard (anti-scrape, prevent runaway vendor bills) · **no odds by default** ·
   logos/headshots → internal abstract/compliant placeholders unless licensed.

**Dual fetch channel (designer-adopted):** in-match (second-level) via **websocket** silent partial refresh;
pre/post (minute-level) via **REST**. Both terminate at the backend proxy; the browser only talks to our backend.

---

## 6. PR #2 handling recommendation

- **Option 1 — keep PR #2 as a full discovery PR** (all data-audit + Evidence-Pack/Real-Recap frontend + strategy docs).
- **Option 2 — split** into: **PR-A** data audit + Kaggle alignment · **PR-B** Evidence Pack / Real Recap frontend ·
  **PR-C** data-source strategy / Level-2 validation docs · **PR-D** vendor verification scripts.

**Recommendation: keep PR #2 as the discovery PR for now (Option 1, stay Draft); split at the implementation
boundary (Option 2) once a data provider is chosen.** Reasons: PR #2 is still **discovery/Draft** and internally
consistent; splitting now adds overhead with no merge imminent. When Owner picks a provider and real Level-2 wiring
starts (backend/API/DB — Owner-gated), open **PR-B (frontend)** and **PR-D (verifier scripts)** as small, reviewable
PRs off `main`, and keep the discovery docs (PR-A/PR-C content) as the reference trail.

---

## 7. Next executable sprint — 7-day plan

| Day | Task | Output | Gate |
|---|---|---|---|
| **1** | API-FOOTBALL Level-2 verification script | `scripts/verify_api_football_level2.py` (**shipped this sprint**; token_required until operator runs) | operator token |
| **2** | API-FOOTBALL coverage report | **Day-2 run = `blocked_by_token`** (no key provisioned; 0 calls); verifier hardened (4 var names) → `docs/API_FOOTBALL_COVERAGE_CHECK.md` | operator token |
| **3** | TheSports trial form / token follow-up | trial applied; `docs/THESPORTS_TRIAL_VERIFICATION.md` (19-pt checklist) | Owner/operator |
| **4** | Sportmonks / Highlightly account feasibility | quick feasibility note (free plan / trial) | operator |
| **5** | Kaggle H2H / recent_form derive | extend `audit_kaggle_wc2022.py` (offline; internal) | none (offline) |
| **6** | Frontend downgrade plan implementation | **only if Owner approves** (else stays a doc spec) | **Owner** |
| **7** | Owner decision review | choose data-provider path (Decision Table) | **Owner** |

---

## 8. Compliance downgrade mapping (design input → product)

| Design-input term (gambling) | Product term (compliant) |
|---|---|
| 竞猜算力 / 竞猜提示 | 模型解释 / 情报提示 |
| 大小球 / 让球 / 盘口偏向 | 风险判断（不含盘口；odds 排除） |
| 滚球盘 / 走地 决策 | 比赛走势观察 |
| 反向买入受让方 / 买小球 | **删除（不提供任何投注建议）** |
| Attack Momentum（竞猜用途） | 进攻势头 / 比赛走势观察（情报视角） |
| "核心减损 → 盘口偏向" | "核心减损指数（模型）→ 风险判断" |
| odds / market / handicap | **EXCLUDED unless Owner separately approves** |

**Designer's closing question** ("E-R diagram first, or a Python momentum/xG model first?") is **directed to the
Owner.** ClaudeT recommendation: **(a)** ship the API-FOOTBALL Level-2 verifier (Day 1, done) and design the
entity-resolution E-R schema (§3) first — they unblock everything; **(b)** defer the Python win-probability model
until real Level-2 data is connected (building a "竞猜胜率" model now would have no real inputs and risks
betting framing — out of scope under the compliance floor).

---

## Guardrails honored
docs-first · no frontend/backend/API/DB change (the verifier is a standalone ops script, token-gated, makes no calls
without an operator token) · reference sites not scraped · frontend never calls vendors · odds excluded · tokens
never committed · StatsBomb non-commercial (offline only) · `42.2%` internal · PR #2 stays Draft.

## Sources (checked 2026-06-10)
API-FOOTBALL [docs](https://www.api-football.com/documentation-v3) · TheSports [api](https://www.thesports.com/api) ·
Sportmonks [pricing](https://www.sportmonks.com/football-api/plans-pricing/) · StatsBomb [open-data](https://github.com/statsbomb/open-data) ·
Highlightly [football-api](https://highlightly.net/football-api/) · Sportradar [soccer](https://developer.sportradar.com/soccer/reference/soccer-api-overview).
