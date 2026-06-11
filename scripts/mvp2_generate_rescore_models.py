#!/usr/bin/env python3
"""
MVP-2 30-Min ReScore model layer v1 (QiuGe sprint, Task C).

Engineering builds the skeleton (trigger topics + current status from the fixture
verification, decision-rule logic from the trial frame outputs); the LLM (persona:
zh 俅哥/俅哥说球 · vi Tiên Tri Bóng Đá) writes ALL customer/operator language:
why_it_matters / possible_impact / free_copy / subscriber_copy per trigger, localized
decision rules, public_teaser, group_join_hook, reminder_message.

Output contract (per fixture × lang):
{ fixture_id, pre_match_lean, pre_match_risk_level, score_range_before,
  rescore_triggers:[{key,name,current_status,why_it_matters,possible_impact,free_copy,subscriber_copy}],
  rescore_decision_rules:[{condition,change_to_lean,change_to_risk,change_to_score_range,operator_note}],
  public_teaser, group_join_hook, reminder_message, llm_provider, ... }

Inline guard: required structure (6 trigger topics, >=3 rules), forbidden/tone/URL scans
(reuses check_mvp2_product_narrative_guard lists), persona presence, vi Han=0.
Writes docs/data_audit/mvp2_rescore_models/{id}.{lang}.{provider}.json.

Usage: python3 scripts/mvp2_generate_rescore_models.py [deepseek|gemini] [fixture_id] [lang]
Default: deepseek × {1489369,1489371} × {zh-CN,vi-VN}.
"""
import importlib.util
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"
VERIF = ROOT / "docs" / "data_audit" / "mvp2_june11_real_fixture_verification.json"
OUT = ROOT / "docs" / "data_audit" / "mvp2_rescore_models"
HAN = re.compile(r"[一-鿿]")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _load("ppgen", ROOT / "scripts" / "mvp2_generate_product_proof_narratives.py")
GUARD = GEN.GUARD
PERSONA = {"zh-CN": "俅哥（俅哥说球）", "vi-VN": "Tiên Tri Bóng Đá"}
TRIGGER_KEYS = ["starting_xi", "goalkeeper", "frontline_availability", "formation",
                "late_injury_suspension", "weather_altitude_stadium"]


def skeleton(fid):
    fr = json.loads((FRAMES / ("%s.json" % fid)).read_text(encoding="utf-8"))
    ver = {r["fixture_id"]: r for r in json.loads(VERIF.read_text(encoding="utf-8"))["verified_candidates"]}.get(int(fid), {})
    o = fr["scoutscore_output"]
    fav = o["primary_lean"]["side"]
    home, away = fr["fixture"]["match"].split(" vs ")
    dog = away if fav == home else home
    lineups = bool(ver.get("lineups_available"))
    return {
        "fixture": fr["fixture"],
        "pre_match_lean": o["primary_lean"],
        "pre_match_risk_level": o["risk_level"],
        "score_range_before": o["score_range"],
        "team_baseline": fr["team_baseline"],
        "trigger_topics": [
            {"key": "starting_xi", "current_status": "announced" if lineups else "not announced yet (re-check ~60-30min before kickoff)",
             "engineering_basis": "squads registered (26); XI unknown -> spine continuity is the single biggest re-score input"},
            {"key": "goalkeeper", "current_status": "starter unknown (GK names known from squads)",
             "engineering_basis": "GK identity/form gap was a decisive blind spot in the 855737 upset case"},
            {"key": "frontline_availability", "current_status": "unknown until XI",
             "engineering_basis": "underdog top-scorer dependence is high -> their presence shifts upset exposure"},
            {"key": "formation", "current_status": "unknown until lineups (coaches confirmed)",
             "engineering_basis": "low-block vs possession collision changes the scoreline band shape"},
            {"key": "late_injury_suspension", "current_status": "no new pre-match signal ingested (0 results — treated as a blind spot, not as 'no injuries')",
             "engineering_basis": "any late name on the list re-weights lineup integrity instantly"},
            {"key": "weather_altitude_stadium", "current_status": "venue/kickoff real; conditions are scenario context" + (" (Estadio Azteca altitude ~2200m)" if fid == "1489369" else " (US summer evening)"),
             "engineering_basis": "altitude/heat degrade pressing intensity late -> affects favourite's tempo plan"},
        ],
        "rule_logic": [
            {"condition_logic": "%s XI missing 2+ spine starters (CB/GK/striker)" % fav,
             "lean": "weaken toward draw", "risk": "raise one band", "range": "tighten toward 1-1 / low-scoring"},
            {"condition_logic": "%s confirms first-choice XI incl. striker spine" % fav,
             "lean": "keep / strengthen %s" % fav, "risk": "hold", "range": "hold (favourite end of band)"},
            {"condition_logic": "%s starting GK is the in-form first choice + back five unchanged" % dog,
             "lean": "hold but flag upset path", "risk": "raise underdog-hold scenario", "range": "shift weight to 1-0/0-0/1-1 tails"},
            {"condition_logic": "late injury/suspension touches either frontline",
             "lean": "re-run required", "risk": "raise", "range": "re-issue band"},
        ],
        "fixture_id": fid,
    }


def build_user(sk, language):
    persona = PERSONA[language]
    return (
        "You write the 30-Min ReScore product layer for the persona '%s' (engine: ScoutScore; brand Giành Cup; "
        "zh persona brand = 俅哥说球). INPUT skeleton (real statuses + rule logic — never invent beyond it):\n" % persona
        + json.dumps(sk, ensure_ascii=False)
        + "\n\nReturn ONLY one JSON object:\n"
          '{"fixture_id":"' + sk["fixture_id"] + '","pre_match_lean":"<one line, persona voice>",'
          '"pre_match_risk_level":"<short>","score_range_before":"<persona reference band: zh 俅哥给出的赛前参考区间… / vi khoảng tham khảo trước trận của Tiên Tri…>",'
          '"rescore_triggers":[{"key":"<copy from trigger_topics>","name":"<customer name>","current_status":"<customer phrasing of status>",'
          '"why_it_matters":"","possible_impact":"","free_copy":"<1 line, free layer>","subscriber_copy":"<1-2 lines, group layer, concrete>"}],'
          '"rescore_decision_rules":[{"condition":"","change_to_lean":"","change_to_risk":"","change_to_score_range":"","operator_note":"<internal-ish but clean>"}],'
          '"public_teaser":"<1 line for the hot-reads entry>","group_join_hook":"<why join tonight>",'
          '"reminder_message":"<the 30-min reminder message an operator pastes in the group when XI drops>"}\n'
          "Rules: cover ALL 6 trigger keys in order; >=3 decision rules from rule_logic; persona voice (%s must appear in "
          "public_teaser or pre_match_lean); language %s%s; NO URLs; no betting words (kèo/cửa trên/cửa dưới/盘口/赔率...); NEVER the words 模型/mô hình/ScoutScore/AI in copy — speak ONLY as the persona; "
          "no 'we lack data' phrasing (use 赛前盲区/临场待确认/cần xác nhận trước giờ bóng lăn); gaps are product features, "
          "not apologies. JSON only." % (persona.split("（")[0], language,
                                          " — ZERO Han characters" if language == "vi-VN" else "")
    )


def check(obj, language):
    errs = []
    for k in ("fixture_id", "pre_match_lean", "pre_match_risk_level", "score_range_before",
              "rescore_triggers", "rescore_decision_rules", "public_teaser", "group_join_hook", "reminder_message"):
        if not obj.get(k):
            errs.append("missing/empty: %s" % k)
    trigs = obj.get("rescore_triggers") or []
    keys = [t.get("key") for t in trigs if isinstance(t, dict)]
    for k in TRIGGER_KEYS:
        if k not in keys:
            errs.append("trigger topic missing: %s" % k)
    for i, t in enumerate(trigs):
        for f in ("name", "current_status", "why_it_matters", "possible_impact", "free_copy", "subscriber_copy"):
            if not str(t.get(f, "")).strip():
                errs.append("trigger[%d].%s empty" % (i, f))
    rules = obj.get("rescore_decision_rules") or []
    if len(rules) < 3:
        errs.append("need >=3 decision rules")
    for i, r in enumerate(rules):
        for f in ("condition", "change_to_lean", "change_to_risk", "change_to_score_range", "operator_note"):
            if not str(r.get(f, "")).strip():
                errs.append("rule[%d].%s empty" % (i, f))
    blob = GUARD.walk_strings({k: v for k, v in obj.items() if k not in ("fixture_id",)})
    bl = blob.lower()
    for term in ("模型", "mô hình", "scoutscore", "deepseek", "gemini", "llm", "pipeline", "schema"):
        if term in bl:
            errs.append("de-model violation: %r" % term)
    for term in GUARD.FORBIDDEN + GUARD.FAKE_PROB + GUARD.TONE_BANS:
        if term.lower() in bl:
            errs.append("forbidden/tone wording: %r" % term)
    if re.search(r"https?://|t\.me/|www\.", blob):
        errs.append("URL in copy")
    if language == "vi-VN":
        if HAN.search(blob):
            errs.append("vi Han chars present")
        if "Tiên Tri" not in blob:
            errs.append("vi persona missing")
    else:
        if "俅哥" not in blob:
            errs.append("zh persona 俅哥 missing")
    return errs


def generate(provider, fid, language, keys):
    sk = skeleton(fid)
    user = build_user(sk, language)
    system = GEN.prompt_body(language)
    call = GEN.call_deepseek if provider == "deepseek" else GEN.call_gemini
    key = keys.get("DEEPSEEK_API_KEY" if provider == "deepseek" else "GEMINI_API_KEY")
    obj = None
    if key:
        for attempt in (1, 2, 3):
            try:
                cand = GEN._extract_json(call(key, system, user))
            except Exception as e:
                print("  ! %s attempt %d failed (%s)" % (provider, attempt, type(e).__name__))
                cand = None
            if cand:
                probs = check(cand, language)
                if not probs:
                    obj = cand
                    break
                print("  ! attempt %d: %s" % (attempt, "; ".join(probs[:4])))
                if attempt < 3:
                    user += ("\n\nSTRICT RETRY — fix ALL: " + "; ".join(probs[:8])
                             + ". ABSOLUTE vi ban: kèo / cửa trên / cửa dưới / nhà cái — write "
                               "'bên được đánh giá cao hơn/thấp hơn' instead. NEVER 模型/mô hình/AI.")
                else:
                    obj = cand
    if obj is None:
        print("  !! %s FAILED -> not writing a mock rescore (page falls back to narrative watch list)" % provider)
        return
    final = check(obj, language)
    obj.update({"fixture_id": fid, "language": language,
                "voice": "qiuge_v2" if language == "zh-CN" else "tientri_v2", "llm_provider": provider,
                "model": "deepseek-chat" if provider == "deepseek" else "gemini-2.5-flash",
                "product_surface": "trial_rescore", "guard_clean": not final,
                "generated_at": datetime.now(timezone.utc).isoformat()})
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / ("%s.%s.%s.json" % (fid, language, provider))
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  saved %s (guard_clean=%s)" % (p.relative_to(ROOT), not final))


def main():
    provider = sys.argv[1] if len(sys.argv) > 1 else "deepseek"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    lang_only = sys.argv[3] if len(sys.argv) > 3 else None
    keys = GEN.load_env_keys()
    for fid in ([only] if only else ["1489369", "1489371"]):
        print("[%s %s]" % (fid, provider))
        for lang in ([lang_only] if lang_only else ["zh-CN", "vi-VN"]):
            generate(provider, fid, lang, keys)


if __name__ == "__main__":
    main()
