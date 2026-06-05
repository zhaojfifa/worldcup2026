from __future__ import annotations
"""
Content asset service — builds R2 storage keys (Giành Cup convention),
uploads bytes via the R2 client, and records ContentAsset metadata.

Key naming (giand-cup convention; never nha-tien-tri):
  share-cards/top-signal/YYYY-MM-DD/{ident}.png
  share-cards/upset-risk/YYYY-MM-DD/{ident}.png
  share-cards/live-correction/YYYY-MM-DD/{ident}.png
  share-cards/post-match-recap/YYYY-MM-DD/{ident}.png
  social/{channel}/YYYY-MM-DD/{slug}.png
  system/placeholders/{name}.png
"""
import base64
import binascii
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import ContentAsset
from app.schemas.asset import AssetUploadRequest, VALID_ASSET_TYPES
from app.services.storage.r2_client import r2_client

_SHARE_PREFIX = {
    "top_signal_card": "share-cards/top-signal",
    "upset_card": "share-cards/upset-risk",
    "live_correction_card": "share-cards/live-correction",
    "post_match_recap": "share-cards/post-match-recap",
}


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def build_key(req: AssetUploadRequest) -> str:
    """Build the canonical R2 key for an upload request."""
    if req.key:
        return req.key
    day = req.day or _today()
    if req.asset_type == "social_material":
        channel = (req.channel or "zalo").strip("/")
        slug = req.slug or req.ident or "post"
        return f"social/{channel}/{day}/{slug}.png"
    prefix = _SHARE_PREFIX[req.asset_type]
    ident = req.ident or (str(req.related_match_id) if req.related_match_id else "asset")
    return f"{prefix}/{day}/{ident}.png"


def upload(db: Session, req: AssetUploadRequest) -> dict:
    """
    Returns a dict matching AssetUploadResponse.
    - Invalid asset_type → ok False (message), no row.
    - R2 not configured → ok False, configured False, no row (graceful).
    - Success → upload bytes, create ContentAsset, return asset.
    """
    if req.asset_type not in VALID_ASSET_TYPES:
        return {"ok": False, "configured": r2_client.is_configured(),
                "message": f"invalid asset_type: {req.asset_type}", "asset": None}

    try:
        file_bytes = base64.b64decode(req.content_base64, validate=True)
    except (binascii.Error, ValueError):
        return {"ok": False, "configured": r2_client.is_configured(),
                "message": "content_base64 is not valid base64", "asset": None}

    key = build_key(req)
    result = r2_client.upload_asset(file_bytes, key, req.content_type)
    if not result.get("ok"):
        # graceful degrade (e.g. R2 not configured) — no DB row created
        return {"ok": False, "configured": result.get("configured", False),
                "message": result.get("message", "upload failed"), "asset": None}

    asset = ContentAsset(
        asset_type=req.asset_type,
        storage_key=key,
        public_url=result.get("public_url"),   # may be None
        content_type=req.content_type,
        size_bytes=result.get("size_bytes", len(file_bytes)),
        related_match_id=req.related_match_id,
        created_by="admin",
        status="active",
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return {"ok": True, "configured": True, "message": "asset uploaded", "asset": asset}


def get_active(db: Session, asset_id: int) -> Optional[ContentAsset]:
    return (
        db.query(ContentAsset)
        .filter(ContentAsset.id == asset_id, ContentAsset.status == "active")
        .first()
    )


def soft_delete(db: Session, asset_id: int) -> Optional[ContentAsset]:
    asset = db.query(ContentAsset).filter(ContentAsset.id == asset_id).first()
    if not asset:
        return None
    # best-effort remove from R2; status flips regardless
    r2_client.delete_asset(asset.storage_key)
    asset.status = "deleted"
    db.commit()
    db.refresh(asset)
    return asset
