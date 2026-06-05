from __future__ import annotations
"""
Settlement service — maps an AI prediction to a settleable target and scores it
against a real outcome.

The label derivation mirrors the frontend ops layer (src/ops/derive.ts) so the
settled label matches exactly what users saw.

Settlement口径 (avoids 战绩 ambiguity):
  主胜偏强 / 主胜略占优 → single_outcome  target {home}
  客胜偏强 / 客胜略占优 → single_outcome  target {away}
  主队不败趋势          → double_chance   target {home, draw}
  客队不败趋势          → double_chance   target {away, draw}
  难分胜负              → neutral         (NOT counted in hit-rate)

COMPLIANCE: this is analytical settlement only — not a betting market.
"""
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Prediction, PredictionSettlement


def ai_pick_label(prob_home: float, prob_draw: float, prob_away: float) -> str:
    """Mirror of frontend aiPickLabel()."""
    lead = prob_home - prob_away
    spread = max(prob_home, prob_draw, prob_away) - min(prob_home, prob_draw, prob_away)
    if prob_home >= 48 and lead >= 12:
        return "主胜偏强"
    if prob_away >= 48 and -lead >= 12:
        return "客胜偏强"
    if prob_home + prob_draw >= 70 and prob_home >= prob_away:
        return "主队不败趋势"
    if prob_away + prob_draw >= 70 and prob_away > prob_home:
        return "客队不败趋势"
    if spread < 8:
        return "难分胜负"
    return "主胜略占优" if lead >= 0 else "客胜略占优"


def confidence_bucket(confidence: float) -> str:
    if confidence >= 72:
        return "high"
    if confidence >= 60:
        return "mid"
    return "low"


# label → (settlement_type, set of winning outcomes)
def _label_to_targets(label: str):
    if label in ("主胜偏强", "主胜略占优"):
        return "single_outcome", {"home"}
    if label in ("客胜偏强", "客胜略占优"):
        return "single_outcome", {"away"}
    if label == "主队不败趋势":
        return "double_chance", {"home", "draw"}
    if label == "客队不败趋势":
        return "double_chance", {"away", "draw"}
    return "neutral", set()


def settle_prediction(db: Session, prediction: Prediction, actual_outcome: str) -> PredictionSettlement:
    """
    Create or update the PredictionSettlement for a prediction given the real
    outcome. Idempotent by prediction_id.
    """
    label = ai_pick_label(prediction.prob_home, prediction.prob_draw, prediction.prob_away)
    settlement_type, targets = _label_to_targets(label)
    is_hit: Optional[bool]
    if settlement_type == "neutral":
        is_hit = None  # excluded from hit-rate
    else:
        is_hit = actual_outcome in targets

    existing = (
        db.query(PredictionSettlement)
        .filter(PredictionSettlement.prediction_id == prediction.id)
        .first()
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.predicted_label = label
        existing.actual_outcome = actual_outcome
        existing.settlement_type = settlement_type
        existing.is_hit = is_hit
        existing.confidence_bucket = confidence_bucket(prediction.confidence)
        existing.risk_level = prediction.risk_level
        existing.settled_at = now
        return existing

    settlement = PredictionSettlement(
        match_id=prediction.match_id,
        prediction_id=prediction.id,
        predicted_label=label,
        actual_outcome=actual_outcome,
        settlement_type=settlement_type,
        is_hit=is_hit,
        confidence_bucket=confidence_bucket(prediction.confidence),
        risk_level=prediction.risk_level,
        settled_at=now,
    )
    db.add(settlement)
    return settlement
