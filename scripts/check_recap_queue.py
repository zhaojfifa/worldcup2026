#!/usr/bin/env python3
"""
P2 — recap queue guard. Recap claims are never invented.
  - durable recap queue file exists; every item has the 10 required fields;
  - publish_eligibility ∈ {PUBLISHED, OBSERVATION_READY, PENDING};
  - every item carries the no_fake_recap guard;
  - an OBSERVATION_READY item is not labelled PUBLISHED (observation is not a full recap).
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_recap_queue"
REQUIRED = ("fixture_id", "match", "status", "source", "deadline", "owner", "next_action",
            "guard_status", "artifact_path", "publish_eligibility")
VALID = {"PUBLISHED", "OBSERVATION_READY", "PENDING"}


def scan(items):
    fails = []
    for it in items:
        for k in REQUIRED:
            if k not in it:
                fails.append("recap item %s missing field %r" % (it.get("fixture_id"), k))
        if it.get("publish_eligibility") not in VALID:
            fails.append("recap item %s invalid publish_eligibility %r" % (it.get("fixture_id"), it.get("publish_eligibility")))
        if "no_fake_recap" not in (it.get("guard_status") or ""):
            fails.append("recap item %s missing no_fake_recap guard" % it.get("fixture_id"))
        if it.get("status") == "OBSERVATION_READY" and it.get("publish_eligibility") == "PUBLISHED":
            fails.append("recap item %s observation labelled PUBLISHED (full recap faked)" % it.get("fixture_id"))
    return fails


def _latest():
    files = sorted(QDIR.glob("*.json")) if QDIR.exists() else []
    return files[-1] if files else None


def selftest():
    good = [{k: "x" for k in REQUIRED}]
    good[0].update(status="OBSERVATION_READY", publish_eligibility="OBSERVATION_READY", guard_status="no_fake_recap")
    fake = [dict(good[0], status="OBSERVATION_READY", publish_eligibility="PUBLISHED")]
    checks = [
        ("clean passes", scan(good) == []),
        ("faked full recap caught", any("full recap faked" in x for x in scan(fake))),
        ("missing guard caught", any("no_fake_recap" in x for x in scan([dict(good[0], guard_status="x")]))),
        ("missing field caught", any("missing field" in x for x in scan([{"fixture_id": "1"}]))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    p = _latest()
    if not p:
        print("FAIL  no recap queue file (run mvp2_daily_ops.py recap-status)"); return 1
    q = json.loads(p.read_text(encoding="utf-8"))
    fails = scan(q.get("items", []))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RECAP QUEUE FAIL — %d issue(s)" % len(fails)); return 1
    print("RECAP QUEUE PASS (%s · %d item(s); no fake recap)" % (p.name, len(q.get("items", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
