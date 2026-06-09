# Real Match Intelligence Selection (Data Recon)

_Created 2026-06-09 · Harness-X Real Match Intelligence Sprint · Data recon (Engineering Role)._

> **Honesty rules:** these are **real fixtures from public news/official sources** (URLs below), **not**
> seed and **not** API-synced yet. Claude has **no Render `$ADMIN_API_TOKEN`** → cannot run the
> API-FOOTBALL sync → `api_available = unknown` for all (operator verifies on Render). **No fabricated
> data; no fabricated results; no win-prob/model numbers here** (see `REAL_MATCH_MODELING_REVIEW.md`).

## Context (verified 2026-06-09)
- **FIFA June international window:** 2026-06-01 → 2026-06-09 (pre-tournament warm-up friendlies).
- **World Cup 2026 opener:** 2026-06-11, **Mexico vs South Africa**, Estadio Azteca, Mexico City
  (Group A: Mexico, South Africa, Korea Republic, Czechia). Group stage 2026-06-11 → 06-27.

## Candidate table
| match_candidate_id | competition_name | league_id | season | home_team | away_team | kickoff_time | status | source_type | source_reference | api_fixture_id | api_available | result_available | usable_for_prematch | usable_for_recap | selected_for_trial | reason_for_selection | data_risk_note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RMI-01 | FIFA World Cup 2026 (opener) | 1 | 2026 | Mexico | South Africa | 2026-06-11 (Estadio Azteca) | upcoming | news/official | FIFA + Yahoo + Sky | unknown | unknown | no | **yes** | no (not played) | **YES (pre-match)** | WC opener; host nation; high attention; clean pre-match Scout target | opponent confirmed by 3 sources; kickoff local TBD; verify in API as league=1 |
| RMI-02 | International friendly | 10 | 2026 | Brazil | Egypt | ~2026-06 (window 1–9) | finished | news | Football365 / FIFA / StrikerReport | unknown | unknown | yes (2-1) | no | **yes** | **YES (recap)** | marquee team for vi audience; clear result for recap/settlement test | exact date/venue to confirm; result 2-1 per news, verify before settlement |
| RMI-03 | International friendly | 10 | 2026 | Argentina | Honduras | ~2026-06 (window 1–9) | finished | news | Football365 / StrikerReport | unknown | unknown | yes (2-0) | no | **yes** | **YES (recap)** | Argentina marquee for vi; decisive result | verify date/result before settlement |
| RMI-04 | International friendly | 10 | 2026 | Switzerland | Australia | 2026-06-06 | finished | news | ESPN (gameId 401869743) | 401869743 (ESPN, not API-FOOTBALL) | unknown | yes (1-1) | no | yes | no | strong single-source (ESPN match report); draw = good risk-watch example | ESPN id ≠ API-FOOTBALL fixture id; verify mapping |
| RMI-05 | International friendly | 10 | 2026 | Portugal | Chile | ~2026-06 (window 1–9) | finished | news | Football365 / StrikerReport | unknown | unknown | yes (2-1) | no | yes | no | backup recap candidate | verify date/result |
| RMI-06 | FIFA World Cup 2026 | 1 | 2026 | Canada | (TBD) | 2026-06-12 | upcoming | news/official | Wikipedia / Yahoo | unknown | unknown | no | partial | no | no | host nation day-2; opponent not confirmed in sources | opponent TBD — do not publish until confirmed |
| RMI-07 | FIFA World Cup 2026 | 1 | 2026 | United States | (TBD) | 2026-06-12 | upcoming | news/official | Wikipedia / Yahoo | unknown | unknown | no | partial | no | no | host nation day-2; opponent not confirmed | opponent TBD — confirm before use |

## Selection for this trial (≥3 candidates · ≥1 upcoming · ≥1 finished)
- **Pre-match (upcoming):** **RMI-01 Mexico vs South Africa** (WC opener, 2026-06-11).
- **Recap (finished):** **RMI-02 Brazil 2-1 Egypt** and **RMI-03 Argentina 2-0 Honduras**.
- (RMI-04 Switzerland 1-1 Australia kept as a strong-source backup recap; RMI-06/07 parked until opponent confirmed.)

## API availability (honest)
`api_available = unknown` for all rows — Claude has no Render token and did not run the sync.
**Operator must verify on Render** whether the API-FOOTBALL key plan returns:
- league `10` (international friendlies) season `2026` for RMI-02/03/04/05, and
- league `1` (World Cup) season `2026` for RMI-01.
If a fixture is **not** returned by the key, mark it `api_available = no` in
`DATA_SOURCE_SYNC_VERIFICATION.md` and treat it as `public_source` only (operator-manual preview) —
**never relabel news data as API data.**

## Sources
- [FIFA — Estadio Azteca hosts opening match](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/estadio-azteca-mexico-city-host-opening-match-world-cup-2026)
- [Yahoo Sports — 2026 WC daily schedule](https://sports.yahoo.com/soccer/article/2026-fifa-world-cup-daily-schedule-every-match-date-kickoff-time-and-venue-for-all-48-teams-234515087.html)
- [Sky Sports — WC2026 fixture schedule](https://www.skysports.com/football/news/12098/13481245/world-cup-2026-fixture-schedule-and-uk-kick-off-times-day-by-day-breakdown-of-all-104-matches-including-england-scotland)
- [Football365 — WC2026 warm-up friendly results](https://www.football365.com/news/world-cup-2026-warm-up-friendly-fixtures-results-kick-off-times-what-tv-channel)
- [FIFA — pre-tournament warm-up results/fixtures](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/pre-tournament-warm-up-results-fixtures-scorers)
- [ESPN — Switzerland 1-1 Australia (Jun 6, 2026)](https://www.espn.com/soccer/report/_/gameId/401869743)
