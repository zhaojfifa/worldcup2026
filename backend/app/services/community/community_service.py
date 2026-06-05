from __future__ import annotations
"""
Community service — social channel config + anonymous in-app engagement.

Anonymous only: counts, no IP, no user identity, no personal data.
No UGC, no comments, no posting, no bots.
"""
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from app.models import SocialChannel, MatchEngagement, Match
from app.schemas.social import (
    SocialChannelOut, ChannelUpsertRequest, CommunityHeat, HeatMatch,
)

# event_type → MatchEngagement counter field (per-match events only)
_EVENT_FIELD = {
    "view_match": "views_count",
    "click_detail": "detail_clicks",
    "click_unlock": "unlock_clicks",
    "click_share": "share_clicks",
    "click_community": "community_clicks",
    "click_social_channel": "social_channel_clicks",
}

_INTERACTION_FIELDS = [
    "views_count", "detail_clicks", "unlock_clicks",
    "favorite_count", "share_clicks", "community_clicks", "social_channel_clicks",
]


# ── Channels ────────────────────────────────────────────────────────────────
def list_channels(db: Session) -> List[SocialChannelOut]:
    rows = (
        db.query(SocialChannel)
        .filter(SocialChannel.is_enabled == True)  # noqa: E712
        .order_by(SocialChannel.sort_order, SocialChannel.id)
        .all()
    )
    return [SocialChannelOut.model_validate(r) for r in rows]


def upsert_channel(db: Session, req: ChannelUpsertRequest) -> SocialChannelOut:
    row = db.query(SocialChannel).filter(SocialChannel.channel_name == req.channel_name).first()
    if row:
        row.display_name = req.display_name
        row.status = req.status
        row.public_url = req.public_url
        row.description = req.description
        row.locale = req.locale
        row.is_enabled = req.is_enabled
        row.sort_order = req.sort_order
    else:
        row = SocialChannel(**req.model_dump())
        db.add(row)
    db.commit()
    db.refresh(row)
    return SocialChannelOut.model_validate(row)


# ── Events ──────────────────────────────────────────────────────────────────
def track_event(db: Session, event_type: str, match_id: Optional[int]) -> None:
    """Increment the matching counter. Anonymous; safe no-op when no match field."""
    field = _EVENT_FIELD.get(event_type)
    if not field or match_id is None:
        return  # global events (e.g. view_home) are accepted but not stored per-match

    eng = db.query(MatchEngagement).filter(MatchEngagement.match_id == match_id).first()
    if not eng:
        # only create if the match exists
        if not db.query(Match.id).filter(Match.id == match_id).first():
            return
        eng = MatchEngagement(match_id=match_id)
        db.add(eng)
        db.flush()
    setattr(eng, field, (getattr(eng, field) or 0) + 1)
    eng.last_updated_at = datetime.now(timezone.utc)
    db.commit()


# ── Heat ────────────────────────────────────────────────────────────────────
def _interactions(eng: MatchEngagement) -> int:
    return sum(int(getattr(eng, f) or 0) for f in _INTERACTION_FIELDS)


def community_heat(db: Session, top_n: int = 5) -> CommunityHeat:
    all_engs = db.query(MatchEngagement).all()
    total = sum(_interactions(e) for e in all_engs)
    ranked = sorted(all_engs, key=_interactions, reverse=True)
    top: List[HeatMatch] = []
    for e in ranked[:top_n]:
        inter = _interactions(e)
        if inter <= 0:
            continue
        m = (
            db.query(Match)
            .options(joinedload(Match.home_team), joinedload(Match.away_team))
            .filter(Match.id == e.match_id)
            .first()
        )
        if not m:
            continue
        top.append(HeatMatch(
            match_id=e.match_id,
            home=m.home_team.name_zh if m.home_team else "",
            away=m.away_team.name_zh if m.away_team else "",
            interactions=inter,
        ))

    enabled_channels = [
        c.channel_name
        for c in db.query(SocialChannel)
        .filter(SocialChannel.is_enabled == True)  # noqa: E712
        .order_by(SocialChannel.sort_order, SocialChannel.id).all()
    ]

    last_updated = None
    if all_engs:
        stamps = [e.last_updated_at for e in all_engs if e.last_updated_at]
        if stamps:
            last_updated = max(stamps)

    message = "社区热度建设中" if total == 0 else "社区热度实时更新"
    return CommunityHeat(
        top_matches=top,
        total_interactions=total,
        hot_channels=enabled_channels,
        updated_at=last_updated,
        message=message,
    )
