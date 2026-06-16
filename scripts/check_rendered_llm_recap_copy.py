#!/usr/bin/env python3
"""
P4R Phase 3 — RENDERED LLM-recap-copy guard. Inspects the rendered /recap DOM and fails if the recap
page renders static/fallback copy, mislabels an observation as a full recap, or fakes events.

For each finished tracked fixture (recap_queue), dump /recap/<id> and fail if:
  - the observation/recap judgment is not rendered (assessment/deviation);
  - predicted-vs-actual is not rendered;
  - correction / next-match hook is missing;
  - share line is missing;
  - a fabricated event claim appears (第N分钟…进球/破门/红牌/点球) with no event source;
  - OBSERVATION-only fixture is presented as a full recap (no observation label).
Usage: check_rendered_llm_recap_copy.py [--base-url URL] | --selftest
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _rendered_dom import dump_dom  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
FAKE_EVENT = re.compile(r"第\s*\d{1,3}\s*分钟.*(进球|破门|红牌|点球)")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _observation(fk):
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a and (a.get("id") == fk or a.get("fixture_key") == fk):
            return a
    return None


def scan(dom, obs):
    fails = []
    zh = (obs.get("i18n") or {}).get("zh") or {}
    # judgment + predicted-vs-actual + deviation + next hook + share
    if zh.get("assessment") and zh["assessment"][:8] not in dom:
        fails.append("recap judgment (assessment) not rendered")
    if not (zh.get("pre_match_call", "")[:8] in dom and (zh.get("actual_line", "")[:6] in dom)):
        fails.append("predicted-vs-actual not rendered")
    if zh.get("deviation") and zh["deviation"][:6] not in dom:
        fails.append("deviation (what-missed) not rendered")
    if zh.get("next_impact") and zh["next_impact"][:6] not in dom:
        fails.append("next-match hook / correction not rendered")
    if not any(m in dom for m in ("分享", "复制", "Share")):
        fails.append("recap share line not rendered")
    # observation must be labelled (not passed off as a full recap)
    if obs.get("recap_ready") is False and not any(m in dom for m in ("赛后观察", "赛后校准", "观察", "完整复盘确认后开放", "Observation")):
        fails.append("observation-only recap not labelled as observation (looks like a full recap)")
    if FAKE_EVENT.search(dom):
        fails.append("fabricated match event rendered without an event source")
    return fails


def selftest():
    obs = {"recap_ready": False, "i18n": {"zh": {"assessment": "结果判断：比分区间命中", "pre_match_call": "赛前主推：偏向巴西",
            "actual_line": "实际比分：1-1", "deviation": "偏差原因：巴西控制力不足", "next_impact": "下一场影响：下调确定性"}}}
    dom_ok = "昨日主推回执 赛前主推：偏向巴西 实际比分：1-1 结果判断：比分区间命中 偏差原因：巴西控制力不足 下一场影响：下调确定性 赛后观察 复制观察链接"
    dom_fake = dom_ok + " 第 23 分钟 进球"
    checks = [
        ("good recap renders", scan(dom_ok, obs) == []),
        ("fabricated event caught", any("fabricated match event" in x for x in scan(dom_fake, obs))),
        ("missing deviation caught", any("deviation" in x for x in scan(dom_ok.replace("偏差原因：巴西控制力不足", ""), obs))),
        ("missing observation label caught", any("not labelled as observation" in x for x in scan("赛前主推：偏向巴西 实际比分：1-1 结果判断：比分区间命中 偏差原因：巴西控制力不足 下一场影响：下调确定性 复制", obs))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    base = argv[argv.index("--base-url") + 1] if "--base-url" in argv else "https://worldcup2026-izid.onrender.com"
    q = _load(QUEUE) or {}
    fails, checked = [], 0
    for rq in q.get("recap_queue", []):
        fk = str(rq.get("fixture_key"))
        obs = _observation(fk)
        if not obs:
            continue  # no observation artifact (e.g. full-recap-only or pending) — covered by other guards
        dom = dump_dom(base.rstrip("/") + "/recap/%s?lang=zh" % fk)
        if not dom:
            fails.append("could not render /recap/%s" % fk); continue
        checked += 1
        fails += ["[%s] %s" % (fk, x) for x in scan(dom, obs)]
    if checked == 0:
        print("WARN  no observation recap pages to render (no bundled observation artifacts) — skipping")
        print("RENDERED LLM RECAP COPY PASS (nothing to verify)"); return 0
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("RENDERED LLM RECAP COPY FAIL — %d issue(s)" % len(fails)); return 1
    print("RENDERED LLM RECAP COPY PASS (%d page(s): judgment + predicted-vs-actual + deviation + hook + share; "
          "observation labelled; no fake events)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
