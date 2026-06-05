from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

DISCLAIMER = "历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。"


class StreakOut(BaseModel):
    user_id: int
    current_streak: int
    best_streak: int
    mtc_earned: int
    last_participation_date: Optional[str]
    disclaimer: str = DISCLAIMER


class RankingUser(BaseModel):
    rank: int
    display_name: str
    current_streak: int
    best_streak: int
    mtc_earned: int


class RankingsOut(BaseModel):
    top_users: List[RankingUser]
    ranking_type: str
    updated_at: Optional[datetime]
    disclaimer: str = DISCLAIMER


class SettleChallengeRequest(BaseModel):
    challenge_id: int
    user_id: int
    actual_result: str                 # "A" / "B" / "neutral"
    match_id: Optional[int] = None
    selected_option: Optional[str] = None  # override; else taken from ChallengeEntry


class SettleChallengeResponse(BaseModel):
    ok: bool
    is_correct: Optional[bool]
    mtc_reward: int
    current_streak: int
    best_streak: int
    message: str
