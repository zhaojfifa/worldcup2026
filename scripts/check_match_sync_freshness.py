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

ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC_DIR = ROOT / "docs" / "data_audit" / "mvp2_match_sync"
PKG_DIR = ROOT / "docs" / "data_audit" / "mvp2_growth_packages"
HOME = ROOT / "frontend" / "src" / "pages" / "HomePage.tsx"
MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"
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

    # 6. frontend active fixture must be registry-sourced, not hardcoded
    home_src = HOME.read_text(encoding="utf-8") if HOME.exists() else ""
    if "activeFixtureEntries" not in home_src:
        fails.append("HomePage does not source the hero from the registry manifest (activeFixtureEntries missing)")
    if re.search(r'TrialHeroCard[^>]*fixtureId="\d+"', home_src):
        fails.append("HomePage hardcodes a hero fixtureId literal — must use registry selection")

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
