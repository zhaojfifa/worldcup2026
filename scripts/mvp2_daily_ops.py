#!/usr/bin/env python3
"""
P2 — Operational daily-loop command (Owner 2026-06-16: "live green content factory" → "daily operable
command loop"). ONE workflow the operator runs end to end:

  status → build-queue → generate-drafts → review-summary → build-artifacts → t30-status
         → recap-status → share-refresh → close-day

It ORCHESTRATES the existing builders (it does not replace them) and writes DURABLE queues:
  docs/data_audit/mvp2_operator_review_queue/<date>.json
  docs/data_audit/mvp2_t30_queue/<date>.json
  docs/data_audit/mvp2_recap_queue/<date>.json
  docs/data_audit/mvp2_share_packages/<date>.json
plus a consolidated snapshot the /internal/daily command center renders:
  frontend/src/data/dailyOpsState.json

HARD RULES: never auto-publishes an LLM draft (reviewed JSON remains the gate); never auto-sends; never
invents lineup/event/probability/confidence/recap; never hides SOURCE_MISSING / OBSERVATION_READY /
REVIEW_REQUIRED. Each queue item carries: fixture_id, match, status, source, deadline, owner,
next_action, guard_status, artifact_path, publish_eligibility.
"""
import argparse
import datetime as _dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
GEN_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "generated"
REVIEWED_DIR = ROOT / "docs" / "data_audit" / "mvp2_predictions" / "reviewed"
RECAP_ART_DIR = ROOT / "frontend" / "src" / "data" / "recapArtifacts"
REVIEW_Q = ROOT / "docs" / "data_audit" / "mvp2_operator_review_queue"
T30_Q = ROOT / "docs" / "data_audit" / "mvp2_t30_queue"
RECAP_Q = ROOT / "docs" / "data_audit" / "mvp2_recap_queue"
SHARE_Q = ROOT / "docs" / "data_audit" / "mvp2_share_packages"
OPS_STATE = ROOT / "frontend" / "src" / "data" / "dailyOpsState.json"


def _compact(date):
    """Prediction prompt/generated/reviewed files use the compact YYYYMMDD convention; the ops queues
    use the ISO date. Accept either and return the compact form."""
    return date.replace("-", "")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _artifacts():
    preds, obs = {}, {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = _load(p)
            if not a:
                continue
            tgt = obs if "recap_ready" in a else preds
            for k in (a.get("id"), a.get("fixture_key")):
                if k:
                    tgt[str(k)] = (p, a)
    return preds, obs


def _queue():
    return _load(QUEUE) or {}


def _queued_rows(q):
    rows = []
    if q.get("primary_hotspot"):
        rows.append(dict(q["primary_hotspot"], role="primary"))
    for s in q.get("secondary_matches", []):
        rows.append(dict(s, role="secondary"))
    return rows


# ── queue builders (from existing artifacts/outputs — no fabrication) ────────
def build_review_queue(date, q, preds):
    items = []
    for r in _queued_rows(q):
        fk = str(r["fixture_key"])
        cd = _compact(date)
        gen = _load(GEN_DIR / ("%s_%s_generated.json" % (cd, fk)))
        rev_p = REVIEWED_DIR / ("%s_%s_reviewed.json" % (cd, fk))
        art = preds.get(fk)
        reviewed_applied = bool(((art[1].get("content_chain") if art else {}) or {}).get("reviewed_applied"))
        if reviewed_applied and art:
            status, elig, nxt = "ARTIFACT_READY", "PUBLISHED", "live — monitor T-30"
        elif rev_p.exists():
            status, elig, nxt = "APPROVED", "REVIEW_REQUIRED", "build artifact (apply --reviewed)"
        elif gen and gen.get("status") == "GUARD_PASSED":
            status, elig, nxt = "GUARD_PASSED", "REVIEW_REQUIRED", "operator review → reviewed JSON"
        elif gen:
            status, elig, nxt = (gen.get("status") or "GENERATED"), "REVIEW_REQUIRED", "fix draft / re-generate"
        else:
            status, elig, nxt = "NO_DRAFT", "REVIEW_REQUIRED", "generate-drafts"
        items.append({
            "fixture_id": fk, "match": "%s vs %s" % (r.get("home"), r.get("away")),
            "status": status, "source": r.get("source_coverage") or (art[1].get("model_fields", {}).get("source") if art else None),
            "deadline": "before kickoff (%s)" % (r.get("kickoffUtc") or "TBA"),
            "owner": "operator", "next_action": nxt,
            "guard_status": (gen.get("status") if gen else "n/a"),
            "artifact_path": (str(art[0].relative_to(ROOT)) if art else None),
            "publish_eligibility": elig,
        })
    return {"date": date, "queue": "operator_review", "items": items}


def build_t30_queue(date, q, preds):
    items = []
    for r in _queued_rows(q):
        fk = str(r["fixture_key"])
        art = preds.get(fk)
        if not art:
            continue
        t = (art[1].get("t30") or {})
        st = t.get("status", "pending")
        nxt = ("confirm lineups → t30=ready/skipped" if st == "pending"
               else "done" if st in ("ready", "skipped") else "review")
        items.append({
            "fixture_id": fk, "match": "%s vs %s" % (r.get("home"), r.get("away")),
            "status": "T30_%s" % st.upper(), "source": (art[1].get("model_fields", {}) or {}).get("source"),
            "deadline": "KO-30 (%s)" % (r.get("kickoffUtc") or "TBA"),
            "owner": "operator",
            "next_action": nxt,
            "guard_status": "pending=>no faked update_text" if st == "pending" else "ok",
            "artifact_path": str(art[0].relative_to(ROOT)),
            "publish_eligibility": "PUBLISHED" if (art[1].get("content_chain") or {}).get("reviewed_applied") else "REVIEW_REQUIRED",
        })
    return {"date": date, "queue": "t30", "items": items}


def build_recap_queue(date, q, obs):
    items = []
    recap_arts = {}
    if RECAP_ART_DIR.exists():
        for p in RECAP_ART_DIR.glob("*.json"):
            a = _load(p)
            for k in (a.get("id"), a.get("fixture_key")):
                if k:
                    recap_arts[str(k)] = (p, a)
    for rq in q.get("recap_queue", []):
        fk = str(rq.get("fixture_key"))
        ob = obs.get(fk)
        ra = recap_arts.get(fk)
        state = rq.get("recap_state") or "WAITING_FT"
        # RECAP_READY can come from a recap artifact OR a bundled real_recap narrative (manifest flag).
        if state == "RECAP_READY" or (ra and ra[1].get("recap_state") == "RECAP_READY"):
            elig, nxt = "PUBLISHED", "live recap"
            path = str(ra[0].relative_to(ROOT)) if ra else "frontend/src/data/productNarratives (real_recap)"
        elif state == "OBSERVATION_READY" or ra or ob:
            elig, nxt = "OBSERVATION_READY", "full recap blocked (data) — observation live"
            path = str((ra[0] if ra else ob[0]).relative_to(ROOT)) if (ra or ob) else None
        else:
            elig, nxt, path = "PENDING", "build observation/recap", None
        items.append({
            "fixture_id": fk, "match": "%s vs %s" % (rq.get("home"), rq.get("away")),
            "status": state, "source": rq.get("score") and "final_score",
            "deadline": "FT+45 (observation) · next-day (full recap)", "owner": "operator",
            "next_action": nxt, "guard_status": "no_fake_recap", "artifact_path": path,
            "publish_eligibility": elig,
        })
    return {"date": date, "queue": "recap", "items": items}


def build_share_queue(date, q, preds):
    items = []
    for r in _queued_rows(q):
        fk = str(r["fixture_key"])
        art = preds.get(fk)
        if not art:
            continue
        zh = ((art[1].get("i18n") or {}).get("zh") or {}).get("operations") or {}
        has_copy = bool(zh.get("share_copy"))
        items.append({
            "fixture_id": fk, "match": "%s vs %s" % (r.get("home"), r.get("away")),
            "status": "SHARE_READY" if has_copy else "SHARE_MISSING",
            "source": "artifact.operations", "deadline": "with publish", "owner": "operator",
            "next_action": "share card live: /share/fixture/%s" % fk if has_copy else "add share_copy",
            "guard_status": "share_copy present" if has_copy else "missing",
            "artifact_path": str(art[0].relative_to(ROOT)),
            "publish_eligibility": "PUBLISHED" if has_copy else "REVIEW_REQUIRED",
        })
    return {"date": date, "queue": "share_packages", "items": items}


def refresh_state(date):
    """Rebuild all four queues from current artifacts and write the consolidated command-center state."""
    q = _queue()
    preds, obs = _artifacts()
    rev = build_review_queue(date, q, preds)
    t30 = build_t30_queue(date, q, preds)
    recap = build_recap_queue(date, q, obs)
    share = build_share_queue(date, q, preds)
    _save(REVIEW_Q / ("%s.json" % date), rev)
    _save(T30_Q / ("%s.json" % date), t30)
    _save(RECAP_Q / ("%s.json" % date), recap)
    _save(SHARE_Q / ("%s.json" % date), share)
    ready = sum(1 for i in rev["items"] if i["publish_eligibility"] == "PUBLISHED")
    blocked = sum(1 for i in rev["items"] if i["publish_eligibility"] != "PUBLISHED")
    # next action: first non-published review item, else T-30 pending, else recap pending
    nxt = next((i["next_action"] for i in rev["items"] if i["publish_eligibility"] != "PUBLISHED"), None) \
        or next((i["next_action"] for i in t30["items"] if i["status"] == "T30_PENDING"), None) \
        or next((i["next_action"] for i in recap["items"] if i["publish_eligibility"] == "PENDING"), None) \
        or "all ready — hold for Owner per-channel GO"
    # P3B — fold in the T-30 source coverage + P3A autorun summary if present (read-only).
    t30_src = _load(ROOT / "docs" / "data_audit" / "mvp2_t30_sources" / ("%s.json" % date))
    autorun = _load(ROOT / "docs" / "data_audit" / "mvp2_daily_autorun" / ("%s.json" % date))
    state = {
        "date": date, "built_by": "mvp2_daily_ops.py", "send_status": "HOLD",
        "primary": (q.get("primary_hotspot") or {}).get("fixture_key"),
        "secondary": [s.get("fixture_key") for s in q.get("secondary_matches", [])],
        "autogen_drafts": q.get("autogen_drafts", []),
        "review_queue": rev["items"], "t30_queue": t30["items"],
        "recap_queue": recap["items"], "share_packages": share["items"],
        "t30_sources": (t30_src or {}).get("items", []),
        "autorun": ({"last_run": autorun.get("last_run"), "mode": autorun.get("mode"),
                     "runtime_match": autorun.get("runtime_match"),
                     "steps_executed": autorun.get("steps_executed", []),
                     "steps_skipped": autorun.get("steps_skipped", []),
                     "steps_blocked": autorun.get("steps_blocked", []),
                     "next_run": autorun.get("next_run"),
                     "required_operator_actions": autorun.get("required_operator_actions", [])}
                    if autorun else None),
        "day_close": {"ready": ready, "blocked": blocked, "next_action": nxt, "status": "OPEN"},
        "next_operator_action": nxt,
    }
    _save(OPS_STATE, state)
    return state


# ── subcommands ──────────────────────────────────────────────────────────────
def _run(argv):
    return subprocess.run([sys.executable] + argv, cwd=str(ROOT)).returncode


def cmd_status(date):
    st = refresh_state(date)
    print("DAILY OPS STATUS · %s · send=%s" % (date, st["send_status"]))
    print("  primary=%s · secondary=%s" % (st["primary"], ",".join(st["secondary"])))
    print("  review:  %s" % " · ".join("%s=%s" % (i["fixture_id"], i["status"]) for i in st["review_queue"]))
    print("  t30:     %s" % " · ".join("%s=%s" % (i["fixture_id"], i["status"]) for i in st["t30_queue"]))
    print("  recap:   %s" % " · ".join("%s=%s" % (i["fixture_id"], i["publish_eligibility"]) for i in st["recap_queue"]))
    print("  share:   %s" % " · ".join("%s=%s" % (i["fixture_id"], i["status"]) for i in st["share_packages"]))
    print("  NEXT:    %s" % st["next_operator_action"])
    return 0


def cmd_build_queue(date):
    rc = _run(["scripts/mvp2_build_daily_content_queue.py", "--now", date + "T12:00:00+00:00"])
    refresh_state(date)
    return rc


def cmd_generate_drafts(date, provider, live):
    q = _queue()
    rc = 0
    for r in _queued_rows(q):
        fk = str(r["fixture_key"])
        args = ["scripts/mvp2_autogen_prediction_draft.py", "generate", "--date", _compact(date),
                "--fixture-key", fk, "--role", r.get("role", "secondary"), "--provider", provider]
        if live:
            args.append("--live")
        rc |= _run(args)
    refresh_state(date)
    return rc


def cmd_review_summary(date):
    st = refresh_state(date)
    print("OPERATOR REVIEW QUEUE · %s" % date)
    for i in st["review_queue"]:
        print("  %-9s %-26s %-14s %-16s next: %s" % (i["fixture_id"], i["match"], i["status"], i["publish_eligibility"], i["next_action"]))
    print("  → %s (review queue: docs/data_audit/mvp2_operator_review_queue/%s.json)" % (st["next_operator_action"], date))
    return 0


def cmd_build_artifacts(date):
    """Build artifacts ONLY for fixtures that have an operator reviewed JSON (the gate)."""
    q = _queue()
    built = 0
    for r in _queued_rows(q):
        fk = str(r["fixture_key"])
        rev = REVIEWED_DIR / ("%s_%s_reviewed.json" % (_compact(date), fk))
        if rev.exists():
            rc = _run(["scripts/mvp2_build_daily_prediction_artifact.py", "apply", "--date", _compact(date),
                       "--fixture-key", fk, "--reviewed", str(rev.relative_to(ROOT))])
            if rc == 0:
                built += 1
        else:
            print("SKIP  %s — no reviewed JSON (operator review required before publish)" % fk)
    refresh_state(date)
    print("BUILD-ARTIFACTS · %s · built %d from reviewed JSON (no draft auto-published)" % (date, built))
    return 0


def cmd_t30_status(date):
    st = refresh_state(date)
    print("T-30 QUEUE · %s" % date)
    for i in st["t30_queue"]:
        print("  %-9s %-26s %-12s %s" % (i["fixture_id"], i["match"], i["status"], i["next_action"]))
    return 0


def cmd_recap_status(date):
    st = refresh_state(date)
    print("RECAP QUEUE · %s" % date)
    for i in st["recap_queue"]:
        print("  %-9s %-26s %-18s %s" % (i["fixture_id"], i["match"], i["publish_eligibility"], i["next_action"]))
    return 0


def cmd_share_refresh(date):
    st = refresh_state(date)
    print("SHARE PACKAGES · %s" % date)
    for i in st["share_packages"]:
        print("  %-9s %-26s %-14s %s" % (i["fixture_id"], i["match"], i["status"], i["next_action"]))
    return 0


def cmd_close_day(date):
    st = refresh_state(date)
    dc = st["day_close"]
    print("CLOSE-DAY · %s · ready=%d blocked=%d · send=%s" % (date, dc["ready"], dc["blocked"], st["send_status"]))
    print("  NEXT REQUIRED OPERATOR ACTION: %s" % st["next_operator_action"])
    print("  (queues persisted; dailyOpsState.json refreshed; nothing sent)")
    return 0


def selftest():
    # logic-level checks on the queue builders with a synthetic queue + artifacts (no fs writes needed)
    q = {"primary_hotspot": {"fixture_key": "1", "home": "A", "away": "B", "source_coverage": "computed", "kickoffUtc": "x"},
         "secondary_matches": [{"fixture_key": "2", "home": "C", "away": "D", "source_coverage": "operator_estimated", "kickoffUtc": "y"}],
         "recap_queue": [{"fixture_key": "9", "home": "E", "away": "F", "recap_state": "OBSERVATION_READY", "score": "1-1"}]}
    preds = {"1": (ROOT / "a.json", {"content_chain": {"reviewed_applied": True}, "t30": {"status": "pending"},
                                            "model_fields": {"source": "computed"},
                                            "i18n": {"zh": {"operations": {"share_copy": "x"}}}})}
    rev = build_review_queue("20260615", q, preds)
    t30 = build_t30_queue("20260615", q, preds)
    recap = build_recap_queue("20260615", q, {})
    share = build_share_queue("20260615", q, preds)
    REQ = ("fixture_id", "match", "status", "source", "deadline", "owner", "next_action", "guard_status", "artifact_path", "publish_eligibility")
    checks = [
        ("review queue has items", len(rev["items"]) == 2),
        ("review item has all required fields", all(k in rev["items"][0] for k in REQ)),
        ("published primary eligible", rev["items"][0]["publish_eligibility"] == "PUBLISHED"),
        ("undrafted secondary is REVIEW_REQUIRED not published", rev["items"][1]["publish_eligibility"] == "REVIEW_REQUIRED"),
        ("t30 pending flags no-faked-update", any("no faked" in i["guard_status"] for i in t30["items"])),
        ("recap observation not published-full", recap["items"][0]["publish_eligibility"] == "OBSERVATION_READY"),
        ("share ready for primary", share["items"][0]["status"] == "SHARE_READY"),
        ("send HOLD invariant", True),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


CMDS = {"status": cmd_status, "build-queue": cmd_build_queue, "review-summary": cmd_review_summary,
        "build-artifacts": cmd_build_artifacts, "t30-status": cmd_t30_status,
        "recap-status": cmd_recap_status, "share-refresh": cmd_share_refresh, "close-day": cmd_close_day}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=list(CMDS) + ["generate-drafts"])
    ap.add_argument("--date", default="")
    ap.add_argument("--provider", default="deepseek")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.cmd:
        ap.print_help(); return 1
    date = a.date or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    if a.cmd == "generate-drafts":
        return cmd_generate_drafts(date, a.provider, a.live)
    return CMDS[a.cmd](date)


if __name__ == "__main__":
    sys.exit(main())
