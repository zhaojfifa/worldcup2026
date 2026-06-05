from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MatchResult(Base):
    """
    Real full-time result for a match, ingested from a data source
    (e.g. API-FOOTBALL finished fixtures). Powers 战绩 / performance.
    Idempotent by external_id.
    """
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(80), unique=True, index=True, nullable=True)

    full_time_home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    full_time_away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    outcome: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # home / draw / away

    result_source: Mapped[str] = mapped_column(String(40), default="api-football")
    result_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # pending / final / postponed / cancelled / abandoned
    status: Mapped[str] = mapped_column(String(20), default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
