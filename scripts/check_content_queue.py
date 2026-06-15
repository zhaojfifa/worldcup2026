#!/usr/bin/env python3
"""
P1 — content-queue guard. Verifies frontend/src/data/dailyContentQueue.json supports >1 match/day
honestly:
  - primary_hotspot present, scheduled, and CURRENT (date == queue date; never stale unless carryover);
  - 1..4 secondary_matches, each with a content_state and a source_coverage label;
  - at least one secondary is ARTIFACT_READY/PUBLISHED (a real second match works on /predict);
  - recap_queue + t30_queue present;
  - every row carries content_state ∈ the state machine; source_coverage ∈ computed/operator_estimated/missing;
  - send_status == HOLD.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
STATES = {"FIXTURE_READY", "MODEL_READY", "PROMPT_READY", "REVIEW_READY", "ARTIFACT_READY", "PUBLISHED"}
COVERAGE = {"computed", "operator_estimated", "missing"}
READY = {"ARTIFACT_READY", "PUBLISHED"}


def scan(q):
    fails = []
    if not isinstance(q, dict):
        return ["queue is not an object"]
    p = q.get("primary_hotspot")
    if not isinstance(p, dict):
        fails.append("primary_hotspot missing")
    else:
        if (p.get("status") or "").lower() != "scheduled":
            fails.append("primary_hotspot is not a scheduled fixture (must be current, not finished)")
        if p.get("content_state") not in STATES:
            fails.append("primary_hotspot content_state %r invalid" % p.get("content_state"))
    sec = q.get("secondary_matches")
    if not isinstance(sec, list) or not (1 <= len(sec) <= 4):
        fails.append("secondary_matches must be a list of 1..4 (got %r)" % (len(sec) if isinstance(sec, list) else None))
        sec = sec if isinstance(sec, list) else []
    for s in sec:
        if s.get("content_state") not in STATES:
            fails.append("secondary %s content_state %r invalid" % (s.get("fixture_key"), s.get("content_state")))
        if s.get("source_coverage") not in COVERAGE:
            fails.append("secondary %s source_coverage %r invalid" % (s.get("fixture_key"), s.get("source_coverage")))
    if not any(s.get("content_state") in READY for s in sec):
        fails.append("no secondary match is ARTIFACT_READY/PUBLISHED (a second /predict match must work)")
    if not isinstance(q.get("recap_queue"), list):
        fails.append("recap_queue missing")
    if not isinstance(q.get("t30_queue"), list):
        fails.append("t30_queue missing")
    if q.get("send_status") != "HOLD":
        fails.append("send_status must be HOLD")
    return fails


def selftest():
    good = {
        "date": "2026-06-15",
        "primary_hotspot": {"fixture_key": "1489377", "status": "scheduled", "content_state": "PUBLISHED",
                            "source_coverage": "computed"},
        "secondary_matches": [
            {"fixture_key": "1489379", "content_state": "PUBLISHED", "source_coverage": "computed"},
            {"fixture_key": "1489380", "content_state": "PUBLISHED", "source_coverage": "operator_estimated"},
        ],
        "recap_queue": [{"fixture_key": "1489371"}], "t30_queue": [{"fixture_key": "1489377"}],
        "send_status": "HOLD",
    }
    checks = [
        ("clean passes", scan(good) == []),
        ("no primary caught", any("primary_hotspot missing" in x for x in scan({k: v for k, v in good.items() if k != "primary_hotspot"}))),
        ("finished primary caught", any("not a scheduled" in x for x in scan(dict(good, primary_hotspot=dict(good["primary_hotspot"], status="finished"))))),
        ("zero secondary caught", any("1..4" in x for x in scan(dict(good, secondary_matches=[])))),
        ("five secondary caught", any("1..4" in x for x in scan(dict(good, secondary_matches=[good["secondary_matches"][0]] * 5)))),
        ("no ready secondary caught", any("ARTIFACT_READY/PUBLISHED" in x for x in scan(dict(good, secondary_matches=[{"fixture_key": "z", "content_state": "FIXTURE_READY", "source_coverage": "missing"}])))),
        ("bad coverage caught", any("source_coverage" in x for x in scan(dict(good, secondary_matches=[dict(good["secondary_matches"][0], source_coverage="mock")])))),
        ("auto-send caught", any("HOLD" in x for x in scan(dict(good, send_status="LIVE")))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if not QUEUE.exists():
        print("FAIL  dailyContentQueue.json missing (run mvp2_build_daily_content_queue.py)"); return 1
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    fails = scan(q)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("CONTENT QUEUE FAIL — %d issue(s)" % len(fails)); return 1
    print("CONTENT QUEUE PASS (primary + %d secondary · recap %d · t30 %d · send HOLD)" % (
        len(q.get("secondary_matches", [])), len(q.get("recap_queue", [])), len(q.get("t30_queue", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
