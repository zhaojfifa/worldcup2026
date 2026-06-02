from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Float, Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TokenWallet(Base):
    """
    MTC (Match Token Coin) — Platform loyalty points.
    COMPLIANCE: NOT withdrawable, NOT transferable, NOT a financial asset.
    """
    __tablename__ = "token_wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    total_earned: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[int] = mapped_column(Integer, default=0)
    last_checkin_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="wallet")  # type: ignore[name-defined]
    logs: Mapped[list["TokenLog"]] = relationship("TokenLog", back_populates="wallet")  # type: ignore[name-defined]


class TokenLog(Base):
    """Audit log for every MTC balance change."""
    __tablename__ = "token_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("token_wallets.id"), index=True)

    # positive = credit, negative = debit
    amount: Mapped[int] = mapped_column(Integer)
    balance_after: Mapped[int] = mapped_column(Integer)

    # Event type
    event_type: Mapped[str] = mapped_column(String(30))
    # checkin / share / invite / unlock_report / spend_shop / admin

    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="token_logs")  # type: ignore[name-defined]
    wallet: Mapped["TokenWallet"] = relationship("TokenWallet", back_populates="logs")  # type: ignore[name-defined]
