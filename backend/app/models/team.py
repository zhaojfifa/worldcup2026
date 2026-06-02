from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    api_id: Mapped[Optional[int]] = mapped_column(unique=True, nullable=True)  # API-FOOTBALL team id
    name: Mapped[str] = mapped_column(String(100), index=True)
    name_zh: Mapped[str] = mapped_column(String(100))        # Chinese display name
    country: Mapped[str] = mapped_column(String(100))
    flag_emoji: Mapped[str] = mapped_column(String(10))       # e.g. "🇧🇷"
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # World Cup group
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    home_matches: Mapped[list["Match"]] = relationship(  # type: ignore[name-defined]
        "Match", back_populates="home_team", foreign_keys="Match.home_team_id"
    )
    away_matches: Mapped[list["Match"]] = relationship(  # type: ignore[name-defined]
        "Match", back_populates="away_team", foreign_keys="Match.away_team_id"
    )
