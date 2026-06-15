#!/usr/bin/env python3
"""
P3A — Daily auto-run. Makes the P2 command loop REPEATABLE: one command runs the whole sequence,
recording what executed / skipped / blocked and the required operator actions. It ORCHESTRATES the
existing commands (mvp2_daily_ops.py subcommands + mvp2_t30_source.py) — it does not duplicate logic.

Modes:
  plan    --date YYYY-MM-DD                       print the sequence + what each step would do
  run     --date YYYY-MM-DD --dry-run             run read-only/idempotent steps; SKIP build-artifacts
  run     --date YYYY-MM-DD --execute-reviewed-only  also run build-artifacts (applies ONLY reviewed JSON)
  report  --date YYYY-MM-DD                       print the latest autorun artifact

Artifact: docs/data_audit/mvp2_daily_autorun/<date>.json with date, command_sequence, steps_executed,
steps_skipped, steps_blocked, required_operator_actions, send_status, publish_eligibility,
review_gate_result, runtime_match, last_run, mode, next_run.

HARD RULES: never auto-sends; never auto-publishes an LLM draft (build-artifacts applies ONLY a reviewed
JSON — and ONLY under --execute-reviewed-only); never invents T-30/recap. send stays HOLD.
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_daily_autorun"
REVIEW_Q = ROOT / "docs" / "data_audit" / "mvp2_operator_review_queue"
OPS_STATE = ROOT / "frontend" / "src" / "data" / "dailyOpsState.json"
BACKEND = "https://worldcup2026-api-71n6.onrender.com"

# (step, command argv, mutating?) — build-artifacts is the only mutating step (applies reviewed JSON).
SEQUENCE = [
    ("status", ["scripts/mvp2_daily_ops.py", "status"], False),
    ("build-queue", ["scripts/mvp2_daily_ops.py", "build-queue"], False),
    ("generate-drafts", ["scripts/mvp2_daily_ops.py", "generate-drafts", "--provider", "deepseek"], False),
    ("review-summary", ["scripts/mvp2_daily_ops.py", "review-summary"], False),
    ("t30-source", ["scripts/mvp2_t30_source.py", "build"], False),
    ("build-artifacts", ["scripts/mvp2_daily_ops.py", "build-artifacts"], True),
    ("t30-status", ["scripts/mvp2_daily_ops.py", "t30-status"], False),
    ("recap-status", ["scripts/mvp2_daily_ops.py", "recap-status"], False),
    ("share-refresh", ["scripts/mvp2_daily_ops.py", "share-refresh"], False),
    ("close-day", ["scripts/mvp2_daily_ops.py", "close-day"], False),
]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _run(argv):
    return subprocess.run([sys.executable] + argv, cwd=str(ROOT),
                          capture_output=True, text=True)


def _runtime_match(date):
    r = _run(["scripts/check_runtime_daily_fixtures.py", "--base-url", BACKEND,
              "--expected-date", date, "--expected-fixture", "1489377"])
    return "PASS" if r.returncode == 0 else "FAIL"


def _review_gate(date):
    q = _load(REVIEW_Q / ("%s.json" % date)) or {}
    items = q.get("items", [])
    published = [i for i in items if i.get("publish_eligibility") == "PUBLISHED"]
    review_required = [i for i in items if i.get("publish_eligibility") != "PUBLISHED"]
    return {"total": len(items), "published": len(published), "review_required": len(review_required),
            "gate": "REVIEWED_JSON_REQUIRED_BEFORE_PUBLISH"}


def cmd_plan(date):
    print("DAILY AUTO-RUN PLAN · %s" % date)
    for step, argv, mut in SEQUENCE:
        print("  %-16s %s%s" % (step, " ".join(argv[1:]) or argv[0], "  [MUTATING — reviewed-only]" if mut else ""))
    print("  send_status: HOLD · build-artifacts runs ONLY with --execute-reviewed-only (and only from reviewed JSON)")
    return 0


def do_run(date, dry_run, execute_reviewed_only):
    executed, skipped, blocked, actions = [], [], [], []
    for step, argv, mutating in SEQUENCE:
        if mutating and not execute_reviewed_only:
            skipped.append({"step": step, "reason": "mutating step skipped (no --execute-reviewed-only); reviewed JSON gate"})
            continue
        r = _run(argv + ["--date", date])
        if r.returncode == 0:
            executed.append({"step": step, "ok": True})
        else:
            blocked.append({"step": step, "reason": (r.stderr or r.stdout or "nonzero exit").strip().splitlines()[-1:] or "error"})
            actions.append("resolve blocked step: %s" % step)
    # operator actions from the review gate + next action
    gate = _review_gate(date)
    if gate["review_required"]:
        actions.append("%d match(es) need operator review → reviewed JSON before publish" % gate["review_required"])
    st = _load(OPS_STATE) or {}
    if st.get("next_operator_action"):
        actions.append(st["next_operator_action"])
    runtime = _runtime_match(date)
    art = {
        "date": date, "mode": ("execute-reviewed-only" if execute_reviewed_only else "dry-run"),
        "last_run": date + "T12:00:00+00:00",   # stamped from --date (no wall-clock; deterministic)
        "next_run": "operator-triggered (manual; no scheduler — no auto-send)",
        "command_sequence": [s for s, _a, _m in SEQUENCE],
        "steps_executed": executed, "steps_skipped": skipped, "steps_blocked": blocked,
        "required_operator_actions": actions or ["none — all ready; hold for Owner per-channel GO"],
        "send_status": "HOLD",
        "publish_eligibility": "%d published / %d review-required" % (gate["published"], gate["review_required"]),
        "review_gate_result": gate, "runtime_match": runtime,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("%s.json" % date)).write_text(json.dumps(art, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # final refresh so dailyOpsState folds in the autorun summary + t30 sources
    _run(["scripts/mvp2_daily_ops.py", "status", "--date", date])
    return art


def cmd_run(date, dry_run, execute_reviewed_only):
    art = do_run(date, dry_run, execute_reviewed_only)
    print("DAILY AUTO-RUN (%s) · %s · runtime=%s · send=%s" % (art["mode"], date, art["runtime_match"], art["send_status"]))
    print("  executed: %s" % ", ".join(s["step"] for s in art["steps_executed"]))
    print("  skipped:  %s" % (", ".join(s["step"] for s in art["steps_skipped"]) or "none"))
    print("  blocked:  %s" % (", ".join(s["step"] for s in art["steps_blocked"]) or "none"))
    print("  publish:  %s" % art["publish_eligibility"])
    print("  actions:  %s" % " | ".join(art["required_operator_actions"]))
    return 0 if not art["steps_blocked"] else 1


def cmd_report(date):
    art = _load(OUT_DIR / ("%s.json" % date))
    if not art:
        print("FAIL  no autorun artifact for %s (run: run --date %s --dry-run)" % (date, date)); return 1
    print(json.dumps(art, ensure_ascii=False, indent=2))
    return 0


def selftest():
    checks = [
        ("sequence has all 10 steps", len(SEQUENCE) == 10),
        ("build-artifacts is the only mutating step", [s for s, _a, m in SEQUENCE if m] == ["build-artifacts"]),
        ("generate-drafts present", any(s == "generate-drafts" for s, _a, _m in SEQUENCE)),
        ("t30-source present", any(s == "t30-source" for s, _a, _m in SEQUENCE)),
        ("close-day last", SEQUENCE[-1][0] == "close-day"),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["plan", "run", "report"])
    ap.add_argument("--date", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute-reviewed-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    import datetime
    date = a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if a.cmd == "plan":
        return cmd_plan(date)
    if a.cmd == "run":
        return cmd_run(date, a.dry_run, a.execute_reviewed_only)
    if a.cmd == "report":
        return cmd_report(date)
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
