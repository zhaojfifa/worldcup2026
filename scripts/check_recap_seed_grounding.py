#!/usr/bin/env python3
"""
P1B — recap_seed grounding guard. Every generated prediction draft must carry a recap_seed that is
GROUNDED in the pre-match call (references the predicted score), so the post-match recap can verify
the call instead of inventing one. Also: no fake event claims in the seed.

  - generated draft has a non-empty recap_seed;
  - the recap_seed references the predicted primary_score (grounding — links call → recap check);
  - the seed contains no fabricated player-event claims (no specific minute/scorer assertions);
  - finished fixtures still resolve to an observation/recap state (no fake full recap) — cross-check
    with recapArtifacts/observation artifacts.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "generated"
RECAP_DIR = ROOT / "frontend" / "src" / "data" / "recapArtifacts"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
# fabricated-event smell: a concrete minute + goal/scorer claim in a PRE-match seed
FAKE_EVENT = re.compile(r"第\s*\d{1,3}\s*分钟.*(进球|破门|红牌|点球|罚下)")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan_seed(name, d):
    fails = []
    draft = d.get("draft") or {}
    seed = draft.get("recap_seed") or ""
    score = draft.get("primary_score") or ""
    if not seed.strip():
        fails.append("%s: empty recap_seed" % name)
        return fails
    # grounding: the seed should reference the predicted score (the call it will verify)
    if score and score not in seed:
        fails.append("%s: recap_seed not grounded in primary_score %r (no call→recap link)" % (name, score))
    if FAKE_EVENT.search(seed):
        fails.append("%s: recap_seed asserts a fabricated match event (pre-match seed must not)" % name)
    return fails


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fails = []
    drafts = sorted(GEN_DIR.glob("*_generated.json")) if GEN_DIR.exists() else []
    if not drafts:
        print("FAIL  no generated drafts to check recap_seed grounding"); return 1
    for p in drafts:
        fails += scan_seed(p.name, _load(p))
    # cross-check: finished fixtures with a recap artifact must not fake a full recap
    if RECAP_DIR.exists():
        for p in RECAP_DIR.glob("*.json"):
            a = _load(p)
            if a and a.get("recap_state") == "OBSERVATION_READY" and a.get("recap_ready") is True:
                fails.append("%s: OBSERVATION_READY recap artifact mislabeled recap_ready=true" % p.name)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RECAP SEED GROUNDING FAIL — %d issue(s)" % len(fails)); return 1
    print("RECAP SEED GROUNDING PASS (%d draft(s): recap_seed present + grounded in primary_score + no "
          "fabricated events)" % len(drafts))
    return 0


def selftest():
    good = {"draft": {"primary_score": "1-0", "recap_seed": "赛后核对：主推 1-0 是否兑现、实际与 1-0 的偏差。"}}
    nogrnd = {"draft": {"primary_score": "1-0", "recap_seed": "赛后看看谁赢。"}}
    fake = {"draft": {"primary_score": "1-0", "recap_seed": "第 23 分钟必进球破门，主推 1-0。"}}
    checks = [
        ("grounded seed passes", scan_seed("g", good) == []),
        ("ungrounded seed caught", any("not grounded" in x for x in scan_seed("g", nogrnd))),
        ("fabricated event caught", any("fabricated" in x for x in scan_seed("g", fake))),
        ("empty seed caught", any("empty" in x for x in scan_seed("g", {"draft": {"primary_score": "1-0", "recap_seed": ""}}))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
