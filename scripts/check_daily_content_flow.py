#!/usr/bin/env python3
"""
R1 P0 — Daily content-production-chain guard (Owner 2026-06-15: content chain FIRST, not UI-only).

Enforces that the selected daily hotspot has a REAL content production chain end-to-end, not a
hand-authored UI-only artifact:

  selected_hotspot → prediction artifact → source_facts → model_fields → LLM/operator judgement
                   → content_chain (prompt generated + reviewed applied) → share kit → T-30 slot

Fails if, for the selected hotspot's prediction artifact:
  - selected_hotspot present but NO artifact;
  - artifact lacks source_facts;
  - artifact lacks model_fields / invalid model_fields.source / non-null win_prob|confidence;
  - artifact lacks LLM/operator judgement (llm_judgment OR i18n[zh].prediction);
  - content_chain missing / prompt_generated not true / no prompt_path recorded;
  - the recorded prompt_path file does not exist on disk; reviewed_applied but reviewed_path missing/absent;
  - share_copy missing;
  - t30 slot missing/invalid;
  - content_chain cannot express /internal/daily readiness (missing the flags the page renders);
  - betting/trading vocabulary anywhere; safety.no_auto_send / no_fake_probability not true.

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"

BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "竞猜", "让球", "大小球", "跟单", "串关",
           "odds", "handicap", "bookmaker", "wager", "betting",
           "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược"]
VALID_MODEL_SOURCES = {"computed", "seed", "operator_estimated", "operator_confirmed", "unavailable"}
CHAIN_FLAGS = ("model_lookup", "prompt_generated", "reviewed_applied", "llm_provider")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(sel, artifacts, check_files=True):
    """sel: dict|None ; artifacts: list[(name, dict)] (prediction artifacts only)."""
    fails = []
    if not sel or sel.get("status") != "active" or not sel.get("fixture_key"):
        return ["selected_hotspot missing/inactive (no authoritative daily pick)"]
    key = sel["fixture_key"]
    art = next((a for (_n, a) in artifacts if a.get("fixture_key") == key), None)
    if not art:
        return ["selected_hotspot %r has NO prediction artifact" % key]

    sf = art.get("source_facts")
    if not isinstance(sf, dict) or not sf.get("fixture_source") or sf.get("data_mode") not in ("api", "seed", "manual", "operator"):
        fails.append("artifact %r missing/invalid source_facts" % key)

    mf = art.get("model_fields")
    if not isinstance(mf, dict):
        fails.append("artifact %r missing model_fields" % key)
    else:
        if mf.get("source") not in VALID_MODEL_SOURCES:
            fails.append("artifact %r model_fields.source=%r invalid" % (key, mf.get("source")))
        if mf.get("win_prob") is not None:
            fails.append("artifact %r model_fields.win_prob must be null (no fake probability)" % key)
        if mf.get("confidence") is not None:
            fails.append("artifact %r model_fields.confidence must be null (no numeric confidence)" % key)
        if mf.get("no_fake_probability") is not True:
            fails.append("artifact %r model_fields.no_fake_probability must be true" % key)

    # LLM/operator judgement present (structured llm_judgment OR the legacy i18n prediction)
    lj = art.get("llm_judgment")
    zp = (((art.get("i18n") or {}).get("zh") or {}).get("prediction") or {})
    if not (isinstance(lj, dict) and lj.get("main_lean")) and not zp.get("primary_direction"):
        fails.append("artifact %r lacks LLM/operator judgement (llm_judgment.main_lean or i18n prediction)" % key)

    # content_chain — the production-chain provenance the /internal/daily page renders
    cc = art.get("content_chain")
    if not isinstance(cc, dict):
        fails.append("artifact %r missing content_chain (daily production chain not run)" % key)
    else:
        for flag in CHAIN_FLAGS:
            if flag not in cc:
                fails.append("artifact %r content_chain missing readiness flag %r" % (key, flag))
        if cc.get("prompt_generated") is not True:
            fails.append("artifact %r content_chain.prompt_generated must be true (run builder: prompt)" % key)
        if not cc.get("prompt_path"):
            fails.append("artifact %r content_chain.prompt_path missing" % key)
        elif check_files and not (ROOT / cc["prompt_path"]).exists():
            fails.append("artifact %r prompt file does not exist: %s" % (key, cc["prompt_path"]))
        if cc.get("reviewed_applied"):
            if not cc.get("reviewed_path"):
                fails.append("artifact %r reviewed_applied but reviewed_path missing" % key)
            elif check_files and not (ROOT / cc["reviewed_path"]).exists():
                fails.append("artifact %r reviewed file does not exist: %s" % (key, cc["reviewed_path"]))

    # share kit
    share_copy = (((art.get("i18n") or {}).get("zh") or {}).get("operations") or {}).get("share_copy")
    if not share_copy:
        fails.append("artifact %r missing operations.share_copy (share kit)" % key)

    # T-30 slot
    t = art.get("t30")
    if not isinstance(t, dict) or t.get("status") not in ("pending", "ready", "skipped"):
        fails.append("artifact %r missing a valid t30 slot" % key)

    # safety + vocabulary (scan the whole artifact text)
    saf = art.get("safety") or {}
    if saf.get("no_auto_send") is not True or saf.get("no_fake_probability") is not True:
        fails.append("artifact %r safety.no_auto_send / no_fake_probability must be true" % key)
    blob = json.dumps(art, ensure_ascii=False)
    low = blob.lower()
    for w in BETTING:
        if (w.lower() in low) if w.isascii() else (w in blob):
            fails.append("artifact %r contains betting/trading vocab %r" % (key, w))
    return fails


def _good():
    return {
        "fixture_key": "manual:X-Y-20260614", "home": "X", "away": "Y",
        "source_facts": {"fixture_source": "manual_slate", "data_mode": "manual",
                         "has_model_fields": True, "source_refs": [], "missing_fields": ["win_prob", "confidence"]},
        "model_fields": {"win_prob": None, "recommended_score": "2-1", "backup_scores": ["1-1"],
                         "risk_level": "中高", "confidence": None, "source": "operator_estimated",
                         "model_status": "operator_estimated", "no_fake_probability": True},
        "llm_judgment": {"main_lean": "倾向X"},
        "content_chain": {"date": "20260614", "model_lookup": "unavailable", "model_lookup_note": "n",
                          "prompt_path": "docs/data_audit/mvp2_predictions/prompts/x_prompt.md",
                          "prompt_generated": True, "reviewed_path": None,
                          "reviewed_applied": False, "llm_provider": "pending"},
        "t30": {"status": "pending"}, "safety": {"no_auto_send": True, "no_fake_probability": True},
        "i18n": {"zh": {"prediction": {"primary_direction": "倾向X"}, "operations": {"share_copy": "今日主推 X vs Y"}}},
    }


def selftest():
    sel = {"status": "active", "fixture_key": "manual:X-Y-20260614", "home": "X", "away": "Y"}
    good = _good()
    checks = [
        ("clean passes", scan(sel, [("g", good)], check_files=False) == []),
        ("no artifact caught", any("NO prediction artifact" in x for x in scan(
            {"status": "active", "fixture_key": "manual:Z"}, [("g", good)], check_files=False))),
        ("missing source_facts caught", any("source_facts" in x for x in scan(
            sel, [("g", {k: v for k, v in good.items() if k != "source_facts"})], check_files=False))),
        ("missing model_fields caught", any("model_fields" in x for x in scan(
            sel, [("g", {k: v for k, v in good.items() if k != "model_fields"})], check_files=False))),
        ("fake win_prob caught", any("win_prob" in x for x in scan(
            sel, [("g", dict(good, model_fields=dict(good["model_fields"], win_prob={"home": 60})))], check_files=False))),
        ("missing content_chain caught", any("content_chain" in x for x in scan(
            sel, [("g", {k: v for k, v in good.items() if k != "content_chain"})], check_files=False))),
        ("prompt_not_generated caught", any("prompt_generated" in x for x in scan(
            sel, [("g", dict(good, content_chain=dict(good["content_chain"], prompt_generated=False)))], check_files=False))),
        ("missing judgement caught", any("judgement" in x for x in scan(
            sel, [("g", dict(good, llm_judgment={}, i18n={"zh": {"prediction": {}, "operations": {"share_copy": "x"}}}))], check_files=False))),
        ("missing share_copy caught", any("share_copy" in x for x in scan(
            sel, [("g", dict(good, i18n={"zh": {"prediction": {"primary_direction": "x"}, "operations": {}}}))], check_files=False))),
        ("missing t30 caught", any("t30" in x for x in scan(
            sel, [("g", {k: v for k, v in good.items() if k != "t30"})], check_files=False))),
        ("betting vocab caught", any("betting" in x for x in scan(
            sel, [("g", dict(good, i18n={"zh": {"prediction": {"primary_direction": "x"}, "operations": {"share_copy": "看 赔率"}}}))], check_files=False))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    sel = _load(SEL)
    artifacts = []
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            try:
                a = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                sys.stdout.write("FAIL  %s invalid JSON (%s)\n" % (p.name, e))
                return 1
            if "recap_ready" in a:   # observation artifact — not a prediction artifact
                continue
            artifacts.append((p.name, a))
    fails = scan(sel, artifacts, check_files=True)
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("DAILY CONTENT FLOW FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("DAILY CONTENT FLOW PASS (selected_hotspot → artifact → source_facts → model_fields "
                     "→ judgement → content_chain[prompt+review] → share kit → t30)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
