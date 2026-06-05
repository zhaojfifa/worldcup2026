from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ContentAsset(Base):
    """
    Metadata for a content asset stored in R2 (share cards, recap images,
    social materials). The bytes live in R2; this row tracks the object.
    No user uploads — admin-created only.
    """
    __tablename__ = "content_assets"

    id: Mapped[int] = mapped_column(primary_key=True)

    # top_signal_card / upset_card / live_correction_card / post_match_recap / social_material
    asset_type: Mapped[str] = mapped_column(String(40), index=True)

    storage_key: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    public_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # null until domain bound
    content_type: Mapped[str] = mapped_column(String(80), default="image/png")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    related_match_id: Mapped[Optional[int]] = mapped_column(ForeignKey("matches.id"), nullable=True)
    created_by: Mapped[str] = mapped_column(String(40), default="admin")

    # active / archived / deleted
    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
