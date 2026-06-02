"""
API-FOOTBALL (api-sports.io) connector.

SECURITY RULES:
- API key is read from environment only — never hardcoded, never logged, never returned to frontend.
- This module is ONLY called server-side.
- All responses are sanitised before being forwarded to the frontend API.

Day 3: connection test + countries endpoint only.
Day 4: fixtures sync for WC 2026 (league_id=1, season=2026).
"""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class APIFootballClient:
    """Thin async-capable wrapper around API-FOOTBALL v3."""

    BASE_URL: str = ""   # filled from settings

    def __init__(self) -> None:
        self.BASE_URL = settings.api_football_base_url.rstrip("/")
        self._key = settings.api_football_key   # NEVER log or return this value

    def _headers(self) -> dict[str, str]:
        return {
            "x-apisports-key": self._key,
            "Accept": "application/json",
        }

    def _is_configured(self) -> bool:
        return bool(self._key and self._key != "replace_with_your_api_key")

    # ------------------------------------------------------------------ #
    #  Connection test                                                      #
    # ------------------------------------------------------------------ #
    def test_connection(self) -> dict[str, Any]:
        """
        Verify the API key is working by calling /status.
        Returns a sanitised status dict (key is NOT included in output).
        """
        if not self._is_configured():
            return {
                "ok": False,
                "source": "api-football",
                "message": "API_FOOTBALL_KEY not configured — running in mock mode",
            }

        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self.BASE_URL}/status", headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            account = data.get("response", {}).get("account", {})
            return {
                "ok": True,
                "source": "api-football",
                "plan": account.get("plan", "unknown"),
                "requests_used": data.get("response", {}).get("requests", {}).get("current", 0),
                "requests_limit": data.get("response", {}).get("requests", {}).get("limit_day", 0),
            }
        except Exception as exc:
            logger.warning("API-FOOTBALL connection test failed: %s", exc)
            return {"ok": False, "source": "api-football", "message": str(exc)}

    # ------------------------------------------------------------------ #
    #  Countries                                                           #
    # ------------------------------------------------------------------ #
    def get_countries(self) -> list[dict[str, str]]:
        """Return a list of {name, code, flag} — useful as a smoke test."""
        if not self._is_configured():
            return []
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{self.BASE_URL}/countries", headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("response", [])

    # ------------------------------------------------------------------ #
    #  Fixtures — placeholder for Day 4                                    #
    # ------------------------------------------------------------------ #
    def get_fixtures(self, league_id: int = 1, season: int = 2026) -> list[dict]:
        """
        Fetch fixtures for a given league & season.
        Day 3: stubbed — returns empty list.
        Day 4: will iterate pages and upsert into DB.
        """
        logger.info("get_fixtures called — league=%s season=%s (stub in Day 3)", league_id, season)
        return []

    def get_lineups(self, fixture_id: int) -> dict:
        """
        Fetch confirmed lineups 30 min before kickoff.
        Day 3: stubbed.
        Day 4: drives LiveCorrection creation.
        """
        logger.info("get_lineups called — fixture_id=%s (stub in Day 3)", fixture_id)
        return {}


# Module-level singleton — import this instead of instantiating directly
api_football = APIFootballClient()
