from __future__ import annotations
"""
Feature snapshot (Phase 3 productization) — pure derivations from a Scout Pack.

Computes **observable, post-match** features only (what happened), each traceable
to a real field in the pack. This is NOT a prediction model:

FORBIDDEN here (never produced): win probability · betting/odds signal · SHAP /
feature-importance · xG · injury impact · player-absence impact.

Every value is derived from the cached pack (events / statistics / player stats /
fixture). No network, no DB, no model.
"""
import re
from typing import Any, Optional

from app.services.scout_pack import contract as C


def _pct(v: Any) -> Optional[float]:
    """Parse '69%' / '69' / 69 -> 69.0; None-safe."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)", str(v))
    return float(m.group(1)) if m else None


def _num(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)", str(v))
    return float(m.group(1)) if m else None


def _minute_num(m: Any) -> Optional[int]:
    if m is None:
        return None
    g = re.match(r"(\d+)", str(m))
    return int(g.group(1)) if g else None


def _diff(home: dict, away: dict, key: str, pct: bool = False) -> Optional[float]:
    fn = _pct if pct else _num
    hv, av = fn(home.get(key)), fn(away.get(key))
    if hv is None or av is None:
        return None
    return round(hv - av, 2)


def compute_feature_snapshot(pack: dict) -> dict:
    fid = pack.get("fixture_id")
    fx = pack.get("fixture", {}).get("value") or {}
    home_name = (fx.get("home_team") or {}).get("name")
    away_name = (fx.get("away_team") or {}).get("name")
    score = fx.get("final_score") or {}

    sec = {k: bool(pack.get(k, {}).get("available")) for k in
           ("lineups", "formation", "coach", "events_summary", "team_statistics",
            "player_statistics", "squad")}

    ev = pack.get("events_summary", {}).get("value") or {}
    by_type = ev.get("by_type") or {}

    # --- goal timeline + running score (own goals flip the credited side) ---
    goals = []
    h = a = 0
    for e in (ev.get("timeline") or []):
        if e.get("type") != "Goal":
            continue
        side = "home" if e.get("team") == home_name else ("away" if e.get("team") == away_name else None)
        if e.get("detail") and "Own Goal" in str(e.get("detail")):
            side = "away" if side == "home" else ("home" if side == "away" else side)
        if side == "home":
            h += 1
        elif side == "away":
            a += 1
        leader = "home" if h > a else ("away" if a > h else "level")
        goals.append({"minute": e.get("minute"), "minute_num": _minute_num(e.get("minute")),
                      "team": e.get("team"), "player": e.get("player"),
                      "detail": e.get("detail"), "score_after": f"{h}-{a}", "leader_after": leader})

    non_level = [g["leader_after"] for g in goals if g["leader_after"] != "level"]
    lead_change = ("home" in non_level and "away" in non_level)
    ht_goals = [g for g in goals if (g["minute_num"] or 0) <= 45]
    ht_leader = ht_goals[-1]["leader_after"] if ht_goals else "level"
    final_leader = goals[-1]["leader_after"] if goals else "level"
    last_minute = goals[-1]["minute_num"] if goals else None
    second_half_turnaround = bool(goals and ht_leader != final_leader and (last_minute or 0) > 45)

    total_events = ev.get("total") or 0

    # --- team statistics differences (home - away) ---
    ts = {t.get("team"): (t.get("stats") or {}) for t in (pack.get("team_statistics", {}).get("value") or [])}
    hs, as_ = ts.get(home_name, {}), ts.get(away_name, {})

    # --- player ratings + goalkeepers ---
    ps = {t.get("team"): t for t in (pack.get("player_statistics", {}).get("value") or [])}
    all_ratings = []
    for t in ps.values():
        for p in (t.get("top_by_rating") or []):
            r = _num(p.get("rating"))
            if r is not None:
                all_ratings.append(r)
    gk = {}
    for side, name in (("home", home_name), ("away", away_name)):
        g = (ps.get(name) or {}).get("goalkeeper") or {}
        gk[side] = {"name": g.get("name"), "rating": _num(g.get("rating"))}

    snapshot = {
        "fixture_id": fid,
        "source": C.SOURCE_API_FOOTBALL,
        "model_type": "observed_feature_snapshot_v0",
        "context": {"home": home_name, "away": away_name,
                    "final_score": {"home": score.get("home"), "away": score.get("away")},
                    "result_winner": fx.get("result_winner")},
        # availability
        "lineup_available": sec["lineups"],
        "formation_available": sec["formation"],
        "coach_available": sec["coach"],
        "events_available": sec["events_summary"],
        "statistics_available": sec["team_statistics"],
        "player_statistics_available": sec["player_statistics"],
        "squad_available": sec["squad"],
        # match shape (observed)
        "goal_timeline": goals,
        "lead_change": lead_change,
        "second_half_turnaround": second_half_turnaround,
        "event_density_per_90": round((total_events or 0) / 90.0, 3),
        "event_total": total_events,
        "card_count": by_type.get("Card", 0),
        "substitution_count": by_type.get("subst", 0),
        # statistical dominance (home - away)
        "shot_difference": _diff(hs, as_, "Total Shots"),
        "shots_on_goal_difference": _diff(hs, as_, "Shots on Goal"),
        "possession_difference": _diff(hs, as_, "Ball Possession", pct=True),
        "pass_accuracy_difference": _diff(hs, as_, "Passes %", pct=True),
        # player ratings (observed)
        "top_player_rating": max(all_ratings) if all_ratings else None,
        "goalkeeper_rating": gk,
        "goalkeeper_saves": {"home": _num(hs.get("Goalkeeper Saves")), "away": _num(as_.get("Goalkeeper Saves"))},
        # coverage + gaps
        "data_coverage_score": pack.get("feature_snapshot", {}).get("coverage_score"),
        "missing_injuries": not bool(pack.get("injuries", {}).get("available")),
        "missing_xg": True,  # xG is not ingested / excluded by policy this round
        "derived_from": ["/fixtures", "/fixtures/events", "/fixtures/statistics", "/fixtures/players"],
        "disclaimer": dict(C.loc(
            "仅为已发生数据的观测特征,不是预测、不是命中率、不作为博彩或资金信号",
            "Chỉ là đặc trưng quan sát từ dữ liệu đã xảy ra, không phải dự đoán, không phải tỷ lệ trúng, không phải tín hiệu tài chính",
            "Observed features from data that already happened — not a prediction, not a hit-rate, not a financial signal",
        )),
    }
    return snapshot
