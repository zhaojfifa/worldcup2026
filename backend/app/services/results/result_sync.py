from __future__ import annotations
"""
Results sync — pulls finished fixtures from API-FOOTBALL, upserts MatchResult
(idempotent by external_id), and settles any existing Prediction.

Graceful degradation: if API-FOOTBALL is not configured, returns mock_mode
without making external calls or raising.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Match, Prediction, MatchResult
from app.services.data_sources.api_football import api_football
from app.services.results import settlement_service

logger = logging.getLogger(__name__)

_FINISHED = {"FT", "AET", "PEN"}
_OTHER_TERMINAL = {"PST": "postponed", "CANC": "cancelled", "ABD": "abandoned", "AWD": "final", "WO": "final"}


def _outcome(home: Optional[int], away: Optional[int]) -> Optional[str]:
    if home is None or away is None:
        return None
    if home > away:
        return "home"
    if home < away:
        return "away"
    return "draw"


def sync_results(db: Session, league_id: Optional[int] = None, season: Optional[int] = None) -> dict:
    """Returns {inserted, updated, settled, skipped, errors[], total, mock_mode}."""
    if not api_football.is_configured():
        return {
            "inserted": 0, "updated": 0, "settled": 0, "skipped": 0, "errors": [],
            "total": 0, "mock_mode": True,
            "message": "API_FOOTBALL_KEY not configured — results sync skipped (mock mode)",
        }

    try:
        fixtures = api_football.get_fixtures(league_id, season, status="FT-AET-PEN")
    except Exception as exc:  # noqa: BLE001
        logger.warning("get_fixtures (results) failed: %s", exc)
        return {
            "inserted": 0, "updated": 0, "settled": 0, "skipped": 0,
            "errors": [f"get_fixtures failed: {exc}"], "total": 0, "mock_mode": False,
            "message": "results fetch failed",
        }

    inserted = updated = settled = skipped = 0
    errors: list[str] = []
    now = datetime.now(timezone.utc)

    for fx in fixtures:
        try:
            fixture = fx.get("fixture", {})
            fixture_id = fixture.get("id")
            if not fixture_id:
                skipped += 1
                continue
            external_id = f"AF-{fixture_id}"

            # Only settle matches we actually track.
            match = db.query(Match).filter(Match.external_id == external_id).first()
            if not match:
                skipped += 1
                continue

            short = (fixture.get("status") or {}).get("short", "")
            goals = fx.get("goals", {})
            home_score = goals.get("home")
            away_score = goals.get("away")

            if short in _FINISHED:
                status = "final"
            elif short in _OTHER_TERMINAL:
                status = _OTHER_TERMINAL[short]
            else:
                status = "pending"

            outcome = _outcome(home_score, away_score) if status == "final" else None

            result = db.query(MatchResult).filter(MatchResult.external_id == external_id).first()
            if result:
                result.match_id = match.id
                result.full_time_home_score = home_score
                result.full_time_away_score = away_score
                result.outcome = outcome
                result.status = status
                result.result_synced_at = now
                updated += 1
            else:
                result = MatchResult(
                    match_id=match.id,
                    external_id=external_id,
                    full_time_home_score=home_score,
                    full_time_away_score=away_score,
                    outcome=outcome,
                    result_source="api-football",
                    result_synced_at=now,
                    status=status,
                )
                db.add(result)
                inserted += 1

            # Settle prediction if we have a final outcome.
            if status == "final" and outcome:
                pred = db.query(Prediction).filter(Prediction.match_id == match.id).first()
                if pred:
                    settlement_service.settle_prediction(db, pred, outcome)
                    settled += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))

    db.commit()
    return {
        "inserted": inserted, "updated": updated, "settled": settled,
        "skipped": skipped, "errors": errors, "total": len(fixtures),
        "mock_mode": False, "message": "results sync complete",
    }
