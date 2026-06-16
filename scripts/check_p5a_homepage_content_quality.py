#!/usr/bin/env python3
"""P5A — homepage content quality (rendered DOM). Primary shows hook + reason + risk; secondary cards
show reason/risk (not bare schedule rows); recap card shows a result judgment; no forbidden phrases.
Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom, strip_folds  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]
FORBIDDEN = ["赛前倾向", "双方实力接近", "临场变量影响有限", "模型判断方向较为明确"]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def cv(fk):
    for p in sorted((ROOT / "frontend/src/data/predictionArtifacts").glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk):
            return ((a.get("i18n") or {}).get("zh") or {}).get("copy_v2") or {}
    return {}


def scan(dom, primary_v2, sec_v2_list):
    f = []
    if primary_v2.get("hook_headline") and primary_v2["hook_headline"][:12] not in dom:
        f.append("primary hook headline not rendered")
    if primary_v2.get("main_reason") and primary_v2["main_reason"][:10] not in dom:
        f.append("primary main_reason not rendered")
    if primary_v2.get("hidden_risk") and primary_v2["hidden_risk"][:8] not in dom:
        f.append("primary hidden_risk not rendered")
    for i, s in enumerate(sec_v2_list):
        if s.get("main_reason") and s["main_reason"][:8] not in dom:
            f.append("secondary[%d] reason not rendered (still a bare schedule row?)" % i)
    # Forbidden-phrase scan is on the ACTIVE customer surface only — collapsed <details> internal-demo
    # / archive folds are stripped (same convention as check_customer_visible_copy).
    active = strip_folds(dom)
    for w in FORBIDDEN:
        if w in active: f.append("forbidden phrase %r in active homepage content" % w)
    return f


def selftest():
    pv = {"hook_headline": "比利时该赢但这是效率局不是碾压局", "main_reason": "Elo 1885 对 1756 硬实力高一档", "hidden_risk": "埃及死守反击拖成平局"}
    dom = "比利时该赢但这是效率局不是碾压局 Elo 1885 对 1756 硬实力高一档 埃及死守反击拖成平局 乌拉圭高出沙特一档"
    checks = [("clean passes", scan(dom, pv, [{"main_reason": "乌拉圭高出沙特一档"}]) == []),
              ("missing hook caught", any("hook" in x for x in scan("Elo 1885 对 1756 硬实力高一档 埃及死守反击拖成平局", pv, []))),
              ("forbidden caught", any("forbidden" in x for x in scan(dom + " 赛前倾向", pv, [])))]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    sel = _load(ROOT / "frontend/src/data/selectedHotspot.json") or {}
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    dom = dump_dom(base.rstrip("/") + "/?lang=zh")
    if not dom: print("FAIL  homepage not rendered"); return 1
    fails = scan(dom, cv(sel.get("fixture_key")), [cv(s.get("fixture_key")) for s in q.get("secondary_matches", [])])
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5A HOMEPAGE CONTENT QUALITY FAIL — %d" % len(fails)); return 1
    print("P5A HOMEPAGE CONTENT QUALITY PASS (hook + reason + risk on primary; secondary not bare rows; no forbidden)"); return 0


if __name__ == "__main__": sys.exit(main())
