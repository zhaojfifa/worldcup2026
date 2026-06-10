#!/usr/bin/env python3
"""API-FOOTBALL Level-2 coverage verifier (operator-run, token-gated).

Probes the API-FOOTBALL endpoints that would unlock Level-2 pre-match scout data
(lineups / events / players / injuries / squads / coachs) for World Cup 2022
(league 1, season 2022) and World Cup 2026 (league 1, season 2026), and writes a
coverage report.

SAFETY:
- Reads the token from env ($API_FOOTBALL_KEY); it is NEVER printed or committed.
- With NO token, makes ZERO network calls and writes status=token_required.
- Read-only GETs only. Stdlib only (urllib/json) — no deps, no backend/DB wiring.

Run:  API_FOOTBALL_KEY=... python scripts/verify_api_football_level2.py
Output: docs/data_audit/api_football_level2_coverage.json
"""
import json, os, urllib.request, urllib.error
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "docs/data_audit/api_football_level2_coverage.json")
BASE = os.environ.get("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io").rstrip("/")
KEY = os.environ.get("API_FOOTBALL_KEY", "").strip()
WC_LEAGUE = os.environ.get("WC_LEAGUE_ID", "1")

# (endpoint, query, level2_field) — fixture/team-dependent ones are filled at runtime.
PLANNED = [
    ("/status", "", "account/plan"),
    ("/leagues", "id=%s" % WC_LEAGUE, "competition"),
    ("/fixtures", "league=%s&season=2022" % WC_LEAGUE, "WC2022 fixtures/results"),
    ("/fixtures", "league=%s&season=2026" % WC_LEAGUE, "WC2026 fixtures"),
    ("/fixtures/lineups", "fixture=<wc2022_fixture>", "starting lineup / formation"),
    ("/fixtures/events", "fixture=<wc2022_fixture>", "match events"),
    ("/fixtures/players", "fixture=<wc2022_fixture>", "per-match player stats"),
    ("/injuries", "league=%s&season=2022" % WC_LEAGUE, "injuries / suspensions"),
    ("/players/squads", "team=<wc2022_team>", "squad / player list"),
    ("/coachs", "team=<wc2022_team>", "coach"),
    ("/teams", "league=%s&season=2022" % WC_LEAGUE, "teams"),
]

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def write(obj):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("WROTE", OUT)

def headers():
    if "rapidapi" in BASE:
        host = BASE.split("//")[-1].split("/")[0]
        return {"x-rapidapi-key": KEY, "x-rapidapi-host": host}
    return {"x-apisports-key": KEY}

def get(endpoint, query=""):
    url = "%s%s%s" % (BASE, endpoint, ("?" + query if query else ""))
    req = urllib.request.Request(url, headers=headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read().decode())
            return r.status, body
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, None
    except Exception as e:  # noqa: BLE001
        return None, {"error": str(e)}

def summarize(body):
    """API-FOOTBALL wraps payload as {results: N, errors: {...}, response: [...]}."""
    if not isinstance(body, dict):
        return None, None
    return body.get("results"), (body.get("errors") or None)

def main():
    if not KEY:
        write({
            "source": "api-football", "base_url": BASE, "checked_at": now_iso(),
            "status": "token_required",
            "expected_env": ["API_FOOTBALL_KEY", "API_FOOTBALL_BASE_URL (optional)", "WC_LEAGUE_ID (optional)"],
            "planned_checks": [{"endpoint": e, "query": q, "level2_field": f} for e, q, f in PLANNED],
            "note": "No token in env → ZERO calls made. Operator sets $API_FOOTBALL_KEY (paid plan) and re-runs. "
                    "Token is never printed or committed.",
        })
        print("status=token_required (no $API_FOOTBALL_KEY) — no calls made")
        return

    checks = []
    # Resolve a WC2022 fixture id + team id for the fixture/team-dependent probes.
    wc_fixture, wc_team = None, None
    st, body = get("/fixtures", "league=%s&season=2022" % WC_LEAGUE)
    if isinstance(body, dict) and body.get("response"):
        first = body["response"][0]
        wc_fixture = (first.get("fixture") or {}).get("id")
        wc_team = ((first.get("teams") or {}).get("home") or {}).get("id")

    for endpoint, query, field in PLANNED:
        q = query.replace("<wc2022_fixture>", str(wc_fixture or "")).replace("<wc2022_team>", str(wc_team or ""))
        if "<wc2022" in query and ("=" + "" in q or q.endswith("=") or q.endswith("=None") or not (wc_fixture or wc_team)):
            checks.append({"endpoint": endpoint, "query": query, "level2_field": field,
                           "http_status": None, "results": None, "ok": False,
                           "note": "skipped — no WC2022 fixture/team id resolved (season not covered on this plan?)"})
            continue
        status, b = get(endpoint, q)
        results, errors = summarize(b)
        checks.append({"endpoint": endpoint, "query": q, "level2_field": field,
                       "http_status": status, "results": results,
                       "ok": status == 200 and not errors and (results or 0) > 0,
                       "errors": errors})

    by_field = {c["level2_field"]: ("covered" if c["ok"] else "missing/blocked") for c in checks}
    write({
        "source": "api-football", "base_url": BASE, "checked_at": now_iso(),
        "status": "probed",
        "wc2022_fixture_probed": wc_fixture, "wc2022_team_probed": wc_team,
        "checks": checks,
        "coverage_summary": by_field,
        "note": "Read-only probe. 'missing/blocked' usually means the season/endpoint is not on the current plan. "
                "Token never printed/committed.",
    })
    covered = sum(1 for c in checks if c["ok"])
    print("status=probed — %d/%d endpoints returned data" % (covered, len(checks)))

if __name__ == "__main__":
    main()
