#!/usr/bin/env python3
"""P5A — copy-contract guard (JSON). Each queued prediction artifact must carry copy_version=p5a_v2 +
a complete zh copy_v2 (7 non-empty fields), no FORBIDDEN generic phrases anywhere in zh; the observation
recap carries recap v2 (result_judgment + what_was_right/wrong + model_correction). Usage: [--selftest]"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend/src/data/dailyContentQueue.json"
PRED = ROOT / "frontend/src/data/predictionArtifacts"
V2 = ["hook_headline", "main_reason", "pressure_point", "hidden_risk", "tactical_watch", "confidence_language", "group_hook"]
FORBIDDEN = ["模型判断方向较为明确", "双方存在差距但并非一边倒", "临场变量影响有限",
             "双方实力接近，结果高度依赖临场阵容", "赛前倾向", "值得继续跟踪", "风险中而已"]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _art(fk):
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk): return a
    return None


def scan_pred(name, a):
    f = []
    if a.get("copy_version") != "p5a_v2": f.append("%s: copy_version != p5a_v2" % name)
    cv = ((a.get("i18n") or {}).get("zh") or {}).get("copy_v2") or {}
    for k in V2:
        if not (cv.get(k) or "").strip(): f.append("%s: copy_v2.%s empty" % (name, k))
    blob = json.dumps((a.get("i18n") or {}).get("zh") or {}, ensure_ascii=False)
    for w in FORBIDDEN:
        if w in blob: f.append("%s: forbidden phrase %r" % (name, w))
    return f


def scan_obs(name, o):
    f = []
    zh = (o.get("i18n") or {}).get("zh") or {}
    for k in ("result_judgment", "what_was_right", "what_was_wrong", "model_correction"):
        if not (zh.get(k) or "").strip(): f.append("%s: recap v2 %s empty" % (name, k))
    return f


def selftest():
    good = {"copy_version": "p5a_v2", "i18n": {"zh": {"copy_v2": {k: "x" for k in V2}}}}
    bad = {"copy_version": "p5a_v2", "i18n": {"zh": {"copy_v2": {k: "x" for k in V2}, "prediction": {"primary_direction": "赛前倾向比利时"}}}}
    obs = {"i18n": {"zh": {"result_judgment": "PARTIAL", "what_was_right": "a", "what_was_wrong": "b", "model_correction": "c"}}}
    checks = [("good pred passes", scan_pred("g", good) == []),
              ("forbidden caught", any("forbidden" in x for x in scan_pred("b", bad))),
              ("missing v2 caught", any("copy_v2" in x for x in scan_pred("m", {"copy_version": "p5a_v2", "i18n": {"zh": {"copy_v2": {}}}}))),
              ("good obs passes", scan_obs("o", obs) == [])]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    if "--selftest" in sys.argv: return selftest()
    q = _load(QUEUE) or {}
    keys = [(q.get("primary_hotspot") or {}).get("fixture_key")] + [s.get("fixture_key") for s in q.get("secondary_matches", [])]
    fails, n = [], 0
    for fk in [str(k) for k in keys if k]:
        a = _art(fk)
        if not a: fails.append("%s: no artifact" % fk); continue
        n += 1; fails += scan_pred("%s vs %s" % (a.get("home"), a.get("away")), a)
    for p in sorted(PRED.glob("*.json")):
        o = _load(p)
        if o and "recap_ready" in o: fails += scan_obs(p.name, o)
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5A COPY CONTRACT FAIL — %d" % len(fails)); return 1
    print("P5A COPY CONTRACT PASS (%d predictions p5a_v2 + copy_v2 complete · recap v2 · no forbidden)" % n); return 0


if __name__ == "__main__": sys.exit(main())
