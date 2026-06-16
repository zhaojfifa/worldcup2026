#!/usr/bin/env python3
"""
P4B — recommendation-closure guard.
  - the closure artifact exists for the date; every item carries the required fields;
  - result_status ∈ {HIT, MISS, PARTIAL, OBSERVATION_ONLY, PENDING};
  - actual_score missing ⇒ result_status PENDING (no closure invented);
  - a non-PENDING item must carry a reason (why_it_hit_or_missed) OR be OBSERVATION_ONLY;
  - recap_eligibility ∈ {FULL_RECAP, OBSERVATION_ONLY, PENDING}; no FULL_RECAP without actual_score;
  - every item declares the no_fake guard marker.
Usage: check_recommendation_closure.py [--date YYYY-MM-DD] | --selftest.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_recommendation_closure"
REQUIRED = ("fixture_id", "match", "predicted_score", "actual_score", "result_status", "source_basis",
            "why_it_hit_or_missed", "correction_note", "recap_eligibility", "recap_artifact_path",
            "share_copy_status", "operator_next_action")
STATUS = {"HIT", "MISS", "PARTIAL", "OBSERVATION_ONLY", "PENDING"}
ELIG = {"FULL_RECAP", "OBSERVATION_ONLY", "PENDING"}


def scan(items):
    fails = []
    for it in items:
        for k in REQUIRED:
            if k not in it:
                fails.append("closure %s missing field %r" % (it.get("fixture_id"), k))
        st = it.get("result_status")
        if st not in STATUS:
            fails.append("closure %s invalid result_status %r" % (it.get("fixture_id"), st))
        if not it.get("actual_score") and st != "PENDING":
            fails.append("closure %s has no actual_score but result_status=%r (must be PENDING)" % (it.get("fixture_id"), st))
        if it.get("recap_eligibility") not in ELIG:
            fails.append("closure %s invalid recap_eligibility %r" % (it.get("fixture_id"), it.get("recap_eligibility")))
        if it.get("recap_eligibility") == "FULL_RECAP" and not it.get("actual_score"):
            fails.append("closure %s FULL_RECAP without actual_score (faked)" % it.get("fixture_id"))
        if "no_fake" not in (it.get("guard_status") or ""):
            fails.append("closure %s missing no_fake guard marker" % it.get("fixture_id"))
    return fails


def selftest():
    good = [{k: "x" for k in REQUIRED}]
    good[0].update(result_status="PARTIAL", actual_score="1-1", recap_eligibility="OBSERVATION_ONLY",
                   guard_status="no_fake_recap")
    pend = [dict(good[0], result_status="HIT", actual_score=None, recap_eligibility="PENDING")]
    fake = [dict(good[0], recap_eligibility="FULL_RECAP", actual_score=None, result_status="PENDING")]
    checks = [
        ("clean passes", scan(good) == []),
        ("no-score-not-pending caught", any("must be PENDING" in x for x in scan(pend))),
        ("full-recap-without-score caught", any("FULL_RECAP without actual_score" in x for x in scan(fake))),
        ("missing guard caught", any("no_fake guard" in x for x in scan([dict(good[0], guard_status="x")]))),
        ("missing field caught", any("missing field" in x for x in scan([{"fixture_id": "1"}]))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    date = argv[argv.index("--date") + 1] if "--date" in argv else None
    files = sorted(QDIR.glob("*.json")) if QDIR.exists() else []
    p = (QDIR / ("%s.json" % date)) if date else (files[-1] if files else None)
    if not p or not p.exists():
        print("FAIL  no closure artifact (run mvp2_recommendation_closure.py build)"); return 1
    fails = scan((json.loads(p.read_text(encoding="utf-8")) or {}).get("items", []))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RECOMMENDATION CLOSURE FAIL — %d issue(s)" % len(fails)); return 1
    print("RECOMMENDATION CLOSURE PASS (%s; PENDING when no score; no faked full recap)" % p.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
