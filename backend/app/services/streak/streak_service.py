from __future__ import annotations
"""
Streak / challenge settlement service.

MTC platform points ONLY — no cash, no cash pool, no withdrawal/transfer/trade.
Rankings are participation / streak / points boards, never earnings boards.
"""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    UserStreak, ChallengeResult, Challenge, ChallengeEntry, User,
)
from app.services.token import wallet_service
from app.schemas.streak import (
    StreakOut, RankingsOut, RankingUser, SettleChallengeResponse,
)

# MTC reward rules (platform points only)
REWARD_CORRECT = 10
BONUS_STREAK_3 = 20
BONUS_STREAK_7 = 80


def calculate_mtc_reward(new_streak: int) -> int:
    reward = REWARD_CORRECT
    if new_streak == 3:
        reward += BONUS_STREAK_3
    if new_streak == 7:
        reward += BONUS_STREAK_7
    return reward


def _get_or_create_streak(db: Session, user_id: int) -> UserStreak:
    s = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    if not s:
        s = UserStreak(user_id=user_id, current_streak=0, best_streak=0, mtc_earned=0)
        db.add(s)
        db.flush()
    return s


def get_user_streak(db: Session, user_id: int) -> StreakOut:
    """Empty-safe: returns zeros if the user has no streak row yet."""
    s = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    if not s:
        return StreakOut(user_id=user_id, current_streak=0, best_streak=0,
                         mtc_earned=0, last_participation_date=None)
    return StreakOut(
        user_id=user_id,
        current_streak=s.current_streak,
        best_streak=s.best_streak,
        mtc_earned=s.mtc_earned,
        last_participation_date=s.last_participation_date,
    )


def settle_challenge_result(
    db: Session,
    challenge_id: int,
    user_id: int,
    actual_result: str,
    match_id: Optional[int] = None,
    selected_option: Optional[str] = None,
) -> SettleChallengeResponse:
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        return SettleChallengeResponse(ok=False, is_correct=None, mtc_reward=0,
                                       current_streak=0, best_streak=0,
                                       message="challenge not found")

    # Determine the user's pick: explicit override, else their join entry.
    if selected_option is None:
        entry = (
            db.query(ChallengeEntry)
            .filter(ChallengeEntry.challenge_id == challenge_id, ChallengeEntry.user_id == user_id)
            .first()
        )
        selected_option = entry.chosen_option if entry else None

    streak = _get_or_create_streak(db, user_id)
    normalized_actual = actual_result.strip()
    is_neutral = normalized_actual.lower() in ("neutral", "unresolved", "")

    if is_neutral:
        is_correct: Optional[bool] = None
    elif selected_option is None:
        # No participation → cannot score; record neutral, no streak change.
        is_correct = None
    else:
        is_correct = selected_option.upper() == normalized_actual.upper()

    # Idempotency: a challenge already settled for this user does not re-apply
    # streak/MTC effects (prevents double-counting on repeat calls).
    cr = (
        db.query(ChallengeResult)
        .filter(ChallengeResult.challenge_id == challenge_id, ChallengeResult.user_id == user_id)
        .first()
    )
    if cr is not None and cr.settled_at is not None:
        return SettleChallengeResponse(
            ok=True, is_correct=cr.is_correct, mtc_reward=0,
            current_streak=streak.current_streak, best_streak=streak.best_streak,
            message="该挑战已结算，未重复计入连胜或积分",
        )

    now = datetime.now(timezone.utc)
    if not cr:
        cr = ChallengeResult(challenge_id=challenge_id, user_id=user_id)
        db.add(cr)
    cr.match_id = match_id or challenge.match_id
    cr.selected_option = selected_option
    cr.actual_result = normalized_actual
    cr.is_correct = is_correct
    cr.settled_at = now

    mtc_reward = 0
    if is_correct is True:
        streak.current_streak += 1
        streak.best_streak = max(streak.best_streak, streak.current_streak)
        mtc_reward = calculate_mtc_reward(streak.current_streak)
        streak.mtc_earned += mtc_reward
        # Credit platform points via the wallet (auditable in TokenLog)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            wallet = wallet_service._get_or_create_wallet(db, user)
            wallet_service._credit(db, wallet, mtc_reward, "challenge_reward",
                                   f"连胜挑战命中 +{mtc_reward} MTC")
    elif is_correct is False:
        streak.current_streak = 0  # reset on miss
    # neutral → unchanged

    streak.last_participation_date = date.today().isoformat()
    db.commit()

    if is_correct is None:
        msg = "中性/未结算，连胜不变"
    elif is_correct:
        msg = f"命中！连胜 {streak.current_streak}，获得 {mtc_reward} MTC 平台积分"
    else:
        msg = "未命中，连胜已重置"

    return SettleChallengeResponse(
        ok=True, is_correct=is_correct, mtc_reward=mtc_reward,
        current_streak=streak.current_streak, best_streak=streak.best_streak,
        message=msg,
    )


def get_rankings(db: Session, limit: int = 20) -> RankingsOut:
    """Streak/points board. Empty-safe; no fabricated users."""
    rows = (
        db.query(UserStreak)
        .order_by(
            UserStreak.current_streak.desc(),
            UserStreak.best_streak.desc(),
            UserStreak.mtc_earned.desc(),
        )
        .limit(limit)
        .all()
    )
    top_users = []
    updated = None
    for i, s in enumerate(rows, start=1):
        user = db.query(User).filter(User.id == s.user_id).first()
        display = (user.nickname if user and user.nickname else f"球迷 {s.user_id:03d}")
        top_users.append(RankingUser(
            rank=i, display_name=display,
            current_streak=s.current_streak, best_streak=s.best_streak,
            mtc_earned=s.mtc_earned,
        ))
        if s.updated_at and (updated is None or s.updated_at > updated):
            updated = s.updated_at

    return RankingsOut(top_users=top_users, ranking_type="streak", updated_at=updated)
