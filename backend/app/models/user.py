from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """
    Platform user.
    No financial identity — MTC points are platform loyalty points only.
    Not withdrawable, not transferable, not a financial asset.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(200), unique=True, nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    wallet: Mapped[Optional["TokenWallet"]] = relationship("TokenWallet", back_populates="user", uselist=False)  # type: ignore[name-defined]
    token_logs: Mapped[list["TokenLog"]] = relationship("TokenLog", back_populates="user")  # type: ignore[name-defined]
    unlock_records: Mapped[list["UnlockRecord"]] = relationship("UnlockRecord", back_populates="user")  # type: ignore[name-defined]
    challenge_entries: Mapped[list["ChallengeEntry"]] = relationship("ChallengeEntry", back_populates="user")  # type: ignore[name-defined]
    subscription: Mapped[Optional["CommunitySubscription"]] = relationship("CommunitySubscription", back_populates="user", uselist=False)  # type: ignore[name-defined]
