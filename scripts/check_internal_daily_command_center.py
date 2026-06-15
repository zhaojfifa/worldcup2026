#!/usr/bin/env python3
"""
P2 — /internal/daily command-center guard. The operator must be able to answer
"what is ready, what is blocked, what do I do next?" on one screen.

DailyStatusPage.tsx must render the command center reading dailyOpsState.json, surfacing:
  runtime · today queue · review queue · artifact readiness · T-30 queue · FT observation+recap ·
  share package · day close · next operator action · Send HOLD.
Also: the queues must be VISIBLE (rendered), not just files — the page must import dailyOpsState.json.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "frontend" / "src" / "pages" / "DailyStatusPage.tsx"
STATE = ROOT / "frontend" / "src" / "data" / "dailyOpsState.json"

REQUIRED = [
    ("imports ops state", ["dailyOpsState.json", "opsStateRaw"]),
    ("command center section", ["Daily command center", "每日指挥台", "COMMAND CENTER"]),
    ("runtime", ["Runtime", "运行时", "drift="]),
    ("today queue", ["Today queue", "今日队列"]),
    ("review queue", ["Review queue", "复核队列"]),
    ("artifact readiness", ["Artifact readiness", "产物就绪"]),
    ("t30 queue", ["T-30 queue", "临场队列"]),
    ("ft observation+recap", ["FT observation", "复盘队列"]),
    ("share package", ["Share package", "分享物料队列"]),
    ("day close", ["Day close", "收日"]),
    ("next operator action", ["Next operator action", "下一步"]),
    ("send HOLD", ["HOLD"]),
]


def scan(src):
    fails = []
    for label, markers in REQUIRED:
        if not any(m in src for m in markers):
            fails.append("command center missing: %s (none of %r)" % (label, markers))
    return fails


def selftest():
    full = " ".join(m for _, ms in REQUIRED for m in ms[:1])
    checks = [
        ("full page passes", scan(full) == []),
        ("missing review queue caught", any("review queue" in x for x in scan(full.replace("Review queue", "")))),
        ("missing day close caught", any("day close" in x for x in scan(full.replace("Day close", "")))),
        ("missing send hold caught", any("send HOLD" in x for x in scan(full.replace("HOLD", "")))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if not PAGE.exists():
        print("FAIL  DailyStatusPage.tsx missing"); return 1
    fails = scan(PAGE.read_text(encoding="utf-8"))
    if not STATE.exists():
        fails.append("dailyOpsState.json missing (queues would not be visible)")
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("INTERNAL DAILY COMMAND CENTER FAIL — %d issue(s)" % len(fails)); return 1
    print("INTERNAL DAILY COMMAND CENTER PASS (runtime · queues · readiness · day close · next action · HOLD; "
          "queues visible via dailyOpsState.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
