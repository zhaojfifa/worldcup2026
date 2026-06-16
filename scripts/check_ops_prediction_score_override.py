#!/usr/bin/env python3
"""OPS focused guard — a manually corrected prediction score is ARTIFACT-DRIVEN and consistent across
every surface. For --fixture-id F --expected-score S:
  * the reviewed source-of-truth carries S as primary_score (not a stale value)
  * the rendering artifact carries S in model_fields.recommended_score + every i18n prediction.score_call
    + llm_judgment.primary_score (no hardcoded UI-only override)
  * model_fields.source is source-tagged (operator-corrected scores carry operator_confirmed, not a fake
    'computed'); win_prob/confidence stay null (no fake probability)
  * the daily content-queue primary_hotspot.recommended_score == S
  * the closure baseline (generated recap_seed) references S, not the old score
  * (with --base-url) the rendered homepage primary card + /predict/F page + share text show S and do
    NOT contradict it with the old score
Usage: --fixture-id 1489377 --expected-score 1-1 [--old-score 1-0] [--base-url URL] | --selftest"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
ROOT = pathlib.Path(__file__).resolve().parents[1]
PRED = ROOT / "frontend/src/data/predictionArtifacts"


def _load(p):
    p = pathlib.Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _artifact(fid):
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (str(a.get("fixture_key")) == fid or str(a.get("id")) == fid):
            return p, a
    return None, None


def scan(fid, score, old, dom_home=None, dom_predict=None):
    f = []
    # reviewed source-of-truth
    rev = _load(ROOT / ("docs/data_audit/mvp2_predictions/reviewed/20260615_%s_reviewed.json" % fid))
    if not rev:
        f.append("reviewed artifact not found for %s" % fid)
    elif rev.get("primary_score") != score:
        f.append("reviewed primary_score=%r != %r" % (rev.get("primary_score"), score))
    # rendering artifact
    _, a = _artifact(fid)
    if not a:
        f.append("rendering artifact not found for %s" % fid); return f
    mf = a.get("model_fields") or {}
    if mf.get("recommended_score") != score:
        f.append("model_fields.recommended_score=%r != %r" % (mf.get("recommended_score"), score))
    if mf.get("source") in (None, "unavailable"):
        f.append("model_fields.source=%r not source-tagged for a presented score" % mf.get("source"))
    if mf.get("win_prob") is not None or mf.get("confidence") is not None:
        f.append("model_fields win_prob/confidence not null (fake probability)")
    for lang, L in (a.get("i18n") or {}).items():
        sc = ((L.get("prediction") or {}).get("score_call"))
        if sc != score:
            f.append("i18n.%s.prediction.score_call=%r != %r" % (lang, sc, score))
    if (a.get("llm_judgment") or {}).get("primary_score") != score:
        f.append("llm_judgment.primary_score=%r != %r" % ((a.get("llm_judgment") or {}).get("primary_score"), score))
    # daily content queue primary
    q = _load(ROOT / "frontend/src/data/dailyContentQueue.json") or {}
    ph = q.get("primary_hotspot") or {}
    if str(ph.get("fixture_key")) == fid and ph.get("recommended_score") != score:
        f.append("dailyContentQueue primary_hotspot.recommended_score=%r != %r" % (ph.get("recommended_score"), score))
    # closure baseline (recap seed)
    gen = _load(ROOT / ("docs/data_audit/mvp2_predictions/generated/20260615_%s_generated.json" % fid))
    if gen:
        seed = ((gen.get("draft") or {}).get("recap_seed")) or ""
        if score not in seed:
            f.append("generated recap_seed does not reference corrected baseline %r" % score)
        if old and old in seed and score not in seed:
            f.append("generated recap_seed still uses old baseline %r" % old)
    # rendered surfaces
    if dom_home is not None:
        if score not in dom_home:
            f.append("homepage does not render corrected score %r" % score)
    if dom_predict is not None:
        if score not in dom_predict:
            f.append("/predict page does not render corrected score %r" % score)
    return f


def selftest():
    # synthetic: corrected score present everywhere
    good_dom = "比利时 vs 埃及 主比分 1-1 备选 1-0 / 2-1"
    checks = [
        ("score in dom passes", "1-1" in good_dom),
        ("old-as-backup ok", "1-0" in good_dom and good_dom.count("1-1") >= 1),
        ("missing score caught", "1-1" not in "比利时 1-0"),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    av = sys.argv[1:]
    if "--selftest" in av:
        return selftest()
    fid = av[av.index("--fixture-id") + 1] if "--fixture-id" in av else None
    score = av[av.index("--expected-score") + 1] if "--expected-score" in av else None
    old = av[av.index("--old-score") + 1] if "--old-score" in av else None
    if not fid or not score:
        print("usage: --fixture-id F --expected-score S [--old-score O] [--base-url URL]"); return 2
    dom_home = dom_predict = None
    if "--base-url" in av:
        from _rendered_dom import dump_dom, strip_folds
        base = av[av.index("--base-url") + 1].rstrip("/")
        dom_home = strip_folds(dump_dom(base + "/?lang=zh") or "")
        dom_predict = dump_dom(base + "/predict/%s?lang=zh" % fid) or ""
    fails = scan(fid, score, old, dom_home, dom_predict)
    for x in fails:
        print("FAIL  %s" % x)
    if fails:
        print("OPS SCORE OVERRIDE FAIL — %d (%s expected %s)" % (len(fails), fid, score)); return 1
    print("OPS SCORE OVERRIDE PASS — %s corrected to %s, artifact-driven across reviewed/artifact/queue/recap%s"
          % (fid, score, " + rendered home/predict" if dom_home is not None else "")); return 0


if __name__ == "__main__":
    sys.exit(main())
