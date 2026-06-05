"""
Seed script — populates DB with demo data matching frontend mock.ts.
Run from backend/ directory:
    python scripts/seed.py

Creates:
  - 3 teams × 3 matches
  - Predictions, Reports for each match
  - 1 Challenge per match
  - Demo user (id=1) with a token wallet (balance=520)
"""
import sys
import os

# Allow running from scripts/ or backend/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone, timedelta
from app.database import SessionLocal, init_db
from app.models import (
    Team, Match, Prediction, Report,
    User, TokenWallet, TokenLog,
)
from app.models.challenge import Challenge

# ─────────────────────────────────────────────
TEAMS = [
    dict(name="Brazil",   name_zh="巴西",   country="Brazil",   flag_emoji="🇧🇷", api_id=6),
    dict(name="Argentina",name_zh="阿根廷",  country="Argentina",flag_emoji="🇦🇷", api_id=26),
    dict(name="Morocco",  name_zh="摩洛哥",  country="Morocco",  flag_emoji="🇲🇦", api_id=31),
    dict(name="France",   name_zh="法国",    country="France",   flag_emoji="🇫🇷", api_id=2),
    dict(name="Spain",    name_zh="西班牙",  country="Spain",    flag_emoji="🇪🇸", api_id=9),
    dict(name="Germany",  name_zh="德国",    country="Germany",  flag_emoji="🇩🇪", api_id=25),
]

MATCHES = [
    dict(
        external_id="BRA-ARG-20260605",
        home_name="Brazil", away_name="Argentina",
        kickoff="2026-06-05T07:00:00+00:00",
        tag="focus",
        prediction=dict(
            prob_home=45, prob_draw=27, prob_away=28,
            recommended_score="2:1 / 1:1",
            risk_level="medium", confidence=62,
            free_note="AI 当前更倾向巴西，但这不是低风险比赛。巴西优势在中场控制和右路推进，阿根廷风险来自后卫线伤停。不过阿根廷反击效率较高，因此平局概率也不可忽视。",
            risk_note="巴西近期中场控制力增强；阿根廷后卫线主力伤停，防线稳定性下降。",
        ),
        report=dict(
            features=[
                {"label": "中场控制力",       "value": 18},
                {"label": "近 5 场 xG 表现", "value": 12},
                {"label": "阿根廷后卫伤停",   "value": 10},
                {"label": "巴西右路突破",     "value": 8},
                {"label": "体能与旅行因素",   "value": -3},
            ],
            trend_history=[
                {"label": "赛前 3 天", "prob": 42},
                {"label": "赛前 1 天", "prob": 45},
                {"label": "临场 30 分", "prob": 49},
            ],
            tactics_note=(
                "巴西本场优势主要来自中场控制和右路推进。如果阿根廷主力中卫无法首发，"
                "巴西右路更容易形成传中和二次进攻。但阿根廷反击效率仍然很高，"
                "因此 AI 并不把本场标记为低风险。"
            ),
            verdict_summary="巴西小幅占优，但不是稳胆。",
        ),
        challenge=dict(
            question="本场是否会出现红牌？",
            option_a="会", option_b="不会", prize_pool=500,
        ),
    ),
    dict(
        external_id="MAR-FRA-20260606",
        home_name="Morocco", away_name="France",
        kickoff="2026-06-06T20:00:00+00:00",
        tag="upset",
        prediction=dict(
            prob_home=38, prob_draw=29, prob_away=33,
            recommended_score="1:1 / 0:1",
            risk_level="high", confidence=51,
            free_note="AI 当前轻微看好法国，但摩洛哥的爆冷能力不容小觑。",
            risk_note="摩洛哥主场优势显著，爆冷可能性不可忽视。",
        ),
        report=dict(
            features=[
                {"label": "主场氛围加成",    "value": 14},
                {"label": "法国控球率",      "value": 9},
                {"label": "摩洛哥防线紧凑度","value": 8},
                {"label": "法国前锋状态",    "value": -5},
            ],
            trend_history=[
                {"label": "赛前 3 天", "prob": 35},
                {"label": "赛前 1 天", "prob": 33},
                {"label": "临场 30 分", "prob": 33},
            ],
            tactics_note=(
                "摩洛哥依靠密集防守与快速反击，法国需要突破其低位防线。"
                "若法国前锋状态未能回升，平局或摩洛哥逆转的概率上升。"
            ),
            verdict_summary="法国小幅占优但风险较高，摩洛哥爆冷概率值得关注。",
        ),
        challenge=dict(
            question="摩洛哥能否在本场攻入进球？",
            option_a="能", option_b="不能", prize_pool=300,
        ),
    ),
    dict(
        external_id="ESP-GER-20260607",
        home_name="Spain", away_name="Germany",
        kickoff="2026-06-07T03:00:00+00:00",
        tag="live",
        prediction=dict(
            prob_home=41, prob_draw=30, prob_away=29,
            recommended_score="1:0 / 2:1",
            risk_level="medium", confidence=57,
            free_note="西班牙略占优，但德国的定位球能力让本场充满变数。",
            risk_note="双方实力接近，临场首发阵容影响显著。",
        ),
        report=dict(
            features=[
                {"label": "控球与传导",     "value": 16},
                {"label": "德国定位球",     "value": 7},
                {"label": "西班牙锋线效率", "value": 6},
                {"label": "德国中场疲劳度", "value": -4},
            ],
            trend_history=[
                {"label": "赛前 3 天", "prob": 39},
                {"label": "赛前 1 天", "prob": 41},
                {"label": "临场 30 分", "prob": 41},
            ],
            tactics_note=(
                "西班牙控球压制节奏，德国依赖定位球和快速反击。"
                "若西班牙中场保持高位压迫，得分窗口将集中在上半场。"
            ),
            verdict_summary="西班牙控球优势明显，但德国定位球是变数。",
        ),
        challenge=dict(
            question="本场是否会有加时赛或点球大战？",
            option_a="是", option_b="否", prize_pool=400,
        ),
    ),
]


DEFAULT_CHANNELS = [
    dict(channel_name="zalo",     display_name="Zalo",     status="coming_soon",
         description="越南球迷主阵地", locale="vi", sort_order=1),
    dict(channel_name="telegram", display_name="Telegram", status="coming_soon",
         description="临场情报推送", locale="vi", sort_order=2),
    dict(channel_name="facebook", display_name="Facebook", status="coming_soon",
         description="赛事讨论与长图复盘", locale="vi", sort_order=3),
    dict(channel_name="tiktok",   display_name="TikTok",   status="coming_soon",
         description="每日 AI 三场速览", locale="vi", sort_order=4),
]


def seed_social_channels(db):
    """Idempotent: insert default channels if missing. Real links NOT set here."""
    from app.models import SocialChannel
    added = 0
    for ch in DEFAULT_CHANNELS:
        exists = db.query(SocialChannel).filter(SocialChannel.channel_name == ch["channel_name"]).first()
        if not exists:
            db.add(SocialChannel(is_enabled=True, **ch))
            added += 1
    db.commit()
    print(f"   social channels: {added} inserted, {len(DEFAULT_CHANNELS) - added} already present")


def run():
    init_db()
    db = SessionLocal()

    try:
        # Social channels are idempotent and seeded regardless of prior seeding.
        seed_social_channels(db)

        # Skip the rest if already seeded
        if db.query(Team).count() > 0:
            print("DB already seeded (teams present) — skipping demo data.")
            return

        # Teams
        team_map: dict[str, Team] = {}
        for t in TEAMS:
            team = Team(**t)
            db.add(team)
            team_map[t["name"]] = team
        db.flush()

        # Demo user + wallet
        demo_user = User(id=1, device_id="demo-device-001", nickname="Demo Fan")
        db.add(demo_user)
        db.flush()

        wallet = TokenWallet(user_id=demo_user.id, balance=520, total_earned=520)
        db.add(wallet)
        db.flush()

        # Log initial grant
        log = TokenLog(
            user_id=demo_user.id,
            wallet_id=wallet.id,
            amount=520,
            balance_after=520,
            event_type="admin",
            note="新用户初始赠送 MTC 球迷积分",
        )
        db.add(log)

        # Matches + Predictions + Reports + Challenges
        for m_data in MATCHES:
            home_team = team_map[m_data["home_name"]]
            away_team = team_map[m_data["away_name"]]
            kickoff = datetime.fromisoformat(m_data["kickoff"])

            match = Match(
                external_id=m_data["external_id"],
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                kickoff_time=kickoff,
                tag=m_data["tag"],
                stage="Group Stage",
                status="scheduled",
            )
            db.add(match)
            db.flush()

            p = m_data["prediction"]
            pred = Prediction(
                match_id=match.id,
                prob_home=p["prob_home"],
                prob_draw=p["prob_draw"],
                prob_away=p["prob_away"],
                recommended_score=p["recommended_score"],
                risk_level=p["risk_level"],
                confidence=p["confidence"],
                free_note=p["free_note"],
                risk_note=p["risk_note"],
                model_version="mock-v1",
                ai_provider="mock",
            )
            db.add(pred)

            r = m_data["report"]
            report = Report(
                match_id=match.id,
                features=r["features"],
                trend_history=r["trend_history"],
                tactics_note=r["tactics_note"],
                verdict_summary=r["verdict_summary"],
            )
            db.add(report)

            c = m_data["challenge"]
            challenge = Challenge(
                match_id=match.id,
                question=c["question"],
                option_a=c["option_a"],
                option_b=c["option_b"],
                prize_pool=c["prize_pool"],
                status="open",
            )
            db.add(challenge)

        db.commit()
        print("✅ Seed complete:")
        print(f"   {len(TEAMS)} teams")
        print(f"   {len(MATCHES)} matches with predictions, reports, challenges")
        print(f"   1 demo user (id=1) with 520 MTC balance")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
