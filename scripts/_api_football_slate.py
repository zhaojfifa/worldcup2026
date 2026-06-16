#!/usr/bin/env python3
"""R2 — automated daily-slate fetch from API-FOOTBALL (no manual file required).

Pulls the WC season fixtures once and returns the rows for ONE date as raw dicts in the exact
shape mvp2_match_sync.evaluate() consumes, plus optional kickoff_utc / api_fixture_id so a fixture
that is NOT in the hand-mapped KNOWN table still carries its real kickoff and id.

Honesty rules (compliance floor): a score is recorded ONLY when the match is finished (FT/AET/PEN)
and the API actually reports goals; otherwise score stays None. Status is mapped honestly to
scheduled / live / finished / postponed / cancelled / unknown — never invented. No events, lineups,
or injuries are read here (data refresh only).

The API fixture id IS our internal id space (e.g. Belgium vs Egypt = 1489377 in both), so it is
passed through as api_fixture_id; mvp2_match_sync decides renderable from whether a bundled narrative
exists for that id. Key/base_url come from the same env/.env the backend client already uses; nothing
is printed or committed.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# API-FOOTBALL status short -> our registry status word (honest mapping, no invention).
_FINISHED = {"FT", "AET", "PEN"}
_LIVE = {"1H", "2H", "HT", "ET", "BT", "P", "LIVE", "INT"}
_POSTP = {"PST"}
_CANC = {"CANC", "ABD", "AWD", "WO"}


def _status_word(short):
    s = (short or "").upper()
    if s in _FINISHED:
        return "finished"
    if s in _LIVE:
        return "live"
    if s in _POSTP:
        return "postponed"
    if s in _CANC:
        return "cancelled"
    if s in ("NS", "TBD"):
        return "scheduled"
    return "unknown"


def fetch_slate(date_iso, league_id=None, season=None):
    """Return a list of raw fixture dicts for date_iso (UTC) from API-FOOTBALL.

    Raises RuntimeError if the client is unavailable / unconfigured so the caller can decide
    whether to fall back. Never fabricates a row."""
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        from app.services.api_football_client import APIFootballScoutClient
    except Exception as e:  # pragma: no cover - import guard
        raise RuntimeError("API-FOOTBALL client import failed: %s" % e)
    client = APIFootballScoutClient()
    if not client.is_configured():
        raise RuntimeError("API-FOOTBALL not configured (no API_FOOTBALL_KEY in env/.env)")
    league = int(league_id if league_id is not None else os.environ.get("WC_LEAGUE_ID", "1"))
    seas = int(season if season is not None else os.environ.get("WC_SEASON", "2026"))
    res = client.get_fixtures(league, seas)
    rows = res.response or []
    out = []
    for f in rows:
        fx = f.get("fixture") or {}
        ko = fx.get("date") or ""
        if ko[:10] != date_iso:
            continue
        teams = f.get("teams") or {}
        goals = f.get("goals") or {}
        short = ((fx.get("status") or {}).get("short"))
        status = _status_word(short)
        # score ONLY for genuinely finished matches that report goals — never invent
        if status == "finished" and goals.get("home") is not None and goals.get("away") is not None:
            sh, sa = int(goals["home"]), int(goals["away"])
        else:
            sh, sa = None, None
        out.append({
            "home": ((teams.get("home") or {}).get("name") or "").strip(),
            "away": ((teams.get("away") or {}).get("name") or "").strip(),
            "score_home": sh,
            "score_away": sa,
            "status": status,
            "kickoff_utc": ko or None,
            "api_fixture_id": fx.get("id"),
            "api_status_short": short,
        })
    # stable order by kickoff time
    out.sort(key=lambda r: r.get("kickoff_utc") or "")
    return out
