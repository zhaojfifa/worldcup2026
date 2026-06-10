from __future__ import annotations
"""
Customer recap API — serves the ScoutScore historical-recap content for the
frontend product flow (Home → Historical Recap → recap detail).

`GET /api/v1/recap/{fixture_id}?lang=zh|vi`

Backend proxy: reads the cached, server-side accountability report and returns a
compact customer payload. The frontend never calls API-FOOTBALL. No auth (public
read of historical, redacted content); no probability/odds/xG/injury inference.
"""
from fastapi import APIRouter, HTTPException, Query

from app.services.scoutscore.recap_view import build_recap_view

router = APIRouter(prefix="/api/v1", tags=["recap"])


@router.get("/recap/{fixture_id}")
def get_recap(fixture_id: str, lang: str = Query("zh")):
    # Only zh/vi are served (customer langs). en/mm → 404 so the frontend falls
    # back to its bundled copy (never Chinese for en/mm).
    view = build_recap_view(fixture_id, lang)
    if view is None:
        raise HTTPException(status_code=404, detail=f"no recap for fixture {fixture_id} ({lang})")
    return view
