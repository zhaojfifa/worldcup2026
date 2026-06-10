#!/usr/bin/env python3
"""MVP-2 Scout Pack ingestion (operator/engineer-run, token-gated).

Pulls real API-FOOTBALL Level-2 data for one or more fixtures, builds the
redacted internal Scout Pack, and writes a bounded JSON sample to
``docs/data_audit/mvp2_scout_pack_samples/<fixture_id>.json``.

SAFETY:
- Token read server-side (settings / gitignored backend/.env). NEVER printed,
  logged, or written to the sample. Only endpoint/status/results are printed.
- Output is whitelisted + bounded — no raw vendor payload is saved.
- Read-only GETs with timeout / 429 backoff / request budget.
- Standalone ops script — not wired into the running app.

Run:   python backend/scripts/mvp2_ingest_scout_pack.py [fixture_id ...]
       (default fixtures: 855737 855741)
"""
import json
import os
import sys
from datetime import datetime, timezone

# Make `app.*` importable when run from the repo root or from backend/.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.api_football_client import APIFootballScoutClient, BudgetExceeded  # noqa: E402
from app.services.scout_pack.builder import build_scout_pack  # noqa: E402

OUT_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_scout_pack_samples")
DEFAULT_FIXTURES = [855737, 855741]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fixture_team_ids(fixture_result):
    fx = (fixture_result.response or [None])[0] if fixture_result.response else None
    if not fx:
        return None, None, None, None
    teams = fx.get("teams") or {}
    lg = fx.get("league") or {}
    return ((teams.get("home") or {}).get("id"), (teams.get("away") or {}).get("id"),
            lg.get("id"), lg.get("season"))


def pull_bundle(client: APIFootballScoutClient, fid: int) -> dict:
    fixture = client.get_fixture(fid)
    home_id, away_id, league_id, season = fixture_team_ids(fixture)

    lineups = client.get_lineups(fid)
    events = client.get_events(fid)
    statistics = client.get_statistics(fid)
    players = client.get_fixture_players(fid)

    # injuries: try fixture-level first; if empty, try league+season (the verified gap).
    injuries = client.get_injuries(fixture_id=fid)
    if (injuries.results or 0) == 0 and league_id and season:
        alt = client.get_injuries(league_id=league_id, season=season)
        if (alt.results or 0) > 0:
            injuries = alt

    squad_home = client.get_squad(home_id) if home_id else None
    squad_away = client.get_squad(away_id) if away_id else None
    coach_home = client.get_coach(home_id) if home_id else None
    coach_away = client.get_coach(away_id) if away_id else None
    team_home = client.get_team(home_id) if home_id else None
    team_away = client.get_team(away_id) if away_id else None

    return {
        "fixture": fixture, "lineups": lineups, "events": events,
        "statistics": statistics, "players": players, "injuries": injuries,
        "squad_home": squad_home, "squad_away": squad_away,
        "coach_home": coach_home, "coach_away": coach_away,
        "team_home": team_home, "team_away": team_away,
    }


def print_summary(fid: int, log_slice: list):
    print(f"  fixture {fid}: {len(log_slice)} calls")
    for row in log_slice:
        print(f"    {row['endpoint']:<22} http={row['http_status']} "
              f"results={row['results']} params={row['params']}")


def main():
    fixtures = [int(a) for a in sys.argv[1:]] or DEFAULT_FIXTURES
    client = APIFootballScoutClient(max_requests=400)
    if not client.is_configured():
        print("BLOCKED: API_FOOTBALL_KEY not configured (server env / backend/.env). No calls made.")
        sys.exit(2)

    plan = None
    st = client.status()
    if isinstance(st.response, dict):
        plan = ((st.response.get("subscription") or {}).get("plan"))
    print(f"plan={plan} (status http={st.http_status})")

    os.makedirs(OUT_DIR, exist_ok=True)
    for fid in fixtures:
        start = len(client.request_log)
        try:
            bundle = pull_bundle(client, fid)
        except BudgetExceeded as exc:
            print(f"STOP: {exc}")
            break
        log_slice = client.request_log[start:]
        pack = build_scout_pack(
            fixture_id=fid, bundle=bundle, last_checked_at=now_iso(),
            plan=plan, request_log=log_slice,
        )
        out_path = os.path.join(OUT_DIR, f"{fid}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(pack, f, ensure_ascii=False, indent=2)
        size = os.path.getsize(out_path)
        print_summary(fid, log_slice)
        cov = pack["feature_snapshot"]["coverage_score"]
        miss = list(pack["missing_evidence"].keys())
        print(f"  -> wrote {out_path} ({size} bytes) coverage={cov}% missing={miss}")

    print(f"total requests this run: {client.request_count}")


if __name__ == "__main__":
    main()
