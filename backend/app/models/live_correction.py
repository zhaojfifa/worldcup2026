from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Float, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class LiveCorrection(Base):
    """Record of a 30-minute pre-match AI re-calculation."""
    __tablename__ = "live_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)

    trigger: Mapped[str] = mapped_column(String(200))  # e.g. "阿根廷主力中卫未进入首发"

    # Probabilities before / after
    prob_home_before: Mapped[float] = mapped_column(Float)
    prob_draw_before: Mapped[float] = mapped_column(Float)
    prob_away_before: Mapped[float] = mapped_column(Float)

    prob_home_after: Mapped[float] = mapped_column(Float)
    prob_draw_after: Mapped[float] = mapped_column(Float)
    prob_away_after: Mapped[float] = mapped_column(Float)

    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_simulated: Mapped[bool] = mapped_column(default=False)  # True in demo/mock mode

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    match: Mapped["Match"] = relationship("Match", back_populates="corrections")  # type: ignore[name-defined]
