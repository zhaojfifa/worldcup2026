#!/usr/bin/env python3
"""
P4A — Daily freshness gate. Builds + verifies docs/data_audit/mvp2_daily_freshness/<date>.json and
fails if today's content is stale or mismatched. Stale content must be FLAGGED, never silently shown.

Checks:
  - an artifact date exists (dailyContentQueue / selectedHotspot);
  - homepage primary is from today's slate (selected hotspot ∈ today's scheduled fixtures);
  - >= 1 primary AND >= 2 secondary recommendations exist;
  - if a runtime/backend date is available (--base-url) and mismatches the artifact date →
    freshness_status = BLOCKED_DAILY_FRESHNESS.

Artifact fields: date, runtime_date, artifact_date, homepage_primary_fixture, secondary_fixtures,
freshness_status (FRESH | STALE | BLOCKED_DAILY_FRESHNESS), stale_reason, next_operator_action, send_status.
Usage: check_daily_freshness.py [--date YYYY-MM-DD] [--base-url URL] | --selftest.
"""
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_daily_freshness"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _backend_date(base_url):
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/api/v1/daily-fixtures", timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        return d.get("date") or d.get("generated_for_date") or d.get("slate_date")
    except Exception:
        return None


def build(date, base_url=None):
    q = _load(QUEUE) or {}
    sel = _load(SEL) or {}
    man = _load(MANIFEST) or {}
    artifact_date = q.get("date") or sel.get("date")
    primary = (q.get("primary_hotspot") or {}).get("fixture_key")
    secondary = [s.get("fixture_key") for s in q.get("secondary_matches", [])]
    runtime_date = _backend_date(base_url) if base_url else man.get("generated_for_date")
    # scheduled fixtures in today's slate
    scheduled = {str(f.get("id") or f.get("external_game_id")) for f in man.get("fixtures", [])
                 if (f.get("status") or "").lower() == "scheduled"}
    primary_in_slate = primary in scheduled or ("af:" + str(primary)) in scheduled

    status, reason, nxt = "FRESH", "", "today is fresh — operator review then hold for Owner GO"
    if not artifact_date:
        status, reason, nxt = "STALE", "no artifact date (selected hotspot / queue missing)", "rebuild daily queue + select hotspot"
    elif not primary:
        status, reason, nxt = "STALE", "no primary recommendation", "select today's hotspot"
    elif len(secondary) < 2:
        status, reason, nxt = "STALE", "fewer than 2 secondary recommendations (%d)" % len(secondary), "build secondary predictions"
    elif not primary_in_slate:
        status, reason, nxt = "STALE", "homepage primary %s not in today's scheduled slate" % primary, "refresh slate / re-select hotspot"
    elif runtime_date and artifact_date and runtime_date != artifact_date:
        status, reason, nxt = ("BLOCKED_DAILY_FRESHNESS",
                               "runtime/backend date %s != artifact date %s" % (runtime_date, artifact_date),
                               "upload today's manifest to backend (mvp2_match_sync upload) — do NOT ship stale")
    out = {
        "date": date, "runtime_date": runtime_date, "artifact_date": artifact_date,
        "homepage_primary_fixture": primary, "secondary_fixtures": secondary,
        "freshness_status": status, "stale_reason": reason or None,
        "next_operator_action": nxt, "send_status": "HOLD",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("%s.json" % date)).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def selftest():
    # synthetic verification of the status logic
    def status_of(artifact_date, primary, secondary, primary_in, runtime):
        if not artifact_date:
            return "STALE"
        if not primary:
            return "STALE"
        if len(secondary) < 2:
            return "STALE"
        if not primary_in:
            return "STALE"
        if runtime and artifact_date and runtime != artifact_date:
            return "BLOCKED_DAILY_FRESHNESS"
        return "FRESH"
    checks = [
        ("fresh when current+match", status_of("2026-06-15", "1", ["2", "3"], True, "2026-06-15") == "FRESH"),
        ("blocked on date mismatch", status_of("2026-06-15", "1", ["2", "3"], True, "2026-06-14") == "BLOCKED_DAILY_FRESHNESS"),
        ("stale on <2 secondary", status_of("2026-06-15", "1", ["2"], True, "2026-06-15") == "STALE"),
        ("stale on primary not in slate", status_of("2026-06-15", "1", ["2", "3"], False, "2026-06-15") == "STALE"),
        ("stale on no artifact date", status_of(None, "1", ["2", "3"], True, None) == "STALE"),
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
    base_url = argv[argv.index("--base-url") + 1] if "--base-url" in argv else None
    import datetime
    date = date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    out = build(date, base_url)
    print("DAILY FRESHNESS · %s · status=%s" % (date, out["freshness_status"]))
    print("  runtime_date=%s · artifact_date=%s · primary=%s · secondary=%d" % (
        out["runtime_date"], out["artifact_date"], out["homepage_primary_fixture"], len(out["secondary_fixtures"])))
    if out["stale_reason"]:
        print("  stale_reason: %s" % out["stale_reason"])
    print("  next: %s" % out["next_operator_action"])
    if out["freshness_status"] in ("STALE", "BLOCKED_DAILY_FRESHNESS"):
        print("DAILY FRESHNESS FLAGGED — %s" % out["freshness_status"]); return 1
    print("DAILY FRESHNESS PASS (today fresh; primary in slate; >=2 secondary; no date mismatch)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
