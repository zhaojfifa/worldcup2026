#!/usr/bin/env python3
"""P4R++ owner-view — live /predict pages show reviewed LLM copy (headline+score+risk+share) for the
queued matches. Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _art(fk):
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk): return a
    return None


def scan(dom, art):
    f = []
    lean = (art.get("llm_judgment") or {}).get("main_lean") or ""
    score = (art.get("model_fields") or {}).get("recommended_score")
    if lean and lean[:14] not in dom and "REVIEW_REQUIRED" not in dom: f.append("reviewed copy not rendered")
    if score and score not in dom: f.append("score %r not rendered" % score)
    if not any(m in dom for m in ("冷门风险", "Upset")): f.append("risk not rendered")
    if not any(m in dom for m in ("分享", "复制", "Share")): f.append("share not rendered")
    return f


def selftest():
    art = {"llm_judgment": {"main_lean": "赛前倾向乌拉圭，沙特需压低节奏才有机会"}, "model_fields": {"recommended_score": "0-1"}}
    dom = "赛前倾向乌拉圭，沙特需压低节奏才有机会 0-1 冷门风险 中 复制分享文案"
    checks = [("clean passes", scan(dom, art) == []),
              ("missing copy caught", any("reviewed copy" in x for x in scan("0-1 冷门风险 分享", art))),
              ("missing score caught", any("score" in x for x in scan("赛前倾向乌拉圭，沙特需压低节奏才有机会 冷门风险 分享", art)))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    keys = [(q.get("primary_hotspot") or {}).get("fixture_key")] + [s.get("fixture_key") for s in q.get("secondary_matches", [])]
    fails, n = [], 0
    for fk in [str(k) for k in keys if k]:
        art = _art(fk)
        if not art: continue
        dom = dump_dom(base.rstrip("/") + "/predict/%s?lang=zh" % fk)
        if not dom: fails.append("/predict/%s not rendered" % fk); continue
        n += 1; fails += ["[%s] %s" % (fk, x) for x in scan(dom, art)]
    if n == 0: print("FAIL  no predict pages"); return 1
    for x in fails: print("FAIL  %s" % x)
    if fails: print("LIVE PREDICT OWNER VIEW FAIL — %d" % len(fails)); return 1
    print("LIVE PREDICT OWNER VIEW PASS (%d pages: reviewed copy + score + risk + share)" % n); return 0


if __name__ == "__main__": sys.exit(main())
