#!/usr/bin/env python3
"""
P3B — T-30 source ingestion status. For each selected match, record what KO-30 update SOURCE is
actually available — and, crucially, what is NOT. The project does NOT ingest live lineups / injuries
/ team news, so this layer must say SOURCE_MISSING / SOURCE_PARTIAL honestly and NEVER invent a T-30
update. The ScoutScore model baseline (kaggle Elo/form) is a PRE-MATCH frame, not a live KO-30 feed.

Writes docs/data_audit/mvp2_t30_sources/<date>.json. Per fixture:
  kickoff_time, t30_deadline, expected_source_fields, available_source_fields, missing_source_fields,
  lineup_availability, injury_news_availability, tactical_variable_availability, source_status,
  update_eligibility, next_operator_action.

source_status ∈ SOURCE_READY | SOURCE_MISSING | SOURCE_STALE | SOURCE_PARTIAL | OPERATOR_OVERRIDE_REQUIRED
HARD RULE: no live lineup/injury source ⇒ never AUTO_UPDATE; the operator confirms at KO-30 manually.
Modes: build --date YYYY-MM-DD ; --selftest
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_t30_sources"

# What a real KO-30 UPDATE source would carry. lineups/injuries/news are NOT ingested by this project.
EXPECTED = ["starting_xi", "formation", "goalkeeper", "injuries_news", "late_tactical_shape"]
VALID_STATUS = {"SOURCE_READY", "SOURCE_MISSING", "SOURCE_STALE", "SOURCE_PARTIAL", "OPERATOR_OVERRIDE_REQUIRED"}


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _artifact(fk):
    if not PRED_DIR.exists():
        return None
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (a.get("fixture_key") == fk or a.get("id") == fk):
            return a
    return None


def assess(fk, row):
    """Honest assessment from what's actually available. No lineup/injury feed exists → those are
    always unavailable; the model baseline only frames the watch, it does not satisfy a KO-30 update."""
    art = _artifact(fk) or {}
    mf = art.get("model_fields") or {}
    t30 = art.get("t30") or {}
    has_model = mf.get("source") == "computed"
    has_checklist = bool((art.get("llm_judgment") or {}).get("t30_checklist") or
                         (((art.get("i18n") or {}).get("zh") or {}).get("analysis") or {}).get("thirty_minute_checklist"))
    # live KO-30 fields — NONE are ingested
    lineup = False
    injury_news = False
    tactical_var = "model_baseline" if has_model else ("operator_estimated" if mf.get("source") else "none")
    available = (["tactical_baseline"] if has_model else []) + (["t30_checklist"] if has_checklist else [])
    missing = [f for f in EXPECTED]  # all live KO-30 fields are missing (not ingested)
    # classification: a model baseline + checklist = PARTIAL framing, but the live update SOURCE is
    # missing → operator must confirm manually at KO-30. If the operator has already confirmed (t30
    # ready/skipped), that is OPERATOR_OVERRIDE_REQUIRED satisfied.
    if t30.get("status") in ("ready", "skipped") and t30.get("update_text") is not None:
        status, elig, nxt = "OPERATOR_OVERRIDE_REQUIRED", "OPERATOR_CONFIRMED", "done — operator confirmed at KO-30"
    elif available:
        status, elig, nxt = ("SOURCE_PARTIAL", "OPERATOR_CONFIRM_REQUIRED",
                             "no live lineup/injury feed — operator confirms lineups at KO-30, then set t30")
    else:
        status, elig, nxt = ("SOURCE_MISSING", "OPERATOR_CONFIRM_REQUIRED",
                             "no source — operator confirms manually at KO-30; do not invent an update")
    ko = row.get("kickoffUtc")
    return {
        "fixture_id": fk, "match": "%s vs %s" % (row.get("home"), row.get("away")),
        "kickoff_time": ko, "t30_deadline": ("KO-30 of %s" % ko) if ko else "TBA",
        "expected_source_fields": EXPECTED, "available_source_fields": available,
        "missing_source_fields": missing,
        "lineup_availability": lineup, "injury_news_availability": injury_news,
        "tactical_variable_availability": tactical_var,
        "source_status": status, "update_eligibility": elig,
        "next_operator_action": nxt,
        "guard_status": "no_fake_t30 (no live feed → no auto update_text)",
    }


def build(date):
    q = _load(QUEUE) or {}
    rows = ([q["primary_hotspot"]] if q.get("primary_hotspot") else []) + (q.get("secondary_matches") or [])
    items = [assess(str(r["fixture_key"]), r) for r in rows]
    out = {"date": date, "built_by": "mvp2_t30_source.py",
           "note": "Live lineup/injury/news are NOT ingested; T-30 update is operator-confirmed. No invented updates.",
           "items": items}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("%s.json" % date)).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def cmd_build(date):
    out = build(date)
    print("T-30 SOURCE · %s" % date)
    for it in out["items"]:
        print("  %-9s %-26s %-18s lineup=%s injury=%s → %s" % (
            it["fixture_id"], it["match"], it["source_status"], it["lineup_availability"],
            it["injury_news_availability"], it["update_eligibility"]))
    print("  → docs/data_audit/mvp2_t30_sources/%s.json" % date)
    return 0


def selftest():
    # synthetic rows; no artifacts → SOURCE_MISSING, no auto update
    row = {"fixture_key": "1", "home": "A", "away": "B", "kickoffUtc": "2026-06-15T19:00:00+00:00"}
    it = assess("1", row)
    checks = [
        ("status valid", it["source_status"] in VALID_STATUS),
        ("lineup never auto-available", it["lineup_availability"] is False),
        ("injury never auto-available", it["injury_news_availability"] is False),
        ("no source → not auto-eligible", it["update_eligibility"] in ("OPERATOR_CONFIRM_REQUIRED", "OPERATOR_CONFIRMED")),
        ("missing fields listed", set(it["missing_source_fields"]) == set(EXPECTED) or len(it["missing_source_fields"]) > 0),
        ("guard marks no_fake_t30", "no_fake_t30" in it["guard_status"]),
        ("next action says do not invent / confirm", "operator" in it["next_operator_action"].lower()),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build", choices=["build"])
    ap.add_argument("--date", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    import datetime
    date = a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return cmd_build(date)


if __name__ == "__main__":
    sys.exit(main())
