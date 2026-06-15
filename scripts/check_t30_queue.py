#!/usr/bin/env python3
"""
P2 — T-30 queue guard. T-30 claims are never invented.
  - durable t30 queue file exists; every item has the 10 required fields;
  - status ∈ {T30_PENDING, T30_READY, T30_SKIPPED};
  - a T30_PENDING item must declare the no-faked-update guard (pending => no update_text).
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_t30_queue"
REQUIRED = ("fixture_id", "match", "status", "source", "deadline", "owner", "next_action",
            "guard_status", "artifact_path", "publish_eligibility")
VALID = {"T30_PENDING", "T30_READY", "T30_SKIPPED"}


def scan(items):
    fails = []
    for it in items:
        for k in REQUIRED:
            if k not in it:
                fails.append("t30 item %s missing field %r" % (it.get("fixture_id"), k))
        if it.get("status") not in VALID:
            fails.append("t30 item %s invalid status %r" % (it.get("fixture_id"), it.get("status")))
        if it.get("status") == "T30_PENDING" and "no faked" not in (it.get("guard_status") or ""):
            fails.append("t30 item %s pending but no 'no faked update' guard recorded" % it.get("fixture_id"))
    return fails


def _latest():
    files = sorted(QDIR.glob("*.json")) if QDIR.exists() else []
    return files[-1] if files else None


def selftest():
    good = [{k: "x" for k in REQUIRED}]
    good[0].update(status="T30_PENDING", guard_status="pending=>no faked update_text")
    checks = [
        ("clean passes", scan(good) == []),
        ("bad status caught", any("invalid status" in x for x in scan([dict(good[0], status="LIVE")]))),
        ("pending-without-guard caught", any("no faked" in x for x in scan([dict(good[0], guard_status="ok")]))),
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
        print("FAIL  no t30 queue file (run mvp2_daily_ops.py t30-status)"); return 1
    q = json.loads(p.read_text(encoding="utf-8"))
    fails = scan(q.get("items", []))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("T30 QUEUE FAIL — %d issue(s)" % len(fails)); return 1
    print("T30 QUEUE PASS (%s · %d item(s); pending=no faked update)" % (p.name, len(q.get("items", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
