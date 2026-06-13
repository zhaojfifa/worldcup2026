#!/usr/bin/env python3
"""
P1.3 stale-registry scanner — the daily fixture registry must be complete and honest.

Fails (exit 1) if:
  1. a completed match in the daily registry is missing from the recap queue
  2. the homepage hero uses a fixture not present in the registry / active manifest
  3. a today_* package file targets a finished fixture
  4. a known completed match (manual input) is absent from the registry
  5. a registry score conflicts with the manual input
  6. the frontend active fixture is hardcoded and ignores the registry

Usage: python3 scripts/check_match_sync_freshness.py [--date YYYY-MM-DD]
Local-first: reads the latest (or --date) registry/recap-queue/manifest + frontend source.
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
PKG_DIR = ROOT / "docs" / "data_audit" / "mvp2_growth_packages"
HOME = ROOT / "frontend" / "src" / "pages" / "HomePage.tsx"
MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"
RUNTIME_MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"   # P1.3b runtime source
FINISHED_CLASS = {"FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}


def _load_sync():
    spec = importlib.util.spec_from_file_location("mvp2_match_sync", ROOT / "scripts" / "mvp2_match_sync.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _latest(glob):
    files = sorted(SYNC_DIR.glob(glob))
    return files[-1] if files else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=None)
    ap.add_argument("--max-age-hours", type=float, default=36.0, help="P1.3b: FAIL if runtime manifest older")
    a = ap.parse_args()
    fails, warns = [], []

    reg_p = (SYNC_DIR / ("daily_fixtures_%s.json" % a.date.replace("-", ""))) if a.date else _latest("daily_fixtures_*.json")
    rq_p = (SYNC_DIR / ("recap_queue_%s.json" % a.date.replace("-", ""))) if a.date else _latest("recap_queue_*.json")
    if not reg_p or not reg_p.exists():
        print("NO REGISTRY found — run scripts/mvp2_match_sync.py sync first")
        return 1
    reg = json.loads(reg_p.read_text(encoding="utf-8"))
    fixtures = reg.get("fixtures", [])
    rq = json.loads(rq_p.read_text(encoding="utf-8")) if rq_p and rq_p.exists() else {"items": []}
    rq_keys = {(it.get("fixture")) for it in rq.get("items", [])}
    print("registry %s — %d fixtures · recap_queue %d items" % (reg_p.name, len(fixtures), len(rq.get("items", []))))

    # 1. completed registry fixture must be in recap queue
    for f in fixtures:
        if f["lifecycle_state"] in FINISHED_CLASS:
            key = "%s vs %s" % (f["home_team"], f["away_team"])
            if key not in rq_keys:
                fails.append("completed %s (%s) missing from recap_queue" % (key, f["lifecycle_state"]))

    # 2. homepage hero fixture present in registry/manifest
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"fixtures": []}
    man_ids = {r.get("id") for r in man.get("fixtures", [])}
    reg_ids = {f.get("internal_fixture_id") for f in fixtures}
    hero = [r for r in man.get("fixtures", []) if r.get("heroCandidate")]
    for h in hero:
        if h["id"] not in reg_ids:
            fails.append("manifest hero %s not present in registry" % h["id"])

    # 3. today_* package file must not target a finished fixture
    state_by_id = {f.get("internal_fixture_id"): f["lifecycle_state"] for f in fixtures}
    for pf in PKG_DIR.glob("today_*.md"):
        m = re.match(r"today_(\d+)_", pf.name)
        if not m:
            continue
        fid = m.group(1)
        body = pf.read_text(encoding="utf-8")
        is_refused = "REFUSED" in body
        st = state_by_id.get(fid)
        if st in FINISHED_CLASS and not is_refused:
            fails.append("today package %s targets a %s fixture without REFUSED stub" % (pf.name, st))

    # 4 + 5. known completed manual matches present in registry + score match
    sync = _load_sync()
    compact = reg["date"].replace("-", "")
    try:
        manual = sync.parse_manual(compact)
    except SystemExit:
        manual = []
    reg_by_pair = {(sync._canon(f["home_team"]), sync._canon(f["away_team"])): f for f in fixtures}
    for r in manual:
        pair = (sync._canon(r["home"]), sync._canon(r["away"]))
        rf = reg_by_pair.get(pair)
        if r["status"] == "finished" and not rf:
            fails.append("completed manual match %s vs %s absent from registry" % (r["home"], r["away"]))
            continue
        if rf and r["score_home"] is not None:
            if rf["score_home"] != r["score_home"] or rf["score_away"] != r["score_away"]:
                fails.append("score conflict %s vs %s: registry %s-%s vs manual %s-%s" % (
                    r["home"], r["away"], rf["score_home"], rf["score_away"], r["score_home"], r["score_away"]))

    # 6. frontend active fixture must be RUNTIME-sourced, not hardcoded / build-time-only
    home_src = HOME.read_text(encoding="utf-8") if HOME.exists() else ""
    if "fetchDailyManifest" not in home_src:
        fails.append("HomePage does not FETCH the runtime daily manifest (P1.3b: build-time-only is insufficient)")
    if re.search(r'TrialHeroCard[^>]*fixtureId="\d+"', home_src):
        fails.append("HomePage hardcodes a hero fixtureId literal — must use registry selection")

    # 6b. P1.4 orchestration — homepage must render the completed/recap desk + upcoming-needs-narrative
    desk = (ROOT / "frontend" / "src" / "components" / "MatchDesk.tsx").read_text(encoding="utf-8") \
        if (ROOT / "frontend" / "src" / "components" / "MatchDesk.tsx").exists() else ""
    for comp in ("RecapDesk", "UpcomingNeedsNarrative", "OperatorStatusLine"):
        if comp not in home_src:
            fails.append("HomePage does not render %s — completed/upcoming matches would be invisible (P1.4)" % comp)
    if "FINISHED" not in desk or "manifest.fixtures" not in desk:
        fails.append("RecapDesk does not iterate finished fixtures from the manifest (P1.4)")
    # a pending recap must NOT be shown as ready: the view button is gated on recapReady
    if "recapReady" not in desk or "/recap/" not in desk:
        fails.append("RecapDesk does not gate the 查看复盘 button on recapReady (could show pending as ready)")
    if "待生成赛前判断" not in desk:
        fails.append("UpcomingNeedsNarrative missing the 待生成赛前判断 label (P1.4 §C)")

    # 7. P1.3b runtime manifest checks (Owner §scanner)
    if not RUNTIME_MANIFEST.exists():
        fails.append("runtime manifest %s missing — run match-sync (P1.3b live source absent)" % RUNTIME_MANIFEST.name)
    else:
        rt = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
        rt_fx = rt.get("fixtures", [])
        rt_teams = {(f.get("home"), f.get("away")) for f in rt_fx}
        # completed known matches (manual finished) must be present in the runtime manifest
        sync2 = _load_sync()
        try:
            for r in sync2.parse_manual(reg["date"].replace("-", "")):
                if r["status"] == "finished" and (r["home"], r["away"]) not in rt_teams:
                    fails.append("completed %s vs %s absent from RUNTIME manifest" % (r["home"], r["away"]))
        except SystemExit:
            pass
        # completed fixture must not be a today/hero candidate in the runtime manifest
        for f in rt_fx:
            if f.get("lifecycle_state") in FINISHED_CLASS and (f.get("heroCandidate") or f.get("nextCandidate")):
                fails.append("runtime manifest marks finished %s vs %s as hero/next candidate" % (f.get("home"), f.get("away")))
        # staleness
        ga = rt.get("generated_at")
        if ga:
            try:
                gat = datetime.fromisoformat(ga)
                if gat.tzinfo is None:
                    gat = gat.replace(tzinfo=timezone.utc)
                age_h = (datetime.now(timezone.utc) - gat).total_seconds() / 3600
                print("runtime manifest age %.1fh (threshold %.0fh) · source_mode=%s" % (age_h, a.max_age_hours, rt.get("source_mode")))
                if age_h > a.max_age_hours:
                    fails.append("runtime manifest stale: %.1fh > %.0fh threshold — re-run match-sync" % (age_h, a.max_age_hours))
            except Exception:
                warns.append("runtime manifest generated_at unparseable: %r" % ga)

    for w in warns:
        print("WARN  %s" % w)
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("MATCH-SYNC FRESHNESS FAIL — %d issue(s)" % len(fails))
        return 1
    print("MATCH-SYNC FRESHNESS PASS (%d fixtures, %d recap-queue items)" % (len(fixtures), len(rq.get("items", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
