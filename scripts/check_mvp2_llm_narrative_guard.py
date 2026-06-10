#!/usr/bin/env python3
"""
MVP-2 LLM narrative guard — gate before a narrative JSON may reach a page.

Checks each docs/data_audit/mvp2_llm_narratives/*.json against
docs/MVP2_LLM_NARRATIVE_CONTRACT.md:
  - required fields present + correct shapes (signals = [{name, text, source_refs, assumption_flag}])
  - customer-facing prose has NO forbidden wording (betting/odds/盘口/竞猜/投注 + guarantee words)
  - NO fake probability (命中率 / 胜率 / win rate / tỷ lệ thắng)
  - customer prose has NO engineering/audit tokens (MISS / source required / historical replay /
    assumption / replay_only / data_status / raw factor keys like team_strength)
  - hero_title has no "MISS"
  - vi-VN files: ZERO Han characters anywhere
  - every signal carries non-empty source_refs OR assumption_flag=true
  - internal_notes is a list (engineering/compliance truth, not customer prose)

Exit code 0 = all PASS; non-zero = at least one FAIL. Usage:
  python3 scripts/check_mvp2_llm_narrative_guard.py [file ...]   (default: scan the narratives dir)
"""
import json
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
NARR_DIR = ROOT / "docs" / "data_audit" / "mvp2_llm_narratives"
HAN = re.compile(r"[一-鿿]")

CUSTOMER_TEXT_FIELDS = ["hero_title", "hero_subtitle", "model_judgement",
                        "customer_takeaway", "operator_copy", "cta_copy"]
SIGNAL_LISTS = ["validated_signals", "underweighted_signals"]
REQUIRED = CUSTOMER_TEXT_FIELDS + SIGNAL_LISTS + ["internal_notes", "source_ref_map", "llm_provider", "language"]

FORBIDDEN = [
    "下注", "稳赚", "稳赢", "必中", "必赢", "包赢", "跟单", "购彩", "回报率", "返奖",
    "收益承诺", "现金奖池", "投注", "盘口", "竞猜", "赔率",
    "cá cược", "đặt cược", "chắc thắng", "đảm bảo thắng",
    "betting", "odds", "guaranteed win", "sure win", "wager",
]
FAKE_PROB = ["命中率", "胜率", "win rate", "win probability", "tỷ lệ thắng", "tỷ lệ trúng"]
# engineering/audit tokens that must NOT appear in customer-facing prose
AUDIT_TOKENS = [
    "MISS", "source required", "source_required", "historical replay", "历史回放", "phát lại lịch sử",
    "assumption", "replay_only", "data_status", "missing_evidence", "source_refs", "assumption_flag",
    "scoutscore_factors", "team_strength", "match_control", "event_momentum", "recent_form",
    "lineup_formation", "missing_risk", "not_real_archived",
]
ALLOWED_FORBIDDEN_CTX = {  # forbidden substring OK only inside these
    "odds": [],  # none
    "betting": ["not a betting", "no betting", "non-betting"],
    "cá cược": ["không phải dịch vụ cá cược", "không nhận cược", "không cá cược"],
}


def _ctx_ok(text_l, term_l):
    ctxs = ALLOWED_FORBIDDEN_CTX.get(term_l)
    return bool(ctxs) and any(c in text_l for c in ctxs)


def _signal_text(sig):
    """Customer prose inside a signal dict (NOT source_refs)."""
    if not isinstance(sig, dict):
        return str(sig)
    return " ".join(str(sig.get(k, "")) for k in ("name", "text", "signal", "detail", "interpretation"))


def check(path):
    errs = []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return ["invalid JSON: %s" % e]
    is_vi = obj.get("language") == "vi-VN" or ".vi-VN." in path.name

    # 1. required fields
    for f in REQUIRED:
        if f not in obj:
            errs.append("missing field: %s" % f)
    # 2. internal_notes must be a list
    if "internal_notes" in obj and not isinstance(obj["internal_notes"], list):
        errs.append("internal_notes must be a list (got %s)" % type(obj["internal_notes"]).__name__)

    # 3. signal lists shape + provenance
    for lst in SIGNAL_LISTS:
        items = obj.get(lst)
        if not isinstance(items, list) or not items:
            errs.append("%s must be a non-empty list" % lst)
            continue
        for i, sig in enumerate(items):
            if not isinstance(sig, dict):
                errs.append("%s[%d] not an object" % (lst, i)); continue
            if "name" not in sig or "text" not in sig:
                errs.append("%s[%d] must have 'name' and 'text' (got keys: %s)" % (lst, i, list(sig.keys())))
            refs = sig.get("source_refs")
            has_refs = isinstance(refs, list) and len(refs) > 0
            if not has_refs and not sig.get("assumption_flag"):
                errs.append("%s[%d] needs non-empty source_refs OR assumption_flag=true" % (lst, i))

    # 4. customer prose scans (text fields + signal name/text)
    prose = [str(obj.get(f, "")) for f in CUSTOMER_TEXT_FIELDS]
    for lst in SIGNAL_LISTS:
        for sig in (obj.get(lst) or []):
            prose.append(_signal_text(sig))
    blob = "\n".join(prose)
    blob_l = blob.lower()
    for term in FORBIDDEN:
        t = term.lower()
        if t in blob_l and not _ctx_ok(blob_l, t):
            errs.append("forbidden wording in customer prose: %r" % term)
    for term in FAKE_PROB:
        if term.lower() in blob_l:
            errs.append("fake-probability wording in customer prose: %r" % term)
    for term in AUDIT_TOKENS:
        # case-sensitive for MISS (avoid matching 'dismiss' etc.), else case-insensitive
        if term == "MISS":
            if re.search(r"\bMISS\b", blob):
                errs.append("audit token in customer prose: 'MISS'")
        elif term.lower() in blob_l:
            errs.append("audit/engineering token in customer prose: %r" % term)
    # 5. hero_title no MISS (redundant but explicit)
    if re.search(r"\bMISS\b", str(obj.get("hero_title", ""))):
        errs.append("hero_title contains 'MISS'")

    # 6. vi Han = 0 (whole file string values)
    if is_vi:
        def walk(v):
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                return " ".join(walk(x) for x in v)
            if isinstance(v, dict):
                return " ".join(walk(x) for x in v.values())
            return ""
        han = HAN.findall(walk(obj))
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
            print("PASS  %s" % p.name)
    print("\n%s" % ("GUARD FAIL" if any_fail else "GUARD PASS"))
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
