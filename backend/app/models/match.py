from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(80), unique=True, nullable=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    kickoff_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    venue: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)   # "Group Stage", "QF", etc.
    group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Display tag for frontend
    tag: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # focus/upset/live/high-conf

    # Match status
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled/live/finished

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    home_team: Mapped["Team"] = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])  # type: ignore[name-defined]
    away_team: Mapped["Team"] = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])  # type: ignore[name-defined]

    prediction: Mapped[Optional["Prediction"]] = relationship("Prediction", back_populates="match", uselist=False)  # type: ignore[name-defined]
    report: Mapped[Optional["Report"]] = relationship("Report", back_populates="match", uselist=False)  # type: ignore[name-defined]
    corrections: Mapped[list["LiveCorrection"]] = relationship("LiveCorrection", back_populates="match")  # type: ignore[name-defined]
    challenges: Mapped[list["Challenge"]] = relationship("Challenge", back_populates="match")  # type: ignore[name-defined]
    unlock_records: Mapped[list["UnlockRecord"]] = relationship("UnlockRecord", back_populates="match")  # type: ignore[name-defined]
