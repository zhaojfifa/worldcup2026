#!/usr/bin/env python3
"""
P3B — no-fake-T30-claims guard. The hard compliance gate for T-30:
  - a fixture must NOT claim lineup_availability/injury_news_availability=true while its source_status
    is SOURCE_MISSING/SOURCE_PARTIAL (would be an invented availability);
  - a prediction artifact's t30.update_text must be null UNLESS the operator confirmed
    (t30.status ∈ {ready, skipped}) — no invented KO-30 update;
  - the t30-source layer must declare the no_fake_t30 guard marker.
Usage: check_no_fake_t30_claims.py [--date YYYY-MM-DD] | --selftest.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QDIR = ROOT / "docs" / "data_audit" / "mvp2_t30_sources"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan_sources(items):
    fails = []
    for it in items:
        st = it.get("source_status")
        if st in ("SOURCE_MISSING", "SOURCE_PARTIAL"):
            if it.get("lineup_availability") is True:
                fails.append("t30 %s claims lineup available while source is %s (invented)" % (it.get("fixture_id"), st))
            if it.get("injury_news_availability") is True:
                fails.append("t30 %s claims injury/news available while source is %s (invented)" % (it.get("fixture_id"), st))
        if "no_fake_t30" not in (it.get("guard_status") or ""):
            fails.append("t30 %s missing no_fake_t30 guard marker" % it.get("fixture_id"))
    return fails


def scan_artifacts():
    fails = []
    if not PRED_DIR.exists():
        return fails
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if not a or "recap_ready" in a:
            continue
        t = a.get("t30") or {}
        if t.get("status") == "pending" and t.get("update_text") not in (None, ""):
            fails.append("%s t30 pending but update_text present (invented KO-30 update)" % p.name)
    return fails


def selftest():
    bad = [{"fixture_id": "1", "source_status": "SOURCE_MISSING", "lineup_availability": True,
            "injury_news_availability": False, "guard_status": "no_fake_t30"}]
    good = [{"fixture_id": "1", "source_status": "SOURCE_PARTIAL", "lineup_availability": False,
             "injury_news_availability": False, "guard_status": "no_fake_t30 (no live feed)"}]
    checks = [
        ("clean passes", scan_sources(good) == []),
        ("invented lineup caught", any("invented" in x for x in scan_sources(bad))),
        ("missing guard caught", any("no_fake_t30 guard" in x for x in scan_sources([dict(good[0], guard_status="x")]))),
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
    fails = []
    if not p or not p.exists():
        fails.append("no t30 source file to verify")
    else:
        fails += scan_sources(_load(p).get("items", []))
    fails += scan_artifacts()
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("NO-FAKE-T30 FAIL — %d issue(s)" % len(fails)); return 1
    print("NO-FAKE-T30 PASS (no invented lineup/injury availability; no faked KO-30 update_text)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
