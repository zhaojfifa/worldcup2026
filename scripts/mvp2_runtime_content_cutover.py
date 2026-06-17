#!/usr/bin/env python3
"""R4 — runtime CONTENT cutover (Owner GO 2026-06-16: daily cutover WITHOUT a frontend deploy).

Extends the R3 content-paired cutover: after the consistency gate passes, it uploads BOTH
  (a) the daily-fixtures slate manifest  -> POST /api/v1/admin/daily-fixtures/upload   (R2/R3, runtime slate)
  (b) the daily CONTENT package          -> POST /api/v1/admin/runtime-content/upload  (R4, runtime content)
so the LIVE frontend (runtime-first) renders the new date's prediction/recap/selectedHotspot content
without a rebuild/deploy. Bundled artifacts stay as the fallback.

The CONTENT package is assembled from the SAME gate-verified artifacts the bundle uses
(selectedHotspot + homepageLifecycle + the selected primary/secondary prediction artifacts + the
selected recap observation artifact). Nothing is invented. send_status stays HOLD; no auto-send.

Flow (--date D, editorial --now optional):
  1. sync slate (R2 source) + build lifecycle for D  (R3 chain; snapshot/restore on block)
  2. HARD GATE (check_r3_day_cutover_consistency.gate)
  3. PASS -> assemble content package -> upload slate + content (only with --target) ; HOLD
     FAIL -> restore bundled artifacts, write CUTOVER_BLOCKED, no upload, production stays green

Token from $ADMIN_API_TOKEN (never printed). Usage:
  python3 scripts/mvp2_runtime_content_cutover.py --date 2026-06-15 --source manual --now 2026-06-15T12:00:00+00:00 --target production
  python3 scripts/mvp2_runtime_content_cutover.py --date 2026-06-16 --source api-football --target production
"""
import argparse, importlib.util, json, os, pathlib, sys, urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE = ROOT / "frontend/src/data"
PUB = ROOT / "frontend/public/data"
PRED = FE / "predictionArtifacts"
SYNC = ROOT / "docs/data_audit/mvp2_match_sync"
CUT_DIR = ROOT / "docs/data_audit/mvp2_runtime_content_cutover"
SNAPSHOT = [FE / "dailyFixtures.generated.json", PUB / "daily-fixtures.json", FE / "homepageLifecycle.json",
            FE / "selectedHotspot.json", FE / "dailyContentQueue.json"]
BACKENDS = {"production": "https://worldcup2026-api-71n6.onrender.com", "local": "http://127.0.0.1:8011"}


def _imp(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


def _load(p):
    p = pathlib.Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _snapshot(): return {p: (p.read_bytes() if p.exists() else None) for p in SNAPSHOT}
def _restore(s):
    for p, b in s.items():
        if b is None and p.exists(): p.unlink()
        elif b is not None: p.write_text(b.decode("utf-8"), encoding="utf-8")


def _find_pred(key):
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (str(a.get("fixture_key")) == str(key) or str(a.get("id")) == str(key)):
            return a
    return None


def _find_obs(key):
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a and (str(a.get("id")) == str(key) or str(a.get("fixture_key")) == str(key)):
            return a
    return None


def assemble_package(date_iso, source):
    """Build the runtime CONTENT package from the gate-verified bundled artifacts (no invention)."""
    sel = _load(FE / "selectedHotspot.json") or {}
    lc = _load(FE / "homepageLifecycle.json") or {}
    queue = _load(FE / "dailyContentQueue.json") or {}
    preds, obs = {}, {}
    keys = []
    if sel.get("fixture_key"):
        keys.append(str(sel["fixture_key"]))
    keys += [str(s.get("fixture_id")) for s in (lc.get("secondary_predictions") or []) if s.get("fixture_id")]
    keys += [str(s.get("fixture_key") or s.get("id")) for s in (queue.get("secondary_matches") or [])]
    for k in dict.fromkeys([k for k in keys if k]):
        a = _find_pred(k)
        if a:
            preds[k] = a
    rk = str((lc.get("latest_recap") or {}).get("fixture_id") or "")
    if rk:
        o = _find_obs(rk)
        if o:
            obs[rk] = o
    return {"date": date_iso, "generated_at": (lc.get("current_time_basis") or datetime.now(timezone.utc).isoformat()),
            "source_mode": source, "send_status": "HOLD",
            "selectedHotspot": sel, "lifecycle": lc, "predictions": preds, "observations": obs}


def _post(base, path, body, token):
    req = urllib.request.Request(base + path, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 method="POST", headers={"Content-Type": "application/json", "x-admin-token": token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def run(date_iso, source, target, now_iso, do_upload):
    CUT_DIR.mkdir(parents=True, exist_ok=True)
    ms = _imp("mvp2_match_sync", ROOT / "scripts" / "mvp2_match_sync.py")
    lcsel = _imp("lcsel", ROOT / "scripts" / "mvp2_homepage_lifecycle_selector.py")
    r3 = _imp("r3gate", ROOT / "scripts" / "check_r3_day_cutover_consistency.py")
    snap = _snapshot()
    print("== R4 runtime-content cutover %s · source=%s · target=%s%s ==" % (
        date_iso, source, target or "(gate only)", (" · basis=%s" % now_iso) if now_iso else ""))
    now_dt = datetime.fromisoformat(now_iso) if now_iso else None
    ms.cmd_sync(date_iso, source, now=now_dt)
    try:
        lcsel.cmd_build(date_iso, now_iso, write_fe=True)
    except Exception as e:
        print("lifecycle build note: %s" % e)
    ok, fails = r3.gate(date_iso)
    if not ok:
        _restore(snap)
        rep = {"date": date_iso, "result": "CUTOVER_BLOCKED", "send_status": "HOLD", "uploaded": False, "reasons": fails}
        (CUT_DIR / ("%s_blocked.json" % date_iso.replace("-", ""))).write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("\nCUTOVER_BLOCKED — %d gate failure(s):" % len(fails))
        for x in fails: print("  - %s" % x)
        print("bundled artifacts RESTORED (no frontend change). SEND_STATUS=HOLD")
        return 2
    pkg = assemble_package(date_iso, source)
    pkg_path = CUT_DIR / ("%s_content_package.json" % date_iso.replace("-", ""))
    pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nGATE PASS — content package: %d prediction(s), %d observation(s) -> %s" % (
        len(pkg["predictions"]), len(pkg["observations"]), pkg_path.relative_to(ROOT)))
    # R6.1 — PRE-UPLOAD customer-visible guard: never upload a package whose customer copy carries
    # engineering/de-model wording, betting vocabulary, or a fabricated probability/confidence.
    cvg = _imp("r6cv", ROOT / "scripts" / "check_r6_runtime_preupload_customer_visible_guard.py")
    cv_violations = cvg.scan_package(pkg)
    if cv_violations:
        _restore(snap)
        rep = {"date": date_iso, "result": "CUTOVER_BLOCKED_CUSTOMER_VISIBLE", "send_status": "HOLD",
               "uploaded": False, "violations": [{"field": fp, "reason": r} for fp, r in cv_violations]}
        (CUT_DIR / ("%s_blocked_customer_visible.json" % date_iso.replace("-", ""))).write_text(
            json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("\nCUTOVER_BLOCKED_CUSTOMER_VISIBLE — %d violation(s) (NOTHING uploaded; production unchanged):" % len(cv_violations))
        for fp, r in cv_violations:
            print("  - %s — %s" % (fp, r))
        print("bundled artifacts RESTORED. SEND_STATUS=HOLD")
        return 4
    if do_upload and target:
        token = os.environ.get("ADMIN_API_TOKEN")
        if not token:
            print("ADMIN_API_TOKEN not set — cannot upload (engineering holds no prod token)"); return 3
        base = BACKENDS.get(target) or target
        slate = _load(SYNC / ("daily_fixtures_%s.json" % date_iso.replace("-", "")))
        print("slate  upload -> %s" % _post(base, "/api/v1/admin/daily-fixtures/upload", slate, token))
        print("content upload -> %s" % _post(base, "/api/v1/admin/runtime-content/upload", pkg, token))
        result = "CUTOVER_UPLOADED_RUNTIME_CONTENT"
    else:
        result = "GATE_PASS_NO_UPLOAD"
        print("(no --target -> gate only; nothing uploaded)")
    (CUT_DIR / ("%s_cutover.json" % date_iso.replace("-", ""))).write_text(
        json.dumps({"date": date_iso, "result": result, "send_status": "HOLD",
                    "uploaded": bool(do_upload and target), "predictions": len(pkg["predictions"]),
                    "observations": len(pkg["observations"])}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("SEND_STATUS=HOLD")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=None)
    ap.add_argument("--source", default="api-football", choices=["api-football", "manual", "fetched"])
    ap.add_argument("--target", default=None, help="production|local|<url> — REQUIRED to upload")
    ap.add_argument("--now", default=None)
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        r3 = _imp("r3gate", ROOT / "scripts" / "check_r3_day_cutover_consistency.py")
        return r3.selftest()
    date_iso = a.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return run(date_iso, a.source, a.target, a.now, bool(a.target) or a.upload)


if __name__ == "__main__":
    sys.exit(main())
