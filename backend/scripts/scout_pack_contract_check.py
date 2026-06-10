#!/usr/bin/env python3
"""Offline contract check for the MVP-2 Scout Pack builder (no network/DB).

Feeds synthetic API-FOOTBALL-shaped payloads (including image fields and
over-long lists) into ``build_scout_pack`` and asserts the hard contract:
envelopes present · redaction (no image URLs) · bounding · injuries unresolved
(never "no injuries") · honest-empty for missing sources · vi has 0 Han ·
AI restricted to verified fields.

Run:  python backend/scripts/scout_pack_contract_check.py
Manual helper — not wired into the app, no pytest dependency.
"""
import json
import os
import re
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.api_football_client import EndpointResult  # noqa: E402
from app.services.scout_pack import contract as C  # noqa: E402
from app.services.scout_pack.builder import build_scout_pack  # noqa: E402

HAN = re.compile(r"[一-鿿]")
ENVELOPE_KEYS = {"value", "available", "source", "endpoint", "fixture_id",
                 "last_checked_at", "confidence", "license_status", "fallback_text", "missing_reason"}
OWNER_TOP_KEYS = ["fixture", "teams", "lineups", "formation", "coach", "squad",
                  "events_summary", "team_statistics", "player_statistics",
                  "missing_evidence", "source_ledger", "ai_allowed_explanations",
                  "ai_forbidden_explanations"]

_fails: list[str] = []


def check(cond: bool, msg: str):
    if cond:
        print(f"  ok  · {msg}")
    else:
        _fails.append(msg)
        print(f"  FAIL· {msg}")


def er(endpoint, response, results=None, team_id=None, fixture_id=None):
    return EndpointResult(endpoint=endpoint, params={}, http_status=200,
                          results=(len(response) if results is None else results),
                          errors=None, response=response, team_id=team_id, fixture_id=fixture_id)


def full_bundle():
    fixture = er("/fixtures", [{
        "fixture": {"id": 999001, "date": "2026-06-11T18:00:00+00:00",
                    "venue": {"name": "Test Arena", "city": "Testville"},
                    "status": {"long": "Match Finished"}},
        "league": {"name": "World Cup", "season": 2026, "round": "Group Stage - 1"},
        "teams": {"home": {"id": 1, "name": "Alpha", "logo": "http://x/l1.png", "winner": True},
                  "away": {"id": 2, "name": "Beta", "logo": "http://x/l2.png", "winner": False}},
        "goals": {"home": 2, "away": 1},
    }], results=1)
    lineups = er("/fixtures/lineups", [
        {"team": {"id": 1, "name": "Alpha", "logo": "http://x/l1.png"},
         "coach": {"id": 10, "name": "Coach A", "photo": "http://x/p.png"}, "formation": "4-3-3",
         "startXI": [{"player": {"id": 100 + i, "name": f"P{i}", "number": i, "pos": "M", "grid": f"2:{i}"}} for i in range(11)],
         "substitutes": [{"player": {"id": 200 + i, "name": f"Sub{i}", "number": 12 + i, "pos": "D"}} for i in range(7)]},
        {"team": {"id": 2, "name": "Beta", "logo": "http://x/l2.png"},
         "coach": {"id": 20, "name": "Coach B", "photo": "http://x/p2.png"}, "formation": "4-4-2",
         "startXI": [{"player": {"id": 300 + i, "name": f"Q{i}", "number": i, "pos": "D", "grid": f"3:{i}"}} for i in range(11)],
         "substitutes": []},
    ], results=2)
    events = er("/fixtures/events", [
        {"time": {"elapsed": i, "extra": None}, "team": {"name": "Alpha"},
         "player": {"name": f"P{i%11}"}, "assist": {"name": None}, "type": "Goal" if i % 5 == 0 else "Card",
         "detail": "Normal Goal"} for i in range(40)  # 40 > MAX_EVENTS(30) -> must truncate
    ], results=40)
    statistics = er("/fixtures/statistics", [
        {"team": {"name": "Alpha"}, "statistics": [{"type": "Shots on Goal", "value": 5},
                                                   {"type": "Ball Possession", "value": "60%"}]},
        {"team": {"name": "Beta"}, "statistics": [{"type": "Shots on Goal", "value": 2},
                                                  {"type": "Ball Possession", "value": "40%"}]},
    ], results=2)
    players = er("/fixtures/players", [
        {"team": {"name": "Alpha"}, "players": [
            {"player": {"name": f"P{i}", "photo": "http://x/ph.png"},
             "statistics": [{"games": {"minutes": 90, "position": "F", "rating": str(9.0 - i * 0.1)},
                             "goals": {"total": 1 if i == 0 else 0, "assists": None}}]} for i in range(15)]},
        {"team": {"name": "Beta"}, "players": [
            {"player": {"name": f"Q{i}", "photo": "http://x/ph.png"},
             "statistics": [{"games": {"minutes": 90, "position": "M", "rating": str(7.0 - i * 0.1)},
                             "goals": {"total": 0, "assists": 1 if i == 1 else None}}]} for i in range(15)]},
    ], results=2)
    squad_home = er("/players/squads", [{"team": {"name": "Alpha"},
                    "players": [{"name": f"S{i}", "number": i, "position": "G", "photo": "http://x/ph.png"} for i in range(25)]}], results=1, team_id=1)
    squad_away = er("/players/squads", [{"team": {"name": "Beta"},
                    "players": [{"name": f"T{i}", "number": i, "position": "D"} for i in range(23)]}], results=1, team_id=2)
    coach_home = er("/coachs", [{"id": 10, "name": "Coach A", "age": 50, "nationality": "Alphaland", "photo": "http://x/c.png"}], results=1, team_id=1)
    coach_away = er("/coachs", [{"id": 20, "name": "Coach B", "age": 48, "nationality": "Betaland"}], results=1, team_id=2)
    team_home = er("/teams", [{"team": {"id": 1, "name": "Alpha", "country": "Alphaland", "founded": 1900, "logo": "http://x/l1.png"},
                               "venue": {"name": "Home Arena", "city": "Cap", "image": "http://x/v.png"}}], results=1, team_id=1)
    team_away = er("/teams", [{"team": {"id": 2, "name": "Beta", "country": "Betaland", "founded": 1910},
                               "venue": {"name": "Away Arena", "city": "Town"}}], results=1, team_id=2)
    injuries = er("/injuries", [], results=0, fixture_id=999001)  # the verified gap
    return {
        "fixture": fixture, "lineups": lineups, "events": events, "statistics": statistics,
        "players": players, "injuries": injuries, "squad_home": squad_home, "squad_away": squad_away,
        "coach_home": coach_home, "coach_away": coach_away, "team_home": team_home, "team_away": team_away,
    }


def all_vi_strings(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "vi" and isinstance(v, str):
                acc.append(v)
            all_vi_strings(v, acc)
    elif isinstance(o, list):
        for v in o:
            all_vi_strings(v, acc)


def main():
    ts = "2026-06-10T00:00:00+00:00"
    print("== full bundle ==")
    pack = build_scout_pack(fixture_id=999001, bundle=full_bundle(), last_checked_at=ts, plan="Pro", request_log=[])
    raw = json.dumps(pack, ensure_ascii=False)

    for k in OWNER_TOP_KEYS:
        check(k in pack, f"top-level key present: {k}")
    for sec in C.SECTION_KEYS:
        env = pack[sec]
        check(ENVELOPE_KEYS.issubset(env.keys()), f"{sec} is an evidence envelope")
        check(env["available"] is True and env["value"] is not None, f"{sec} available with real value")

    # redaction: no image/logo/photo URLs leaked
    check("http://" not in raw and "https://" not in raw, "no URLs in output (redacted)")
    for bad in ("logo", "photo", "image"):
        check(bad not in raw, f'no "{bad}" field in output')

    # bounding
    ev = pack["events_summary"]["value"]
    check(len(ev["timeline"]) <= C.MAX_EVENTS and ev["timeline_truncated"] is True, "events timeline bounded + truncation flagged")
    for col in pack["player_statistics"]["value"]:
        check(len(col["top_by_rating"]) <= C.MAX_PLAYER_STATS_PER_TEAM, f"player_statistics bounded for {col['team']}")
        check("_rk" not in json.dumps(col), "internal sort key stripped from output")
    for side in ("home", "away"):
        s = pack["squad"]["value"][side]
        check(len(s["sample"]) <= C.MAX_SQUAD_SAMPLE_PER_TEAM and s["players_count"] >= len(s["sample"]),
              f"squad sample bounded ({side}), count preserved")

    # player_statistics sorted by rating (top first)
    top = pack["player_statistics"]["value"][0]["top_by_rating"]
    check(top[0]["name"] == "P0", "player_statistics sorted by rating (highest first)")

    # injuries unresolved — never "no injuries"
    inj = pack["injuries"]
    check(inj["available"] is False, "injuries available == False (unresolved)")
    # The AI-guard lists intentionally say "do NOT state 'no injuries'" (a negation, like 不可提现).
    # Scope the claim-scan to the injuries data representation, where a false "no injuries" would live.
    inj_blob = json.dumps([pack["injuries"], pack["missing_evidence"].get("injuries"),
                           pack["source_ledger"].get("injuries")], ensure_ascii=False)
    check("no injuries" not in inj_blob.lower() and "无伤停" not in inj_blob, 'injuries data never states "no injuries"/"无伤停"')
    check(bool(inj["missing_reason"]) and "UNRESOLVED" in inj["missing_reason"], "injuries missing_reason set + UNRESOLVED")
    check("injuries" in pack["missing_evidence"], "injuries in missing_evidence")
    check("injuries" in pack["source_ledger"], "injuries in source_ledger")
    check(pack["feature_snapshot"]["injuries_unresolved"] is True, "feature_snapshot.injuries_unresolved == True")

    # AI guardrail
    check("injuries" not in pack["ai_allowed_explanations"], "AI not allowed to explain injuries")
    check(any("no injuries" in s for s in pack["ai_forbidden_explanations"]), "ai_forbidden guards against 'no injuries'")
    check(all(pack[f]["available"] and pack[f]["license_status"] == "ok" for f in pack["ai_allowed_explanations"]),
          "ai_allowed only verified + licensed fields")

    # no betting/odds/market wording anywhere
    bad_words = ["betting", "odds", "market", "盘口", "竞猜", "走地", "滚球", "大小球", "让球", "42.2", "下注"]
    hits = [w for w in bad_words if w.lower() in raw.lower()]
    check(not hits, f"no betting/odds wording (hits={hits})")

    # vi strings: zero Han
    vi = []
    all_vi_strings(pack, vi)
    vi_han = [s for s in vi if HAN.search(s)]
    check(not vi_han, f"all vi strings have 0 Han (offenders={vi_han})")

    # source_ledger provenance complete
    check(set(pack["source_ledger"].keys()) >= set(C.SECTION_KEYS) | {"injuries"}, "source_ledger covers every section + injuries")

    print("== honest-empty bundle (missing lineups/events/stats/players) ==")
    b2 = full_bundle()
    for empty_key, sec in (("lineups", "lineups"), ("events", "events_summary"),
                           ("statistics", "team_statistics"), ("players", "player_statistics")):
        b2[empty_key] = er("/x", [], results=0)
    pack2 = build_scout_pack(fixture_id=999002, bundle=b2, last_checked_at=ts, plan="Pro", request_log=[])
    for sec in ("lineups", "formation", "events_summary", "team_statistics", "player_statistics"):
        env = pack2[sec]
        check(env["available"] is False and env["value"] is None, f"honest-empty: {sec} unavailable, value None")
        check(bool(env["fallback_text"]) and bool(env["missing_reason"]), f"honest-empty: {sec} has fallback + reason")
    check(pack2["feature_snapshot"]["coverage_score"] < 100, "coverage_score drops when sources missing")

    print()
    if _fails:
        print(f"RESULT: FAIL ({len(_fails)} checks)")
        for f in _fails:
            print("  -", f)
        sys.exit(1)
    print("RESULT: PASS (all contract checks)")


if __name__ == "__main__":
    main()
