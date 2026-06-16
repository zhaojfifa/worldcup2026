#!/usr/bin/env python3
"""
R1 P0 — Daily prediction artifact builder (Owner 2026-06-15: content production chain FIRST).

Recovers the original content mechanism as a runnable chain WITHOUT auto-calling any LLM:

  selected_hotspot → model/source lookup → source_facts/model_fields → LLM prompt file
                   → (operator pastes to DeepSeek/Gemini/Kimi MANUALLY) → reviewed JSON
                   → prediction artifact (llm_judgment + content_chain) → homepage/predict/internal

Subcommands:
  prompt  --date YYYYMMDD [--fixture-key KEY]
          model-lookup + (re)write source_facts/model_fields on the artifact, then emit the LLM
          prompt to docs/data_audit/mvp2_predictions/prompts/<date>_<slug>_prompt.md.
  apply   --date YYYYMMDD [--fixture-key KEY] --reviewed <file.json>
          validate a reviewed LLM/operator JSON and merge it into the artifact's llm_judgment +
          content_chain (reviewed_applied=true).
  --selftest

HARD RULES: never calls an external LLM; never invents win_prob / numeric confidence (they stay
null); never fabricates a probability; no betting/trading vocabulary; no auto-send. When the model
lookup fails (e.g. an id=null manual fixture with no frame), model_fields.source = operator_estimated
and /internal/daily says so.
"""
import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
FALLBACK_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"
PROMPT_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "prompts"
REVIEWED_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "reviewed"

BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "竞猜", "让球", "大小球", "跟单", "串关",
           "odds", "handicap", "bookmaker", "wager", "betting",
           "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược"]
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]
REVIEWED_KEYS = ["main_lean", "primary_score", "backup_scores", "risk_level", "risk_note",
                 "top_variable", "why", "tactical_read", "risk_factors", "external_expectation",
                 "t30_checklist", "share_copy"]


def slug(key: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", key)


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_artifact_path(fixture_key):
    if not PRED_DIR.exists():
        return None
    for p in sorted(PRED_DIR.glob("*.json")):
        try:
            a = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "recap_ready" in a:   # observation artifact — skip
            continue
        if a.get("fixture_key") == fixture_key:
            return p
    return None


def fixture_facts(fixture_key, artifact):
    """Resolve home/away/kickoff/status — prefer the runtime manifest, fall back to the artifact."""
    facts = {"home": artifact.get("home"), "away": artifact.get("away"),
             "kickoffUtc": artifact.get("kickoffUtc"), "status": artifact.get("status"),
             "fixture_source": "manual_slate"}
    man = _load(MANIFEST) or _load(FALLBACK_MANIFEST)
    if man:
        for f in man.get("fixtures", []):
            if (f.get("id") or f.get("external_game_id")) == fixture_key:
                facts["home"] = f.get("home") or facts["home"]
                facts["away"] = f.get("away") or facts["away"]
                facts["kickoffUtc"] = f.get("kickoffUtc") or facts["kickoffUtc"]
                facts["status"] = f.get("status") or facts["status"]
                facts["fixture_source"] = "api_football" if f.get("id") else "manual_slate"
                break
    return facts


_SS = None


def _scoutscore():
    """Lazy-import the ScoutScore v0.2 builder (offline kaggle Elo/form/Poisson). None if unavailable."""
    global _SS
    if _SS is None:
        try:
            spec = importlib.util.spec_from_file_location(
                "mvp2_scoutscore", ROOT / "scripts" / "mvp2_build_scoutscore_v0_2_factors.py")
            mod = importlib.util.module_from_spec(spec)
            sys.modules["mvp2_scoutscore"] = mod
            spec.loader.exec_module(mod)
            mod.load_results()  # verify kaggle present
            _SS = mod
        except BaseException:
            _SS = False
    return _SS or None


def model_lookup(fixture_key, artifact, cutoff=None):
    """OFFLINE model/source lookup (R2 — real ScoutScore). Compute kaggle Elo + last-10 form + Poisson
    band + upset_band for the fixture's teams. Both teams resolve in kaggle → source='computed' with
    source_refs. A cold-start team (Elo None) or no kaggle → 'unavailable' (builder then uses
    operator_estimated, disclosed). NEVER returns win_prob / numeric confidence (compliance floor)."""
    home, away = artifact.get("home"), artifact.get("away")
    ss = _scoutscore()
    if not ss or not home or not away:
        return {"result": "unavailable",
                "note": "no offline model source available — operator_estimated fields used"}
    try:
        rows = ss.load_results()
        cut = cutoff or "2026-12-31"
        elo = ss.elo_snapshot(rows, cut)
        eh, ea = elo.get(ss.kname(home)), elo.get(ss.kname(away))
        if eh is None or ea is None:
            cold = home if eh is None else away
            return {"result": "unavailable",
                    "note": "%s not in the historical dataset (Elo cold-start) — no honest computed model; operator_estimated used" % cold}
        gap = round(eh - ea)
        fh, fa = ss.recent_form(rows, home, cut), ss.recent_form(rows, away, cut)
        band, band_note = ss.upset_band(abs(gap), 0)
        # documented Elo→goal-expectation heuristic (disclosed in source_refs); home carries the gap tilt
        lam_h = max(0.5, min(2.6, 1.35 + gap / 300.0))
        lam_a = max(0.4, min(2.6, 1.15 - gap / 300.0))
        bands = ss.poisson_bands(lam_h, lam_a)
        fav, under = (home, away) if gap >= 0 else (away, home)
        favform = (fh if gap >= 0 else fa)["record"]
        risk_note = ("%s 实力领先（Elo 差 %d，近 10 场 %s），但 %s 防守稳健、具备反击空间，%s。"
                     % (fav, abs(gap), favform, under, band_note))
        return {
            "result": "computed",
            "note": "ScoutScore v0.2 — kaggle Elo + last-10 form + Poisson",
            "fields": {
                "recommended_score": bands[0] if bands else None,
                "backup_scores": bands[1:3] if bands else [],
                "risk_level": {"low": "低", "medium": "中", "high": "高"}.get(band, "中"),
                "risk_note": risk_note,
            },
            "source_refs": [
                "kaggle Elo: %s %.0f / %s %.0f (gap %d)" % (home, eh, away, ea, gap),
                "form10: %s %s GF%d/GA%d · %s %s GF%d/GA%d" % (
                    home, fh["record"], fh["goals_for"], fh["goals_against"],
                    away, fa["record"], fa["goals_for"], fa["goals_against"]),
                "upset_band=%s (%s)" % (band, band_note),
                "poisson_bands(%.2f,%.2f)=%s" % (lam_h, lam_a, "/".join(bands)),
            ],
            "favoured": fav,
        }
    except BaseException as e:
        return {"result": "unavailable", "note": "model lookup error (%s) — operator_estimated used" % type(e).__name__}


def build_source_facts(facts, lookup, model_fields):
    has_model = model_fields.get("source") not in (None, "unavailable")
    missing = [k for k in ("win_prob", "confidence") if model_fields.get(k) is None]
    return {
        "fixture_source": facts["fixture_source"],
        "data_mode": "manual" if facts["fixture_source"] == "manual_slate" else "api",
        "has_model_fields": has_model,
        "source_refs": lookup.get("source_refs", []),
        "missing_fields": missing,
    }


def build_model_fields(artifact, lookup):
    """computed lookup → source='computed' using the ScoutScore fields. Otherwise operator_estimated,
    reusing the operator-confirmed score/risk on the artifact (model_fields or i18n.zh.prediction).
    win_prob/confidence ALWAYS null (no fake probability)."""
    existing = artifact.get("model_fields") or {}
    zp = (((artifact.get("i18n") or {}).get("zh") or {}).get("prediction") or {})
    if lookup["result"] == "computed":
        f = lookup["fields"]
        return {
            "win_prob": None,
            "recommended_score": f["recommended_score"],
            "backup_scores": f["backup_scores"],
            "risk_level": f["risk_level"],
            "risk_note": f["risk_note"],
            "confidence": None,
            "source": "computed",
            "model_status": "scoutscore_v0_2_elo_form",
            "no_fake_probability": True,
        }
    rec = existing.get("recommended_score") or zp.get("score_call")
    backups = existing.get("backup_scores")
    if not backups and zp.get("backup_score"):
        backups = [s.strip() for s in zp["backup_score"].split("/") if s.strip()]
    return {
        "win_prob": None,
        "recommended_score": rec,
        "backup_scores": backups or [],
        "risk_level": existing.get("risk_level") or zp.get("risk_level"),
        "risk_note": existing.get("risk_note") or zp.get("risk_note"),
        "confidence": None,
        "source": "operator_estimated",
        "model_status": "operator_estimated",
        "no_fake_probability": True,
    }


def build_prompt(facts, model_fields, fixture_key):
    mf = model_fields
    avail = mf["source"] != "unavailable"
    score = mf.get("recommended_score") or "（待大模型给出参考区间）"
    risk = mf.get("risk_level") or "（待大模型给出风险等级）"
    missing = ", ".join(facts.get("missing_fields") or ["win_prob", "confidence"])
    ko = facts.get("kickoffUtc") or "TBA / 待确认"
    return f"""# Daily Prediction Prompt · {facts['home']} vs {facts['away']}
<!-- R1 generated. Operator: paste into DeepSeek (default) / Gemini / Kimi MANUALLY, review, then save
     the JSON to docs/data_audit/mvp2_predictions/reviewed/. NO automatic API call. -->

fixture_key: {fixture_key}
kickoff (UTC): {ko}
status: {facts.get('status')}
fixture_source: {facts['fixture_source']}

## Model / source facts (engineering-provided)
- recommended_score: {score}
- risk_level: {risk}
- model_fields.source: {mf['source']}{' (real model values present)' if avail else ' (operator_estimated — no computed model source)'}
- UNAVAILABLE / DO NOT INVENT: {missing}  (win_prob and numeric confidence MUST stay absent — no probability promise)

## Your task (persona voice — zh 俅哥 / vi Tiên Tri / my Oracle; here author the zh canonical)
Produce a pre-match tactical read for the daily hotspot. Reason over: tempo & control, wings &
half-spaces, set-pieces & second balls, lineup/rotation, fitness/schedule, motivation. Use the model
facts above; never invent a win probability or a numeric confidence.

Market / public expectation: SAFE wording ONLY — public tendency / heat focus / upset variable.
FORBIDDEN: odds, handicap, 盘口, 赔率, 投注, 让球, kèo, cửa trên/dưới, betting, bookmaker.

T-30 checklist (5 items): starting XI & positions; formation (3 vs 4 back); key-player status &
warm-up; live heat & risk direction; re-confirm direction before kickoff (lower certainty if needed).

Recap-receipt format (for after full-time, not now): pre-match call → actual score → partial-hit
assessment → deviation reason → calibration points → next-match impact.

## Return EXACTLY this JSON (no extra prose)
```json
{{
  "main_lean": "",
  "primary_score": "{mf.get('recommended_score') or ''}",
  "backup_scores": {json.dumps(mf.get('backup_scores') or [], ensure_ascii=False)},
  "risk_level": "{mf.get('risk_level') or ''}",
  "risk_note": "",
  "top_variable": "",
  "why": "",
  "tactical_read": ["", ""],
  "risk_factors": ["", ""],
  "external_expectation": ["公开预测倾向…", "热度集中…", "冷门变量…"],
  "t30_checklist": ["首发阵容与位置", "阵型与三/四后卫选择", "核心球员状态与热身反馈", "临场热度与风险方向", "开球前再确认方向，必要时下调把握度"],
  "share_copy": "",
  "llm_provider": "deepseek|gemini|kimi|operator_manual",
  "safety": {{ "no_betting_vocab": true, "no_fake_probability": true, "no_auto_send": true }}
}}
```
"""


def validate_reviewed(d):
    errs = []
    if not isinstance(d, dict):
        return ["reviewed JSON is not an object"]
    for k in REVIEWED_KEYS:
        if k not in d:
            errs.append("reviewed JSON missing key %s" % k)
    for lk in ("backup_scores", "tactical_read", "risk_factors", "external_expectation", "t30_checklist"):
        if lk in d and not isinstance(d[lk], list):
            errs.append("reviewed %s must be a list" % lk)
    # Scan ONLY the judgement CONTENT values (never the structural keys like 'no_betting_vocab',
    # which would self-trip the substring match). Collect strings from the content keys.
    parts = []
    for k in REVIEWED_KEYS:
        v = d.get(k)
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(x for x in v if isinstance(x, str))
    blob = " ".join(parts)
    low = blob.lower()
    for w in BETTING:
        if (w.lower() in low) if w.isascii() else (w in blob):
            errs.append("reviewed JSON contains betting/trading vocab %r" % w)
    for w in FAKE_PROB:
        if (w.lower() in low) if w.isascii() else (w in blob):
            errs.append("reviewed JSON contains fake-probability claim %r" % w)
    if "win_prob" in d and d["win_prob"] not in (None, "", "unavailable"):
        errs.append("reviewed JSON must NOT carry a win_prob value (no fake probability)")
    if "confidence" in d and isinstance(d.get("confidence"), (int, float)):
        errs.append("reviewed JSON must NOT carry a numeric confidence")
    saf = d.get("safety") or {}
    if saf.get("no_fake_probability") is not True or saf.get("no_auto_send") is not True:
        errs.append("reviewed JSON safety.no_fake_probability/no_auto_send must be true")
    return errs


def cmd_prompt(date, fixture_key):
    sel = _load(SEL)
    if not fixture_key:
        if not sel or not sel.get("fixture_key"):
            print("FAIL  no selected_hotspot and no --fixture-key"); return 1
        fixture_key = sel["fixture_key"]
    path = find_artifact_path(fixture_key)
    if not path:
        print("FAIL  no prediction artifact for %r (create the artifact first)" % fixture_key); return 1
    art = json.loads(path.read_text(encoding="utf-8"))
    facts = fixture_facts(fixture_key, art)
    # Elo cutoff = the fixture date (YYYYMMDD → YYYY-MM-DD) so the snapshot has no future leakage.
    cutoff = "%s-%s-%s" % (date[0:4], date[4:6], date[6:8]) if len(date) == 8 and date.isdigit() else None
    lookup = model_lookup(fixture_key, art, cutoff)
    mf = build_model_fields(art, lookup)
    facts_with_missing = dict(facts, missing_fields=[k for k in ("win_prob", "confidence") if mf.get(k) is None])
    sf = build_source_facts(facts, lookup, mf)
    art["source_facts"] = sf
    art["model_fields"] = mf
    prompt = build_prompt(facts_with_missing, mf, fixture_key)
    pp = PROMPT_DIR / ("%s_%s_prompt.md" % (date, slug(fixture_key)))
    pp.parent.mkdir(parents=True, exist_ok=True)
    pp.write_text(prompt, encoding="utf-8")
    cc = art.get("content_chain") or {}
    art["content_chain"] = {
        "date": date,
        "model_lookup": lookup["result"],
        "model_lookup_note": lookup["note"],
        "prompt_path": str(pp.relative_to(ROOT)),
        "prompt_generated": True,
        "reviewed_path": cc.get("reviewed_path"),
        "reviewed_applied": bool(cc.get("reviewed_applied")),
        "llm_provider": cc.get("llm_provider") or "pending",
        "built_by": "mvp2_build_daily_prediction_artifact.py",
        "built_at": date,
    }
    _save(path, art)
    print("OK    model_lookup=%s · source=%s · prompt=%s" % (lookup["result"], mf["source"], pp.relative_to(ROOT)))
    print("OK    artifact updated: %s (source_facts + model_fields + content_chain.prompt_generated)" % path.relative_to(ROOT))
    return 0


def cmd_apply(date, fixture_key, reviewed_file):
    sel = _load(SEL)
    if not fixture_key:
        fixture_key = (sel or {}).get("fixture_key")
    path = find_artifact_path(fixture_key) if fixture_key else None
    if not path:
        print("FAIL  no prediction artifact for %r" % fixture_key); return 1
    rp = pathlib.Path(reviewed_file)
    if not rp.is_absolute():
        rp = ROOT / reviewed_file
    rev = _load(rp)
    if rev is None:
        print("FAIL  reviewed file not found: %s" % reviewed_file); return 1
    errs = validate_reviewed(rev)
    if errs:
        for e in errs:
            print("FAIL  %s" % e)
        return 1
    art = json.loads(path.read_text(encoding="utf-8"))
    art["llm_judgment"] = {
        "main_lean": rev["main_lean"], "primary_score": rev.get("primary_score"),
        "backup_scores": rev.get("backup_scores") or [], "top_variable": rev.get("top_variable", ""),
        "why": rev.get("why", ""), "tactical_read": rev.get("tactical_read") or [],
        "risk_factors": rev.get("risk_factors") or [], "external_expectation": rev.get("external_expectation") or [],
        "t30_checklist": rev.get("t30_checklist") or [],
    }
    # P4R copy-wiring fix (Owner 2026-06-16): the RENDERER reads i18n.zh.prediction/analysis, not
    # llm_judgment — so the reviewed LLM judgement must be SYNCED into the zh i18n or it is dead-
    # rendered. Sync the zh slice from the reviewed JSON (the canonical persona judgement). vi/my/en
    # stay as authored translations (Han=0 preserved). This makes the rendered zh /predict + homepage
    # copy BE the reviewed LLM copy.
    i18n = art.setdefault("i18n", {})
    zh = i18n.setdefault("zh", {})
    zp = zh.setdefault("prediction", {})
    zp["primary_direction"] = rev["main_lean"]
    if rev.get("primary_score"):
        zp["score_call"] = rev["primary_score"]
    if rev.get("backup_scores"):
        zp["backup_score"] = " / ".join(rev["backup_scores"])
    if rev.get("risk_level"):
        zp["risk_level"] = rev["risk_level"]
    if rev.get("risk_note"):
        zp["risk_note"] = rev["risk_note"]
    if rev.get("top_variable"):
        zp["top_variable"] = rev["top_variable"]
    if rev.get("why"):
        zp["why"] = rev["why"]
    za = zh.setdefault("analysis", {})
    if rev.get("tactical_read"):
        za["tactical_matchup"] = rev["tactical_read"]
    if rev.get("risk_factors"):
        za["risk_variables"] = rev["risk_factors"]
    if rev.get("external_expectation"):
        za["external_expectation"] = rev["external_expectation"]
    if rev.get("t30_checklist"):
        za["thirty_minute_checklist"] = rev["t30_checklist"]
    if rev.get("share_copy"):
        ops = zh.setdefault("operations", {})
        ops["share_copy"] = rev["share_copy"]
    provider = rev.get("llm_provider") or "operator_manual"
    # record that the reviewed copy is the rendered source (renderer-traceability for /internal/daily)
    art["rendered_copy_source"] = ("reviewed_llm:" + provider) if provider not in ("operator_manual", "pending") else "operator_reviewed_llm_judgment"
    cc = art.get("content_chain") or {}
    cc.update({"reviewed_path": str(rp.relative_to(ROOT)) if str(rp).startswith(str(ROOT)) else reviewed_file,
               "reviewed_applied": True, "llm_provider": provider, "built_at": date})
    art["content_chain"] = cc
    oc = art.get("operator_confirmation") or {}
    oc["confirmed"] = True
    oc.setdefault("confirmed_by", "operator")
    oc.setdefault("confirmed_at", date + "T00:00:00+00:00")
    oc.setdefault("edited_fields", [])
    art["operator_confirmation"] = oc
    saf = art.get("safety") or {}
    # NOTE: do NOT add a 'no_betting_vocab' key — the literal substring 'betting' self-trips the
    # vocabulary scanners over the artifact JSON. 'vocabulary_compliant' carries the same intent.
    saf.pop("no_betting_vocab", None)
    saf["vocabulary_compliant"] = True
    saf["no_fake_probability"] = True
    saf["no_auto_send"] = True
    art["safety"] = saf
    _save(path, art)
    print("OK    applied reviewed JSON (provider=%s) → %s" % (provider, path.relative_to(ROOT)))
    print("OK    content_chain.reviewed_applied=true · llm_judgment merged")
    return 0


def selftest():
    checks = []
    good = {k: ("x" if k not in ("backup_scores", "tactical_read", "risk_factors",
                                  "external_expectation", "t30_checklist") else ["a"]) for k in REVIEWED_KEYS}
    good["safety"] = {"no_fake_probability": True, "no_auto_send": True}
    checks.append(("good reviewed validates", validate_reviewed(good) == []))
    checks.append(("missing key caught", any("missing key" in e for e in validate_reviewed(
        {k: good[k] for k in REVIEWED_KEYS if k != "main_lean"} | {"safety": good["safety"]}))))
    checks.append(("betting vocab caught", any("betting" in e for e in validate_reviewed(
        dict(good, share_copy="看 赔率")))))
    checks.append(("fake win_prob caught", any("win_prob" in e for e in validate_reviewed(
        dict(good, win_prob={"home": 60})))))
    checks.append(("numeric confidence caught", any("confidence" in e for e in validate_reviewed(
        dict(good, confidence=72)))))
    checks.append(("fake-prob word caught", any("fake-probability" in e for e in validate_reviewed(
        dict(good, why="胜率 60%")))))
    checks.append(("slug strips colon", slug("manual:Nether-Japan-20260614") == "manual_Nether-Japan-20260614"))
    lk = model_lookup("manual:X", {"id": None})
    checks.append(("manual lookup unavailable", lk["result"] == "unavailable"))
    mf = build_model_fields({"model_fields": {"recommended_score": "2-1", "backup_scores": ["1-1"],
                                              "risk_level": "中高", "risk_note": "n"}}, lk)
    checks.append(("model_fields win_prob null", mf["win_prob"] is None and mf["confidence"] is None
                   and mf["source"] == "operator_estimated" and mf["no_fake_probability"] is True))
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["prompt", "apply"])
    ap.add_argument("--date", default="")
    ap.add_argument("--fixture-key", default="")
    ap.add_argument("--reviewed", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd == "prompt":
        return cmd_prompt(a.date or "00000000", a.fixture_key)
    if a.cmd == "apply":
        if not a.reviewed:
            print("FAIL  apply requires --reviewed <file>"); return 1
        return cmd_apply(a.date or "00000000", a.fixture_key, a.reviewed)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
