#!/usr/bin/env python3
"""R4 guard — the frontend reads runtime content FIRST, bundled as fallback. Source inspection:
getPredictionArtifact/getObservationArtifact check the runtime accessor before the bundled array;
selectProductLoop prefers runtime lifecycle/selectedHotspot; the App bootstrap populates the cache
before rendering. Usage: --selftest"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    a = sys.argv[1:]
    pa = (ROOT/"frontend/src/data/predictionArtifacts.ts").read_text(encoding="utf-8")
    df = (ROOT/"frontend/src/data/dailyFixtures.ts").read_text(encoding="utf-8")
    app = (ROOT/"frontend/src/App.tsx").read_text(encoding="utf-8")
    rc = (ROOT/"frontend/src/data/runtimeContent.ts").read_text(encoding="utf-8")
    # getPredictionArtifact: runtime check before the bundled PREDICTION.find
    gp = pa.split("export function getPredictionArtifact", 1)[-1].split("export function", 1)[0]
    go = pa.split("export function getObservationArtifact", 1)[-1].split("export function", 1)[0]
    checks = [
        ("getPredictionArtifact prefers runtime", "getRuntimePrediction" in gp and gp.index("getRuntimePrediction") < gp.index("PREDICTION.find")),
        ("getObservationArtifact prefers runtime", "getRuntimeObservation" in go and go.index("getRuntimeObservation") < go.index("OBSERVATION.find")),
        ("selectProductLoop prefers runtime lifecycle", "getRuntimeLifecycle() as HomepageLifecycle" in df or "getRuntimeLifecycle()" in df),
        ("selectProductLoop prefers runtime selectedHotspot", "getRuntimeSelectedHotspot()" in df),
        ("App awaits bootstrapRuntime before render", "bootstrapRuntime()" in app and "if (!ready)" in app),
        ("runtimeContent module has no import statements (no cycle)", not any(l.lstrip().startswith("import ") for l in rc.splitlines())),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else (0 if "--selftest" not in a and ok else 1)


if __name__ == "__main__": sys.exit(0 if main()==0 else 1)
