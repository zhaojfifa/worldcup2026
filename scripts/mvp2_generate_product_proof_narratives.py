#!/usr/bin/env python3
"""
MVP-2 product proof narrative generator (LLM-Driven Product Proof sprint).

Engineering builds the stage; the LLM writes the football intelligence. For each of the
three product samples (855737 upset recap, 979139 final recap, 2026_brazil_argentina
pre-match modeling) × zh-CN/vi-VN × provider:
  1. read the ScoutScore v0.2 factor frame (docs/data_audit/mvp2_scoutscore_v0_2/),
  2. assemble the LLM input JSON (factor keys naturalized — no snake_case reaches prose),
  3. call DeepSeek (default, must be real) / Gemini (benchmark) with the v2 product prompt
     (docs/prompts/mvp2_scoutscore_product_narrative_{zh,vi}.md),
  4. write docs/data_audit/mvp2_product_proof_narratives/{id}.{lang}.{provider}.json.

A failed call retries once; only then a MARKED mock fallback (llm_provider="mock") is
written so the page never renders engineering-template intelligence unmarked. Keys come
from backend/.env / env (never printed). The frontend never calls the LLM or the vendor.

Usage: python3 scripts/mvp2_generate_product_proof_narratives.py [deepseek|gemini|both] [sample_id] [zh-CN|vi-VN]
Default: both providers, all three samples, both languages. The retry loop runs the FULL
standalone guard (check_mvp2_product_narrative_guard.check_obj) before accepting output.
"""
import json
import os
import re
import sys
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV = ROOT / "backend" / ".env"
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_scoutscore_v0_2"
OUT = ROOT / "docs" / "data_audit" / "mvp2_product_proof_narratives"
PROMPTS = ROOT / "docs" / "prompts"
HAN = re.compile(r"[一-鿿]")

PRODUCT_NAME = "Giành Cup AI ScoutScore"
SAMPLES = ["855737", "979139", "2026_brazil_argentina"]

# natural factor names sent to the LLM — raw snake_case keys must never reach prose
FACTOR_NAME = {
    "baseline_strength": "Long-run strength (Elo baseline)",
    "recent_form": "Recent form (last 10)",
    "lineup_integrity": "Lineup integrity",
    "finishing_efficiency": "Finishing efficiency",
    "goalkeeper_delta": "Goalkeeper performance gap",
    "event_momentum": "In-match momentum / late swings",
    "tactical_matchup": "Tactical matchup",
    "travel_environment": "Venue / travel / climate",
    "missing_data_risk": "Model blind spots",
    "upset_risk": "Upset / volatility risk",
}
PRODUCT_GOAL = ("Make a fan want to keep reading, subscribe, and join the group: judgement first, "
                "factor-backed, risk-aware — a prediction product, not post-match journalism.")
GROWTH_BRIEF = {
    "free_layer": "main lean + risk level + part of the factor read (this page)",
    "locked_layers": ["full factor breakdown", "live 30-minute pre-kickoff re-score and updated lean",
                      "scoreline band deep-dive", "daily AI view feed"],
    "channels": "Telegram group (active) / Zalo (coming); subscription inside the app",
    "compliance": "data analysis / AI judgement / risk observation / entertainment reference only — never betting language",
}


def load_env_keys():
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


def naturalize(frame):
    """Factor frame -> LLM-safe factor list (natural names, no raw keys)."""
    factors = []
    for f in frame.get("factors", []):
        factors.append({
            "name": FACTOR_NAME.get(f["factor"], f["factor"].replace("_", " ")),
            "value": f.get("value"),
            "pre_match_read": f.get("pre_match_interpretation"),
            "post_match_validation": f.get("post_match_validation"),
            "source_refs": f.get("source_refs", []),
            "assumption": bool(f.get("assumption")),
        })
    return factors


def build_input(sample_id, language):
    frame = json.loads((FRAMES / ("%s.factor_frame.json" % sample_id)).read_text(encoding="utf-8"))
    mode = frame["mode"]
    fx = frame["fixture"]
    kb = frame["kaggle_baseline"]
    inp = {
        "product_name": PRODUCT_NAME,
        "fixture_id": sample_id,
        "mode": mode,
        "language": language,
        "fixture": {"home": fx["home"], "away": fx["away"], "competition": fx.get("competition"),
                    "date": fx.get("date"), "status": "finished" if mode == "historical_recap" else "pre_match"},
        "baseline": {
            "elo_snapshot": kb["elo"],
            "recent_form": {t: {"record": v["record"], "goals_for": v["goals_for"], "goals_against": v["goals_against"],
                                "last_matches": v["matches"][-5:]} for t, v in kb["recent_form"].items()},
            "h2h_last10": kb.get("h2h_last10", []),
        },
        "scoutscore_factors": naturalize(frame),
        "model_frame_outputs": frame["outputs"],
        "live_30min_triggers": frame.get("live_30min_update_trigger"),
        "known_gaps_internal": frame.get("known_gaps", []),
        "product_goal": PRODUCT_GOAL,
        "growth_brief": GROWTH_BRIEF,
    }
    if mode == "historical_recap":
        inp["score"] = {"final": fx.get("final_score"), "winner": fx.get("result_winner"),
                        "shootout_winner": fx.get("shootout_winner")}
        inp["replay_notice"] = "historical replay — NOT a real archived pre-match prediction; say so in internal_notes only"
        if frame.get("shootout_events_note"):
            inp["data_note"] = frame["shootout_events_note"]
    else:
        inp["hypothetical_notice"] = frame.get("hypothetical_note")
        inp["baseline"]["recent_scorers"] = kb.get("recent_scorers")
        inp["baseline"]["shootout_history"] = kb.get("shootout_history")
    return inp


def prompt_body(language):
    name = "mvp2_scoutscore_product_narrative_vi.md" if language == "vi-VN" else "mvp2_scoutscore_product_narrative_zh.md"
    text = (PROMPTS / name).read_text(encoding="utf-8")
    parts = text.split("\n---\n", 1)
    return (parts[1] if len(parts) == 2 else text).strip()


def _extract_json(text):
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
        json={"model": "deepseek-chat",
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
              "temperature": 0.5, "max_tokens": 4500,
              "response_format": {"type": "json_object"}},
        timeout=120.0,
    )
    resp.raise_for_status()
    return (resp.json().get("choices") or [{}])[0].get("message", {}).get("content")


def call_gemini(api_key, system, user):
    import httpx
    resp = httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        params={"key": api_key}, headers={"Content-Type": "application/json"},
        json={"system_instruction": {"parts": [{"text": system}]},
              "contents": [{"role": "user", "parts": [{"text": user}]}],
              "generationConfig": {"temperature": 0.5, "maxOutputTokens": 4600,
                                   "responseMimeType": "application/json",
                                   "thinkingConfig": {"thinkingBudget": 0}}},
        timeout=120.0,
    )
    resp.raise_for_status()
    parts = (((resp.json().get("candidates") or [{}])[0].get("content") or {}).get("parts") or [{}])
    return parts[0].get("text")


def _load_guard():
    """Import the guard script as a module so the retry loop runs the FULL gate."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mvp2_product_guard", ROOT / "scripts" / "check_mvp2_product_narrative_guard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GUARD = _load_guard()


def quick_check(obj):
    """Full guard check on the in-memory object (same gate as the standalone script)."""
    return GUARD.check_obj(obj)


def mock_narrative(sample_id, language, mode):
    """MARKED fallback only — minimal, provider-down placeholder; never the product path."""
    zh = language == "zh-CN"
    t = (lambda a, b: a if zh else b)
    base = {
        "product_name": PRODUCT_NAME, "fixture_id": sample_id, "mode": mode, "language": language,
        "hero_title": t("Giành Cup AI ScoutScore 观点暂不可用", "Quan điểm Giành Cup AI ScoutScore tạm thời chưa có"),
        "hero_subtitle": t("模型叙事服务暂时不可用，稍后再试。", "Dịch vụ tường thuật của mô hình tạm gián đoạn, vui lòng quay lại sau."),
        "short_title": t("AI 观点稍后更新", "Quan điểm AI sẽ cập nhật sau"),
        "screenshot_line": t("AI 观点生成中。", "Quan điểm AI đang được tạo."),
        "model_judgement": t("本场的模型解读正在生成，请稍后查看。", "Phần nhận định của mô hình đang được tạo, vui lòng xem lại sau."),
        "main_lean": t("待更新", "Sẽ cập nhật"),
        "scoreline_view": t("待更新", "Sẽ cập nhật"), "risk_level": t("待更新", "Sẽ cập nhật"),
        "risk_factors": [{"name": t("数据更新中", "Đang cập nhật dữ liệu"), "text": t("稍后查看完整因子。", "Xem bộ yếu tố đầy đủ sau."), "source_refs": [], "assumption_flag": True}],
        "validated_factors": [], "underweighted_factors": [],
        "watch_next_signals": [{"name": t("稍后再来", "Quay lại sau"), "text": t("AI 观点更新后第一时间可看。", "Quan điểm AI sẽ có ngay khi cập nhật."), "source_refs": [], "assumption_flag": True}],
        "operator_copy": t("AI 观点生成中，稍后发布。", "Quan điểm AI đang tạo, sẽ đăng sau."),
        "subscription_hook": t("订阅后第一时间收到 AI 观点更新。", "Đăng ký để nhận quan điểm AI ngay khi cập nhật."),
        "group_join_copy": t("入群第一时间看完整分析。", "Vào nhóm để xem phân tích đầy đủ sớm nhất."),
        "today_cta": t("查看今日 AI 观点", "Xem quan điểm AI hôm nay"),
        "social_post": t("Giành Cup AI 观点稍后更新。", "Quan điểm Giành Cup AI sẽ cập nhật sau."),
        "internal_notes": ["mock fallback — provider unavailable; NOT product content",
                           "historical replay disclosure n/a (mock)" if mode == "historical_recap" else "hypothetical fixture disclosure n/a (mock)"],
        "source_ref_map": {"all": ["mock_fallback"]},
    }
    if mode == "historical_recap":
        base["validated_factors"] = base["underweighted_factors"] = [
            {"name": t("数据更新中", "Đang cập nhật"), "text": t("完整复盘稍后可看。", "Bản phục dựng đầy đủ sẽ có sau."), "source_refs": [], "assumption_flag": True}]
    return base


def generate(provider, sample_id, language, keys):
    system = prompt_body(language)
    inp = build_input(sample_id, language)
    user = ("INPUT (real data + flagged assumptions — never invent beyond it):\n"
            + json.dumps(inp, ensure_ascii=False)
            + "\n\nReturn ONLY the JSON object defined in the contract. No markdown, no prose.")
    obj, used, model = None, "mock", "fallback"
    key = keys.get("DEEPSEEK_API_KEY" if provider == "deepseek" else "GEMINI_API_KEY")
    call = call_deepseek if provider == "deepseek" else call_gemini
    meta = {"product_name": PRODUCT_NAME, "fixture_id": sample_id, "mode": inp["mode"],
            "language": language, "llm_provider": provider,
            "model": "deepseek-chat" if provider == "deepseek" else "gemini-2.5-flash"}
    if key:
        for attempt in (1, 2, 3):
            try:
                cand = _extract_json(call(key, system, user))
            except Exception as e:
                print("  ! %s attempt %d failed (%s)" % (provider, attempt, type(e).__name__))
                cand = None
            else:
                if cand is None:
                    print("  ! %s attempt %d returned unparseable/empty JSON (likely truncation)" % (provider, attempt))
            if cand:
                cand.update(meta)
                probs = quick_check(cand)
                if not probs:
                    obj = cand
                    break
                print("  ! %s attempt %d guard pre-check: %s" % (provider, attempt, "; ".join(probs[:4])))
                if attempt < 3:
                    user += ("\n\nSTRICT RETRY: your previous output failed the gate: " + "; ".join(probs[:6])
                             + ". Fix ALL of these. Every factor entry needs source_refs (copy from INPUT) or "
                               "assumption_flag=true. vi-VN must contain ZERO Han characters. All keys required.")
                else:
                    obj = cand  # keep best-effort; the standalone guard gives the final verdict
    if obj is not None:
        used, model = meta["llm_provider"], meta["model"]
    if obj is None:
        obj = mock_narrative(sample_id, language, inp["mode"])
        used, model = "mock", "fallback"
    obj.update({"product_name": PRODUCT_NAME, "fixture_id": sample_id, "mode": inp["mode"],
                "language": language, "llm_provider": used, "model": model,
                "generated_at": datetime.now(timezone.utc).isoformat()})
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / ("%s.%s.%s.json" % (sample_id, language, provider))
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  saved %s  (llm_provider=%s)" % (path.relative_to(ROOT), used))
    return used


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    lang_only = sys.argv[3] if len(sys.argv) > 3 else None
    providers = ["deepseek", "gemini"] if which == "both" else [which]
    samples = [only] if only else SAMPLES
    langs = [lang_only] if lang_only else ["zh-CN", "vi-VN"]
    keys = load_env_keys()
    print("providers=%s samples=%s langs=%s  keys: deepseek=%s gemini=%s" % (
        providers, samples, langs,
        "set" if keys.get("DEEPSEEK_API_KEY") else "MISSING",
        "set" if keys.get("GEMINI_API_KEY") else "MISSING"))
    for sid in samples:
        for p in providers:
            print("[%s %s]" % (sid, p))
            for lang in langs:
                generate(p, sid, lang, keys)


if __name__ == "__main__":
    main()
