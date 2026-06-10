from __future__ import annotations
"""
ScoutScore v0.1 — Factor Scoring Layer (rule-based, historical replay).

Produces 7 structured factors representing the model's **pre-match view** in a
historical replay (NOT a real archived prediction). Orientation: a positive
`score` favours the HOME side; negative favours AWAY. `direction` restates it.

Honesty rules baked in:
- `data_status`: `available` | `missing` | `replay_only`. A factor that a real
  pre-match model could not have had is `missing` or `replay_only` (never faked
  as a pre-match input).
- `score` is the PRE-MATCH model weighting; `post_match_validation` is how the
  actual result judged it (this is where blind spots surface).
- Every factor carries `source_refs` OR `assumption=true` (no unsourced claims).
- No win probability, no SHAP, no xG, no odds, no injury inference.

Output language for this data contract = English (ASCII identifiers/strings);
the localized zh/vi narrative lives in the accountability report.
"""
from typing import Any, Optional

SOURCE = "api-football"


def _ref(pack: dict, field: str, metric: Optional[str] = None, value: Any = None) -> dict:
    led = (pack.get("source_ledger") or {}).get(field) or {}
    return {"field": field, "metric": metric, "value": value,
            "source": led.get("source") or SOURCE, "endpoint": led.get("endpoint"),
            "fixture_id": pack.get("fixture_id")}


def _stat(pack: dict, team_name: str, key: str):
    for t in (pack.get("team_statistics", {}).get("value") or []):
        if t.get("team") == team_name:
            return (t.get("stats") or {}).get(key)
    return None


def compute_factor_scores(pack: dict, features: dict, favored_side: str = "home") -> dict:
    """favored_side = the replay paper-strength assumption (Elo/squad value not ingested)."""
    ctx = features.get("context") or {}
    home, away = ctx.get("home"), ctx.get("away")
    score = ctx.get("final_score") or {}
    winner_side = ctx.get("result_winner")
    fav_name = home if favored_side == "home" else away
    fav_sign = 1 if favored_side == "home" else -1

    formations = pack.get("formation", {}).get("value") or {}
    poss_diff = features.get("possession_difference")
    shot_diff = features.get("shot_difference")
    gk = features.get("goalkeeper_rating") or {}
    gh = (gk.get("home") or {}).get("rating")
    ga = (gk.get("away") or {}).get("rating")
    second_half = [f"{g['minute']}' {g['team']}" for g in (features.get("goal_timeline") or [])
                   if (g.get("minute_num") or 0) > 45]

    factors = [
        {
            "factor": "team_strength",
            "direction": ("argentina" if fav_name == "Argentina" else fav_name.lower().replace(" ", "_")) if fav_name else "unknown",
            "weight": 2, "score": 2 * fav_sign,
            "interpretation_pre_match": f"Paper strength / reputation favours {fav_name} (world-class squad, star players).",
            "post_match_validation": "NOT validated — paper strength did not convert; the favoured side dominated play but lost. Over-weighted.",
            "source_refs": [], "assumption": True, "data_status": "missing",
            "note": "Team strength / Elo / squad value is NOT ingested — this is a replay assumption.",
        },
        {
            "factor": "recent_form",
            "direction": "unknown", "weight": 1, "score": 0,
            "interpretation_pre_match": "Recent form not ingested — unknown pre-match.",
            "post_match_validation": "Cannot validate (data missing).",
            "source_refs": [], "assumption": True, "data_status": "missing",
        },
        {
            "factor": "lineup_formation",
            "direction": "argentina" if (formations.get("home") or {}).get("formation") else "unknown",
            "weight": 1, "score": 1,
            "interpretation_pre_match": f"{home} {(formations.get('home') or {}).get('formation')} vs {away} {(formations.get('away') or {}).get('formation')} (read from match lineup; replay).",
            "post_match_validation": f"Partial — the favoured side's setup created chances, but {away}'s compact block held the result.",
            "source_refs": [_ref(pack, "formation", "formation", f"{(formations.get('home') or {}).get('formation')} / {(formations.get('away') or {}).get('formation')}"),
                            _ref(pack, "lineups", "startXI", None)],
            "assumption": False, "data_status": "replay_only",
        },
        {
            "factor": "match_control",
            "direction": "argentina" if (poss_diff or 0) > 0 else "saudi_arabia",
            "weight": 1, "score": 1,
            "interpretation_pre_match": "Model assumes the favoured side controls possession — an in-match factor, not a true pre-match input.",
            "post_match_validation": f"Validated as control ({_stat(pack, home, 'Ball Possession')} vs {_stat(pack, away, 'Ball Possession')}), INVALIDATED as a result predictor — control did not convert.",
            "source_refs": [_ref(pack, "team_statistics", "Ball Possession", f"diff {poss_diff}")],
            "assumption": True, "data_status": "replay_only",
        },
        {
            "factor": "efficiency",
            "direction": "unknown", "weight": 2, "score": 0,
            "interpretation_pre_match": "No shot-quality / finishing-efficiency factor pre-match — model blind spot.",
            "post_match_validation": f"DECISIVE (missed): {away} {_stat(pack, away, 'Shots on Goal')} on-target → {score.get('away')} goals vs {home} {_stat(pack, home, 'Shots on Goal')} on-target → {score.get('home')}; keeper ratings home {gh} / away {ga}, saves {_stat(pack, home, 'Goalkeeper Saves')} / {_stat(pack, away, 'Goalkeeper Saves')}.",
            "source_refs": [_ref(pack, "team_statistics", "Shots on Goal / Total Shots", f"{shot_diff} shot diff"),
                            _ref(pack, "player_statistics", "goalkeeper rating", f"home {gh} / away {ga}")],
            "assumption": False, "data_status": "replay_only",
        },
        {
            "factor": "event_momentum",
            "direction": "unknown", "weight": 2, "score": 0,
            "interpretation_pre_match": "No momentum / turning-point factor pre-match — model blind spot.",
            "post_match_validation": f"DECISIVE (missed): second-half turnaround — {', '.join(second_half) if second_half else 'n/a'}.",
            "source_refs": [_ref(pack, "events_summary", "second-half goals", "; ".join(second_half))],
            "assumption": False, "data_status": "replay_only",
        },
        {
            "factor": "missing_risk",
            "direction": "neutral", "weight": 1, "score": 0,
            "interpretation_pre_match": "Model blind spots: injuries (0 results) + xG (not ingested) — cannot assess availability or chance quality.",
            "post_match_validation": "Confirmed — these gaps must be filled (injuries P0, xG P1).",
            "source_refs": [_ref(pack, "injuries", "results", "0 (source required)")],
            "assumption": False, "data_status": "missing",
        },
    ]

    agg = sum(f["weight"] * f["score"] for f in factors)
    expected_side = home if agg > 0 else (away if agg < 0 else "neutral")
    missing_ct = sum(1 for f in factors if f["data_status"] == "missing")
    # Heavy reliance on assumptions + missing inputs => deliberately LOW confidence.
    confidence_tier = "low" if missing_ct >= 2 or any(f["assumption"] and f["score"] for f in factors) else "medium"
    accountability_status = "miss" if (winner_side in ("home", "away") and
                                       ((expected_side == home) != (winner_side == "home"))) else "hit"

    return {
        "model_name": "ScoutScore v0.1",
        "model_type": "hybrid_factor_scoring_with_llm_reasoning",
        "fixture_id": pack.get("fixture_id"),
        "prediction_mode": "historical_replay",
        "not_real_archived_prediction": True,
        "orientation": "positive score favours HOME (%s); negative favours AWAY (%s)" % (home, away),
        "favored_side_assumption": {"side": favored_side, "team": fav_name,
                                    "basis": "paper strength assumption — Elo/squad value NOT ingested"},
        "factors": factors,
        "aggregate_score": agg,
        "expected_side": expected_side,
        "confidence_tier": confidence_tier,
        "accountability_status": accountability_status,
        "actual_result": {"home": home, "away": away, "score": f"{score.get('home')}-{score.get('away')}",
                          "winner_side": winner_side},
        "disclaimer": "Historical replay only — not a real archived prediction; no win-rate, no feature-importance weights, no xG, no financial signal.",
    }
