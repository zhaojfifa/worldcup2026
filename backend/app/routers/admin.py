from __future__ import annotations
"""
Admin-only endpoints. Every route requires a valid x-admin-token header
matching ADMIN_API_TOKEN from the environment. If ADMIN_API_TOKEN is unset,
admin routes are locked (always 401) — never open to the public.
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.jobs import fixtures_sync
from app.services.results import result_sync

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
settings = get_settings()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Dependency: reject unless x-admin-token matches ADMIN_API_TOKEN."""
    expected = settings.admin_api_token
    if not expected:
        # No token configured → admin surface is closed, not open.
        raise HTTPException(status_code=401, detail="Admin endpoints are disabled (ADMIN_API_TOKEN unset)")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing x-admin-token")


@router.post("/sync/fixtures")
def sync_fixtures(
    league_id: int | None = None,
    season: int | None = None,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Manually trigger an API-FOOTBALL fixtures sync.
    Returns inserted / updated / skipped / errors counts.
    """
    return fixtures_sync.sync_fixtures(db, league_id=league_id, season=season)


@router.post("/sync/results")
def sync_results(
    league_id: int | None = None,
    season: int | None = None,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Pull finished fixtures from API-FOOTBALL, upsert MatchResult, and settle
    existing predictions. Returns inserted / updated / settled / skipped / errors.
    Gracefully degrades to mock_mode when API-FOOTBALL is not configured.
    """
    return result_sync.sync_results(db, league_id=league_id, season=season)
