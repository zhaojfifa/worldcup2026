#!/usr/bin/env python3
"""
P1B — auto-LLM factory guard. Validates the generated draft layer + generator safety:
  - the generator exists with a dry-run path and a --selftest (offline-capable, no network needed);
  - no provider secret is committed (no API key literal in the generator);
  - every generated draft carries: required output fields, a recorded provider + mode, a valid status,
    recap_seed, safety_flags; win_prob/numeric confidence absent; no betting/fake-probability vocab.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "generated"
GEN_SCRIPT = ROOT / "scripts" / "mvp2_autogen_prediction_draft.py"
REQUIRED_OUT = ["strong_headline", "main_lean", "primary_score", "backup_scores", "risk_level",
                "top_variable", "why", "tactical_beats", "data_source_basis", "external_expectation_safe",
                "t30_checklist", "homepage_short", "predict_medium", "share_copy", "recap_seed", "safety_flags"]
VALID_STATUS = {"GENERATED", "GUARD_PASSED", "NEEDS_REVIEW", "APPROVED", "REJECTED", "ARTIFACT_READY"}
BETTING = ["赔率", "盘口", "下注", "投注", "让球", "odds", "handicap", "betting", "kèo", "稳赢", "必胜", "chắc thắng"]
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]
# a committed API key would look like a long opaque token assigned to a *_API_KEY var with a real value
KEY_LITERAL = re.compile(r"(DEEPSEEK|GEMINI|KIMI|MOONSHOT)_API_KEY\s*=\s*['\"][A-Za-z0-9_\-]{16,}")


def _strings(x, out):
    if isinstance(x, str):
        out.append(x)
    elif isinstance(x, list):
        [_strings(i, out) for i in x]
    elif isinstance(x, dict):
        [_strings(v, out) for v in x.values()]


def scan_draft(name, d):
    fails = []
    if d.get("status") not in VALID_STATUS:
        fails.append("%s: status %r invalid" % (name, d.get("status")))
    if not d.get("provider"):
        fails.append("%s: no provider recorded" % name)
    draft = d.get("draft") or {}
    for k in REQUIRED_OUT:
        if k not in draft or (isinstance(draft[k], str) and not draft[k].strip()):
            fails.append("%s: draft missing/empty %s" % (name, k))
    if not draft.get("recap_seed"):
        fails.append("%s: draft missing recap_seed" % name)
    if "win_prob" in draft or isinstance(draft.get("confidence"), (int, float)):
        fails.append("%s: draft carries a probability/confidence value" % name)
    vals = []
    _strings({k: v for k, v in draft.items() if k != "safety_flags"}, vals)
    blob = " ".join(vals); low = blob.lower()
    for w in BETTING + FAKE_PROB:
        if (w.lower() in low) if w.isascii() else (w in blob):
            fails.append("%s: forbidden vocab %r" % (name, w))
    return fails


def scan_generator(src):
    fails = []
    if "dry_run_draft" not in src:
        fails.append("generator missing dry-run path")
    if "def selftest" not in src:
        fails.append("generator missing --selftest")
    if KEY_LITERAL.search(src):
        fails.append("generator appears to embed an API key literal (secret must not be committed)")
    return fails


def selftest():
    good = {"status": "GUARD_PASSED", "provider": "deepseek",
            "draft": {k: ("x" if k not in ("backup_scores", "tactical_beats", "external_expectation_safe", "t30_checklist", "safety_flags") else (["a", "b"] if k != "safety_flags" else {})) for k in REQUIRED_OUT}}
    good["draft"]["recap_seed"] = "赛后核对主推 1-0"
    good["draft"]["primary_score"] = "1-0"
    checks = [
        ("clean draft passes", scan_draft("g", good) == []),
        ("bad status caught", any("status" in x for x in scan_draft("g", dict(good, status="LIVE")))),
        ("missing recap_seed caught", any("recap_seed" in x for x in scan_draft("g", dict(good, draft={k: v for k, v in good["draft"].items() if k != "recap_seed"})))),
        ("forbidden vocab caught", any("forbidden" in x for x in scan_draft("g", dict(good, draft=dict(good["draft"], why="看 赔率"))))),
        ("probability caught", any("probability" in x for x in scan_draft("g", dict(good, draft=dict(good["draft"], confidence=0.6))))),
        ("generator dry-run+selftest ok", scan_generator("def dry_run_draft(): pass\ndef selftest(): pass") == []),
        ("committed key caught", any("API key" in x for x in scan_generator("DEEPSEEK_API_KEY='sk-abcdef0123456789abcdef'\ndef dry_run_draft():0\ndef selftest():0"))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fails = []
    if not GEN_SCRIPT.exists():
        print("FAIL  generator script missing"); return 1
    fails += scan_generator(GEN_SCRIPT.read_text(encoding="utf-8"))
    drafts = sorted(GEN_DIR.glob("*_generated.json")) if GEN_DIR.exists() else []
    if not drafts:
        print("FAIL  no generated drafts in %s (run mvp2_autogen_prediction_draft.py generate)" % GEN_DIR.relative_to(ROOT)); return 1
    for p in drafts:
        fails += scan_draft(p.name, json.loads(p.read_text(encoding="utf-8")))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("AUTO LLM FACTORY FAIL — %d issue(s)" % len(fails)); return 1
    print("AUTO LLM FACTORY PASS (%d draft(s); generator dry-run+selftest; no committed secret; "
          "required fields + recap_seed; no probability/forbidden vocab)" % len(drafts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
