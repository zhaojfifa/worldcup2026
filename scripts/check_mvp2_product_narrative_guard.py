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
# Case-sensitive standalone "AI" with ASCII-only boundaries: Python \b treats CJK as \w,
# so r"\bAI\b" misses zh-embedded tokens like 今日AI观点 (Track A P0 hardening; lowercase
# Vietnamese "ai" = who stays allowed).
AI_TOKEN = re.compile(r"(?<![A-Za-z0-9_])AI(?![A-Za-z0-9_])")

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
    # vi (incl. handicap slang: kèo / cửa trên / cửa dưới)
    "cá cược", "đặt cược", "kèo", "cửa trên", "cửa dưới", "nhà cái", "soi kèo", "chắc thắng", "bao thắng", "ăn chắc",
    # my (Burmese gambling/odds/guarantee vocabulary — banned even in negation in narrative prose;
    # the UI compliance footer keeps its negated form OUTSIDE narrative JSON)
    "လောင်းကစား", "လောင်းကြေး", "အလောင်းအစား", "လောင်းထား", "ကြေးပေါက်", "ပေါက်ကြေး", "သေချာပေါက်",
    # handicap vocabulary (Evidence Expansion sprint: external signals stay internal-only)
    "亚盘", "让球盘", "大小球", "tài xỉu", "chấp bóng",
    # en
    "betting", "odds", "wager", "bookmaker", "parlay", "guaranteed win", "sure win", "handicap",
    # brand / voice bans (June-11 trial): football product must not surface Cloud or generic AI-analysis voice
    "cloud", "ai 分析", "ai分析", "我们没有数据", "không có dữ liệu nên", "thiếu dữ liệu", "缺数据", "缺少数据",
    "数据缺失", "模型自证",
]
FAKE_PROB = ["命中率", "胜率", "中奖率", "win rate", "win probability", "tỷ lệ thắng", "tỷ lệ trúng", "xác suất thắng",
             "အောင်နှုန်း"]
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
# real_recap (Track A A4): the pre-match judgement is a REAL archived prediction, so the
# recap must stay honest — no hindsight-brag / "told you so" voice in customer prose.
# NOTE: bare 马后炮 is NOT banned — existing narratives legitimately use the negation
# 「不是马后炮」; only positive brag phrasings are listed.
HINDSIGHT_BANS = ["早就说过", "我早说", "看吧，我说", "i told you so",
                  "đã bảo mà", "thấy chưa, tôi đã nói",
                  # Evidence Expansion sprint: "we already knew everything" class
                  "全都料到", "全部料到", "一切尽在掌握", "早已看穿", "我们早就知道", "全部命中",
                  "knew everything", "đã biết trước tất cả"]
# "predicted the red card / penalty" overclaim — the pre-match judgement can NEVER claim
# event-level foresight (Evidence Expansion sprint requirement 7)
PREDICTED_EVENT_OVERCLAIM = [
    re.compile(r"(预判|预测|预言|料到|算到|早就?知道)[^。；.!?\n]{0,10}(红牌|点球|罚下)"),
    re.compile(r"(红牌|点球|罚下)[^。；.!?\n]{0,14}(预料之中|意料之中|早有预判|早在预判)"),
    re.compile(r"(đoán trước|dự đoán trước|biết trước|lường trước)[^.;!?\n]{0,40}(thẻ đỏ|phạt đền)", re.I),
    re.compile(r"predicted[^.;!?\n]{0,30}(red card|penalty)", re.I),
]
# decisive-event mention requirement: when the factor frame records red cards / penalty
# goals, the recap customer prose must engage with them (per-language terms; en accepted
# for my which mixes concise English product terms)
EVENT_TERMS = {
    "red_card": {"zh-CN": ["红牌", "罚下"], "vi-VN": ["thẻ đỏ"],
                 "my-MM": ["အနီကဒ်", "အနီကတ်", "ကဒ်နီ", "red card"]},
    "penalty": {"zh-CN": ["点球"], "vi-VN": ["phạt đền", "penalty"],
                "my-MM": ["ပယ်နယ်တီ", "penalty"]},
}
RECAP_MODES = ("historical_recap", "real_recap")
FRAMES_DIR = pathlib.Path(__file__).resolve().parents[1] / "docs" / "data_audit" / "mvp2_scoutscore_v0_2"


def _recap_frame_for(obj):
    """Load the factor frame backing a recap narrative (None if absent — older artifacts)."""
    fid = str(obj.get("fixture_id", ""))
    name = ("%s.real_recap.factor_frame.json" % fid) if obj.get("mode") == "real_recap" \
        else ("%s.factor_frame.json" % fid)
    p = FRAMES_DIR / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def has_model_estimate_marker(text):
    """scoreline_view must read as a non-promise band: legacy model-estimate phrasing OR
    de-modeled persona reference-band phrasing (俅哥…参考区间 / khoảng tham khảo…Tiên Tri /
    Football Oracle ၏ ပွဲကြို ရည်ညွှန်းအပိုင်းအခြား)."""
    t = str(text).lower()
    est = any(m in t for m in ("估计", "预估", "ước tính", "estimate"))
    subj = any(m in t for m in ("模型", "mô hình", "scoutscore", "giành cup ai", "model"))
    ref = any(m in t for m in ("参考区间", "参考比分", "tham khảo", "ရည်ညွှန်း"))
    persona = any(m in t for m in ("俅哥", "tiên tri", "赛前", "trước trận", "oracle", "ပွဲကြို"))
    return (est and subj) or (ref and persona)


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
    if obj.get("product_surface") == "trial_rescore_update":
        return check_rescore_update_obj(obj, path.name)
    return check_obj(obj, path.name)


def check_obj(obj, filename=""):
    """Full guard on a narrative dict (also imported by the generator's retry loop)."""
    errs = []
    mode = obj.get("mode", "")
    is_recap = mode in RECAP_MODES
    is_real_recap = mode == "real_recap"
    is_pre = mode == "pre_match_2026_modeling"
    is_vi = obj.get("language") == "vi-VN" or ".vi-VN." in filename
    is_my = obj.get("language") == "my-MM" or ".my-MM." in filename

    # 1. required fields
    for f in REQUIRED:
        if f not in obj:
            errs.append("missing field: %s" % f)
    if mode not in ("historical_recap", "real_recap", "pre_match_2026_modeling"):
        errs.append("mode must be historical_recap | real_recap | pre_match_2026_modeling (got %r)" % mode)
    if not isinstance(obj.get("internal_notes"), list) or not obj.get("internal_notes"):
        errs.append("internal_notes must be a non-empty list")
    if not isinstance(obj.get("source_ref_map"), dict) or not obj.get("source_ref_map"):
        errs.append("source_ref_map must be a non-empty object")

    # 2. product name / persona in the hero block
    hero_blob = " ".join(str(obj.get(k, "")) for k in ("hero_title", "hero_subtitle", "model_judgement"))
    if not any(b in hero_blob for b in ("Giành Cup", "ScoutScore", "俅哥", "中文先知", "Tiên Tri", "Football Oracle")):
        errs.append("brand/persona (Giành Cup / ScoutScore / 俅哥 / Tiên Tri / Football Oracle) missing from hero block")

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
                errs.append("%s requires non-empty %s" % (mode, k))
        notes_raw_all = walk_strings(obj.get("internal_notes", []))
        notes = notes_raw_all.lower()
        if is_real_recap:
            # the pre-match judgement is a REAL archived prediction: internal_notes must
            # cite the stored artifact (path + sha256 + timestamp), NOT a replay disclaimer.
            if "sha256:" not in notes:
                errs.append("real_recap internal_notes must cite the archived pre-match artifact hash (sha256:…)")
            if "docs/data_audit/" not in notes_raw_all:
                errs.append("real_recap internal_notes must cite the archived pre-match artifact path (docs/data_audit/…)")
        elif "replay" not in notes and "archived" not in notes and "phục dựng" not in notes and "回放" not in notes_raw_all:
            errs.append("internal_notes must disclose the historical-replay nature")
    if is_pre:
        for k in ("risk_level", "scoreline_view"):
            if not str(obj.get(k, "")).strip():
                errs.append("pre_match requires non-empty %s" % k)
        sv = str(obj.get("scoreline_view", ""))
        if sv and not has_model_estimate_marker(sv):
            errs.append("scoreline_view must carry a model-estimate marker (e.g. 模型估计 / mô hình ước tính)")
        basis = obj.get("fixture_basis")
        notes_raw = walk_strings(obj.get("internal_notes", []))
        notes_blob = notes_raw.lower()
        if basis not in ("real_scheduled", "hypothetical_scenario"):
            errs.append("pre_match requires fixture_basis = real_scheduled | hypothetical_scenario (got %r)" % basis)
        elif basis == "hypothetical_scenario":
            if "hypothetical" not in notes_blob and "giả định" not in notes_blob and "假想" not in notes_raw:
                errs.append("internal_notes must disclose the hypothetical fixture")
        else:  # real_scheduled: pre-match view on a real fixture — lineups-pending disclosure required
            if not any(t in notes_blob for t in ("lineup", "đội hình")) and not any(t in notes_raw for t in ("阵容", "首发")):
                errs.append("internal_notes must disclose that lineups/XI are not announced (real_scheduled)")

    # 4b. June-11 trial surface: persona + tactical_read required
    if obj.get("product_surface") == "trial_prediction":
        if not str(obj.get("tactical_read", "")).strip():
            errs.append("trial_prediction requires non-empty tactical_read")
        whole = walk_strings({k: v for k, v in obj.items() if k not in ("internal_notes", "source_ref_map")})
        if is_vi:
            if "Tiên Tri" not in whole:
                errs.append("vi trial narrative must speak as Tiên Tri Bóng Đá")
        elif is_my:
            if "Football Oracle" not in whole:
                errs.append("my trial narrative must speak as Football Oracle (temporary trial persona)")
        elif obj.get("language") == "zh-CN" and "俅哥" not in whole:
            errs.append("zh trial narrative must speak as 俅哥 (俅哥说球)")

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
    if str(obj.get("tactical_read", "")).strip():
        prose.append(str(obj.get("tactical_read")))
    for lst in FACTOR_LISTS:
        for sig in (obj.get(lst) or []):
            prose.append(_factor_text(sig))
    blob = "\n".join(prose)
    blob_l = blob.lower()
    # de-modeled persona surfaces: NO model/process subject words in customer prose at all
    if str(obj.get("voice", "")).endswith("_v2"):
        # zh list mirrors scripts/check_customer_visible_copy.py ZH_FORBIDDEN — the scanner
        # bans the literal n-gram (e.g. 过程验证 even as 过程+验证了), so the guard must too
        for term in ("模型", "盲区", "过程验证", "数据缺失", "缺数据", "自证", "mô hình", "မော်ဒယ်", "ဒေတာမရှိ", "scoutscore", "deepseek", "gemini", "llm", "pipeline", "schema", "provider"):
            if term in blob_l:
                errs.append("de-model violation in customer prose: %r" % term)
        # case-sensitive standalone AI (lowercase 'ai' is the Vietnamese word for 'who');
        # ASCII-boundary pattern catches zh-embedded AI (今日AI观点) that \b misses
        if AI_TOKEN.search(blob):
            errs.append("de-model violation in customer prose: 'AI'")
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
    # hindsight bans only for real_recap (NEW mode) — historical_recap baseline untouched
    if is_real_recap:
        for term in HINDSIGHT_BANS:
            if term.lower() in blob_l:
                errs.append("hindsight-brag tone in recap prose: %r" % term)
        # scoreline overclaim: if the actual score is NOT one of the archived reference
        # scores, the recap must not claim it fell inside the band (first real A4 caught
        # zh writing "实际比分2-0，在合理区间内" against an archived 1-1/1-0/0-1 band)
        sv = str(obj.get("scoreline_view", ""))
        m = re.search(r"(?:实际比分|实际|tỷ số thực tế|kết quả thực|အမှန်တကယ်|ပြီးခဲ့သောရလဒ်)\D{0,8}(\d+\s*[-–]\s*\d+)", sv, re.I)
        # negated phrasing ("不在区间内" / "nằm ngoài khoảng") is the honest case — strip it first
        sv_claims = re.sub(r"(?:不在|没在|不属于|nằm ngoài|ngoài)\s*[^。.!?；;]*?(?:区间内|区间之内|khoảng)", "", sv, flags=re.I)
        in_band_claim = re.search(r"区间内|区间之内|nằm trong khoảng|trong vùng tham khảo|အပိုင်းအခြားအတွင်း", sv_claims, re.I)
        if m and in_band_claim:
            actual = re.sub(r"\s", "", m.group(1)).replace("–", "-")
            band = [re.sub(r"\s", "", s).replace("–", "-") for s in re.findall(r"\d+\s*[-–]\s*\d+", sv[:m.start()])]
            if actual not in band:
                errs.append("real_recap scoreline overclaim: actual %s not in archived band %s but prose claims in-band" % (actual, band))

    # ── Evidence Expansion sprint (both recap modes) ──────────────────────────
    if is_recap:
        # 7a. event-level foresight overclaim ("predicted the red card") — honest
        # negations ("无法预判…红牌" / "không thể đoán trước…thẻ đỏ" / "could not have
        # predicted…") are the CORRECT phrasing and stay legal
        NEG_BEFORE = ("无法", "没法", "不能", "未能", "没能", "无从", "不可能", "没办法", "谁也没",
                      "không thể", "không ai", "could not", "couldn't", "cannot", "can't", "no way to")
        for pat in PREDICTED_EVENT_OVERCLAIM:
            for mm in pat.finditer(blob):
                lead = blob[max(0, mm.start() - 14):mm.start()].lower()
                if any(neg in lead for neg in NEG_BEFORE):
                    continue
                errs.append("event-foresight overclaim in recap prose: %r" % mm.group(0))
        frame = _recap_frame_for(obj)
        ei = (frame or {}).get("event_impact")
        # event-mention requirement applies to artifacts generated AFTER the Evidence
        # Expansion sprint landed (2026-06-12); older artifacts predate the contract and
        # are superseded on their own regeneration schedule, not failed retroactively.
        # NO generated_at = in-flight candidate inside the generator retry loop -> NEW.
        gen_at = str(obj.get("generated_at", ""))
        if ei and (not gen_at or gen_at >= "2026-06-12"):
            lang = obj.get("language") or ("vi-VN" if is_vi else "my-MM" if is_my else "zh-CN")
            # 7b. decisive events must be engaged with, not skipped
            reds_total = sum((ei.get("cards") or {}).get("red_count", {}).values())
            red_mentioned = any(t.lower() in blob_l for t in EVENT_TERMS["red_card"].get(lang, []))
            if reds_total and not red_mentioned:
                errs.append("decisive event missing: frame records %d red card(s) but recap prose never mentions them" % reds_total)
            if not reds_total and red_mentioned:
                errs.append("PHANTOM event: recap prose mentions a red card but the frame records ZERO red cards (fabricated fact)")
            pens = [d for d in ei.get("decisive_events", []) if d.get("event_type") == "penalty_goal"]
            pen_mentioned = any(t.lower() in blob_l for t in EVENT_TERMS["penalty"].get(lang, []))
            if pens and not pen_mentioned:
                errs.append("decisive event missing: frame records %d penalty goal(s) but recap prose never mentions them" % len(pens))
            # "ALL goals came against 10 men" class: false whenever any goal was scored
            # at equal men (first live vi recap wrote '2 bàn đều ghi khi…còn 10 người'
            # though the 9' opener came at 11v11)
            goals_ev = [d for d in ei.get("decisive_events", []) if d.get("event_type") in ("goal", "penalty_goal")]
            any_equal_men = any(len(set((d.get("men_on_pitch_after") or {}).values())) <= 1 for d in goals_ev)
            if any_equal_men:
                for pat in (r"(两|2|兩)[个粒]?(进球|球)都?在?[^。；.!?\n]{0,12}(少打|10人|多打)",
                            r"全部进球[^。；.!?\n]{0,10}(少打|10人)",
                            r"(cả hai|2|hai)\s*bàn[^.;!?\n]{0,40}đều[^.;!?\n]{0,40}(10 người|hơn người|thẻ đỏ)",
                            r"(both|all)\s+goals[^.;!?\n]{0,40}(10 men|man advantage)"):
                    mm = re.search(pat, blob, re.I)
                    if mm:
                        errs.append("event overclaim: claims ALL goals came with a man advantage but the frame shows a goal at equal men: %r" % mm.group(0))
                        break
            if not pens and pen_mentioned and not (ei.get("var_available")):
                # shootout-decided matches legitimately discuss 点球大战 — only flag when
                # NO penalty goal and NO shootout exists in the frame
                sw = ((frame or {}).get("fixture") or {}).get("shootout_winner")
                if not sw:
                    errs.append("PHANTOM event: recap prose mentions a penalty but the frame records none (fabricated fact)")
        # 7c. unsupported exact claims — ages/workload (no source ingested -> no numbers)
        dims = {d.get("dimension"): d for d in ((frame or {}).get("extended_dimensions") or {}).get("dimensions", [])}
        age_missing = (not dims) or dims.get("age_profile", {}).get("missing_evidence", True)
        if age_missing:
            for pat in (r"\d+\s*岁", r"\d+\s*tuổi", r"aged\s+\d+", r"平均年龄[^。;\n]{0,6}\d+"):
                mm = re.search(pat, blob, re.I)
                if mm:
                    errs.append("unsupported exact age claim (age source NOT ingested): %r" % mm.group(0))
        mm = re.search(r"\d+(?:\.\d+)?\s*(?:公里|km)", blob, re.I)
        if mm:
            errs.append("unsupported exact workload claim (no distance/workload source): %r" % mm.group(0))
        # 7d. external expectation claims need a recorded signal (stubs are all missing now)
        for term in ("市场共识", "外部预期", "公开预测倾向", "đồng thuận thị trường", "kỳ vọng bên ngoài"):
            if term.lower() in blob_l:
                errs.append("external expectation claim %r without a recorded signal (mvp2_external_signals stub is missing_evidence)" % term)
    # links are engineering stage (real CTA buttons) — the LLM must never invent one
    if re.search(r"https?://|t\.me/|www\.", blob):
        errs.append("URL in customer prose (links are injected by the page, never written by the LLM)")

    # 10. vi / my Han = 0 (whole file — Burmese surfaces must contain zero Chinese)
    if is_vi or is_my:
        han = HAN.findall(walk_strings(obj))
        if han:
            errs.append("%s has %d Han char(s): %s" % ("my-MM" if is_my else "vi-VN", len(han), "".join(han[:30])))

    return errs


# ── Track A A3 surface: trial_rescore_update (LLM update on a facts-only diff skeleton) ──
RESCORE_UPDATE_PERSONA = {"zh-CN": "俅哥", "vi-VN": "Tiên Tri", "my-MM": "Football Oracle"}


def check_rescore_update_obj(obj, filename=""):
    """Guard for `trial_rescore_update` artifacts (Track A A3). Customer prose =
    what_changed texts + updated_* + group_update_message + no_change_note;
    based_on / lineup_facts are the engineering skeleton (internal)."""
    errs = []
    lang = obj.get("language") or ""
    if obj.get("product_surface") != "trial_rescore_update":
        errs.append("product_surface must be trial_rescore_update")
    if not obj.get("llm_provider") or obj.get("llm_provider") == "mock":
        errs.append("rescore updates must be REAL LLM output (llm_provider=%r)" % obj.get("llm_provider"))
    for f in ("fixture_id", "language", "voice", "updated_lean", "updated_risk_level",
              "updated_score_range", "group_update_message", "expires_at"):
        if not str(obj.get(f, "")).strip():
            errs.append("missing/empty field: %s" % f)
    based = obj.get("based_on") or {}
    if not (isinstance(based, dict) and based.get("judgement_path") and based.get("inputs_hash")):
        errs.append("based_on must carry judgement_path + inputs_hash (provenance of the original judgement)")
    if not isinstance(obj.get("lineup_facts"), dict) or not obj.get("lineup_facts"):
        errs.append("lineup_facts (engineering skeleton) must be a non-empty object")
    wc = obj.get("what_changed")
    if not isinstance(wc, list):
        errs.append("what_changed must be a list")
        wc = []
    if not wc and not str(obj.get("no_change_note", "")).strip():
        errs.append("empty what_changed requires a no_change_note")
    for i, ch in enumerate(wc):
        if not isinstance(ch, dict):
            errs.append("what_changed[%d] not an object" % i)
            continue
        for f in ("name", "before", "now", "effect"):
            if not str(ch.get(f, "")).strip():
                errs.append("what_changed[%d].%s empty" % (i, f))
        if not str(ch.get("fired_rule", "")).strip() and not ch.get("assumption_flag"):
            errs.append("what_changed[%d] needs fired_rule OR assumption_flag=true" % i)
    rng = str(obj.get("updated_score_range", ""))
    if rng and not has_model_estimate_marker(rng):
        errs.append("updated_score_range must carry the persona reference-band marker")
    # customer prose scans (skeleton fields excluded — they are internal engineering facts)
    prose = [str(obj.get(k, "")) for k in ("updated_lean", "updated_risk_level",
                                           "updated_score_range", "group_update_message", "no_change_note")]
    for ch in wc:
        if isinstance(ch, dict):
            prose.append(" ".join(str(ch.get(k, "")) for k in ("name", "before", "now", "effect")))
    blob = "\n".join(prose)
    bl = blob.lower()
    for term in ("模型", "盲区", "过程验证", "数据缺失", "缺数据", "自证", "mô hình", "မော်ဒယ်", "ဒေတာမရှိ", "scoutscore", "deepseek", "gemini", "llm",
                 "pipeline", "schema", "provider"):
        if term in bl:
            errs.append("de-model violation in customer prose: %r" % term)
    if AI_TOKEN.search(blob):
        errs.append("de-model violation in customer prose: 'AI'")
    for term in FORBIDDEN + FAKE_PROB + TONE_BANS + HINDSIGHT_BANS:
        if term.lower() in bl:
            errs.append("forbidden/tone wording in customer prose: %r" % term)
    if re.search(r"https?://|t\.me/|www\.", blob):
        errs.append("URL in customer prose (links are page-injected, never LLM-written)")
    persona = RESCORE_UPDATE_PERSONA.get(lang)
    if persona and persona not in blob:
        errs.append("%s rescore update must speak as %s" % (lang, persona))
    if lang in ("vi-VN", "my-MM"):
        han = HAN.findall(walk_strings(obj))
        if han:
            errs.append("%s has %d Han char(s): %s" % (lang, len(han), "".join(han[:20])))
    return errs


def _selftest_tracka():
    """Synthetic vectors for the Track A guard extensions (no artifacts written)."""
    base = json.loads((NARR_DIR / "855737.zh-CN.deepseek.json").read_text(encoding="utf-8"))
    results = []

    rr_ok = dict(base)
    rr_ok["mode"] = "real_recap"
    rr_ok["internal_notes"] = [
        "real recap of an archived pre-match judgement",
        "pre-match artifact: docs/data_audit/mvp2_trial_prediction_narratives/855737.zh-CN.deepseek.json "
        "(sha256:deadbeef) generated_at 2026-06-11T05:00:00+00:00",
    ]
    results.append(("real_recap provenance PASS", not check_obj(rr_ok)))

    rr_bad = dict(rr_ok)
    rr_bad["internal_notes"] = ["real recap, no citation"]
    e = check_obj(rr_bad)
    results.append(("real_recap missing provenance FAIL", any("sha256" in x for x in e)))

    rr_brag = dict(rr_ok)
    rr_brag = json.loads(json.dumps(rr_brag, ensure_ascii=False))
    rr_brag["model_judgement"] = rr_brag["model_judgement"] + " 俅哥早就说过这场要爆冷。"
    e = check_obj(rr_brag)
    results.append(("real_recap hindsight-brag FAIL", any("hindsight" in x for x in e)))

    ru_ok = {
        "product_surface": "trial_rescore_update", "fixture_id": "1489371", "language": "zh-CN",
        "voice": "qiuge_v2", "llm_provider": "deepseek", "expires_at": "2026-06-13T22:00:00+00:00",
        "based_on": {"judgement_path": "docs/data_audit/mvp2_trial_prediction_narratives/1489371.zh-CN.deepseek.json",
                      "inputs_hash": "sha256:abc"},
        "lineup_facts": {"home_xi": ["..."], "gk": {"Brazil": "Alisson"}},
        "what_changed": [{"name": "门将人选确认", "before": "门将未定", "now": "首发门将已确认",
                           "effect": "后防稳定性判断上调", "fired_rule": "favourite_spine_intact"}],
        "updated_lean": "俅哥维持巴西方向，信心略升",
        "updated_risk_level": "中高——锋线依赖仍在",
        "updated_score_range": "俅哥给出的赛前参考区间：2-0、2-1、1-1",
        "group_update_message": "【俅哥临场修正】首发出了：巴西中轴完整，俅哥维持原判断，比分参考区间收窄。",
    }
    results.append(("rescore_update PASS", not check_rescore_update_obj(ru_ok)))

    ru_bad = json.loads(json.dumps(ru_ok, ensure_ascii=False))
    ru_bad["llm_provider"] = "mock"
    ru_bad["what_changed"][0].pop("fired_rule")
    ru_bad["group_update_message"] = "盘口告诉你们：必中。"
    e = check_rescore_update_obj(ru_bad)
    results.append(("rescore_update mock+rule+betting FAIL",
                    any("mock" in x.lower() for x in e) and any("fired_rule" in x for x in e)
                    and any("盘口" in x for x in e)))

    ru_noband = json.loads(json.dumps(ru_ok, ensure_ascii=False))
    ru_noband["updated_score_range"] = "2-0"
    e = check_rescore_update_obj(ru_noband)
    results.append(("rescore_update missing band marker FAIL", any("reference-band" in x for x in e)))

    failed = [n for n, good in results if not good]
    for n, good in results:
        print("%s  %s" % ("PASS" if good else "FAIL", n))
    print("\nTRACK-A GUARD SELFTEST %s (%d/%d)" % ("PASS" if not failed else "FAIL",
                                                    len(results) - len(failed), len(results)))
    sys.exit(1 if failed else 0)


def main():
    if "--selftest-tracka" in sys.argv:
        _selftest_tracka()
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
