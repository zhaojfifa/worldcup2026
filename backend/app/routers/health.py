from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter
from app.services.data_sources.api_football import api_football
from app.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/api/v1/health")
def health():
    """Liveness + readiness probe — safe to expose publicly."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "ai_provider": settings.ai_provider,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        # Compliance declaration — never removed
        "compliance": {
            "real_money_betting_enabled": settings.enable_real_money_betting,
            "token_withdrawal_enabled": settings.enable_token_withdrawal,
            "mtc_description": "Platform loyalty points only. Not withdrawable. Not transferable. Not a financial asset.",
        },
    }


@router.get("/api/v1/health/data-source")
def health_data_source():
    """Test API-FOOTBALL connectivity — backend only, key is never exposed."""
    result = api_football.test_connection()
    return result
