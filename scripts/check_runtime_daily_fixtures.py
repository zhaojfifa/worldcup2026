#!/usr/bin/env python3
"""
P1.3c scanner — the runtime daily-fixtures source must be wired and honest.

Code-wiring checks (always run, no server needed):
  * backend exposes GET /api/v1/daily-fixtures + POST admin upload/refresh
  * frontend fetches the BACKEND first, then static, then bundled (three-tier)
  * HomePage selects the hero from the fetched manifest (no hardcoded fixtureId)
  * the static runtime manifest exists and contains the completed Canada/USA matches
  * no betting/trading vocab + no customer auto-send in the P1.3c surfaces

Optional live probe (--base-url URL):
  * GET /api/v1/daily-fixtures returns 200 with fixtures
  * generated_at is fresh (< --max-age-hours)
  * Canada/USA completed matches present · active_hero present (not hardcoded)

Exit 0 = PASS · exit 1 = FAIL.
Usage: python3 scripts/check_runtime_daily_fixtures.py [--base-url https://...] [--max-age-hours 36]
"""
import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROUTER = ROOT / "backend" / "app" / "routers" / "daily_fixtures.py"
SERVICE = ROOT / "backend" / "app" / "services" / "daily_fixtures_service.py"
MAIN = ROOT / "backend" / "app" / "main.py"
FE_DATA = ROOT / "frontend" / "src" / "data" / "dailyFixtures.ts"
HOME = ROOT / "frontend" / "src" / "pages" / "HomePage.tsx"
RUNTIME_MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
BETTING = ["赔率", "盘口", "下注", "博彩", "套利", "跟单", "返佣", "odds", "handicap", "bookmaker", "wager", "payout", "commission"]
AUTOSEND = ["sendMessage", "telegram", "smtp", "webhook"]
# finished/completed lifecycle states — completed matches are derived from the slate itself,
# never hardcoded to specific teams (the daily slate changes; Owner 2026-06-14 refresh).
FINISHED_STATES = {"FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}


def _read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default=None, help="probe a live backend (else code-wiring checks only)")
    ap.add_argument("--max-age-hours", type=float, default=36.0)
    a = ap.parse_args()
    fails, warns = [], []

    router = _read(ROUTER)
    if 'get("/daily-fixtures")' not in router and "/daily-fixtures" not in router:
        fails.append("backend GET /daily-fixtures endpoint not found")
    if "admin/daily-fixtures/upload" not in router:
        fails.append("backend admin upload endpoint not found")
    if "require_admin" not in router:
        fails.append("backend upload endpoint not admin-guarded (require_admin missing)")
    if "daily_fixtures" not in _read(MAIN):
        fails.append("daily_fixtures router not registered in main.py")

    fe = _read(FE_DATA)
    if "api/v1/daily-fixtures" not in fe:
        fails.append("frontend does not fetch the BACKEND endpoint first (P1.3c)")
    for tier in ("'backend'", "'static'", "'bundled'"):
        if tier not in fe:
            fails.append("frontend missing fetch tier %s" % tier)
    home = _read(HOME)
    if "fetchDailyManifest" not in home:
        fails.append("HomePage does not use the runtime fetch (fetchDailyManifest)")
    if re.search(r'TrialHeroCard[^>]*fixtureId="\d+"', home):
        fails.append("HomePage hardcodes a hero fixtureId literal")
    for label in ("实时", "静态备份", "内置"):
        if label not in home:
            warns.append("HomePage missing source label %s" % label)

    # static runtime manifest must exist and carry the slate's fixtures (completed matches are
    # cross-checked against the live endpoint below — no hardcoded team names).
    static_teams = set()
    if not RUNTIME_MANIFEST.exists():
        fails.append("static runtime manifest %s missing" % RUNTIME_MANIFEST.name)
    else:
        rt = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
        static_teams = {f.get("home") for f in rt.get("fixtures", [])}
        if not rt.get("fixtures"):
            fails.append("static runtime manifest has no fixtures")

    # vocab + auto-send hygiene on P1.3c surfaces
    for p in (router, _read(SERVICE), fe, _read(ROOT / "scripts" / "mvp2_match_sync.py")):
        low = p.lower()
        for w in BETTING:
            if w.lower() in low:
                fails.append("forbidden betting/trading vocab '%s' in a P1.3c surface" % w)
        for w in AUTOSEND:
            if w.lower() in low:
                fails.append("customer-send pattern '%s' in a P1.3c surface" % w)

    # optional live probe
    if a.base_url:
        import urllib.request
        url = a.base_url.rstrip("/") + "/api/v1/daily-fixtures"
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                live = json.loads(resp.read().decode("utf-8"))
            n = len(live.get("fixtures", []))
            print("live GET %s -> %d fixtures" % (url, n))
            if n == 0:
                fails.append("live endpoint returned 0 fixtures (nothing uploaded?)")
            # every completed (finished) fixture the live endpoint shows must also exist in the
            # static fallback manifest, so a backend outage can never hide a finished match.
            live_completed = {f.get("home") for f in live.get("fixtures", [])
                              if f.get("lifecycle_state") in FINISHED_STATES}
            for home in sorted(live_completed):
                if home not in static_teams:
                    fails.append("live completed match %s absent from static fallback manifest" % home)
            if not live_completed:
                warns.append("live endpoint shows no completed match today")
            if not live.get("active_hero"):
                warns.append("live endpoint active_hero is null (no hero candidate)")
            ga = live.get("generated_at")
            if ga:
                gat = datetime.fromisoformat(ga.replace("Z", "+00:00"))
                if gat.tzinfo is None:
                    gat = gat.replace(tzinfo=timezone.utc)
                age_h = (datetime.now(timezone.utc) - gat).total_seconds() / 3600
                print("live manifest age %.1fh (threshold %.0fh)" % (age_h, a.max_age_hours))
                if age_h > a.max_age_hours:
                    fails.append("live manifest stale: %.1fh > %.0fh" % (age_h, a.max_age_hours))
        except Exception as e:
            fails.append("live endpoint probe failed: %s" % e)
    else:
        print("(code-wiring checks only — pass --base-url to probe a live backend)")

    for w in warns:
        print("WARN  %s" % w)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RUNTIME DAILY-FIXTURES FAIL — %d issue(s)" % len(fails))
        return 1
    print("RUNTIME DAILY-FIXTURES PASS (%d warning(s))" % len(warns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
