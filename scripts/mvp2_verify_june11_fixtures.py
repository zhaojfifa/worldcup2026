#!/usr/bin/env python3
"""
MVP-2 June 11 trial — real fixture verification (source of truth = API-FOOTBALL).

Fetches /fixtures (league=1, season=2026), verifies the June-11 opening-window
candidates, probes per-fixture pre-match endpoint availability (lineups/injuries),
and writes docs/data_audit/mvp2_june11_real_fixture_verification.json.

SAFETY: token read from backend/.env via the existing server-side client — never
printed; output is bounded facts only (no raw payload); frontend never calls the vendor.

Usage: python3 scripts/mvp2_verify_june11_fixtures.py [fixture_id ...]
Default candidates: 1489369 1489371
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.api_football_client import APIFootballScoutClient  # noqa: E402

OUT = ROOT / "docs" / "data_audit" / "mvp2_june11_real_fixture_verification.json"
PACKS = ROOT / "docs" / "data_audit" / "mvp2_scout_pack_samples"
LEAGUE, SEASON = 1, 2026
WINDOW = ("2026-06-11", "2026-06-15")


def main():
    cands = [int(a) for a in sys.argv[1:]] or [1489369, 1489371]
    client = APIFootballScoutClient()
    season_res = client.get_fixtures(LEAGUE, SEASON)
    window_rows = []
    by_id = {}
    for fx in (season_res.response or []):
        f, t, lg = fx.get("fixture", {}), fx.get("teams", {}), fx.get("league", {})
        date = (f.get("date") or "")
        row = {
            "fixture_id": f.get("id"),
            "home_team": (t.get("home") or {}).get("name"),
            "away_team": (t.get("away") or {}).get("name"),
            "kickoff_time": date,
            "timezone": f.get("timezone"),
            "venue": {"name": (f.get("venue") or {}).get("name"), "city": (f.get("venue") or {}).get("city")},
            "round": lg.get("round"),
            "match_status": (f.get("status") or {}).get("long"),
        }
        by_id[row["fixture_id"]] = row
        if WINDOW[0] <= date[:10] < WINDOW[1]:
            window_rows.append(row)
    window_rows.sort(key=lambda r: r["kickoff_time"])

    verified = []
    for fid in cands:
        row = dict(by_id.get(fid) or {"fixture_id": fid, "error": "not found in season list"})
        lu = client.get_lineups(fid)
        inj = client.get_injuries(fixture_id=fid)
        pack = PACKS / ("%d.json" % fid)
        pack_d = json.loads(pack.read_text(encoding="utf-8")) if pack.exists() else {}
        row.update({
            "league_id": LEAGUE, "season": SEASON,
            "api_endpoint": "/fixtures?league=1&season=2026 (+/fixtures/lineups, /injuries probes)",
            "lineups_available": bool(lu.results),
            "injuries_available": bool(inj.results),
            "squads_available": bool(((pack_d.get("squad") or {}).get("value") or {})),
            "coaches_available": bool(((pack_d.get("coach") or {}).get("value") or {})),
            "teams_available": bool(((pack_d.get("teams") or {}).get("value") or {})),
            "scout_pack": str(pack.relative_to(ROOT)) if pack.exists() else None,
        })
        verified.append(row)

    doc = {
        "sprint": "MVP-2 June 11 Real Match Trial Prediction",
        "league_id": LEAGUE, "season": SEASON,
        "fetch_time": datetime.now(timezone.utc).isoformat(),
        "season_fixture_count": season_res.results,
        "http_status": season_res.http_status,
        "opening_window": {"from": WINDOW[0], "to": WINDOW[1], "fixtures": window_rows},
        "verified_candidates": verified,
        "source_ledger": {
            "source": "api-football",
            "endpoints": ["/fixtures", "/fixtures/lineups", "/injuries"],
            "license_status": "ok",
            "token_handling": "server-side env only, never printed/committed",
            "frontend_vendor_call": False,
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    for r in verified:
        print("  fixture %s: %s vs %s | %s | %s | lineups=%s injuries=%s squads=%s" % (
            r.get("fixture_id"), r.get("home_team"), r.get("away_team"), r.get("kickoff_time"),
            r.get("match_status"), r.get("lineups_available"), r.get("injuries_available"), r.get("squads_available")))


if __name__ == "__main__":
    main()
