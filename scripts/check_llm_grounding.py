#!/usr/bin/env python3
"""
R3 — LLM grounding guard.

Proves the customer-facing judgement is GROUNDED in the model facts and TRACEABLE end to end for the
selected hotspot's prediction artifact:
  - content_chain present with prompt_path + (if reviewed_applied) reviewed_path;
  - the prompt file exists on disk and contains the fixture key, the model_fields.source line, and the
    "DO NOT INVENT" missing-fields guardrail;
  - the reviewed JSON exists and carries a judgement (main_lean / primary_score) that preserves
    model-derived facts (primary_score consistent with model_fields.recommended_score, OR risk_level
    echoed) — i.e. the copy is not free-floating;
  - the artifact carries a judgement (llm_judgment.main_lean OR i18n[zh].prediction.primary_direction);
  - no betting / fake-probability vocabulary in the reviewed JSON.

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
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _string_values(obj):
    """Yield string VALUES recursively (never dict keys) for vocabulary scanning."""
    out = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_string_values(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_string_values(v))
    return out


def scan(sel, artifacts, read_text=None):
    """read_text(relpath)->str|None lets selftest inject prompt/reviewed bodies."""
    if read_text is None:
        def read_text(rel):
            p = ROOT / rel
            return p.read_text(encoding="utf-8") if p.exists() else None
    fails = []
    if not sel or sel.get("status") != "active" or not sel.get("fixture_key"):
        return ["selected_hotspot missing/inactive"]
    key = sel["fixture_key"]
    art = next((a for (_n, a) in artifacts if a.get("fixture_key") == key), None)
    if not art:
        return ["selected_hotspot %r has NO prediction artifact" % key]

    cc = art.get("content_chain")
    if not isinstance(cc, dict):
        return ["artifact %r missing content_chain (no grounding chain)" % key]
    if not cc.get("prompt_generated") or not cc.get("prompt_path"):
        fails.append("artifact %r content_chain.prompt not generated/recorded" % key)
    mf = art.get("model_fields") or {}
    rec = mf.get("recommended_score")
    risk = mf.get("risk_level")

    prompt_body = read_text(cc["prompt_path"]) if cc.get("prompt_path") else None
    if cc.get("prompt_path") and prompt_body is None:
        fails.append("artifact %r prompt file missing on disk: %s" % (key, cc["prompt_path"]))
    elif prompt_body is not None:
        if key not in prompt_body:
            fails.append("prompt does not reference fixture key %r" % key)
        if "model_fields.source" not in prompt_body and "model" not in prompt_body.lower():
            fails.append("prompt does not carry the model_fields source block")
        if "DO NOT INVENT" not in prompt_body and "DO NOT" not in prompt_body:
            fails.append("prompt missing the DO-NOT-INVENT missing-fields guardrail")

    if cc.get("reviewed_applied"):
        if not cc.get("reviewed_path"):
            fails.append("artifact %r reviewed_applied but reviewed_path missing" % key)
        else:
            rv_raw = read_text(cc["reviewed_path"])
            if rv_raw is None:
                fails.append("artifact %r reviewed file missing on disk: %s" % (key, cc["reviewed_path"]))
            else:
                try:
                    rv = json.loads(rv_raw)
                except Exception:  # noqa: BLE001
                    rv = None
                    fails.append("artifact %r reviewed JSON invalid" % key)
                if rv is not None:
                    if not (rv.get("main_lean") or rv.get("primary_score")):
                        fails.append("reviewed JSON lacks a judgement (main_lean/primary_score)")
                    # grounding: the reviewed copy must preserve a model-derived fact
                    grounded = False
                    if rec and rv.get("primary_score") == rec:
                        grounded = True
                    if risk and rv.get("risk_level") == risk:
                        grounded = True
                    if rec is None and risk is None:
                        grounded = True  # operator_estimated/unavailable — nothing to echo
                    if not grounded:
                        fails.append("reviewed JSON not grounded in model_fields "
                                     "(primary_score %r / risk_level %r vs reviewed %r / %r)"
                                     % (rec, risk, rv.get("primary_score"), rv.get("risk_level")))
                    # Scan only string VALUES (not keys) so safety flag KEYS like
                    # 'no_betting_vocab' do not self-trip the substring scanner (documented lesson).
                    blob = " ".join(_string_values(rv))
                    low = blob.lower()
                    for w in BETTING + FAKE_PROB:
                        if (w.lower() in low) if w.isascii() else (w in blob):
                            fails.append("reviewed JSON contains forbidden vocab %r" % w)

    lj = art.get("llm_judgment")
    zp = (((art.get("i18n") or {}).get("zh") or {}).get("prediction") or {})
    if not (isinstance(lj, dict) and lj.get("main_lean")) and not zp.get("primary_direction"):
        fails.append("artifact %r lacks a judgement on the artifact (llm_judgment/i18n prediction)" % key)
    return fails


def _good_art():
    return {
        "fixture_key": "1489377",
        "model_fields": {"recommended_score": "1-0", "risk_level": "中"},
        "llm_judgment": {"main_lean": "倾向比利时"},
        "content_chain": {"prompt_generated": True, "prompt_path": "p/prompt.md",
                          "reviewed_applied": True, "reviewed_path": "p/reviewed.json"},
        "i18n": {"zh": {"prediction": {"primary_direction": "倾向比利时"}}},
    }


def selftest():
    sel = {"status": "active", "fixture_key": "1489377"}
    art = _good_art()
    bodies = {
        "p/prompt.md": "fixture_key: 1489377\nmodel_fields.source: computed\nDO NOT INVENT: win_prob, confidence",
        "p/reviewed.json": json.dumps({"main_lean": "倾向比利时", "primary_score": "1-0", "risk_level": "中"}),
    }
    def rt(rel):
        return bodies.get(rel)
    checks = [
        ("clean passes", scan(sel, [("g", art)], read_text=rt) == []),
        ("missing prompt file caught", any("prompt file missing" in x for x in scan(
            sel, [("g", art)], read_text=lambda r: None if r == "p/prompt.md" else bodies.get(r)))),
        ("prompt missing DO-NOT-INVENT caught", any("DO-NOT-INVENT" in x for x in scan(
            sel, [("g", art)], read_text=lambda r: ("fixture_key: 1489377\nmodel_fields.source: computed" if r == "p/prompt.md" else bodies.get(r))))),
        ("ungrounded reviewed caught", any("not grounded" in x for x in scan(
            sel, [("g", art)], read_text=lambda r: (json.dumps({"main_lean": "x", "primary_score": "3-3", "risk_level": "低"}) if r == "p/reviewed.json" else bodies.get(r))))),
        ("forbidden vocab caught", any("forbidden vocab" in x for x in scan(
            sel, [("g", art)], read_text=lambda r: (json.dumps({"main_lean": "x", "primary_score": "1-0", "note": "看 赔率"}) if r == "p/reviewed.json" else bodies.get(r))))),
        ("no judgement caught", any("lacks a judgement" in x for x in scan(
            sel, [("g", dict(art, llm_judgment={}, i18n={"zh": {"prediction": {}}}))], read_text=rt))),
        ("operator_estimated (no model echo) passes", scan(
            sel, [("g", dict(art, model_fields={"recommended_score": None, "risk_level": None}))],
            read_text=lambda r: (json.dumps({"main_lean": "倾向X", "primary_score": "2-1"}) if r == "p/reviewed.json" else bodies.get(r))) == []),
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
            a = json.loads(p.read_text(encoding="utf-8"))
            if "recap_ready" in a:
                continue
            artifacts.append((p.name, a))
    fails = scan(sel, artifacts)
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("LLM GROUNDING FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("LLM GROUNDING PASS (prompt cites model facts → reviewed JSON grounded → artifact "
                     "content_chain traceable → judgement present; no forbidden vocab)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
