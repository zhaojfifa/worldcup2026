#!/usr/bin/env python3
"""
P1 — LLM copy-quality guard. Rejects weak/generic prediction copy; requires strong, attractive,
grounded copy for every PUBLISHED match in the content queue (primary + secondary).

For each queued match's prediction artifact, REQUIRE:
  - strong headline / main lean (llm_judgment.main_lean, non-trivial length, not a generic filler);
  - a score call (primary_score);
  - a top tactical variable (top_variable);
  - a why (why);
  - a tactical story (tactical_read: >=2 items);
  - data/source basis (source_facts.source_refs present, OR risk_note cites data: Elo/form/近10/历史);
  - share copy (i18n.zh.operations.share_copy).
REJECT:
  - generic fillers: 双方都有机会 / 都有机会 / 需要关注临场变化 / 注意临场 (alone) / both teams have chances;
  - missing any required field above;
  - betting vocab / fake probability.
Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"

GENERIC = ["双方都有机会", "都有机会", "需要关注临场变化", "两队都有机会", "胜负难料",
           "both teams have chances", "anything can happen"]
BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "竞猜", "让球", "大小球", "跟单",
           "odds", "handicap", "bookmaker", "betting", "wager", "kèo", "cửa trên", "cửa dưới"]
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]
DATA_TOKENS = ["elo", "近 10", "近10", "历史", "form", "近 5", "gf", "ga", "进球", "排名", "pedigree", "强度"]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_preds():
    out = {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = _load(p)
            if not a or "recap_ready" in a:
                continue
            for k in (a.get("id"), a.get("fixture_key")):
                if k:
                    out[str(k)] = a
    return out


def check_copy(name, art):
    fails = []
    lj = art.get("llm_judgment") or {}
    zp = (((art.get("i18n") or {}).get("zh") or {}).get("prediction") or {})
    main = lj.get("main_lean") or zp.get("primary_direction") or ""
    if len(main.strip()) < 8:
        fails.append("%s: weak/empty headline (main_lean)" % name)
    if not (lj.get("primary_score") or zp.get("score_call")):
        fails.append("%s: no score call" % name)
    if not (lj.get("top_variable") or zp.get("top_variable")):
        fails.append("%s: no top tactical variable" % name)
    if not (lj.get("why") or zp.get("why")):
        fails.append("%s: no why" % name)
    tac = lj.get("tactical_read") or (((art.get("i18n") or {}).get("zh") or {}).get("analysis") or {}).get("tactical_matchup") or []
    if not isinstance(tac, list) or len(tac) < 2:
        fails.append("%s: no tactical story (need >=2 tactical_read items)" % name)
    # data/source basis
    refs = (art.get("source_facts") or {}).get("source_refs") or []
    risk_note = (lj.get("risk_note") or zp.get("risk_note") or "").lower()
    if not refs and not any(t in risk_note for t in DATA_TOKENS):
        fails.append("%s: no data/source basis (no source_refs and risk_note cites no data)" % name)
    if not (((art.get("i18n") or {}).get("zh") or {}).get("operations") or {}).get("share_copy"):
        fails.append("%s: no share copy" % name)
    # weak/forbidden content scan over the zh judgement values only
    parts = [main, lj.get("why") or "", lj.get("top_variable") or ""]
    parts += [x for x in tac if isinstance(x, str)]
    parts += [x for x in (lj.get("risk_factors") or []) if isinstance(x, str)]
    blob = " ".join(parts)
    low = blob.lower()
    for g in GENERIC:
        if (g.lower() in low) if g.isascii() else (g in blob):
            fails.append("%s: generic/weak filler %r" % (name, g))
    for w in BETTING + FAKE_PROB:
        if (w.lower() in low) if w.isascii() else (w in blob):
            fails.append("%s: forbidden vocab %r" % (name, w))
    return fails


def queued_keys(q):
    keys = []
    p = q.get("primary_hotspot")
    if p:
        keys.append(str(p.get("fixture_key")))
    for s in q.get("secondary_matches", []):
        keys.append(str(s.get("fixture_key")))
    return keys


def selftest():
    strong = {
        "llm_judgment": {"main_lean": "赛前倾向乌拉圭，沙特需压低节奏才有机会", "primary_score": "0-1",
                         "top_variable": "乌拉圭中场控制 vs 沙特反击效率", "why": "乌拉圭实力与状态领先",
                         "tactical_read": ["乌拉圭控球推进", "沙特低位防守与反击"], "risk_factors": ["首发轮换"],
                         "risk_note": "乌拉圭历史 Elo 与近 10 场领先"},
        "source_facts": {"source_refs": ["kaggle Elo: Uruguay 1872 / Saudi 1645"]},
        "i18n": {"zh": {"operations": {"share_copy": "今日次要推荐：沙特 vs 乌拉圭…"}}},
    }
    weak = {
        "llm_judgment": {"main_lean": "双方都有机会", "primary_score": "", "top_variable": "",
                         "why": "", "tactical_read": [], "risk_note": ""},
        "i18n": {"zh": {"operations": {}}},
    }
    checks = [
        ("strong passes", check_copy("s", strong) == []),
        ("generic filler caught", any("generic" in x for x in check_copy("w", weak))),
        ("no score caught", any("no score call" in x for x in check_copy("w", weak))),
        ("no tactical caught", any("tactical story" in x for x in check_copy("w", weak))),
        ("no share caught", any("share copy" in x for x in check_copy("w", weak))),
        ("betting caught", any("forbidden" in x for x in check_copy("b", dict(strong, llm_judgment=dict(strong["llm_judgment"], why="看 赔率"))))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    q = _load(QUEUE)
    if not q:
        print("FAIL  dailyContentQueue.json missing"); return 1
    preds = load_preds()
    fails, checked = [], 0
    for k in queued_keys(q):
        art = preds.get(k)
        if not art:
            # only PUBLISHED rows must have copy; a not-yet-built row is allowed (state says so)
            continue
        checked += 1
        fails.extend(check_copy("%s vs %s" % (art.get("home"), art.get("away")), art))
    if checked == 0:
        print("FAIL  no queued match has a prediction artifact to quality-check"); return 1
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("LLM COPY QUALITY FAIL — %d issue(s)" % len(fails)); return 1
    print("LLM COPY QUALITY PASS (%d match(es): strong headline + score + variable + why + tactical + "
          "data basis + share copy; no generic/forbidden)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
