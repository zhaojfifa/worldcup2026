from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WalletOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    balance: int
    total_earned: int
    total_spent: int
    last_checkin_date: Optional[str]


class CheckInRequest(BaseModel):
    user_id: int


class CheckInResponse(BaseModel):
    success: bool
    earned: int
    balance: int
    message: str


class UnlockReportRequest(BaseModel):
    user_id: int
    match_id: int
    method: str   # "cash" | "token"


class UnlockReportResponse(BaseModel):
    success: bool
    method: str
    balance: Optional[int]
    message: str


class SimulateCorrectionRequest(BaseModel):
    user_id: Optional[int] = None   # optional in demo mode


class SimulateCorrectionResponse(BaseModel):
    success: bool
    trigger: str
    before: dict
    after: dict
    reason: str
    timestamp: datetime


class JoinChallengeRequest(BaseModel):
    user_id: int
    chosen_option: str   # "A" or "B"


class JoinChallengeResponse(BaseModel):
    success: bool
    chosen_option: str
    message: str


class SubscribeRequest(BaseModel):
    user_id: int
    plan: str = "monthly"


class SubscribeResponse(BaseModel):
    success: bool
    plan: str
    message: str
