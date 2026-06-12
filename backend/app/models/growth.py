from __future__ import annotations
"""
Growth P1 — Intelligence Ambassador（情报官）models. Owner GO 2026-06-12.

COMPLIANCE (non-negotiable):
  - contribution points are MTC platform points context ONLY: non-cash, non-withdrawable,
    non-transferable, non-tradable; NO money/price/odds columns exist in this module.
  - NO hierarchy: ambassador rows have no parent/child relations.
  - NO identity capture: clicks/intents store surface/lang/device-class/timestamps only —
    no IP, no raw user agent, no names/phones/emails, no per-user identity fields.
  - growth_audit_log is APPEND-ONLY; services must write an audit row for every mutation.
Additive tables only; no existing table or API shape is modified.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GrowthAmbassador(Base):
    """Operator-issued ambassador code (QG-/TT-/FO- prefix). No self-serve signup."""
    __tablename__ = "growth_ambassadors"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    display_alias: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    lang: Mapped[str] = mapped_column(String(8), default="zh")          # zh | vi | my
    default_channel: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(12), default="active")   # active|paused|retired
    created_by: Mapped[str] = mapped_column(String(60), default="operator")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    clicks: Mapped[list["GrowthClick"]] = relationship(back_populates="ambassador")
    intents: Mapped[list["GrowthJoinIntent"]] = relationship(back_populates="ambassador")
    contributions: Mapped[list["GrowthContribution"]] = relationship(back_populates="ambassador")


class GrowthClick(Base):
    """One landing with a valid ref. NO ip / raw UA / identity columns by design."""
    __tablename__ = "growth_clicks"

    id: Mapped[int] = mapped_column(primary_key=True)
    ambassador_id: Mapped[int] = mapped_column(ForeignKey("growth_ambassadors.id"), index=True)
    surface: Mapped[str] = mapped_column(String(60))                    # /join, /predict/<id>, ...
    lang: Mapped[str] = mapped_column(String(8), default="zh")
    channel_tag: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    device_class: Mapped[str] = mapped_column(String(10), default="unknown")  # mobile|desktop|unknown
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    ambassador: Mapped["GrowthAmbassador"] = relationship(back_populates="clicks")


class GrowthJoinIntent(Base):
    """Group-CTA tap. Confirmation is a MANUAL operator act (no in-group bot)."""
    __tablename__ = "growth_join_intents"

    id: Mapped[int] = mapped_column(primary_key=True)
    ambassador_id: Mapped[int] = mapped_column(ForeignKey("growth_ambassadors.id"), index=True)
    surface: Mapped[str] = mapped_column(String(60))
    lang: Mapped[str] = mapped_column(String(8), default="zh")
    confirm_status: Mapped[str] = mapped_column(String(12), default="unconfirmed")  # unconfirmed|confirmed|rejected
    confirmed_by: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    ambassador: Mapped["GrowthAmbassador"] = relationship(back_populates="intents")


class GrowthContribution(Base):
    """贡献值 ledger entry. Points are INT only; every credit needs manual review.
    Approved entries credit MTC via the existing wallet rails (token_log_id recorded)."""
    __tablename__ = "growth_contributions"

    id: Mapped[int] = mapped_column(primary_key=True)
    ambassador_id: Mapped[int] = mapped_column(ForeignKey("growth_ambassadors.id"), index=True)
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(20))                     # confirmed_join|content_share|monthly_bonus|other
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="pending", index=True)  # pending|approved|rejected
    created_by: Mapped[str] = mapped_column(String(60), default="rule")
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    token_log_id: Mapped[Optional[int]] = mapped_column(ForeignKey("token_logs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    ambassador: Mapped["GrowthAmbassador"] = relationship(back_populates="contributions")


class GrowthAuditLog(Base):
    """Append-only audit trail. Services NEVER update or delete rows here."""
    __tablename__ = "growth_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(60))
    action: Mapped[str] = mapped_column(String(40))
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    before_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    after_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
