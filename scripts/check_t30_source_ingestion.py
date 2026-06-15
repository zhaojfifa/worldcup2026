#!/usr/bin/env python3
"""
P3B — T-30 source-ingestion guard.
  - docs/data_audit/mvp2_t30_sources/<date>.json exists; every item carries the required fields;
  - source_status ∈ the valid set;
  - lineup/injury availability are explicit booleans;
  - update_eligibility is NEVER an automatic-update value (no live feed ⇒ operator confirm).
Usage: check_t30_source_ingestion.py [--date YYYY-MM-DD] | --selftest.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_t30_sources"
REQUIRED = ("fixture_id", "match", "kickoff_time", "t30_deadline", "expected_source_fields",
            "available_source_fields", "missing_source_fields", "lineup_availability",
            "injury_news_availability", "tactical_variable_availability", "source_status",
            "update_eligibility", "next_operator_action")
VALID_STATUS = {"SOURCE_READY", "SOURCE_MISSING", "SOURCE_STALE", "SOURCE_PARTIAL", "OPERATOR_OVERRIDE_REQUIRED"}
ELIG_OK = {"OPERATOR_CONFIRM_REQUIRED", "OPERATOR_CONFIRMED"}  # never AUTO_UPDATE without a real feed


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(items):
    fails = []
    for it in items:
        for k in REQUIRED:
            if k not in it:
                fails.append("t30-source %s missing field %r" % (it.get("fixture_id"), k))
        if it.get("source_status") not in VALID_STATUS:
            fails.append("t30-source %s invalid source_status %r" % (it.get("fixture_id"), it.get("source_status")))
        if not isinstance(it.get("lineup_availability"), bool) or not isinstance(it.get("injury_news_availability"), bool):
            fails.append("t30-source %s lineup/injury availability must be explicit booleans" % it.get("fixture_id"))
        if it.get("update_eligibility") not in ELIG_OK:
            fails.append("t30-source %s update_eligibility %r not allowed (no auto-update without a real feed)"
                         % (it.get("fixture_id"), it.get("update_eligibility")))
    return fails


def selftest():
    good = {k: "x" for k in REQUIRED}
    good.update(lineup_availability=False, injury_news_availability=False, source_status="SOURCE_MISSING",
                update_eligibility="OPERATOR_CONFIRM_REQUIRED")
    checks = [
        ("clean passes", scan([good]) == []),
        ("bad status caught", any("invalid source_status" in x for x in scan([dict(good, source_status="X")]))),
        ("auto-update caught", any("auto-update" in x for x in scan([dict(good, update_eligibility="AUTO_UPDATE")]))),
        ("non-bool availability caught", any("explicit booleans" in x for x in scan([dict(good, lineup_availability="yes")]))),
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
        print("FAIL  no t30 source file (run mvp2_t30_source.py build)"); return 1
    fails = scan(_load(p).get("items", []))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("T30 SOURCE INGESTION FAIL — %d issue(s)" % len(fails)); return 1
    print("T30 SOURCE INGESTION PASS (%s; source_status explicit; no auto-update without a real feed)" % p.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
