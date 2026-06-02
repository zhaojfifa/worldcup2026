from __future__ import annotations
from typing import Optional, List
"""
Match + Prediction query service.
All data returned by this service is AI analysis for informational purposes only.
No betting recommendations; no guaranteed outcomes.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

from app.models import Match, Prediction, Report, LiveCorrection
from app.schemas.match import (
    MatchListItem, MatchDetail, ReportOut,
    TeamOut, WinProbOut, FeatureFactorOut, TrendPointOut, LiveCorrectionOut,
)


def _team_out(team) -> TeamOut:
    return TeamOut(name=team.name_zh, flag=team.flag_emoji)


def _win_prob_from_prediction(pred: Prediction) -> WinProbOut:
    return WinProbOut(home=pred.prob_home, draw=pred.prob_draw, away=pred.prob_away)


def _latest_correction(match: Match) -> Optional[LiveCorrectionOut]:
    if not match.corrections:
        return None
    latest = sorted(match.corrections, key=lambda c: c.created_at, reverse=True)[0]
    return LiveCorrectionOut(
        trigger=latest.trigger,
        before=WinProbOut(
            home=latest.prob_home_before,
            draw=latest.prob_draw_before,
            away=latest.prob_away_before,
        ),
        after=WinProbOut(
            home=latest.prob_home_after,
            draw=latest.prob_draw_after,
            away=latest.prob_away_after,
        ),
        reason=latest.reason or "",
        timestamp=latest.created_at,
    )


def get_matches(db: Session) -> List[MatchListItem]:
    matches = (
        db.query(Match)
        .options(
            joinedload(Match.home_team),
            joinedload(Match.away_team),
            joinedload(Match.prediction),
            joinedload(Match.corrections),
        )
        .order_by(Match.kickoff_time)
        .all()
    )
    result = []
    for m in matches:
        pred = m.prediction
        if not pred:
            continue
        # Use latest correction probabilities if available
        correction = _latest_correction(m)
        win_prob = (
            correction.after if correction
            else _win_prob_from_prediction(pred)
        )
        result.append(MatchListItem(
            id=m.id,
            external_id=m.external_id,
            home_team=_team_out(m.home_team),
            away_team=_team_out(m.away_team),
            kickoff_time=m.kickoff_time,
            tag=m.tag,
            status=m.status,
            win_prob=win_prob,
            recommended_score=pred.recommended_score,
            risk_level=pred.risk_level,
            risk_note=pred.risk_note,
            confidence=pred.confidence,
            updated_at=m.updated_at,
        ))
    return result


def get_match_detail(db: Session, match_id: int) -> Optional[MatchDetail]:
    m = (
        db.query(Match)
        .options(
            joinedload(Match.home_team),
            joinedload(Match.away_team),
            joinedload(Match.prediction),
            joinedload(Match.corrections),
        )
        .filter(Match.id == match_id)
        .first()
    )
    if not m or not m.prediction:
        return None

    pred = m.prediction
    correction = _latest_correction(m)
    win_prob = correction.after if correction else _win_prob_from_prediction(pred)

    return MatchDetail(
        id=m.id,
        external_id=m.external_id,
        home_team=_team_out(m.home_team),
        away_team=_team_out(m.away_team),
        kickoff_time=m.kickoff_time,
        tag=m.tag,
        status=m.status,
        win_prob=win_prob,
        recommended_score=pred.recommended_score,
        risk_level=pred.risk_level,
        risk_note=pred.risk_note,
        confidence=pred.confidence,
        free_note=pred.free_note,
        live_correction=correction,
        updated_at=m.updated_at,
    )


def get_report(db: Session, match_id: int) -> Optional[ReportOut]:
    m = (
        db.query(Match)
        .options(
            joinedload(Match.home_team),
            joinedload(Match.away_team),
            joinedload(Match.prediction),
            joinedload(Match.report),
            joinedload(Match.corrections),
        )
        .filter(Match.id == match_id)
        .first()
    )
    if not m or not m.prediction or not m.report:
        return None

    pred = m.prediction
    rep = m.report
    correction = _latest_correction(m)
    win_prob = correction.after if correction else _win_prob_from_prediction(pred)

    return ReportOut(
        match_id=m.id,
        features=[FeatureFactorOut(**f) for f in rep.features],
        trend_history=[TrendPointOut(**t) for t in rep.trend_history],
        tactics_note=rep.tactics_note,
        verdict_summary=rep.verdict_summary,
        win_prob=win_prob,
        recommended_score=pred.recommended_score,
        risk_level=pred.risk_level,
        confidence=pred.confidence,
        live_correction=correction,
    )
