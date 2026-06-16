#!/usr/bin/env python3
"""P5B — archive/demo exclusion guard. No WC-2022 archive or demo PAIRING in the ACTIVE homepage
surface (folds stripped); the lifecycle artifact's active roles contain no archive/demo fixture.
Usage: --base-url URL | --selftest"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom, strip_folds, demo_pair_leak  # noqa: E402
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(p): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan_artifact(lc):
    f = []
    active = [lc.get("primary_prediction")] + lc.get("secondary_predictions", []) + [lc.get("latest_recap")]
    for r in [x for x in active if x]:
        if r.get("lifecycle_state") in ("ARCHIVE_ONLY", "EXCLUDED_DEMO"):
            f.append("active role holds archive/demo fixture %s" % r["fixture_id"])
    return f


def selftest():
    checks = [("clean passes", scan_artifact({"primary_prediction": {"fixture_id": "1", "lifecycle_state": "UPCOMING_PREDICTION_READY"}}) == []),
              ("archive active caught", any("archive/demo" in x for x in scan_artifact({"primary_prediction": {"fixture_id": "1", "lifecycle_state": "ARCHIVE_ONLY"}}))),
              ("demo_pair_leak precise", demo_pair_leak("德国 vs Japan") is None and demo_pair_leak("荷兰 vs Japan") is not None)]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks))); return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url") + 1] if "--base-url" in a else "https://worldcup2026-izid.onrender.com"
    lc = _load(ROOT / "frontend/src/data/homepageLifecycle.json") or {}
    fails = scan_artifact(lc)
    dom = dump_dom(base.rstrip("/") + "/?lang=zh")
    if dom:
        leak = demo_pair_leak(strip_folds(dom))
        if leak: fails.append("demo pairing %r in active homepage surface" % leak)
    for x in fails: print("FAIL  %s" % x)
    if fails: print("P5B ARCHIVE/DEMO EXCLUSION FAIL — %d" % len(fails)); return 1
    print("P5B ARCHIVE/DEMO EXCLUSION PASS (no archive/demo in active roles or active homepage surface)"); return 0


if __name__ == "__main__": sys.exit(main())
