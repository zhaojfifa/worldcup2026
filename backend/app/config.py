from __future__ import annotations
"""
Application configuration — loaded from environment variables / .env file.
Never import secrets directly; always use settings.xxx.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",          # repo root .env
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_env: str = "development"
    app_name: str = "worldcup2026"
    app_base_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    # Database
    database_url: str = "sqlite:///./worldcup2026.db"

    # API-FOOTBALL (only ever read here; never forwarded to frontend)
    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_key: str = ""

    # AI Provider
    ai_provider: str = "mock"
    deepseek_api_key: str = ""
    kimi_api_key: str = ""
    gemini_api_key: str = ""

    # Cloudflare R2 (pre-configured, not used in Day 3)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "worldcup2026"
    r2_public_base_url: str = ""

    # Token rules
    mtc_daily_checkin: int = 10
    mtc_share_reward: int = 50
    mtc_invite_reward: int = 100
    mtc_report_unlock_cost: int = 390
    mtc_community_trial_cost: int = 1500

    # Compliance flags — MUST remain false in production
    enable_real_money_betting: bool = False
    enable_token_withdrawal: bool = False

    # CORS origins (comma-separated)
    cors_origins: str = "http://localhost:5173,https://worldcup2026-izid.onrender.com"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
