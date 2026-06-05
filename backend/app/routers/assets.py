from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.admin import require_admin
from app.schemas.asset import AssetUploadRequest, AssetUploadResponse, AssetOut
from app.services.assets import asset_service
from app.services.storage.r2_client import r2_client

router = APIRouter(prefix="/api/v1", tags=["assets"])


@router.get("/assets/status")
def assets_status():
    """Public, safe R2 status — never exposes credentials."""
    return r2_client.status()


@router.post("/admin/assets/upload", response_model=AssetUploadResponse)
def upload_asset(
    req: AssetUploadRequest,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Admin-only. Upload an asset (base64) to R2 and record metadata.
    Gracefully degrades (ok=False) when R2 is not configured — no row created.
    public_url is null until R2_PUBLIC_BASE_URL is bound.
    """
    return asset_service.upload(db, req)


@router.get("/assets/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Public read — only active assets are returned."""
    asset = asset_service.get_active(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/admin/assets/{asset_id}", response_model=AssetOut)
def delete_asset(
    asset_id: int,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only soft delete (status → deleted); best-effort R2 removal."""
    asset = asset_service.soft_delete(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
