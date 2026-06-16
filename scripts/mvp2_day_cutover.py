#!/usr/bin/env python3
"""R3 — content-paired day cutover (Owner 2026-06-16).

R2 proved a DATA-ONLY cutover (upload a new slate while the frontend selectedHotspot/reviewed content
still points at the old date) breaks live consistency. R3 fixes that: data and content move TOGETHER,
and production is uploaded ONLY after a hard local consistency gate passes.

Flow for --date D:
  1. sync the slate (R2 source; api-football default) -> daily_fixtures_D.json + bundled FE manifest
  2. build the homepage lifecycle artifact for D
  3. run the HARD GATE (check_r3_day_cutover_consistency.gate): selectedHotspot/lifecycle/slate/
     prediction+recap+share artifacts must all agree on D, primary reviewed + not finished, etc.
  4. PASS  -> upload the generated registry to the backend (only with --target) ; send stays HOLD
     FAIL  -> RESTORE the bundled artifacts to their pre-cutover bytes (no homepage change), write a
              CUTOVER_BLOCKED report, do NOT upload (production stays on the last green baseline)

This script changes NO product/UI code and never sends/publishes anything. Token (upload only) comes
from $ADMIN_API_TOKEN; it is never printed.

Usage:
  python3 scripts/mvp2_day_cutover.py --date 2026-06-15 --source manual --target production
  python3 scripts/mvp2_day_cutover.py --date 2026-06-16 --source api-football --target production
  python3 scripts/mvp2_day_cutover.py --date 2026-06-16 --source api-football        # gate only, no upload
"""
import argparse
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE = ROOT / "frontend/src/data"
PUB = ROOT / "frontend/public/data"
SYNC = ROOT / "docs/data_audit/mvp2_match_sync"
CUT_DIR = ROOT / "docs/data_audit/mvp2_day_cutover"
# bundled artifacts the cutover may touch — snapshot so a BLOCKED cutover leaves the tree clean
SNAPSHOT_FILES = [
    FE / "dailyFixtures.generated.json",
    PUB / "daily-fixtures.json",
    FE / "homepageLifecycle.json",
    FE / "selectedHotspot.json",
    FE / "dailyContentQueue.json",
]


def _imp(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _snapshot():
    return {p: (p.read_bytes() if p.exists() else None) for p in SNAPSHOT_FILES}


def _restore(snap):
    for p, b in snap.items():
        if b is None:
            if p.exists():
                p.unlink()
        else:
            p.write_text(b.decode("utf-8"), encoding="utf-8")


def run(date_iso, source, target, do_upload, now_iso=None):
    CUT_DIR.mkdir(parents=True, exist_ok=True)
    ms = _imp("mvp2_match_sync", ROOT / "scripts" / "mvp2_match_sync.py")
    lcsel = _imp("lcsel", ROOT / "scripts" / "mvp2_homepage_lifecycle_selector.py")
    r3 = _imp("r3gate", ROOT / "scripts" / "check_r3_day_cutover_consistency.py")

    snap = _snapshot()
    print("== R3 cutover %s · source=%s · target=%s%s ==" % (
        date_iso, source, target or "(gate only)", (" · basis=%s" % now_iso) if now_iso else ""))
    # 1) data refresh (R2) + 2) lifecycle build (content/homepage artifact for the SAME date).
    # now_iso is the editorial as-of basis used to evaluate lifecycle state (defaults to real now).
    now_dt = datetime.fromisoformat(now_iso) if now_iso else None
    ms.cmd_sync(date_iso, source, now=now_dt)
    try:
        lcsel.cmd_build(date_iso, now_iso, write_fe=True)
    except Exception as e:
        print("lifecycle build note: %s" % e)

    # 3) HARD GATE
    ok, fails = r3.gate(date_iso)
    if not ok:
        # 4-FAIL: restore bundled artifacts (no homepage change), write blocked report, NO upload
        _restore(snap)
        report = {"date": date_iso, "source": source, "result": "CUTOVER_BLOCKED",
                  "send_status": "HOLD", "uploaded": False, "reasons": fails,
                  "action": "production left on last green baseline; prepare reviewed content + "
                            "selectedHotspot for %s, then re-run cutover" % date_iso}
        rp = CUT_DIR / ("%s_blocked.json" % date_iso.replace("-", ""))
        rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("\nCUTOVER_BLOCKED — %d gate failure(s):" % len(fails))
        for x in fails:
            print("  - %s" % x)
        print("bundled artifacts RESTORED (no homepage change). report -> %s" % rp.relative_to(ROOT))
        print("SEND_STATUS=HOLD")
        return 2

    # 4-PASS: optionally upload to the backend (token from env, never printed)
    print("\nGATE PASS — data+content paired for %s." % date_iso)
    if do_upload and target:
        ms.cmd_upload(date_iso, target, None)
        result = "CUTOVER_UPLOADED"
    else:
        result = "GATE_PASS_NO_UPLOAD"
        print("(no --target/--upload -> gate only; nothing uploaded)")
    report = {"date": date_iso, "source": source, "result": result, "send_status": "HOLD",
              "uploaded": bool(do_upload and target), "target": target if (do_upload and target) else None}
    rp = CUT_DIR / ("%s_cutover.json" % date_iso.replace("-", ""))
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("report -> %s" % rp.relative_to(ROOT))
    print("SEND_STATUS=HOLD")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=None)
    ap.add_argument("--source", default="api-football", choices=["api-football", "manual", "fetched"])
    ap.add_argument("--target", default=None, help="production|local — REQUIRED to actually upload")
    ap.add_argument("--now", default=None, help="editorial as-of basis (ISO) for lifecycle state (default: real now)")
    ap.add_argument("--upload", action="store_true", help="upload if the gate passes (implied when --target set)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        # selftest delegates to the gate selftest (the cutover is orchestration around it)
        r3 = _imp("r3gate", ROOT / "scripts" / "check_r3_day_cutover_consistency.py")
        return r3.selftest()
    date_iso = a.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    do_upload = bool(a.target) or a.upload
    return run(date_iso, a.source, a.target, do_upload, a.now)


if __name__ == "__main__":
    sys.exit(main())
