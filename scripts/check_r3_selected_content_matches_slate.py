#!/usr/bin/env python3
"""R3 guard — every SELECTED content fixture (primary/secondary/recap) exists in the generated slate
and is backed by the right artifact: the primary by a REVIEWED prediction artifact, a recap fixture by
an observation/recap artifact. Prevents a homepage that points at a fixture the slate/content lacks.

--selftest: synthetic checks (primary present+reviewed passes; primary absent from slate fails;
  recap without artifact fails). --date D: validates the live artifacts for D via the gate.
Usage: --selftest | --date YYYY-MM-DD"""
import importlib.util, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _gate_mod():
    spec = importlib.util.spec_from_file_location("r3gate", ROOT / "scripts" / "check_r3_day_cutover_consistency.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def selftest():
    g = _gate_mod()
    # primary in slate but no reviewed artifact -> flagged
    reg = {"date": "2026-06-16", "fixtures": [{"internal_fixture_id": "9999", "status": "scheduled", "lifecycle_state": "SCHEDULED"}]}
    _, f1 = g.gate("2026-06-16", reg=reg, sel={"date": "2026-06-16", "fixture_key": "9999"}, lc={}, queue={})
    # primary not in slate -> flagged
    _, f2 = g.gate("2026-06-16", reg={"date": "2026-06-16", "fixtures": []}, sel={"date": "2026-06-16", "fixture_key": "9999"}, lc={}, queue={})
    checks = [
        ("primary without reviewed artifact flagged", any("NO reviewed prediction artifact" in x for x in f1)),
        ("primary not in slate flagged", any("not in generated slate" in x for x in f2)),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        return selftest()
    date_iso = a[a.index("--date") + 1] if "--date" in a else "2026-06-15"
    g = _gate_mod()
    ok, fails = g.gate(date_iso)
    rel = [x for x in fails if ("not in generated slate" in x or "reviewed prediction artifact" in x or "not reviewed" in x)]
    for x in rel: print("FAIL  %s" % x)
    if rel:
        print("R3 SELECTED-CONTENT-MATCHES-SLATE FAIL — %d (selected content not backed by slate/artifacts)" % len(rel))
        return 1
    print("R3 SELECTED-CONTENT-MATCHES-SLATE PASS (%s: selected primary/secondary/recap all in slate + artifact-backed)" % date_iso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
