#!/usr/bin/env python3
"""
ScoutScore v0.2 factor-frame builder (engineering stage — NOT narrative).

Builds the per-fixture factor frame defined in docs/MVP2_SCOUTSCORE_V0_2_MODELING_FRAME.md:
  - Kaggle-derived Elo snapshot (start 1500, K=32, +60 home when not neutral) at match eve
  - recent form (last 10), H2H, shootout history from data/external/kaggle/*.csv (local, untracked)
  - Scout Pack extraction (stats / GK / events momentum / formation) for the two recap fixtures
  - the v0.2 factor set with source_refs (real) or assumption flags (gaps) — never invented numbers

Outputs docs/data_audit/mvp2_scoutscore_v0_2/{855737,979139,2026_brazil_argentina}.factor_frame.json,
consumed by scripts/mvp2_generate_product_proof_narratives.py. Interpretation strings here are terse
model-internal notes (inputs to the LLM) — the customer-facing language is written by the LLM only.

Usage: python3 scripts/mvp2_build_scoutscore_v0_2_factors.py
"""
import csv
import json
import math
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
KAGGLE = ROOT / "data" / "external" / "kaggle"
PACKS = ROOT / "docs" / "data_audit" / "mvp2_scout_pack_samples"
OUT = ROOT / "docs" / "data_audit" / "mvp2_scoutscore_v0_2"

KAGGLE_REF = {"source": "kaggle_intl_results", "dataset": "international football results 1872-2026 (results/shootouts/goalscorers.csv, local data/external/kaggle)", "derived": True}
ELO_METHOD = "elo: start 1500, K=32, home +60 when neutral=FALSE, ordered by date (see MVP2_SCOUTSCORE_V0_2_MODELING_FRAME.md §3)"


# ── Kaggle baseline ──────────────────────────────────────────────────────────
def load_results():
    rows = []
    with open(KAGGLE / "results.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hs, as_ = r["home_score"], r["away_score"]
            if not hs or hs == "NA" or not as_ or as_ == "NA":
                continue  # future fixtures have NA scores
            rows.append({
                "date": r["date"], "home": r["home_team"], "away": r["away_team"],
                "hs": int(float(hs)), "as": int(float(as_)),
                "tournament": r["tournament"], "neutral": r["neutral"].strip().upper() == "TRUE",
            })
    rows.sort(key=lambda x: x["date"])
    return rows


def elo_snapshot(rows, cutoff):
    """Ratings using all matches strictly before cutoff (ISO date string)."""
    R = {}
    for m in rows:
        if m["date"] >= cutoff:
            break
        ra, rb = R.get(m["home"], 1500.0), R.get(m["away"], 1500.0)
        adv = 0 if m["neutral"] else 60
        ea = 1.0 / (1.0 + 10 ** ((rb - (ra + adv)) / 400.0))
        sa = 1.0 if m["hs"] > m["as"] else 0.0 if m["hs"] < m["as"] else 0.5
        R[m["home"]] = ra + 32 * (sa - ea)
        R[m["away"]] = rb + 32 * ((1 - sa) - (1 - ea))
    return R


def recent_form(rows, team, cutoff, n=10):
    ms = [m for m in rows if m["date"] < cutoff and team in (m["home"], m["away"])][-n:]
    out, gf, ga, w, d, l = [], 0, 0, 0, 0, 0
    for m in ms:
        mine, theirs = (m["hs"], m["as"]) if m["home"] == team else (m["as"], m["hs"])
        opp = m["away"] if m["home"] == team else m["home"]
        res = "W" if mine > theirs else "L" if mine < theirs else "D"
        w, d, l = w + (res == "W"), d + (res == "D"), l + (res == "L")
        gf, ga = gf + mine, ga + theirs
        out.append({"date": m["date"], "opponent": opp, "score": "%d-%d" % (mine, theirs), "result": res, "tournament": m["tournament"]})
    return {"matches": out, "record": "%dW-%dD-%dL" % (w, d, l), "goals_for": gf, "goals_against": ga, "n": len(ms)}


def h2h(rows, a, b, cutoff, n=10):
    ms = [m for m in rows if m["date"] < cutoff and {m["home"], m["away"]} == {a, b}][-n:]
    return [{"date": m["date"], "fixture": "%s %d-%d %s" % (m["home"], m["hs"], m["as"], m["away"]), "tournament": m["tournament"]} for m in ms]


def shootout_lookup(date, a, b):
    with open(KAGGLE / "shootouts.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["date"] == date and {r["home_team"], r["away_team"]} == {a, b}:
                return r.get("winner")
    return None


def shootout_history(team, cutoff, n=5):
    rows = []
    with open(KAGGLE / "shootouts.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["date"] < cutoff and team in (r["home_team"], r["away_team"]):
                rows.append({"date": r["date"], "vs": r["away_team"] if r["home_team"] == team else r["home_team"],
                             "won": r.get("winner") == team})
    return rows[-n:]


def recent_scorers(rows, team, cutoff, n_matches=10, top=4):
    window = [m["date"] for m in rows if m["date"] < cutoff and team in (m["home"], m["away"])][-n_matches:]
    if not window:
        return []
    lo = min(window)
    counts = {}
    with open(KAGGLE / "goalscorers.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if lo <= r["date"] < cutoff and r["team"] == team and r.get("scorer"):
                counts[r["scorer"]] = counts.get(r["scorer"], 0) + 1
    return sorted(({"scorer": k, "goals": v} for k, v in counts.items()), key=lambda x: -x["goals"])[:top]


# ── Scout Pack extraction (recap fixtures) ───────────────────────────────────
def pack_extract(fid):
    d = json.loads((PACKS / ("%s.json" % fid)).read_text(encoding="utf-8"))
    fx = d["fixture"]["value"]
    stats = {t["team"]: t["stats"] for t in d["team_statistics"]["value"]}
    tops = {t["team"]: t["top_by_rating"] for t in d["player_statistics"]["value"]}
    gk = {team: next((p for p in lst if p.get("pos") == "G"), None) for team, lst in tops.items()}
    tl = d["events_summary"]["value"]["timeline"]
    goals_reg = [e for e in tl if e["type"] == "Goal" and isinstance(e["minute"], int)]
    shootout = [e for e in tl if e["type"] in ("Goal", "Missed Penalty") and not isinstance(e["minute"], int)]
    return {
        "fixture": fx, "stats": stats, "top_by_rating": tops, "gk": gk,
        "formation": d["formation"]["value"], "coach": d["coach"]["value"],
        "goals_regulation_and_et": [{"minute": g["minute"], "team": g["team"], "player": g["player"], "detail": g["detail"]} for g in goals_reg],
        "shootout_events_note": "timeline entries at minute '120+x' are SHOOTOUT kicks, not match goals" if shootout else None,
        "missing_evidence": d.get("missing_evidence"),
    }


def ref(field, endpoint, fid, value=None):
    r = {"field": field, "source": "api-football", "endpoint": endpoint, "fixture_id": fid}
    if value is not None:
        r["value"] = value
    return r


def kref(metric, value=None):
    r = dict(KAGGLE_REF); r["metric"] = metric
    if value is not None:
        r["value"] = value
    return r


# ── factor assembly ──────────────────────────────────────────────────────────
def num(x):
    try:
        return float(str(x).replace("%", ""))
    except (TypeError, ValueError):
        return None


def upset_band(elo_gap, missing_count):
    if elo_gap < 60:
        return "volatility", "near-even strength: risk is volatility (draw/late swing/pens), not a one-sided upset"
    if elo_gap > 150 and missing_count >= 3:
        return "high", "big favourite + model blind spots (lineup/injury/xG not ingested) = classic blind-favourite trap"
    return "medium", "clear favourite but gaps are partially covered"


def poisson_bands(lam_h, lam_a, top=3):
    """Top scorelines from two independent Poissons (coarse model_estimate basis)."""
    def pmf(lam, k):
        return math.exp(-lam) * lam ** k / math.factorial(k)
    grid = [(h, a, pmf(lam_h, h) * pmf(lam_a, a)) for h in range(5) for a in range(5)]
    grid.sort(key=lambda x: -x[2])
    return ["%d-%d" % (h, a) for h, a, _ in grid[:top]]


def recap_frame(fid, rows):
    p = pack_extract(fid)
    fx = p["fixture"]
    home, away = fx["home_team"]["name"] if isinstance(fx.get("home_team"), dict) else fx["home_team"], None
    # scout packs store home/away under fixture.home_team/away_team or via formation block
    if isinstance(fx.get("home_team"), dict):
        home, away = fx["home_team"]["name"], fx["away_team"]["name"]
    else:
        home, away = p["formation"]["home"]["team"], p["formation"]["away"]["team"]
    date = fx["date"][:10]
    R = elo_snapshot(RESULTS, date)
    eh, ea = round(R.get(home, 1500)), round(R.get(away, 1500))
    gap = abs(eh - ea)
    fav = home if eh >= ea else away
    dog = away if fav == home else home
    form = {home: recent_form(RESULTS, home, date), away: recent_form(RESULTS, away, date)}
    s_h, s_a = p["stats"][home], p["stats"][away]
    sog_h, sog_a = s_h.get("Shots on Goal"), s_a.get("Shots on Goal")
    shots_h, shots_a = s_h.get("Total Shots"), s_a.get("Total Shots")
    saves_h, saves_a = s_h.get("Goalkeeper Saves"), s_a.get("Goalkeeper Saves")
    poss_h, poss_a = s_h.get("Ball Possession"), s_a.get("Ball Possession")
    score = fx["final_score"]
    goals = p["goals_regulation_and_et"]
    miss_n = 3  # injuries, xG, squad value — still not ingested
    band, band_why = upset_band(gap, miss_n)
    gk_rows = {t: g for t, g in p["gk"].items() if g}

    factors = [
        {"factor": "baseline_strength", "value": {"elo": {home: eh, away: ea}, "gap": gap, "favoured": fav},
         "pre_match_interpretation": "kaggle-derived elo favours %s by %d" % (fav, gap),
         "post_match_validation": "favourite %s; final %s-%s (%s won)" % (fav, score["home"], score["away"], fx.get("result_winner")),
         "source_refs": [kref("elo_snapshot@" + date, "%s %d / %s %d" % (home, eh, away, ea)), {"method": ELO_METHOD}],
         "assumption": False, "data_status": "derived"},
        {"factor": "recent_form", "value": {home: form[home]["record"], away: form[away]["record"]},
         "pre_match_interpretation": "last-10: %s %s (gf%d ga%d) vs %s %s (gf%d ga%d)" % (
             home, form[home]["record"], form[home]["goals_for"], form[home]["goals_against"],
             away, form[away]["record"], form[away]["goals_for"], form[away]["goals_against"]),
         "post_match_validation": "see result", "source_refs": [kref("last10_form")], "assumption": False, "data_status": "derived"},
        {"factor": "lineup_integrity", "value": {"formation": p["formation"]},
         "pre_match_interpretation": "formations %s vs %s (read from match lineups — replay, not a true pre-match feed)" % (
             p["formation"]["home"]["formation"], p["formation"]["away"]["formation"]),
         "post_match_validation": "lineups as fielded", "source_refs": [ref("lineups", "/fixtures/lineups", fid)],
         "assumption": False, "data_status": "replay_only"},
        {"factor": "finishing_efficiency", "value": {"shots": {home: shots_h, away: shots_a}, "sog": {home: sog_h, away: sog_a}, "goals": {home: score["home"], away: score["away"]}},
         "pre_match_interpretation": "no pre-match xG feed — efficiency was a blind spot",
         "post_match_validation": "%s %s shots / %s on target -> %s goals; %s %s shots / %s on target -> %s goals" % (
             home, shots_h, sog_h, score["home"], away, shots_a, sog_a, score["away"]),
         "source_refs": [ref("team_statistics", "/fixtures/statistics", fid, "shots %s/%s, sog %s/%s" % (shots_h, shots_a, sog_h, sog_a))],
         "assumption": False, "data_status": "observed"},
        {"factor": "goalkeeper_delta", "value": {"saves": {home: saves_h, away: saves_a},
                                                  "gk_rating": {t: g.get("rating") for t, g in gk_rows.items()}},
         "pre_match_interpretation": "no pre-match GK form feed",
         "post_match_validation": "saves %s vs %s%s" % (saves_h, saves_a,
             "; " + " / ".join("%s GK %s rated %s" % (t, g["name"], g["rating"]) for t, g in gk_rows.items()) if gk_rows else ""),
         "source_refs": [ref("team_statistics", "/fixtures/statistics", fid, "saves %s/%s" % (saves_h, saves_a)),
                         ref("player_statistics", "/fixtures/players", fid)],
         "assumption": False, "data_status": "observed"},
        {"factor": "event_momentum", "value": {"goal_timeline": goals},
         "pre_match_interpretation": "momentum windows are an in-match risk; pre-match proxy = comeback exposure of the favourite",
         "post_match_validation": "; ".join("%s' %s (%s)" % (g["minute"], g["team"], g["player"]) for g in goals),
         "source_refs": [ref("events", "/fixtures/events", fid)], "assumption": False, "data_status": "observed"},
        {"factor": "tactical_matchup", "value": {"coach": {k: v["name"] for k, v in p["coach"].items()},
                                                  "formations": "%s vs %s" % (p["formation"]["home"]["formation"], p["formation"]["away"]["formation"])},
         "pre_match_interpretation": "style collision read from formations/coaches (replay)",
         "post_match_validation": "possession %s vs %s" % (poss_h, poss_a),
         "source_refs": [ref("lineups+coach", "/fixtures/lineups", fid), ref("team_statistics", "/fixtures/statistics", fid, "possession %s/%s" % (poss_h, poss_a))],
         "assumption": False, "data_status": "replay_only"},
        {"factor": "travel_environment", "value": {"venue": fx.get("venue"), "neutral": True},
         "pre_match_interpretation": "Qatar 2022 neutral venue — low differential impact assumed",
         "post_match_validation": "not a differentiator in this match",
         "source_refs": [ref("fixture", "/fixtures", fid)], "assumption": True, "data_status": "context"},
        {"factor": "missing_data_risk", "value": {"not_ingested": ["injuries/suspensions", "xG", "squad market value"]},
         "pre_match_interpretation": "model was blind on injuries, xG, squad value at kickoff",
         "post_match_validation": "gaps stand; efficiency/GK signals had to be discovered in-match",
         "source_refs": [], "assumption": True, "data_status": "missing"},
        {"factor": "upset_risk", "value": {"band": band},
         "pre_match_interpretation": band_why,
         "post_match_validation": "final %s-%s" % (score["home"], score["away"]),
         "source_refs": [{"method": "upset_band(elo_gap=%d, missing=%d)" % (gap, miss_n)}], "assumption": False, "data_status": "derived"},
    ]
    lam_h = max(0.4, min(2.6, form[home]["goals_for"] / max(1, form[home]["n"]) + (0.25 if fav == home else -0.15)))
    lam_a = max(0.4, min(2.6, form[away]["goals_for"] / max(1, form[away]["n"]) + (0.25 if fav == away else -0.15)))
    frame = {
        "model_name": "ScoutScore v0.2", "mode": "historical_recap", "fixture_id": fid,
        "generated_by": "scripts/mvp2_build_scoutscore_v0_2_factors.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "not_real_archived_prediction": True,
        "fixture": {"home": home, "away": away, "date": fx["date"], "venue": fx.get("venue"),
                    "competition": "%s %s" % (fx["league"]["name"], fx["league"].get("season", "")),
                    "final_score": score, "result_winner": fx.get("result_winner"),
                    "shootout_winner": shootout_lookup(date, home, away)},
        "kaggle_baseline": {"elo": {home: eh, away: ea, "gap": gap, "favoured": fav, "asof": date, "method": ELO_METHOD},
                            "recent_form": form, "h2h_last10": h2h(RESULTS, home, away, date)},
        "factors": factors,
        "shootout_events_note": p["shootout_events_note"],
        "live_30min_update_trigger": {
            "would_recompute": ["lineup_integrity", "goalkeeper_delta", "tactical_matchup"],
            "then_reissue": ["main_lean", "scoreline_band", "risk_level"],
            "note": "recap framing: what a live pre-match run would re-check 30' before kickoff"},
        "outputs": {
            "pre_match_main_lean": {"side": fav, "basis": "elo gap %d + form" % gap, "label": "model_estimate"},
            "risk_level_basis": band,
            "scoreline_band_basis": {"plausible_bands": poisson_bands(lam_h, lam_a),
                                      "method": "poisson(last10 gf/avg, elo-adjusted) — coarse model_estimate, NOT a claim",
                                      "label": "model_estimate"},
            "underdog": dog,
        },
        "known_gaps": ["injuries/suspensions not ingested", "xG not ingested", "squad market value not ingested",
                       "official FIFA ranking not ingested (kaggle-derived elo used instead)"],
        "source_ledger_ref": "docs/data_audit/mvp2_scout_pack_samples/%s.json#source_ledger" % fid,
    }
    return frame


def prematch_2026_frame(rows):
    sid = "2026_brazil_argentina"
    a, b = "Brazil", "Argentina"
    cutoff = "2026-06-11"
    R = elo_snapshot(rows, cutoff)
    eb_, ea_ = round(R.get(a, 1500)), round(R.get(b, 1500))
    gap = abs(eb_ - ea_)
    fav = a if eb_ >= ea_ else b
    form = {a: recent_form(rows, a, cutoff), b: recent_form(rows, b, cutoff)}
    meetings = h2h(rows, a, b, cutoff)
    scorers = {a: recent_scorers(rows, a, cutoff), b: recent_scorers(rows, b, cutoff)}
    sh = {a: shootout_history(a, cutoff), b: shootout_history(b, cutoff)}
    band, band_why = upset_band(gap, 4)
    lam_a = max(0.5, min(2.4, form[a]["goals_for"] / max(1, form[a]["n"]) * 0.75))   # WC-knockout damping
    lam_b = max(0.5, min(2.4, form[b]["goals_for"] / max(1, form[b]["n"]) * 0.75))
    wc_group = {a: [m for m in ("Brazil-Morocco 06-13", "Brazil-Haiti 06-19", "Scotland-Brazil 06-24")],
                b: [m for m in ("Argentina-Algeria 06-16", "Argentina-Austria 06-22", "Jordan-Argentina 06-27")]}

    factors = [
        {"factor": "baseline_strength", "value": {"elo": {a: eb_, b: ea_}, "gap": gap, "favoured": fav},
         "pre_match_interpretation": "kaggle-derived elo: %s %d vs %s %d (gap %d)" % (a, eb_, b, ea_, gap),
         "source_refs": [kref("elo_snapshot@" + cutoff, "%s %d / %s %d" % (a, eb_, b, ea_)), {"method": ELO_METHOD}],
         "assumption": False, "data_status": "derived"},
        {"factor": "recent_form", "value": {a: form[a]["record"], b: form[b]["record"]},
         "pre_match_interpretation": "last-10: %s %s (gf%d ga%d) vs %s %s (gf%d ga%d); includes 2026-03/06 friendlies" % (
             a, form[a]["record"], form[a]["goals_for"], form[a]["goals_against"],
             b, form[b]["record"], form[b]["goals_for"], form[b]["goals_against"]),
         "source_refs": [kref("last10_form")], "assumption": False, "data_status": "derived"},
        {"factor": "lineup_integrity", "value": None,
         "pre_match_interpretation": "no lineup feed yet — both squads unannounced; becomes a live-30min trigger",
         "source_refs": [], "assumption": True, "data_status": "assumption_context"},
        {"factor": "finishing_efficiency", "value": {"recent_scorers": scorers},
         "pre_match_interpretation": "proxy = last-10 goals-for + scorer spread; no xG feed",
         "source_refs": [kref("goalscorers_last10")], "assumption": False, "data_status": "derived_proxy"},
        {"factor": "goalkeeper_delta", "value": None,
         "pre_match_interpretation": "no GK form feed — flagged as pre-match watch variable",
         "source_refs": [], "assumption": True, "data_status": "assumption_context"},
        {"factor": "event_momentum", "value": {"h2h_volatility": meetings[-5:], "shootout_history": sh},
         "pre_match_interpretation": "knockout context: late-swing + pens exposure judged from h2h and shootout records",
         "source_refs": [kref("h2h+shootouts")], "assumption": False, "data_status": "derived"},
        {"factor": "tactical_matchup", "value": None,
         "pre_match_interpretation": "2026 formations/coach plans not ingested — assumption_context for the LLM",
         "source_refs": [], "assumption": True, "data_status": "assumption_context"},
        {"factor": "travel_environment", "value": {"context": "2026 US summer venues; heat/travel between host cities",
                                                    "group_schedule": wc_group},
         "pre_match_interpretation": "group schedules are real (results.csv 2026 fixtures); venue/heat impact for a knockout meeting is scenario context",
         "source_refs": [kref("2026_group_fixtures")], "assumption": True, "data_status": "mixed"},
        {"factor": "missing_data_risk", "value": {"not_ingested": ["injuries/suspensions", "xG", "squad market value", "official FIFA rank", "2026 knockout venue"]},
         "pre_match_interpretation": "pre-match blind spots -> phrased to the user as variables to track",
         "source_refs": [], "assumption": True, "data_status": "missing"},
        {"factor": "upset_risk", "value": {"band": band},
         "pre_match_interpretation": band_why,
         "source_refs": [{"method": "upset_band(elo_gap=%d, missing=4)" % gap}], "assumption": False, "data_status": "derived"},
    ]
    frame = {
        "model_name": "ScoutScore v0.2", "mode": "pre_match_2026_modeling", "fixture_id": sid,
        "generated_by": "scripts/mvp2_build_scoutscore_v0_2_factors.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hypothetical_fixture": True,
        "hypothetical_note": "Brazil vs Argentina is NOT scheduled in the 2026 group stage — both are group hosts' side; a meeting is a knockout scenario. Customer copy must say 'if they meet in the knockouts'.",
        "fixture": {"home": a, "away": b, "date": None, "venue": None, "competition": "FIFA World Cup 2026 (hypothetical knockout meeting)"},
        "kaggle_baseline": {"elo": {a: eb_, b: ea_, "gap": gap, "favoured": fav, "asof": cutoff, "method": ELO_METHOD},
                            "recent_form": form, "h2h_last10": meetings,
                            "recent_scorers": scorers, "shootout_history": sh},
        "factors": factors,
        "live_30min_update_trigger": {
            "would_recompute": ["lineup_integrity (XI in/out, spine changes)", "goalkeeper_delta (starting GK)", "tactical_matchup (formation)"],
            "then_reissue": ["main_lean", "scoreline_band", "risk_level"],
            "note": "this is the subscription-layer live update: 30' before kickoff the model re-scores and re-issues its lean"},
        "outputs": {
            "pre_match_main_lean": {"side": fav, "strength": "slight" if gap < 60 else "clear", "basis": "elo gap %d + form" % gap, "label": "model_estimate"},
            "risk_level_basis": band,
            "scoreline_band_basis": {"plausible_bands": poisson_bands(lam_a, lam_b),
                                      "method": "poisson(last10 gf avg, knockout-damped) — coarse model_estimate, NOT a claim",
                                      "label": "model_estimate"},
        },
        "known_gaps": ["injuries/suspensions not ingested", "xG not ingested", "squad market value not ingested",
                       "official FIFA ranking not ingested (kaggle-derived elo used)", "no scheduled fixture — hypothetical knockout"],
        "source_ledger_ref": "data/external/kaggle (local, untracked raw)",
    }
    return frame


def main():
    global RESULTS
    RESULTS = load_results()
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [recap_frame("855737", RESULTS), recap_frame("979139", RESULTS), prematch_2026_frame(RESULTS)]
    for fr in frames:
        p = OUT / ("%s.factor_frame.json" % fr["fixture_id"])
        p.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("saved %s  (mode=%s, lean=%s, risk=%s)" % (
            p.relative_to(ROOT), fr["mode"],
            fr["outputs"]["pre_match_main_lean"]["side"], fr["outputs"]["risk_level_basis"]))


if __name__ == "__main__":
    RESULTS = None
    main()
