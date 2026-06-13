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
from app.services.modeling import baseline
from app.services import lifecycle


def _team_out(team) -> TeamOut:
    return TeamOut(name=team.name_zh, flag=team.flag_emoji)


def _freshness(m) -> dict:
    """Runtime freshness for a Match (P1.2b) — never trusts stored status alone."""
    return lifecycle.normalize(m.kickoff_time, stored_status=m.status)


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
            **_freshness(m),
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
        **_freshness(m),
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


def refresh_prediction(db: Session, match_id: int) -> Optional[MatchDetail]:
    """
    Recompute a match's prediction with the baseline rules model, persist it,
    touch updated_at, and return the standard MatchDetail (shape unchanged).
    """
    m = (
        db.query(Match)
        .options(joinedload(Match.home_team), joinedload(Match.away_team), joinedload(Match.prediction))
        .filter(Match.id == match_id)
        .first()
    )
    if not m:
        return None

    out = baseline.predict(baseline.build_input_for_match(m))

    pred = m.prediction
    if pred:
        pred.prob_home = out["prob_home"]
        pred.prob_draw = out["prob_draw"]
        pred.prob_away = out["prob_away"]
        pred.recommended_score = out["recommended_score"]
        pred.risk_level = out["risk_level"]
        pred.confidence = out["confidence"]
        pred.risk_note = out["risk_note"]
        pred.model_version = out["model_version"]
        pred.ai_provider = out["ai_provider"]
    else:
        pred = Prediction(
            match_id=m.id,
            prob_home=out["prob_home"],
            prob_draw=out["prob_draw"],
            prob_away=out["prob_away"],
            recommended_score=out["recommended_score"],
            risk_level=out["risk_level"],
            confidence=out["confidence"],
            risk_note=out["risk_note"],
            free_note="AI 基线模型已生成本场赛前判断，解锁可查看完整模型解释。",
            model_version=out["model_version"],
            ai_provider=out["ai_provider"],
        )
        db.add(pred)

    m.updated_at = datetime.now(timezone.utc)
    db.commit()

    return get_match_detail(db, match_id)
