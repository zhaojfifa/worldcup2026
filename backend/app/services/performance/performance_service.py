from __future__ import annotations
"""
Performance service — computes 战绩 strictly from stored PredictionSettlement
rows (which are traceable to real MatchResult). Never fabricates numbers.

COMPLIANCE: every payload carries the mandatory disclaimer; neutral (难分胜负)
settlements are excluded from hit-rate.
"""
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models import PredictionSettlement, LiveCorrection

DISCLAIMER = "历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。"


def _as_aware(dt: datetime) -> datetime:
    """Coerce a possibly-naive datetime (SQLite returns naive) to UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _rate(hits: int, total: int) -> Optional[float]:
    if total <= 0:
        return None
    return round(hits / total * 100, 1)


def _directional(settlements):
    """Only settlements that count toward hit-rate (exclude neutral)."""
    return [s for s in settlements if s.is_hit is not None]


def _risk_breakdown(settlements) -> dict:
    out = {}
    for level in ("low", "medium", "high"):
        subset = [s for s in _directional(settlements) if s.risk_level == level]
        hits = sum(1 for s in subset if s.is_hit)
        out[level] = {"settled": len(subset), "hit_count": hits, "hit_rate": _rate(hits, len(subset))}
    return out


def _high_conf_rate(settlements) -> Optional[float]:
    subset = [s for s in _directional(settlements) if s.confidence_bucket == "high"]
    hits = sum(1 for s in subset if s.is_hit)
    return _rate(hits, len(subset))


def daily(db: Session, day: Optional[str] = None) -> dict:
    target = date.fromisoformat(day) if day else datetime.now(timezone.utc).date()
    all_rows = db.query(PredictionSettlement).all()
    rows = [s for s in all_rows if s.settled_at and _as_aware(s.settled_at).date() == target]
    directional = _directional(rows)
    hits = sum(1 for s in directional if s.is_hit)
    return {
        "date": target.isoformat(),
        "total_settled": len(directional),
        "hit_count": hits,
        "hit_rate": _rate(hits, len(directional)),
        "high_confidence_hit_rate": _high_conf_rate(rows),
        "neutral_count": len(rows) - len(directional),
        "risk_breakdown": _risk_breakdown(rows),
        "disclaimer": DISCLAIMER,
    }


def summary(db: Session) -> dict:
    all_rows = db.query(PredictionSettlement).all()
    directional = _directional(all_rows)
    hits = sum(1 for s in directional if s.is_hit)

    # last 7 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    last7 = _directional([s for s in all_rows if s.settled_at and _as_aware(s.settled_at) >= cutoff])
    last7_hits = sum(1 for s in last7 if s.is_hit)

    # live-correction uplift: corrected vs uncorrected hit-rate
    corrected_match_ids = {c.match_id for c in db.query(LiveCorrection).all()}
    corrected = [s for s in directional if s.match_id in corrected_match_ids]
    uncorrected = [s for s in directional if s.match_id not in corrected_match_ids]
    corrected_rate = _rate(sum(1 for s in corrected if s.is_hit), len(corrected))
    uncorrected_rate = _rate(sum(1 for s in uncorrected if s.is_hit), len(uncorrected))
    uplift = (
        round(corrected_rate - uncorrected_rate, 1)
        if corrected_rate is not None and uncorrected_rate is not None
        else None
    )

    return {
        "total_settled": len(directional),
        "hit_count": hits,
        "hit_rate": _rate(hits, len(directional)),
        "last7d_hit_rate": _rate(last7_hits, len(last7)),
        "high_confidence_hit_rate": _high_conf_rate(all_rows),
        "live_correction_uplift": uplift,
        "neutral_count": len(all_rows) - len(directional),
        "risk_breakdown": _risk_breakdown(all_rows),
        "disclaimer": DISCLAIMER,
    }
