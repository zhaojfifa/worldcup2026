from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Challenge(Base):
    """Free prediction challenge — users pick an option, MTC distributed after settlement."""
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    question: Mapped[str] = mapped_column(String(200))    # "本场是否会出现红牌？"
    option_a: Mapped[str] = mapped_column(String(100))   # "会"
    option_b: Mapped[str] = mapped_column(String(100))   # "不会"
    correct_option: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # "A" or "B"
    prize_pool: Mapped[int] = mapped_column(Integer, default=0)   # MTC to distribute
    status: Mapped[str] = mapped_column(String(20), default="open")  # open/closed/settled

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    match: Mapped["Match"] = relationship("Match", back_populates="challenges")  # type: ignore[name-defined]
    entries: Mapped[list["ChallengeEntry"]] = relationship("ChallengeEntry", back_populates="challenge")  # type: ignore[name-defined]


class ChallengeEntry(Base):
    """A user's participation in one challenge."""
    __tablename__ = "challenge_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    chosen_option: Mapped[str] = mapped_column(String(1))  # "A" or "B"
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    reward_amount: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="entries")  # type: ignore[name-defined]
    user: Mapped["User"] = relationship("User", back_populates="challenge_entries")  # type: ignore[name-defined]
