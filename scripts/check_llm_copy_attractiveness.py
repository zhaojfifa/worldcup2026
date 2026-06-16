#!/usr/bin/env python3
"""
P4C — LLM copy-attractiveness guard. Product-grade copy, not engineering filler.

Prediction copy (each queued primary/secondary artifact, zh) must have: strong headline (main lean,
non-trivial), exact score call, primary reason (why), hidden risk (risk_note/risk_variables), tactical
variable (top_variable), short share line (operations.share_copy), source basis (source_refs OR
risk_note cites data).
Recap/observation copy (each observation artifact, zh) must have: hit/miss judgment (assessment),
predicted vs actual (pre_match_call + actual_line), deviation (what missed), correction (next_impact),
share line (share_copy).

REJECT: generic filler (双方都有机会 / 需要关注临场变化 / 胜负难料), a weak "可能…激烈/胶着" with NO reason
nearby, fake certainty (必胜/稳赢/100%/包赢), betting language, fake confidence (胜率/命中率/具体置信度),
fake event claims (第N分钟…进球 in a PRE-match field), missing score call, missing risk, missing share line.
Usage: check_llm_copy_attractiveness.py | --selftest.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"

GENERIC = ["双方都有机会", "都有机会", "需要关注临场变化", "胜负难料", "两队都有机会", "都有一定机会"]
FAKE_CERT = ["必胜", "稳赢", "包赢", "100%", "必中"]
BETTING = ["赔率", "盘口", "下注", "投注", "让球", "大小球", "跟单", "odds", "handicap", "betting", "kèo"]
FAKE_PROB = ["胜率", "命中率", "win rate", "tỷ lệ thắng"]
DATA_TOKENS = ["elo", "近 10", "近10", "历史", "form", "进球", "排名", "强度", "防守", "反击", "控球", "节奏", "状态"]
WEAK = ["激烈", "胶着", "焦灼"]
FAKE_EVENT = re.compile(r"第\s*\d{1,3}\s*分钟.*(进球|破门|红牌|点球)")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _vocab(name, text, kinds):
    out = []
    low = (text or "").lower()
    for label, terms in kinds:
        for w in terms:
            if (w.lower() in low) if w.isascii() else (w in (text or "")):
                out.append("%s: %s vocab %r" % (name, label, w))
    return out


def check_prediction(name, art):
    fails = []
    zh = (art.get("i18n") or {}).get("zh") or {}
    pred, ana, ops = zh.get("prediction") or {}, zh.get("analysis") or {}, zh.get("operations") or {}
    lj = art.get("llm_judgment") or {}
    headline = lj.get("main_lean") or pred.get("primary_direction") or ""
    if len(headline.strip()) < 8:
        fails.append("%s: weak/empty headline" % name)
    if not (lj.get("primary_score") or pred.get("score_call")):
        fails.append("%s: missing exact score call" % name)
    if not (lj.get("why") or pred.get("why")):
        fails.append("%s: missing primary reason (why)" % name)
    if not (lj.get("risk_note") or pred.get("risk_note") or ana.get("risk_variables")):
        fails.append("%s: missing hidden risk" % name)
    if not (lj.get("top_variable") or pred.get("top_variable")):
        fails.append("%s: missing tactical variable" % name)
    if not ops.get("share_copy"):
        fails.append("%s: missing share line" % name)
    refs = (art.get("source_facts") or {}).get("source_refs") or []
    risk_note = (lj.get("risk_note") or pred.get("risk_note") or "")
    if not refs and not any(t in risk_note.lower() for t in DATA_TOKENS):
        fails.append("%s: missing source basis (no source_refs and risk_note cites no data)" % name)
    # weak-phrase-without-reason: a WEAK word present but no data token in the same field
    for field in (headline, lj.get("why") or pred.get("why") or ""):
        if any(w in field for w in WEAK) and not any(t in field.lower() for t in DATA_TOKENS):
            fails.append("%s: weak phrase without a reason (%r)" % (name, field[:24]))
    blob = " ".join([headline, lj.get("why") or "", risk_note] + (lj.get("tactical_read") or []))
    fails += _vocab(name, blob, [("generic-filler", GENERIC), ("fake-certainty", FAKE_CERT),
                                 ("betting", BETTING), ("fake-probability", FAKE_PROB)])
    if FAKE_EVENT.search(blob):
        fails.append("%s: fabricated pre-match event claim" % name)
    return fails


def check_recap(name, obs):
    fails = []
    zh = (obs.get("i18n") or {}).get("zh") or {}
    if not zh.get("assessment"):
        fails.append("%s: recap missing hit/miss judgment (assessment)" % name)
    if not (zh.get("pre_match_call") and zh.get("actual_line")):
        fails.append("%s: recap missing predicted-vs-actual" % name)
    if not zh.get("deviation"):
        fails.append("%s: recap missing what-missed (deviation)" % name)
    if not zh.get("next_impact"):
        fails.append("%s: recap missing correction/next hook" % name)
    if not zh.get("share_copy"):
        fails.append("%s: recap missing share line" % name)
    blob = " ".join(str(v) for v in zh.values() if isinstance(v, str))
    fails += _vocab(name, blob, [("fake-certainty", FAKE_CERT), ("betting", BETTING), ("fake-probability", FAKE_PROB)])
    return fails


def selftest():
    strong = {"i18n": {"zh": {"prediction": {"primary_direction": "赛前倾向乌拉圭，沙特需压低节奏才有机会",
              "score_call": "0-1", "why": "乌拉圭历史 Elo 与近 10 场领先", "risk_note": "沙特反击有威胁",
              "top_variable": "中场控制"}, "analysis": {"risk_variables": ["首发"]},
              "operations": {"share_copy": "今日次推：沙特 vs 乌拉圭…"}}},
              "source_facts": {"source_refs": ["kaggle Elo"]}, "llm_judgment": {}}
    weak = {"i18n": {"zh": {"prediction": {"primary_direction": "双方都有机会", "score_call": "",
            "why": "可能会比较激烈", "risk_note": "", "top_variable": ""},
            "analysis": {}, "operations": {}}}, "source_facts": {}, "llm_judgment": {}}
    obs_ok = {"i18n": {"zh": {"assessment": "部分命中", "pre_match_call": "主推 2-1", "actual_line": "实际 1-1",
              "deviation": "控制力不足", "next_impact": "下调确定性", "share_copy": "x"}}}
    checks = [
        ("strong prediction passes", check_prediction("s", strong) == []),
        ("generic filler caught", any("generic" in x for x in check_prediction("w", weak))),
        ("missing score caught", any("score call" in x for x in check_prediction("w", weak))),
        ("weak-without-reason caught", any("weak phrase" in x for x in check_prediction("w", weak))),
        ("missing share caught", any("share line" in x for x in check_prediction("w", weak))),
        ("good recap passes", check_recap("r", obs_ok) == []),
        ("recap missing deviation caught", any("what-missed" in x for x in check_recap("r", {"i18n": {"zh": {"assessment": "x", "pre_match_call": "a", "actual_line": "b", "next_impact": "c", "share_copy": "d"}}}))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    q = _load(QUEUE) or {}
    keys = ([(q.get("primary_hotspot") or {}).get("fixture_key")] +
            [s.get("fixture_key") for s in q.get("secondary_matches", [])])
    keys = [str(k) for k in keys if k]
    preds, obs = {}, {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = _load(p)
            if not a:
                continue
            (obs if "recap_ready" in a else preds)[p.name] = a
    fails, checked = [], 0
    for name, a in preds.items():
        if str(a.get("fixture_key")) in keys or str(a.get("id")) in keys:
            checked += 1
            fails += check_prediction("%s vs %s" % (a.get("home"), a.get("away")), a)
    for name, a in obs.items():
        checked += 1
        fails += check_recap("%s vs %s (recap)" % (a.get("home"), a.get("away")), a)
    if checked == 0:
        print("FAIL  nothing to check"); return 1
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("LLM COPY ATTRACTIVENESS FAIL — %d issue(s)" % len(fails)); return 1
    print("LLM COPY ATTRACTIVENESS PASS (%d artifact(s): strong headline + score + reason + risk + "
          "variable + share + source basis; recap has judgment/deviation/correction; no filler/fake/betting)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
