#!/usr/bin/env python3
"""R4 guard — runtime content is used ONLY when its date matches the EFFECTIVE daily-manifest date, so
the UI never mixes a runtime selection with a different-date slate. Source inspection of the bootstrap
gating rule. Usage: --selftest"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    df = (ROOT/"frontend/src/data/dailyFixtures.ts").read_text(encoding="utf-8")
    boot = df.split("export async function bootstrapRuntime", 1)[-1].split("export function", 1)[0]
    checks = [
        ("computes effectiveDate from manifest", "generated_for_date" in boot and "effectiveDate" in boot),
        ("requires content date == effectiveDate", "dateMatch" in boot and "pkg.date === effectiveDate" in boot),
        ("requires fresh (not stale)", "rcFresh" in boot and "stale" in boot),
        ("sets bundled fallback on mismatch", "setRuntimeContent(null)" in boot),
        ("only enables runtime when rcFresh && dateMatch", "rcFresh && dateMatch" in boot),
        # R5 follow-up: the runtime selectedHotspot anchors R2a acceptance (fetched before the manifest)
        ("runtime selectedHotspot anchors R2a", "runtimeSel" in boot and "fetchDailyManifest(runtimeSel)" in boot),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass · no mixed backend/frontend dates" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


if __name__ == "__main__": sys.exit(main())
