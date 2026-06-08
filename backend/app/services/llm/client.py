from __future__ import annotations
"""
Real LLM client (DeepSeek / Kimi / Gemini) — draft generation only.

Provider is chosen by an optional `provider` override, else `settings.ai_provider`:
  - 'deepseek' → DeepSeek chat completions  (OpenAI-compatible, api.deepseek.com)
  - 'kimi'     → Moonshot/Kimi chat completions (OpenAI-compatible, api.moonshot.cn)
  - 'gemini'   → Google Generative Language generateContent (generativelanguage.googleapis.com)
  - anything else, or missing key, or any error → returns None (caller falls back
    to a human template).

Never raises to the caller. Never logs secrets. Short timeout; no retries (draft path).
"""
from typing import Optional

from app.config import get_settings

_TIMEOUT_S = 20.0

# OpenAI-compatible providers: (base_url, api_key_attr, model).
_OPENAI_COMPAT = {
    "deepseek": ("https://api.deepseek.com/v1", "deepseek_api_key", "deepseek-chat"),
    "kimi": ("https://api.moonshot.cn/v1", "kimi_api_key", "moonshot-v1-8k"),
}
_GEMINI = ("https://generativelanguage.googleapis.com/v1beta", "gemini_api_key", "gemini-2.5-flash")


def _resolve_provider(settings, provider: Optional[str]) -> str:
    return (provider or settings.ai_provider or "mock").lower()


def active_provider(provider: Optional[str] = None) -> str:
    """Effective provider label for diagnostics (no secrets). 'none' if unavailable."""
    settings = get_settings()
    name = _resolve_provider(settings, provider)
    if name in _OPENAI_COMPAT and getattr(settings, _OPENAI_COMPAT[name][1], ""):
        return name
    if name == "gemini" and getattr(settings, _GEMINI[1], ""):
        return "gemini"
    return "none"


def _generate_openai_compat(base_url: str, api_key: str, model: str, system: str, user: str) -> Optional[str]:
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
    return text.strip() if text and text.strip() else None


def _generate_gemini(base_url: str, api_key: str, model: str, system: str, user: str) -> Optional[str]:
    import httpx

    resp = httpx.post(
        f"{base_url}/models/{model}:generateContent",
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            # thinkingBudget=0 keeps the token budget for the actual copy (2.5-flash is a
            # thinking model; otherwise reasoning eats maxOutputTokens and truncates output).
            "generationConfig": {
                "temperature": 0.6,
                "maxOutputTokens": 600,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        },
        timeout=_TIMEOUT_S,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [{}])
    text = parts[0].get("text")
    return text.strip() if text and text.strip() else None


def generate(system: str, user: str, provider: Optional[str] = None) -> Optional[str]:
    """Call the resolved LLM and return text, or None on any failure/unavailability.

    `provider` (optional): 'deepseek' | 'kimi' | 'gemini'. Falls back to settings.ai_provider.
    """
    settings = get_settings()
    name = _resolve_provider(settings, provider)
    try:
        if name in _OPENAI_COMPAT:
            base_url, key_attr, model = _OPENAI_COMPAT[name]
            api_key = getattr(settings, key_attr, "")
            if not api_key:
                return None
            return _generate_openai_compat(base_url, api_key, model, system, user)
        if name == "gemini":
            base_url, key_attr, model = _GEMINI
            api_key = getattr(settings, key_attr, "")
            if not api_key:
                return None
            return _generate_gemini(base_url, api_key, model, system, user)
        return None
    except Exception:
        # Any network/parse/auth error → fall back to human template.
        return None
