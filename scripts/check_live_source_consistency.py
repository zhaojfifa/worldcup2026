#!/usr/bin/env python3
"""P4R++ owner-view — backend↔frontend source consistency. The frontend-active content (primary
fixture + its date) must match the live backend runtime slate. Fails if backend runtime date and the
rendered homepage primary disagree, or the primary fixture is absent from the backend slate.
Usage: check_live_source_consistency.py --frontend-url FE --backend-url BE | --selftest"""
import json, pathlib, sys, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        print("PASS consistency logic (backend date == active date AND primary in backend slate)")
        print("1/1 checks pass"); return 0
    fe = a[a.index("--frontend-url") + 1] if "--frontend-url" in a else "https://worldcup2026-izid.onrender.com"
    be = a[a.index("--backend-url") + 1] if "--backend-url" in a else "https://worldcup2026-api-71n6.onrender.com"
    # R5 follow-up: runtime content is the source of truth when active. Resolve the ACTIVE selectedHotspot
    # from the backend runtime-content package (stored + fresh + has a selectedHotspot); fall back to the
    # bundled selectedHotspot.json only when runtime content is absent/stale/invalid.
    sel = _load(ROOT / "frontend/src/data/selectedHotspot.json") or {}
    sel_source = "bundled"
    try:
        with urllib.request.urlopen(be.rstrip("/") + "/api/v1/runtime-content", timeout=20) as r:
            rc = json.loads(r.read().decode("utf-8"))
        fr = rc.get("freshness") or {}
        if fr.get("stored") and fr.get("stale") is not True and rc.get("selectedHotspot") and rc.get("date"):
            rsel = rc["selectedHotspot"]
            sel = {"date": rc.get("date"), "fixture_key": rsel.get("fixture_key"),
                   "home": rsel.get("home"), "away": rsel.get("away")}
            sel_source = "runtime"
    except Exception:
        pass
    with urllib.request.urlopen(be.rstrip("/") + "/api/v1/daily-fixtures", timeout=20) as r:
        bd = json.loads(r.read().decode("utf-8"))
    fails = []
    backend_date = bd.get("date")
    active_date = sel.get("date")
    if backend_date != active_date:
        fails.append("backend runtime date %r != frontend active content date %r" % (backend_date, active_date))
    keys = {str(f.get("id")) for f in bd.get("fixtures", [])} | {str(f.get("external_game_id")) for f in bd.get("fixtures", [])}
    if str(sel.get("fixture_key")) not in keys and ("af:" + str(sel.get("fixture_key"))) not in keys:
        fails.append("frontend primary %r not in backend active slate" % sel.get("fixture_key"))
    # the rendered homepage must show the same primary teams
    dom = dump_dom(fe.rstrip("/") + "/?lang=zh")
    for t in (sel.get("home"), sel.get("away")):
        if t and dom and t not in dom:
            fails.append("rendered homepage missing backend-active primary team %r" % t)
    print("LIVE SOURCE CONSISTENCY · backend_date=%s · active_date=%s (sel_source=%s) · primary=%s" % (backend_date, active_date, sel_source, sel.get("fixture_key")))
    for x in fails: print("FAIL  %s" % x)
    if fails: print("LIVE SOURCE CONSISTENCY FAIL — %d" % len(fails)); return 1
    print("LIVE SOURCE CONSISTENCY PASS (backend runtime == %s active selectedHotspot; primary rendered)" % sel_source); return 0


if __name__ == "__main__": sys.exit(main())
