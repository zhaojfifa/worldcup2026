# R2 — STATUS

> Heavy sprint: reconnect REAL data/model/LLM-supported content into the daily product loop.
> Read-only audit complete; implementation gated on the 7 Phase-A files existing.

## Git / environment
| Item | Value |
|---|---|
| Branch | `feature/mvp2-r2-real-content-source-recovery` (off main `2a8e1ec`) |
| Today (system) | **2026-06-15** |
| Local slate | stale — `daily-fixtures.json` `generated_for_date=2026-06-14` (Netherlands–Japan, all manual id=null) |
| Live backend slate | also 06-14 (the `/api/v1/daily-fixtures` endpoint, ~26h old) |
| API-FOOTBALL | key present in `backend/.env`; **direct query works** (`v3.football.api-sports.io`, `x-apisports-key`) |
| kaggle dataset | **present** at `data/external/kaggle/results.csv` → real Elo/form computable |

## Real fixtures available TODAY (2026-06-15, API-FOOTBALL league=1 season=2026)
| id | kickoff UTC | status | match |
|---|---|---|---|
| 1539002 | 02:00 | FT | Sweden 2 ? Tunisia (finished early today) |
| 1489380 | 16:00 | NS | Spain vs Cape Verde Islands |
| **1489377** | **19:00** | **NS** | **Belgium vs Egypt ← selected fresh hotspot** |
| 1489379 | 22:00 | NS | Saudi Arabia vs Uruguay |

## Chosen fresh hotspot: Belgium vs Egypt (1489377)
Real computed model (ScoutScore v0.2 from kaggle): Belgium Elo **1884.9** vs Egypt **1755.6** → gap
**+129** (Belgium favoured); form10 Belgium **7W-3D-0L GF37/GA6**, Egypt **5W-3D-2L GF13/GA6**;
`upset_band(129)` → **medium** ("clear favourite but gaps partially covered"); `poisson_bands(1.9,0.8)`
→ **1-0 / 2-0 / 1-1**. → clear favourite + genuine upset angle, **source = computed** (not
operator_estimated). Spain–Cape Verde rejected (Cape Verde absent from kaggle → cold-start, no honest
model). win_prob/numeric confidence stay NULL (compliance floor) even though Elo implies a lean.

## Key constraint found
`fetchDailyManifest` is **backend-first** (backend → static → bundled). The live backend serves the
stale 06-14 slate, so the DEPLOYED homepage will not show the fresh 06-15 hotspot until the operator
uploads the new manifest to the backend (`mvp2_match_sync … upload --target production`) — a **runtime
data upload**, which the R2 boundary forbids engineering from doing. R2 therefore ships fresh content in
the **bundle + static** file and screenshots it locally with the backend bypassed; the deployed flip is
an operator step (documented in the deploy instruction).

## Discovery status
COMPLETE. Sources audited: `baseline.py` (seed-hash noise — NOT honest to surface), ScoutScore builder
(real Elo/form — usable), `mvp2_build_daily_prediction_artifact.py` (R1 chain), manifest/selected_hotspot/
artifact/projection/internal-daily. Plan in the 6 sibling files. **Implementation may proceed** (all 7
Phase-A files now exist).

## Next action
Implement R2 P0 per `R2_IMPLEMENTATION_SPEC.md`; verify against `ACCEPTANCE_CHECKLIST.md`; screenshots
mandatory; send stays HOLD.
