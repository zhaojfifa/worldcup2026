from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

VALID_EVENTS = {
    "view_home",
    "view_match",
    "click_detail",
    "click_unlock",
    "click_share",
    "click_community",
    "click_social_channel",
}


class SocialChannelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    channel_name: str
    display_name: str
    status: str
    public_url: Optional[str]
    description: Optional[str]
    locale: str
    is_enabled: bool
    sort_order: int


class ChannelUpsertRequest(BaseModel):
    channel_name: str
    display_name: str
    status: str = "coming_soon"      # coming_soon / active / disabled
    public_url: Optional[str] = None
    description: Optional[str] = None
    locale: str = "vi"
    is_enabled: bool = True
    sort_order: int = 0


class TrackEventRequest(BaseModel):
    event_type: str
    match_id: Optional[int] = None
    channel_name: Optional[str] = None


class TrackEventResponse(BaseModel):
    ok: bool
    event_type: str
    message: str


class HeatMatch(BaseModel):
    match_id: int
    home: str
    away: str
    interactions: int


class CommunityHeat(BaseModel):
    top_matches: List[HeatMatch]
    total_interactions: int
    hot_channels: List[str]
    updated_at: Optional[datetime]
    message: str
