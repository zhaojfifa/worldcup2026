from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

VALID_ASSET_TYPES = {
    "top_signal_card",
    "upset_card",
    "live_correction_card",
    "post_match_recap",
    "social_material",
}


class AssetUploadRequest(BaseModel):
    asset_type: str
    content_base64: str                       # raw bytes, base64-encoded
    content_type: str = "image/png"
    related_match_id: Optional[int] = None
    # Key building hints (optional; a default key is built when omitted)
    ident: Optional[str] = None               # match external id or id
    day: Optional[str] = None                 # YYYY-MM-DD; defaults to today (UTC)
    channel: Optional[str] = None             # for social_material: zalo/telegram/...
    slug: Optional[str] = None                # for social_material
    key: Optional[str] = None                 # explicit override


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_type: str
    storage_key: str
    public_url: Optional[str]                 # null until R2_PUBLIC_BASE_URL bound
    content_type: str
    size_bytes: int
    related_match_id: Optional[int]
    status: str
    created_at: datetime


class AssetUploadResponse(BaseModel):
    ok: bool
    configured: bool
    message: str
    asset: Optional[AssetOut] = None
