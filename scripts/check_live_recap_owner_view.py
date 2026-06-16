#!/usr/bin/env python3
"""P4R++ owner-view — live /recap shows observation/full recap copy, labelled, no fake event.
Usage: --base-url URL | --selftest"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]
FAKE = re.compile(r"第\s*\d{1,3}\s*分钟.*(进球|破门|红牌|点球)")


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _obs(fk):
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a and (a.get("id") == fk or a.get("fixture_key") == fk): return a
    return None


def scan(dom, obs):
    f = []
    zh = (obs.get("i18n") or {}).get("zh") or {}
    if zh.get("assessment", "")[:8] and zh["assessment"][:8] not in dom: f.append("judgment not rendered")
    if zh.get("deviation", "")[:6] and zh["deviation"][:6] not in dom: f.append("deviation not rendered")
    if not any(m in dom for m in ("分享", "复制")): f.append("share not rendered")
    if obs.get("recap_ready") is False and not any(m in dom for m in ("赛后观察", "赛后校准", "完整复盘确认后开放")): f.append("observation not labelled")
    if FAKE.search(dom): f.append("fabricated event rendered")
    return f


def selftest():
    obs = {"recap_ready": False, "i18n": {"zh": {"assessment": "结果判断：比分区间命中", "deviation": "偏差原因：控制力不足"}}}
    dom = "昨日主推回执 结果判断：比分区间命中 偏差原因：控制力不足 赛后观察 复制观察链接"
    checks = [("clean passes", scan(dom, obs) == []),
              ("fake event caught", any("fabricated" in x for x in scan(dom + " 第 23 分钟 进球", obs))),
              ("unlabelled caught", any("not labelled" in x for x in scan("结果判断：比分区间命中 偏差原因：控制力不足 复制", obs)))]
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
        fk = str(rq.get("fixture_key")); obs = _obs(fk)
        if not obs: continue
        dom = dump_dom(base.rstrip("/") + "/recap/%s?lang=zh" % fk)
        if not dom: fails.append("/recap/%s not rendered" % fk); continue
        n += 1; fails += ["[%s] %s" % (fk, x) for x in scan(dom, obs)]
    if n == 0: print("LIVE RECAP OWNER VIEW PASS (no observation pages to verify)"); return 0
    for x in fails: print("FAIL  %s" % x)
    if fails: print("LIVE RECAP OWNER VIEW FAIL — %d" % len(fails)); return 1
    print("LIVE RECAP OWNER VIEW PASS (%d page: judgment + deviation + share + observation labelled; no fake event)" % n); return 0


if __name__ == "__main__": sys.exit(main())
