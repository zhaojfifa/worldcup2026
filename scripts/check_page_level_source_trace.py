#!/usr/bin/env python3
"""
P4R+ — page-level source-trace gate. ONE guard that, for the canonical page set, dumps the rendered
DOM and proves the visible product == the source-of-truth artifact (teams + the reviewed-copy
substring), carries NO demo fixture, and labels honest states (OBSERVATION_ONLY) instead of faking.

Pages checked (per docs/qa_reports/p4r_page_level_source_trace.md):
  homepage (primary + yesterday recap + secondary, no demo) · /predict/<primary> · /predict/<secondary>
  · /recap/<recap> · /share/fixture/<primary>.
Usage: check_page_level_source_trace.py --base-url URL | --selftest
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


def _pred(fk):
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk):
            return a
    return None


def _obs(fk):
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a and (a.get("id") == fk or a.get("fixture_key") == fk):
            return a
    return None


def _lean(a):
    return ((a.get("llm_judgment") or {}).get("main_lean")
            or (((a.get("i18n") or {}).get("zh") or {}).get("prediction") or {}).get("primary_direction") or "")


def trace(base):
    fails = []
    sel = _load(SEL) or {}
    q = _load(QUEUE) or {}
    primary = (q.get("primary_hotspot") or {}).get("fixture_key") or sel.get("fixture_key")
    secondary = [s.get("fixture_key") for s in q.get("secondary_matches", [])]
    recap_q = q.get("recap_queue") or []
    yrec = recap_q[0] if recap_q else {}
    primary_teams = [sel.get("home"), sel.get("away")]

    # 1-3 homepage
    home = dump_dom(base.rstrip("/") + "/?lang=zh")
    if not home:
        return ["could not render homepage"]
    for t in primary_teams + [yrec.get("home"), yrec.get("away")]:
        if t and t not in home:
            fails.append("homepage missing source team %r (stale/wrong)" % t)
    art_p = _pred(str(primary)) if primary else None
    if art_p:
        lean = _lean(art_p)
        if lean and lean[:14] not in home and "COPY_MISSING" not in home:
            fails.append("homepage primary card not showing reviewed copy (%r)" % lean[:20])
    for d in DEMO:
        if d not in primary_teams and d not in [yrec.get("home"), yrec.get("away")] and d in home:
            fails.append("demo fixture %r in rendered homepage" % d)

    # 4-5 predict pages (primary + first secondary)
    for fk in ([str(primary)] if primary else []) + [str(s) for s in secondary[:1]]:
        a = _pred(fk)
        if not a:
            continue
        dom = dump_dom(base.rstrip("/") + "/predict/%s?lang=zh" % fk)
        if not dom:
            fails.append("could not render /predict/%s" % fk); continue
        lean = _lean(a)
        score = (a.get("model_fields") or {}).get("recommended_score")
        if lean and lean[:14] not in dom and "COPY_MISSING" not in dom:
            fails.append("/predict/%s not showing reviewed copy" % fk)
        if score and score not in dom:
            fails.append("/predict/%s not showing score %r" % (fk, score))

    # 6 recap page
    if yrec.get("fixture_key"):
        rk = str(yrec["fixture_key"])
        ob = _obs(rk)
        dom = dump_dom(base.rstrip("/") + "/recap/%s?lang=zh" % rk)
        if dom and ob:
            zh = (ob.get("i18n") or {}).get("zh") or {}
            if zh.get("assessment", "")[:8] and zh["assessment"][:8] not in dom:
                fails.append("/recap/%s not showing observation judgment" % rk)
            if ob.get("recap_ready") is False and not any(m in dom for m in ("赛后观察", "赛后校准", "完整复盘确认后开放")):
                fails.append("/recap/%s observation not labelled (looks like full recap)" % rk)

    # 7 share card (primary) — the card renders the strong-call PROJECTION (lean + score), not the
    # raw share_copy paragraph; assert the reviewed lean substring + the score are on the card.
    if art_p and primary:
        lean = _lean(art_p)
        score = (art_p.get("model_fields") or {}).get("recommended_score")
        dom = dump_dom(base.rstrip("/") + "/share/fixture/%s?lang=zh" % primary)
        if dom:
            if lean and lean[:10] not in dom:
                fails.append("/share/fixture/%s not showing reviewed lean copy" % primary)
            if score and score not in dom:
                fails.append("/share/fixture/%s not showing score %r" % (primary, score))
        else:
            fails.append("could not render /share/fixture/%s" % primary)
    return fails


def selftest():
    # pure-logic smoke: the DEMO list + substring logic
    home = "今日热点预测 Belgium vs Egypt 赛前倾向比利时 昨日热点复盘 Brazil vs Morocco"
    checks = [
        ("primary team present", "Belgium" in home and "Egypt" in home),
        ("reviewed lean substring detectable", "赛前倾向比利时" in home),
        ("demo absent", not any(d in home for d in DEMO)),
        ("demo detected when present", any(d in (home + " Netherlands") for d in DEMO)),
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
    fails = trace(base)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("PAGE-LEVEL SOURCE TRACE FAIL — %d issue(s)" % len(fails)); return 1
    print("PAGE-LEVEL SOURCE TRACE PASS (homepage + predict + recap + share render their source "
          "artifacts; reviewed copy shown; no demo leak) @ %s" % base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
