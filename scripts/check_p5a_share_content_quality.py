#!/usr/bin/env python3
"""P5A — share-card content quality (rendered DOM). Prediction share card shows the hook/lean + score
+ a reason; recap share card shows the result + teams; no forbidden phrases. Usage: --base-url | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]
FORBIDDEN = ["赛前倾向", "双方实力接近", "临场变量影响有限"]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def art(fk):
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk): return a
    return None


def scan_pred(dom, a):
    f = []
    lean = (a.get("llm_judgment") or {}).get("main_lean") or ""
    score = (a.get("model_fields") or {}).get("recommended_score")
    if lean and lean[:10] not in dom: f.append("share: lean not rendered")
    if score and score not in dom: f.append("share: score %r not rendered" % score)
    if not any(t in dom for t in (a.get("home", ""), a.get("away", ""))): f.append("share: teams not rendered")
    for w in FORBIDDEN:
        if w in dom: f.append("share: forbidden %r" % w)
    return f


def selftest():
    a = {"llm_judgment": {"main_lean": "俅哥主看比利时拿下XYZ"}, "model_fields": {"recommended_score": "1-0"}, "home": "Belgium", "away": "Egypt"}
    dom = "俅哥主看比利时拿下XYZ 1-0 Belgium Egypt"
    checks = [("clean passes", scan_pred(dom, a) == []),
              ("missing score caught", any("score" in x for x in scan_pred("俅哥主看比利时拿下XYZ Belgium Egypt", a))),
              ("forbidden caught", any("forbidden" in x for x in scan_pred(dom + " 赛前倾向", a)))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    ar = sys.argv[1:]
    if "--selftest" in ar: return selftest()
    base = ar[ar.index("--base-url") + 1] if "--base-url" in ar else "https://worldcup2026-izid.onrender.com"
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    fk = str((q.get("primary_hotspot") or {}).get("fixture_key"))
    a = art(fk); fails = []
    if a:
        dom = dump_dom(base.rstrip("/") + "/share/fixture/%s?lang=zh" % fk)
        if not dom: fails.append("share card not rendered")
        else: fails += scan_pred(dom, a)
    # recap share card renders teams + result
    rq = (q.get("recap_queue") or [{}])[0]
    if rq.get("fixture_key"):
        rdom = dump_dom(base.rstrip("/") + "/share/recap/%s?lang=zh" % rq["fixture_key"])
        if rdom and not any(t in rdom for t in (rq.get("home", ""), rq.get("away", ""))):
            fails.append("recap share card: teams not rendered")
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5A SHARE CONTENT QUALITY FAIL — %d" % len(fails)); return 1
    print("P5A SHARE CONTENT QUALITY PASS (prediction share: lean+score+teams; recap share: teams; no forbidden)"); return 0


if __name__ == "__main__": sys.exit(main())
