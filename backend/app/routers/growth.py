from __future__ import annotations
"""
Growth P1 router — Intelligence Ambassador（情报官）endpoints. Owner GO 2026-06-12.

Public (rate-limited): click + join-intent recording. Invalid refs are counted, never
attached. NO identity capture (no IP stored, no raw UA; a coarse in-memory rate limiter
hashes the client address transiently and never persists it).
Admin (x-admin-token, same lock pattern as routers/admin.py): code CRUD, dashboard,
intent confirm, contribution create/review, export. NO auto-send, NO settlement.
"""
import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services.growth import growth_service as G

router = APIRouter(prefix="/api/v1/growth", tags=["growth"])
settings = get_settings()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = settings.admin_api_token
    if not expected:
        raise HTTPException(status_code=401, detail="Admin endpoints are disabled (ADMIN_API_TOKEN unset)")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing x-admin-token")


# ── coarse in-memory rate limit (per process; transient; nothing persisted) ──
_BUCKET: dict[str, list[float]] = {}
RATE_N, RATE_WINDOW = 30, 60.0  # 30 req/min per client key per endpoint


def _rate_ok(request: Request, endpoint: str) -> bool:
    key = "%s|%s" % (endpoint, request.client.host if request.client else "?")
    now = time.time()
    hits = [t for t in _BUCKET.get(key, []) if now - t < RATE_WINDOW]
    if len(hits) >= RATE_N:
        _BUCKET[key] = hits
        return False
    hits.append(now)
    _BUCKET[key] = hits
    return True


class TrackIn(BaseModel):
    ref: str = Field(max_length=20)
    surface: str = Field(max_length=60)
    lang: str = Field(default="zh", max_length=8)
    channel: Optional[str] = Field(default=None, max_length=40)
    device_class: str = Field(default="unknown", max_length=10)


@router.post("/click")
def track_click(body: TrackIn, request: Request, db: Session = Depends(get_db)):
    if not _rate_ok(request, "click"):
        raise HTTPException(status_code=429, detail="rate limited")
    attached = G.record_click(db, body.ref, body.surface, body.lang, body.channel, body.device_class)
    return {"ok": True, "attached": attached}


@router.post("/join-intent")
def join_intent(body: TrackIn, request: Request, db: Session = Depends(get_db)):
    if not _rate_ok(request, "join"):
        raise HTTPException(status_code=429, detail="rate limited")
    attached = G.record_join_intent(db, body.ref, body.surface, body.lang)
    return {"ok": True, "attached": attached}


# ── admin ────────────────────────────────────────────────────────────────────
class AmbassadorIn(BaseModel):
    code: str = Field(max_length=20)
    alias: str = Field(default="", max_length=80)
    lang: str = Field(default="zh", max_length=8)
    channel: Optional[str] = Field(default=None, max_length=40)
    actor: str = Field(default="operator", max_length=60)


@router.post("/admin/ambassadors")
def create_ambassador(body: AmbassadorIn, _: None = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        a = G.create_ambassador(db, body.code, body.alias, body.lang, body.channel, body.actor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "code": a.code, "status": a.status}


class StatusIn(BaseModel):
    status: str
    actor: str = "operator"


@router.patch("/admin/ambassadors/{code}")
def patch_ambassador(code: str, body: StatusIn, _: None = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        a = G.set_ambassador_status(db, code, body.status, body.actor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "code": a.code, "status": a.status}


@router.get("/admin/dashboard")
def admin_dashboard(_: None = Depends(require_admin), db: Session = Depends(get_db)):
    return G.dashboard(db)


class IntentReviewIn(BaseModel):
    decision: str
    actor: str = "operator"


@router.post("/admin/intents/{intent_id}/confirm")
def confirm_intent(intent_id: int, body: IntentReviewIn, _: None = Depends(require_admin),
                   db: Session = Depends(get_db)):
    try:
        it = G.confirm_intent(db, intent_id, body.decision, body.actor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "intent_id": it.id, "confirm_status": it.confirm_status}


class ContributionIn(BaseModel):
    code: str
    points: int
    reason: str
    note: str = ""
    actor: str = "operator"


@router.post("/admin/contributions")
def create_contribution(body: ContributionIn, _: None = Depends(require_admin),
                        db: Session = Depends(get_db)):
    try:
        c = G.create_contribution(db, body.code, body.points, body.reason, body.note, body.actor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "contribution_id": c.id, "status": c.status}


class ReviewIn(BaseModel):
    decision: str
    actor: str = "operator"
    note: str = ""


@router.post("/admin/contributions/{contribution_id}/review")
def review_contribution(contribution_id: int, body: ReviewIn, _: None = Depends(require_admin),
                        db: Session = Depends(get_db)):
    try:
        c = G.review_contribution(db, contribution_id, body.decision, body.actor, body.note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "contribution_id": c.id, "status": c.status, "token_log_id": c.token_log_id}


@router.get("/admin/export")
def export_report(_: None = Depends(require_admin), db: Session = Depends(get_db)):
    return G.export_report(db)
