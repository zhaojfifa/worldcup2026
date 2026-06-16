#!/usr/bin/env python3
"""P5B — /internal/daily lifecycle trace guard (source). DailyStatusPage must render the lifecycle
trace: primary + why, latest recap, secondary, next, pending recap, archive/demo excluded, blocked,
next action, send HOLD. Usage: [--base-url ignored] | --selftest"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "frontend/src/pages/DailyStatusPage.tsx"
REQ = [("lifecycle section", ["比赛生命周期", "Match lifecycle", "LIFECYCLE"]),
       ("time basis", ["time basis", "current_time_basis"]),
       ("primary + reason", ["主推预测", "Primary prediction", "reason_for_role"]),
       ("latest recap", ["最新复盘", "Latest recap"]),
       ("secondary", ["次推预测", "Secondary"]),
       ("next upcoming", ["下一场", "Next upcoming"]),
       ("pending recap", ["待复盘", "Finished pending recap"]),
       ("archive/demo excluded", ["排除", "Excluded", "excluded_archive"]),
       ("blocked", ["阻塞项", "Blocked", "blocked_items"]),
       ("next action", ["下一步", "Next action"]),
       ("send HOLD", ["HOLD"])]


def scan(src): return ["missing: %s" % l for l, ms in REQ if not any(m in src for m in ms)]


def selftest():
    full = " ".join(m for _, ms in REQ for m in ms[:1])
    checks = [("full passes", scan(full) == []),
              ("missing primary caught", any("primary" in x for x in scan(full.replace("主推预测", "").replace("Primary prediction", "").replace("reason_for_role", "")))),
              ("missing HOLD caught", any("send HOLD" in x for x in scan(full.replace("HOLD", ""))))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    if "--selftest" in sys.argv: return selftest()
    fails = scan(PAGE.read_text(encoding="utf-8"))
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5B INTERNAL DAILY LIFECYCLE TRACE FAIL — %d" % len(fails)); return 1
    print("P5B INTERNAL DAILY LIFECYCLE TRACE PASS (primary+why · recap · secondary · next · pending · excluded · blocked · action · HOLD)"); return 0


if __name__ == "__main__": sys.exit(main())
