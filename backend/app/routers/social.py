from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.admin import require_admin
from app.schemas.social import (
    SocialChannelOut, ChannelUpsertRequest,
    TrackEventRequest, TrackEventResponse, CommunityHeat, VALID_EVENTS,
)
from app.services.community import community_service

router = APIRouter(prefix="/api/v1", tags=["community"])


@router.get("/social/channels", response_model=List[SocialChannelOut])
def social_channels(db: Session = Depends(get_db)):
    """Public — enabled community channels in sort order."""
    return community_service.list_channels(db)


@router.post("/admin/social/channels/upsert", response_model=SocialChannelOut)
def upsert_channel(
    req: ChannelUpsertRequest,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only — create/update a channel (real links configurable here)."""
    return community_service.upsert_channel(db, req)


@router.post("/events/track", response_model=TrackEventResponse)
def track_event(req: TrackEventRequest, db: Session = Depends(get_db)):
    """
    Anonymous in-app event counter. Unknown event_type → 400.
    Never stores IP / user identity. Best-effort; failures don't propagate
    to the frontend main flow.
    """
    if req.event_type not in VALID_EVENTS:
        raise HTTPException(status_code=400, detail=f"unknown event_type: {req.event_type}")
    try:
        community_service.track_event(db, req.event_type, req.match_id)
    except Exception:  # noqa: BLE001 — tracking must never break the caller
        return TrackEventResponse(ok=False, event_type=req.event_type, message="tracking skipped")
    return TrackEventResponse(ok=True, event_type=req.event_type, message="recorded")


@router.get("/community/heat", response_model=CommunityHeat)
def community_heat(db: Session = Depends(get_db)):
    """Empty-safe community heat from anonymous engagement counts."""
    return community_service.community_heat(db)
