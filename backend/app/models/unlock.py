from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UnlockRecord(Base):
    """Records when a user unlocks a full AI report (cash or MTC points)."""
    __tablename__ = "unlock_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)

    # Payment method
    method: Mapped[str] = mapped_column(String(10))   # "cash" or "token"
    amount_cny: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)   # fen (¥39 = 3900)
    amount_mtc: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="unlock_records")  # type: ignore[name-defined]
    match: Mapped["Match"] = relationship("Match", back_populates="unlock_records")  # type: ignore[name-defined]
