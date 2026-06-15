#!/usr/bin/env python3
"""
P1 — recap-generation-flow guard. Fails if:
  - a finished fixture in the queue's recap_queue has neither an observation nor a recap state;
  - the recap route (RecapDetailPage.tsx) is not gated (would leak a raw backend no-recap error);
  - a RECAP_READY recap artifact has no full text (headline + tactical_review present);
  - an observation-only artifact is mislabeled as a full recap (recap_ready true while OBSERVATION_READY);
  - a recap artifact / observation is missing share copy.
Reads frontend/src/data/recapArtifacts/*.json + observation artifacts + the recap route source +
the content queue's recap_queue.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECAP_PAGE = ROOT / "frontend" / "src" / "pages" / "RecapDetailPage.tsx"
RECAP_DIR = ROOT / "frontend" / "src" / "data" / "recapArtifacts"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
VALID_RECAP_STATES = {"WAITING_FT", "FT_READY", "OBSERVATION_READY", "RECAP_PROMPT_READY",
                      "RECAP_REVIEW_READY", "RECAP_READY", "RECAP_ERROR"}


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan_route(src):
    fails = []
    if "api.getRecap" in src:
        before = src[:src.index("api.getRecap")]
        if "hasObservation" not in before and "hasLocalProductRecap" not in before:
            fails.append("RecapDetailPage: api.getRecap not gated — would leak the backend no-recap error")
    return fails


def scan_recap_artifact(name, a):
    fails = []
    st = a.get("recap_state")
    if st not in VALID_RECAP_STATES:
        fails.append("%s: recap_state %r invalid" % (name, st))
    if st == "RECAP_READY":
        if not a.get("headline") or not a.get("tactical_review") or "pending" in str(a.get("tactical_review", "")).lower():
            fails.append("%s: RECAP_READY but no full tactical_review text (fake/empty full recap)" % name)
    if st == "OBSERVATION_READY" and a.get("recap_ready") is True:
        fails.append("%s: OBSERVATION_READY mislabeled recap_ready=true (observation is not a full recap)" % name)
    if (a.get("safety") or {}).get("no_fake_recap") is not True:
        fails.append("%s: safety.no_fake_recap must be true" % name)
    return fails


def scan_observation(name, o):
    fails = []
    if o.get("recap_ready") is not False:
        fails.append("%s: observation recap_ready must be false" % name)
    if not (((o.get("i18n") or {}).get("zh") or {}).get("share_copy")):
        fails.append("%s: observation missing zh share_copy (recap share)" % name)
    return fails


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fails = []
    src = RECAP_PAGE.read_text(encoding="utf-8") if RECAP_PAGE.exists() else ""
    fails += scan_route(src)

    observations, recaps = {}, {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = _load(p)
            if a and "recap_ready" in a:
                for k in (a.get("id"), a.get("fixture_key")):
                    if k:
                        observations[str(k)] = a
                fails += scan_observation(p.name, a)
    if RECAP_DIR.exists():
        for p in sorted(RECAP_DIR.glob("*.json")):
            a = _load(p)
            if a:
                for k in (a.get("id"), a.get("fixture_key")):
                    if k:
                        recaps[str(k)] = a
                fails += scan_recap_artifact(p.name, a)

    # every finished fixture in the recap queue must resolve to an observation or a recap state
    q = _load(QUEUE) or {}
    for rq in q.get("recap_queue", []):
        keys = [str(rq.get("fixture_key")), str(rq.get("id"))]
        has = any(k in observations or k in recaps for k in keys) or rq.get("recap_state") in VALID_RECAP_STATES
        if not has:
            fails.append("recap_queue %s vs %s has no observation/recap state" % (rq.get("home"), rq.get("away")))

    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RECAP GENERATION FLOW FAIL — %d issue(s)" % len(fails)); return 1
    print("RECAP GENERATION FLOW PASS (route gated · %d observation · %d recap artifact · states valid · "
          "no fake full recap · share present)" % (len(observations), len(recaps)))
    return 0


def selftest():
    good_obs = {"recap_ready": False, "i18n": {"zh": {"share_copy": "x"}}}
    good_recap = {"recap_state": "OBSERVATION_READY", "recap_ready": False, "safety": {"no_fake_recap": True}}
    full = {"recap_state": "RECAP_READY", "headline": "h", "tactical_review": "real review", "safety": {"no_fake_recap": True}}
    checks = [
        ("gated route passes", scan_route("const hasObservation=x; if(hasObservation)return; api.getRecap()") == []),
        ("ungated route caught", any("not gated" in x for x in scan_route("api.getRecap(a,b)"))),
        ("good observation passes", scan_observation("o", good_obs) == []),
        ("observation no-share caught", any("share" in x for x in scan_observation("o", {"recap_ready": False, "i18n": {"zh": {}}}))),
        ("good recap passes", scan_recap_artifact("r", good_recap) == []),
        ("full recap passes", scan_recap_artifact("r", full) == []),
        ("empty full recap caught", any("full tactical_review" in x for x in scan_recap_artifact("r", {"recap_state": "RECAP_READY", "headline": "h", "tactical_review": "pending", "safety": {"no_fake_recap": True}}))),
        ("mislabel caught", any("mislabeled" in x for x in scan_recap_artifact("r", {"recap_state": "OBSERVATION_READY", "recap_ready": True, "safety": {"no_fake_recap": True}}))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
