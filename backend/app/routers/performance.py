from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.performance import performance_service

router = APIRouter(prefix="/api/v1", tags=["performance"])


@router.get("/performance/daily")
def performance_daily(
    day: Optional[str] = Query(default=None, description="YYYY-MM-DD; defaults to today (UTC)"),
    db: Session = Depends(get_db),
):
    """
    Daily 战绩 computed from stored settlements (traceable to real results).
    Returns zeros + disclaimer when no settlements exist yet
    (真实赛果回灌后开放).
    """
    return performance_service.daily(db, day)


@router.get("/performance/summary")
def performance_summary(db: Session = Depends(get_db)):
    """Aggregate 战绩 summary. Empty-safe; always includes disclaimer."""
    return performance_service.summary(db)
