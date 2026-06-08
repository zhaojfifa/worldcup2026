from __future__ import annotations
"""
Draft copy generation service (draft-only; never auto-publishes).

Flow: fetch match → build context → try real LLM → on failure use a human template
→ run the forbidden-phrase filter → return a draft payload with warnings + hits.

No DB writes. No publishing. Status is always 'draft_only'.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.match import Match
from app.services import match_service
from app.services.llm import client, compliance, prompts

VALID_LANGS = {"vi", "mm", "zh", "en"}
VALID_TYPES = {"preview", "upset", "live", "recap"}

_DISCLAIMER = {
    "vi": "Kết quả trong quá khứ không đảm bảo kết quả tương lai. Chỉ phân tích dữ liệu & giải trí.",
    "mm": "အတိတ်ရလဒ်က အနာဂတ်ကို အာမမခံပါ။ ဒေတာ ခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဖျော်ဖြေရေးအတွက်သာ။",
    "zh": "历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。",
    "en": "Past performance does not guarantee future results. For data analysis & entertainment only.",
}


def _localized_team_names(db: Session, match_id: int, language: str) -> Optional[tuple[str, str]]:
    """Locale-appropriate team names: zh → Chinese (name_zh), vi/mm/en → English (name).

    The MatchDetail/TeamOut only carries the Chinese display name, so vi/mm/en drafts would
    otherwise embed Chinese team names (e.g. "巴西" instead of "Brazil"). Read the raw teams.
    """
    m = db.get(Match, match_id)
    if m is None or m.home_team is None or m.away_team is None:
        return None
    if language == "zh":
        return (m.home_team.name_zh, m.away_team.name_zh)
    return (m.home_team.name, m.away_team.name)


def _ctx_from_match(detail) -> dict:
    settings = get_settings()
    return {
        "home": detail.home_team.name,
        "away": detail.away_team.name,
        "win_prob": {"home": detail.win_prob.home, "draw": detail.win_prob.draw, "away": detail.win_prob.away},
        "confidence": round(detail.confidence),
        "risk_level": detail.risk_level,
        "risk_note": detail.risk_note or "",
        "recommended_score": detail.recommended_score or "",
        # Mirror /data-source/status: mock_mode == (ai_provider == "mock").
        "data_mode": "mock" if (settings.ai_provider or "mock").lower() == "mock" else "real",
    }


def _human_template(copy_type: str, language: str, ctx: dict) -> str:
    """Compliant fallback copy when the LLM is unavailable. Short, AI-viewpoint framing."""
    home, away = ctx["home"], ctx["away"]
    wp = ctx["win_prob"]
    disc = _DISCLAIMER.get(language, _DISCLAIMER["en"])
    lead = "home" if wp["home"] >= wp["away"] else "away"
    lead_team = home if lead == "home" else away
    pct = wp["home"] if lead == "home" else wp["away"]

    if language == "vi":
        head = {
            "preview": f"⚽ {home} vs {away} — Xu hướng AI: {lead_team} nhỉnh ({pct}%).",
            "upset": f"⚠️ Rủi ro bất ngờ: {home} vs {away} — mức rủi ro {ctx['risk_level']}, cần theo dõi đội hình.",
            "live": f"📡 Cập nhật sát giờ · {home} vs {away}: AI tính lại theo đội hình.",
            "recap": f"📊 Nhìn lại {home} vs {away}: so sánh nhận định AI với kết quả thực tế.",
        }.get(copy_type, "")
        return f"{head}\nĐây là góc nhìn dữ liệu AI, không phải cam kết kết quả.\n{disc}"
    if language == "mm":
        head = {
            "preview": f"⚽ {home} vs {away} — AI အမြင်: {lead_team} သာ ({pct}%)။",
            "upset": f"⚠️ အံ့အားသင့်နိုင်ခြေ: {home} vs {away} — အန္တရာယ် {ctx['risk_level']}၊ လူစာရင်း စောင့်ကြည့်ပါ။",
            "live": f"📡 ပွဲချိန် update · {home} vs {away}: AI က လူစာရင်းအရ ပြန်တွက်သည်။",
            "recap": f"📊 {home} vs {away} ပြန်သုံးသပ်: AI သုံးသပ်ချက်နှင့် တကယ့်ရလဒ် နှိုင်းယှဉ်။",
        }.get(copy_type, "")
        return f"{head}\nဤသည် AI ဒေတာအမြင်ဖြစ်ပြီး ရလဒ် အာမခံချက် မဟုတ်ပါ။\n{disc}"
    if language == "zh":
        head = {
            "preview": f"⚽ {home} vs {away} — AI 倾向：{lead_team}略占优（{pct}%）。",
            "upset": f"⚠️ 爆冷风险：{home} vs {away} — 风险等级 {ctx['risk_level']}，关注临场首发。",
            "live": f"📡 临场更新 · {home} vs {away}：AI 根据首发重新计算。",
            "recap": f"📊 赛后复盘：{home} vs {away}，对比 AI 观点与实际结果。",
        }.get(copy_type, "")
        return f"{head}\n这是 AI 数据观点，并非结果承诺。\n{disc}"
    head = {
        "preview": f"⚽ {home} vs {away} — AI view: {lead_team} edge ({pct}%).",
        "upset": f"⚠️ Upset risk: {home} vs {away} — {ctx['risk_level']} risk; watch the lineup.",
        "live": f"📡 Live update · {home} vs {away}: AI recalculated on the lineup.",
        "recap": f"📊 Recap: {home} vs {away} — AI read vs the actual result.",
    }.get(copy_type, "")
    return f"{head}\nThis is an AI data viewpoint, not a result promise.\n{disc}"


def generate_copy(db: Session, match_id: int, language: str, copy_type: str) -> dict:
    language = (language or "").lower()
    copy_type = (copy_type or "").lower()
    if language not in VALID_LANGS:
        return {"error": f"unsupported language '{language}'", "status": "rejected"}
    if copy_type not in VALID_TYPES:
        return {"error": f"unsupported copy_type '{copy_type}'", "status": "rejected"}

    detail = match_service.get_match_detail(db, match_id)
    if detail is None:
        return {"error": f"match {match_id} not found", "status": "rejected"}

    ctx = _ctx_from_match(detail)
    # Use locale-appropriate team names (vi/mm/en → English, zh → Chinese) so drafts are
    # not polluted with Chinese team names on non-zh customer copy.
    names = _localized_team_names(db, match_id, language)
    if names is not None:
        ctx["home"], ctx["away"] = names
    warnings: list[str] = []

    system, user = prompts.build_prompt(copy_type, language, ctx)
    text = client.generate(system, user)
    if text:
        provenance = f"llm:{client.active_provider()}"
    else:
        text = _human_template(copy_type, language, ctx)
        provenance = "human_template_fallback"
        warnings.append("LLM unavailable or returned empty; used human template fallback.")

    forbidden_hits = compliance.scan(text, language)
    if forbidden_hits:
        warnings.append("Forbidden phrases detected — must be revised before publish.")
    if ctx["data_mode"] == "mock":
        warnings.append("data_mode=mock: do not present as real accuracy / hit-rate.")

    return {
        "match_id": match_id,
        "language": language,
        "copy_type": copy_type,
        "generated_text": text,
        "provenance": provenance,
        "data_mode": ctx["data_mode"],
        "warnings": warnings,
        "forbidden_hits": forbidden_hits,
        "disclaimer": _DISCLAIMER.get(language, _DISCLAIMER["en"]),
        "status": "draft_only",
        "publishable": False,
    }
