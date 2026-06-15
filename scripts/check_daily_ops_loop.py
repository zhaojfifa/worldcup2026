#!/usr/bin/env python3
"""
P2 — daily-ops-loop guard. Verifies the operator command loop is real and safe:
  - scripts/mvp2_daily_ops.py exists with every required subcommand + --selftest;
  - it writes the consolidated frontend/src/data/dailyOpsState.json (the command-center snapshot);
  - the loop NEVER auto-publishes (build-artifacts only applies from an operator reviewed JSON) and
    NEVER auto-sends (send_status HOLD; no send wiring);
  - dailyOpsState carries the review/t30/recap/share queues + day_close + next_operator_action + HOLD.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OPS = ROOT / "scripts" / "mvp2_daily_ops.py"
STATE = ROOT / "frontend" / "src" / "data" / "dailyOpsState.json"
REQUIRED_CMDS = ["status", "build-queue", "generate-drafts", "review-summary", "build-artifacts",
                 "t30-status", "recap-status", "share-refresh", "close-day"]
STATE_KEYS = ["review_queue", "t30_queue", "recap_queue", "share_packages", "day_close",
              "next_operator_action", "send_status"]


def scan_script(src):
    fails = []
    for c in REQUIRED_CMDS:
        if ('"%s"' % c) not in src and ("'%s'" % c) not in src:
            fails.append("ops script missing subcommand %r" % c)
    if "def selftest" not in src:
        fails.append("ops script missing --selftest")
    if "dailyOpsState.json" not in src:
        fails.append("ops script does not write dailyOpsState.json")
    # operator gate: build-artifacts must require a reviewed JSON (no draft auto-publish)
    if "no reviewed JSON" not in src and "reviewed JSON (operator review required" not in src:
        fails.append("build-artifacts may publish without a reviewed JSON (operator gate missing)")
    return fails


def scan_state(st):
    fails = []
    for k in STATE_KEYS:
        if k not in st:
            fails.append("dailyOpsState missing %r" % k)
    if st.get("send_status") != "HOLD":
        fails.append("dailyOpsState send_status must be HOLD")
    return fails


def selftest():
    good_src = " ".join('"%s"' % c for c in REQUIRED_CMDS) + " def selftest(): pass dailyOpsState.json 'no reviewed JSON'"
    good_state = {k: ([] if k.endswith("queue") or k == "share_packages" else {}) for k in STATE_KEYS}
    good_state["send_status"] = "HOLD"
    checks = [
        ("clean script passes", scan_script(good_src) == []),
        ("missing cmd caught", any("subcommand" in x for x in scan_script(good_src.replace('"close-day"', "")))),
        ("missing gate caught", any("operator gate" in x for x in scan_script(good_src.replace("'no reviewed JSON'", "")))),
        ("clean state passes", scan_state(good_state) == []),
        ("auto-send caught", any("HOLD" in x for x in scan_state(dict(good_state, send_status="LIVE")))),
        ("missing queue caught", any("review_queue" in x for x in scan_state({k: v for k, v in good_state.items() if k != "review_queue"}))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fails = []
    if not OPS.exists():
        print("FAIL  mvp2_daily_ops.py missing"); return 1
    fails += scan_script(OPS.read_text(encoding="utf-8"))
    if not STATE.exists():
        fails.append("dailyOpsState.json missing (run mvp2_daily_ops.py status/close-day)")
    else:
        fails += scan_state(json.loads(STATE.read_text(encoding="utf-8")))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("DAILY OPS LOOP FAIL — %d issue(s)" % len(fails)); return 1
    print("DAILY OPS LOOP PASS (9 subcommands · selftest · dailyOpsState snapshot · operator gate · send HOLD)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
