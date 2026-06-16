from __future__ import annotations
"""
R4 — runtime CONTENT source (Owner GO 2026-06-16: daily content cutover without a frontend deploy).

  GET  /api/v1/runtime-content            public read — current content package (or empty-but-valid)
  GET  /api/v1/runtime-content/{date}     public read — package only if its date matches
  POST /api/v1/admin/runtime-content/upload   admin (x-admin-token) — store a gate-passed package

No auto-send. No user/payment data. Additive endpoints; no existing shape changed; reuses the
runtime_manifests table. send_status is always HOLD.
"""
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services import runtime_content_service as svc

router = APIRouter(prefix="/api/v1", tags=["runtime-content"])
settings = get_settings()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = settings.admin_api_token
    if not expected:
        raise HTTPException(status_code=401, detail="Admin endpoints are disabled (ADMIN_API_TOKEN unset)")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing x-admin-token")


@router.get("/runtime-content")
def get_runtime_content(db: Session = Depends(get_db)):
    return svc.assemble_response(db)


@router.get("/runtime-content/{date}")
def get_runtime_content_for_date(date: str, db: Session = Depends(get_db)):
    return svc.assemble_response(db, date=date)


@router.post("/admin/runtime-content/upload")
def upload_runtime_content(body: dict = Body(...), x_admin_token: str | None = Header(default=None),
                           by: str | None = None, db: Session = Depends(get_db)):
    require_admin(x_admin_token)
    if not isinstance(body, dict) or not (body.get("date") or body.get("generated_for_date")):
        raise HTTPException(status_code=422, detail="content package must be an object with a 'date'")
    if not isinstance(body.get("predictions"), dict) or not body.get("predictions"):
        raise HTTPException(status_code=422, detail="content package must include a non-empty 'predictions' object")
    stored = svc.upsert_current(db, body, by or "operator-upload")
    return {"stored": True, "date": stored.get("date"), "source_mode": stored.get("source_mode"),
            "predictions": len(stored.get("predictions", {})), "observations": len(stored.get("observations", {})),
            "send_status": "HOLD"}
