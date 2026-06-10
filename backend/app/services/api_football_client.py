from __future__ import annotations
"""
API-FOOTBALL (api-sports.io v3) — server-side Level-2 scout client.

Dedicated to MVP-2 Scout Pack ingestion (lineups / events / statistics /
fixture players / squad / coach / teams / injuries). Kept SEPARATE from the
Day-4 connector (`data_sources/api_football.py`) so the existing fixtures-sync
path is never disturbed.

SECURITY / OPS RULES (enforced here):
- Token is read from server-side env only (settings, with a best-effort
  gitignored `.env` fallback for the standalone ingestion script). It is
  **never printed, logged, returned, or written to the Scout Pack**.
- Requests carry the key in the ``x-apisports-key`` header only.
- Every call has a timeout, a 429 backoff+retry, and a hard request budget.
- Logs contain only: endpoint, http status, results count, fixture/team id.
- Server-side only — the frontend never calls the vendor.
"""
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger("scout.api_football")

_TOKEN_VARS = ["API_FOOTBALL_KEY", "API_KEY", "API_TOKEN", "API_SPORTS_KEY"]
_DEFAULT_BASE = "https://v3.football.api-sports.io"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_key_from_dotenv() -> tuple[str, str]:
    """Best-effort token read from a gitignored local .env (script path only).

    Returns (key, base_url). Only recognized var names are read; nothing is
    printed. Used when the process did not export the key (e.g. the standalone
    ingestion script run from the repo root). Mirrors the verifier's loader.
    """
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    key, base = "", ""
    for fn in (os.path.join(repo, "backend/.env"), os.path.join(repo, ".env"),
               os.path.join(repo, "backend/.env.local")):
        if not os.path.isfile(fn):
            continue
        try:
            with open(fn, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if not key and k in _TOKEN_VARS:
                        key = v
                    elif not base and k == "API_FOOTBALL_BASE_URL":
                        base = v
        except Exception:  # noqa: BLE001 — never fail ingestion on a bad .env line
            pass
        if key:
            break
    return key, base


class BudgetExceeded(RuntimeError):
    """Raised when the per-run request budget is hit (runaway / cost guard)."""


@dataclass
class EndpointResult:
    """Normalized, secret-free result of one vendor call (safe to embed/log)."""

    endpoint: str
    params: dict = field(default_factory=dict)   # safe params (never the key)
    http_status: Optional[int] = None
    results: int = 0
    errors: Any = None
    response: Any = field(default_factory=list)
    fixture_id: Optional[int] = None
    team_id: Optional[int] = None
    checked_at: str = field(default_factory=_now_iso)

    @property
    def ok(self) -> bool:
        return self.http_status == 200 and not self.errors and (self.results or 0) > 0

    def ledger_row(self) -> dict:
        """Compact provenance row (no payload) for source_request_log."""
        return {
            "endpoint": self.endpoint,
            "params": self.params,
            "http_status": self.http_status,
            "results": self.results,
            "fixture_id": self.fixture_id,
            "team_id": self.team_id,
            "checked_at": self.checked_at,
            "errors": self.errors,
        }


class APIFootballScoutClient:
    """Read-only Level-2 client with timeout / 429 backoff / budget guard."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        *,
        timeout: float = 20.0,
        max_requests: int = 200,
        backoff_seconds: float = 65.0,
        max_retries: int = 2,
    ) -> None:
        settings = get_settings()
        key = api_key or settings.api_football_key or ""
        base = base_url or settings.api_football_base_url or _DEFAULT_BASE
        if not key:
            dot_key, dot_base = _load_key_from_dotenv()
            key = dot_key
            base = base_url or dot_base or base
        self._key = key                      # NEVER log / return this value
        self.base_url = (base or _DEFAULT_BASE).rstrip("/")
        self.timeout = timeout
        self.max_requests = max_requests
        self.backoff_seconds = backoff_seconds
        self.max_retries = max_retries
        self.request_count = 0
        self.request_log: list[dict] = []

    def is_configured(self) -> bool:
        return bool(self._key and self._key not in ("", "replace_with_your_api_key"))

    def _headers(self) -> dict:
        # RapidAPI hosting uses different headers; default is api-sports direct.
        if "rapidapi" in self.base_url:
            host = self.base_url.split("//")[-1].split("/")[0]
            return {"x-rapidapi-key": self._key, "x-rapidapi-host": host, "Accept": "application/json"}
        return {"x-apisports-key": self._key, "Accept": "application/json"}

    def _get(
        self,
        endpoint: str,
        params: dict,
        *,
        fixture_id: Optional[int] = None,
        team_id: Optional[int] = None,
    ) -> EndpointResult:
        if not self.is_configured():
            return EndpointResult(endpoint=endpoint, params=params, http_status=None,
                                  errors="not_configured", fixture_id=fixture_id, team_id=team_id)
        if self.request_count >= self.max_requests:
            raise BudgetExceeded(f"request budget {self.max_requests} reached at {endpoint}")

        attempt = 0
        while True:
            attempt += 1
            self.request_count += 1
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.get(f"{self.base_url}{endpoint}", headers=self._headers(), params=params)
                status = resp.status_code
                if status == 429 and attempt <= self.max_retries:
                    wait = self._retry_after(resp)
                    logger.warning("429 on %s — backoff %ss (attempt %s)", endpoint, wait, attempt)
                    time.sleep(wait)
                    continue
                body = resp.json() if resp.content else {}
                raw_errors = body.get("errors") if isinstance(body, dict) else None
                errors = raw_errors if raw_errors else None  # [] / {} -> None
                results = body.get("results", 0) if isinstance(body, dict) else 0
                response = body.get("response", []) if isinstance(body, dict) else []
                out = EndpointResult(
                    endpoint=endpoint, params=params, http_status=status,
                    results=results or 0, errors=errors, response=response,
                    fixture_id=fixture_id, team_id=team_id,
                )
            except Exception as exc:  # noqa: BLE001
                out = EndpointResult(endpoint=endpoint, params=params, http_status=None,
                                     errors=f"{type(exc).__name__}: {exc}",
                                     fixture_id=fixture_id, team_id=team_id)
            logger.info("GET %s params=%s -> http=%s results=%s fixture=%s team=%s",
                        endpoint, params, out.http_status, out.results, fixture_id, team_id)
            self.request_log.append(out.ledger_row())
            return out

    @staticmethod
    def _retry_after(resp: httpx.Response) -> float:
        try:
            return min(float(resp.headers.get("Retry-After", "")), 65.0)
        except (TypeError, ValueError):
            return 65.0

    # ------------------------------------------------------------------ #
    #  Endpoints (read-only)                                              #
    # ------------------------------------------------------------------ #
    def status(self) -> EndpointResult:
        # /status has a dict response; normalize results from its body.
        res = self._get("/status", {})
        if isinstance(res.response, dict):
            res.results = 1 if res.response else 0
        return res

    def get_fixture(self, fixture_id: int) -> EndpointResult:
        return self._get("/fixtures", {"id": fixture_id}, fixture_id=fixture_id)

    def get_fixtures(self, league_id: int, season: int) -> EndpointResult:
        return self._get("/fixtures", {"league": league_id, "season": season})

    def get_lineups(self, fixture_id: int) -> EndpointResult:
        return self._get("/fixtures/lineups", {"fixture": fixture_id}, fixture_id=fixture_id)

    def get_events(self, fixture_id: int) -> EndpointResult:
        return self._get("/fixtures/events", {"fixture": fixture_id}, fixture_id=fixture_id)

    def get_statistics(self, fixture_id: int) -> EndpointResult:
        return self._get("/fixtures/statistics", {"fixture": fixture_id}, fixture_id=fixture_id)

    def get_fixture_players(self, fixture_id: int) -> EndpointResult:
        return self._get("/fixtures/players", {"fixture": fixture_id}, fixture_id=fixture_id)

    def get_squad(self, team_id: int) -> EndpointResult:
        return self._get("/players/squads", {"team": team_id}, team_id=team_id)

    def get_coach(self, team_id: int) -> EndpointResult:
        return self._get("/coachs", {"team": team_id}, team_id=team_id)

    def get_team(self, team_id: int) -> EndpointResult:
        return self._get("/teams", {"id": team_id}, team_id=team_id)

    def get_injuries(
        self,
        fixture_id: Optional[int] = None,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
    ) -> EndpointResult:
        params: dict = {}
        if fixture_id is not None:
            params["fixture"] = fixture_id
        if league_id is not None:
            params["league"] = league_id
        if season is not None:
            params["season"] = season
        return self._get("/injuries", params, fixture_id=fixture_id)
