#!/usr/bin/env python3
"""
P1.3 — Match Sync & Daily Fixture Registry (Owner verdict 2026-06-13).

The lifecycle gate (P1.2/P1.2b) can only protect fixtures it KNOWS about. This sync
discovers the daily slate — today's scheduled / live / finished matches with real final
scores — and writes a daily fixture registry + a recap queue + a frontend-safe active
manifest, each fixture run through the canonical lifecycle. Nothing here sends anything,
fabricates a score, or invents a fixture.

Source modes:
  manual  (default, P1.3) — parse docs/data_audit/mvp2_match_sync/manual_scores_<date>.md
  fetched (--source fetched) — best-effort API-FOOTBALL by date; fills kickoff/status/score
                               for fixtures it can match; never overwrites a confirmed manual
                               score with a different value (records a conflict instead).

Usage:
  python3 scripts/mvp2_match_sync.py sync --date 2026-06-13 [--source manual|fetched]
  python3 scripts/mvp2_match_sync.py --selftest

Writes:
  docs/data_audit/mvp2_match_sync/daily_fixtures_YYYYMMDD.json
  docs/data_audit/mvp2_match_sync/recap_queue_YYYYMMDD.json
  frontend/src/data/dailyFixtures.generated.json   (active manifest for the homepage hero)
"""
import argparse
import importlib.util
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC_DIR = ROOT / "docs" / "data_audit" / "mvp2_match_sync"
FE_NARR = ROOT / "frontend" / "src" / "data" / "productNarratives"
FE_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"   # P1.3 build-time fallback
FE_RUNTIME = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"          # P1.3b runtime source (fetched)

_LC = None


def _lc():
    global _LC
    if _LC is None:
        spec = importlib.util.spec_from_file_location(
            "mvp2_fixture_lifecycle", ROOT / "scripts" / "mvp2_fixture_lifecycle.py")
        _LC = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_LC)
    return _LC


# ── known fixtures: internal id ↔ teams ↔ kickoff (engineering facts already ingested) ──
# Only fixtures we have actually verified carry an internal id / kickoff / flags. Unmapped
# fixtures get internal_fixture_id=null and a manual external slug — never a faked id.
KNOWN = {
    ("canada", "bosnia and herzegovina"): {
        "internal": "1539000", "kickoff": "2026-06-12T19:00:00+00:00",
        "flag_home": "🇨🇦", "flag_away": "🇧🇦", "group": "Group Stage · 1"},
    ("mexico", "south africa"): {
        "internal": "1489369", "kickoff": "2026-06-11T19:00:00+00:00",
        "flag_home": "🇲🇽", "flag_away": "🇿🇦", "group": "Group Stage · 1"},
    ("brazil", "morocco"): {
        "internal": "1489371", "kickoff": "2026-06-13T22:00:00+00:00",
        "flag_home": "🇧🇷", "flag_away": "🇲🇦", "group": "Group Stage · 1"},
}
# team-name aliases -> canonical lower-case key used above
ALIASES = {
    "bosnia": "bosnia and herzegovina", "bosnia & herzegovina": "bosnia and herzegovina",
    "usa": "united states", "us": "united states", "south korea": "south korea",
    "korea republic": "south korea", "czechia": "czechia", "czech republic": "czechia",
}


def _canon(name):
    n = name.strip().lower()
    return ALIASES.get(n, n)


def parse_manual(date_compact):
    """Parse manual_scores_<date>.md -> list of raw fixture dicts. No score invention:
    only scores explicitly written are recorded; 'vs' lines carry no score."""
    p = SYNC_DIR / ("manual_scores_%s.md" % date_compact)
    if not p.exists():
        raise SystemExit("manual scores file not found: %s" % p.relative_to(ROOT))
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ">", "<!--", "-->")):
            continue
        # finished with score:  "Home 1-1 Away — finished"
        m = re.match(r"^(.*?)\s+(\d+)\s*[-–]\s*(\d+)\s+(.*?)\s+[—-]+\s*(\w+)\s*$", line)
        if m:
            out.append({"home": m.group(1).strip(), "away": m.group(4).strip(),
                        "score_home": int(m.group(2)), "score_away": int(m.group(3)),
                        "status": m.group(5).strip().lower()})
            continue
        # no score:  "Home vs Away — scheduled|unknown"
        m = re.match(r"^(.*?)\s+vs\.?\s+(.*?)\s+[—-]+\s*(\w+)\s*$", line, re.I)
        if m:
            out.append({"home": m.group(1).strip(), "away": m.group(2).strip(),
                        "score_home": None, "score_away": None,
                        "status": m.group(3).strip().lower()})
    return out


def _api_short_for(status, score_home):
    """Map a manual/registry status word to an API-FOOTBALL-style short for lifecycle."""
    s = (status or "").lower()
    if s == "finished":
        return "FT"
    if s == "live":
        return "2H"
    if s in ("postponed", "cancelled", "canceled"):
        return "PST" if s == "postponed" else "CANC"
    return None  # scheduled / unknown -> drive by time/kickoff


def _recap_ready(internal):
    if not internal:
        return False
    p = FE_NARR / ("%s.zh-CN.json" % internal)
    if not p.exists():
        return False
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("mode") == "real_recap"
    except Exception:
        return False


def _renderable(internal):
    """Has ANY bundled frontend narrative (pre-match or recap) -> can back a customer surface."""
    return bool(internal) and any((FE_NARR / ("%s.%s.json" % (internal, l))).exists()
                                  for l in ("zh-CN", "vi-VN", "my-MM"))


def evaluate(raw, now, captured_at, source_mode, source_name, source_note):
    lc = _lc()
    hk = (_canon(raw["home"]), _canon(raw["away"]))
    known = KNOWN.get(hk, {})
    internal = known.get("internal")
    kickoff_raw = known.get("kickoff")
    kickoff = None
    if kickoff_raw:
        kickoff = datetime.fromisoformat(kickoff_raw)
    recap_ready = _recap_ready(internal)
    api_short = _api_short_for(raw["status"], raw["score_home"])
    state, reason = lc.decide(now, kickoff, api_short=api_short, recap_ready=recap_ready)
    halted = api_short in lc.HALTED_SHORT
    g = lc.gates(state, halted=halted)
    renderable = _renderable(internal)
    external = ("af:%s" % internal) if internal else ("manual:%s-%s-%s" % (
        re.sub(r"\W+", "", raw["home"])[:6], re.sub(r"\W+", "", raw["away"])[:6], captured_at[:10].replace("-", "")))
    return {
        "external_game_id": external,
        "internal_fixture_id": internal,
        "home_team": raw["home"],
        "away_team": raw["away"],
        "group": known.get("group"),
        "kickoff_time_utc": kickoff_raw,
        "status": raw["status"] if raw["status"] in
                  ("scheduled", "live", "finished", "postponed", "cancelled", "unknown") else "unknown",
        "score_home": raw["score_home"],
        "score_away": raw["score_away"],
        "source_name": source_name,
        "source_url": None,
        "source_note": source_note,
        "source_mode": source_mode,
        "captured_at": captured_at,
        "lifecycle_state": state,
        "pre_match_allowed": g["pre_match_allowed"],
        "recap_needed": g["recap_needed"] or (raw["status"] == "finished" and not recap_ready),
        "recap_ready": recap_ready,
        "package_today_allowed": g["today_package_allowed"],
        "narrative_renderable": renderable,
        "hero_candidate": False,   # filled by select_candidates
        "recap_candidate": False,
        "next_candidate": False,
        "reason": reason,
    }


def select_candidates(fixtures):
    """Owner §5 priority. hero/recap/next flags are set on the registry rows in place."""
    def ts(f):
        return f["kickoff_time_utc"] or ""
    # hero: 1 live → 2 earliest scheduled pre-match (renderable) → 3 latest recap-ready → 4 latest recap-pending
    live = [f for f in fixtures if f["lifecycle_state"] == "LIVE" and f["narrative_renderable"]]
    pre = sorted([f for f in fixtures if f["pre_match_allowed"] and f["narrative_renderable"]], key=ts)
    ready = sorted([f for f in fixtures if f["recap_ready"] and f["narrative_renderable"]], key=ts, reverse=True)
    pend = sorted([f for f in fixtures if f["recap_needed"] and not f["recap_ready"]], key=ts, reverse=True)
    hero = (live[:1] or pre[:1] or ready[:1] or pend[:1])
    for f in hero:
        f["hero_candidate"] = True
    # next: earliest scheduled that is NOT the hero
    nxt = [f for f in pre if not f["hero_candidate"]]
    if nxt:
        nxt[0]["next_candidate"] = True
    # recap candidates: every finished fixture needing a recap
    for f in fixtures:
        if f["recap_needed"]:
            f["recap_candidate"] = True
    return fixtures


def build_recap_queue(fixtures, date_iso):
    items = []
    for f in fixtures:
        if not f["recap_needed"] and not f["recap_ready"]:
            continue
        score = None
        if f["score_home"] is not None:
            score = "%s-%s" % (f["score_home"], f["score_away"])
        items.append({
            "fixture": "%s vs %s" % (f["home_team"], f["away_team"]),
            "internal_fixture_id": f["internal_fixture_id"],
            "final_score": score,
            "recap_needed": f["recap_needed"] and not f["recap_ready"],
            "recap_ready": f["recap_ready"],
            "priority": 1 if (f["recap_needed"] and not f["recap_ready"] and f["narrative_renderable"]) else
                        2 if f["recap_needed"] and not f["recap_ready"] else 3,
            "operator_next_step": ("recap published" if f["recap_ready"]
                                   else "generate recap (A4) before any recap package/send"),
            "reason": f["reason"],
        })
    items.sort(key=lambda x: x["priority"])
    return {"date": date_iso, "generated_at": None, "items": items}


def write_frontend_manifest(fixtures, date_iso, stamp, source_mode):
    """Frontend daily-fixtures manifest (Owner §5 / P1.3b §runtime). The FULL slate is exposed
    so the runtime frontend KNOWS about completed matches (recap_needed/pending/ready), but only
    `renderable` fixtures (those with a bundled narrative) are hero-eligible. Written to BOTH:
      - frontend/src/data/dailyFixtures.generated.json  (build-time fallback import)
      - frontend/public/data/daily-fixtures.json        (P1.3b runtime fetch source)
    """
    rows = [{
        "id": f["internal_fixture_id"],
        "external_game_id": f["external_game_id"],
        "home": f["home_team"], "away": f["away_team"],
        "kickoffUtc": f["kickoff_time_utc"],
        "status": f["status"],
        "lifecycle_state": f["lifecycle_state"],
        "preMatchAllowed": f["pre_match_allowed"],
        "recapReady": f["recap_ready"],
        "recapNeeded": f["recap_needed"],
        "renderable": f["narrative_renderable"],
        "heroCandidate": f["hero_candidate"],
        "recapCandidate": f["recap_candidate"],
        "nextCandidate": f["next_candidate"],
        "scoreHome": f["score_home"],
        "scoreAway": f["score_away"],
    } for f in fixtures]
    doc = {"generated_for_date": date_iso, "generated_at": stamp,
           "source_mode": source_mode, "fixture_count": len(rows), "fixtures": rows}
    body = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    FE_MANIFEST.write_text(body, encoding="utf-8")
    FE_RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    FE_RUNTIME.write_text(body, encoding="utf-8")
    return doc


def cmd_sync(date_iso, source, now=None, stamp=None):
    now = now or datetime.now(timezone.utc)
    stamp = stamp or now.isoformat()
    compact = date_iso.replace("-", "")
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    raws = parse_manual(compact)
    source_name = "manual operator input (manual_scores_%s.md)" % compact
    source_note = "Owner/operator-provided slate; no score invented; unconfirmed = unknown"
    fixtures = [evaluate(r, now, stamp, "manual", source_name, source_note) for r in raws]

    if source == "fetched":
        _enrich_fetched(fixtures, date_iso, now)

    select_candidates(fixtures)
    doc = {"date": date_iso, "generated_at": stamp, "source_mode": source,
           "fixture_count": len(fixtures), "fixtures": fixtures}
    out = SYNC_DIR / ("daily_fixtures_%s.json" % compact)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    rq = build_recap_queue(fixtures, date_iso)
    rq["generated_at"] = stamp
    rqp = SYNC_DIR / ("recap_queue_%s.json" % compact)
    rqp.write_text(json.dumps(rq, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    man = write_frontend_manifest(fixtures, date_iso, stamp, source)

    for f in fixtures:
        tag = "HERO" if f["hero_candidate"] else "next" if f["next_candidate"] else \
              "recap" if f["recap_candidate"] else ""
        sc = " %s-%s" % (f["score_home"], f["score_away"]) if f["score_home"] is not None else ""
        print("%-26s %-13s pre=%-5s recap_need=%-5s%s  %s" % (
            "%s vs %s" % (f["home_team"], f["away_team"]), f["lifecycle_state"],
            f["pre_match_allowed"], f["recap_needed"], sc, tag))
    renderable = sum(1 for r in man["fixtures"] if r["renderable"])
    print("registry -> %s" % out.relative_to(ROOT))
    print("recap_queue -> %s (%d item(s))" % (rqp.relative_to(ROOT), len(rq["items"])))
    print("fallback manifest -> %s (%d fixtures, %d renderable)" % (FE_MANIFEST.relative_to(ROOT), len(man["fixtures"]), renderable))
    print("runtime manifest -> %s" % FE_RUNTIME.relative_to(ROOT))
    return doc


def _enrich_fetched(fixtures, date_iso, now):
    """Best-effort API-FOOTBALL enrichment. Fills kickoff/status/score where matchable;
    NEVER overwrites a confirmed manual score with a different value (records conflict)."""
    try:
        sys.path.insert(0, str(ROOT / "backend"))
        from app.services.api_football_client import APIFootballScoutClient
        client = APIFootballScoutClient()
    except Exception as e:
        print("fetched mode unavailable (%s) — manual values kept" % e)
        return
    for f in fixtures:
        iid = f["internal_fixture_id"]
        if not iid:
            continue
        try:
            fx = (client.get_fixture(int(iid)).response or [{}])[0]
            g = fx.get("goals") or {}
            short = ((fx.get("fixture") or {}).get("status") or {}).get("short")
            if short:
                f["source_mode"] = "fetched"
                f["source_note"] = "API-FOOTBALL status %s (manual score authoritative on conflict)" % short
            if g.get("home") is not None and f["score_home"] is not None and (
                    g.get("home") != f["score_home"] or g.get("away") != f["score_away"]):
                f["score_conflict"] = "manual %s-%s vs api %s-%s (manual kept)" % (
                    f["score_home"], f["score_away"], g.get("home"), g.get("away"))
        except Exception:
            continue


def selftest():
    now = datetime(2026, 6, 13, 4, 0, tzinfo=timezone.utc)
    raws = [
        {"home": "Canada", "away": "Bosnia and Herzegovina", "score_home": 1, "score_away": 1, "status": "finished"},
        {"home": "United States", "away": "Paraguay", "score_home": 4, "score_away": 1, "status": "finished"},
        {"home": "Brazil", "away": "Morocco", "score_home": None, "score_away": None, "status": "scheduled"},
        {"home": "Qatar", "away": "Switzerland", "score_home": None, "score_away": None, "status": "scheduled"},
    ]
    fx = [evaluate(r, now, now.isoformat(), "manual", "selftest", "selftest") for r in raws]
    select_candidates(fx)
    by = {f["home_team"]: f for f in fx}
    checks = [
        ("Canada finished->recap_needed", by["Canada"]["lifecycle_state"] in ("FINISHED", "RECAP_PENDING") and by["Canada"]["recap_needed"] and not by["Canada"]["pre_match_allowed"]),
        ("USA finished->recap_needed", by["United States"]["recap_needed"] and not by["United States"]["pre_match_allowed"]),
        ("Canada/USA never today pkg", not by["Canada"]["package_today_allowed"] and not by["United States"]["package_today_allowed"]),
        ("Brazil scheduled pre-match", by["Brazil"]["lifecycle_state"] in ("SCHEDULED", "T_MINUS_2H", "T_MINUS_30") and by["Brazil"]["pre_match_allowed"]),
        ("Brazil is hero (renderable pre-match)", by["Brazil"]["hero_candidate"]),
        ("Qatar not hero (no narrative)", not by["Qatar"]["hero_candidate"]),
        ("Canada not hero", not by["Canada"]["hero_candidate"]),
        ("no invented score for scheduled", by["Brazil"]["score_home"] is None and by["Qatar"]["score_home"] is None),
    ]
    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        print("%s  %s" % ("PASS" if c else "FAIL", name))
    print("MATCH-SYNC SELFTEST %s (%d/%d)" % ("PASS" if ok == len(checks) else "FAIL", ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="sync", choices=["sync"])
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (default: today UTC)")
    ap.add_argument("--source", default="manual", choices=["manual", "fetched"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    date_iso = a.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cmd_sync(date_iso, a.source)


if __name__ == "__main__":
    main()
