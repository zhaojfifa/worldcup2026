"""
Fixtures sync job — Day 4 implementation.
Polls API-FOOTBALL every hour for WC 2026 fixtures and upserts into DB.
"""


def sync_fixtures():
    """
    Day 3: stub — no-op.
    Day 4: call api_football.get_fixtures(league_id=1, season=2026)
           and upsert Match + Team rows.
    """
    pass


def sync_lineups(match_id: int):
    """
    Day 4: called 35 minutes before kickoff.
    Fetches confirmed lineups from API-FOOTBALL and triggers LiveCorrection.
    """
    pass
