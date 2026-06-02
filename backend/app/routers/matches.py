from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.match import MatchListItem, MatchDetail, ReportOut
from app.services import match_service

router = APIRouter(prefix="/api/v1", tags=["matches"])


@router.get("/matches", response_model=list[MatchListItem])
def list_matches(db: Session = Depends(get_db)):
    """
    Return all upcoming matches with AI win probabilities.
    Free-tier — no authentication required.
    Data is AI analysis only; not a betting recommendation.
    """
    return match_service.get_matches(db)


@router.get("/matches/{match_id}", response_model=MatchDetail)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Return full match detail including free note and latest live correction.
    Free-tier — no authentication required.
    """
    match = match_service.get_match_detail(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("/reports/{match_id}", response_model=ReportOut)
def get_report(match_id: int, db: Session = Depends(get_db)):
    """
    Return full AI report — premium content.
    In production this endpoint checks unlock status.
    Day 3: open for development/testing.
    """
    report = match_service.get_report(db, match_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or match has no prediction")
    return report
