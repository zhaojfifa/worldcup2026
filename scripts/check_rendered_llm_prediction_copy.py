#!/usr/bin/env python3
"""
P4R Phase 2 — RENDERED LLM-prediction-copy guard. Inspects the rendered /predict DOM (not the artifact
JSON) and proves the reviewed LLM copy is what renders — or that COPY_MISSING/REVIEW_REQUIRED is shown.

For each queued match with a prediction artifact, dump /predict/<fixture_key> and fail if:
  - the reviewed main_lean (the headline the renderer should show) is NOT in the DOM (reviewed copy not
    rendered) AND no COPY_MISSING/REVIEW_REQUIRED label is shown;
  - the exact score call is missing; the risk label is missing; the tactical variable is missing;
  - the share line / share control is missing;
  - generic fallback frame phrases dominate (节奏差异/风险变量：首发边路配置 — the manual {home}/{away} template).
Usage: check_rendered_llm_prediction_copy.py [--base-url URL] | --selftest
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
FALLBACK_FRAME = ["节奏差异：", "风险变量：首发边路配置与中场压迫强度"]  # manual HotspotPrediction template lines


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _art(fk):
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk):
            return a
    return None


def scan(dom, art):
    """Reviewed-copy-rendered checks against the DOM for one prediction."""
    fails = []
    zh = (art.get("i18n") or {}).get("zh") or {}
    pred = zh.get("prediction") or {}
    lj = art.get("llm_judgment") or {}
    main = lj.get("main_lean") or pred.get("primary_direction") or ""
    score = (art.get("model_fields") or {}).get("recommended_score") or pred.get("score_call")
    var = lj.get("top_variable") or pred.get("top_variable")
    copy_missing = ("COPY_MISSING" in dom) or ("REVIEW_REQUIRED" in dom)
    if main and main[:14] not in dom and not copy_missing:
        fails.append("reviewed main_lean not rendered (and no COPY_MISSING label): %r" % main[:24])
    if score and score not in dom:
        fails.append("exact score call %r not rendered" % score)
    if var and var[:10] not in dom and not copy_missing:
        fails.append("tactical variable not rendered")
    # risk label + share control presence (chrome labels)
    if not any(m in dom for m in ("冷门风险", "Upset risk", "Rủi ro")):
        fails.append("risk label not rendered")
    if not any(m in dom for m in ("复制分享文案", "复制情报链", "分享", "Share")):
        fails.append("share line/control not rendered")
    if all(f in dom for f in FALLBACK_FRAME):
        fails.append("generic fallback frame dominates the page (artifact copy not rendered)")
    return fails


def selftest():
    art = {"i18n": {"zh": {"prediction": {"primary_direction": "赛前倾向乌拉圭，沙特需压低节奏才有机会",
            "top_variable": "中场控制"}}}, "model_fields": {"recommended_score": "0-1"},
           "llm_judgment": {"main_lean": "赛前倾向乌拉圭，沙特需压低节奏才有机会", "top_variable": "中场控制"}}
    dom_ok = "赛前倾向乌拉圭，沙特需压低节奏才有机会 主比分 0-1 冷门风险 中 中场控制 复制分享文案"
    dom_bad = "节奏差异：A 推进与 B 反击转换 风险变量：首发边路配置与中场压迫强度 冷门风险 分享"
    checks = [
        ("rendered reviewed copy passes", scan(dom_ok, art) == []),
        ("missing main_lean caught", any("main_lean not rendered" in x for x in scan(dom_bad, art))),
        ("missing score caught", any("score call" in x for x in scan(dom_bad, art))),
        ("fallback frame caught", any("fallback frame dominates" in x for x in scan(dom_bad, art))),
        ("copy_missing label tolerated", scan("COPY_MISSING 主比分 0-1 冷门风险 分享", art) == []),
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
    q = _load(QUEUE) or {}
    keys = [(q.get("primary_hotspot") or {}).get("fixture_key")] + [s.get("fixture_key") for s in q.get("secondary_matches", [])]
    keys = [str(k) for k in keys if k]
    fails, checked = [], 0
    for fk in keys:
        art = _art(fk)
        if not art:
            continue
        dom = dump_dom(base.rstrip("/") + "/predict/%s?lang=zh" % fk)
        if not dom:
            fails.append("could not render /predict/%s" % fk); continue
        checked += 1
        fails += ["[%s] %s" % (fk, x) for x in scan(dom, art)]
    if checked == 0:
        print("FAIL  no /predict pages rendered"); return 1
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RENDERED LLM PREDICTION COPY FAIL — %d issue(s)" % len(fails)); return 1
    print("RENDERED LLM PREDICTION COPY PASS (%d page(s): reviewed copy rendered · score · risk · variable · share)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
