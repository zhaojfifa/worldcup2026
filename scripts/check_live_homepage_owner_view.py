#!/usr/bin/env python3
"""P4R++ owner-view — live homepage. Active primary + yesterday recap rendered, reviewed lean
projected, no demo PAIRING in critical sections. Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom, demo_pair_leak  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def lean():
    sel = _load(ROOT / "frontend/src/data/selectedHotspot.json") or {}
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and a.get("fixture_key") == sel.get("fixture_key"):
            return (a.get("llm_judgment") or {}).get("main_lean") or ""
    return ""


def scan(dom, primary, yest, ln):
    f = []
    for t in primary + yest:
        if t and t not in dom: f.append("homepage missing %r" % t)
    if ln and ln[:14] not in dom and "REVIEW_REQUIRED" not in dom: f.append("reviewed lean not projected")
    leak = demo_pair_leak(dom)
    if leak: f.append("demo pairing %r in homepage" % leak)
    return f


def selftest():
    dom = "今日热点预测 Belgium vs Egypt 赛前倾向比利时，但埃及有能力压低比分 昨日热点复盘 Brazil vs Morocco 德国 vs Japan"
    checks = [("clean passes", scan(dom, ["Belgium", "Egypt"], ["Brazil", "Morocco"], "赛前倾向比利时，但埃及有能力压低比分") == []),
              ("2022 archive not flagged", not any("demo pairing" in x for x in scan(dom, ["Belgium", "Egypt"], ["Brazil", "Morocco"], ""))),
              ("demo pairing flagged", any("demo pairing" in x for x in scan(dom + " 荷兰 vs Japan", ["Belgium", "Egypt"], ["Brazil", "Morocco"], "")))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    sel = _load(ROOT / "frontend/src/data/selectedHotspot.json") or {}
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    yq = (q.get("recap_queue") or [{}])[0]
    dom = dump_dom(base.rstrip("/") + "/?lang=zh")
    if not dom: print("FAIL  homepage not rendered"); return 1
    fails = scan(dom, [sel.get("home"), sel.get("away")], [yq.get("home"), yq.get("away")], lean())
    for x in fails: print("FAIL  %s" % x)
    if fails: print("LIVE HOMEPAGE OWNER VIEW FAIL — %d" % len(fails)); return 1
    print("LIVE HOMEPAGE OWNER VIEW PASS (active primary + yesterday recap + reviewed lean; no demo)"); return 0


if __name__ == "__main__": sys.exit(main())
