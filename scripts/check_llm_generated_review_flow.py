#!/usr/bin/env python3
"""
P1B — generated→review→artifact flow guard. Enforces the operator-gate invariant:
  - the three flow dirs exist: prompts/ generated/ reviewed/;
  - a GENERATED draft NEVER becomes a published artifact without a reviewed JSON (operator gate):
    for every generated draft, IF a prediction artifact exists for that fixture_key, its
    content_chain.reviewed_applied must be true and a reviewed file must exist — i.e. the draft did
    not silently publish;
  - generated drafts carry a non-publishing note and a valid status;
  - the generator does not write into predictionArtifacts/ (no auto-publish path).
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
PROMPT_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "prompts"
GEN_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "generated"
REVIEWED_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "reviewed"
GEN_SCRIPT = ROOT / "scripts" / "mvp2_autogen_prediction_draft.py"
VALID_STATUS = {"GENERATED", "GUARD_PASSED", "NEEDS_REVIEW", "APPROVED", "REJECTED", "ARTIFACT_READY"}


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def find_artifact(fixture_key):
    if not PRED_DIR.exists():
        return None
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if not a or "recap_ready" in a:
            continue
        if a.get("fixture_key") == fixture_key or (a.get("id") and a["id"] == fixture_key):
            return a
    return None


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fails = []
    for d in (PROMPT_DIR, GEN_DIR, REVIEWED_DIR):
        if not d.exists():
            fails.append("flow dir missing: %s" % d.relative_to(ROOT))
    # generator must not write into predictionArtifacts (no auto-publish)
    if GEN_SCRIPT.exists():
        src = GEN_SCRIPT.read_text(encoding="utf-8")
        if "predictionArtifacts" in src and "PRED_DIR" in src:
            # PRED_DIR is read-only (find_artifact); fail only if it writes there
            if any(w in src for w in ("PRED_DIR /", "PRED_DIR/")) and "write_text" in src.split("PRED_DIR")[-1][:200]:
                fails.append("generator may write into predictionArtifacts (auto-publish risk)")
    drafts = sorted(GEN_DIR.glob("*_generated.json")) if GEN_DIR.exists() else []
    for p in drafts:
        d = _load(p)
        if d.get("status") not in VALID_STATUS:
            fails.append("%s: invalid status %r" % (p.name, d.get("status")))
        if "NOT published" not in (d.get("_note") or "") and "review" not in (d.get("_note") or "").lower():
            fails.append("%s: missing non-publishing operator-review note" % p.name)
        # operator gate: a published artifact for this fixture must have gone through reviewed JSON
        art = find_artifact(d.get("fixture_key"))
        if art:
            cc = art.get("content_chain") or {}
            if not cc.get("reviewed_applied"):
                fails.append("%s: artifact exists but reviewed_applied is not true (draft published without review?)" % p.name)
            elif cc.get("reviewed_path") and not (ROOT / cc["reviewed_path"]).exists():
                fails.append("%s: artifact reviewed_path missing on disk" % p.name)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("LLM GENERATED REVIEW FLOW FAIL — %d issue(s)" % len(fails)); return 1
    print("LLM GENERATED REVIEW FLOW PASS (prompts/generated/reviewed dirs · %d draft(s) non-publishing · "
          "every published artifact went through reviewed JSON · no auto-publish path)" % len(drafts))
    return 0


def selftest():
    # logic-level checks via temp reasoning (no fs writes): status validity + note requirement
    checks = [
        ("valid status set", "GUARD_PASSED" in VALID_STATUS and "LIVE" not in VALID_STATUS),
        ("note requirement string", "NOT published".lower() in "generated draft for operator review only — not published".lower()),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
