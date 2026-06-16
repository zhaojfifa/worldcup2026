#!/usr/bin/env python3
"""P5A — /recap content quality (rendered DOM). Recap shows result_judgment + what_was_right +
what_was_wrong + model_correction + share; OBSERVATION labelled; no fabricated event. Usage: --base-url | --selftest"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]
FAKE = re.compile(r"第\s*\d{1,3}\s*分钟.*(进球|破门|红牌|点球)")


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def obs(fk):
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a and (a.get("id") == fk or a.get("fixture_key") == fk): return a
    return None


def scan(dom, o):
    f = []
    zh = (o.get("i18n") or {}).get("zh") or {}
    for k, lbl in (("result_judgment", "result_judgment"), ("what_was_right", "what_was_right"),
                   ("what_was_wrong", "what_was_wrong"), ("model_correction", "model_correction")):
        if zh.get(k) and zh[k][:8] not in dom: f.append("%s not rendered" % lbl)
    if not any(m in dom for m in ("分享", "复制")): f.append("share not rendered")
    if o.get("recap_ready") is False and not any(m in dom for m in ("赛后观察", "OBSERVATION", "完整复盘确认后开放", "赛后校准")):
        f.append("observation not labelled")
    if FAKE.search(dom): f.append("fabricated event")
    return f


def selftest():
    o = {"recap_ready": False, "i18n": {"zh": {"result_judgment": "部分命中PARTIAL", "what_was_right": "看对比分区间AAA", "what_was_wrong": "看错胜负方向BBB", "model_correction": "下调确定性CCC"}}}
    dom = "赛后观察 部分命中PARTIAL 看对比分区间AAA 看错胜负方向BBB 下调确定性CCC 复制"
    checks = [("clean passes", scan(dom, o) == []),
              ("fake event caught", any("fabricated" in x for x in scan(dom + " 第 23 分钟 进球", o))),
              ("missing wrong caught", any("what_was_wrong" in x for x in scan(dom.replace("看错胜负方向BBB", ""), o)))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    fails, n = [], 0
    for rq in q.get("recap_queue", []):
        fk = str(rq.get("fixture_key")); o = obs(fk)
        if not o: continue
        dom = dump_dom(base.rstrip("/") + "/recap/%s?lang=zh" % fk)
        if not dom: fails.append("/recap/%s not rendered" % fk); continue
        n += 1; fails += ["[%s] %s" % (fk, x) for x in scan(dom, o)]
    if n == 0: print("P5A RECAP CONTENT QUALITY PASS (no observation pages)"); return 0
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5A RECAP CONTENT QUALITY FAIL — %d" % len(fails)); return 1
    print("P5A RECAP CONTENT QUALITY PASS (%d: judgment+right+wrong+correction+share; observation labelled; no fake event)" % n); return 0


if __name__ == "__main__": sys.exit(main())
