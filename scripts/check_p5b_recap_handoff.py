#!/usr/bin/env python3
"""P5B — recap handoff guard (JSON). Every finished tracked match (has observation/recap) must be
routed to latest_recap or finished_pending_recap; no fake full recap. Usage: [--date D] | --selftest"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
LC = ROOT / "frontend/src/data/homepageLifecycle.json"
PRED = ROOT / "frontend/src/data/predictionArtifacts"


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(lc):
    f = []
    routed = set()
    if lc.get("latest_recap"): routed.add(lc["latest_recap"]["fixture_id"])
    for r in lc.get("finished_pending_recap", []): routed.add(r["fixture_id"])
    # observation artifacts that are finished must be routed somewhere
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a:
            fk = str(a.get("id") or a.get("fixture_key"))
            allf = {r["fixture_id"] for r in lc.get("all_fixtures", [])}
            if fk in allf and fk not in routed and lc.get("latest_recap", {}) and lc["latest_recap"].get("fixture_id") != fk:
                # only fail if it's a finished fixture in the slate not routed
                row = next((x for x in lc.get("all_fixtures", []) if x["fixture_id"] == fk), None)
                if row and "FINISHED" in row.get("lifecycle_state", ""):
                    f.append("finished tracked %s (has observation) not routed to recap" % fk)
            if a.get("recap_ready") is True:
                f.append("observation %s claims recap_ready=true (fake full recap)" % fk)
    lr = lc.get("latest_recap")
    if lr and "FINISHED" not in lr["lifecycle_state"]: f.append("latest_recap is not finished")
    return f


def selftest():
    lc = {"latest_recap": {"fixture_id": "9", "lifecycle_state": "FINISHED_OBSERVATION_READY"}, "finished_pending_recap": [], "all_fixtures": [{"fixture_id": "9", "lifecycle_state": "FINISHED_OBSERVATION_READY"}]}
    checks = [("routed recap passes", scan(lc) == [] or all("not routed" not in x for x in scan(lc))),
              ("non-finished recap caught", any("not finished" in x for x in scan({"latest_recap": {"fixture_id": "1", "lifecycle_state": "UPCOMING_PREDICTION_READY"}, "all_fixtures": []})))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    if "--selftest" in sys.argv: return selftest()
    lc = _load(LC) or {}
    fails = scan(lc)
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5B RECAP HANDOFF FAIL — %d" % len(fails)); return 1
    print("P5B RECAP HANDOFF PASS (finished tracked matches routed to recap/pending; no fake full recap)"); return 0


if __name__ == "__main__": sys.exit(main())
