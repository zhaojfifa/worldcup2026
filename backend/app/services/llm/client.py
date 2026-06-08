from __future__ import annotations
"""
Real LLM client (DeepSeek / Kimi) — draft generation only.

Dispatch on settings.ai_provider:
  - 'deepseek' → DeepSeek chat completions (api.deepseek.com)
  - 'kimi'     → Moonshot/Kimi chat completions (api.moonshot.cn)
  - anything else, or missing key, or any error → returns None (caller falls back
    to a human template).

Never raises to the caller. Never logs secrets. Short timeout; no retries (draft path).
"""
from typing import Optional

from app.config import get_settings

_TIMEOUT_S = 20.0


def _provider_conf(settings) -> Optional[tuple[str, str, str]]:
    """Return (base_url, api_key, model) for the active provider, or None."""
    provider = (settings.ai_provider or "mock").lower()
    if provider == "deepseek" and settings.deepseek_api_key:
        return ("https://api.deepseek.com/v1", settings.deepseek_api_key, "deepseek-chat")
    if provider == "kimi" and settings.kimi_api_key:
        return ("https://api.moonshot.cn/v1", settings.kimi_api_key, "moonshot-v1-8k")
    return None


def active_provider() -> str:
    """Human-readable provider label for diagnostics (no secrets)."""
    settings = get_settings()
    conf = _provider_conf(settings)
    if not conf:
        return "none"
    return (settings.ai_provider or "mock").lower()


def generate(system: str, user: str) -> Optional[str]:
    """Call the configured LLM and return text, or None on any failure/unavailability."""
    settings = get_settings()
    conf = _provider_conf(settings)
    if not conf:
        return None
    base_url, api_key, model = conf
    try:
        import httpx  # lazy import; keeps cold paths light

        resp = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.6,
                "max_tokens": 400,
            },
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        data = resp.json()
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content")
        if text and text.strip():
            return text.strip()
        return None
    except Exception:
        # Any network/parse/auth error → fall back to human template.
        return None
