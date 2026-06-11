#!/usr/bin/env python3
"""
MVP-2 June 11 trial — trial prediction data frame builder (Task C).

Builds docs/data_audit/mvp2_trial_prediction_frames/{fixture_id}.json for the
opening-window real fixtures: fixture basis + team baseline + extended model
factors + ScoutScore output. Every factor carries source_refs, data_status
(verified|partial|assumption|missing), customer_visible, internal_note.
Engineering computes the frame; the LLM writes the customer language (Task D).

Reuses the Kaggle helpers from scripts/mvp2_build_scoutscore_v0_2_factors.py.
Usage: python3 scripts/mvp2_build_trial_prediction_frame.py [fixture_id ...]
Default: 1489369 1489371
"""
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKS = ROOT / "docs" / "data_audit" / "mvp2_scout_pack_samples"
VERIF = ROOT / "docs" / "data_audit" / "mvp2_june11_real_fixture_verification.json"
OUT = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"

spec = importlib.util.spec_from_file_location("v02", ROOT / "scripts" / "mvp2_build_scoutscore_v0_2_factors.py")
v02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v02)


def factor(name, value, status, visible, note, refs):
    return {"factor": name, "value": value, "data_status": status,
            "customer_visible": visible, "internal_note": note, "source_refs": refs}


def split_trend(matches, key):
    """last-5 vs previous-5 totals for goals_for ('gf') or against ('ga')."""
    def tot(ms):
        return sum(int(m["score"].split("-")[0 if key == "gf" else 1]) for m in ms)
    prev5, last5 = matches[:-5], matches[-5:]
    return {"last5": tot(last5), "prev5": tot(prev5) if prev5 else None}


def build(fid, rows, verif_map):
    pack = json.loads((PACKS / ("%s.json" % fid)).read_text(encoding="utf-8"))
    fx = pack["fixture"]["value"]
    home, away = fx["home_team"]["name"], fx["away_team"]["name"]
    date = fx["date"][:10]
    squad = (pack.get("squad") or {}).get("value") or {}
    coach = (pack.get("coach") or {}).get("value") or {}
    ver = verif_map.get(int(fid), {})

    R = v02.elo_snapshot(rows, date)
    eh, ea = round(R.get(home, 1500)), round(R.get(away, 1500))
    gap = abs(eh - ea)
    fav = home if eh >= ea else away
    dog = away if fav == home else home
    form = {home: v02.recent_form(rows, home, date), away: v02.recent_form(rows, away, date)}
    meetings = v02.h2h(rows, home, away, date)
    scorers = {home: v02.recent_scorers(rows, home, date), away: v02.recent_scorers(rows, away, date)}
    band, band_why = v02.upset_band(gap, 4)
    lam_h = max(0.5, min(2.4, form[home]["goals_for"] / max(1, form[home]["n"]) * 0.85))
    lam_a = max(0.5, min(2.4, form[away]["goals_for"] / max(1, form[away]["n"]) * 0.85))
    bands = v02.poisson_bands(lam_h, lam_a)

    kag = [dict(v02.KAGGLE_REF)]
    pack_ref = lambda field, ep: [{"field": field, "source": "api-football", "endpoint": ep, "fixture_id": int(fid)}]

    def team_block(side, team):
        s = squad.get(side) or {}
        gks = [p["name"] for p in (s.get("sample") or []) if p.get("position") == "Goalkeeper"][:3]
        dep = scorers[team]
        top_share = (dep[0]["goals"] / max(1, form[team]["goals_for"])) if dep else None
        return {
            "team": team, "coach": (coach.get(side) or {}).get("name"),
            "squad_players": s.get("players_count"), "squad_goalkeepers": gks,
            "formation": None,
            "expected_setup_note": "formation not announced — expected tactical setup is an LLM assumption_flag item",
            "top_scorers_last10": dep, "top_scorer_share": round(top_share, 2) if top_share else None,
        }

    cs = {t: sum(1 for m in form[t]["matches"] if m["score"].split("-")[1] == "0") for t in (home, away)}

    factors = [
        factor("baseline_strength", {"elo": {home: eh, away: ea}, "gap": gap, "favoured": fav},
               "verified", True, "derived from kaggle intl results (49k rows, through 2026-06); " + v02.ELO_METHOD, kag),
        factor("recent_form", {t: form[t]["record"] for t in (home, away)},
               "verified", True, "last-10 W/D/L from kaggle results", kag),
        factor("h2h", meetings[-5:], "verified", True, "last meetings incl. WC2010 opener 1-1 (Mexico-South Africa)" if fid == "1489369" else "last meetings incl. Morocco 2-1 Brazil 2023", kag),
        factor("goal_trend", {t: split_trend(form[t]["matches"], "gf") for t in (home, away)},
               "verified", True, "goals scored last5 vs prev5", kag),
        factor("defensive_trend", {t: dict(split_trend(form[t]["matches"], "ga"), clean_sheets_last10=cs[t]) for t in (home, away)},
               "verified", True, "goals against last5 vs prev5 + clean sheets", kag),
        factor("squad_stability", {t: (squad.get(s) or {}).get("players_count") for s, t in (("home", home), ("away", away))},
               "partial", True, "26-man squads registered (real); XI continuity unknown until lineups", pack_ref("squad", "/players/squads")),
        factor("goalkeeper_risk", {t: team_block(s, t)["squad_goalkeepers"] for s, t in (("home", home), ("away", away))},
               "partial", True, "GK names real from squads; starter + form unknown -> 30min recheck", pack_ref("squad", "/players/squads")),
        factor("striker_finishing_risk", {t: {"top_scorers": scorers[t], "share_of_team_goals": team_block(s, t)["top_scorer_share"]} for s, t in (("home", home), ("away", away))},
               "verified", True, "top-scorer dependence from kaggle goalscorers; no xG feed", kag),
        factor("travel_venue_context", {"venue": fx.get("venue"), "kickoff_utc": fx["date"], "round": fx["league"].get("round"),
                                         "context_note": "Estadio Azteca altitude ~2200m + opener crowd" if fid == "1489369" else "US summer heat window"},
               "partial", True, "venue/kickoff verified from /fixtures; altitude/heat/crowd impact is scenario assumption", pack_ref("fixture", "/fixtures")),
        factor("lineup_uncertainty", {"lineups_available": bool(ver.get("lineups_available"))},
               "missing", True, "XI/formation not announced at build time — phrased to customers as the 30min variable", pack_ref("lineups", "/fixtures/lineups")),
        factor("injury_gap", {"injuries_available": bool(ver.get("injuries_available")), "results": 0},
               "missing", False, "0 injury results pre-match (unresolved) — NEVER stated as 'no injuries'; internal only", pack_ref("injuries", "/injuries")),
        factor("live_30min_trigger", {"recompute": ["lineup/XI spine", "starting GK", "formation matchup"],
                                       "reissue": ["primary_lean", "score_range", "risk_level"]},
               "verified", True, "subscription-layer mechanic: re-score ~30' before kickoff", []),
    ]

    flips = [
        "%s announced XI missing 2+ spine starters (CB/GK/striker)" % fav,
        "%s starting GK on a hot streak (validated only in-match)" % dog,
        "early goal for %s flips momentum exposure (opener nerves)" % dog,
        "weather/altitude visibly degrading %s pressing intensity" % fav,
    ]
    frame = {
        "sprint": "MVP-2 June 11 Real Match Trial Prediction",
        "model_name": "ScoutScore v0.2-trial", "fixture_basis": "real_scheduled",
        "generated_by": "scripts/mvp2_build_trial_prediction_frame.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture": {"fixture_id": int(fid), "match": "%s vs %s" % (home, away), "kickoff": fx["date"],
                    "venue": fx.get("venue"), "group_round": fx["league"].get("round"), "status": fx.get("status")},
        "team_baseline": {"home": team_block("home", home), "away": team_block("away", away)},
        "factors": factors,
        "scoutscore_output": {
            "primary_lean": {"side": fav, "strength": "slight" if gap < 60 else "clear",
                             "basis": "elo gap %d + form" % gap, "label": "model_estimate"},
            "score_range": {"bands": bands, "label": "model_estimate",
                            "method": "poisson(last10 gf avg, group-stage damped) — coarse, never a claim"},
            "risk_level": band, "risk_why": band_why,
            "key_risk_variables": ["lineup_uncertainty", "goalkeeper_risk", "striker_finishing_risk",
                                    "travel_venue_context" if fid == "1489369" else "defensive_trend"],
            "what_could_flip": flips,
            "recheck_30min": ["announced XI vs expected spine", "starting GK", "formation collision",
                              "late injury/suspension news (currently unresolved)"],
        },
        "verification_ref": "docs/data_audit/mvp2_june11_real_fixture_verification.json",
        "source_ledger_ref": "docs/data_audit/mvp2_scout_pack_samples/%s.json#source_ledger" % fid,
    }
    return frame


def main():
    fids = sys.argv[1:] or ["1489369", "1489371"]
    rows = v02.load_results()
    verif = json.loads(VERIF.read_text(encoding="utf-8"))
    verif_map = {r["fixture_id"]: r for r in verif.get("verified_candidates", [])}
    OUT.mkdir(parents=True, exist_ok=True)
    for fid in fids:
        fr = build(fid, rows, verif_map)
        p = OUT / ("%s.json" % fid)
        p.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        o = fr["scoutscore_output"]
        print("saved %s  lean=%s risk=%s bands=%s" % (p.relative_to(ROOT), o["primary_lean"]["side"], o["risk_level"], o["score_range"]["bands"]))


if __name__ == "__main__":
    main()
