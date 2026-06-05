from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.admin import require_admin
from app.schemas.streak import (
    StreakOut, RankingsOut, SettleChallengeRequest, SettleChallengeResponse,
)
from app.services.streak import streak_service

router = APIRouter(prefix="/api/v1", tags=["rankings"])


@router.get("/users/{user_id}/streak", response_model=StreakOut)
def user_streak(user_id: int, db: Session = Depends(get_db)):
    """Empty-safe — returns zeros if the user has no streak yet."""
    return streak_service.get_user_streak(db, user_id)


@router.get("/rankings", response_model=RankingsOut)
def rankings(db: Session = Depends(get_db)):
    """Streak / participation / MTC-points board. Empty-safe; never an earnings board."""
    return streak_service.get_rankings(db)


@router.post("/admin/challenges/settle", response_model=SettleChallengeResponse)
def settle_challenge(
    req: SettleChallengeRequest,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Admin-only. Record a ChallengeResult and update the user's streak + MTC.
    actual_result: "A" / "B" / "neutral". Reuses the user's existing
    ChallengeEntry pick unless selected_option is provided.
    """
    return streak_service.settle_challenge_result(
        db,
        challenge_id=req.challenge_id,
        user_id=req.user_id,
        actual_result=req.actual_result,
        match_id=req.match_id,
        selected_option=req.selected_option,
    )
