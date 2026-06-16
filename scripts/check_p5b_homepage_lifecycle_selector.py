#!/usr/bin/env python3
"""P5B — lifecycle selector guard (JSON). The artifact's roles must obey the rules: primary upcoming +
source-qualified (not finished/operator_estimated/archive/demo); secondary <=2; latest_recap finished;
blocked PRIMARY_REVIEW_REQUIRED when no primary; reason_for_role recorded; send HOLD.
Usage: [--date D] | --selftest"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
LC = ROOT / "frontend/src/data/homepageLifecycle.json"
SQ = {"computed", "operator_confirmed", "seed"}


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(o):
    f = []
    p = o.get("primary_prediction")
    if p:
        if "FINISHED" in p["lifecycle_state"]: f.append("primary is FINISHED")
        if p.get("model_source") == "operator_estimated": f.append("primary is operator_estimated")
        if p["lifecycle_state"] in ("ARCHIVE_ONLY", "EXCLUDED_DEMO"): f.append("primary is archive/demo")
        if p.get("model_source") not in SQ: f.append("primary not source-qualified (%s)" % p.get("model_source"))
        if not p.get("reason_for_role"): f.append("primary has no reason_for_role")
    else:
        if not any(b.get("state") == "PRIMARY_REVIEW_REQUIRED" for b in o.get("blocked_items", [])):
            f.append("no primary and no PRIMARY_REVIEW_REQUIRED block")
    if len(o.get("secondary_predictions", [])) > 2: f.append("more than 2 secondary")
    for s in o.get("secondary_predictions", []):
        if "FINISHED" in s["lifecycle_state"]: f.append("secondary %s finished" % s["fixture_id"])
    lr = o.get("latest_recap")
    if lr and "FINISHED" not in lr["lifecycle_state"]: f.append("latest_recap not finished")
    if o.get("send_status") != "HOLD": f.append("send_status not HOLD")
    return f


def selftest():
    good = {"primary_prediction": {"fixture_id": "1", "lifecycle_state": "UPCOMING_PREDICTION_READY", "model_source": "computed", "reason_for_role": "x"},
            "secondary_predictions": [{"fixture_id": "2", "lifecycle_state": "UPCOMING_PREDICTION_READY", "model_source": "operator_estimated"}],
            "latest_recap": {"fixture_id": "3", "lifecycle_state": "FINISHED_OBSERVATION_READY"}, "send_status": "HOLD"}
    checks = [("good passes", scan(good) == []),
              ("finished primary caught", any("FINISHED" in x for x in scan(dict(good, primary_prediction=dict(good["primary_prediction"], lifecycle_state="FINISHED_RECAP_READY"))))),
              ("op_est primary caught", any("operator_estimated" in x for x in scan(dict(good, primary_prediction=dict(good["primary_prediction"], model_source="operator_estimated"))))),
              ("no-primary block ok", scan({"primary_prediction": None, "blocked_items": [{"state": "PRIMARY_REVIEW_REQUIRED"}], "send_status": "HOLD"}) == []),
              (">2 secondary caught", any("more than 2" in x for x in scan(dict(good, secondary_predictions=[good["secondary_predictions"][0]] * 3))))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    if "--selftest" in sys.argv: return selftest()
    o = _load(LC)
    if not o: print("FAIL  homepageLifecycle.json missing (run mvp2_homepage_lifecycle_selector.py build)"); return 1
    fails = scan(o)
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5B LIFECYCLE SELECTOR FAIL — %d" % len(fails)); return 1
    print("P5B LIFECYCLE SELECTOR PASS (primary upcoming+source-qualified · secondary<=2 · recap finished · HOLD)"); return 0


if __name__ == "__main__": sys.exit(main())
