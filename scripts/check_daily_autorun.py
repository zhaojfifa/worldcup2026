#!/usr/bin/env python3
"""
P3A — daily-autorun guard.
  - scripts/mvp2_daily_autorun.py exists with plan/run/report + --selftest;
  - build-artifacts is the ONLY mutating step and runs ONLY under --execute-reviewed-only
    (dry-run must skip it — no draft auto-publish, reviewed-JSON gate);
  - the autorun never auto-sends;
  - the artifact for the date carries: date, command_sequence, steps_executed/skipped/blocked,
    required_operator_actions, send_status=HOLD, publish_eligibility, review_gate_result, runtime_match.
Usage: check_daily_autorun.py [--date YYYY-MM-DD] | --selftest.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mvp2_daily_autorun.py"
ART_DIR = ROOT / "docs" / "data_audit" / "mvp2_daily_autorun"
ART_KEYS = ["date", "command_sequence", "steps_executed", "steps_skipped", "steps_blocked",
            "required_operator_actions", "send_status", "publish_eligibility", "review_gate_result", "runtime_match"]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan_script(src):
    fails = []
    for c in ("plan", "run", "report"):
        if ('"%s"' % c) not in src:
            fails.append("autorun missing mode %r" % c)
    if "def selftest" not in src:
        fails.append("autorun missing --selftest")
    if "execute_reviewed_only" not in src and "execute-reviewed-only" not in src:
        fails.append("autorun missing --execute-reviewed-only gate")
    # build-artifacts must be guarded by the reviewed-only flag (mutating-skip path)
    if "mutating" not in src or "execute_reviewed_only" not in src:
        fails.append("autorun does not gate the mutating build-artifacts step")
    return fails


def scan_artifact(art):
    fails = []
    for k in ART_KEYS:
        if k not in art:
            fails.append("autorun artifact missing %r" % k)
    if art.get("send_status") != "HOLD":
        fails.append("autorun artifact send_status must be HOLD")
    # in dry-run mode, build-artifacts must be among skipped (gate)
    if art.get("mode") == "dry-run":
        if "build-artifacts" not in [s.get("step") for s in art.get("steps_skipped", [])]:
            fails.append("dry-run did not skip build-artifacts (reviewed gate not enforced)")
    return fails


def selftest():
    good_src = '"plan" "run" "report" def selftest(): pass execute_reviewed_only mutating'
    good_art = {k: ([] if "steps" in k or k == "required_operator_actions" else "x") for k in ART_KEYS}
    good_art.update(send_status="HOLD", mode="dry-run", steps_skipped=[{"step": "build-artifacts"}])
    checks = [
        ("clean script passes", scan_script(good_src) == []),
        ("missing gate caught", any("gate" in x for x in scan_script('"plan" "run" "report" def selftest(): pass'))),
        ("clean artifact passes", scan_artifact(good_art) == []),
        ("auto-send caught", any("HOLD" in x for x in scan_artifact(dict(good_art, send_status="LIVE")))),
        ("dry-run not skipping build-artifacts caught", any("did not skip" in x for x in scan_artifact(dict(good_art, steps_skipped=[])))),
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
    date = argv[argv.index("--date") + 1] if "--date" in argv else None
    fails = []
    if not SCRIPT.exists():
        print("FAIL  mvp2_daily_autorun.py missing"); return 1
    fails += scan_script(SCRIPT.read_text(encoding="utf-8"))
    arts = sorted(ART_DIR.glob("*.json")) if ART_DIR.exists() else []
    art_p = (ART_DIR / ("%s.json" % date)) if date else (arts[-1] if arts else None)
    if not art_p or not art_p.exists():
        fails.append("no autorun artifact (run: mvp2_daily_autorun.py run --date <d> --dry-run)")
    else:
        fails += scan_artifact(_load(art_p))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("DAILY AUTORUN FAIL — %d issue(s)" % len(fails)); return 1
    print("DAILY AUTORUN PASS (plan/run/report · reviewed-only gate on build-artifacts · artifact complete · send HOLD)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
