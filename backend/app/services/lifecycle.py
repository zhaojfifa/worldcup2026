"""
P1.2b — runtime fixture lifecycle normalization (Owner verdict 2026-06-13).

Trust-critical: API/DB `status` is NOT trusted on its own. A fixture whose kickoff has
passed is live/finished even if the stored status still says "scheduled". This module
computes the lifecycle at response time from kickoff_time + now (+ optional api status /
final score / recap availability) and derives packaging permissions.

It is the backend mirror of scripts/mvp2_fixture_lifecycle.py and
frontend/src/lib/freshness.ts — SAME states, SAME thresholds. Additive only: no DB
schema change; new response fields are optional.

Run the selftest:  python3 -m app.services.lifecycle   (from backend/)
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional

WATCH_MIN = 120
RESCORE_MIN = 30
FT_ESTIMATE_MIN = 130
RECAP_GRACE_MIN = 45
ARCHIVE_AFTER_MIN = 72 * 60

FINISHED_SHORT = {"FT", "AET", "PEN"}
LIVE_SHORT = {"1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"}
HALTED_SHORT = {"PST", "CANC", "ABD", "AWD", "WO"}
# stored DB statuses that are NOT authoritative once kickoff passes
_STALE_DB_STATUS = {"scheduled", "ns", "tbd", "not started", "", None}

PRE_MATCH_STATES = {"SCHEDULED", "T_MINUS_2H", "T_MINUS_30"}


def decide(now: datetime, kickoff: Optional[datetime], api_short: Optional[str] = None,
           recap_ready: bool = False) -> tuple[str, str]:
    """Pure lifecycle decision (mirror of the canonical spec). api_short is an
    API-FOOTBALL status.short when known; a stale DB 'scheduled' should be passed as None."""
    mins = None if kickoff is None else (kickoff - now).total_seconds() / 60.0
    trusted_live = api_short in LIVE_SHORT
    halted = api_short in HALTED_SHORT
    finished = (recap_ready or api_short in FINISHED_SHORT
                or (not trusted_live and not halted and mins is not None and mins <= -FT_ESTIMATE_MIN))
    if finished:
        if recap_ready:
            if mins is not None and mins <= -ARCHIVE_AFTER_MIN:
                return "ARCHIVED", "recap ready, kickoff >72h ago"
            return "RECAP_READY", "recap available"
        if mins is not None and mins > -(FT_ESTIMATE_MIN + RECAP_GRACE_MIN):
            return "FINISHED", "final-whistle window, recap not due yet"
        return "RECAP_PENDING", "match finished, recap generating"
    if halted:
        return "SCHEDULED", "halted/postponed (%s)" % api_short
    if trusted_live:
        return "LIVE", "live (%s)" % api_short
    if mins is not None and mins <= 0:
        return "LIVE", "kickoff passed without a finished signal — frozen"
    if mins is None:
        return "SCHEDULED", "no kickoff time on record"
    if mins <= RESCORE_MIN:
        return "T_MINUS_30", "T-%.0fmin" % mins
    if mins <= WATCH_MIN:
        return "T_MINUS_2H", "T-%.0fmin" % mins
    return "SCHEDULED", "T-%.0fmin" % mins


def normalize(kickoff: Optional[datetime], stored_status: Optional[str] = None,
              api_short: Optional[str] = None, recap_ready: bool = False,
              now: Optional[datetime] = None) -> dict:
    """Compute the lifecycle + packaging permissions for one fixture response.

    stored_status is the DB status string; if it's a stale 'scheduled'/'ns' we ignore it
    in favour of time (the bug P1.2b defeats). An explicit api_short (live/finished/halted)
    overrides. Returns the additive fields exposed on the API."""
    if now is None:
        now = datetime.now(timezone.utc)
    if kickoff is not None and kickoff.tzinfo is None:
        kickoff = kickoff.replace(tzinfo=timezone.utc)
    eff = api_short
    if eff is None and stored_status is not None:
        s = stored_status.strip().lower()
        if s not in _STALE_DB_STATUS:
            # a meaningful stored status (e.g. 'live'/'finished') maps to a short bucket
            if s in ("finished", "ft", "match finished"):
                eff = "FT"
            elif s in ("live", "in_play", "playing"):
                eff = "LIVE"
    state, reason = decide(now, kickoff, api_short=eff, recap_ready=recap_ready)
    # halted/postponed lands on SCHEDULED but must NOT allow pre-match packaging
    pre = state in PRE_MATCH_STATES and eff not in HALTED_SHORT
    return {
        "lifecycle_state": state,
        "pre_match_allowed": pre,
        "today_package_allowed": pre,
        "recap_needed": state in ("FINISHED", "RECAP_PENDING"),
        "recap_ready": state in ("RECAP_READY", "ARCHIVED"),
        "freshness_reason": reason,
    }


def _selftest() -> int:
    ko = datetime(2026, 6, 13, 22, 0, tzinfo=timezone.utc)
    t = lambda **kw: ko + timedelta(**kw)  # noqa: E731
    cases = [
        # (now, stored_status, api_short, recap_ready, expect_state, expect_pre)
        (t(hours=-21), "scheduled", None, False, "SCHEDULED", True),    # A future
        (t(days=8), "scheduled", None, False, "RECAP_PENDING", False),  # B stale-scheduled days past
        (t(hours=4), None, "FT", True, "RECAP_READY", False),           # C finished recap-ready
        (t(minutes=20), "scheduled", None, False, "LIVE", False),       # D synthetic live (now = ko+20m, stale 'scheduled')
        (t(minutes=50), None, "2H", False, "LIVE", False),
        (t(minutes=140), None, "FT", False, "FINISHED", False),
        (t(hours=-21), None, "PST", False, "SCHEDULED", False),         # halted: state ok but pre False
    ]
    fails = []
    for now, ss, short, ready, want_state, want_pre in cases:
        r = normalize(ko, stored_status=ss, api_short=short, recap_ready=ready, now=now)
        ok = r["lifecycle_state"] == want_state and r["pre_match_allowed"] == want_pre
        # halted special: pre_match must be False even though state=SCHEDULED
        if short == "PST":
            ok = r["lifecycle_state"] == "SCHEDULED" and r["pre_match_allowed"] is False
        if not ok:
            fails.append((now.isoformat(), ss, short, want_state, r["lifecycle_state"], r["pre_match_allowed"]))
        print("%s now=%s store=%-9s api=%-4s -> %-13s pre=%s" % (
            "PASS" if ok else "FAIL", now.strftime("%dT%H:%M"), ss, short,
            r["lifecycle_state"], r["pre_match_allowed"]))
    if fails:
        print("BACKEND LIFECYCLE SELFTEST FAIL: %s" % fails)
        return 1
    print("BACKEND LIFECYCLE SELFTEST PASS (%d cases)" % len(cases))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
