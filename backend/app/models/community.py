from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CommunitySubscription(Base):
    """
    Live intelligence community subscription (¥199/month).
    This is a paid AI data analysis service — NOT a betting pool.
    """
    __tablename__ = "community_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    plan: Mapped[str] = mapped_column(String(20), default="monthly")   # monthly / trial
    price_cny: Mapped[int] = mapped_column(Integer, default=19900)     # fen: ¥199

    status: Mapped[str] = mapped_column(String(20), default="active")  # active/expired/cancelled

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="subscription")  # type: ignore[name-defined]
