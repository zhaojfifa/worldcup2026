from __future__ import annotations
"""
Baseline rules predictor.

This is a deterministic RULES model — NOT machine learning. It exists so the
pipeline (fixtures → prediction → API → frontend) is fully wired end-to-end.
It can later be swapped for CatBoost / LightGBM / SHAP without changing the
public `predict()` signature or the Prediction DB shape.

COMPLIANCE: output is AI data analysis only. No betting advice, no guaranteed
outcomes, no monetary return.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PredictorInput:
    """All fields are placeholders today; real feature sources plug in later."""
    home_strength: float = 50.0      # 0..100 team strength placeholder
    away_strength: float = 50.0
    home_form: float = 0.0           # recent form, -10..+10 placeholder
    away_form: float = 0.0
    risk_factors: float = 0.0        # 0..1 extra volatility placeholder
    home_lineup_ok: bool = True      # lineup status placeholder
    away_lineup_ok: bool = True


def _normalize_to_100(values: list[float]) -> list[int]:
    """
    Convert raw weights to integer percentages that ALWAYS sum to exactly 100
    (largest-remainder method). Prevents 45+27+37 type bugs.
    """
    vals = [max(v, 0.0) for v in values]
    total = sum(vals)
    if total <= 0:
        n = len(vals)
        out = [100 // n] * n
        out[0] += 100 - sum(out)
        return out
    scaled = [v / total * 100 for v in vals]
    floors = [int(x) for x in scaled]
    remainder = 100 - sum(floors)
    order = sorted(range(len(vals)), key=lambda i: scaled[i] - floors[i], reverse=True)
    for i in range(remainder):
        floors[order[i % len(order)]] += 1
    return floors


def _recommended_score(home: int, draw: int, away: int) -> str:
    top = max(home, draw, away)
    if top == home:
        margin = home - max(draw, away)
        return "2:0 / 2:1" if margin >= 18 else "2:1 / 1:1"
    if top == away:
        margin = away - max(draw, home)
        return "0:2 / 1:2" if margin >= 18 else "1:2 / 1:1"
    return "1:1 / 1:0"


def predict(inp: PredictorInput) -> dict:
    """
    Returns a dict matching the Prediction model fields:
      prob_home, prob_draw, prob_away (ints summing to 100),
      confidence, risk_level, risk_note, recommended_score.
    """
    HOME_ADVANTAGE = 4.0
    LINEUP_PENALTY = 6.0

    home_score = inp.home_strength + inp.home_form + HOME_ADVANTAGE \
        - (0.0 if inp.home_lineup_ok else LINEUP_PENALTY)
    away_score = inp.away_strength + inp.away_form \
        - (0.0 if inp.away_lineup_ok else LINEUP_PENALTY)

    diff = home_score - away_score

    # Raw tendencies (kept positive via clamps in normalize)
    home_raw = 50.0 + diff * 1.1
    away_raw = 50.0 - diff * 1.1
    # Draws more likely when teams are close; volatility nudges draw down
    draw_raw = 28.0 - abs(diff) * 0.4 - inp.risk_factors * 6.0

    home_raw = max(home_raw, 3.0)
    away_raw = max(away_raw, 3.0)
    draw_raw = max(draw_raw, 8.0)

    home, draw, away = _normalize_to_100([home_raw, draw_raw, away_raw])

    # Confidence: how decisive is the top pick
    probs = [home, draw, away]
    top = max(probs)
    second = sorted(probs, reverse=True)[1]
    margin = top - second
    confidence = round(min(max(48 + margin * 1.3 + (top - 33) * 0.4, 45), 88))

    # Risk level from decisiveness + volatility
    if margin >= 18 and inp.risk_factors < 0.5:
        risk_level = "low"
    elif margin >= 8:
        risk_level = "medium"
    else:
        risk_level = "high"

    if risk_level == "low":
        risk_note = "模型判断方向较为明确，主要因子一致，临场变量影响有限。"
    elif risk_level == "medium":
        risk_note = "双方存在差距但并非一边倒，临场阵容与状态变化仍可能影响结果。"
    else:
        risk_note = "双方实力接近，结果高度依赖临场阵容与战术对位，不确定性较高。"

    return {
        "prob_home": home,
        "prob_draw": draw,
        "prob_away": away,
        "confidence": float(confidence),
        "risk_level": risk_level,
        "risk_note": risk_note,
        "recommended_score": _recommended_score(home, draw, away),
        "model_version": "baseline-rules-v1",
        "ai_provider": "mock",
    }


def _stable_strength(seed: str) -> float:
    """Deterministic placeholder strength in [40, 72] derived from a stable seed."""
    h = 0
    for ch in seed:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return 40.0 + (h % 33)


def build_input_for_match(match) -> PredictorInput:
    """
    Build predictor input from a Match ORM object.
    Strengths are deterministic placeholders (stable across refreshes) until
    real feature sources (form, xG, injuries) are connected.
    """
    home_seed = match.home_team.name if match.home_team else f"home-{match.id}"
    away_seed = match.away_team.name if match.away_team else f"away-{match.id}"
    return PredictorInput(
        home_strength=_stable_strength(home_seed),
        away_strength=_stable_strength(away_seed),
        home_form=0.0,
        away_form=0.0,
        risk_factors=0.0,
        home_lineup_ok=True,
        away_lineup_ok=True,
    )
