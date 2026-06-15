# R3 · DATA_SOURCE_AUDIT

> Phase A — audit only. No implementation depends on this doc being "nice"; it must be HONEST.
> Baseline: `feature/mvp2-r3-data-llm-update-recap-sla` off `main @ e354352`
> (tag `mvp2-r2a-homepage-fallback-baseline-20260615`). Audited 2026-06-15.

Scope: every data source feeding the daily content loop, what it actually provides today, and
who is authoritative for each customer-visible fact.

## Source-by-source

| # | Source | Location | Fields | Freshness | Coverage | Reliability | Model? | LLM prompt? | Frontend? | Gaps |
|---|--------|----------|--------|-----------|----------|-------------|--------|-------------|-----------|------|
| 1 | API-FOOTBALL `/fixtures` | `backend/app/services/...` + `scripts/mvp2_match_sync.py` (`--source fetched`), `scripts/mvp2_daily_scan.py` | fixture.id, date, status (NS/1H/HT/FT/AET/PEN), teams, goals, round, venue; L2 lineups/events/stats post-match | per-match; updated at FT | 2026 WC fixtures | HIGH (token-gated; Pro key works locally per memory) | indirectly (status/score) | facts only | via manifest | no injuries/xG/market value/FIFA rank |
| 2 | Kaggle `data/external/kaggle/results.csv` | local, gitignored | date, home/away team, scores, tournament, neutral | frozen at build | 1872–2026 internationals | HIGH for Elo/form (real history) | YES (ScoutScore Elo/form/Poisson) | as `source_refs` text | never raw | future fixtures = NA; cold-start teams missing; needs `KAGGLE_TEAM_ALIASES` |
| 3 | ScoutScore v0.2 | `scripts/mvp2_build_scoutscore_v0_2_factors.py` | Elo gap, last-10 form, Poisson bands, upset_band, factor frame | computed offline | any fixture with both teams in kaggle | HIGH (deterministic, reproducible) | YES (the model judgment) | feeds `model_fields` → prompt | via artifact `model_fields` | no injuries/xG; pre-match formations/GK only post-match |
| 4 | baseline.py | `backend/app/services/modeling/baseline.py` | prob_home/draw/away, confidence, risk, recommended_score | deterministic | any | **NAME-HASH NOISE — `ai_provider=mock`** | **NO (not used in production)** | NO | NO | not honest to surface; superseded by ScoutScore (see [memory R2]) |
| 5 | selectedHotspot | `frontend/src/data/selectedHotspot.json` (+ audit mirror `docs/data_audit/mvp2_match_sync/selected_hotspot_*.json`) | date, fixture_key, home/away, source, status | operator-edited, build-bundled | one fixture/day | HIGH (editorial authority, P7 P0-1) | no | no | AUTHORITY for homepage lead | manual only; no auto-refresh |
| 6 | runtime daily-fixtures backend | `backend/app/routers/daily_fixtures.py`, `runtime_manifests` table, `GET /api/v1/daily-fixtures` | normalized fixtures + lifecycle + recap_queue + active_hero + product_status + freshness | operator upload, no automation | today's slate | storage layer only; **currently STALE (06-14, no 1489377)** | no | no | fetched first (R2a-gated) | no auto-generation; stale unless operator uploads |
| 7 | bundled/static manifests | `frontend/src/data/dailyFixtures.generated.json` (bundled), `frontend/public/data/daily-fixtures.json` (static) | same shape as backend | build-time / sync-time | today's slate | HIGH (matches the deployed bundle) | no | no | fallback when backend stale/missing-selection | snapshot-in-time; no live scores |
| 8 | predictionArtifacts | `frontend/src/data/predictionArtifacts/*.json` via `predictionArtifacts.ts` | source_facts, model_fields, llm_judgment, operator_confirmation, content_chain, t30, i18n | build-bundled; rebuilt by `mvp2_build_daily_prediction_artifact.py` | per fixture | HIGH (provenance-tagged) | consumes ScoutScore | records prompt+reviewed paths | drives /predict + /internal/daily | win_prob/confidence always null (by rule); auto-LLM = P1 |
| 9 | recap / observation artifacts | `frontend/src/data/predictionArtifacts/observation_*.json` (FE), `docs/data_audit/mvp2_prediction_accountability_reports/{id}.{tag}.json` (backend recap), `frontend/src/data/recapData.ts` | receipt / full recap content | build-bundled / server file | per finished fixture | observation HIGH; full recap only where built (855737) | recap uses ScoutScore replay | no | drives /recap | **NO full recap for 1489371 — observation only; backend has no file → 404** |

## Concrete current fixtures

- **Belgium vs Egypt (1489377, 2026-06-15)** — the live selected hotspot.
  - Identity/kickoff/status: API-FOOTBALL (`scheduled`, KO 19:00 UTC).
  - Model: ScoutScore v0.2 COMPUTED from kaggle (Elo Belgium 1885 / Egypt 1756, gap +129; form 7W-3D-0L vs 5W-3D-2L; Poisson 1-0/2-0/1-1; upset_band=medium) → `model_fields.source=computed`.
  - Artifact: `match_Belgium-Egypt-20260615.json` (prediction_confirmed=true, llm_provider=operator_manual).
  - Score/result: NONE (scheduled; never invented).
- **Brazil vs Morocco (1489371, finished 1-1)** — yesterday's hotspot carryover.
  - Identity/kickoff/score: API-FOOTBALL (`finished`, 1-1).
  - Recap: OBSERVATION ONLY (`observation_1489371.json`, recap_ready=false). No full recap artifact, no backend accountability report → backend `/api/v1/recap/1489371` returns **404**.

## Authoritative answers (the questions the Owner asked)

- **Fixture identity** → API-FOOTBALL `fixture.id` (canonical). Manual slate slug (`manual:HOME-AWAY-date`) is the fallback when a fixture is not API-mapped.
- **Kickoff / status** → API-FOOTBALL `fixture.date` + `fixture.status.short`. Backend runtime manifest carries the operator-confirmed status for the day; the lifecycle engine (`lifecycle.py` / `freshness.ts`) applies time-inference so a stale `NS` never reads as "live/pre-match" after kickoff.
- **Score / result** → API-FOOTBALL `goals.*` (confirmed by the post-match scout pack). NEVER invented: a scheduled fixture with no score keeps `score_home/away = null` (`mvp2_match_sync.py`).
- **Model judgment** → **ScoutScore v0.2** (kaggle Elo + last-10 form + Poisson). Operator review layers a persona narrative on top but must stay consistent with the computed fields.
- **Fallback / mock only** → `baseline.py` (`ai_provider=mock`, name-hash noise — NOT used on customer surfaces); bundled/static manifests (fallback only); observation artifact (fallback when full recap not ready).
- **Never customer-visible-as-real if the computed source is missing** → `win_prob` and `confidence` (always `null`; `no_fake_probability=true`); `recommended_score` / `risk_level` (null + listed in `missing_fields` when `model_fields.source=unavailable`); `primary_direction` (shows "方向待临场确认" when not confirmed). Raw Elo/form/Poisson numbers are internal-only and never shown raw.

## Validity verdict (today)

- Fixture identity / kickoff / status / score: **PROVEN VALID** (real API-FOOTBALL + manual scores, never invented).
- Model judgment: **VALID & HONEST** for Belgium-Egypt (`source=computed`, traceable to kaggle). Cold-start teams correctly downgrade to `operator_estimated`.
- Open gap (P1, not a validity hole): the **live backend manifest is stale** (06-14, no 1489377). The R2a fallback keeps the homepage correct via bundled/static, but `check_runtime_daily_fixtures.py --expected-date 2026-06-15 --expected-fixture 1489377` FAILS until the operator uploads (`mvp2_match_sync.py upload --target production`, needs prod `ADMIN_API_TOKEN` which engineering does not hold).
