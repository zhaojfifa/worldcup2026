from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.token import (
    WalletOut, CheckInRequest, CheckInResponse,
    UnlockReportRequest, UnlockReportResponse,
    SimulateCorrectionRequest, SimulateCorrectionResponse,
    JoinChallengeRequest, JoinChallengeResponse,
    SubscribeRequest, SubscribeResponse,
)
from app.services.token import wallet_service

router = APIRouter(prefix="/api/v1", tags=["tokens"])


@router.get("/tokens/wallet/{user_id}", response_model=WalletOut)
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    """Get MTC loyalty points wallet for a user."""
    try:
        return wallet_service.get_wallet(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tokens/checkin", response_model=CheckInResponse)
def checkin(req: CheckInRequest, db: Session = Depends(get_db)):
    """Daily check-in — awards MTC loyalty points. Once per calendar day."""
    try:
        return wallet_service.checkin(db, req.user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tokens/unlock-report", response_model=UnlockReportResponse)
def unlock_report(req: UnlockReportRequest, db: Session = Depends(get_db)):
    """
    Unlock full AI report via cash (¥39) or MTC loyalty points (390).
    MTC points are platform loyalty points — not withdrawable, not transferable.
    """
    try:
        return wallet_service.unlock_report(db, req.user_id, req.match_id, req.method)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/corrections/{match_id}/simulate", response_model=SimulateCorrectionResponse)
def simulate_correction(match_id: int, req: SimulateCorrectionRequest, db: Session = Depends(get_db)):
    """
    Simulate a 30-minute pre-match AI lineup correction.
    In production this is triggered automatically when official lineups are confirmed.
    """
    try:
        return wallet_service.simulate_correction(db, match_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/challenges/{challenge_id}/join", response_model=JoinChallengeResponse)
def join_challenge(
    challenge_id: int,
    req: JoinChallengeRequest,
    db: Session = Depends(get_db),
):
    """
    Join a free prediction challenge.
    MTC loyalty points distributed to correct entries after match settlement.
    """
    try:
        return wallet_service.join_challenge(db, challenge_id, req.user_id, req.chosen_option)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/community/subscribe", response_model=SubscribeResponse)
def subscribe(req: SubscribeRequest, db: Session = Depends(get_db)):
    """
    Subscribe to the live intelligence community (¥199/month).
    This is an AI data analysis subscription service — not a betting service.
    """
    try:
        return wallet_service.subscribe(db, req.user_id, req.plan)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
