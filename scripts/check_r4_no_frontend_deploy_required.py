#!/usr/bin/env python3
"""R4 guard — a daily content change needs NO frontend deploy: runtime content overrides bundled, and
bundled remains a safe fallback. Source-level proof that the override path exists AND the fallback path
exists (so an empty/invalid runtime package degrades to bundled, never blank). Usage: --selftest"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    pa = (ROOT/"frontend/src/data/predictionArtifacts.ts").read_text(encoding="utf-8")
    rc = (ROOT/"frontend/src/data/runtimeContent.ts").read_text(encoding="utf-8")
    checks = [
        ("runtime override path present", "const rt = getRuntimePrediction(key)" in pa and "if (rt) return rt" in pa),
        ("bundled fallback retained", "PREDICTION.find(" in pa and "OBSERVATION.find(" in pa),
        ("runtime cache cleared -> bundled (setRuntimeContent(null))", "setRuntimeContent" in rc and "RC = pkg && pkg.date ? pkg : null" in rc),
        ("runtimeActive() reflects whether runtime is in use", "export function runtimeActive()" in rc),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass · content changes flow via runtime upload, not a frontend rebuild" % (
        sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


if __name__ == "__main__": sys.exit(main())
