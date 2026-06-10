from __future__ import annotations
"""
Scout Pack builder (Phase 2 + Phase 3) — pure normalization, no network/DB.

Takes a bundle of API-FOOTBALL ``EndpointResult`` objects for one fixture and
produces a redacted, bounded, provenance-tagged internal Scout Pack:

- Every section is wrapped in an Evidence Field envelope (real value or honest
  "source required"). Only **whitelisted** fields are copied → no image URLs,
  no raw vendor payload, lists bounded by the contract limits.
- ``source_ledger`` records per-field provenance; ``missing_evidence`` records
  every absent field with a localized reason.
- ``injuries`` returning 0 results is recorded as **unresolved** (never "no
  injuries"); the feature snapshot carries ``injuries_unresolved=True``.
- The feature snapshot is a *coverage* read (which evidence exists), not a
  prediction or betting signal.
"""
from typing import Any, Optional

from app.services.api_football_client import EndpointResult
from app.services.scout_pack import contract as C
from app.services.scout_pack.contract import (
    evidence_field,
    missing_field,
    loc,
)

# Sections that count toward the data-coverage score.
COVERAGE_FIELDS = [
    "fixture", "teams", "lineups", "formation", "coach",
    "events_summary", "team_statistics", "player_statistics", "squad",
]


def _f(num: Any) -> Optional[float]:
    try:
        return float(num)
    except (TypeError, ValueError):
        return None


def _first(res: Optional[EndpointResult]) -> Optional[dict]:
    if res and isinstance(res.response, list) and res.response:
        return res.response[0]
    return None


def _avail(res: Optional[EndpointResult]) -> bool:
    return bool(res and res.ok)


def _ep(res: Optional[EndpointResult], default: str = "") -> str:
    return res.endpoint if res else default


# --------------------------------------------------------------------------- #
#  Section builders (whitelist only — inherently redacted)                     #
# --------------------------------------------------------------------------- #
def _build_fixture(res, fid, ts) -> dict:
    fx = _first(res)
    if not fx:
        return missing_field(C.FALLBACK_GENERIC, "fixture not returned",
                             endpoint=_ep(res, "/fixtures"), fixture_id=fid, last_checked_at=ts)
    f = fx.get("fixture") or {}
    lg = fx.get("league") or {}
    teams = fx.get("teams") or {}
    goals = fx.get("goals") or {}
    venue = f.get("venue") or {}
    status = f.get("status") or {}
    home, away = teams.get("home") or {}, teams.get("away") or {}
    winner = "home" if home.get("winner") else ("away" if away.get("winner") else "draw_or_unknown")
    value = {
        "fixture_id": (f.get("id")),
        "date": f.get("date"),
        "status": status.get("long") or status.get("short"),
        "venue": {"name": venue.get("name"), "city": venue.get("city")},
        "league": {"name": lg.get("name"), "season": lg.get("season"), "round": lg.get("round")},
        "home_team": {"id": home.get("id"), "name": home.get("name")},
        "away_team": {"id": away.get("id"), "name": away.get("name")},
        "final_score": {"home": goals.get("home"), "away": goals.get("away")},
        "result_winner": winner,
    }
    return evidence_field(value, True, endpoint=_ep(res), fixture_id=fid, last_checked_at=ts,
                          confidence="high", license_status="ok", fallback_text=C.FALLBACK_GENERIC)


def _build_teams(team_home, team_away, fx_fallback, fid, ts) -> dict:
    def one(res, fb):
        t = _first(res)
        if t:
            tm, vn = t.get("team") or {}, t.get("venue") or {}
            return {"id": tm.get("id"), "name": tm.get("name"), "country": tm.get("country"),
                    "founded": tm.get("founded"), "national": tm.get("national"),
                    "venue": {"name": vn.get("name"), "city": vn.get("city")}}
        # fall back to the basic id/name carried by the fixture
        return {"id": fb.get("id"), "name": fb.get("name"), "country": None,
                "founded": None, "national": None, "venue": {"name": None, "city": None}}
    fxv = fx_fallback.get("value") or {}
    home_fb = fxv.get("home_team") or {}
    away_fb = fxv.get("away_team") or {}
    available = _avail(team_home) or _avail(team_away) or bool(home_fb.get("id"))
    value = {"home": one(team_home, home_fb), "away": one(team_away, away_fb)}
    conf = "high" if (_avail(team_home) and _avail(team_away)) else "medium"
    return evidence_field(value, available, endpoint=_ep(team_home, "/teams"), fixture_id=fid,
                          last_checked_at=ts, confidence=conf, license_status="ok",
                          fallback_text=C.FALLBACK_GENERIC,
                          missing_reason="teams endpoint empty")


def _xi(entries) -> list:
    out = []
    for e in (entries or []):
        p = (e or {}).get("player") or {}
        out.append({"name": p.get("name"), "number": p.get("number"),
                    "pos": p.get("pos"), "grid": p.get("grid")})
    return out


def _build_lineups(res, fid, ts) -> dict:
    if not _avail(res):
        return missing_field(C.FALLBACK_LINEUPS, "lineups endpoint returned no data",
                             endpoint=_ep(res, "/fixtures/lineups"), fixture_id=fid, last_checked_at=ts)
    value = []
    for team in res.response:
        tm = (team or {}).get("team") or {}
        coach = (team or {}).get("coach") or {}
        value.append({
            "team": {"id": tm.get("id"), "name": tm.get("name")},
            "formation": team.get("formation"),
            "coach": {"id": coach.get("id"), "name": coach.get("name")},
            "startXI": _xi(team.get("startXI")),
            "substitutes": _xi(team.get("substitutes")),
        })
    return evidence_field(value, True, endpoint=_ep(res), fixture_id=fid, last_checked_at=ts,
                          confidence="high", license_status="ok", fallback_text=C.FALLBACK_LINEUPS)


def _build_formation(lineups_field, fid, ts) -> dict:
    lv = lineups_field.get("value")
    if not lv:
        return missing_field(C.FALLBACK_FORMATION, "formation requires lineups (not available)",
                             endpoint="/fixtures/lineups", fixture_id=fid, last_checked_at=ts)
    value = {}
    for i, side in enumerate(("home", "away")):
        if i < len(lv):
            value[side] = {"team": (lv[i].get("team") or {}).get("name"),
                           "formation": lv[i].get("formation")}
    available = any(v.get("formation") for v in value.values())
    return evidence_field(value, available, endpoint="/fixtures/lineups", fixture_id=fid,
                          last_checked_at=ts, confidence="high", license_status="ok",
                          fallback_text=C.FALLBACK_FORMATION, missing_reason="no formation in lineups")


def _build_coach(lineups_field, coach_home, coach_away, fid, ts) -> dict:
    """Prefer the actual match coach (from lineups); enrich age/nationality from /coachs."""
    lv = lineups_field.get("value") or []

    def enrich(coach_id, coach_res):
        for c in ((coach_res.response if coach_res else None) or []):
            if c.get("id") == coach_id:
                return {"age": c.get("age"), "nationality": c.get("nationality")}
        first = _first(coach_res)
        if first and coach_id is None:
            return {"age": first.get("age"), "nationality": first.get("nationality")}
        return {"age": None, "nationality": None}

    value = {}
    for i, (side, cres) in enumerate((("home", coach_home), ("away", coach_away))):
        base = lv[i].get("coach") if i < len(lv) else None
        if base and base.get("name"):
            extra = enrich(base.get("id"), cres)
            value[side] = {"id": base.get("id"), "name": base.get("name"), **extra}
        else:
            c = _first(cres)
            value[side] = ({"id": c.get("id"), "name": c.get("name"),
                            "age": c.get("age"), "nationality": c.get("nationality")} if c
                           else {"id": None, "name": None, "age": None, "nationality": None})
    available = any(v.get("name") for v in value.values())
    conf = "high" if (lv and all(v.get("name") for v in value.values())) else "medium"
    return evidence_field(value, available, endpoint="/fixtures/lineups + /coachs", fixture_id=fid,
                          last_checked_at=ts, confidence=conf, license_status="ok",
                          fallback_text=C.FALLBACK_COACH, missing_reason="coach not available")


def _build_squad(squad_home, squad_away, fid, ts) -> dict:
    def one(res):
        s = _first(res)
        if not s:
            return None
        players = s.get("players") or []
        sample = [{"name": p.get("name"), "number": p.get("number"), "position": p.get("position")}
                  for p in players[:C.MAX_SQUAD_SAMPLE_PER_TEAM]]
        return {"team": (s.get("team") or {}).get("name"),
                "players_count": len(players), "sample": sample}
    value = {"home": one(squad_home), "away": one(squad_away)}
    available = bool(value["home"] or value["away"])
    return evidence_field(value, available, endpoint=_ep(squad_home, "/players/squads"), fixture_id=fid,
                          last_checked_at=ts, confidence="medium", license_status="ok",
                          fallback_text=C.FALLBACK_SQUAD, missing_reason="squad endpoint empty",
                          )


def _build_events(res, fid, ts) -> dict:
    if not _avail(res):
        return missing_field(C.FALLBACK_EVENTS, "events endpoint returned no data",
                             endpoint=_ep(res, "/fixtures/events"), fixture_id=fid, last_checked_at=ts)
    by_type: dict[str, int] = {}
    timeline = []
    for ev in res.response:
        et = ev.get("type") or "Other"
        by_type[et] = by_type.get(et, 0) + 1
    for ev in res.response[: C.MAX_EVENTS]:
        t = ev.get("time") or {}
        elapsed = t.get("elapsed")
        if t.get("extra"):
            elapsed = f"{elapsed}+{t.get('extra')}"
        timeline.append({
            "minute": elapsed,
            "type": ev.get("type"),
            "detail": ev.get("detail"),
            "team": (ev.get("team") or {}).get("name"),
            "player": (ev.get("player") or {}).get("name"),
            "assist": (ev.get("assist") or {}).get("name"),
        })
    value = {"total": res.results, "by_type": by_type, "timeline": timeline,
             "timeline_truncated": res.results > C.MAX_EVENTS}
    return evidence_field(value, True, endpoint=_ep(res), fixture_id=fid, last_checked_at=ts,
                          confidence="high", license_status="ok", fallback_text=C.FALLBACK_EVENTS)


def _build_team_statistics(res, fid, ts) -> dict:
    if not _avail(res):
        return missing_field(C.FALLBACK_TEAM_STATS, "statistics endpoint returned no data",
                             endpoint=_ep(res, "/fixtures/statistics"), fixture_id=fid, last_checked_at=ts)
    value = []
    for team in res.response:
        stats = {}
        for s in (team.get("statistics") or [])[: C.MAX_TEAM_STATS_PER_TEAM]:
            typ = s.get("type")
            if typ and "expected" in typ.lower():  # exclude xG / expected_* (policy: not used this round)
                continue
            stats[typ] = s.get("value")
        value.append({"team": (team.get("team") or {}).get("name"), "stats": stats})
    return evidence_field(value, True, endpoint=_ep(res), fixture_id=fid, last_checked_at=ts,
                          confidence="high", license_status="ok", fallback_text=C.FALLBACK_TEAM_STATS)


def _build_player_statistics(res, fid, ts) -> dict:
    if not _avail(res):
        return missing_field(C.FALLBACK_PLAYER_STATS, "fixture players endpoint returned no data",
                             endpoint=_ep(res, "/fixtures/players"), fixture_id=fid, last_checked_at=ts)
    value = []
    for team in res.response:
        rows = []
        for entry in (team.get("players") or []):
            p = entry.get("player") or {}
            st = (entry.get("statistics") or [{}])[0]
            games, goals = st.get("games") or {}, st.get("goals") or {}
            rows.append({
                "name": p.get("name"),
                "pos": games.get("position"),
                "minutes": games.get("minutes"),
                "rating": games.get("rating"),
                "goals": goals.get("total"),
                "assists": goals.get("assists"),
                "_rk": _f(games.get("rating")) or -1,
            })
        rows.sort(key=lambda r: r["_rk"], reverse=True)
        top = [{k: v for k, v in r.items() if k != "_rk"} for r in rows[: C.MAX_PLAYER_STATS_PER_TEAM]]
        # always capture each team's goalkeeper (the starter by minutes) — the GK is
        # often outside the top-N-by-rating slice but needed for the feature snapshot.
        gks = sorted((r for r in rows if r["pos"] == "G"),
                     key=lambda r: (r["minutes"] or 0, r["_rk"]), reverse=True)
        gk = {"name": gks[0]["name"], "rating": gks[0]["rating"]} if gks else None
        value.append({"team": (team.get("team") or {}).get("name"),
                      "players_count": len(team.get("players") or []),
                      "goalkeeper": gk,
                      "top_by_rating": top})
    return evidence_field(value, True, endpoint=_ep(res), fixture_id=fid, last_checked_at=ts,
                          confidence="high", license_status="ok", fallback_text=C.FALLBACK_PLAYER_STATS)


def _build_injuries_marker(res, fid, ts) -> dict:
    """injuries is the verified open gap. 0 results == UNRESOLVED, never 'no injuries'."""
    http = res.http_status if res else None
    results = res.results if res else 0
    reason = (f"endpoint returned {results} results (HTTP {http}) — UNRESOLVED: "
              "historical season may be unpopulated or needs fixture/current-season form; "
              "second-source verification required before any 'key absence' feature")
    return missing_field(C.MISSING_INJURIES, reason,
                         endpoint=_ep(res, "/injuries"), fixture_id=fid, last_checked_at=ts)


# --------------------------------------------------------------------------- #
#  Provenance + features                                                       #
# --------------------------------------------------------------------------- #
def _ledger_row(field_key: str, env: dict, res: Optional[EndpointResult]) -> dict:
    return {
        "field": field_key,
        "source": env.get("source"),
        "endpoint": env.get("endpoint"),
        "params": (res.params if res else None),
        "http_status": (res.http_status if res else None),
        "results": (res.results if res else None),
        "available": env.get("available"),
        "confidence": env.get("confidence"),
        "license_status": env.get("license_status"),
        "last_checked_at": env.get("last_checked_at"),
    }


def _feature_snapshot(sections: dict, injuries_field: dict, ts: str) -> dict:
    avail = {k: bool(sections[k].get("available")) for k in COVERAGE_FIELDS}
    covered = sum(1 for k in COVERAGE_FIELDS if avail[k])
    coverage_score = round(covered / len(COVERAGE_FIELDS) * 100)
    allowed = [k for k in COVERAGE_FIELDS
               if sections[k].get("available") and sections[k].get("license_status") == "ok"]
    forbidden = [
        "injuries (unresolved — 0 results; do NOT state 'no injuries')",
        "player_absence_impact",
        "suspensions",
        "any field not present in source_ledger",
        "match outcome prediction or any financial / profit signal",
    ] + [k for k in COVERAGE_FIELDS if not sections[k].get("available")]
    return {
        "lineup_available": avail["lineups"],
        "formation_available": avail["formation"],
        "coach_available": avail["coach"],
        "events_available": avail["events_summary"],
        "statistics_available": avail["team_statistics"],
        "player_statistics_available": avail["player_statistics"],
        "squad_available": avail["squad"],
        "injuries_unresolved": True,  # verified open gap; flips only on a non-empty source
        "data_freshness": ts,
        "coverage_score": coverage_score,
        "coverage_score_note": loc(
            "仅数据覆盖评分，不是预测命中率，不作为博彩或资金信号",
            "Chỉ là điểm độ phủ dữ liệu, không phải tỷ lệ dự đoán đúng, không phải tín hiệu tài chính",
            "Data-coverage score only — not a prediction hit-rate, not a financial signal",
        ),
        "ai_explanation_allowed_fields": allowed,
        "ai_explanation_forbidden_fields": forbidden,
    }


# --------------------------------------------------------------------------- #
#  Top-level assembly                                                          #
# --------------------------------------------------------------------------- #
def build_scout_pack(
    *,
    fixture_id: int,
    bundle: dict[str, Optional[EndpointResult]],
    last_checked_at: str,
    plan: Optional[str] = None,
    request_log: Optional[list] = None,
) -> dict:
    ts = last_checked_at
    fid = fixture_id
    b = bundle

    fixture = _build_fixture(b.get("fixture"), fid, ts)
    teams = _build_teams(b.get("team_home"), b.get("team_away"), fixture, fid, ts)
    lineups = _build_lineups(b.get("lineups"), fid, ts)
    formation = _build_formation(lineups, fid, ts)
    coach = _build_coach(lineups, b.get("coach_home"), b.get("coach_away"), fid, ts)
    squad = _build_squad(b.get("squad_home"), b.get("squad_away"), fid, ts)
    events_summary = _build_events(b.get("events"), fid, ts)
    team_statistics = _build_team_statistics(b.get("statistics"), fid, ts)
    player_statistics = _build_player_statistics(b.get("players"), fid, ts)
    injuries_field = _build_injuries_marker(b.get("injuries"), fid, ts)

    sections = {
        "fixture": fixture, "teams": teams, "lineups": lineups, "formation": formation,
        "coach": coach, "squad": squad, "events_summary": events_summary,
        "team_statistics": team_statistics, "player_statistics": player_statistics,
    }

    # source_ledger: one provenance row per attempted field.
    ledger_map = {
        "fixture": b.get("fixture"), "teams": b.get("team_home"), "lineups": b.get("lineups"),
        "formation": b.get("lineups"), "coach": b.get("coach_home"), "squad": b.get("squad_home"),
        "events_summary": b.get("events"), "team_statistics": b.get("statistics"),
        "player_statistics": b.get("players"),
    }
    source_ledger = {k: _ledger_row(k, sections[k], ledger_map.get(k)) for k in sections}
    source_ledger["injuries"] = _ledger_row("injuries", injuries_field, b.get("injuries"))

    # missing_evidence: every absent field with a localized reason.
    missing_evidence = {}
    for k, env in {**sections, "injuries": injuries_field}.items():
        if not env.get("available"):
            missing_evidence[k] = {
                "reason": env.get("missing_reason"),
                "fallback_text": env.get("fallback_text"),
                "endpoint": env.get("endpoint"),
                "last_checked_at": env.get("last_checked_at"),
            }

    snapshot = _feature_snapshot(sections, injuries_field, ts)

    ai_allowed = snapshot["ai_explanation_allowed_fields"]
    ai_forbidden = snapshot["ai_explanation_forbidden_fields"]

    return {
        "schema_version": C.SCOUT_PACK_SCHEMA_VERSION,
        "source": C.SOURCE_API_FOOTBALL,
        "fixture_id": fid,
        "last_checked_at": ts,
        "plan": plan,
        "license_note": C.LICENSE_NOTE_INTERNAL,
        "operation_status": "paused",
        "public_ready": False,
        # --- Owner Phase-0 top-level contract sections ---
        "fixture": fixture,
        "teams": teams,
        "lineups": lineups,
        "formation": formation,
        "coach": coach,
        "squad": squad,
        "events_summary": events_summary,
        "team_statistics": team_statistics,
        "player_statistics": player_statistics,
        "missing_evidence": missing_evidence,
        "source_ledger": source_ledger,
        "ai_allowed_explanations": ai_allowed,
        "ai_forbidden_explanations": ai_forbidden,
        # --- Phase-3 feature snapshot + injuries marker ---
        "feature_snapshot": snapshot,
        "injuries": injuries_field,
        "request_summary": {
            "count": len(request_log or []),
            "log": (request_log or []),
        },
    }
