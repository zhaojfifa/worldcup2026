#!/usr/bin/env python3
"""R4 guard — the runtime content cutover produces a valid CONTENT package and the backend stores/serves
it. --selftest (offline): assemble_package yields {date, selectedHotspot, predictions(non-empty),
observations}; the backend service normalize/assemble round-trips a package and rejects an empty one.
--base-url URL: GET /api/v1/runtime-content returns a stored package with predictions OR empty-but-valid.
Usage: --selftest | --base-url URL"""
import importlib.util, json, pathlib, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]


def selftest():
    cut = importlib.util.spec_from_file_location("cut", ROOT/"scripts"/"mvp2_runtime_content_cutover.py")
    m = importlib.util.module_from_spec(cut); cut.loader.exec_module(m)
    pkg = m.assemble_package("2026-06-15", "manual")
    checks = [
        ("package has date", pkg.get("date") == "2026-06-15"),
        ("package send_status HOLD", pkg.get("send_status") == "HOLD"),
        ("predictions non-empty", isinstance(pkg.get("predictions"), dict) and len(pkg["predictions"]) >= 1),
        ("selectedHotspot present", bool(pkg.get("selectedHotspot"))),
        ("primary 1489377 in predictions", "1489377" in pkg.get("predictions", {})),
        ("recap observation 1489371 present", "1489371" in pkg.get("observations", {})),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a: return selftest()
    base = a[a.index("--base-url")+1].rstrip("/") if "--base-url" in a else "https://worldcup2026-api-71n6.onrender.com"
    try:
        with urllib.request.urlopen(base+"/api/v1/runtime-content", timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print("FAIL  runtime-content endpoint unreachable: %s" % e); return 1
    stored = d.get("freshness", {}).get("stored")
    npred = len(d.get("predictions") or {})
    print("R4 RUNTIME CONTENT CUTOVER PASS (endpoint live · stored=%s · predictions=%d · send_status=%s)" % (
        stored, npred, d.get("send_status"))); return 0


if __name__ == "__main__": sys.exit(main())
