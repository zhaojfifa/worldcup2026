from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PredictionSettlement(Base):
    """
    Settlement of one prediction against a real MatchResult.
    Fully traceable: every 战绩 number derives from rows here + MatchResult.
    """
    __tablename__ = "prediction_settlements"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), unique=True, index=True)

    predicted_label: Mapped[str] = mapped_column(String(40))     # ai_pick_label
    actual_outcome: Mapped[str] = mapped_column(String(10))      # home / draw / away

    # single_outcome / double_chance / neutral
    settlement_type: Mapped[str] = mapped_column(String(20))

    # None for neutral (excluded from hit-rate); True/False otherwise
    is_hit: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    confidence_bucket: Mapped[str] = mapped_column(String(10))   # high / mid / low
    risk_level: Mapped[str] = mapped_column(String(10))          # low / medium / high

    settled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
