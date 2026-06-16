#!/usr/bin/env python3
"""
P4D — /internal/daily critical-ops-view guard. The TOP screen must let the operator answer in 10s:
今天是不是新内容 / 昨天推荐有没有复盘 / 哪场命中或偏差为什么 / 哪些文案还需复核 / 今天能不能发 / 下一步该做什么.

DailyStatusPage.tsx must render a Critical ops section reading dailyOpsState (freshness +
recommendation_closure folded in) with: daily freshness · today primary · today secondary · yesterday
closure · hit/miss/pending · copy review · share packages · can-we-send (HOLD) · next action.
Usage: check_critical_ops_view.py | --selftest.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "frontend" / "src" / "pages" / "DailyStatusPage.tsx"
STATE = ROOT / "frontend" / "src" / "data" / "dailyOpsState.json"

REQUIRED = [
    ("critical section", ["Critical ops", "今日关键运营", "CRITICAL"]),
    ("daily freshness", ["今日内容是否新鲜", "Daily freshness", "freshness"]),
    ("today primary", ["今日主推", "Today primary"]),
    ("today secondary", ["今日次级推荐", "Today secondary"]),
    ("yesterday closure", ["昨日推荐闭环", "Yesterday closure", "recommendation_closure"]),
    ("hit/miss/pending", ["命中/偏差/待观察", "Hit·Miss·Pending", "result_status"]),
    ("copy review", ["文案复核", "Copy review"]),
    ("share packages", ["分享物料", "Share packages"]),
    ("can we send", ["今天能不能发", "Can we send"]),
    ("next action", ["下一步运营动作", "Next action", "next_operator_action"]),
    ("send HOLD", ["HOLD"]),
]


def scan(src):
    return ["critical ops view missing: %s (none of %r)" % (label, markers)
            for label, markers in REQUIRED if not any(m in src for m in markers)]


def selftest():
    full = " ".join(m for _, ms in REQUIRED for m in ms[:1])
    checks = [
        ("full passes", scan(full) == []),
        ("missing freshness caught", any("daily freshness" in x for x in scan(full.replace("今日内容是否新鲜", "").replace("Daily freshness", "").replace("freshness", "")))),
        ("missing closure caught", any("yesterday closure" in x for x in scan(full.replace("昨日推荐闭环", "").replace("Yesterday closure", "").replace("recommendation_closure", "")))),
        ("missing send caught", any("can we send" in x for x in scan(full.replace("今天能不能发", "").replace("Can we send", "")))),
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
        fails.append("dailyOpsState.json missing (critical ops would not be visible)")
    else:
        st = json.loads(STATE.read_text(encoding="utf-8"))
        if "freshness" not in st:
            fails.append("dailyOpsState missing freshness block")
        if "recommendation_closure" not in st:
            fails.append("dailyOpsState missing recommendation_closure block")
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("CRITICAL OPS VIEW FAIL — %d issue(s)" % len(fails)); return 1
    print("CRITICAL OPS VIEW PASS (freshness · primary/secondary · yesterday closure · hit/miss · copy "
          "review · share · can-we-send HOLD · next action)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
