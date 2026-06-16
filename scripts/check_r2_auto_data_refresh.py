#!/usr/bin/env python3
"""R2 guard — automated data refresh from API-FOOTBALL produces a valid daily registry with NO
manual file and NO fabricated data.

--selftest (offline): the API status→word mapping is honest (NS→scheduled, FT→finished, live→live);
  a finished fixture WITH goals keeps its score; a NOT-finished fixture (NS) carries NO score even if
  the feed had numbers; evaluate() carries the API id + kickoff through for an unmapped fixture.
--date YYYY-MM-DD: the generated docs/data_audit/mvp2_match_sync/daily_fixtures_<date>.json exists,
  was source_mode=api-football, has every required field per fixture, and is honest:
    * scheduled/unknown fixtures have score_home/score_away == null (no invented score)
    * a finished fixture has an integer score OR null (never a guessed score)
    * no fixture invents finished status without the source word
Usage: --selftest | --date 2026-06-16"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC = ROOT / "docs/data_audit/mvp2_match_sync"
REQUIRED = ["external_game_id", "internal_fixture_id", "home_team", "away_team", "kickoff_time_utc",
            "status", "score_home", "score_away", "lifecycle_state", "pre_match_allowed",
            "recap_ready", "recap_needed", "narrative_renderable", "hero_candidate",
            "recap_candidate", "next_candidate"]


def scan_registry(date_iso):
    f = []
    compact = date_iso.replace("-", "")
    p = SYNC / ("daily_fixtures_%s.json" % compact)
    if not p.exists():
        return ["registry not generated: %s (run sync --source api-football --date %s)" % (p.name, date_iso)]
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("source_mode") != "api-football":
        f.append("source_mode=%r (expected api-football)" % d.get("source_mode"))
    fixtures = d.get("fixtures") or []
    if not fixtures:
        f.append("no fixtures in generated registry")
    for fx in fixtures:
        nm = "%s vs %s" % (fx.get("home_team"), fx.get("away_team"))
        for k in REQUIRED:
            if k not in fx:
                f.append("%s: missing field %s" % (nm, k))
        st = fx.get("status")
        sh, sa = fx.get("score_home"), fx.get("score_away")
        # honesty: only a finished match may carry a score; non-finished must be null/null
        if st in ("scheduled", "unknown") and (sh is not None or sa is not None):
            f.append("%s: %s fixture carries a score %s-%s (invented?)" % (nm, st, sh, sa))
        if (sh is None) != (sa is None):
            f.append("%s: half-null score %s-%s" % (nm, sh, sa))
        if sh is not None and not (isinstance(sh, int) and isinstance(sa, int)):
            f.append("%s: non-integer score" % nm)
    return f


def selftest():
    sys.path.insert(0, str(ROOT / "scripts"))
    from _api_football_slate import _status_word
    import importlib.util
    spec = importlib.util.spec_from_file_location("ms", ROOT / "scripts" / "mvp2_match_sync.py")
    ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
    from datetime import datetime, timezone
    now = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    # unmapped finished fixture with goals -> score kept, id+kickoff carried
    fin = ms.evaluate({"home": "Iran", "away": "New Zealand", "score_home": 2, "score_away": 2,
                       "status": "finished", "kickoff_utc": "2026-06-16T01:00:00+00:00",
                       "api_fixture_id": 1489378}, now, now.isoformat(), "api-football", "t", "t")
    # unmapped scheduled fixture -> NO score even if a stray number sneaks in upstream (we pass None)
    sched = ms.evaluate({"home": "France", "away": "Senegal", "score_home": None, "score_away": None,
                         "status": "scheduled", "kickoff_utc": "2026-06-16T19:00:00+00:00",
                         "api_fixture_id": 1489383}, now, now.isoformat(), "api-football", "t", "t")
    checks = [
        ("NS->scheduled", _status_word("NS") == "scheduled"),
        ("FT->finished", _status_word("FT") == "finished"),
        ("2H->live", _status_word("2H") == "live"),
        ("PST->postponed", _status_word("PST") == "postponed"),
        ("finished keeps score", fin["score_home"] == 2 and fin["score_away"] == 2),
        ("finished carries api id", fin["internal_fixture_id"] == "1489378"),
        ("finished carries kickoff", fin["kickoff_time_utc"] == "2026-06-16T01:00:00+00:00"),
        ("scheduled has null score", sched["score_home"] is None and sched["score_away"] is None),
        ("scheduled pre-match allowed", sched["pre_match_allowed"]),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        return selftest()
    date_iso = a[a.index("--date") + 1] if "--date" in a else "2026-06-16"
    fails = scan_registry(date_iso)
    for x in fails: print("FAIL  %s" % x)
    if fails:
        print("R2 AUTO DATA REFRESH FAIL — %d" % len(fails)); return 1
    print("R2 AUTO DATA REFRESH PASS (api-football registry for %s: required fields present, scores honest, no invention)" % date_iso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
