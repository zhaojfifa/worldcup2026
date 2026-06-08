from __future__ import annotations
"""
Prompt templates for draft copy generation. Pure string builders — no I/O.

Languages: vi (Vietnamese), mm (Burmese), zh (internal), en (fallback).
copy_type: preview | upset | live | recap.

Hard rules embedded in the system prompt: AI-viewpoint framing only, no betting,
no guaranteed result, no profit/cash, no hit-rate claims, MTC = platform points.
"""

_LANG_NAME = {"vi": "Vietnamese", "mm": "Burmese (Myanmar)", "zh": "Chinese", "en": "English"}

_SYSTEM = (
    "You are a football data-intelligence copywriter for Giành Cup, a World Cup AI "
    "football intelligence community. Write SHORT, mobile-friendly {lang} copy.\n"
    "STRICT RULES:\n"
    "- Frame everything as 'AI data viewpoint / tendency / risk signal', never a guarantee.\n"
    "- NEVER use betting, gambling, 'sure win', 'guaranteed', profit, cash-prize, or hit-rate wording.\n"
    "- NEVER promise results or returns. MTC is platform loyalty points only (not withdrawable).\n"
    "- Keep team names in English; numbers/percentages as given.\n"
    "- Respond ONLY in {lang}. Do NOT use Chinese characters unless {lang} is Chinese. "
    "Do NOT mix languages or add labels in another language.\n"
    "- End with a one-line disclaimer that past performance does not guarantee future results.\n"
    "- Output ONLY the copy text, no preamble."
)

_TASK = {
    "preview": "Write a pre-match brief: AI tendency, confidence (as stars or words), one-line reason, a short risk note.",
    "upset": "Write an upset-risk note: why this match could surprise, what to watch, keep it punchy.",
    "live": "Write a live (T-30min) update: lineup trigger, win-probability shift before→after, why the AI recalculated.",
    "recap": "Write a post-match recap: AI's original read vs the actual result, whether it matched, error source, next adjustment. (Only meaningful when a real result exists.)",
}


def build_prompt(copy_type: str, language: str, ctx: dict) -> tuple[str, str]:
    lang = _LANG_NAME.get(language, "English")
    system = _SYSTEM.format(lang=lang)
    task = _TASK.get(copy_type, _TASK["preview"])
    wp = ctx.get("win_prob", {})
    user = (
        f"Task: {task}\n"
        f"Match: {ctx.get('home')} vs {ctx.get('away')}\n"
        f"Win probability: home {wp.get('home')}% / draw {wp.get('draw')}% / away {wp.get('away')}%\n"
        f"Confidence: {ctx.get('confidence')} (0-100)\n"
        f"Risk level: {ctx.get('risk_level')}\n"
        f"Risk note (source): {ctx.get('risk_note')}\n"
        f"Recommended score: {ctx.get('recommended_score')}\n"
        f"Data mode: {ctx.get('data_mode')} (if 'mock', do NOT imply real accuracy)\n"
        f"Write in {lang}. Short. Compliant."
    )
    return system, user
