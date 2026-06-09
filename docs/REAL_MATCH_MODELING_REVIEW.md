# Real Match Modeling Review

_Created 2026-06-09 · Modeling Role · pairs with `REAL_MATCH_INTELLIGENCE_SELECTION.md`._

> **No fake model output.** None of the selected real matches are in the system yet (the DB holds only
> the 3 seed matches: BRA-ARG, MAR-FRA, ESP-GER). Until the operator syncs the fixture into the DB and
> runs `POST /matches/{id}/refresh`, **`model_status = pending_api_sync`** and win-prob/confidence are
> **blank (not invented)**. A qualitative `manual_preview` is allowed **only** when explicitly tagged as
> operator preview — it is **not** model output.

## Modeling chain (existing, unchanged)
`match (synced) → win_prob → confidence → risk_level → risk_note → feature impact → Scout verdict → copy draft`
Endpoints: `GET /matches/{id}` (get match_id) · `POST /matches/{id}/refresh` (response shape unchanged) ·
`/performance/summary` (settlement). All require the match to exist in the DB first (operator sync).

## Review rows
| match_candidate_id | match_id | model_status | win_prob_home | win_prob_draw | win_prob_away | confidence | risk_level | risk_note | top_3_signals | contrarian_risk | watch_before_kickoff | model_limitations | can_use_in_copy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RMI-01 Mexico v South Africa | — | **pending_api_sync** | — | — | — | — | — | — | — | — | — | mock/seed not used; sync first | **partial** (manual_preview only, tagged) |
| RMI-02 Brazil 2-1 Egypt | — | **pending_api_sync** | — | — | — | — | — | — | — | — | — | finished → recap once synced+settled | **partial** (recap framing, real result cited as news) |
| RMI-03 Argentina 2-0 Honduras | — | **pending_api_sync** | — | — | — | — | — | — | — | — | — | finished → recap once synced+settled | **partial** (recap framing) |

## Manual preview (operator preview — NOT model output)
Qualitative, public-knowledge framing for copy direction only. **Tagged `manual_preview`; no numbers
presented as model probabilities.** Real model numbers appear **only after** operator sync + refresh.
- **RMI-01 Mexico v South Africa (pre-match):** host nation + opener atmosphere is the storyline; the
  open question is whether South Africa can absorb early Mexico pressure. *Scout angle, not a probability.*
- **RMI-02 Brazil 2-1 Egypt (recap):** result known (news: 2-1). Recap angle = did the favourite control
  the game or was it closer than the scoreline? *To be confirmed against synced result before settlement.*
- **RMI-03 Argentina 2-0 Honduras (recap):** result known (news: 2-0). Recap angle = comfortable margin;
  good "model direction vs result" example **once synced**.

## Update (2026-06-09) — WC-2022 historical is in the system; 2026 still unavailable
- **2026 (league 1) and friendlies (league 10): 0 fixtures** → RMI-01/02/03 remain
  `model_status=pending_api_sync` and `api_available=no` (public_source only; no fake numbers).
- **WC-2022 (league 1, season 2022): 64 fixtures/results/settled.** Historical matches **id 4–67** are now
  in the DB and **can be refreshed** (`POST /matches/{id}/refresh`) for **backtest/recap/calibration only**.
  Candidates: id 8 (ARG-KSA), 13 (GER-JPN), 58 (MAR-ESP), 67 (ARG-FRA).
- **`hit_rate=42.2%` is a settlement/backtest metric, NOT marketable predictive accuracy.** Use it for
  internal model calibration only; never present it to customers as a hit rate. 2022 matches are
  **historical**, not current — keep them out of the live "current preview" surfaces
  (`docs/HISTORICAL_RECAP_MODE_PROPOSAL.md`).

## Operator action to unblock modeling (Render)
1. Sync fixtures/results for league `10`/`1` season `2026` (see `DATA_SOURCE_SYNC_VERIFICATION.md`).
2. `GET /matches` → find the `match_id` for each selected fixture.
3. `POST /matches/{match_id}/refresh` → record win_prob / confidence / risk_level / risk_note / features here.
4. For finished matches, confirm the settled result, then `/performance/summary`.
**Do not market hit-rate** until enough settled matches exist; framing stays AI-viewpoint, not a guarantee.
