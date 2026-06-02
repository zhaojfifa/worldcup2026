from __future__ import annotations
from fastapi import APIRouter

from app.config import get_settings
from app.services.data_sources.api_football import api_football

router = APIRouter(prefix="/api/v1", tags=["data-source"])
settings = get_settings()


@router.get("/data-source/status")
def data_source_status():
    """
    Public, safe data-source status. Never exposes the API key.
    `mock_mode` reflects whether predictions currently come from mock/seed
    data (AI_PROVIDER=mock) rather than a live inference provider.
    """
    s = api_football.status()
    return {
        "api_football_configured": s["api_football_configured"],
        "connector_status": s["connector_status"],
        "last_check_at": s["last_check_at"],
        "mock_mode": settings.ai_provider == "mock",
        "plan": s.get("plan"),
        "requests_used": s.get("requests_used"),
        "requests_limit": s.get("requests_limit"),
        "message": s.get("message"),
    }
