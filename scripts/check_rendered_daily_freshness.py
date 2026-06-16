#!/usr/bin/env python3
"""
P4R Phase 1 — RENDERED daily-freshness guard. Inspects the actual rendered homepage DOM (not just
artifact equality) and fails if today's visible content is stale or demo content leaks.

Fails if:
  - the homepage does NOT render the active primary (selectedHotspot home & away);
  - the homepage does NOT render the previous-cycle recap (recap_queue[0] home & away);
  - old demo fixtures (Qatar/Ecuador/Netherlands/Japan) appear in the rendered homepage;
  - (the "today/yesterday" labels are present but their teams are missing → label-without-content).

Also writes docs/data_audit/mvp2_rendered_freshness/<date>.json with active_content_date, runtime_date,
homepage_primary_fixture, homepage_yesterday_recap_fixture, rendered_content_freshness, stale_reason.
Usage: check_rendered_daily_freshness.py [--base-url URL] [--date D] | --selftest
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom, demo_pair_leak  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_rendered_freshness"
DEMO = ["Qatar", "Ecuador", "Netherlands", "Japan"]   # demoted demo fixtures — must not be in critical sections


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(dom, primary_teams, yesterday_teams):
    fails = []
    for t in primary_teams:
        if t and t not in dom:
            fails.append("homepage does NOT render active primary team %r (stale/wrong today content)" % t)
    for t in yesterday_teams:
        if t and t not in dom:
            fails.append("homepage does NOT render previous-cycle recap team %r" % t)
    leak = demo_pair_leak(dom)
    if leak:
        fails.append("demo/stale pairing %r leaked into the rendered homepage (critical section)" % leak)
    return fails


def selftest():
    dom_ok = "<div>今日热点预测 Belgium vs Egypt … 昨日热点复盘 Brazil 1-1 Morocco</div>"
    dom_stale = "<div>今日热点预测 Netherlands vs Japan …</div>"
    checks = [
        ("fresh dom passes", scan(dom_ok, ["Belgium", "Egypt"], ["Brazil", "Morocco"]) == []),
        ("missing primary caught", any("active primary" in x for x in scan(dom_stale, ["Belgium", "Egypt"], ["Brazil", "Morocco"]))),
        ("demo leak caught", any("leaked" in x for x in scan(dom_stale, ["Belgium", "Egypt"], ["Brazil", "Morocco"]))),
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
    base = argv[argv.index("--base-url") + 1] if "--base-url" in argv else "https://worldcup2026-izid.onrender.com"
    date = argv[argv.index("--date") + 1] if "--date" in argv else None
    sel = _load(SEL) or {}
    q = _load(QUEUE) or {}
    primary_teams = [sel.get("home"), sel.get("away")]
    recap_q = q.get("recap_queue") or []
    yrec = recap_q[0] if recap_q else {}
    yesterday_teams = [yrec.get("home"), yrec.get("away")]
    dom = dump_dom(base.rstrip("/") + "/?lang=zh")
    if not dom:
        print("FAIL  could not render homepage DOM (%s) — is the URL serving?" % base); return 1
    fails = scan(dom, primary_teams, yesterday_teams)
    status = "FRESH" if not fails else "STALE"
    out = {"date": date, "base_url": base, "active_content_date": q.get("date") or sel.get("date"),
           "homepage_primary_fixture": sel.get("fixture_key"),
           "homepage_primary_teams": primary_teams, "homepage_yesterday_recap_teams": yesterday_teams,
           "rendered_content_freshness": status, "stale_reason": ("; ".join(fails) or None)}
    if date:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / ("%s.json" % date)).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("RENDERED FRESHNESS · %s · %s" % (base, status))
    print("  primary=%s · yesterday=%s" % (" ".join(t for t in primary_teams if t), " ".join(t for t in yesterday_teams if t)))
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RENDERED DAILY FRESHNESS FAIL — %d issue(s)" % len(fails)); return 1
    print("RENDERED DAILY FRESHNESS PASS (homepage renders active primary + prior recap; no demo leak)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
