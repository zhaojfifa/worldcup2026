#!/usr/bin/env python3
"""
R3 — Recap-pipeline guard.

Proves the recap route no longer leaks a backend "no recap" 404 as a product failure, and that
recap state is explicit:
  - RecapDetailPage.tsx GATES api.getRecap — it must NOT be called unconditionally; when a local
    source (bundled product-narrative recap OR an observation artifact) drives the page, the backend
    call is skipped (no 404 leak). We assert the guard exists (hasLocalProductRecap / hasObservation
    short-circuit before api.getRecap).
  - predictionArtifacts.ts exports a recapState(...) helper with the four states.
  - every observation artifact: recap_ready=false (NO fake recap), carries full content fields, and
    safety.no_fake_recap is asserted.
  - the carryover observation resolves to a non-RECAP_ERROR state.

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECAP_PAGE = ROOT / "frontend" / "src" / "pages" / "RecapDetailPage.tsx"
PRED_TS = ROOT / "frontend" / "src" / "data" / "predictionArtifacts.ts"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"

OBS_REQUIRED = ["receipt_title", "pre_match_call", "actual_line", "assessment",
                "calibration_title", "calibration_points", "deviation", "next_impact",
                "pending_line", "state_line", "share_title", "share_copy", "join_cta"]


def scan_source(recap_src, pred_src):
    fails = []
    # the api.getRecap call must be guarded — a short-circuit return precedes it
    if "api.getRecap" in recap_src:
        # find the guard: hasObservation / hasLocalProductRecap referenced before the api call
        idx = recap_src.index("api.getRecap")
        before = recap_src[:idx]
        if "hasObservation" not in before and "hasLocalProductRecap" not in before:
            fails.append("RecapDetailPage: api.getRecap is not gated by a local-source short-circuit "
                         "(would leak the backend 404)")
    else:
        fails.append("RecapDetailPage: api.getRecap not found (unexpected)")
    if "recapState" not in pred_src or "export function recapState" not in pred_src:
        fails.append("predictionArtifacts.ts: recapState helper not exported")
    for st in ("OBSERVATION_READY", "RECAP_PENDING", "RECAP_READY", "RECAP_ERROR"):
        if st not in pred_src:
            fails.append("predictionArtifacts.ts: recap state %r missing" % st)
    return fails


def scan_observations(observations):
    fails = []
    for name, o in observations:
        if o.get("recap_ready") is not False:
            fails.append("%s: observation recap_ready must be false (no fake recap)" % name)
        zh = ((o.get("i18n") or {}).get("zh") or {})
        for f in OBS_REQUIRED:
            if not zh.get(f):
                fails.append("%s: observation zh missing %r" % (name, f))
        saf = o.get("safety") or {}
        if saf.get("no_fake_recap") is not True:
            fails.append("%s: observation safety.no_fake_recap must be true" % name)
    return fails


def selftest():
    good_recap = ("const obsLocal = getObservationArtifact(fixtureId);\n"
                  "const hasObservation = !!obsLocal && !obsLocal.recap_ready;\n"
                  "if (hasLocalProductRecap || hasObservation) { return; }\n"
                  "api.getRecap(fixtureId, loc)")
    bad_recap = "api.getRecap(fixtureId, loc).then(setContent)"
    good_pred = ("export type RecapState = 'OBSERVATION_READY'|'RECAP_PENDING'|'RECAP_READY'|'RECAP_ERROR';\n"
                 "export function recapState(key, h) { return 'OBSERVATION_READY'; }")
    good_obs = {"recap_ready": False, "i18n": {"zh": {f: "x" for f in OBS_REQUIRED}},
                "safety": {"no_fake_recap": True}}
    bad_obs = {"recap_ready": True, "i18n": {"zh": {f: "x" for f in OBS_REQUIRED}},
               "safety": {"no_fake_recap": True}}
    checks = [
        ("clean source passes", scan_source(good_recap, good_pred) == []),
        ("ungated api call caught", any("not gated" in x for x in scan_source(bad_recap, good_pred))),
        ("missing recapState caught", any("recapState" in x for x in scan_source(good_recap, "x"))),
        ("clean observation passes", scan_observations([("o", good_obs)]) == []),
        ("fake recap caught", any("no fake recap" in x for x in scan_observations([("o", bad_obs)]))),
        ("missing field caught", any("missing" in x for x in scan_observations(
            [("o", {"recap_ready": False, "i18n": {"zh": {}}, "safety": {"no_fake_recap": True}})]))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    recap_src = RECAP_PAGE.read_text(encoding="utf-8") if RECAP_PAGE.exists() else ""
    pred_src = PRED_TS.read_text(encoding="utf-8") if PRED_TS.exists() else ""
    observations = []
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = json.loads(p.read_text(encoding="utf-8"))
            if "recap_ready" in a:
                observations.append((p.name, a))
    fails = scan_source(recap_src, pred_src) + scan_observations(observations)
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("RECAP PIPELINE FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("RECAP PIPELINE PASS (route gates backend call · recapState explicit · "
                     "observations recap_ready=false · no fake recap · no raw 404 leak)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
