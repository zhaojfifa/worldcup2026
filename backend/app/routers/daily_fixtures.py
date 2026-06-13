from __future__ import annotations
"""
P1.3c — daily fixtures runtime source (Owner GO 2026-06-13: 能更新才是硬道理).

  GET  /api/v1/daily-fixtures                 public read — current daily manifest (+ recap_queue,
                                               active_hero, freshness). Empty-but-valid if none stored.
  POST /api/v1/admin/daily-fixtures/upload    admin (x-admin-token) — store an uploaded manifest
                                               (frontend OR docs shape). No score invented here.
  POST /api/v1/admin/daily-fixtures/refresh    admin — alias of upload (body-provided manifest);
                                               server-side file read is not assumed reliable.

No auto-send. No user/payment/attribution data. Additive endpoints; no existing shape changed.
"""
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services import daily_fixtures_service as svc

router = APIRouter(prefix="/api/v1", tags=["daily-fixtures"])
settings = get_settings()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = settings.admin_api_token
    if not expected:
        raise HTTPException(status_code=401, detail="Admin endpoints are disabled (ADMIN_API_TOKEN unset)")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing x-admin-token")


@router.get("/daily-fixtures")
def get_daily_fixtures(db: Session = Depends(get_db)):
    """Public, read-only. Customer/runtime frontend fetches this FIRST (P1.3c)."""
    return svc.assemble_response(db)


def _store(body: dict, by: str | None, db: Session):
    if not isinstance(body, dict) or "fixtures" not in body:
        raise HTTPException(status_code=422, detail="manifest body must be an object with a 'fixtures' array")
    stored = svc.upsert_current(db, body, by)
    return {"stored": True, "fixture_count": len(stored.get("fixtures", [])),
            "generated_at": stored.get("generated_at"), "source_mode": stored.get("source_mode")}


@router.post("/admin/daily-fixtures/upload")
def upload_daily_fixtures(body: dict = Body(...), x_admin_token: str | None = Header(default=None),
                          by: str | None = None, db: Session = Depends(get_db)):
    require_admin(x_admin_token)
    return _store(body, by or "operator-upload", db)


@router.post("/admin/daily-fixtures/refresh")
def refresh_daily_fixtures(body: dict = Body(...), x_admin_token: str | None = Header(default=None),
                           by: str | None = None, db: Session = Depends(get_db)):
    require_admin(x_admin_token)
    return _store(body, by or "operator-refresh", db)
