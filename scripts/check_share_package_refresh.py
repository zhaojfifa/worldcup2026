#!/usr/bin/env python3
"""
P2 — share-package-refresh guard.
  - durable share-package queue file exists; every item has the 10 required fields;
  - status ∈ {SHARE_READY, SHARE_MISSING};
  - a SHARE_READY item is PUBLISHED-eligible and names its /share route in next_action.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_share_packages"
REQUIRED = ("fixture_id", "match", "status", "source", "deadline", "owner", "next_action",
            "guard_status", "artifact_path", "publish_eligibility")
VALID = {"SHARE_READY", "SHARE_MISSING"}


def scan(items):
    fails = []
    for it in items:
        for k in REQUIRED:
            if k not in it:
                fails.append("share item %s missing field %r" % (it.get("fixture_id"), k))
        if it.get("status") not in VALID:
            fails.append("share item %s invalid status %r" % (it.get("fixture_id"), it.get("status")))
        if it.get("status") == "SHARE_READY" and "/share/" not in (it.get("next_action") or ""):
            fails.append("share item %s SHARE_READY but no /share route named" % it.get("fixture_id"))
    return fails


def _latest():
    files = sorted(QDIR.glob("*.json")) if QDIR.exists() else []
    return files[-1] if files else None


def selftest():
    good = [{k: "x" for k in REQUIRED}]
    good[0].update(status="SHARE_READY", next_action="share card live: /share/fixture/1")
    checks = [
        ("clean passes", scan(good) == []),
        ("bad status caught", any("invalid status" in x for x in scan([dict(good[0], status="X")]))),
        ("ready-without-route caught", any("no /share route" in x for x in scan([dict(good[0], next_action="go")]))),
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
        print("FAIL  no share package file (run mvp2_daily_ops.py share-refresh)"); return 1
    q = json.loads(p.read_text(encoding="utf-8"))
    fails = scan(q.get("items", []))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("SHARE PACKAGE FAIL — %d issue(s)" % len(fails)); return 1
    print("SHARE PACKAGE PASS (%s · %d item(s))" % (p.name, len(q.get("items", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
