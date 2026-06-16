#!/usr/bin/env python3
"""P5B — homepage lifecycle rendering (DOM). The rendered homepage primary == lifecycle primary teams;
rendered recap == lifecycle latest_recap teams. Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def teams(m): return [t.strip() for t in (m or "").split(" vs ")] if m else []


def scan(dom, lc):
    f = []
    p = lc.get("primary_prediction")
    if p:
        for t in teams(p["match"]):
            if t and t not in dom: f.append("primary team %r not rendered" % t)
    lr = lc.get("latest_recap")
    if lr:
        for t in teams(lr["match"]):
            if t and t not in dom: f.append("latest_recap team %r not rendered" % t)
    return f


def selftest():
    lc = {"primary_prediction": {"match": "Belgium vs Egypt"}, "latest_recap": {"match": "Brazil vs Morocco"}}
    checks = [("clean passes", scan("Belgium vs Egypt Brazil vs Morocco", lc) == []),
              ("missing primary caught", any("primary" in x for x in scan("Brazil vs Morocco", lc)))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    lc = _load(ROOT / "frontend/src/data/homepageLifecycle.json") or {}
    dom = dump_dom(base.rstrip("/") + "/?lang=zh")
    if not dom: print("FAIL  homepage not rendered"); return 1
    fails = scan(dom, lc)
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5B LIFECYCLE RENDERING FAIL — %d" % len(fails)); return 1
    print("P5B LIFECYCLE RENDERING PASS (rendered primary + latest_recap match the lifecycle artifact)"); return 0


if __name__ == "__main__": sys.exit(main())
