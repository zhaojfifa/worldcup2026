#!/usr/bin/env python3
"""
MVP-2 product narrative guard — gate before a product proof narrative reaches a page.

Checks docs/data_audit/mvp2_product_proof_narratives/*.json against the v2 product
contract (docs/MVP2_LLM_NARRATIVE_CONTRACT.md + Owner guard list):
  - all required fields; factor entries = {name, text} + source_refs OR assumption_flag
  - product name (Giành Cup / ScoutScore) present in the hero block
  - model_judgement + risk_factors + watch_next_signals non-empty
  - historical_recap: validated_factors + underweighted_factors non-empty
  - pre_match_2026_modeling: main_lean + risk_level + scoreline_view non-empty, scoreline
    carries a model-estimate marker, internal_notes disclose the hypothetical fixture
  - subscription_hook or group_join_copy present (we require the fields, ≥1 non-empty)
  - operator_copy: short, not a research report, distinct from model_judgement
  - no journalism-only hero (score-only title), no generic post-match / AI-filler tone
  - no betting/odds wording (zh/vi/en incl. kèo/nhà cái), no guarantee words
  - no fake probability terms (real match stats like possession % are allowed)
  - no engineering/audit tokens or raw factor keys in customer prose
  - vi-VN: ZERO Han characters anywhere
Exit 0 = all PASS. Usage:
  python3 scripts/check_mvp2_product_narrative_guard.py [file ...]
"""
import json
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
NARR_DIR = ROOT / "docs" / "data_audit" / "mvp2_product_proof_narratives"
HAN = re.compile(r"[一-鿿]")

TEXT_FIELDS = ["hero_title", "hero_subtitle", "short_title", "screenshot_line", "model_judgement",
               "main_lean", "scoreline_view", "risk_level", "operator_copy", "subscription_hook",
               "group_join_copy", "today_cta", "social_post"]
FACTOR_LISTS = ["risk_factors", "validated_factors", "underweighted_factors", "watch_next_signals"]
REQUIRED = ["product_name", "fixture_id", "mode", "language", "llm_provider",
            "internal_notes", "source_ref_map"] + TEXT_FIELDS + FACTOR_LISTS

FORBIDDEN = [
    # betting / gambling (zh)
    "下注", "投注", "赔率", "盘口", "竞猜", "串关", "购彩", "博彩", "彩票", "庄家",
    "稳赚", "稳赢", "必中", "必赢", "包赢", "跟单", "回报率", "返奖", "收益承诺", "现金奖池",
    # vi
    "cá cược", "đặt cược", "kèo", "nhà cái", "soi kèo", "chắc thắng", "bao thắng", "ăn chắc",
    # en
    "betting", "odds", "wager", "bookmaker", "parlay", "guaranteed win", "sure win",
]
FAKE_PROB = ["命中率", "胜率", "中奖率", "win rate", "win probability", "tỷ lệ thắng", "tỷ lệ trúng", "xác suất thắng"]
AUDIT_TOKENS = [
    "MISS", "source required", "source_required", "historical replay", "历史回放", "phát lại lịch sử",
    "assumption", "replay_only", "data_status", "missing_evidence", "source_refs", "assumption_flag",
    "scoutscore_factors", "baseline_strength", "recent_form", "lineup_integrity", "finishing_efficiency",
    "goalkeeper_delta", "event_momentum", "tactical_matchup", "travel_environment", "missing_data_risk",
    "upset_risk", "model_estimate", "kaggle", "factor_frame", "hypothetical_fixture", "snake_case",
]
# generic post-match / AI-filler tone (Owner: no journalism tone, no AI flavour)
TONE_BANS = ["一场精彩", "精彩的比赛", "精彩对决", "综上所述", "总而言之", "值得注意的是", "总体而言",
             "不难发现", "让我们拭目以待", "nhìn chung", "tóm lại", "đáng chú ý là", "có thể thấy rằng"]
RESEARCH_TONE = ["研究报告", "本报告", "本文", "审计", "白皮书", "báo cáo nghiên cứu", "this report"]


def has_model_estimate_marker(text):
    """scoreline_view must read as a model estimate: an estimate word AND a model/product subject."""
    t = str(text).lower()
    est = any(m in t for m in ("估计", "预估", "ước tính", "estimate"))
    subj = any(m in t for m in ("模型", "mô hình", "scoutscore", "giành cup ai", "model"))
    return est and subj


def _factor_text(sig):
    if not isinstance(sig, dict):
        return str(sig)
    return " ".join(str(sig.get(k, "")) for k in ("name", "text"))


def walk_strings(v):
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return " ".join(walk_strings(x) for x in v)
    if isinstance(v, dict):
        return " ".join(walk_strings(x) for x in v.values())
    return ""


def check(path):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return ["invalid JSON: %s" % e]
    return check_obj(obj, path.name)


def check_obj(obj, filename=""):
    """Full guard on a narrative dict (also imported by the generator's retry loop)."""
    errs = []
    mode = obj.get("mode", "")
    is_recap = mode == "historical_recap"
    is_pre = mode == "pre_match_2026_modeling"
    is_vi = obj.get("language") == "vi-VN" or ".vi-VN." in filename

    # 1. required fields
    for f in REQUIRED:
        if f not in obj:
            errs.append("missing field: %s" % f)
    if mode not in ("historical_recap", "pre_match_2026_modeling"):
        errs.append("mode must be historical_recap | pre_match_2026_modeling (got %r)" % mode)
    if not isinstance(obj.get("internal_notes"), list) or not obj.get("internal_notes"):
        errs.append("internal_notes must be a non-empty list")
    if not isinstance(obj.get("source_ref_map"), dict) or not obj.get("source_ref_map"):
        errs.append("source_ref_map must be a non-empty object")

    # 2. product name in the hero block
    hero_blob = " ".join(str(obj.get(k, "")) for k in ("hero_title", "hero_subtitle", "model_judgement"))
    if "Giành Cup" not in hero_blob and "ScoutScore" not in hero_blob:
        errs.append("product name (Giành Cup / ScoutScore) missing from hero block")

    # 3. core judgement fields
    for k in ("model_judgement", "main_lean"):
        if not str(obj.get(k, "")).strip():
            errs.append("%s must be non-empty" % k)
    if not obj.get("risk_factors"):
        errs.append("risk_factors must be non-empty")
    if not obj.get("watch_next_signals"):
        errs.append("watch_next_signals must be non-empty")

    # 4. mode-specific requirements
    if is_recap:
        for k in ("validated_factors", "underweighted_factors"):
            if not obj.get(k):
                errs.append("historical_recap requires non-empty %s" % k)
        notes = walk_strings(obj.get("internal_notes", [])).lower()
        if "replay" not in notes and "archived" not in notes and "phục dựng" not in notes and "回放" not in walk_strings(obj.get("internal_notes", [])):
            errs.append("internal_notes must disclose the historical-replay nature")
    if is_pre:
        for k in ("risk_level", "scoreline_view"):
            if not str(obj.get(k, "")).strip():
                errs.append("pre_match requires non-empty %s" % k)
        sv = str(obj.get("scoreline_view", ""))
        if sv and not has_model_estimate_marker(sv):
            errs.append("scoreline_view must carry a model-estimate marker (e.g. 模型估计 / mô hình ước tính)")
        notes_blob = walk_strings(obj.get("internal_notes", [])).lower()
        if "hypothetical" not in notes_blob and "giả định" not in notes_blob and "假想" not in walk_strings(obj.get("internal_notes", [])):
            errs.append("internal_notes must disclose the hypothetical 2026 fixture")

    # 5. CTA presence
    if not str(obj.get("subscription_hook", "")).strip() and not str(obj.get("group_join_copy", "")).strip():
        errs.append("need subscription_hook or group_join_copy (both empty)")

    # 6. factor list shapes + provenance
    for lst in FACTOR_LISTS:
        items = obj.get(lst)
        if items is None:
            continue
        if not isinstance(items, list):
            errs.append("%s must be a list" % lst)
            continue
        if lst == "risk_factors" and not items:
            continue  # already reported
        for i, sig in enumerate(items):
            if not isinstance(sig, dict):
                errs.append("%s[%d] not an object" % (lst, i)); continue
            if "name" not in sig or "text" not in sig:
                errs.append("%s[%d] must have 'name' and 'text'" % (lst, i))
            refs = sig.get("source_refs")
            has_refs = isinstance(refs, list) and len(refs) > 0
            if not has_refs and not sig.get("assumption_flag"):
                errs.append("%s[%d] needs source_refs OR assumption_flag=true" % (lst, i))

    # 7. journalism-only hero (a bare scoreline headline)
    title = str(obj.get("hero_title", "")).strip()
    if re.fullmatch(r"[\w .À-ỹÀ-ɏ-]+\d\s*[-–:]\s*\d[\w .À-ỹÀ-ɏ-]+", title):
        errs.append("hero_title is a bare scoreline (journalism-only title)")

    # 8. operator_copy: not a research report, not a clone of the judgement
    op = str(obj.get("operator_copy", ""))
    if len(op) > 600:
        errs.append("operator_copy too long (%d chars) — reads like a report" % len(op))
    if op and op == str(obj.get("model_judgement", "")):
        errs.append("operator_copy must not duplicate model_judgement")

    # 9. customer prose scans
    prose = [str(obj.get(f, "")) for f in TEXT_FIELDS]
    for lst in FACTOR_LISTS:
        for sig in (obj.get(lst) or []):
            prose.append(_factor_text(sig))
    blob = "\n".join(prose)
    blob_l = blob.lower()
    for term in FORBIDDEN:
        if term.lower() in blob_l:
            errs.append("forbidden wording in customer prose: %r" % term)
    for term in FAKE_PROB:
        if term.lower() in blob_l:
            errs.append("fake-probability wording in customer prose: %r" % term)
    for term in AUDIT_TOKENS:
        if term == "MISS":
            if re.search(r"\bMISS\b", blob):
                errs.append("audit token in customer prose: 'MISS'")
        elif term.lower() in blob_l:
            errs.append("audit/engineering token in customer prose: %r" % term)
    for term in TONE_BANS:
        if term.lower() in blob_l:
            errs.append("generic/AI-filler tone in customer prose: %r" % term)
    for term in RESEARCH_TONE:
        if term.lower() in blob_l:
            errs.append("research-report tone in customer prose: %r" % term)
    # links are engineering stage (real CTA buttons) — the LLM must never invent one
    if re.search(r"https?://|t\.me/|www\.", blob):
        errs.append("URL in customer prose (links are injected by the page, never written by the LLM)")

    # 10. vi Han = 0 (whole file)
    if is_vi:
        han = HAN.findall(walk_strings(obj))
        if han:
            errs.append("vi-VN has %d Han char(s): %s" % (len(han), "".join(han[:30])))

    return errs


def main():
    files = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(NARR_DIR.glob("*.json"))
    if not files:
        print("no narrative files found in %s" % NARR_DIR); sys.exit(2)
    any_fail = False
    for p in files:
        errs = check(p)
        if errs:
            any_fail = True
            print("FAIL  %s" % p.name)
            for e in errs:
                print("        - %s" % e)
        else:
            obj = json.loads(p.read_text(encoding="utf-8"))
            print("PASS  %s  (provider=%s mode=%s)" % (p.name, obj.get("llm_provider"), obj.get("mode")))
    print("\n%s" % ("GUARD FAIL" if any_fail else "GUARD PASS"))
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
