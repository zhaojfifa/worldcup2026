#!/usr/bin/env python3
"""
P1B — Auto-LLM prediction-draft generator (provider abstraction; operator stays the approval gate).

Moves the daily loop from operator_manual reviewed JSON toward:
  prediction artifact (model_fields, source coverage) → STRONG prompt → LLM DRAFT (generated/)
                     → guard check → operator review → reviewed/ → artifact build (existing apply)

HARD RULES (unchanged): the generated draft NEVER publishes directly — it lands in
docs/data_audit/mvp2_predictions/generated/ with status GENERATED/GUARD_PASSED/NEEDS_REVIEW; the
operator must still produce the reviewed JSON before `mvp2_build_daily_prediction_artifact.py apply`
writes the artifact. No auto-publish, no auto-send. win_prob/confidence stay null; no betting vocab;
no fake event claims. recap_seed is generated (links the pre-match call to the eventual recap).

Modes:
  generate --date YYYYMMDD --fixture-key KEY [--provider deepseek|gemini|kimi] [--live]
           --live calls the provider (key from env / backend/.env, never printed/committed);
           without --live runs DRY-RUN: a deterministic, model-grounded draft (offline, no network).
  --selftest
Secrets: keys are read from the environment (optionally hydrated from backend/.env); never logged.
"""
import argparse
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
GEN_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "generated"
ENV_FILE = ROOT / "backend" / ".env"

PROVIDERS = {
    "deepseek": {"env": "DEEPSEEK_API_KEY", "url": "https://api.deepseek.com/chat/completions", "model": "deepseek-chat"},
    "gemini":   {"env": "GEMINI_API_KEY", "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", "model": "gemini-2.0-flash"},
    "kimi":     {"env": "KIMI_API_KEY", "url": "https://api.moonshot.cn/v1/chat/completions", "model": "moonshot-v1-8k"},
}
TIMEOUT_S = 60
RETRIES = 2
REQUIRED_OUT = ["strong_headline", "main_lean", "primary_score", "backup_scores", "risk_level",
                "top_variable", "why", "tactical_beats", "data_source_basis", "external_expectation_safe",
                "t30_checklist", "homepage_short", "predict_medium", "share_copy", "recap_seed", "safety_flags"]
BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "竞猜", "让球", "大小球", "跟单", "odds", "handicap",
           "bookmaker", "betting", "wager", "kèo", "cửa trên", "cửa dưới", "稳赢", "必胜", "chắc thắng"]
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _hydrate_env():
    """Load provider keys from backend/.env into os.environ if not already set (local dev only)."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z0-9_]+)=(.*)$", line.strip())
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2)


def find_artifact(fixture_key):
    if not PRED_DIR.exists():
        return None, None
    for p in sorted(PRED_DIR.glob("*.json")):
        a = _load(p)
        if not a or "recap_ready" in a:
            continue
        if a.get("fixture_key") == fixture_key or (a.get("id") and a["id"] == fixture_key):
            return p, a
    return None, None


def strong_prompt(art, role):
    mf = art.get("model_fields") or {}
    sf = art.get("source_facts") or {}
    refs = "; ".join(sf.get("source_refs") or []) or "(no computed refs — operator_estimated)"
    return f"""You are 俅哥, a sharp football-intelligence persona. Produce an ATTRACTIVE, sharp, grounded
PRE-MATCH read for {art.get('home')} vs {art.get('away')} (role: {role}).

FACTS (engineering-provided; do not contradict):
- model_fields.source: {mf.get('source')}  | source coverage: {sf.get('data_mode')}
- recommended_score: {mf.get('recommended_score')}  | backup: {mf.get('backup_scores')}
- risk_level: {mf.get('risk_level')}
- data/source basis: {refs}
- UNAVAILABLE / DO NOT INVENT: win_prob, numeric confidence; no fake player events.

STRONG COPY REQUIREMENTS: a confident directional headline; the score call; a top tactical variable;
a why; >=2 tactical beats; cite the data basis; SAFE external expectation (public tendency / heat /
upset variable — never odds); a 5-item T-30 checklist; a recap_seed (one line linking the pre-match
call to what the post-match recap should verify).
FORBIDDEN: odds/handicap/盘口/赔率/投注/让球/betting/kèo; win-rate/胜率/命中率; win-guarantee (稳赢/必胜/
chắc thắng). NO fake win probability or numeric confidence.

Return EXACTLY this JSON (zh canonical):
{{"strong_headline":"","main_lean":"","primary_score":"{mf.get('recommended_score') or ''}",
 "backup_scores":{json.dumps(mf.get('backup_scores') or [], ensure_ascii=False)},"risk_level":"{mf.get('risk_level') or ''}",
 "top_variable":"","why":"","tactical_beats":["",""],"data_source_basis":"",
 "external_expectation_safe":["公开预测倾向…","热度集中…","冷门变量…"],
 "t30_checklist":["首发阵容与位置","阵型与三/四后卫选择","核心球员状态与热身","临场热度与风险方向","开球前再确认方向"],
 "homepage_short":"","predict_medium":"","share_copy":"","recap_seed":"",
 "safety_flags":{{"no_betting_vocab":true,"no_fake_probability":true,"no_fake_events":true,"no_auto_send":true}}}}"""


def dry_run_draft(art, role):
    """Deterministic, model-grounded draft (offline). Strong + compliant; passes the copy guard.
    This is a DRAFT for operator review — NOT an auto-published artifact."""
    mf = art.get("model_fields") or {}
    sf = art.get("source_facts") or {}
    home, away = art.get("home"), art.get("away")
    score = mf.get("recommended_score") or "待定"
    backups = mf.get("backup_scores") or []
    risk = mf.get("risk_level") or "中"
    refs = sf.get("source_refs") or []
    basis = refs[0] if refs else ("数据来源：%s（操作组估计，无完整历史模型覆盖）" % (sf.get("data_mode") or "manual"))
    # lean toward the team implied by the score (home-away); honest about cold-start
    try:
        h, a = [int(x) for x in re.findall(r"\d+", score)[:2]]
        fav = home if h > a else away if a > h else None
    except Exception:
        fav = None
    lean = ("赛前倾向%s，但对手具备压低比分/反击的能力" % fav) if fav else "赛前势均力敌，方向待临场确认"
    estimated = (mf.get("source") != "computed")
    why = ("%s在历史强度与近况上更稳，但对手的防守与反击会压缩比分空间。" % (fav or "强队")) + \
          ("（注：对手数据冷启动，倾向为操作组估计，非完整模型。）" if estimated else "")
    return {
        "strong_headline": "%s vs %s：俅哥主看 %s，%s" % (home, away, score, ("偏向%s" % fav) if fav else "方向待定"),
        "main_lean": lean,
        "primary_score": mf.get("recommended_score"),
        "backup_scores": backups,
        "risk_level": risk,
        "top_variable": "%s能否压低节奏 + %s的进攻终结效率" % (away if fav == home else home, fav or home),
        "why": why,
        "tactical_beats": [
            "%s控球推进与边中结合，关注能否打穿对手低位防线" % (fav or home),
            "对手低位防守加一侧反击，关注反击落点与定位球威胁",
            "比分走向取决于首粒进球时间与体能保持",
        ],
        "data_source_basis": basis,
        "external_expectation_safe": [
            "公开预测倾向偏向%s" % (fav or "强队"),
            "热度集中在%s取胜" % (fav or "热门"),
            "冷门变量主要在对手压低比分或偷袭得手",
        ],
        "t30_checklist": ["首发阵容与位置", "阵型与三/四后卫选择", "核心球员状态与热身", "临场热度与风险方向",
                          "开球前再确认方向，必要时下调把握度"],
        "homepage_short": "%s vs %s · 俅哥主看 %s，冷门风险%s" % (home, away, score, risk),
        "predict_medium": "%s。主比分参考 %s，备选 %s。%s" % (lean, score, " / ".join(backups) or "—", why),
        "share_copy": "今日%s：%s vs %s。俅哥主看：%s。主比分 %s，备选 %s，冷门风险%s。%s。开球前 30 分钟看首发与临场修正，进群等修正。"
                      % ("主推" if role == "primary" else "次要推荐", home, away, lean, score, " / ".join(backups) or "—", risk, basis),
        "recap_seed": "赛后核对：主推%s是否兑现、实际比分与 %s 的偏差、对手反击质量是否高于赛前判断。" % (score, score),
        "safety_flags": {"no_betting_vocab": True, "no_fake_probability": True, "no_fake_events": True, "no_auto_send": True},
    }


def _call_provider(provider, prompt):
    import httpx
    cfg = PROVIDERS[provider]
    key = os.environ.get(cfg["env"])
    if not key:
        raise SystemExit("provider %s key (%s) not in env — set it or run dry-run" % (provider, cfg["env"]))
    last = None
    for _ in range(RETRIES + 1):
        try:
            if provider == "gemini":
                r = httpx.post(cfg["url"] + "?key=" + key, timeout=TIMEOUT_S,
                               json={"contents": [{"parts": [{"text": prompt}]}],
                                     "generationConfig": {"temperature": 0.6, "responseMimeType": "application/json"}})
                r.raise_for_status()
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                r = httpx.post(cfg["url"], timeout=TIMEOUT_S,
                               headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
                               json={"model": cfg["model"], "temperature": 0.6,
                                     "response_format": {"type": "json_object"},
                                     "messages": [{"role": "user", "content": prompt}]})
                r.raise_for_status()
                txt = r.json()["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", txt, re.S)
            return json.loads(m.group(0) if m else txt)
        except Exception as e:  # noqa: BLE001
            last = e
    raise SystemExit("provider %s call failed after retries: %s" % (provider, type(last).__name__))


def guard_draft(d):
    """Inline guard for the generated draft → returns (status, issues)."""
    issues = []
    for k in REQUIRED_OUT:
        if k not in d or (isinstance(d[k], str) and not d[k].strip()):
            issues.append("missing/empty %s" % k)
    if isinstance(d.get("tactical_beats"), list) and len(d["tactical_beats"]) < 2:
        issues.append("tactical_beats < 2")
    if d.get("primary_score") in (None, ""):
        issues.append("no primary_score")
    if not d.get("recap_seed"):
        issues.append("no recap_seed")
    # vocab over string values only
    vals = []
    def collect(x):
        if isinstance(x, str):
            vals.append(x)
        elif isinstance(x, list):
            [collect(i) for i in x]
        elif isinstance(x, dict):
            [collect(v) for v in x.values()]
    collect({k: v for k, v in d.items() if k != "safety_flags"})
    blob = " ".join(vals); low = blob.lower()
    for w in BETTING + FAKE_PROB:
        if (w.lower() in low) if w.isascii() else (w in blob):
            issues.append("forbidden vocab %r" % w)
    if "win_prob" in d or any(isinstance(d.get(k), (int, float)) for k in ("confidence",)):
        issues.append("draft carries a probability/confidence value")
    status = "GUARD_PASSED" if not issues else "NEEDS_REVIEW"
    return status, issues


def cmd_generate(date, fixture_key, provider, live, role):
    _hydrate_env()
    path, art = find_artifact(fixture_key)
    if not art:
        print("FAIL  no prediction artifact for %r" % fixture_key); return 1
    role = role or "primary"
    if live:
        draft = _call_provider(provider, strong_prompt(art, role))
        used = provider
    else:
        draft = dry_run_draft(art, role)
        used = "dry-run(offline, model-grounded)"
    status, issues = guard_draft(draft)
    out = {
        "date": date, "fixture_key": fixture_key, "home": art.get("home"), "away": art.get("away"),
        "role": role, "provider": used, "mode": "live" if live else "dry-run",
        "status": status, "guard_issues": issues,
        "model_source": (art.get("model_fields") or {}).get("source"),
        "draft": draft,
        "_note": "GENERATED draft for OPERATOR REVIEW only — NOT published. Operator must copy/edit into "
                 "docs/data_audit/mvp2_predictions/reviewed/%s_%s_reviewed.json then run "
                 "mvp2_build_daily_prediction_artifact.py apply. No auto-publish, no auto-send." % (date, fixture_key),
    }
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    gp = GEN_DIR / ("%s_%s_generated.json" % (date, fixture_key))
    gp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK    generated draft (%s) status=%s → %s" % (used, status, gp.relative_to(ROOT)))
    if issues:
        for i in issues:
            print("      NEEDS_REVIEW: %s" % i)
    return 0


def selftest():
    sample = {"home": "Belgium", "away": "Egypt",
              "model_fields": {"source": "computed", "recommended_score": "1-0", "backup_scores": ["2-0", "1-1"], "risk_level": "中"},
              "source_facts": {"data_mode": "api", "source_refs": ["kaggle Elo: Belgium 1885 / Egypt 1756 (gap 129)"]}}
    d = dry_run_draft(sample, "primary")
    st, iss = guard_draft(d)
    bad = dict(d, share_copy="看 赔率", recap_seed="")
    st2, iss2 = guard_draft(bad)
    checks = [
        ("dry-run draft has all required fields", all(k in d for k in REQUIRED_OUT)),
        ("dry-run draft guard-passes", st == "GUARD_PASSED" and not iss),
        ("recap_seed present", bool(d.get("recap_seed"))),
        ("primary_score grounded in model_fields", d["primary_score"] == "1-0"),
        ("forbidden vocab caught", any("forbidden" in x for x in iss2)),
        ("missing recap_seed caught", any("recap_seed" in x for x in iss2)),
        ("no probability in draft", "win_prob" not in d and not isinstance(d.get("confidence"), (int, float))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["generate"])
    ap.add_argument("--date", default="00000000")
    ap.add_argument("--fixture-key", default="")
    ap.add_argument("--provider", default="deepseek", choices=list(PROVIDERS))
    ap.add_argument("--role", default="primary", choices=["primary", "secondary"])
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd == "generate":
        if not a.fixture_key:
            print("FAIL  generate requires --fixture-key"); return 1
        return cmd_generate(a.date, a.fixture_key, a.provider, a.live, a.role)
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
