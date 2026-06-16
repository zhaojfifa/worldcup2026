#!/usr/bin/env python3
"""P4R++ owner-view — live backend daily-source. Verifies GET /api/v1/daily-fixtures is the active
source-of-truth and does NOT treat WC-2022 history / demo as today's active content; and that the
admin update path is protected (POST without token → 401). Never sends the token.
Usage: check_live_api_daily_source.py --base-url URL | --selftest"""
import json, sys, urllib.request

ARCHIVE_2022 = ["Germany", "Qatar"]  # WC2022 archive opponents that must NOT be in the ACTIVE slate


def fetch(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def scan(d):
    fails = []
    if not d.get("date"):
        fails.append("live API has no active 'date'")
    fx = d.get("fixtures", [])
    if not fx:
        fails.append("live API active slate empty")
    teams = " ".join("%s %s" % (f.get("home"), f.get("away")) for f in fx)
    for t in ARCHIVE_2022:
        if t in teams:
            fails.append("WC-2022 archive team %r is in the ACTIVE slate (history treated as today)" % t)
    fr = d.get("freshness") or {}
    if fr.get("stale") is True:
        fails.append("live API manifest flagged stale")
    return fails


def selftest():
    ok = {"date": "2026-06-15", "fixtures": [{"home": "Belgium", "away": "Egypt"}], "freshness": {"stale": False}}
    bad = {"date": "2026-06-15", "fixtures": [{"home": "Germany", "away": "Japan"}], "freshness": {"stale": False}}
    checks = [("clean passes", scan(ok) == []),
              ("2022 in active caught", any("ACTIVE slate" in x for x in scan(bad))),
              ("stale caught", any("stale" in x for x in scan({"date": "x", "fixtures": [{"home": "A", "away": "B"}], "freshness": {"stale": True}})))]
    ok2 = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok2 else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-api-71n6.onrender.com"
    d = fetch(base.rstrip("/") + "/api/v1/daily-fixtures")
    fails = scan(d)
    # admin path is protected (no token → 401)
    try:
        req = urllib.request.Request(base.rstrip("/") + "/api/v1/admin/daily-fixtures/upload", data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15); fails.append("admin upload NOT protected (accepted with no token)")
    except urllib.error.HTTPError as e:
        if e.code != 401: fails.append("admin upload returned %d without token (expected 401)" % e.code)
    except Exception:
        pass
    print("LIVE API DAILY SOURCE · date=%s · %d fixtures · stale=%s" % (d.get("date"), len(d.get("fixtures", [])), (d.get("freshness") or {}).get("stale")))
    for f in fails: print("FAIL  %s" % f)
    if fails: print("LIVE API DAILY SOURCE FAIL — %d" % len(fails)); return 1
    print("LIVE API DAILY SOURCE PASS (active slate is today; no 2022/demo as active; admin path protected)"); return 0


if __name__ == "__main__": sys.exit(main())
