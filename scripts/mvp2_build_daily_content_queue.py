#!/usr/bin/env python3
"""
P1 content factory — daily content queue builder (Owner 2026-06-15: production capacity, >1 match/day).

Reads the daily fixture slate + the selected hotspot + the bundled prediction/observation artifacts,
ranks fixtures by a transparent priority score, and writes a queue artifact the homepage and
/internal/daily read:

  daily-fixtures slate → priority score → primary_hotspot + secondary_matches + recap_queue + t30_queue
                       → content_state per match → frontend/src/data/dailyContentQueue.json

content_state per match is derived from the bundled prediction artifact (NOT invented):
  FIXTURE_READY  — fixture in slate, no artifact yet
  MODEL_READY    — artifact + source_facts/model_fields present
  PROMPT_READY   — content_chain.prompt_generated
  REVIEW_READY   — content_chain.reviewed_applied
  ARTIFACT_READY — model_fields + reviewed + judgement all present
  PUBLISHED      — ARTIFACT_READY + prediction_confirmed (renders on /predict)

HARD RULES: never invents scores/probability; primary must be current (not older than the slate)
unless it is an explicit carryover recap; if source coverage is missing it is stated, not faked.
Subcommands: build (default), --selftest.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
FALLBACK_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
GEN_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "generated"

# Transparent priority inputs (documented in MATCH_PRIORITY_QUEUE.md). Popularity / market relevance
# are small static lists — editorial, not a model. Host nations 2026 = USA/Canada/Mexico; market =
# Vietnam/Myanmar fan pull (Asian sides). NEVER a betting/odds signal.
POPULAR = {"Brazil", "Argentina", "Spain", "France", "Germany", "England", "Portugal", "Belgium",
           "Netherlands", "Italy", "Uruguay", "Croatia", "Morocco", "Mexico"}
MARKET = {"Japan", "South Korea", "Saudi Arabia", "Australia", "Qatar", "Iran", "Vietnam", "Thailand"}
HOST = {"United States", "USA", "Canada", "Mexico"}
SECONDARY_MAX = 4


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_artifacts():
    preds, obs = {}, {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            try:
                a = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if "recap_ready" in a:
                for k in (a.get("id"), a.get("fixture_key")):
                    if k:
                        obs[str(k)] = a
            else:
                for k in (a.get("id"), a.get("fixture_key")):
                    if k:
                        preds[str(k)] = a
    return preds, obs


def fixture_keys(f):
    return [str(k) for k in (f.get("id"), f.get("external_game_id")) if k]


def find_pred(f, preds):
    for k in fixture_keys(f):
        if k in preds:
            return preds[k]
    return None


def content_state(art):
    """Derive the prediction content_state from the bundled artifact (never invented)."""
    if not art:
        return "FIXTURE_READY"
    cc = art.get("content_chain") or {}
    has_model = isinstance(art.get("model_fields"), dict) and art["model_fields"].get("source") not in (None,)
    has_judgement = bool((art.get("llm_judgment") or {}).get("main_lean")) or \
        bool((((art.get("i18n") or {}).get("zh") or {}).get("prediction") or {}).get("primary_direction"))
    if cc.get("reviewed_applied") and has_model and has_judgement and art.get("prediction_confirmed"):
        return "PUBLISHED"
    if cc.get("reviewed_applied"):
        return "REVIEW_READY"
    if cc.get("prompt_generated"):
        return "PROMPT_READY"
    if has_model:
        return "MODEL_READY"
    return "FIXTURE_READY"


def priority_score(f, art):
    """Transparent additive score (higher = more worth productizing). Documented in the design doc."""
    s, why = 0, []
    for team in (f.get("home"), f.get("away")):
        if team in POPULAR:
            s += 25; why.append("popular:%s" % team)
        if team in MARKET:
            s += 20; why.append("market:%s" % team)
        if team in HOST:
            s += 15; why.append("host:%s" % team)
    # source coverage: a computed model is more publishable than operator_estimated/none
    mf = (art or {}).get("model_fields") or {}
    src = mf.get("source")
    if src == "computed":
        s += 20; why.append("model:computed")
    elif src in ("operator_estimated", "operator_confirmed", "seed"):
        s += 8; why.append("model:%s" % src)
    else:
        why.append("model:none (source coverage missing)")
    # upset / narrative potential: a medium/high upset band reads as a stronger story
    rl = mf.get("risk_level")
    if rl in ("中", "中高", "高", "Medium", "High"):
        s += 10; why.append("narrative:upset-risk")
    # scheduled & fresh beats finished for the prediction queue
    if (f.get("status") or "").lower() == "scheduled":
        s += 10; why.append("scheduled")
    return s, why


def build(now_iso=None):
    man = _load(MANIFEST) or _load(FALLBACK_MANIFEST) or {}
    sel = _load(SEL)
    preds, obs = load_artifacts()
    slate_date = man.get("generated_for_date")
    fixtures = man.get("fixtures", [])

    def row(f, role):
        art = find_pred(f, preds)
        score, why = priority_score(f, art)
        mf = (art or {}).get("model_fields") or {}
        return {
            "fixture_key": (f.get("id") or f.get("external_game_id")),
            "id": f.get("id"),
            "home": f.get("home"), "away": f.get("away"),
            "kickoffUtc": f.get("kickoffUtc"), "status": f.get("status"),
            "lifecycle_state": f.get("lifecycle_state"),
            "role": role,
            "priority_score": score,
            "priority_reasons": why,
            "content_state": content_state(art),
            "artifact_ready": content_state(art) in ("ARTIFACT_READY", "PUBLISHED"),
            "model_source": mf.get("source"),
            "source_coverage": "computed" if mf.get("source") == "computed"
                               else ("operator_estimated" if mf.get("source") in ("operator_estimated", "operator_confirmed", "seed")
                                     else "missing"),
            "recommended_score": mf.get("recommended_score"),
            "risk_level": mf.get("risk_level"),
        }

    scheduled = [f for f in fixtures if (f.get("status") or "").lower() == "scheduled"]
    finished = [f for f in fixtures if (f.get("status") or "").lower() == "finished"]

    # PRIMARY: the selected hotspot is the AUTHORITY (P7 P0-1) when it is current & in the slate.
    primary = None
    if sel and sel.get("status") == "active" and sel.get("fixture_key"):
        if not (slate_date and sel.get("date") and sel["date"] < slate_date):  # not stale
            for f in scheduled:
                if sel["fixture_key"] in fixture_keys(f):
                    primary = row(f, "primary"); break
    if primary is None and scheduled:  # fallback: top-scored scheduled
        best = max(scheduled, key=lambda f: priority_score(f, find_pred(f, preds))[0])
        primary = row(best, "primary")

    # SECONDARY: remaining scheduled fixtures, ranked by priority, capped.
    secondary = []
    for f in sorted(scheduled, key=lambda f: -priority_score(f, find_pred(f, preds))[0]):
        if primary and (f.get("id") or f.get("external_game_id")) == primary["fixture_key"]:
            continue
        secondary.append(row(f, "secondary"))
        if len(secondary) >= SECONDARY_MAX:
            break

    # RECAP queue: finished fixtures that need a recap; recap_state from observation/recap presence.
    recap_q = []
    for f in finished:
        ob = None
        for k in fixture_keys(f):
            if k in obs:
                ob = obs[k]; break
        recapReady = bool(f.get("recapReady"))
        state = ("RECAP_READY" if recapReady else
                 ("OBSERVATION_READY" if ob else "WAITING_FT" if not (f.get("scoreHome") is not None) else "FT_READY"))
        recap_q.append({
            "fixture_key": (f.get("id") or f.get("external_game_id")), "id": f.get("id"),
            "home": f.get("home"), "away": f.get("away"),
            "score": (None if f.get("scoreHome") is None else "%s-%s" % (f.get("scoreHome"), f.get("scoreAway"))),
            "recap_state": state,
            "has_observation": bool(ob),
        })

    # T-30 queue: scheduled fixtures that have a prediction artifact (a t30 slot to confirm at KO-30).
    t30_q = []
    for r in ([primary] if primary else []) + secondary:
        art = preds.get(str(r["fixture_key"])) or preds.get(str(r["id"]))
        t = (art or {}).get("t30") or {}
        if art:
            t30_q.append({"fixture_key": r["fixture_key"], "home": r["home"], "away": r["away"],
                          "t30_status": t.get("status", "pending"), "kickoffUtc": r["kickoffUtc"]})

    # P1B — auto-LLM generated-draft status per fixture (read the generated/ drafts; never auto-publish)
    autogen = []
    if GEN_DIR.exists():
        for gp in sorted(GEN_DIR.glob("*_generated.json")):
            try:
                g = json.loads(gp.read_text(encoding="utf-8"))
            except Exception:
                continue
            autogen.append({"fixture_key": str(g.get("fixture_key")), "home": g.get("home"), "away": g.get("away"),
                            "provider": g.get("provider"), "mode": g.get("mode"), "status": g.get("status")})

    queue = {
        "date": slate_date,
        "generated_at": now_iso or man.get("generated_at"),
        "built_by": "mvp2_build_daily_content_queue.py",
        "autogen_drafts": autogen,
        "scoring": {"weights": {"popular": 25, "market": 20, "host": 15, "model_computed": 20,
                                "model_estimated": 8, "narrative_upset": 10, "scheduled": 10},
                    "note": "transparent editorial priority — never a betting/odds signal"},
        "primary_hotspot": primary,
        "secondary_matches": secondary,
        "recap_queue": recap_q,
        "t30_queue": t30_q,
        "send_status": "HOLD",
    }
    return queue


def cmd_build(now_iso):
    q = build(now_iso)
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    p = q.get("primary_hotspot")
    print("OK    queue: primary=%s · secondary=%d · recap=%d · t30=%d → %s" % (
        (p["home"] + " vs " + p["away"]) if p else "NONE",
        len(q["secondary_matches"]), len(q["recap_queue"]), len(q["t30_queue"]),
        QUEUE.relative_to(ROOT)))
    for r in q["secondary_matches"]:
        print("      secondary: %s vs %s · %s · %s · score=%d" % (
            r["home"], r["away"], r["content_state"], r["source_coverage"], r["priority_score"]))
    return 0


def selftest():
    q = build(now_iso="2026-06-15T12:00:00+00:00")
    checks = [
        ("primary present", q["primary_hotspot"] is not None),
        ("primary is scheduled & current", (q["primary_hotspot"] or {}).get("status") == "scheduled"),
        ("at least one secondary", len(q["secondary_matches"]) >= 1),
        ("secondary capped", len(q["secondary_matches"]) <= SECONDARY_MAX),
        ("recap queue has entries", len(q["recap_queue"]) >= 1),
        ("content_state on every row", all(r.get("content_state") for r in
            ([q["primary_hotspot"]] + q["secondary_matches"]))),
        ("send HOLD", q["send_status"] == "HOLD"),
        ("source coverage labelled", all(r.get("source_coverage") in ("computed", "operator_estimated", "missing")
            for r in ([q["primary_hotspot"]] + q["secondary_matches"]))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build", choices=["build"])
    ap.add_argument("--now", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return cmd_build(a.now or None)


if __name__ == "__main__":
    sys.exit(main())
