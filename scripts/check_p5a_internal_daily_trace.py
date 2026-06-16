#!/usr/bin/env python3
"""P5A — /internal/daily trace guard (source). DailyStatusPage must surface the copy version + source
trace + send HOLD. Usage: --base-url (optional, source-scan) | --selftest"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "frontend/src/pages/DailyStatusPage.tsx"
REQ = [("copy version", ["文案版本", "Copy version", "copy_version"]),
       ("active content date", ["生效内容日期", "Active content date"]),
       ("prediction copy source", ["预测文案来源", "Prediction copy source", "rendered_copy_source"]),
       ("recap copy source", ["复盘文案来源", "Recap copy source"]),
       ("freshness", ["今日内容是否新鲜", "Daily freshness", "freshness"]),
       ("send HOLD", ["HOLD"])]


def scan(src): return ["missing: %s" % l for l, ms in REQ if not any(m in src for m in ms)]


def selftest():
    full = " ".join(m for _, ms in REQ for m in ms[:1])
    checks = [("full passes", scan(full) == []),
              ("missing copy version caught", any("copy version" in x for x in scan(full.replace("文案版本", "").replace("Copy version", "").replace("copy_version", "")))),
              ("missing HOLD caught", any("send HOLD" in x for x in scan(full.replace("HOLD", ""))))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    if "--selftest" in sys.argv: return selftest()
    fails = scan(PAGE.read_text(encoding="utf-8"))
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5A INTERNAL DAILY TRACE FAIL — %d" % len(fails)); return 1
    print("P5A INTERNAL DAILY TRACE PASS (copy version + active date + copy sources + freshness + HOLD)"); return 0


if __name__ == "__main__": sys.exit(main())
