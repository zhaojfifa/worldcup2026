from __future__ import annotations
"""
API response schemas — shape aligned with frontend mock.ts
so the frontend can swap mock data for real API with minimal changes.
"""
from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    flag: str   # emoji


class WinProbOut(BaseModel):
    home: float
    draw: float
    away: float


class FeatureFactorOut(BaseModel):
    label: str
    value: float


class TrendPointOut(BaseModel):
    label: str
    prob: float


class LiveCorrectionOut(BaseModel):
    trigger: str
    before: WinProbOut
    after: WinProbOut
    reason: str
    timestamp: datetime


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prob_home: float
    prob_draw: float
    prob_away: float
    recommended_score: Optional[str]
    risk_level: str
    confidence: float
    free_note: Optional[str]
    risk_note: Optional[str]


class MatchListItem(BaseModel):
    """Lightweight match card for the home page list."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: Optional[str]
    home_team: TeamOut
    away_team: TeamOut
    kickoff_time: datetime
    tag: Optional[str]
    status: str
    win_prob: WinProbOut
    recommended_score: Optional[str]
    risk_level: str
    risk_note: Optional[str]
    confidence: float
    updated_at: datetime


class MatchDetail(MatchListItem):
    """Full match detail — includes free note and live correction."""
    free_note: Optional[str]
    live_correction: Optional[LiveCorrectionOut]


class ReportOut(BaseModel):
    """Full AI report — paid / token-unlocked content."""
    match_id: int
    features: List[FeatureFactorOut]
    trend_history: List[TrendPointOut]
    tactics_note: Optional[str]
    verdict_summary: Optional[str]
    win_prob: WinProbOut
    recommended_score: Optional[str]
    risk_level: str
    confidence: float
    live_correction: Optional[LiveCorrectionOut]
