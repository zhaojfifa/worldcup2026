#!/usr/bin/env python3
"""
P1 — operator-console guard. Fails if /internal/daily (DailyStatusPage.tsx) lacks the command-console
surfaces the operator needs:
  - primary hotspot · secondary queue · prediction readiness · content/LLM grounding readiness ·
    recap readiness · SLA status · next operator action · send HOLD.
Source-scan of frontend/src/pages/DailyStatusPage.tsx (the bundled, build-time operator surface).
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "frontend" / "src" / "pages" / "DailyStatusPage.tsx"

# (label, list-of-acceptable-markers) — any marker present satisfies the requirement.
REQUIRED = [
    ("primary hotspot", ["Primary hotspot", "主热点", "Selected hotspot", "今日选定"]),
    ("secondary queue", ["Secondary matches", "次要赛事", "secondary_matches"]),
    ("prediction readiness", ["Prediction artifact", "预测产物", "Artifact ready", "content_state"]),
    ("content/LLM grounding readiness", ["Content grounding", "内容接地", "content_chain", "Reviewed JSON"]),
    ("recap readiness", ["Recap SLA state", "复盘状态", "Recap queue", "复盘队列", "Observation / recap"]),
    ("SLA status", ["Update SLA state", "更新就绪", "Recap SLA state", "Drift status"]),
    ("next operator action", ["Next operator action", "下一步运营动作"]),
    ("send HOLD", ["HOLD"]),
]


def scan(src):
    fails = []
    for label, markers in REQUIRED:
        if not any(m in src for m in markers):
            fails.append("/internal/daily console missing: %s (none of %r)" % (label, markers))
    return fails


def selftest():
    full = " ".join(m for _, ms in REQUIRED for m in ms[:1])
    checks = [
        ("full console passes", scan(full) == []),
        ("missing next-action caught", any("next operator action" in x for x in scan(full.replace("Primary hotspot", "Primary hotspot").replace("Next operator action", "")))),
        ("missing send-hold caught", any("send HOLD" in x for x in scan(full.replace("HOLD", "")))),
        ("missing secondary caught", any("secondary queue" in x for x in scan(full.replace("Secondary matches", "")))),
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
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("OPERATOR CONSOLE FAIL — %d issue(s)" % len(fails)); return 1
    print("OPERATOR CONSOLE PASS (primary + secondary queue · prediction/LLM/recap readiness · SLA · "
          "next action · send HOLD)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
