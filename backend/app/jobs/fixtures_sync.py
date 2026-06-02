from __future__ import annotations
"""
Fixtures sync — pulls fixtures from API-FOOTBALL and upserts Team / Match rows.

Idempotent: matches are keyed by external_id ("AF-<fixtureId>"); existing rows
are updated, not duplicated. Newly created matches also get a baseline
prediction so they appear in /api/v1/matches immediately.

NOTE: On Render Starter, APScheduler-style in-process timers are NOT a
production scheduler. This module is invoked on demand via the admin endpoint;
production should run it from a dedicated Cron Job / Worker. See
docs/DAY4_DATA_AUTOMATION.md.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Team, Match, Prediction
from app.services.data_sources.api_football import api_football
from app.services.modeling import baseline

logger = logging.getLogger(__name__)

# Map API-FOOTBALL fixture status.short → our Match.status
_STATUS_MAP = {
    "NS": "scheduled", "TBD": "scheduled", "PST": "scheduled",
    "1H": "live", "2H": "live", "HT": "live", "ET": "live", "LIVE": "live", "P": "live",
    "FT": "finished", "AET": "finished", "PEN": "finished",
}


def _parse_dt(raw: Optional[str]) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _upsert_team(db: Session, api_team: dict) -> Optional[Team]:
    api_id = api_team.get("id")
    name = api_team.get("name")
    if api_id is None or not name:
        return None
    team = db.query(Team).filter(Team.api_id == api_id).first()
    if team:
        team.name = name
        if api_team.get("logo"):
            team.logo_url = api_team["logo"]
        return team
    team = Team(
        api_id=api_id,
        name=name,
        name_zh=name,            # zh mapping can be added later
        country=name,
        flag_emoji="⚽",          # placeholder; emoji mapping added later
        logo_url=api_team.get("logo"),
    )
    db.add(team)
    db.flush()
    return team


def _generate_baseline_prediction(db: Session, match: Match) -> None:
    """Create a baseline prediction for a match that has none."""
    inp = baseline.build_input_for_match(match)
    out = baseline.predict(inp)
    pred = Prediction(
        match_id=match.id,
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


def sync_fixtures(db: Session, league_id: Optional[int] = None, season: Optional[int] = None) -> dict:
    """
    Returns: {inserted, updated, skipped, errors:[...], total, mock_mode}
    """
    if not api_football.is_configured():
        return {
            "inserted": 0, "updated": 0, "skipped": 0, "errors": [],
            "total": 0, "mock_mode": True,
            "message": "API_FOOTBALL_KEY not configured — sync skipped (mock mode)",
        }

    try:
        fixtures = api_football.get_fixtures(league_id, season)
    except Exception as exc:
        logger.warning("get_fixtures failed: %s", exc)
        return {
            "inserted": 0, "updated": 0, "skipped": 0,
            "errors": [f"get_fixtures failed: {exc}"],
            "total": 0, "mock_mode": False,
            "message": "fixtures fetch failed",
        }

    inserted = updated = skipped = 0
    errors: list[str] = []

    for fx in fixtures:
        try:
            fixture = fx.get("fixture", {})
            teams = fx.get("teams", {})
            league = fx.get("league", {})
            fixture_id = fixture.get("id")
            home_api = teams.get("home") or {}
            away_api = teams.get("away") or {}

            if not fixture_id or not home_api.get("id") or not away_api.get("id"):
                skipped += 1
                continue

            home = _upsert_team(db, home_api)
            away = _upsert_team(db, away_api)
            if not home or not away:
                skipped += 1
                continue

            external_id = f"AF-{fixture_id}"
            kickoff = _parse_dt(fixture.get("date"))
            venue = (fixture.get("venue") or {}).get("name")
            stage = league.get("round")
            status = _STATUS_MAP.get((fixture.get("status") or {}).get("short", ""), "scheduled")

            match = db.query(Match).filter(Match.external_id == external_id).first()
            if match:
                match.home_team_id = home.id
                match.away_team_id = away.id
                match.kickoff_time = kickoff
                match.venue = venue
                match.stage = stage
                match.status = status
                match.updated_at = datetime.now(timezone.utc)
                updated += 1
            else:
                match = Match(
                    external_id=external_id,
                    home_team_id=home.id,
                    away_team_id=away.id,
                    kickoff_time=kickoff,
                    venue=venue,
                    stage=stage,
                    status=status,
                )
                db.add(match)
                db.flush()
                _generate_baseline_prediction(db, match)
                inserted += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))

    db.commit()
    total = len(fixtures)
    logger.info("fixtures sync: total=%s inserted=%s updated=%s skipped=%s errors=%s",
                total, inserted, updated, skipped, len(errors))
    return {
        "inserted": inserted, "updated": updated, "skipped": skipped,
        "errors": errors, "total": total, "mock_mode": False,
        "message": "fixtures sync complete",
    }


def sync_lineups(match_id: int):
    """Placeholder for T-35min lineup-driven LiveCorrection (Day 5)."""
    pass
