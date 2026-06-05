from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class SocialChannel(Base):
    """
    Configurable community channel entry (Zalo / Telegram / Facebook / TikTok).
    Admin-configurable; no bots, no auto-push. Real links may be set by admin.
    """
    __tablename__ = "social_channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_name: Mapped[str] = mapped_column(String(40), unique=True, index=True)  # zalo/telegram/...
    display_name: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="coming_soon")  # coming_soon/active/disabled
    public_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="vi")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
