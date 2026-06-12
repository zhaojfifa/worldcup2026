#!/usr/bin/env python3
"""
MVP-2 Track A+ — facts-only EVENT IMPACT + EXTENDED DIMENSIONS builders
(Evidence Expansion Sprint, Owner verdict 2026-06-12).

Engineering produces FACTS ONLY here — minutes, scores, man counts, rule-derived
flags with reason codes. The LLM writes every customer sentence afterwards, gated
by the guard. Nothing in this module is customer prose.

build_event_impact(fid)            -> event impact layer for a finished fixture:
    phase timeline (0-15 / 16-30 / 31-45+ / 46-60 / 61-75 / 76-90+ / 91-105 /
    106-120+ / shootout), halftime + final score, decisive events (red cards,
    penalties, goals, VAR if present) each with minute / team / player /
    event_type / score_before / score_after / man_count before+after /
    tactical_effect (factual descriptor) / changed_risk_interpretation
    (rule-derived bool + reason) / prematch_judgement_relation
    (validates | weakens | neutral, rule-derived vs the favoured side),
    substitutions (incl. possible forced subs near injuries — flagged unknown),
    goalkeeper signal from player stats when available.

build_extended_dimensions(fid, ...) -> 17 football-intelligence dimensions, each
    {dimension, value, source, confidence, customer_visible_summary,
     internal_note, missing_evidence}. Dimensions without a real source are
    flagged missing_evidence=true with the needed source named — NEVER invented
    (no ages exist in the scout pack: age dims stay missing until a squad-age
    source is ingested).

Used by scripts/mvp2_build_scoutscore_v0_2_factors.py (recap_frame) so both
historical_recap (979139) and real_recap (1489369) frames carry the layers.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKS = ROOT / "docs" / "data_audit" / "mvp2_scout_pack_samples"

PHASES = (("0-15", 0, 15), ("16-30", 16, 30), ("31-45+", 31, 45), ("46-60", 46, 60),
          ("61-75", 61, 75), ("76-90+", 76, 90), ("91-105", 91, 105), ("106-120+", 106, 120))


def _minute_parts(m):
    """'90+2' -> (90, 2); 49 -> (49, 0); shootout strings beyond 120 keep base 120."""
    if isinstance(m, int):
        return m, 0
    mm = re.match(r"^\s*(\d+)\s*\+\s*(\d+)\s*$", str(m))
    if mm:
        return int(mm.group(1)), int(mm.group(2))
    mm = re.match(r"^\s*(\d+)\s*$", str(m))
    return (int(mm.group(1)), 0) if mm else (None, None)


def _phase(base):
    for name, lo, hi in PHASES:
        if lo <= base <= hi:
            return name
    return "106-120+" if base and base > 120 else None


def _pack(fid):
    return json.loads((PACKS / ("%s.json" % fid)).read_text(encoding="utf-8"))


def _ordered_timeline(pack):
    tl = (pack.get("events_summary") or {}).get("value", {}).get("timeline") or []
    out = []
    for e in tl:
        base, extra = _minute_parts(e.get("minute"))
        if base is None:
            continue
        out.append({**e, "_base": base, "_extra": extra,
                    "_shootout": base >= 120 and extra > 0 and e.get("type") in ("Goal", "Missed Penalty")})
    out.sort(key=lambda x: (x["_base"], x["_extra"]))
    return out


def _teams(pack):
    fx = pack["fixture"]["value"]
    if isinstance(fx.get("home_team"), dict):
        return fx["home_team"]["name"], fx["away_team"]["name"]
    fv = pack["formation"]["value"]
    return fv["home"]["team"], fv["away"]["team"]


def build_event_impact(fid, favoured=None, underdog=None):
    pack = _pack(fid)
    home, away = _teams(pack)
    fx = pack["fixture"]["value"]
    tl = _ordered_timeline(pack)
    src = {"endpoint": "/fixtures/events", "fixture_id": str(fid),
           "note": "facts only; every flag below is rule-derived (reason given), not narrative"}

    score = {home: 0, away: 0}
    men = {home: 11, away: 11}
    half_time = None
    phases = {name: [] for name, _, _ in PHASES}
    decisive, subs, cards = [], [], []
    sub_off_on_note = "events 'subst': player = OFF, assist = ON (verified vs 979139 Giroud 41')"

    for e in tl:
        if e["_shootout"]:
            continue
        base, team, typ, detail = e["_base"], e.get("team"), e.get("type"), e.get("detail") or ""
        if half_time is None and base > 45:
            half_time = dict(score)
        before = dict(score)
        is_goal = typ == "Goal" and detail != "Missed Penalty"
        if is_goal and team in score:
            score[team] += 1
        entry = {"minute": e.get("minute"), "phase": _phase(base), "team": team,
                 "player": e.get("player"), "type": typ, "detail": detail}
        ph = _phase(base)
        if ph:
            phases[ph].append(entry)

        if typ == "subst":
            subs.append({"minute": e.get("minute"), "team": team,
                         "off": e.get("player"), "on": e.get("assist"),
                         "forced_by_injury": "unknown (no injury feed — never inferred)"})
            continue
        if typ == "Card":
            cards.append({"minute": e.get("minute"), "team": team, "player": e.get("player"), "detail": detail})

        red = typ == "Card" and "Red" in detail
        pen_goal = is_goal and "Penalty" in detail
        var = typ == "Var"
        if not (red or pen_goal or is_goal or var):
            continue

        if red and team in men:
            men[team] -= 1
        opp = away if team == home else home
        etype = ("red_card" if red else "penalty_goal" if pen_goal else
                 "var" if var else "goal")
        # rule-derived relation to the pre-match lean (facts: who was favoured + state)
        relation, reason, risk_change = "neutral", "", False
        if favoured:
            lead = score.get(favoured, 0) - score.get(opp if favoured == team else team, 0)
            if red:
                if team != favoured:
                    relation, risk_change = "validates", True
                    reason = ("underdog %s to %d men at %s' while %s — favourite path eased by the event, "
                              "not only by baseline strength" % (team, men[team], e.get("minute"),
                              "trailing %d-%d" % (before[home], before[away]) if before[opp] > before[team]
                              else "level/leading %d-%d" % (before[home], before[away])))
                else:
                    relation, risk_change = "weakens", True
                    reason = "favourite %s reduced to %d men at %s'" % (team, men[team], e.get("minute"))
            elif is_goal:
                relation = "validates" if team == favoured else "weakens"
                reason = "%s goal at %s' -> %d-%d (favourite was %s)" % (team, e.get("minute"),
                                                                          score[home], score[away], favoured)
        tactical = []
        if red:
            tactical.append("%s down to %d men from %s' (score %d-%d at the time)"
                            % (team, men[team], e.get("minute"), before[home], before[away]))
        if pen_goal:
            tactical.append("penalty converted by %s (%s)" % (e.get("player"), team))
        if is_goal and not pen_goal:
            tactical.append("score %d-%d -> %d-%d" % (before[home], before[away], score[home], score[away]))
        man_note = None
        if is_goal and men[home] != men[away]:
            adv = home if men[home] > men[away] else away
            if team == adv:
                man_note = "goal scored WITH a man advantage (%d v %d since earlier red card)" % (
                    men[adv], men[away if adv == home else home])
                tactical.append(man_note)
        decisive.append({
            "minute": e.get("minute"), "phase": _phase(base), "team": team, "player": e.get("player"),
            "event_type": etype, "detail": detail,
            "score_before": {home: before[home], away: before[away]},
            "score_after": {home: score[home], away: score[away]},
            "men_on_pitch_after": dict(men),
            "tactical_effect": "; ".join(tactical),
            "changed_risk_interpretation": {"flag": risk_change, "reason": reason or "no rule fired"},
            "prematch_judgement_relation": {"relation": relation, "reason": reason or "no favoured side supplied",
                                            "basis": "rule-derived vs favoured=%s" % favoured},
        })

    if half_time is None:
        half_time = dict(score)
    # goalkeeper decisive signal (player stats; observed post-match only)
    gk_signal = []
    for trow in (pack.get("player_statistics") or {}).get("value") or []:
        g = next((x for x in trow.get("top_by_rating", []) if x.get("pos") == "G"), None)
        if g:
            gk_signal.append({"team": trow.get("team"), "gk": g.get("name"), "rating": g.get("rating"),
                              "minutes": g.get("minutes"),
                              "saves_team_stat": next((t["stats"].get("Goalkeeper Saves")
                                                       for t in (pack.get("team_statistics") or {}).get("value") or []
                                                       if t.get("team") == trow.get("team")), None)})
    reds = [c for c in cards if "Red" in c["detail"]]
    return {
        "source": src, "sub_mapping_note": sub_off_on_note,
        "halftime_score": {home: half_time[home], away: half_time[away]},
        "final_score_regulation_and_et": {home: score[home], away: score[away]},
        "phases": phases,
        "decisive_events": decisive,
        "substitutions": subs,
        "cards": {"all": cards, "red_count": {home: sum(1 for c in reds if c["team"] == home),
                                              away: sum(1 for c in reds if c["team"] == away)}},
        "goalkeeper_signal": gk_signal,
        "var_available": any(e.get("type") == "Var" for e in tl),
        "injury_feed_available": False,
    }


# ── extended football-intelligence dimensions ────────────────────────────────
def _dim(name, value, source, confidence, summary, note, missing=False):
    return {"dimension": name, "value": value, "source": source, "confidence": confidence,
            "customer_visible_summary": summary, "internal_note": note, "missing_evidence": missing}


def _missing(name, needed):
    return _dim(name, None, None, "none", None,
                "NO SOURCE — needs %s; never invent (guard bans unsourced exact claims)" % needed, missing=True)


def build_extended_dimensions(fid, favoured=None, shootout_history=None, round_label=None):
    pack = _pack(fid)
    home, away = _teams(pack)
    ei = build_event_impact(fid, favoured=favoured)
    stats = {t["team"]: t["stats"] for t in (pack.get("team_statistics") or {}).get("value") or []}
    tops = {t["team"]: t.get("top_by_rating", []) for t in (pack.get("player_statistics") or {}).get("value") or []}
    pstats_src = "/fixtures/players"
    dims = []

    # load: top-rated players' minutes/goals (observed)
    load = {team: [{"name": p.get("name"), "minutes": p.get("minutes"), "rating": p.get("rating"),
                    "goals": p.get("goals"), "assists": p.get("assists")} for p in lst[:3]]
            for team, lst in tops.items()}
    dims.append(_dim("key_player_load", load, pstats_src, "high",
                     "top performers' minutes and direct goal involvement (observed this match)",
                     "post-match observation; season-long workload feed NOT ingested — do not claim "
                     "cumulative fatigue numbers"))
    et_minutes = any(isinstance(p.get("minutes"), int) and p["minutes"] > 95 for lst in tops.values() for p in lst)
    dims.append(_dim("extra_time_fatigue",
                     {"extra_time_played": et_minutes,
                      "players_over_110min": [p.get("name") for lst in tops.values() for p in lst
                                              if isinstance(p.get("minutes"), int) and p["minutes"] >= 110]},
                     pstats_src, "high" if et_minutes else "n/a",
                     "who carried 110+ minutes" if et_minutes else None,
                     "minutes are per-match facts; physiological fatigue is interpretation — LLM territory",
                     missing=not tops))
    subs_by_team = {}
    for s in ei["substitutions"]:
        subs_by_team.setdefault(s["team"], []).append(s)
    dims.append(_dim("substitution_depth",
                     {t: {"used": len(v), "minutes": [s["minute"] for s in v]} for t, v in subs_by_team.items()},
                     "/fixtures/events", "high",
                     "substitution windows actually used",
                     "bench SIZE/quality needs squad-value or rating source (not ingested)"))
    sub_ons = {s["on"] for s in ei["substitutions"] if s.get("on")}
    bench_impact = [d for d in ei["decisive_events"] if d["event_type"] in ("goal", "penalty_goal")
                    and d.get("player") in sub_ons]
    dims.append(_dim("bench_quality",
                     {"goals_by_substitutes": [{"minute": b["minute"], "team": b["team"], "player": b["player"]}
                                               for b in bench_impact]} if tops else None,
                     "/fixtures/events", "medium" if tops else "none",
                     "substitute goal involvement (observed)" if bench_impact else None,
                     "observed impact only — market-value bench depth NOT ingested",
                     missing=not tops))
    gk = ei["goalkeeper_signal"]
    dims.append(_dim("goalkeeper_reliability",
                     gk or None, pstats_src + " + /fixtures/statistics", "medium" if gk else "none",
                     "GK rating + saves this match" if gk else None,
                     "single-match observation; GK season form feed NOT ingested", missing=not gk))
    if shootout_history:
        # source label kept neutral — LLMs copy these strings into prose, and 'kaggle'
        # is an audit token banned in customer fields (first vi run quoted it verbatim)
        dims.append(_dim("penalty_history", shootout_history, "historical shootout archive (internal dataset)", "medium",
                         "documented shootout record",
                         "kaggle-derived historical shootouts; psychology is LLM interpretation, record is fact"))
    else:
        dims.append(_missing("penalty_history", "kaggle shootout lookup (pass shootout_history in)"))
    reds = ei["cards"]["red_count"]
    dims.append(_dim("red_card_sensitivity",
                     {"red_cards_this_match": reds,
                      "first_red": next((d for d in ei["decisive_events"] if d["event_type"] == "red_card"), None)},
                     "/fixtures/events", "high",
                     "red-card events and the score/man-count at the moment they happened",
                     "pre-match red-card propensity (discipline record) NOT ingested — this is observed only"))
    # game-state resilience: did the trailing side score after going behind (facts)
    resp = []
    goals = [d for d in ei["decisive_events"] if d["event_type"] in ("goal", "penalty_goal")]
    for i, g in enumerate(goals):
        trailing = [t for t in (home, away) if g["score_after"][t] < g["score_after"][away if t == home else home]]
        if trailing:
            t = trailing[0]
            nxt = next((h for h in goals[i + 1:] if h["team"] == t), None)
            resp.append({"behind_from": g["minute"], "team": t,
                         "responded": bool(nxt), "response_minute": nxt["minute"] if nxt else None})
    dims.append(_dim("game_state_resilience", resp or None, "/fixtures/events",
                     "medium" if goals else "none",
                     "how each side responded after falling behind (timeline facts)",
                     "derived from goal timeline only", missing=not goals))
    pens = [d for d in ei["decisive_events"] if d["event_type"] == "penalty_goal"]
    corners = {t: s.get("Corner Kicks") for t, s in stats.items()}
    dims.append(_dim("set_piece_threat",
                     {"penalty_goals": [{"minute": p["minute"], "team": p["team"]} for p in pens],
                      "corners": corners},
                     "/fixtures/events + /fixtures/statistics", "medium",
                     "set-piece output this match (penalties, corners)",
                     "free-kick/corner conversion season data NOT ingested"))
    if round_label:
        knockout = not str(round_label).lower().startswith("group")
        dims.append(_dim("knockout_pressure", {"round": round_label, "knockout": knockout},
                         "/fixtures", "low",
                         "stage context (group vs knockout)",
                         "context only; pressure response is LLM interpretation"))
        dims.append(_dim("tournament_pressure", {"round": round_label}, "/fixtures", "low",
                         "tournament stage context",
                         "host-nation / opener flags live in the ops manifest key_reasons"))
    else:
        dims.append(_missing("knockout_pressure", "fixture round label"))
        dims.append(_missing("tournament_pressure", "fixture round label"))
    # honest gaps — no source ingested, never inferred:
    dims.append(_missing("age_profile", "squad birthdates (API /players or FIFA squad list) — pack squads carry name/number/position ONLY"))
    dims.append(_missing("defensive_line_age", "squad birthdates (same gap as age_profile)"))
    dims.append(_missing("squad_experience", "caps / tournaments-played source"))
    dims.append(_missing("captain_core_stability", "captaincy + appearance-streak source"))
    dims.append(_missing("coach_adjustment_pattern", "multi-match tactical-change dataset"))
    dims.append(_missing("attacking_transition_speed", "possession-sequence / progressive-carry data (no xG-adjacent feed)"))
    return {"note": "facts-only; missing_evidence dims are NAMED gaps, never inferred",
            "dimensions": dims,
            "missing_count": sum(1 for d in dims if d["missing_evidence"])}


if __name__ == "__main__":
    import sys
    fid = sys.argv[1] if len(sys.argv) > 1 else "1489369"
    fav = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps({"event_impact": build_event_impact(fid, favoured=fav),
                      "extended_dimensions": build_extended_dimensions(fid, favoured=fav)},
                     ensure_ascii=False, indent=1))
