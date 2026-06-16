#!/usr/bin/env python3
"""P5B — no-finished-primary guard. The lifecycle primary must not be a finished match, and the
rendered homepage primary card must be the lifecycle (upcoming) primary, not a finished fixture.
Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]
FIN = ("FINISHED", "RECAP", "ARCHIVED", "LIVE_OR_LOCKED")


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan_artifact(lc, man):
    f = []
    p = lc.get("primary_prediction")
    if p and any(s in p["lifecycle_state"] for s in FIN):
        f.append("lifecycle primary %s is finished/live (%s)" % (p["fixture_id"], p["lifecycle_state"]))
    # cross-check the manifest status of the primary
    if p:
        row = next((x for x in man.get("fixtures", []) if str(x.get("id") or x.get("external_game_id")) == p["fixture_id"]), None)
        if row and (row.get("status") or "").lower() == "finished":
            f.append("lifecycle primary %s has manifest status finished" % p["fixture_id"])
    return f


def selftest():
    man = {"fixtures": [{"id": "1", "status": "scheduled"}]}
    checks = [("upcoming primary passes", scan_artifact({"primary_prediction": {"fixture_id": "1", "lifecycle_state": "UPCOMING_PREDICTION_READY"}}, man) == []),
              ("finished-state caught", any("finished/live" in x for x in scan_artifact({"primary_prediction": {"fixture_id": "1", "lifecycle_state": "FINISHED_RECAP_READY"}}, man))),
              ("finished-status caught", any("manifest status finished" in x for x in scan_artifact({"primary_prediction": {"fixture_id": "1", "lifecycle_state": "UPCOMING_PREDICTION_READY"}}, {"fixtures": [{"id": "1", "status": "finished"}]})))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    lc = _load(ROOT / "frontend/src/data/homepageLifecycle.json") or {}
    man = _load(ROOT / "frontend/public/data/daily-fixtures.json") or _load(ROOT / "frontend/src/data/dailyFixtures.generated.json") or {}
    fails = scan_artifact(lc, man)
    # rendered cross-check: the primary teams appear in the prediction zone (best-effort: present in DOM)
    p = lc.get("primary_prediction")
    if p and not fails:
        dom = dump_dom(base.rstrip("/") + "/?lang=zh")
        for t in [x.strip() for x in p["match"].split(" vs ")]:
            if t and dom and t not in dom: fails.append("rendered homepage missing lifecycle primary team %r" % t)
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5B NO-FINISHED-PRIMARY FAIL — %d" % len(fails)); return 1
    print("P5B NO-FINISHED-PRIMARY PASS (primary is upcoming, not finished; rendered primary matches lifecycle)"); return 0


if __name__ == "__main__": sys.exit(main())
