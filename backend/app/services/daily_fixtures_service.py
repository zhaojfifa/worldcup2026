from __future__ import annotations
"""
P1.3c — daily fixtures runtime store + assembly (Owner GO 2026-06-13).

Stores the daily-fixtures manifest uploaded by the operator (key 'daily_fixtures_current')
and assembles the public GET /api/v1/daily-fixtures response. Accepts EITHER the frontend-shaped
manifest (rows with `id`/`home`) or the docs-shaped registry (rows with `internal_fixture_id`/
`home_team`) and normalizes to the frontend shape so all client fallback tiers parse identically.

No score is ever invented here; this layer only stores and reshapes what match-sync produced.
"""
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.runtime_manifest import RuntimeManifest

CURRENT_KEY = "daily_fixtures_current"
FINISHED_CLASS = {"FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _norm_row(r: dict) -> dict:
    """Map a registry/frontend row to the canonical frontend shape (same as the static
    /data/daily-fixtures.json rows). Detects docs shape by `internal_fixture_id`/`home_team`."""
    if "home_team" in r or "internal_fixture_id" in r:  # docs shape
        return {
            "id": r.get("internal_fixture_id"),
            "external_game_id": r.get("external_game_id"),
            "home": r.get("home_team"), "away": r.get("away_team"),
            "kickoffUtc": r.get("kickoff_time_utc"),
            "status": r.get("status"),
            "lifecycle_state": r.get("lifecycle_state"),
            "preMatchAllowed": r.get("pre_match_allowed"),
            "recapReady": bool(r.get("recap_ready")),
            "recapNeeded": bool(r.get("recap_needed")),
            "renderable": bool(r.get("narrative_renderable")),
            "heroCandidate": bool(r.get("hero_candidate")),
            "recapCandidate": bool(r.get("recap_candidate")),
            "nextCandidate": bool(r.get("next_candidate")),
            "scoreHome": r.get("score_home"), "scoreAway": r.get("score_away"),
        }
    # already frontend shape
    return {
        "id": r.get("id"),
        "external_game_id": r.get("external_game_id"),
        "home": r.get("home"), "away": r.get("away"),
        "kickoffUtc": r.get("kickoffUtc"),
        "status": r.get("status"),
        "lifecycle_state": r.get("lifecycle_state"),
        "preMatchAllowed": r.get("preMatchAllowed"),
        "recapReady": bool(r.get("recapReady")),
        "recapNeeded": bool(r.get("recapNeeded")),
        "renderable": bool(r.get("renderable", True)),
        "heroCandidate": bool(r.get("heroCandidate")),
        "recapCandidate": bool(r.get("recapCandidate")),
        "nextCandidate": bool(r.get("nextCandidate")),
        "scoreHome": r.get("scoreHome"), "scoreAway": r.get("scoreAway"),
    }


def normalize_manifest(manifest: dict) -> dict:
    """Return a stored-shape manifest: {generated_at, source_mode, date, fixtures[frontend shape]}."""
    rows = [_norm_row(r) for r in (manifest.get("fixtures") or [])]
    return {
        "generated_at": manifest.get("generated_at") or manifest.get("captured_at"),
        "source_mode": manifest.get("source_mode", "manual"),
        "date": manifest.get("date") or manifest.get("generated_for_date"),
        "fixtures": rows,
    }


def upsert_current(db: Session, manifest: dict, by: str | None) -> dict:
    stored = normalize_manifest(manifest)
    stored["stored_at"] = _now().isoformat()
    row = db.get(RuntimeManifest, CURRENT_KEY)
    payload = json.dumps(stored, ensure_ascii=False)
    if row:
        row.value_json = payload
        row.updated_at = _now()
        row.updated_by = by
    else:
        db.add(RuntimeManifest(key=CURRENT_KEY, value_json=payload, updated_at=_now(), updated_by=by))
    db.commit()
    return stored


def get_current(db: Session) -> dict | None:
    row = db.get(RuntimeManifest, CURRENT_KEY)
    if not row:
        return None
    try:
        return json.loads(row.value_json)
    except Exception:
        return None


def assemble_response(db: Session) -> dict:
    """Public GET payload: {generated_at, source_mode, date, fixtures, recap_queue, active_hero,
    freshness}. Empty-but-valid when nothing is stored yet (client then falls back to its static
    file) — never 500s."""
    stored = get_current(db)
    if not stored:
        return {"generated_at": None, "source_mode": None, "date": None,
                "fixtures": [], "recap_queue": [], "active_hero": None,
                "freshness": {"stored": False, "reason": "no manifest uploaded yet"}}
    fixtures = stored.get("fixtures", [])
    recap_queue = [{
        "fixture": "%s vs %s" % (f.get("home"), f.get("away")),
        "id": f.get("id"), "final_score": (
            "%s-%s" % (f.get("scoreHome"), f.get("scoreAway")) if f.get("scoreHome") is not None else None),
        "recap_needed": bool(f.get("recapNeeded")) and not bool(f.get("recapReady")),
        "recap_ready": bool(f.get("recapReady")),
    } for f in fixtures if f.get("recapNeeded") or f.get("recapReady")]
    hero = next((f for f in fixtures if f.get("heroCandidate")), None)
    active_hero = None
    if hero:
        active_hero = {"id": hero.get("id"), "home": hero.get("home"), "away": hero.get("away"),
                       "kickoffUtc": hero.get("kickoffUtc"), "lifecycle_state": hero.get("lifecycle_state")}
    ga = stored.get("generated_at")
    age_seconds, stale = None, None
    if ga:
        try:
            gat = datetime.fromisoformat(ga)
            if gat.tzinfo is None:
                gat = gat.replace(tzinfo=timezone.utc)
            age_seconds = (_now() - gat).total_seconds()
            stale = age_seconds > 36 * 3600
        except Exception:
            pass
    # P1.4 product buckets — orchestration view for any API consumer.
    def _recap_status(f):
        if f.get("recapReady"):
            return "RECAP_READY"
        if f.get("id"):
            return "NEEDS_A4_RECAP"               # mapped fixture, recap not yet generated
        return "NEEDS_MAPPING_OR_A4_RECAP"        # unmapped: needs internal fixture + A4
    completed_matches = [{
        "id": f.get("id"), "home": f.get("home"), "away": f.get("away"),
        "score": ("%s-%s" % (f.get("scoreHome"), f.get("scoreAway")) if f.get("scoreHome") is not None else None),
        "lifecycle_state": f.get("lifecycle_state"), "recap_status": _recap_status(f),
        "renderable": bool(f.get("renderable")),
    } for f in fixtures if f.get("lifecycle_state") in FINISHED_CLASS]
    upcoming_needs_narrative = [{
        "id": f.get("id"), "home": f.get("home"), "away": f.get("away"), "kickoffUtc": f.get("kickoffUtc"),
    } for f in fixtures if f.get("preMatchAllowed") and not f.get("renderable")]
    product_status = ("赛程已同步 · 复盘队列已更新 · 下一场赛前判断已就绪" if active_hero
                      else "赛程已同步 · 复盘队列已更新 · 暂无可用赛前判断")
    return {
        "generated_at": ga, "source_mode": stored.get("source_mode"), "date": stored.get("date"),
        "fixtures": fixtures, "recap_queue": recap_queue, "active_hero": active_hero,
        "completed_matches": completed_matches, "upcoming_needs_narrative": upcoming_needs_narrative,
        "product_status": product_status,
        "freshness": {"stored": True, "stored_at": stored.get("stored_at"),
                      "age_seconds": age_seconds, "stale": stale},
    }
