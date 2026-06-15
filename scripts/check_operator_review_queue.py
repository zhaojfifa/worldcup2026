#!/usr/bin/env python3
"""
P2 — operator-review-queue guard. The review gate CANNOT be bypassed.
  - the durable queue file exists for the latest date;
  - every item carries the 10 required fields;
  - publish_eligibility ∈ {PUBLISHED, REVIEW_REQUIRED};
  - an item is PUBLISHED ONLY if status == ARTIFACT_READY (i.e. a reviewed JSON was applied) — a
    GENERATED/GUARD_PASSED/APPROVED/NO_DRAFT item must be REVIEW_REQUIRED (no draft auto-publish).
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_operator_review_queue"
REQUIRED = ("fixture_id", "match", "status", "source", "deadline", "owner", "next_action",
            "guard_status", "artifact_path", "publish_eligibility")


def scan(items):
    fails = []
    for it in items:
        for k in REQUIRED:
            if k not in it:
                fails.append("review item %s missing field %r" % (it.get("fixture_id"), k))
        elig = it.get("publish_eligibility")
        if elig not in ("PUBLISHED", "REVIEW_REQUIRED"):
            fails.append("review item %s invalid publish_eligibility %r" % (it.get("fixture_id"), elig))
        if elig == "PUBLISHED" and it.get("status") != "ARTIFACT_READY":
            fails.append("review item %s PUBLISHED without ARTIFACT_READY (review gate bypassed)" % it.get("fixture_id"))
        if it.get("status") in ("GENERATED", "GUARD_PASSED", "APPROVED", "NO_DRAFT") and elig != "REVIEW_REQUIRED":
            fails.append("review item %s status %r must be REVIEW_REQUIRED" % (it.get("fixture_id"), it.get("status")))
    return fails


def _latest():
    files = sorted(QDIR.glob("*.json")) if QDIR.exists() else []
    return files[-1] if files else None


def selftest():
    good = [{k: "x" for k in REQUIRED}]
    good[0].update(status="ARTIFACT_READY", publish_eligibility="PUBLISHED")
    bypass = [dict(good[0], status="GUARD_PASSED", publish_eligibility="PUBLISHED")]
    review = [dict(good[0], status="GUARD_PASSED", publish_eligibility="REVIEW_REQUIRED")]
    checks = [
        ("published-after-review passes", scan(good) == []),
        ("bypass caught", any("gate bypassed" in x for x in scan(bypass))),
        ("guard_passed stays review_required", scan(review) == []),
        ("missing field caught", any("missing field" in x for x in scan([{ "fixture_id": "1" }]))),
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
        print("FAIL  no operator review queue file (run mvp2_daily_ops.py review-summary)"); return 1
    q = json.loads(p.read_text(encoding="utf-8"))
    fails = scan(q.get("items", []))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("OPERATOR REVIEW QUEUE FAIL — %d issue(s)" % len(fails)); return 1
    print("OPERATOR REVIEW QUEUE PASS (%s · %d item(s); review gate not bypassable)" % (p.name, len(q.get("items", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
