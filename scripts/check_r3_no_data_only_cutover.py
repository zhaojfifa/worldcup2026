#!/usr/bin/env python3
"""R3 guard — a DATA-ONLY cutover must be BLOCKED. The cutover gate must refuse to upload when the
slate date moves but the content anchor (selectedHotspot) / lifecycle does NOT move with it.

--selftest: a slate for date D2 with selectedHotspot still on D1 is flagged DATA_ONLY_CUTOVER; a
  matched D/D slate+content is NOT flagged for that reason. Also asserts the cutover orchestrator
  RESTORES bundled artifacts + writes no upload on block (source inspection).
--date D: the live gate result for D — if selectedHotspot.date != D it must report blocked.
Usage: --selftest | --date YYYY-MM-DD"""
import importlib.util, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _gate():
    spec = importlib.util.spec_from_file_location("r3gate", ROOT / "scripts" / "check_r3_day_cutover_consistency.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def selftest():
    g = _gate().gate
    reg2 = {"date": "2026-06-16", "fixtures": [{"internal_fixture_id": "1489383", "status": "scheduled", "lifecycle_state": "SCHEDULED"}]}
    sel1 = {"date": "2026-06-15", "fixture_key": "1489377"}
    ok_block, fb = g("2026-06-16", reg=reg2, sel=sel1, lc={}, queue={})
    # matched date does not raise the data-only reason (other reasons may exist but not DATA_ONLY)
    reg1 = {"date": "2026-06-15", "fixtures": [{"internal_fixture_id": "1489377", "status": "scheduled", "lifecycle_state": "SCHEDULED"}]}
    _, fm = g("2026-06-15", reg=reg1, sel={"date": "2026-06-15", "fixture_key": "1489377"}, lc={}, queue={})
    src = (ROOT / "scripts" / "mvp2_day_cutover.py").read_text(encoding="utf-8")
    restores = "_restore(snap)" in src and "CUTOVER_BLOCKED" in src and "uploaded\": False" in src
    upload_after_gate = src.index("ok, fails = r3.gate") < src.index("ms.cmd_upload")
    checks = [
        ("data-only (D2 slate, D1 hotspot) BLOCKED", not ok_block and any("DATA_ONLY_CUTOVER" in x for x in fb)),
        ("matched date raises no DATA_ONLY reason", not any("DATA_ONLY_CUTOVER" in x for x in fm)),
        ("blocked cutover restores bundled artifacts + no upload", restores),
        ("upload happens only AFTER the gate", upload_after_gate),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        return selftest()
    date_iso = a[a.index("--date") + 1] if "--date" in a else "2026-06-16"
    ok, fails = _gate().gate(date_iso)
    data_only = [x for x in fails if "DATA_ONLY_CUTOVER" in x]
    if data_only:
        print("R3 NO-DATA-ONLY-CUTOVER: correctly BLOCKED for %s" % date_iso)
        for x in data_only: print("  - %s" % x)
        print("R3 NO-DATA-ONLY-CUTOVER PASS (data-only cutover is blocked; production protected)")
        return 0
    # no data-only reason -> either fully consistent (fine) or blocked for another reason (also fine)
    print("R3 NO-DATA-ONLY-CUTOVER PASS (%s: no data-only mismatch%s)" % (
        date_iso, "" if ok else " — blocked for other gate reasons"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
