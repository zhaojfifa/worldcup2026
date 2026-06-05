from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MatchEngagement(Base):
    """
    Anonymous, aggregate in-app engagement counters per match.
    No IP, no user identity, no personal data — counts only.
    """
    __tablename__ = "match_engagements"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True, index=True)

    views_count: Mapped[int] = mapped_column(Integer, default=0)
    detail_clicks: Mapped[int] = mapped_column(Integer, default=0)
    unlock_clicks: Mapped[int] = mapped_column(Integer, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)
    share_clicks: Mapped[int] = mapped_column(Integer, default=0)
    community_clicks: Mapped[int] = mapped_column(Integer, default=0)
    social_channel_clicks: Mapped[int] = mapped_column(Integer, default=0)

    last_updated_at: Mapped[datetime] = mapped_column(
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
