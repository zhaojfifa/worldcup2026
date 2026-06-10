#!/usr/bin/env python3
"""
MVP-2 LLM-guided ScoutScore narrative generator (internal QA helper, NOT the build).

Engineering builds the stage; the LLM writes the football intelligence. This script:
  1. reads REAL 855737 artifacts (ScoutScore factors + accountability evidence/gaps/source_refs),
  2. assembles the LLM input JSON per docs/MVP2_LLM_NARRATIVE_CONTRACT.md,
  3. calls DeepSeek (and Gemini if a key is present) with the prompt in docs/prompts/,
  4. writes the narrative JSON to docs/data_audit/mvp2_llm_narratives/.

If a provider key is missing or the call fails, it writes a MARKED mock fallback
(`llm_provider: "mock"`) so the page still has something to render — but mock is a
fallback only, never the default. Never prints the API key. Frontend never calls the
LLM or the vendor; this runs server/dev-side only.

Usage: python3 scripts/mvp2_generate_scoutscore_narrative.py [deepseek|gemini|both]
Default: both (prefers DeepSeek; Gemini is the benchmark).
"""
import json
import os
import re
import sys
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV = ROOT / "backend" / ".env"
OUT = ROOT / "docs" / "data_audit" / "mvp2_llm_narratives"
PROMPTS = ROOT / "docs" / "prompts"
FACTORS = ROOT / "docs" / "data_audit" / "mvp2_scoutscore_v0" / "855737.factor_scores.json"
ACCT = ROOT / "docs" / "data_audit" / "mvp2_prediction_accountability_reports" / "855737.zh-CN.json"

FIXTURE_ID = "855737"
PRODUCT_NAME = "Giành Cup AI ScoutScore"
PRODUCT_GOAL = "帮助用户理解模型怎么看、哪些风险被验证、下一场该看什么"

# role hint per factor key (the LLM still decides the narrative; this only labels inputs)
ROLE_HINT = {
    "efficiency": "decisive", "event_momentum": "decisive",
    "match_control": "verified_not_predictive", "team_strength": "overweighted",
    "lineup_formation": "context", "recent_form": "missing", "missing_risk": "missing",
}
# Natural names sent to the LLM instead of snake_case keys, so there is no code
# identifier to echo into customer prose (the guard rejects raw factor keys).
FACTOR_NAME = {
    "efficiency": "Finishing efficiency", "event_momentum": "Second-half momentum / turning point",
    "match_control": "Match control (possession)", "team_strength": "Paper strength / reputation",
    "lineup_formation": "Lineup / formation", "recent_form": "Recent form", "missing_risk": "Missing-data risk",
}
AVAIL = {"missing": "not ingested", "replay_only": "observed in this match only", "observed": "observed"}


def load_env_keys():
    """Parse backend/.env for provider keys (never printed). Real env overrides file."""
    keys = {}
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            keys[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("DEEPSEEK_API_KEY", "GEMINI_API_KEY"):
        if os.environ.get(k):
            keys[k] = os.environ[k]
    return keys


def build_input(language):
    """Assemble the language-neutral LLM input JSON from real artifacts."""
    factors = json.loads(FACTORS.read_text(encoding="utf-8"))
    acct = json.loads(ACCT.read_text(encoding="utf-8"))
    ar = factors.get("actual_result", {})
    score = {
        "home": ar.get("home"), "away": ar.get("away"),
        "result": ar.get("score"), "winner_side": ar.get("winner_side"),
    }
    scoutscore_factors = []
    for f in factors.get("factors", []):
        key = f.get("factor")
        scoutscore_factors.append({
            "name": FACTOR_NAME.get(key, key),   # natural name only — no snake_case keys
            "role": ROLE_HINT.get(key, "context"),
            "pre_match_interpretation": f.get("interpretation_pre_match"),
            "post_match_validation": f.get("post_match_validation"),
            "availability": AVAIL.get(f.get("data_status"), f.get("data_status")),
            "assumption": bool(f.get("assumption")),
            "source_refs": f.get("source_refs", []),
        })
    evidence_cards = []
    for e in acct.get("key_evidence", []):
        refs = e.get("source_refs", [])
        metric = refs[0].get("metric") if refs else e.get("title")
        evidence_cards.append({
            "metric": metric, "value": e.get("value"),
            "endpoint": refs[0].get("endpoint") if refs else None,
        })
    return {
        "fixture_id": FIXTURE_ID,
        "product_name": PRODUCT_NAME,
        "language": language,
        "mode": "historical_recap_product_validation",
        "fixture": {"home": ar.get("home"), "away": ar.get("away"), "status": "finished"},
        "score": score,
        "teams": {"home": ar.get("home"), "away": ar.get("away")},
        "scoutscore_factors": scoutscore_factors,
        "evidence_cards": evidence_cards,
        "source_refs": acct.get("source_refs", []),
        "known_missing_or_unverified": [
            "injuries: 0 results (source required, unresolved)",
            "xG: not ingested this round",
            "recent_form / Elo: not ingested",
        ],
        "product_goal": PRODUCT_GOAL,
    }


def prompt_body(language):
    """Use the prompt .md body (after the leading meta blockquote / first '---')."""
    name = "mvp2_scoutscore_narrative_vi.md" if language == "vi-VN" else "mvp2_scoutscore_narrative_zh.md"
    text = (PROMPTS / name).read_text(encoding="utf-8")
    parts = text.split("\n---\n", 1)
    return (parts[1] if len(parts) == 2 else text).strip()


def _extract_json(text):
    """Strip code fences / prose and parse the first JSON object."""
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"\{.*\}", t, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
    return None


def call_deepseek(api_key, system, user):
    import httpx
    resp = httpx.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.5, "max_tokens": 1600,
            "response_format": {"type": "json_object"},
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json()
    return (data.get("choices") or [{}])[0].get("message", {}).get("content")


def call_gemini(api_key, system, user):
    import httpx
    resp = httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        params={"key": api_key}, headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": 0.5, "maxOutputTokens": 1800,
                "responseMimeType": "application/json",
                "thinkingConfig": {"thinkingBudget": 0},
            },
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [{}])
    return parts[0].get("text")


def mock_narrative(language):
    """Marked fallback ONLY (llm_provider=mock). Concise, product-voice, source-backed."""
    if language == "vi-VN":
        return {
            "hero_title": "Cú sốc này không ngẫu nhiên: AI cần nhắm ba yếu tố rủi ro trước trận",
            "hero_subtitle": "Argentina mạnh hơn trên giấy, nhưng thủ môn, hiệu suất dứt điểm và động lượng hiệp hai đã viết lại kết quả.",
            "model_judgement": "Giành Cup AI xem Argentina nhỉnh hơn dựa trên sức mạnh trên giấy, nhưng cảnh báo rủi ro bất ngờ không thấp; kết quả cho thấy thế trận không tự chuyển thành chiến thắng.",
            "validated_signals": [
                {"name": "Kiểm soát thế trận", "text": "Argentina kiểm soát bóng 69% đúng như kỳ vọng, nhưng không thành kết quả.", "source_refs": [{"field": "team_statistics", "endpoint": "/fixtures/statistics"}], "assumption_flag": False}
            ],
            "underweighted_signals": [
                {"name": "Hiệu suất dứt điểm", "text": "Saudi Arabia 2 cú trúng đích thành 2 bàn; Argentina 15 sút chỉ 1 bàn.", "source_refs": [{"field": "team_statistics", "endpoint": "/fixtures/statistics"}], "assumption_flag": False},
                {"name": "Thủ môn", "text": "Thủ môn Saudi Arabia 7.7, cứu thua 5; Argentina 6.0, cứu thua 0.", "source_refs": [{"field": "player_statistics", "endpoint": "/fixtures/players"}], "assumption_flag": False},
                {"name": "Động lượng hiệp hai", "text": "Hai bàn phút 48 và 53 lật ngược thế cờ.", "source_refs": [{"field": "events_summary", "endpoint": "/fixtures/events"}], "assumption_flag": False}
            ],
            "customer_takeaway": "Ở trận chênh lệch rõ ràng tiếp theo, hãy nhắm thủ môn, hiệu suất dứt điểm, động lượng hiệp hai và mức đầy đủ đội hình trước trận.",
            "operator_copy": "Đội mạnh kiểm soát bóng chưa chắc đã thắng: Argentina kiểm soát nhiều hơn nhưng Saudi Arabia thay đổi trận đấu bằng thủ môn, hiệu suất và màn lội ngược dòng. AI đưa các yếu tố này vào phán đoán trước trận lần sau.",
            "cta_copy": "Xem quan điểm AI hôm nay",
            "internal_notes": ["historical_replay: not a real pre-match archived prediction", "accountability: MISS (model leaned Argentina)", "missing_evidence: injuries 0 results / xG not ingested"],
            "source_ref_map": {"hero": ["/fixtures/statistics", "/fixtures/players", "/fixtures/events"]},
        }
    return {
        "hero_title": "这场爆冷不是偶然：AI 赛前应重点盯住三个风险因子",
        "hero_subtitle": "Argentina 纸面实力更强，但 Saudi Arabia 用门将表现、射门效率和下半场动量改写结果。",
        "model_judgement": "Giành Cup AI 基于纸面强弱看好 Argentina，但提示冷门风险不低；结果说明控场本身不会自动变成胜利。",
        "validated_signals": [
            {"name": "控场", "text": "Argentina 控球 69% 如预期兑现，但没有转化为结果。", "source_refs": [{"field": "team_statistics", "endpoint": "/fixtures/statistics"}], "assumption_flag": False}
        ],
        "underweighted_signals": [
            {"name": "射门效率", "text": "Saudi Arabia 2 次射正全部进球，Argentina 15 射仅 1 球。", "source_refs": [{"field": "team_statistics", "endpoint": "/fixtures/statistics"}], "assumption_flag": False},
            {"name": "门将表现", "text": "Saudi Arabia 门将 7.7、扑救 5 次；Argentina 门将 6.0、0 扑救。", "source_refs": [{"field": "player_statistics", "endpoint": "/fixtures/players"}], "assumption_flag": False},
            {"name": "下半场动量", "text": "48′、53′ 连入两球完成反超。", "source_refs": [{"field": "events_summary", "endpoint": "/fixtures/events"}], "assumption_flag": False}
        ],
        "customer_takeaway": "下一场强弱分明的比赛，重点盯门将、射门效率、下半场动量和赛前首发完整性。",
        "operator_copy": "强队控球不等于一定能赢：Argentina 控球占优，但 Saudi Arabia 靠门将、效率和下半场反超改变比赛。AI 把这些风险因子沉淀到下一次赛前判断里。",
        "cta_copy": "查看今日 AI 观点",
        "internal_notes": ["historical_replay: 非真实赛前存档预测", "accountability: MISS（模型倾向 Argentina）", "missing_evidence: injuries 0 / xG 未接入"],
        "source_ref_map": {"hero": ["/fixtures/statistics", "/fixtures/players", "/fixtures/events"]},
    }


def generate(provider, language, keys):
    system = prompt_body(language)
    inp = build_input(language)
    user = "INPUT (real data — do not invent beyond it):\n" + json.dumps(inp, ensure_ascii=False) + \
           "\n\nReturn ONLY the JSON object defined in the contract. No markdown, no prose."
    obj, used, model = None, "mock", "fallback"
    try:
        if provider == "deepseek" and keys.get("DEEPSEEK_API_KEY"):
            obj = _extract_json(call_deepseek(keys["DEEPSEEK_API_KEY"], system, user))
            if obj:
                used, model = "deepseek", "deepseek-chat"
        elif provider == "gemini" and keys.get("GEMINI_API_KEY"):
            obj = _extract_json(call_gemini(keys["GEMINI_API_KEY"], system, user))
            if obj:
                used, model = "gemini", "gemini-2.5-flash"
    except Exception as e:
        print("  ! %s call failed (%s) -> mock fallback" % (provider, type(e).__name__))
    if not obj:
        obj = mock_narrative(language)
    obj["llm_provider"] = used
    obj["model"] = model
    obj["language"] = language
    obj["generated_at"] = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / ("%s.%s.%s.json" % (FIXTURE_ID, language, provider))
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  saved %s  (llm_provider=%s, model=%s)" % (path.relative_to(ROOT), used, model))
    return used


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    providers = ["deepseek", "gemini"] if which == "both" else [which]
    keys = load_env_keys()
    print("providers=%s  keys: deepseek=%s gemini=%s" % (
        providers, "set" if keys.get("DEEPSEEK_API_KEY") else "MISSING",
        "set" if keys.get("GEMINI_API_KEY") else "MISSING"))
    for p in providers:
        print("[%s]" % p)
        for lang in ("zh-CN", "vi-VN"):
            generate(p, lang, keys)


if __name__ == "__main__":
    main()
