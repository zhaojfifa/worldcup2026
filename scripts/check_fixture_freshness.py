#!/usr/bin/env python3
"""
P1.2 stale-surface scanner — a finished/live match must never look pre-match.

Local-first by design (Owner P1.2 §4): scans the BUNDLED narrative manifests,
the frontend source that pins surface fixture ids, and the generated growth
package files. The live site renders exactly these bundled inputs, so a local
PASS plus a verified deploy implies live freshness; live DOM scanning stays
with scripts/check_customer_visible_copy.py.

Checks, per tracked fixture whose lifecycle is LIVE/FINISHED/RECAP_PENDING/
RECAP_READY/ARCHIVED:
  1. /predict/<id> + /share/fixture/<id> source: every bundled narrative for
     the fixture must be mode=real_recap (PredictPage/ShareCardPage switch to
     recap rendering on that field; a pre-match mode = stale surface). FAIL.
  2. homepage hero / rescore hook: the fixture ids hardcoded in HomePage.tsx
     must not be finished-class for hero/today surfaces. FAIL.
  3. /recap/<id>: a bundled real_recap narrative exists (recap-ready), else
     report recap-pending (WARN — the A4 recap job owes one; surfaces must
     not pretend it exists).
  4. growth package files: no today_/next_ package for a finished/live fixture
     may still carry paste-ready pre-match copy (今晚主看/即将开赛 heads or an
     'available' status). FAIL — re-run refresh, which writes a REFUSED stub.

Exit 0 = PASS (warnings allowed) · exit 1 = FAIL (stale surface found).
Usage: python3 scripts/check_fixture_freshness.py [--no-api]
"""
import argparse
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_NARR = ROOT / "frontend" / "src" / "data" / "productNarratives"
PKG_DIR = ROOT / "docs" / "data_audit" / "mvp2_growth_packages"
HOME = ROOT / "frontend" / "src" / "pages" / "HomePage.tsx"
LANG_FILES = ("zh-CN", "vi-VN", "my-MM")
STALE_HEADS = ("今晚主看", "即将开赛", "Trận đáng xem", "Sắp đá", "ဒီညအဓိကပွဲ", "မကြာမီ")
FINISHED_CLASS = {"LIVE", "FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}


def _load_lifecycle():
    spec = importlib.util.spec_from_file_location(
        "mvp2_fixture_lifecycle", ROOT / "scripts" / "mvp2_fixture_lifecycle.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-api", action="store_true", help="time/bundle inference only")
    a = ap.parse_args()
    lc = _load_lifecycle()
    fails, warns = [], []
    states = {}
    for fid in lc.tracked_fixtures():
        e = lc.evaluate_fixture(fid, use_api=not a.no_api)
        states[fid] = e["new_state"]
        print("lifecycle %-9s %-13s (%s)" % (fid, e["new_state"], e["status_source"]))

    home_src = HOME.read_text(encoding="utf-8") if HOME.exists() else ""
    hero_ids = re.findall(r'(?:TrialHeroCard|RescoreHookCard)[^>]*fixtureId="(\w+)"', home_src)

    for fid, state in states.items():
        if state not in FINISHED_CLASS:
            continue
        # 1. bundled narrative mode per language (drives /predict and /share/fixture)
        bundled = False
        for lang in LANG_FILES:
            p = FE_NARR / ("%s.%s.json" % (fid, lang))
            if not p.exists():
                continue
            bundled = True
            mode = ""
            m = re.search(r'"mode"\s*:\s*"([^"]+)"', p.read_text(encoding="utf-8"))
            mode = m.group(1) if m else ""
            if mode != "real_recap":
                fails.append("%s %s: bundled narrative still pre-match (mode=%s) — "
                             "/predict + /share/fixture present a %s match as active" % (fid, lang, mode, state))
        if not bundled:
            warns.append("%s: not bundled in the frontend — no customer surface, lifecycle gate only" % fid)
        # 2. homepage hero / rescore hook pins
        if fid in hero_ids:
            fails.append("%s: HomePage hero/rescore hook still pins a %s fixture as 今日主推 — "
                         "engineer update + redeploy required" % (fid, state))
        # 3. recap surface availability
        if state in ("FINISHED", "RECAP_PENDING"):
            warns.append("%s: recap not bundled yet (%s) — /recap absent; run the A4 recap job, "
                         "customer message until then = 赛后复盘生成中" % (fid, state))
        # 4. growth package files must not carry paste-ready pre-match copy
        for kind in ("today", "next"):
            for f in PKG_DIR.glob("%s_%s_*.md" % (kind, fid)):
                body = f.read_text(encoding="utf-8")
                if "package_status: available" in body or any(h in body for h in STALE_HEADS):
                    fails.append("%s: stale %s package %s still offers pre-match copy for a %s match — "
                                 "re-run refresh (writes REFUSED stub)" % (fid, kind, f.name, state))

    for w in warns:
        print("WARN  %s" % w)
    for f in fails:
        print("STALE %s" % f)
    if fails:
        print("FRESHNESS FAIL — %d stale surface(s)" % len(fails))
        return 1
    print("FRESHNESS PASS (%d fixtures, %d warning(s))" % (len(states), len(warns)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
