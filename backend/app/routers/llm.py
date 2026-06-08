from __future__ import annotations
"""
Admin-only, draft-only LLM copy generation.

POST /api/v1/admin/llm/generate-copy
  body: { match_id:int, language:"vi|mm|zh|en", copy_type:"preview|upset|live|recap" }
  → draft payload (generated_text, provenance, warnings, forbidden_hits, status:"draft_only").

NEVER publishes, NEVER writes to the DB, NEVER sends to Telegram/Zalo. Requires
x-admin-token. Additive endpoint — does not touch existing public API shapes.
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.services.llm import copy_service

router = APIRouter(prefix="/api/v1/admin/llm", tags=["admin-llm"])
settings = get_settings()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = settings.admin_api_token
    if not expected:
        raise HTTPException(status_code=401, detail="Admin endpoints are disabled (ADMIN_API_TOKEN unset)")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing x-admin-token")


class GenerateCopyIn(BaseModel):
    match_id: int
    language: str
    copy_type: str


@router.post("/generate-copy")
def generate_copy(
    body: GenerateCopyIn,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Generate a single draft copy (LLM if configured, else human-template fallback)."""
    result = copy_service.generate_copy(db, body.match_id, body.language, body.copy_type)
    if result.get("status") == "rejected":
        raise HTTPException(status_code=400, detail=result.get("error", "invalid request"))
    return result
