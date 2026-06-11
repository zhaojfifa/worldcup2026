#!/usr/bin/env python3
"""
MVP-2 Track A — A1 daily upcoming-match scan (design §3 A1; Owner A-GO-1).

Fetches the season fixture list (API-FOOTBALL, server-side key via the existing
backend client — never printed), keeps today + next-day fixtures, marks key
matches with DETERMINISTIC ordered rules + an operator override file, reads the
local pipeline state for each fixture (frame / narratives / rescore models /
bundle), and writes docs/data_audit/mvp2_daily_scan/{YYYY-MM-DD}.json.

A1 only MARKS and reports `actions_needed` — it generates no narrative and
sends nothing. Hot-reads/tactical-room entries come from A2 artifacts.

Key-match rules (ordered; reasons recorded):
  0 operator override force_key / force_skip (always wins)
  1 knockout round            2 opening day
  3 both teams Elo top-12     4 elo gap >=150 and favourite top-8
  5 host nation playing       cap: max 2 key/day (override-forced exempt)

Usage: python3 scripts/mvp2_daily_scan.py [--date YYYY-MM-DD]
Callable from scripts/mvp2_ops.py (run manifest injected).
"""
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.api_football_client import APIFootballScoutClient  # noqa: E402

OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_daily_scan"
REGISTRY = ROOT / "docs" / "data_audit" / "mvp2_ops_registry"
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"
NARR = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_narratives"
RESCORE = ROOT / "docs" / "data_audit" / "mvp2_rescore_models"
BUNDLED = ROOT / "frontend" / "src" / "data" / "productNarratives"
KAGGLE_CSV = ROOT / "data" / "external" / "kaggle" / "results.csv"
LEAGUE, SEASON = 1, 2026
LANGS = ("zh-CN", "vi-VN", "my-MM")
HOSTS = {"Mexico", "USA", "United States", "Canada"}
DAILY_KEY_CAP = 2


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _load("opsq", ROOT / "scripts" / "mvp2_ops_queue.py")


def _elo_context(cutoff):
    """kaggle-derived Elo snapshot (reuses the v0.2 builder); honest None if the
    local CSV is absent — Elo rules are then skipped and marked in the output."""
    if not KAGGLE_CSV.exists():
        return None
    v02 = _load("v02", ROOT / "scripts" / "mvp2_build_scoutscore_v0_2_factors.py")
    rows = v02.load_results()
    snap = v02.elo_snapshot(rows, cutoff)
    ranked = sorted(snap.items(), key=lambda kv: -kv[1])
    rank = {team: i + 1 for i, (team, _) in enumerate(ranked)}
    return {"snapshot": snap, "rank": rank, "asof": cutoff}


def _pipeline_state(fid):
    fid = str(fid)
    narr = {lang: (NARR / ("%s.%s.deepseek.json" % (fid, lang))).exists() for lang in LANGS}
    resc = {lang: (RESCORE / ("%s.%s.deepseek.json" % (fid, lang))).exists() for lang in LANGS}
    bundled = {lang: (BUNDLED / ("%s.%s.json" % (fid, lang))).exists() for lang in LANGS}
    return {
        "frame": (FRAMES / ("%s.json" % fid)).exists(),
        "narratives": narr, "rescore_models": resc, "bundled": bundled,
    }


def _actions(fx, pipe):
    acts = []
    if not fx["key_match"]:
        return acts
    if not pipe["frame"]:
        acts.append("A2 prematch: build frame + narratives + rescore models")
    else:
        missing_n = [l for l, ok in pipe["narratives"].items() if not ok]
        missing_r = [l for l, ok in pipe["rescore_models"].items() if not ok]
        if missing_n:
            acts.append("A2 narratives missing: %s" % ",".join(missing_n))
        if missing_r:
            acts.append("A2 rescore models missing: %s" % ",".join(missing_r))
        missing_b = [l for l, ok in pipe["bundled"].items() if pipe["narratives"].get(l) and not ok]
        if missing_b:
            acts.append("bundle missing: %s (engineer import step for new fixtures)" % ",".join(missing_b))
    if fx["is_today"] and fx["status_short"] == "NS":
        acts.append("start `mvp2_ops.py watch --fixture %s` at T-90" % fx["fixture_id"])
    return acts


def scan(date_str=None, run=None, client=None):
    now = datetime.now(timezone.utc)
    today = date_str or now.strftime("%Y-%m-%d")
    next_day = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    client = client or APIFootballScoutClient()
    degraded, rows = False, []
    try:
        res = client.get_fixtures(LEAGUE, SEASON)
        if run:
            run.api("/fixtures")
        rows = res.response or []
    except Exception as e:
        degraded = True
        if run:
            run.step("fetch_fixtures", "failed", detail=type(e).__name__)

    season_dates = sorted({(fx.get("fixture") or {}).get("date", "")[:10] for fx in rows if fx.get("fixture")})
    opening_date = season_dates[0] if season_dates else None
    elo = None if degraded else _elo_context(today)
    overrides = Q.read_json(REGISTRY / "key_match_overrides.json", default={}) or {}

    window = []
    for fx in rows:
        f, t, lg = fx.get("fixture", {}), fx.get("teams", {}), fx.get("league", {})
        d = (f.get("date") or "")[:10]
        if d not in (today, next_day):
            continue
        home = (t.get("home") or {}).get("name")
        away = (t.get("away") or {}).get("name")
        fid = f.get("id")
        ov = overrides.get(str(fid), {})
        reasons, forced = [], False
        if ov.get("force_skip"):
            reasons = ["operator_force_skip"]
        else:
            if ov.get("force_key"):
                reasons.append("operator_force_key")
                forced = True
            rnd = (lg.get("round") or "")
            if rnd and "Group" not in rnd:
                reasons.append("knockout_round")
            if opening_date and d == opening_date:
                reasons.append("opening_day")
            if elo:
                rh, ra = elo["rank"].get(home), elo["rank"].get(away)
                eh, ea = elo["snapshot"].get(home), elo["snapshot"].get(away)
                if rh and ra and rh <= 12 and ra <= 12:
                    reasons.append("marquee_pair_top12_elo")
                if eh and ea and abs(eh - ea) >= 150:
                    fav_rank = min(rh or 999, ra or 999)
                    if fav_rank <= 8:
                        reasons.append("big_gap_upset_watch")
            else:
                reasons.append("elo_rules_skipped_no_local_kaggle") if not degraded else None
            if HOSTS & {home, away}:
                reasons.append("host_nation")
        key = bool([r for r in reasons if r not in ("elo_rules_skipped_no_local_kaggle",)]) \
            and not ov.get("force_skip")
        window.append({
            "fixture_id": fid, "match": "%s vs %s" % (home, away),
            "kickoff_utc": f.get("date"), "status_short": ((f.get("status") or {}).get("short")),
            "round": lg.get("round"), "venue": ((f.get("venue") or {}).get("name")),
            "is_today": d == today, "date": d,
            "key_match": key, "key_forced": forced, "key_reasons": reasons,
        })

    # daily cap (rule order = priority; operator-forced exempt)
    for d in (today, next_day):
        keys = [w for w in window if w["date"] == d and w["key_match"] and not w["key_forced"]]
        keys.sort(key=lambda w: min((["operator_force_key", "knockout_round", "opening_day",
                                      "marquee_pair_top12_elo", "big_gap_upset_watch", "host_nation"].index(r)
                                     for r in w["key_reasons"] if r in (
                                         "operator_force_key", "knockout_round", "opening_day",
                                         "marquee_pair_top12_elo", "big_gap_upset_watch", "host_nation")),
                                    default=99))
        forced_n = len([w for w in window if w["date"] == d and w["key_forced"]])
        for w in keys[max(0, DAILY_KEY_CAP - forced_n):]:
            w["key_match"] = False
            w["key_reasons"].append("dropped_by_daily_cap")

    for w in window:
        pipe = _pipeline_state(w["fixture_id"])
        w["pipeline"] = pipe
        w["actions_needed"] = _actions(w, pipe)
        if w["key_match"]:
            m = Q.load_manifest(w["fixture_id"])
            m.update({"match": w["match"], "kickoff_utc": w["kickoff_utc"],
                      "key_match": True, "key_reasons": w["key_reasons"]})
            Q.save_manifest(m)

    doc = {
        "date": today, "generated_at": Q.iso(), "degraded": degraded,
        "league": LEAGUE, "season": SEASON, "opening_date": opening_date,
        "elo_available": bool(elo),
        "fixtures_today": [w for w in window if w["is_today"]],
        "fixtures_next_day": [w for w in window if not w["is_today"]],
        "key_match_cap_per_day": DAILY_KEY_CAP,
        "api_requests_this_scan": 1 if not degraded else 0,
    }
    out = OUT_DIR / ("%s.json" % today)
    Q.write_json(out, doc)
    return out, doc


def main():
    date_str = None
    if "--date" in sys.argv:
        date_str = sys.argv[sys.argv.index("--date") + 1]
    out, doc = scan(date_str)
    keys = [w for w in doc["fixtures_today"] + doc["fixtures_next_day"] if w["key_match"]]
    print("saved %s  (today=%d next=%d key=%d degraded=%s)" % (
        out.relative_to(ROOT), len(doc["fixtures_today"]), len(doc["fixtures_next_day"]),
        len(keys), doc["degraded"]))
    for w in keys:
        print("  KEY %s %s  %s  reasons=%s" % (w["fixture_id"], w["match"], w["kickoff_utc"],
                                               ",".join(w["key_reasons"])))
        for a in w["actions_needed"]:
            print("        -> %s" % a)


if __name__ == "__main__":
    main()
