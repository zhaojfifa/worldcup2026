from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ChallengeResult(Base):
    """
    Settlement of a user's free prediction challenge entry.
    actual_result comes from MatchResult / challenge settlement.
    is_correct affects MTC points + streak only — never cash.
    """
    __tablename__ = "challenge_results"
    __table_args__ = (UniqueConstraint("challenge_id", "user_id", name="uq_challenge_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    match_id: Mapped[Optional[int]] = mapped_column(ForeignKey("matches.id"), nullable=True)

    selected_option: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # "A"/"B"
    actual_result: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)   # "A"/"B"/neutral
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)         # None = neutral/unresolved

    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
