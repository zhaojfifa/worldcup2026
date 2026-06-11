#!/usr/bin/env python3
"""
MVP-2 Track A — A3 rescore diff builder (design §3 A3; Owner A-GO-1).

ENGINEERING produces a FACTS-ONLY skeleton: announced XI / formation / goalkeeper /
late injury signals fetched from API-FOOTBALL, compared against the archived trial
frame's team_baseline (squad GKs, top scorers, expected setup) plus the machine-
readable rule candidates from the rescore generator skeleton. THE LLM remains the
only author of customer-facing language: it writes the `trial_rescore_update`
(what_changed / updated_lean / updated_risk_level / updated_score_range /
group_update_message) in persona voice, gated in-loop by
check_mvp2_product_narrative_guard.check_rescore_update_obj.

Artifacts are written ONLY after guard pass (Owner scope item 4):
  docs/data_audit/mvp2_rescore_runs/{fixture}.{lang}.{run_id}.json
No lineups posted yet -> returns blocked_by_time_or_data (caller records the
manifest; nothing is written, nothing is sent).

Usage: python3 scripts/mvp2_build_rescore_diff.py FIXTURE_ID [zh-CN|vi-VN|my-MM ...]
Default langs: all three. Provider: deepseek (per project decision).
"""
import importlib.util
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.api_football_client import APIFootballScoutClient  # noqa: E402

OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_rescore_runs"
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"
NARR = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_narratives"
LANGS = ("zh-CN", "vi-VN", "my-MM")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _load("ppgen", ROOT / "scripts" / "mvp2_generate_product_proof_narratives.py")
RG = _load("rg", ROOT / "scripts" / "mvp2_generate_rescore_models.py")
Q = _load("opsq", ROOT / "scripts" / "mvp2_ops_queue.py")
GUARD = GEN.GUARD

BAND_EXAMPLE = {
    "zh-CN": "俅哥给出的赛前参考区间：…",
    "vi-VN": "khoảng tham khảo trước trận của Tiên Tri: …",
    "my-MM": "Football Oracle ၏ ပွဲကြို ရည်ညွှန်းအပိုင်းအခြား: …",
}


# ── facts (engineering only — no narrative) ──────────────────────────────────
def fetch_facts(fid, run=None, client=None):
    """Returns (facts|None, info). facts None => lineups not posted yet."""
    client = client or APIFootballScoutClient()
    fx = (client.get_fixture(int(fid)).response or [{}])[0]
    if run:
        run.api("/fixtures")
    f = fx.get("fixture", {})
    info = {"kickoff_utc": f.get("date"), "status_short": (f.get("status") or {}).get("short")}
    lu = client.get_lineups(int(fid)).response or []
    if run:
        run.api("/fixtures/lineups")
    if not lu:
        return None, info
    inj = client.get_injuries(fixture_id=int(fid)).response or []
    if run:
        run.api("/injuries")
    teams = []
    for side in lu:
        starters = [((p.get("player") or {})) for p in (side.get("startXI") or [])]
        gk = next((p.get("name") for p in starters if (p.get("pos") or "") == "G"), None)
        teams.append({
            "team": (side.get("team") or {}).get("name"),
            "formation": side.get("formation"),
            "coach": (side.get("coach") or {}).get("name"),
            "goalkeeper_started": gk,
            "starters": [p.get("name") for p in starters],
            "substitutes_count": len(side.get("substitutes") or []),
        })
    info["late_injury_entries"] = [
        {"team": ((e.get("team") or {}).get("name")), "player": ((e.get("player") or {}).get("name")),
         "reason": ((e.get("player") or {}).get("reason"))} for e in inj]
    return teams, info


def build_skeleton(fid, teams, info):
    frame = Q.read_json(FRAMES / ("%s.json" % fid))
    if not frame:
        raise SystemExit("rescore-diff: no archived trial frame for %s — run A2 first" % fid)
    base = frame["team_baseline"]
    out = frame["scoutscore_output"]
    checks = {}
    for side_key in ("home", "away"):
        b = base[side_key]
        announced = next((t for t in teams if t["team"] == b["team"]), None)
        if not announced:
            continue
        known_gks = [g.get("name") if isinstance(g, dict) else g for g in (b.get("squad_goalkeepers") or [])]
        scorers = [s.get("scorer") if isinstance(s, dict) else s for s in (b.get("top_scorers_last10") or [])]
        checks[b["team"]] = {
            "goalkeeper_started": announced["goalkeeper_started"],
            "gk_in_known_squad_gks": announced["goalkeeper_started"] in known_gks if announced["goalkeeper_started"] else None,
            "top_scorers_started": {s: (s in announced["starters"]) for s in scorers[:3]},
            "formation_announced": announced["formation"],
            "expected_setup_note_prematch": b.get("expected_setup_note"),
        }
    rules = [{"rule_id": "rule_%d" % i, **r} for i, r in enumerate(RG.skeleton(str(fid))["rule_logic"])]
    return {
        "fixture_id": str(fid),
        "match": frame["fixture"]["match"],
        "kickoff_utc": info.get("kickoff_utc") or frame["fixture"].get("kickoff"),
        "announced_lineups": teams,
        "baseline_checks": checks,
        "late_injury_entries": info.get("late_injury_entries", []),
        "pre_match_output": {"primary_lean": out["primary_lean"], "risk_level": out["risk_level"],
                             "score_range": out["score_range"], "what_could_flip": out["what_could_flip"]},
        "rule_candidates": rules,
    }


def _based_on(fid, lang):
    p = NARR / ("%s.%s.deepseek.json" % (fid, lang))
    if not p.exists():
        return None
    n = Q.read_json(p)
    return {
        "judgement_path": str(p.relative_to(ROOT)),
        "inputs_hash": Q.sha256_file(p),
        "generated_at": n.get("generated_at"),
        "quotes": {k: n.get(k) for k in ("main_lean", "scoreline_view", "risk_level")},
    }


# ── LLM rescore update (the only narrative author) ───────────────────────────
def _user_prompt(skeleton, lang, based_on):
    persona = RG.PERSONA[lang]
    return (
        "You write the 30-minute RESCORE UPDATE for the persona '%s' — the starting lineups are now "
        "ANNOUNCED. INPUT (facts-only engineering skeleton + the persona's ORIGINAL pre-match judgement "
        "quotes — never invent beyond them):\n" % persona
        + json.dumps({"skeleton": skeleton, "original_judgement": based_on["quotes"]}, ensure_ascii=False)
        + "\n\nReturn ONLY one JSON object:\n"
          '{"what_changed":[{"name":"<customer-facing variable name>","before":"<what the pre-match view assumed>",'
          '"now":"<announced fact>","effect":"<persona read of the effect>","fired_rule":"<rule_id from rule_candidates>"'
          ' OR "assumption_flag":true}],'
          '"no_change_note":"<persona line if nothing material changed; else empty>",'
          '"updated_lean":"<one line, persona voice>","updated_risk_level":"<short, persona voice>",'
          '"updated_score_range":"<persona reference band, e.g. %s>",'
          '"group_update_message":"<THE in-group correction message the operator pastes — persona voice, '
          'concrete, references the announced XI/GK; no URL>"}\n'
          "Rules: every what_changed entry cites a fired_rule from rule_candidates OR carries assumption_flag=true; "
          "language %s%s; persona '%s' must appear in the customer text; NEVER 模型/mô hình/မော်ဒယ်/AI/ScoutScore; "
          "no betting words (盘口/赔率/kèo/cửa trên/cá cược/လောင်းကစား...); no guarantees; no URLs; "
          "if lineups confirm the pre-match view, say so honestly via no_change_note. JSON only."
        % (BAND_EXAMPLE[lang], lang,
           " — ZERO Han characters" if lang in ("vi-VN", "my-MM") else "", persona.split("（")[0])
    )


def generate_lang(fid, lang, skeleton, expires_at, run_id, provider="deepseek", keys=None):
    based = _based_on(fid, lang)
    if not based:
        return {"language": lang, "status": "skipped_no_prematch_narrative"}
    keys = keys or GEN.load_env_keys()
    key = keys.get("DEEPSEEK_API_KEY" if provider == "deepseek" else "GEMINI_API_KEY")
    if not key:
        return {"language": lang, "status": "failed_no_key"}
    call = GEN.call_deepseek if provider == "deepseek" else GEN.call_gemini
    system = GEN.prompt_body(lang)
    user = _user_prompt(skeleton, lang, based)
    meta = {"product_surface": "trial_rescore_update", "fixture_id": str(fid), "language": lang,
            "voice": GEN.VOICE.get(lang, "tientri_v2"), "llm_provider": provider,
            "model": "deepseek-chat" if provider == "deepseek" else "gemini-2.5-flash",
            "expires_at": expires_at, "based_on": based,
            "lineup_facts": {"announced_lineups": skeleton["announced_lineups"],
                              "baseline_checks": skeleton["baseline_checks"],
                              "late_injury_entries": skeleton["late_injury_entries"]},
            "run_id": run_id}
    errs, obj = ["not attempted"], None
    for attempt in (1, 2, 3):
        try:
            cand = GEN._extract_json(call(key, system, user, GEN.max_tokens_for(lang)))
        except Exception as e:
            print("  ! %s %s attempt %d failed (%s)" % (fid, lang, attempt, type(e).__name__))
            cand = None
        if cand:
            cand.update(meta)
            cand["generated_at"] = datetime.now(timezone.utc).isoformat()
            errs = GUARD.check_rescore_update_obj(cand)
            if not errs:
                obj = cand
                break
            print("  ! %s %s attempt %d guard: %s" % (fid, lang, attempt, "; ".join(errs[:3])))
            user += "\n\nSTRICT RETRY — fix ALL: " + "; ".join(errs[:8])
    if obj is None:
        # Owner scope: trial_rescore_update artifacts ONLY after guard pass — nothing written.
        return {"language": lang, "status": "failed_guard", "errors": errs[:6]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / ("%s.%s.%s.json" % (fid, lang, run_id))
    Q.write_json(p, obj)
    return {"language": lang, "status": "guard_passed", "artifact": str(p.relative_to(ROOT))}


def build_and_generate(fid, langs=LANGS, provider="deepseek", run=None, client=None):
    """Full A3 unit: fetch facts -> skeleton -> 3-lang parallel LLM -> guard-passed artifacts.
    Returns dict with status blocked_by_time_or_data when lineups are not posted."""
    teams, info = fetch_facts(fid, run=run, client=client)
    if info.get("status_short") not in ("NS", "TBD", None):
        return {"status": "blocked_kickoff_passed", "info": info}
    if not teams:
        return {"status": "blocked_by_time_or_data", "reason": "lineups not posted yet", "info": info}
    skeleton = build_skeleton(fid, teams, info)
    expires_at = skeleton["kickoff_utc"]
    run_id = run.run_id if run else Q.new_run_id("rescore")
    keys = GEN.load_env_keys()
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(lambda lang: generate_lang(fid, lang, skeleton, expires_at, run_id,
                                                          provider, keys), langs))
    return {"status": "ok", "info": info, "skeleton_teams": [t["team"] for t in teams],
            "results": results, "run_id": run_id}


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    fid = sys.argv[1]
    langs = [a for a in sys.argv[2:] if a in LANGS] or list(LANGS)
    res = build_and_generate(fid, langs)
    print(json.dumps({k: v for k, v in res.items() if k != "skeleton"}, ensure_ascii=False, indent=2))
    sys.exit(0 if res["status"] == "ok" else 2)


if __name__ == "__main__":
    main()
