# Reference-Site Intelligence Benchmark (v1)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Purpose:** Decompose the **information structure** of the reference sites/categories the Owner pointed at — so
> we know *what an intelligence read should contain* — and define a **Minimum Intelligence Pack v1** target.
> **Rule:** structure only. **No content is copied** from any site; ToS/scraping risks are flagged in
> `REAL_INTELLIGENCE_DATA_AVAILABILITY_AUDIT.md`. This is a design benchmark, not an integration.

---

## 1. Field structure by reference category (what each *exposes*)

### A. Official schedule / result pages (FIFA, league sites)
Modules: match list (date, kickoff, venue, group/round), team names + crests, **final score** & status
(live/HT/FT), goal timeline, basic match officials. → Authoritative for **fixture / result / venue**; nothing
predictive. **Mirror legally:** fixture/result/venue facts (also via API-FOOTBALL).

### B. Odds / 竞猜 sites
Modules: 1X2 prices, over/under, handicap, **odds movement over time**, "market %"/implied probability,
bookmaker comparison. → Rich "market signal", but **betting-adjacent**. **Our floor: excluded.** We do **not**
mirror odds; at most an abstract non-odds signal, Owner/compliance-gated (default: omit).

### C. SofaScore-type live/stat pages
Modules: lineups + formation, average positions/heatmap, live stats (shots, xG, possession, duels), player
ratings, momentum graph, H2H, standings, form (W/D/L last 5). → The "deep live" read. **High anti-scrape/ToS.**
**Use as a UI/field benchmark only**, source equivalent fields from API-FOOTBALL (paid).

### D. Transfermarkt
Modules: squad list + positions, **market value per player & squad total**, injuries/suspensions, transfers,
contract data. → Best for **squad_value_delta / injuries**. **High ToS risk** → manual reference only.

### E. Elo / 538-SPI-type model pages
Modules: team **rating**, win/draw/loss probabilities, projected table, rating change per match. → Benchmark for
**elo_delta / model_probability** and a sanity check on our baseline. Elo = reference; 538 SPI = archived
benchmark.

### F. Football-analytics stations (FBref / Understat / WhoScored)
Modules: xG/xGA, shot maps, possession-adjusted stats, set-piece data, player-level advanced metrics. → Feeds
**recent_form / model features**. Med/high ToS → licensed feed long-term, reference now.

**Synthesis:** an "intelligence read" the market expects = **fixture/result (A)** + **form/H2H/standings/lineups
(C/F)** + **squad value/injuries (D)** + **Elo/model probability (E)** + (market signal **B — we exclude**) +
media context. We currently hold only **A (partial)** + our **baseline model**.

---

## 2. Minimum Intelligence Pack v1 (target schema)

Status legend → **NOW**: in Evidence Pack v1 today · **DERIVE**: computable from synced data (no new source) ·
**OPERATOR**: needs operator/paid API sync · **REFERENCE**: manual/reference-only · **EXCLUDE**: compliance.

| Field | Source (audit ref) | Status | In customer UI today |
|---|---|---|---|
| `match_title` | fixture (1) | **NOW** | yes (header) |
| `kickoff_time` | fixture (1) | **NOW** | yes |
| `status` | fixture (1) | **NOW** | yes (recap banner) |
| `final_score` (if finished) | result/score (2,3) | OPERATOR (backend field) | **no** (settled, not surfaced) |
| `home_team` / `away_team` | team profile (4) | **NOW** | yes |
| `coach_home` / `coach_away` | coach (5) | OPERATOR | no → Evidence Pack: missing |
| `formation_home` / `formation_away` | lineup (7) | OPERATOR | no → missing |
| `key_players_home` / `key_players_away` | squad (6) | OPERATOR | no → missing |
| `missing_players` | injuries (9) | OPERATOR / REFERENCE | no → missing |
| `starting_lineup_status` (confirmed/probable/unavailable) | lineup (7) | OPERATOR | no → "unavailable" |
| `recent_form_5` | form (10) | DERIVE (from synced results) | no yet |
| `head_to_head_summary` | h2h (11) | DERIVE | no yet |
| `elo_delta` | Elo (13) | REFERENCE | no |
| `squad_value_delta` | Transfermarkt (14) | REFERENCE (high ToS) | no |
| `market_signal` / `odds_movement` | odds (15) | **EXCLUDE** | **no (compliance)** |
| `media_signal_summary` | media (16) | REFERENCE (human-authored) | no → missing |
| `model_probability` | model (19) | **NOW** | yes (win/draw/loss) |
| `model_delta_reason` | model/live (19) | NOW (current) / hidden on recap | current only |
| `scout_verdict` | model (19) | **NOW** (conservative on recap) | yes |
| `missing_data_notice` | Evidence Pack (21) | **NOW** | yes |
| `source_confidence` | meta | **NOW** (implied: baseline-only on recap) | yes (conservative note) |

**v1 reality:** ~7 fields are live now (`match_title`, `kickoff_time`, `status`, teams, `model_probability`,
`scout_verdict`, `missing_data_notice`, `source_confidence`); `recent_form_5` + `head_to_head_summary` are the
cheapest **DERIVE** upgrades (no new source); the player/coach/lineup/injury cluster is the **OPERATOR** upgrade;
`elo_delta`/`squad_value_delta`/`media` are **REFERENCE**; odds is **EXCLUDED**.

---

## 3. Roadmap implication (no code change here)
1. **NOW (shipped):** Evidence Pack states the 7 live fields + lists the missing cluster honestly.
2. **DERIVE (next, low risk):** compute `recent_form_5` + `head_to_head_summary` from the 64 synced WC2022
   results — no new source, no fabrication.
3. **OPERATOR (gated):** operator runs API-FOOTBALL sync (coach/squad/lineup/injury, paid plan + token on Render).
4. **REFERENCE (manual, careful):** Elo / squad-value / media as human-curated references with attribution.
5. **EXCLUDE:** odds/market — compliance floor; Owner decision required before any market signal.

## 4. Guardrails honored
Structure-only (no copied content) · odds excluded · no fabrication · no backend/API/DB change in this doc/sprint.
