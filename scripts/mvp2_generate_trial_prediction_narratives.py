#!/usr/bin/env python3
"""
MVP-2 June 11 trial — persona narrative generator (Task D).

For each trial fixture × zh/vi × provider: reads the trial prediction frame
(docs/data_audit/mvp2_trial_prediction_frames/), assembles the persona LLM input
(中文先知 / Tiên Tri Bóng Đá; engine = ScoutScore; brand = LEIZE / Giành Cup; no Cloud),
calls DeepSeek (default candidate) / Gemini (benchmark) with the v2 product prompt +
June-11 trial addendum, gates with the FULL guard in the retry loop, and writes
docs/data_audit/mvp2_trial_prediction_narratives/{id}.{lang}.{provider}.json.

Adds the trial-only required field `tactical_read` and stamps
product_surface=trial_prediction / fixture_basis=real_scheduled. If a provider fails
after retries, the failure is recorded (marked mock fallback) — never silent.

Usage: python3 scripts/mvp2_generate_trial_prediction_narratives.py [deepseek|gemini|both] [fixture_id] [lang]
Default: both providers × {1489369, 1489371} × {zh-CN, vi-VN}.
"""
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"
OUT = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_narratives"
SAMPLES = ["1489369", "1489371"]

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

GEN = _load("ppgen", ROOT / "scripts" / "mvp2_generate_product_proof_narratives.py")
GUARD = GEN.GUARD

PERSONA = {"zh-CN": "俅哥（俅哥说球）", "vi-VN": "Tiên Tri Bóng Đá"}
FACTOR_NAME = {
    "baseline_strength": "Long-run strength (Elo baseline)", "recent_form": "Recent form (last 10)",
    "h2h": "Head-to-head", "goal_trend": "Goal trend (last 5 vs prev 5)",
    "defensive_trend": "Defensive trend + clean sheets", "squad_stability": "Squad stability",
    "goalkeeper_risk": "Goalkeeper risk", "striker_finishing_risk": "Striker dependence / finishing",
    "travel_venue_context": "Venue / altitude / context", "lineup_uncertainty": "Lineup uncertainty",
    "injury_gap": "Injury news gap", "live_30min_trigger": "30-minute pre-kickoff re-score",
}


def build_input(sample_id, language):
    fr = json.loads((FRAMES / ("%s.json" % sample_id)).read_text(encoding="utf-8"))
    factors = []
    for f in fr["factors"]:
        factors.append({
            "name": FACTOR_NAME.get(f["factor"], f["factor"].replace("_", " ")),
            "value": f.get("value"),
            "status": f.get("data_status"),
            "customer_visible": f.get("customer_visible"),
            "note_internal": f.get("internal_note"),
            "source_refs": f.get("source_refs", []),
            "assumption": f.get("data_status") in ("assumption", "missing", "partial"),
        })
    out = fr["scoutscore_output"]
    return {
        "product_name": "Giành Cup AI ScoutScore",
        "trial_persona": PERSONA[language],
        "brand_rules": {
            "company": "LEIZE DIGITAL TECHNOLOGY COMPANY LIMITED / CÔNG TY TNHH CÔNG NGHỆ SỐ LEIZE (legal only, not headlines)",
            "use_only": ["LEIZE", "LEIZE AI", "Giành Cup", PERSONA[language], "ScoutScore (engine)"],
            "never": ["Cloud", "generic 'AI 分析' voice", "we-lack-data phrasing"],
        },
        "fixture_id": sample_id,
        "mode": "pre_match_2026_modeling",
        "product_surface": "trial_prediction",
        "fixture_basis": "real_scheduled",
        "language": language,
        "fixture": fr["fixture"],
        "team_baseline": fr["team_baseline"],
        "scoutscore_factors": factors,
        "model_frame_outputs": out,
        "what_could_flip": out["what_could_flip"],
        "recheck_30min": out["recheck_30min"],
        "real_fixture_notice": (
            "REAL scheduled World Cup 2026 fixture (kickoff/venue/round real). Trial send-to-group "
            "pre-match judgement. Lineups NOT announced: internal_notes must say so; expected shapes "
            "only as assumption_flag entries; never invent injuries. Speak AS the persona."),
        "extra_required_field": {"tactical_read": "tactical card: both sides' expected approach, key duels, tempo — persona voice, assumption-flagged expectations"},
        "product_goal": "An operator can screenshot this and send it to a fan group before kickoff: direction for free, live 30-min re-score in the group.",
        "growth_brief": {
            "free_layer": "main lean + risk level + part of the read (this page)",
            "locked_layers": ["full factor breakdown", "live 30-minute re-score after XI announced", "scoreline band deep-dive", "daily view feed"],
            "link_policy": "NEVER write a URL; if a join entry is needed in copy, the operator appends it",
        },
    }


REQUIRED_EXTRA = ["tactical_read"]


def generate(provider, sample_id, language, keys):
    system = GEN.prompt_body(language)
    inp = build_input(sample_id, language)
    user = ("INPUT (real data + flagged assumptions — never invent beyond it):\n"
            + json.dumps(inp, ensure_ascii=False)
            + "\n\nReturn ONLY the contract JSON object, plus the REQUIRED extra key \"tactical_read\". "
              "No markdown, no prose.")
    meta = {"product_name": "Giành Cup AI ScoutScore", "fixture_id": sample_id,
            "mode": "pre_match_2026_modeling", "language": language,
            "product_surface": "trial_prediction", "fixture_basis": "real_scheduled",
            "llm_provider": provider,
            "model": "deepseek-chat" if provider == "deepseek" else "gemini-2.5-flash"}
    key = keys.get("DEEPSEEK_API_KEY" if provider == "deepseek" else "GEMINI_API_KEY")
    call = GEN.call_deepseek if provider == "deepseek" else GEN.call_gemini
    obj = None
    if key:
        for attempt in (1, 2, 3):
            try:
                cand = GEN._extract_json(call(key, system, user))
            except Exception as e:
                print("  ! %s attempt %d failed (%s)" % (provider, attempt, type(e).__name__))
                cand = None
            else:
                if cand is None:
                    print("  ! %s attempt %d unparseable/empty (likely truncation)" % (provider, attempt))
            if cand:
                cand.update(meta)
                probs = GUARD.check_obj(cand)
                probs += ["missing field: %s" % k for k in REQUIRED_EXTRA if not str(cand.get(k, "")).strip()]
                probs += ["%s must be a plain string" % k for k in REQUIRED_EXTRA if cand.get(k) is not None and not isinstance(cand.get(k), str)]
                if not probs:
                    obj = cand
                    break
                print("  ! %s attempt %d guard pre-check: %s" % (provider, attempt, "; ".join(probs[:4])))
                if attempt < 3:
                    user += ("\n\nSTRICT RETRY: previous output failed: " + "; ".join(probs[:6])
                             + ". Fix ALL. tactical_read required. Persona (%s) must appear in hero/judgement. "
                               "Every factor entry: source_refs from INPUT or assumption_flag=true. "
                               "vi-VN: ZERO Han characters. ABSOLUTE vi vocabulary ban (betting slang): "
                               "kèo, cửa trên, cửa dưới, nhà cái, chắc thắng — write 'bên được đánh giá cao "
                               "hơn/thấp hơn' instead; never any form of 'kèo'. Data gaps: write 'đội hình "
                               "chưa công bố' / 'biến số cần canh sát giờ', never 'thiếu dữ liệu'."
                               % PERSONA[language])
                else:
                    obj = cand
    used, model = (meta["llm_provider"], meta["model"]) if obj is not None else ("mock", "fallback")
    if obj is None:
        obj = GEN.mock_narrative(sample_id, language, "pre_match_2026_modeling")
        obj["tactical_read"] = obj["model_judgement"]
        print("  !! %s FAILED after retries -> MARKED mock fallback recorded" % provider)
    obj.update(meta)
    obj.update({"llm_provider": used, "model": model,
                "generated_at": datetime.now(timezone.utc).isoformat()})
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / ("%s.%s.%s.json" % (sample_id, language, provider))
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  saved %s  (llm_provider=%s)" % (path.relative_to(ROOT), used))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    lang_only = sys.argv[3] if len(sys.argv) > 3 else None
    providers = ["deepseek", "gemini"] if which == "both" else [which]
    samples = [only] if only else SAMPLES
    langs = [lang_only] if lang_only else ["zh-CN", "vi-VN"]
    keys = GEN.load_env_keys()
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
