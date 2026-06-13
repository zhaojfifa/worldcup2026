from __future__ import annotations
"""
P1.3c — runtime manifest key/value store (Owner GO 2026-06-13).

A tiny JSON store so the daily fixture registry can be UPDATED on the live site without a
frontend rebuild: an operator uploads the manifest via the admin endpoint, the public
GET /api/v1/daily-fixtures serves it. Additive table only; no existing table/shape changes.

COMPLIANCE: holds ONLY the public daily-fixtures manifest (team names, kickoff, status, score,
lifecycle). NO user data, NO payment data, NO growth-attribution data. Append/overwrite by key.
value_json is stored as TEXT (json string) for cross-DB portability (sqlite dev + postgres prod).
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeManifest(Base):
    """Keyed JSON blobs: 'daily_fixtures_current' (and future 'recap_queue_current')."""
    __tablename__ = "runtime_manifests"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text, nullable=False)   # json.dumps(...) payload
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
