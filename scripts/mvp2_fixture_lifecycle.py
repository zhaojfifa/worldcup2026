#!/usr/bin/env python3
"""
P1.2 Status Refresh Gate — canonical fixture lifecycle (freshness over prediction).

A finished or live match must NEVER be presented as an active pre-match
prediction. This module is the ONE place that decides a fixture's lifecycle
state; the growth CLI (package/refresh/status-refresh) and the stale-surface
scanner (check_fixture_freshness.py) all consume it. Nothing here sends
anything or writes customer copy.

Canonical states (in order):
  SCHEDULED      pre-match prediction allowed
  T_MINUS_2H     operator watch starts (pre-match still allowed)
  T_MINUS_30     A3 rescore path allowed (pre-match still allowed)
  LIVE           pre-match copy FROZEN — must not show as today prediction
  FINISHED       final whistle window; pre-match share/package refused
  RECAP_PENDING  recap narrative not bundled yet — surface 赛后复盘生成中
  RECAP_READY    bundled real_recap narrative exists — recap page/share allowed
  ARCHIVED       historical recap only; never a today package

Status sources (best available, recorded per fixture in status_source):
  api_football      fixture status + final score from API-FOOTBALL
  bundled_narrative a bundled real_recap narrative proves the match finished
  time_inference    kickoff-time arithmetic only (API unavailable/disabled)

CLI:
  python3 scripts/mvp2_fixture_lifecycle.py [--no-api] [--fixture ID ...] [--no-write]
  python3 scripts/mvp2_fixture_lifecycle.py --selftest
  (`scripts/mvp2_growth_cli.py status-refresh` is the operator entry point.)

Output:
  docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_YYYYMMDD_HHMM.json
"""
import argparse
import json
import pathlib
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "data_audit" / "mvp2_ops_registry"
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"
FE_NARR = ROOT / "frontend" / "src" / "data" / "productNarratives"
OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_daily_refresh"

STATES = ("SCHEDULED", "T_MINUS_2H", "T_MINUS_30", "LIVE", "FINISHED",
          "RECAP_PENDING", "RECAP_READY", "ARCHIVED")
PRE_MATCH_STATES = {"SCHEDULED", "T_MINUS_2H", "T_MINUS_30"}
RECAP_PACKAGE_STATES = {"FINISHED", "RECAP_PENDING", "RECAP_READY"}

# API-FOOTBALL status.short mapping
FINISHED_SHORT = {"FT", "AET", "PEN"}
LIVE_SHORT = {"1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"}
HALTED_SHORT = {"PST", "CANC", "ABD", "AWD", "WO"}  # never package anything

WATCH_WINDOW_MIN = 120     # T-2h: operator watch starts
RESCORE_WINDOW_MIN = 30    # T-30: A3 rescore path opens
FT_ESTIMATE_MIN = 130      # kickoff + ~130min ≈ final whistle (time inference)
RECAP_JOB_GRACE_MIN = 45   # A4 recap job is due from FT+45
ARCHIVE_AFTER_HOURS = 72   # recap-ready fixtures become historical after 72h


def decide(now, kickoff, api_short=None, recap_ready=False):
    """Pure state decision — fully unit-testable, no IO.

    Returns (state, reason). `kickoff` may be None (unknown → conservative
    SCHEDULED, packaging callers must treat missing kickoff as not-today).
    Time inference of FINISHED happens only when the API gave no status.
    """
    mins = None if kickoff is None else (kickoff - now).total_seconds() / 60.0
    finished = (recap_ready or api_short in FINISHED_SHORT
                or (api_short is None and mins is not None and mins <= -FT_ESTIMATE_MIN))
    if finished:
        if recap_ready:
            if mins is not None and mins <= -ARCHIVE_AFTER_HOURS * 60:
                return "ARCHIVED", "recap ready and kickoff more than %dh ago" % ARCHIVE_AFTER_HOURS
            return "RECAP_READY", "bundled real_recap narrative exists"
        if mins is not None and mins > -(FT_ESTIMATE_MIN + RECAP_JOB_GRACE_MIN):
            return "FINISHED", "final whistle window; A4 recap job not due yet (FT+%dmin)" % RECAP_JOB_GRACE_MIN
        return "RECAP_PENDING", "match finished but no recap narrative bundled — 赛后复盘生成中"
    if api_short in HALTED_SHORT:
        return "SCHEDULED", "api status %s (halted/postponed) — ALL packaging refused" % api_short
    if api_short in LIVE_SHORT:
        return "LIVE", "api status %s — pre-match copy frozen" % api_short
    if mins is not None and mins <= 0:
        # kickoff passed but no finished signal (API stale/NS or time-only): freeze.
        return "LIVE", "kickoff passed without a finished signal — pre-match copy frozen"
    if mins is None:
        return "SCHEDULED", "no kickoff time on record — verify fixture before packaging"
    if mins <= RESCORE_WINDOW_MIN:
        return "T_MINUS_30", "T-%.0fmin — A3 rescore window open" % mins
    if mins <= WATCH_WINDOW_MIN:
        return "T_MINUS_2H", "T-%.0fmin — operator watch window" % mins
    return "SCHEDULED", "T-%.0fmin to kickoff" % mins


def gates(state, halted=False):
    """Packaging permissions derived from the state (single source of truth)."""
    pre = state in PRE_MATCH_STATES and not halted
    return {
        "pre_match_allowed": pre,
        "today_package_allowed": pre,
        "recap_needed": state in ("FINISHED", "RECAP_PENDING"),
        "recap_ready": state in ("RECAP_READY", "ARCHIVED"),
        "recap_package_allowed": state in RECAP_PACKAGE_STATES,
    }


# ── fixture facts (IO) ────────────────────────────────────────────────────────
def _read_json(p):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None


def tracked_fixtures():
    """Registry manifests are the tracked-fixture source of truth."""
    fids = sorted(p.stem.split(".")[0] for p in REGISTRY.glob("*.manifest.json"))
    return fids or ["1489369", "1489371"]


def fixture_facts(fid):
    """kickoff datetime + display title from registry manifest / trial frame."""
    kickoff, title = None, fid
    m = _read_json(REGISTRY / ("%s.manifest.json" % fid)) or {}
    fr = (_read_json(FRAMES / ("%s.json" % fid)) or {}).get("fixture", {})
    raw = m.get("kickoff_utc") or fr.get("kickoff")
    if raw:
        kickoff = datetime.fromisoformat(raw)
        if kickoff.tzinfo is None:
            kickoff = kickoff.replace(tzinfo=timezone.utc)
    title = fr.get("match") or m.get("title") or fid
    return kickoff, title


def recap_ready_for(fid):
    n = _read_json(FE_NARR / ("%s.zh-CN.json" % fid))
    return bool(n and n.get("mode") == "real_recap")


def api_probe(fid):
    """Best-effort fixture status from API-FOOTBALL. Returns (short, score, kickoff)
    or (None, None, None) — callers fall back to time inference, never crash."""
    try:
        sys.path.insert(0, str(ROOT / "backend"))
        from app.services.api_football_client import APIFootballScoutClient
        fx = (APIFootballScoutClient().get_fixture(int(fid)).response or [{}])[0]
        f = fx.get("fixture", {})
        short = (f.get("status") or {}).get("short")
        goals = fx.get("goals") or {}
        score = None
        if short in FINISHED_SHORT and goals.get("home") is not None:
            score = "%s-%s" % (goals.get("home"), goals.get("away"))
        ko = datetime.fromisoformat(f["date"]) if f.get("date") else None
        return short, score, ko
    except Exception:
        return None, None, None


def previous_state(fid):
    files = sorted(OUT_DIR.glob("fixture_lifecycle_*.json"))
    if not files:
        return None
    doc = _read_json(files[-1]) or {}
    for e in doc.get("fixtures", []):
        if str(e.get("fixture_id")) == str(fid):
            return e.get("new_state")
    return None


def evaluate_fixture(fid, use_api=True, now=None):
    """Full lifecycle entry for one fixture (Owner P1.2 §2 field list)."""
    now = now or datetime.now(timezone.utc)
    kickoff, title = fixture_facts(fid)
    recap_ready = recap_ready_for(fid)
    short = score = None
    source = "time_inference"
    if use_api:
        short, score, api_ko = api_probe(fid)
        if short is not None:
            source = "api_football"
            kickoff = kickoff or api_ko
    if recap_ready and source != "api_football":
        source = "bundled_narrative"
    state, reason = decide(now, kickoff, api_short=short, recap_ready=recap_ready)
    halted = short in HALTED_SHORT
    g = gates(state, halted=halted)
    return {
        "fixture_id": fid,
        "teams": title,
        "kickoff_time_utc": kickoff.isoformat() if kickoff else None,
        "current_time_utc": now.isoformat(),
        "previous_state": previous_state(fid),
        "new_state": state,
        "status_source": source,
        "api_status_short": short,
        "score_if_finished": score,
        "pre_match_allowed": g["pre_match_allowed"],
        "today_package_allowed": g["today_package_allowed"],
        "recap_needed": g["recap_needed"],
        "recap_ready": g["recap_ready"],
        "recap_package_allowed": g["recap_package_allowed"],
        "reason": reason,
    }


def run_status_refresh(fids=None, use_api=True, write=True, now=None):
    now = now or datetime.now(timezone.utc)
    entries = [evaluate_fixture(f, use_api=use_api, now=now) for f in (fids or tracked_fixtures())]
    doc = {"generated_at": now.isoformat(), "job": "status_refresh",
           "status_sources_used": sorted({e["status_source"] for e in entries}),
           "fixtures": entries}
    for e in entries:
        flag = "" if e["previous_state"] in (None, e["new_state"]) else "  (was %s)" % e["previous_state"]
        print("%-9s %-13s %-16s today=%-5s recap_pkg=%-5s %s%s" % (
            e["fixture_id"], e["new_state"], e["kickoff_time_utc"] or "-",
            e["today_package_allowed"], e["recap_package_allowed"], e["reason"], flag))
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / ("fixture_lifecycle_%s.json" % now.strftime("%Y%m%d_%H%M"))
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("lifecycle -> %s" % out.relative_to(ROOT))
        doc["output_file"] = str(out.relative_to(ROOT))
    return doc


# ── selftest (pure decide()/gates(), no network, no files) ───────────────────
def selftest():
    ko = datetime(2026, 6, 13, 22, 0, tzinfo=timezone.utc)
    t = lambda **kw: ko + timedelta(**kw)  # noqa: E731
    cases = [
        # (now, api_short, recap_ready, expect_state)
        (t(hours=-21), None, False, "SCHEDULED"),
        (t(minutes=-90), None, False, "T_MINUS_2H"),
        (t(minutes=-25), None, False, "T_MINUS_30"),
        (t(minutes=10), None, False, "LIVE"),              # time-only freeze
        (t(minutes=50), "1H", False, "LIVE"),
        (t(minutes=50), "NS", False, "LIVE"),              # API stale, kickoff passed -> freeze
        (t(minutes=140), "FT", False, "FINISHED"),         # recap job not due yet
        (t(hours=4), "FT", False, "RECAP_PENDING"),
        (t(hours=4), None, False, "RECAP_PENDING"),        # time inference of finished
        (t(hours=4), "FT", True, "RECAP_READY"),
        (t(hours=80), "FT", True, "ARCHIVED"),
        (t(hours=-21), "PST", False, "SCHEDULED"),         # halted -> gates all False
    ]
    failures = []
    for now, short, ready, want in cases:
        got, reason = decide(now, ko, api_short=short, recap_ready=ready)
        ok = got == want
        if not ok:
            failures.append((now.isoformat(), short, ready, want, got))
        print("%s now=%s api=%-4s recap_ready=%-5s -> %-13s (want %s)" % (
            "PASS" if ok else "FAIL", now.strftime("%dT%H:%M"), short, ready, got, want))
    # gate assertions (the actual acceptance criteria)
    for state in ("LIVE", "FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"):
        if gates(state)["today_package_allowed"]:
            failures.append(("gate", state, "today_package_allowed must be False"))
    for state in ("FINISHED", "RECAP_PENDING", "RECAP_READY"):
        if not gates(state)["recap_package_allowed"]:
            failures.append(("gate", state, "recap_package_allowed must be True"))
    if gates("ARCHIVED")["recap_package_allowed"]:
        failures.append(("gate", "ARCHIVED", "recap_package_allowed must be False"))
    if gates("SCHEDULED", halted=True)["pre_match_allowed"]:
        failures.append(("gate", "SCHEDULED+halted", "pre_match_allowed must be False"))
    print("gate matrix: today refused for LIVE/FINISHED/RECAP_*/ARCHIVED · recap only FINISHED/RECAP_* · halted all-off")
    if failures:
        print("SELFTEST FAIL: %s" % failures)
        return 1
    print("SELFTEST PASS (%d state cases + gate matrix)" % len(cases))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fixture", action="append", help="fixture id (repeatable; default = registry)")
    ap.add_argument("--no-api", action="store_true", help="time/bundle inference only")
    ap.add_argument("--no-write", action="store_true", help="print only, no lifecycle file")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    run_status_refresh(fids=a.fixture, use_api=not a.no_api, write=not a.no_write)


if __name__ == "__main__":
    main()
