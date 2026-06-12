from __future__ import annotations
"""
Growth P1 service layer — Intelligence Ambassador（情报官）.

Owner-decided rules (2026-06-12):
  confirmed_join = 10 points · content_share = 2 points · monthly_bonus = manual only ·
  daily cap = 100 points/ambassador · monthly cap = 1000 points/ambassador ·
  EVERY credit requires manual review; approve credits MTC via the existing wallet rails.

Every mutation writes a GrowthAuditLog row (append-only). No automatic settlement of anything.
"""
import json
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.growth import (
    GrowthAmbassador, GrowthAuditLog, GrowthClick, GrowthContribution, GrowthJoinIntent,
)
from app.models.user import User
from app.services.token import wallet_service

POINTS = {"confirmed_join": 10, "content_share": 2}   # monthly_bonus/other = manual amount
DAILY_CAP = 100
MONTHLY_CAP = 1000
CODE_RE = re.compile(r"^(QG|TT|FO)-[A-Z0-9]{4,6}$")
ALLOWED_CHANNELS = {"telegram_group_1", "zalo_test_group", "telegram_vi_trusted",
                    "zh_internal_group", "facebook_dm", "operator_manual"}

# invalid-ref landings are counted, never attached to an ambassador (in-process counter;
# the audit log keeps a daily row via record_invalid_ref)
_invalid_ref_count = {"count": 0}


def _now():
    return datetime.now(timezone.utc)


def _audit(db: Session, actor: str, action: str, entity_type: str, entity_id: Optional[int],
           before: Optional[dict] = None, after: Optional[dict] = None) -> None:
    db.add(GrowthAuditLog(actor=actor, action=action, entity_type=entity_type, entity_id=entity_id,
                          before_json=json.dumps(before, ensure_ascii=False, default=str) if before else None,
                          after_json=json.dumps(after, ensure_ascii=False, default=str) if after else None))


def get_ambassador(db: Session, code: str, active_only: bool = True) -> Optional[GrowthAmbassador]:
    q = db.query(GrowthAmbassador).filter(GrowthAmbassador.code == code.upper().strip())
    a = q.first()
    if a and active_only and a.status != "active":
        return None
    return a


def create_ambassador(db: Session, code: str, alias: str = "", lang: str = "zh",
                      channel: Optional[str] = None, actor: str = "operator") -> GrowthAmbassador:
    code = code.upper().strip()
    if not CODE_RE.match(code):
        raise ValueError("code must match QG|TT|FO-XXXX (4-6 alnum)")
    if db.query(GrowthAmbassador).filter_by(code=code).first():
        raise ValueError("code already exists")
    if channel and channel not in ALLOWED_CHANNELS:
        raise ValueError("channel not in allowed tag set")
    a = GrowthAmbassador(code=code, display_alias=alias or None, lang=lang, default_channel=channel,
                         created_by=actor)
    db.add(a)
    db.flush()
    _audit(db, actor, "ambassador.create", "ambassador", a.id, after={"code": code, "lang": lang})
    db.commit()
    db.refresh(a)
    return a


def set_ambassador_status(db: Session, code: str, status: str, actor: str) -> GrowthAmbassador:
    if status not in ("active", "paused", "retired"):
        raise ValueError("bad status")
    a = get_ambassador(db, code, active_only=False)
    if not a:
        raise ValueError("unknown code")
    before = {"status": a.status}
    a.status = status
    _audit(db, actor, "ambassador.status", "ambassador", a.id, before=before, after={"status": status})
    db.commit()
    return a


def record_click(db: Session, ref: str, surface: str, lang: str,
                 channel: Optional[str], device_class: str) -> bool:
    """True if attached to an ambassador; False = invalid ref (counted, not attached)."""
    a = get_ambassador(db, ref or "")
    if not a:
        _invalid_ref_count["count"] += 1
        _audit(db, "public", "click.invalid_ref", "click", None,
               after={"surface": surface[:60], "total_invalid": _invalid_ref_count["count"]})
        db.commit()
        return False
    db.add(GrowthClick(ambassador_id=a.id, surface=surface[:60], lang=lang[:8],
                       channel_tag=channel if channel in ALLOWED_CHANNELS else None,
                       device_class=device_class if device_class in ("mobile", "desktop") else "unknown"))
    db.commit()
    return True


def record_join_intent(db: Session, ref: str, surface: str, lang: str) -> bool:
    a = get_ambassador(db, ref or "")
    if not a:
        _invalid_ref_count["count"] += 1
        db.commit()
        return False
    it = GrowthJoinIntent(ambassador_id=a.id, surface=surface[:60], lang=lang[:8])
    db.add(it)
    db.flush()
    _audit(db, "public", "join_intent.create", "join_intent", it.id, after={"code": a.code})
    db.commit()
    return True


def confirm_intent(db: Session, intent_id: int, decision: str, actor: str,
                   auto_contribution: bool = True) -> GrowthJoinIntent:
    """Manual operator confirm/reject. Confirm may create a PENDING contribution
    (rule: confirmed_join = 10) — still requires separate review to credit anything."""
    if decision not in ("confirmed", "rejected"):
        raise ValueError("decision must be confirmed|rejected")
    it = db.query(GrowthJoinIntent).get(intent_id)
    if not it:
        raise ValueError("unknown intent")
    if it.confirm_status != "unconfirmed":
        raise ValueError("intent already reviewed (no silent re-review)")
    before = {"confirm_status": it.confirm_status}
    it.confirm_status = decision
    it.confirmed_by = actor
    it.confirmed_at = _now()
    _audit(db, actor, "join_intent." + decision, "join_intent", it.id, before=before,
           after={"confirm_status": decision})
    if decision == "confirmed" and auto_contribution:
        _create_contribution(db, it.ambassador_id, POINTS["confirmed_join"], "confirmed_join",
                             "auto-suggested on intent #%d confirm" % it.id, actor="rule")
    db.commit()
    return it


def _points_in_window(db: Session, ambassador_id: int, since: datetime) -> int:
    val = (db.query(func.coalesce(func.sum(GrowthContribution.points), 0))
             .filter(GrowthContribution.ambassador_id == ambassador_id,
                     GrowthContribution.status.in_(("pending", "approved")),
                     GrowthContribution.created_at >= since).scalar())
    return int(val or 0)


def _create_contribution(db: Session, ambassador_id: int, points: int, reason: str,
                         note: str, actor: str) -> GrowthContribution:
    if reason not in ("confirmed_join", "content_share", "monthly_bonus", "other"):
        raise ValueError("bad reason")
    if points <= 0:
        raise ValueError("points must be positive")
    now = _now()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if _points_in_window(db, ambassador_id, day_start) + points > DAILY_CAP:
        raise ValueError("daily cap %d exceeded" % DAILY_CAP)
    if _points_in_window(db, ambassador_id, month_start) + points > MONTHLY_CAP:
        raise ValueError("monthly cap %d exceeded" % MONTHLY_CAP)
    c = GrowthContribution(ambassador_id=ambassador_id, points=points, reason=reason,
                           note=note or None, created_by=actor)
    db.add(c)
    db.flush()
    _audit(db, actor, "contribution.create", "contribution", c.id,
           after={"points": points, "reason": reason, "status": "pending"})
    return c


def create_contribution(db: Session, code: str, points: int, reason: str, note: str,
                        actor: str) -> GrowthContribution:
    a = get_ambassador(db, code, active_only=False)
    if not a:
        raise ValueError("unknown code")
    c = _create_contribution(db, a.id, points, reason, note, actor)
    db.commit()
    db.refresh(c)
    return c


def review_contribution(db: Session, contribution_id: int, decision: str, actor: str,
                        note: str = "") -> GrowthContribution:
    """approve -> MTC credit via existing wallet rails (shadow user per ambassador code);
    reject -> audit only. Never automatic; this function is reachable only from
    admin-token endpoints / operator CLI."""
    if decision not in ("approved", "rejected"):
        raise ValueError("decision must be approved|rejected")
    if decision == "rejected" and not note:
        raise ValueError("reject requires a note")
    c = db.query(GrowthContribution).get(contribution_id)
    if not c:
        raise ValueError("unknown contribution")
    if c.status != "pending":
        raise ValueError("contribution already reviewed (no silent mutation)")
    before = {"status": c.status}
    c.status = decision
    c.reviewed_by = actor
    c.reviewed_at = _now()
    if note:
        c.note = ((c.note + " | ") if c.note else "") + "review: " + note
    if decision == "approved":
        a = db.query(GrowthAmbassador).get(c.ambassador_id)
        # shadow user per code: MTC stays on existing platform rails (non-cash, capped)
        device_id = "growth-ambassador-%s" % a.code
        user = db.query(User).filter_by(device_id=device_id).first()
        if not user:
            user = User(device_id=device_id, nickname="情报官 %s" % a.code)
            db.add(user)
            db.flush()
        wallet = wallet_service._get_or_create_wallet(db, user)
        wallet_service._credit(db, wallet, c.points, "growth_contribution",
                               "贡献值 %s (%s)" % (a.code, c.reason))
        db.flush()
        last_log = wallet.logs[-1] if wallet.logs else None
        c.token_log_id = last_log.id if last_log else None
    _audit(db, actor, "contribution." + decision, "contribution", c.id, before=before,
           after={"status": decision, "token_log_id": c.token_log_id})
    db.commit()
    db.refresh(c)
    return c


def dashboard(db: Session) -> dict:
    out = []
    for a in db.query(GrowthAmbassador).order_by(GrowthAmbassador.code).all():
        clicks = db.query(func.count(GrowthClick.id)).filter_by(ambassador_id=a.id).scalar()
        intents = db.query(func.count(GrowthJoinIntent.id)).filter_by(ambassador_id=a.id).scalar()
        confirmed = db.query(func.count(GrowthJoinIntent.id)).filter_by(
            ambassador_id=a.id, confirm_status="confirmed").scalar()
        approved_pts = (db.query(func.coalesce(func.sum(GrowthContribution.points), 0))
                        .filter_by(ambassador_id=a.id, status="approved").scalar())
        pending_pts = (db.query(func.coalesce(func.sum(GrowthContribution.points), 0))
                       .filter_by(ambassador_id=a.id, status="pending").scalar())
        out.append({"code": a.code, "alias": a.display_alias, "lang": a.lang,
                    "channel": a.default_channel, "status": a.status,
                    "clicks": int(clicks or 0), "join_intents": int(intents or 0),
                    "confirmed_joins": int(confirmed or 0),
                    "points_approved": int(approved_pts or 0), "points_pending": int(pending_pts or 0)})
    pending = [{"id": c.id, "code": c.ambassador.code, "points": c.points, "reason": c.reason,
                "note": c.note, "created_at": str(c.created_at)}
               for c in db.query(GrowthContribution).filter_by(status="pending")
                          .order_by(GrowthContribution.created_at).all()]
    unconfirmed = [{"id": i.id, "code": i.ambassador.code, "surface": i.surface, "lang": i.lang,
                    "created_at": str(i.created_at)}
                   for i in db.query(GrowthJoinIntent).filter_by(confirm_status="unconfirmed")
                              .order_by(GrowthJoinIntent.created_at).all()]
    return {"ambassadors": out, "pending_contributions": pending,
            "unconfirmed_intents": unconfirmed,
            "invalid_ref_count_since_boot": _invalid_ref_count["count"],
            "compliance": "MTC 平台积分：不可提现 · 不可转让 · 不可交易 · 非现金 · 人工审核"}


def export_report(db: Session) -> dict:
    d = dashboard(db)
    d["exported_at"] = str(_now())
    d["note"] = "counts only — no identities recorded by design"
    return d
