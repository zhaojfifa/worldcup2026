from __future__ import annotations
from typing import Optional, List
"""
MTC (Match Token Coin) wallet service.
COMPLIANCE:
- MTC = platform loyalty points ONLY
- NOT withdrawable, NOT transferable, NOT a financial asset
- No real-money pool; no guaranteed return
"""
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from app.models import User, TokenWallet, TokenLog, UnlockRecord, CommunitySubscription
from app.models.challenge import Challenge, ChallengeEntry
from app.models.live_correction import LiveCorrection
from app.models.match import Match
from app.config import get_settings
from app.schemas.token import (
    WalletOut, CheckInResponse, UnlockReportResponse,
    SimulateCorrectionResponse, JoinChallengeResponse, SubscribeResponse,
)

settings = get_settings()


def _get_or_create_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user


def _get_or_create_wallet(db: Session, user: User) -> TokenWallet:
    if user.wallet:
        return user.wallet
    wallet = TokenWallet(user_id=user.id, balance=520)  # new user gets 520 starter MTC
    db.add(wallet)
    db.flush()
    return wallet


def _credit(db: Session, wallet: TokenWallet, amount: int, event_type: str, note: str = "") -> None:
    wallet.balance += amount
    wallet.total_earned += amount
    log = TokenLog(
        user_id=wallet.user_id,
        wallet_id=wallet.id,
        amount=amount,
        balance_after=wallet.balance,
        event_type=event_type,
        note=note,
    )
    db.add(log)


def _debit(db: Session, wallet: TokenWallet, amount: int, event_type: str, note: str = "") -> None:
    wallet.balance -= amount
    wallet.total_spent += amount
    log = TokenLog(
        user_id=wallet.user_id,
        wallet_id=wallet.id,
        amount=-amount,
        balance_after=wallet.balance,
        event_type=event_type,
        note=note,
    )
    db.add(log)


def get_wallet(db: Session, user_id: int) -> WalletOut:
    user = _get_or_create_user(db, user_id)
    wallet = _get_or_create_wallet(db, user)
    db.commit()
    return WalletOut(
        user_id=user_id,
        balance=wallet.balance,
        total_earned=wallet.total_earned,
        total_spent=wallet.total_spent,
        last_checkin_date=wallet.last_checkin_date,
    )


def checkin(db: Session, user_id: int) -> CheckInResponse:
    user = _get_or_create_user(db, user_id)
    wallet = _get_or_create_wallet(db, user)

    today = date.today().isoformat()
    if wallet.last_checkin_date == today:
        return CheckInResponse(
            success=False,
            earned=0,
            balance=wallet.balance,
            message="今日已签到",
        )

    reward = settings.mtc_daily_checkin
    _credit(db, wallet, reward, "checkin", "每日签到")
    wallet.last_checkin_date = today
    db.commit()

    return CheckInResponse(
        success=True,
        earned=reward,
        balance=wallet.balance,
        message=f"签到成功 +{reward} MTC 球迷积分",
    )


def unlock_report(db: Session, user_id: int, match_id: int, method: str) -> UnlockReportResponse:
    # Check existing unlock
    existing = (
        db.query(UnlockRecord)
        .filter(UnlockRecord.user_id == user_id, UnlockRecord.match_id == match_id)
        .first()
    )
    if existing:
        return UnlockReportResponse(
            success=True,
            method=existing.method,
            balance=None,
            message="已解锁，可直接查看完整报告",
        )

    user = _get_or_create_user(db, user_id)
    wallet = _get_or_create_wallet(db, user)

    if method == "token":
        cost = settings.mtc_report_unlock_cost
        if wallet.balance < cost:
            return UnlockReportResponse(
                success=False,
                method="token",
                balance=wallet.balance,
                message="MTC 球迷积分不足，请先完成任务积累积分",
            )
        _debit(db, wallet, cost, "unlock_report", f"解锁场次 {match_id} AI 完整报告")
        record = UnlockRecord(user_id=user_id, match_id=match_id, method="token", amount_mtc=cost)
        db.add(record)
        db.commit()
        return UnlockReportResponse(
            success=True,
            method="token",
            balance=wallet.balance,
            message=f"已消耗 {cost} MTC 积分，完整 AI 报告已解锁",
        )
    else:
        # cash — in production would verify payment receipt
        record = UnlockRecord(user_id=user_id, match_id=match_id, method="cash", amount_cny=3900)
        db.add(record)
        db.commit()
        return UnlockReportResponse(
            success=True,
            method="cash",
            balance=None,
            message="支付成功，完整 AI 报告已解锁（演示模式）",
        )


def simulate_correction(db: Session, match_id: int) -> SimulateCorrectionResponse:
    """Simulate a 30-minute pre-match lineup correction (demo mode)."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match or not match.prediction:
        raise ValueError(f"Match {match_id} not found or no prediction")

    pred = match.prediction
    # Compute delta: away defender missing → home team gains
    delta = 4.0
    trigger = f"{match.away_team.name_zh}主力中卫未进入首发"
    reason = f"{match.away_team.name_zh}后场出球稳定性下降，{match.home_team.name_zh}右路进攻优势扩大。"

    correction = LiveCorrection(
        match_id=match_id,
        trigger=trigger,
        prob_home_before=pred.prob_home,
        prob_draw_before=pred.prob_draw,
        prob_away_before=pred.prob_away,
        prob_home_after=min(pred.prob_home + delta, 99),
        prob_draw_after=max(pred.prob_draw - 1, 1),
        prob_away_after=max(pred.prob_away - (delta - 1), 1),
        reason=reason,
        is_simulated=True,
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)

    now = datetime.now(timezone.utc)
    return SimulateCorrectionResponse(
        success=True,
        trigger=trigger,
        before={"home": pred.prob_home, "draw": pred.prob_draw, "away": pred.prob_away},
        after={"home": correction.prob_home_after, "draw": correction.prob_draw_after, "away": correction.prob_away_after},
        reason=reason,
        timestamp=now,
    )


def join_challenge(db: Session, challenge_id: int, user_id: int, chosen_option: str) -> JoinChallengeResponse:
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise ValueError(f"Challenge {challenge_id} not found")

    existing = (
        db.query(ChallengeEntry)
        .filter(ChallengeEntry.challenge_id == challenge_id, ChallengeEntry.user_id == user_id)
        .first()
    )
    if existing:
        return JoinChallengeResponse(
            success=False,
            chosen_option=existing.chosen_option,
            message="已参与，等待赛后结算",
        )

    entry = ChallengeEntry(
        challenge_id=challenge_id,
        user_id=user_id,
        chosen_option=chosen_option.upper(),
    )
    db.add(entry)
    db.commit()

    label = challenge.option_a if chosen_option.upper() == "A" else challenge.option_b
    return JoinChallengeResponse(
        success=True,
        chosen_option=chosen_option.upper(),
        message=f"已参与免费预测挑战（选择「{label}」），赛后结算瓜分 MTC 球迷积分奖池",
    )


def subscribe(db: Session, user_id: int, plan: str = "monthly") -> SubscribeResponse:
    existing = (
        db.query(CommunitySubscription)
        .filter(CommunitySubscription.user_id == user_id)
        .first()
    )
    if existing and existing.status == "active":
        return SubscribeResponse(
            success=False,
            plan=existing.plan,
            message="已订阅临场情报社群服务",
        )

    sub = CommunitySubscription(user_id=user_id, plan=plan, status="active")
    db.add(sub)
    db.commit()

    return SubscribeResponse(
        success=True,
        plan=plan,
        message="订阅成功 · 临场推送已开启（AI 数据分析服务 · 非博彩）",
    )
