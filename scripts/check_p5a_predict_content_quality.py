#!/usr/bin/env python3
"""P5A — /predict content quality (rendered DOM). Each queued match's /predict must render hook +
score + main_reason + pressure_point + hidden_risk + tactical_watch + share; no forbidden phrases.
Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]
FORBIDDEN = ["赛前倾向", "双方实力接近", "临场变量影响有限", "模型判断方向较为明确"]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def art(fk):
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk): return a
    return None


def scan(dom, a):
    f = []
    cv = ((a.get("i18n") or {}).get("zh") or {}).get("copy_v2") or {}
    score = (a.get("model_fields") or {}).get("recommended_score")
    for k, lbl in (("hook_headline", "hook"), ("main_reason", "reason"), ("pressure_point", "pressure_point"),
                   ("hidden_risk", "hidden_risk"), ("tactical_watch", "tactical_watch")):
        if cv.get(k) and cv[k][:10] not in dom: f.append("%s not rendered" % lbl)
    if score and score not in dom: f.append("score %r not rendered" % score)
    if not any(m in dom for m in ("复制分享文案", "复制情报链", "分享")): f.append("share not rendered")
    for w in FORBIDDEN:
        if w in dom: f.append("forbidden %r" % w)
    return f


def selftest():
    a = {"i18n": {"zh": {"copy_v2": {"hook_headline": "效率局不是碾压局XYZ", "main_reason": "Elo差一档ABC", "pressure_point": "首球时间QQQ", "hidden_risk": "死守反击WWW", "tactical_watch": "最强前场EEE"}}}, "model_fields": {"recommended_score": "1-0"}}
    dom = "效率局不是碾压局XYZ Elo差一档ABC 首球时间QQQ 死守反击WWW 最强前场EEE 1-0 复制分享文案"
    checks = [("clean passes", scan(dom, a) == []),
              ("missing pressure caught", any("pressure_point" in x for x in scan(dom.replace("首球时间QQQ", ""), a))),
              ("forbidden caught", any("forbidden" in x for x in scan(dom + " 赛前倾向", a)))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    ar = sys.argv[1:]
    if "--selftest" in ar: return selftest()
    base = ar[ar.index("--base-url") + 1] if "--base-url" in ar else "https://worldcup2026-izid.onrender.com"
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    keys = [(q.get("primary_hotspot") or {}).get("fixture_key")] + [s.get("fixture_key") for s in q.get("secondary_matches", [])]
    fails, n = [], 0
    for fk in [str(k) for k in keys if k]:
        a = art(fk)
        if not a: continue
        dom = dump_dom(base.rstrip("/") + "/predict/%s?lang=zh" % fk)
        if not dom: fails.append("/predict/%s not rendered" % fk); continue
        n += 1; fails += ["[%s] %s" % (fk, x) for x in scan(dom, a)]
    if n == 0: print("FAIL  no predict pages"); return 1
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5A PREDICT CONTENT QUALITY FAIL — %d" % len(fails)); return 1
    print("P5A PREDICT CONTENT QUALITY PASS (%d pages: hook+score+reason+pressure+risk+watch+share)" % n); return 0


if __name__ == "__main__": sys.exit(main())
