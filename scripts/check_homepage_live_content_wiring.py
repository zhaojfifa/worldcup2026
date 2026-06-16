#!/usr/bin/env python3
"""
P4R Phase 4 — homepage live-content-wiring guard. Inspects the rendered homepage DOM and proves the
product loop renders REAL artifacts (not labels-only, not demo content).

Fails if:
  - the homepage primary (selectedHotspot teams) is not rendered;
  - the reviewed prediction copy (primary main_lean) is not projected onto the homepage card;
  - the yesterday recap (recap_queue[0] teams) is not rendered;
  - a demo/static fixture (Qatar/Ecuador/Netherlands/Japan) appears in the rendered homepage;
  - the loop section labels (今日热点预测 / 昨日热点复盘) are present but their teams are absent
    (label-without-content).
Usage: check_homepage_live_content_wiring.py [--base-url URL] | --selftest
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
DEMO = ["Qatar", "Ecuador", "Netherlands", "Japan"]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _primary_lean(fk):
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk):
            return ((a.get("llm_judgment") or {}).get("main_lean")
                    or (((a.get("i18n") or {}).get("zh") or {}).get("prediction") or {}).get("primary_direction") or "")
    return ""


def scan(dom, primary_teams, lean, yesterday_teams):
    fails = []
    if "今日热点预测" in dom or "HOTSPOT PREDICTION" in dom:
        for t in primary_teams:
            if t and t not in dom:
                fails.append("今日热点预测 label present but primary team %r not rendered (label-without-content)" % t)
    else:
        fails.append("homepage missing 今日热点预测 section")
    if lean and lean[:14] not in dom:
        fails.append("reviewed primary copy (main_lean) not projected on homepage: %r" % lean[:24])
    if "昨日热点复盘" in dom or "HOTSPOT RECAP" in dom:
        for t in yesterday_teams:
            if t and t not in dom:
                fails.append("昨日热点复盘 label present but recap team %r not rendered" % t)
    else:
        fails.append("homepage missing 昨日热点复盘 section")
    for d in DEMO:
        if d not in primary_teams and d not in yesterday_teams and d in dom:
            fails.append("demo/static fixture %r in rendered homepage" % d)
    return fails


def selftest():
    dom_ok = "今日热点预测 Belgium vs Egypt 赛前倾向比利时，但埃及有能力压低比分 昨日热点复盘 Brazil vs Morocco"
    checks = [
        ("wired homepage passes", scan(dom_ok, ["Belgium", "Egypt"], "赛前倾向比利时，但埃及有能力压低比分", ["Brazil", "Morocco"]) == []),
        ("missing primary team caught", any("label-without-content" in x for x in scan("今日热点预测 昨日热点复盘 Brazil vs Morocco 赛前倾向比利时，但埃及有能力压低比分", ["Belgium", "Egypt"], "赛前倾向比利时，但埃及有能力压低比分", ["Brazil", "Morocco"]))),
        ("missing lean caught", any("main_lean" in x for x in scan("今日热点预测 Belgium vs Egypt 昨日热点复盘 Brazil vs Morocco", ["Belgium", "Egypt"], "赛前倾向比利时，但埃及有能力压低比分", ["Brazil", "Morocco"]))),
        ("demo leak caught", any("demo/static" in x for x in scan(dom_ok + " Netherlands vs Japan", ["Belgium", "Egypt"], "赛前倾向比利时，但埃及有能力压低比分", ["Brazil", "Morocco"]))),
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
    base = argv[argv.index("--base-url") + 1] if "--base-url" in argv else "https://worldcup2026-izid.onrender.com"
    sel = _load(SEL) or {}
    q = _load(QUEUE) or {}
    primary_teams = [sel.get("home"), sel.get("away")]
    lean = _primary_lean(sel.get("fixture_key"))
    recap_q = q.get("recap_queue") or []
    yrec = recap_q[0] if recap_q else {}
    yesterday_teams = [yrec.get("home"), yrec.get("away")]
    dom = dump_dom(base.rstrip("/") + "/?lang=zh")
    if not dom:
        print("FAIL  could not render homepage DOM (%s)" % base); return 1
    fails = scan(dom, primary_teams, lean, yesterday_teams)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("HOMEPAGE LIVE CONTENT WIRING FAIL — %d issue(s)" % len(fails)); return 1
    print("HOMEPAGE LIVE CONTENT WIRING PASS (primary + reviewed copy + yesterday recap rendered; no demo)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
