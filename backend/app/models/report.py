from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Float, Integer, ForeignKey, String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Report(Base):
    """Full AI analysis report — paid / token-unlocked content."""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True, index=True)

    # Structured data
    features: Mapped[list] = mapped_column(JSON, default=list)
    # [{"label": "中场控制力", "value": 18}, ...]

    trend_history: Mapped[list] = mapped_column(JSON, default=list)
    # [{"label": "赛前3天", "prob": 42}, ...]

    # Long-form text (premium)
    tactics_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI verdict summary
    verdict_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    match: Mapped["Match"] = relationship("Match", back_populates="report")  # type: ignore[name-defined]
