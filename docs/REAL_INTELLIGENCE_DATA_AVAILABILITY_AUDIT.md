# Real Intelligence — Data Availability Audit (v1)

> **Owner:** ClaudeT (executing engineer) · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Purpose:** Engineering audit of which "real football intelligence" fields are *actually* available to this
> project **today** vs. which need an operator token, a paid plan, manual sourcing, or carry compliance risk.
> **Rule of this doc:** do **not** blindly trust the candidate source list, and **never fabricate** a player,
> coach, lineup, injury, odds, or media value. If we cannot get it now, it is recorded as `missing` /
> `unavailable` / `operator-token-needed` / `paid-plan-needed` / `reference-only`.

---

## 0. Live state this audit is anchored on (verified 2026-06-10, public GET)

- `GET /api/v1/data-source/status` → `mock_mode:true`, `connector_status:ok`, `requests_used:0`, `plan:unknown`.
- `GET /api/v1/matches` → **67 matches** = 3 seed **scheduled** (id 1–3) + 64 **WC2022 finished** (id 4–67).
- `GET /api/v1/matches/8` → Argentina vs Saudi Arabia, `status:"finished"` (win_prob 52/19/29, risk_note, live_correction). **No score field.**
- `GET /api/v1/reports/8` → **HTTP 404** `{"detail":"Report not found or match has no prediction"}` (finished recaps have no detailed report).
- `GET /api/v1/reports/1` (seed scheduled) → **full report** (features / trend_history / tactics_note present).

**Conclusion:** the only "intelligence" we hold for the customer is: fixture + baseline model probability (+ a
detailed factor report **only for the 3 current seed matches**). Everything player/coach/lineup/injury/odds/media
is **not connected**. Real WC2026 fixtures are still 0 (provider returned none); sync is operator-gated on Render
(`BLOCKED_OPERATOR_RENDER_SHELL` — Claude has no `$ADMIN_API_TOKEN`).

---

## 1. Field-by-field audit (21 fields)

Legend — `available_now`: yes / no / unknown · `source`: existing_api / api_football / public_reference /
manual_reference / not_available · `can_use_in_customer_ui`: yes / no · `compliance_risk`: low / med / high.

### 1. fixture (teams / kickoff / status)
- available_now: **yes** · source: existing_api · endpoint: `GET /matches`, `GET /matches/{id}`
- sample_match_id: 8 · sample_payload_available: yes · can_use_in_customer_ui: **yes** · compliance_risk: low
- short_term: already live (3 scheduled + 64 WC2022). · long_term: operator syncs real WC2026 fixtures.

### 2. result (match settled outcome)
- available_now: **yes (backend only)** · source: existing_api (settlement: 64/64 settled per docs) · endpoint: settlement pipeline / `performance/summary`
- sample_match_id: 8 · sample_payload_available: **no** (settled flag, not a customer field) · can_use_in_customer_ui: **partial** ("settled, recap-only", no scoreline) · compliance_risk: low
- short_term: Evidence Pack states "real result settled (recap)" **without a scoreline**. · long_term: see field 3.

### 3. final score (e.g. ARG 1–2 KSA)
- available_now: **no (not in any customer payload)** · source: existing_api (backend settlement) / not_available (frontend) · endpoint: **none** in `/matches`|`/reports`
- sample_match_id: 8 · sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low
- short_term: **do not display a scoreline** (would be fabrication) — Evidence Pack lists it as ingested-but-not-surfaced. · long_term: expose a real `final_score` field via API (**backend change → Owner/operator-gated, OUT OF SCOPE here**).

### 4. team profile (name / flag)
- available_now: **yes (minimal)** · source: existing_api · endpoint: `/matches` (`home_team`/`away_team` = name + flag only)
- sample_match_id: 8 · sample_payload_available: yes (name+flag) · can_use_in_customer_ui: yes · compliance_risk: low
- short_term: live. · long_term: richer profile via api_football `teams` (paid).

### 5. coach
- available_now: **no** · source: api_football (`coachs`) — **operator-token-needed / paid-plan-needed**, not exercised · endpoint: api_football `GET /coachs?team=`
- sample_match_id: 8 · sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low
- short_term: mark **missing** in Evidence Pack. · long_term: operator syncs coachs (paid plan).

### 6. squad / player list
- available_now: **no** · source: api_football (`players/squads`) — paid-plan-needed, not exercised
- sample_match_id: 8 · sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low
- short_term: **missing**. · long_term: operator syncs squads (paid).

### 7. starting XI
- available_now: **no** · source: api_football (`fixtures/lineups`, ~20–40 min pre-kickoff, paid) — for 2022 recaps, often not_available
- sample_match_id: 8 · sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low
- short_term: **missing**. · long_term: operator syncs lineups near kickoff for live WC2026 matches.

### 8. substitutes
- available_now: **no** · source: api_football (`fixtures/lineups`) — paid · same constraints as field 7
- sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low
- short_term: **missing**. · long_term: operator (paid lineups).

### 9. injuries / suspensions
- available_now: **no** · source: api_football (`injuries`, paid) / Transfermarkt (reference-only) · endpoint: api_football `GET /injuries?fixture=`
- sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low (api_football) / **med** (Transfermarkt ToS)
- short_term: **missing**. · long_term: operator syncs api_football injuries; Transfermarkt reference-only (no scrape).

### 10. recent form (last 5)
- available_now: **no (but derivable)** · source: existing_api (compute from synced finished results) + api_football (`teams/statistics`) · endpoint: derive from `/matches` finished set / backend
- sample_match_id: 8 · sample_payload_available: **no** (not computed/exposed) · can_use_in_customer_ui: **no yet** · compliance_risk: low
- short_term: optionally **derive** from the 64 synced WC2022 results (no new data), else mark missing. · long_term: api_football form/stats (operator).

### 11. head-to-head
- available_now: **no (but derivable)** · source: existing_api (derive from historical results) / api_football (`fixtures/headtohead`)
- sample_payload_available: **no** · can_use_in_customer_ui: **no yet** · compliance_risk: low
- short_term: derive from synced results or mark missing. · long_term: api_football h2h (operator).

### 12. standings / ranking
- available_now: **no** · source: api_football (`standings`, paid) / FIFA ranking (manual_reference)
- sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: low
- short_term: **missing** / manual. · long_term: operator api_football standings, or FIFA ranking manual import.

### 13. Elo rating
- available_now: **no** · source: public_reference (World Football Elo Ratings, eloratings.net) · endpoint: site/CSV — **reference-only**
- sample_payload_available: **no** · can_use_in_customer_ui: **reference-only** (compute `elo_delta` manually, cite source) · compliance_risk: **med** (ToS / attribution)
- short_term: **manual reference**, do not auto-scrape. · long_term: evaluate a licensed feed or a Kaggle Elo dataset for `elo_delta`.

### 14. Transfermarkt squad value
- available_now: **no** · source: public_reference (transfermarkt.com) — **reference-only** · endpoint: site (no open API)
- sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: **high** (scraping/ToS, redistribution)
- short_term: **manual reference only**, no scrape/redistribute. · long_term: licensed data partnership, or drop `squad_value_delta`.

### 15. odds / market movement
- available_now: **no** · source: api_football (`odds`, paid) / odds sites (reference) · endpoint: api_football `GET /odds?fixture=`
- sample_payload_available: **no** · can_use_in_customer_ui: **NO** · compliance_risk: **HIGH** (betting adjacency)
- short_term: **excluded** — compliance floor is no betting/odds. If ever shown, only as an abstract non-odds "market signal", **gated by Owner + compliance review**. · long_term: **Owner/compliance decision required; default = exclude.**

### 16. media / news signal
- available_now: **no** · source: manual_reference / not_available (no news API) · endpoint: none
- sample_payload_available: **no** · can_use_in_customer_ui: **no** · compliance_risk: **med** (accuracy / attribution)
- short_term: **missing**; only human-authored summaries, never fabricated. · long_term: evaluate a news API behind editorial review.

### 17. weather / venue / travel
- available_now: **no** · source: api_football (`venue` in fixtures, paid) + manual_reference (climate refs; ESPN/SI travel mileage) · endpoint: api_football fixtures venue / manual
- sample_payload_available: **no** (no venue/weather field in our payload) · can_use_in_customer_ui: **no yet** · compliance_risk: low
- short_term: **missing** / manual. · long_term: operator adds venue, integrate a weather API; travel mileage as a manual reference table.

### 18. community heat
- available_now: **yes (building)** · source: existing_api · endpoint: `GET /community/heat`
- sample_payload_available: yes (may be sparse) · can_use_in_customer_ui: **yes** (already a surface, "coming soon"-gated) · compliance_risk: low (anonymous in-app stats)
- short_term: live but building. · long_term: accumulate real interactions.

### 19. model prediction (win_prob / confidence / risk)
- available_now: **yes** · source: existing_api (baseline model) · endpoint: `/matches`, `/matches/{id}`, `/reports/{id}` (when present), `POST /matches/{id}/refresh`
- sample_match_id: 8 (52/19/29, conf 75, risk medium) · sample_payload_available: yes · can_use_in_customer_ui: **yes (as AI viewpoint, NOT hit-rate)** · compliance_risk: low
- short_term: live. · long_term: improve model once real features (5–17 above) are connected.

### 20. explanation factors (features / tactics / trend)
- available_now: **yes for matches WITH a report; NO for finished recaps** · source: existing_api · endpoint: `GET /reports/{id}`
- sample_match_id: 1 (present) / **8 (absent — 404)** · sample_payload_available: yes(id1) / **no(id8)** · can_use_in_customer_ui: yes when present · compliance_risk: low
- short_term: present for current preview (seed); **absent for WC2022 recaps → Evidence Pack lists them missing**. · long_term: generate reports for recaps (backend/operator).

### 21. missing-data notice (Evidence Pack)
- available_now: **yes (shipped this sprint, frontend)** · source: frontend (this change) · endpoint: derived from `match.status === 'finished'`
- sample_match_id: 8 · sample_payload_available: n/a · can_use_in_customer_ui: **yes** · compliance_risk: low (honest disclosure)
- short_term: shipped (`EvidencePack.tsx`). · long_term: extend to *scheduled* fixtures whose `/reports` is missing (add a `reportMissing` flag — see Known Gap).

---

## 2. Candidate-source verdicts (the 12 sources proposed)

| # | Source | Verdict | Short-term | Long-term |
|---|--------|---------|------------|-----------|
| 1 | FIFA WC 2026 official site | reference-only | manual fixture/venue cross-check | official schedule reference |
| 2 | Kaggle Intl results 1872–2026 | usable (dataset) | offline form / Elo derivation, **not live** | calibration dataset for model |
| 3 | **API-FOOTBALL** | **primary live source** | fixtures/results live (mock now); coach/squad/XI/injury/odds/standings = **paid + operator token** | the real integration path |
| 4 | Transfermarkt | reference-only (**high ToS risk**) | manual squad-value reference only | licensed partnership or drop |
| 5 | World Football Elo | reference-only (med) | manual `elo_delta` | licensed/Kaggle Elo feed |
| 6 | soccerdata (py lib) | tooling (scrapes FBref/etc.) | offline research only, **ToS caution** | evaluate for batch enrichment |
| 7 | FBref / Understat / WhoScored | reference-only (med/high ToS) | manual xG/stat reference | licensed stats feed |
| 8 | FiveThirtyEight / SPI | reference-only (538 SPI archived) | benchmark our probabilities | model benchmark only |
| 9 | SofaScore | reference-only (**high ToS**, anti-scrape) | UI/field-structure benchmark only | no direct integration |
| 10 | Tales of the Stands (climate) | manual_reference | manual venue-climate note | weather API |
| 11 | ESPN / SI travel mileage | manual_reference | manual travel table | computed travel feature |
| 12 | odds / 竞猜 sites | **compliance-blocked** | **excluded** (no betting/odds) | Owner/compliance decision; default exclude |

---

## 3. Known gap (documented, not fixed this sprint)

The Evidence Pack trigger is `match.status === 'finished'` — a perfect 1:1 with "no detailed report" for **all
current data** (seed scheduled have reports; finished WC2022 → 404). A **future scheduled WC2026 fixture** whose
AI report has not yet been generated would still render the hollow report. Fix when that case is real: add an
optional `match.reportMissing` flag (set in `loadReport`'s catch) and OR it into the trigger — one clean line, no
backend change.

## 4. Guardrails honored
No backend/API/DB change · no operator sync run/faked · no fabricated player/coach/lineup/injury/odds/media ·
odds excluded (compliance) · `42.2%` hit-rate kept out of all customer UI.
