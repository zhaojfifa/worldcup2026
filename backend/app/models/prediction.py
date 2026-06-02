from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Float, Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Prediction(Base):
    """AI model output — win/draw/loss probabilities and recommendation."""
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True, index=True)

    # Win probabilities (0-100, sum ≈ 100)
    prob_home: Mapped[float] = mapped_column(Float)
    prob_draw: Mapped[float] = mapped_column(Float)
    prob_away: Mapped[float] = mapped_column(Float)

    # AI output
    recommended_score: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "2:1 / 1:1"
    risk_level: Mapped[str] = mapped_column(String(10), default="medium")  # low/medium/high
    confidence: Mapped[float] = mapped_column(Float, default=50.0)         # 0-100

    # Free-tier text
    free_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Provider tracking
    model_version: Mapped[str] = mapped_column(String(50), default="mock-v1")
    ai_provider: Mapped[str] = mapped_column(String(20), default="mock")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    match: Mapped["Match"] = relationship("Match", back_populates="prediction")  # type: ignore[name-defined]
