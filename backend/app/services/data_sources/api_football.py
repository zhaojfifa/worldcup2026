from __future__ import annotations
"""
API-FOOTBALL (api-sports.io) connector.

SECURITY RULES:
- API key is read from environment only — never hardcoded, never logged, never returned to frontend.
- This module is ONLY called server-side.
- All responses are sanitised before being forwarded to the frontend API.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class APIFootballClient:
    """Thin wrapper around API-FOOTBALL v3."""

    def __init__(self) -> None:
        self.base_url = settings.api_football_base_url.rstrip("/")
        self._key = settings.api_football_key   # NEVER log or return this value

    def _headers(self) -> dict:
        return {"x-apisports-key": self._key, "Accept": "application/json"}

    def is_configured(self) -> bool:
        return bool(self._key and self._key not in ("", "replace_with_your_api_key"))

    # ------------------------------------------------------------------ #
    #  Status                                                              #
    # ------------------------------------------------------------------ #
    def status(self) -> dict:
        """
        Structured connector status. Key is never included in output.
        """
        now = datetime.now(timezone.utc).isoformat()
        if not self.is_configured():
            return {
                "api_football_configured": False,
                "connector_status": "not_configured",
                "last_check_at": now,
                "plan": None,
                "requests_used": None,
                "requests_limit": None,
                "message": "API_FOOTBALL_KEY not configured — running in mock mode",
            }
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self.base_url}/status", headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            account = data.get("response", {}).get("account", {})
            requests = data.get("response", {}).get("requests", {})
            return {
                "api_football_configured": True,
                "connector_status": "ok",
                "last_check_at": now,
                "plan": account.get("plan", "unknown"),
                "requests_used": requests.get("current", 0),
                "requests_limit": requests.get("limit_day", 0),
                "message": "API-FOOTBALL reachable",
            }
        except Exception as exc:
            logger.warning("API-FOOTBALL status check failed: %s", exc)
            return {
                "api_football_configured": True,
                "connector_status": "error",
                "last_check_at": now,
                "plan": None,
                "requests_used": None,
                "requests_limit": None,
                "message": f"connection error: {exc}",
            }

    def test_connection(self) -> dict:
        """Backwards-compatible alias used by /health/data-source."""
        s = self.status()
        return {
            "ok": s["connector_status"] == "ok",
            "source": "api-football",
            "plan": s.get("plan"),
            "requests_used": s.get("requests_used"),
            "requests_limit": s.get("requests_limit"),
            "message": s.get("message"),
        }

    # ------------------------------------------------------------------ #
    #  Fixtures                                                            #
    # ------------------------------------------------------------------ #
    def get_fixtures(self, league_id: Optional[int] = None, season: Optional[int] = None) -> list[dict]:
        """
        Fetch fixtures for a league & season.
        Returns the raw `response` array (list of fixture dicts) or [] if not configured.
        """
        if not self.is_configured():
            logger.info("get_fixtures skipped — API-FOOTBALL not configured")
            return []
        league = league_id if league_id is not None else settings.wc_league_id
        yr = season if season is not None else settings.wc_season
        params = {"league": league, "season": yr}
        with httpx.Client(timeout=20) as client:
            resp = client.get(f"{self.base_url}/fixtures", headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json().get("response", [])

    def get_lineups(self, fixture_id: int) -> dict:
        """
        Fetch confirmed lineups (used T-35min before kickoff to drive LiveCorrection).
        Day 4: available but not yet scheduled automatically.
        """
        if not self.is_configured():
            return {}
        with httpx.Client(timeout=15) as client:
            resp = client.get(
                f"{self.base_url}/fixtures/lineups",
                headers=self._headers(),
                params={"fixture": fixture_id},
            )
        resp.raise_for_status()
        return resp.json().get("response", {})


# Module-level singleton — import this instead of instantiating directly
api_football = APIFootballClient()
