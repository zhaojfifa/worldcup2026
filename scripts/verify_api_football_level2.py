#!/usr/bin/env python3
"""API-FOOTBALL Level-2 coverage verifier (operator-run, token-gated).

Probes the API-FOOTBALL endpoints that unlock Level-2 pre-match scout data
(lineups / events / statistics / fixture players / injuries / squad / coach) for
World Cup 2022 (league 1, season 2022) and World Cup 2026 (season 2026), resolves
fixture ids for the four test matches (8/13/58/67), and emits a verdict.

SAFETY:
- Token read from env (any of API_FOOTBALL_KEY / API_KEY / API_TOKEN / API_SPORTS_KEY),
  or a local gitignored .env. It is NEVER printed or committed; it never enters the JSON.
- With NO token: ZERO network calls, verdict = blocked_by_token (no fabrication).
- Read-only GETs. Stdlib only. Standalone ops script — not wired into the app.

Run:  API_FOOTBALL_KEY=... python scripts/verify_api_football_level2.py
Output: docs/data_audit/api_football_level2_coverage.json
"""
import json, os, urllib.request, urllib.error
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "docs/data_audit/api_football_level2_coverage.json")
TOKEN_VARS = ["API_FOOTBALL_KEY", "API_KEY", "API_TOKEN", "API_SPORTS_KEY"]
WC_LEAGUE = os.environ.get("WC_LEAGUE_ID", "1")

# Four test matches (unordered team pairs) → our Render match ids.
TEST_MATCHES = [
    ("Argentina", "Saudi Arabia", 8),
    ("Germany", "Japan", 13),
    ("Morocco", "Spain", 58),
    ("Argentina", "France", 67),
]
CORE_FIELDS = ["lineups", "events", "statistics", "players"]  # for the PASS rule

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def load_local_env():
    """Best-effort: pull token vars from a gitignored local .env if not already set.
    Only the recognized var names are imported; nothing is printed."""
    for fn in (os.path.join(REPO, "backend/.env"), os.path.join(REPO, ".env"),
               os.path.join(REPO, "backend/.env.local")):
        if not os.path.isfile(fn):
            continue
        try:
            with open(fn, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    k = k.strip()
                    if k in TOKEN_VARS + ["API_FOOTBALL_BASE_URL", "WC_LEAGUE_ID"] and not os.environ.get(k):
                        os.environ[k] = v.strip().strip('"').strip("'")
        except Exception:  # noqa: BLE001
            pass

def resolve_token():
    for v in TOKEN_VARS:
        val = os.environ.get(v, "").strip()
        if val:
            return val, v
    return "", None

def write(obj):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("WROTE", OUT)

def headers(base, key):
    if "rapidapi" in base:
        return {"x-rapidapi-key": key, "x-rapidapi-host": base.split("//")[-1].split("/")[0]}
    return {"x-apisports-key": key}

def get(base, key, endpoint, query=""):
    url = "%s%s%s" % (base, endpoint, ("?" + query if query else ""))
    req = urllib.request.Request(url, headers=headers(base, key))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, None
    except Exception as e:  # noqa: BLE001
        return None, {"_error": str(e)}

def summary(body):
    if not isinstance(body, dict):
        return None, None, []
    return body.get("results"), (body.get("errors") or None), (body.get("response") or [])

PLAN = [
    ("status", "/status", "", "account/plan"),
    ("leagues", "/leagues", "id=%s" % WC_LEAGUE, "World Cup league id/season"),
    ("fixtures2022", "/fixtures", "league=%s&season=2022" % WC_LEAGUE, "WC2022 fixtures"),
    ("fixtures2026", "/fixtures", "league=%s&season=2026" % WC_LEAGUE, "WC2026 fixtures"),
    ("lineups", "/fixtures/lineups", "fixture=<f>", "starting lineup / formation"),
    ("events", "/fixtures/events", "fixture=<f>", "match events"),
    ("statistics", "/fixtures/statistics", "fixture=<f>", "match statistics"),
    ("players", "/fixtures/players", "fixture=<f>", "per-match player stats"),
    ("injuries", "/injuries", "league=%s&season=2022" % WC_LEAGUE, "injuries / suspensions"),
    ("squad", "/players/squads", "team=<t>", "squad / player list"),
    ("coachs", "/coachs", "team=<t>", "coach"),
    ("teams", "/teams", "league=%s&season=2022" % WC_LEAGUE, "teams"),
]

def main():
    load_local_env()
    key, key_var = resolve_token()
    base = os.environ.get("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io").rstrip("/")

    if not key:
        write({
            "source": "api-football", "base_url": base, "checked_at": now_iso(),
            "status": "token_required", "verdict": "blocked_by_token",
            "verdict_reason": "no API-FOOTBALL token in env (%s) or local .env" % " / ".join(TOKEN_VARS),
            "token_var_used": None,
            "accepted_token_vars": TOKEN_VARS,
            "test_matches": [{"home": h, "away": a, "render_id": i, "fixture_id": None} for h, a, i in TEST_MATCHES],
            "planned_checks": [{"key": k, "endpoint": e, "query": q, "field": f} for k, e, q, f in PLAN],
            "note": "ZERO calls made. Operator sets one of the accepted token vars (paid plan) and re-runs. "
                    "Token never printed/committed.",
        })
        print("verdict=blocked_by_token (no token) — no calls made")
        return

    # --- probe (operator path, token present) ---
    # Resolve a WC2022 fixture id + team id, and the four test-match fixture ids.
    fixtures = []
    _, _, fixtures = summary(get(base, key, "/fixtures", "league=%s&season=2022" % WC_LEAGUE)[1] or {})
    def pair(a, b):
        return frozenset([a.lower(), b.lower()])
    test_ids = {}
    f_default = t_default = None
    for fx in fixtures:
        teams = fx.get("teams") or {}
        h = ((teams.get("home") or {}).get("name") or "")
        a = ((teams.get("away") or {}).get("name") or "")
        fid = (fx.get("fixture") or {}).get("id")
        if f_default is None:
            f_default = fid
            t_default = (teams.get("home") or {}).get("id")
        for th, ta, rid in TEST_MATCHES:
            if pair(h, a) == pair(th, ta):
                test_ids[rid] = fid
    probe_fixture = test_ids.get(8) or f_default

    checks = []
    formation_readable = False
    for k, endpoint, query, field in PLAN:
        if "<f>" in query and not probe_fixture:
            checks.append({"key": k, "field": field, "http_status": None, "results": None, "ok": False,
                           "note": "no WC2022 fixture id resolved (season likely not on plan)"})
            continue
        if "<t>" in query and not t_default:
            checks.append({"key": k, "field": field, "http_status": None, "results": None, "ok": False,
                           "note": "no WC2022 team id resolved"})
            continue
        q = query.replace("<f>", str(probe_fixture or "")).replace("<t>", str(t_default or ""))
        st, body = get(base, key, endpoint, q)
        results, errors, response = summary(body)
        ok = st == 200 and not errors and (results or 0) > 0
        if k == "lineups" and ok:
            formation_readable = any((r.get("formation") for r in response))
        checks.append({"key": k, "field": field, "http_status": st, "results": results, "ok": ok,
                       "errors": errors})

    cov = {c["key"]: c["ok"] for c in checks}
    wc2022_ok = cov.get("fixtures2022", False)
    core_ok = sum(1 for f in CORE_FIELDS if cov.get(f))
    mapped = any(test_ids.values())
    any_perm_error = any((c.get("errors") for c in checks))

    if not wc2022_ok and any_perm_error:
        verdict, reason = "blocked_by_plan", "WC2022 fixtures not returned and endpoints report plan/permission errors"
    elif core_ok >= 3 and mapped:
        verdict, reason = "pass", "%d/4 Level-2 core fields available and mapped to a WC2022 test match" % core_ok
    elif wc2022_ok and 0 < core_ok < 3:
        verdict, reason = "partial", "fixtures available but Level-2 core partially missing/plan-limited (%d/4 core)" % core_ok
    elif not wc2022_ok or core_ok == 0:
        verdict, reason = "fail", "WC2022 fixtures unreachable or Level-2 core basically unavailable"
    else:
        verdict, reason = "partial", "mixed coverage"

    write({
        "source": "api-football", "base_url": base, "checked_at": now_iso(),
        "status": "probed", "verdict": verdict, "verdict_reason": reason,
        "token_var_used": key_var,
        "wc2022_fixture_probed": probe_fixture, "wc2022_team_probed": t_default,
        "test_matches": [{"home": h, "away": a, "render_id": i, "fixture_id": test_ids.get(i)} for h, a, i in TEST_MATCHES],
        "formation_readable_from_lineups": formation_readable,
        "checks": checks,
        "coverage_summary": cov,
        "note": "Read-only probe. 'ok=false' usually means the season/endpoint is not on the current plan. "
                "Token never printed/committed.",
    })
    print("verdict=%s (%d/4 core, mapped=%s)" % (verdict, core_ok, mapped))

if __name__ == "__main__":
    main()
