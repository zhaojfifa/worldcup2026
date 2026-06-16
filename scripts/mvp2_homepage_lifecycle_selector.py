#!/usr/bin/env python3
"""
P5B — Homepage match-lifecycle selector. The homepage must FOLLOW match progress, not be a fixed board.
From the runtime slate (kickoff + status), the reviewed prediction artifacts (copy_version + model
source) and the observation/recap artifacts, this computes — at a given time basis — the homepage roles:
  primary_prediction · secondary_predictions[1-2] · latest_recap · next_upcoming · finished_pending_recap
  · excluded_archive · excluded_demo · blocked_items.

HARD RULES: primary is the EARLIEST UPCOMING source-qualified (model computed|operator_confirmed) match
with reviewed copy — NEVER a finished match, NEVER operator_estimated, NEVER archive/demo. operator_
estimated can only be secondary (labelled). latest_recap = most recent finished tracked match
(RECAP_READY > OBSERVATION_ONLY > PENDING). No valid primary → PRIMARY_REVIEW_REQUIRED (never stale
fixed content). No fake data; send HOLD.

Commands: build --date / validate --date [--now ISO] / report --date. Writes
docs/data_audit/mvp2_homepage_lifecycle/<date>.json + bundled frontend/src/data/homepageLifecycle.json.
"""
import argparse
import datetime as _dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
FALLBACK = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
OUT_DOCS = ROOT / "docs" / "data_audit" / "mvp2_homepage_lifecycle"
OUT_FE = ROOT / "frontend" / "src" / "data" / "homepageLifecycle.json"

T30_MIN = 30
ARCHIVE_TEAMS = {"Germany", "Qatar"}          # WC-2022 archive opponents — never active
DEMO_PAIRS = [("Brazil", "Argentina")]        # legacy home-demo-fold mock — never active
SOURCE_QUALIFIED = {"computed", "operator_confirmed", "seed"}
FINISHED = {"finished", "FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _preds_obs():
    preds, obs = {}, {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = _load(p)
            if not a:
                continue
            tgt = obs if "recap_ready" in a else preds
            for k in (a.get("id"), a.get("fixture_key")):
                if k:
                    tgt[str(k)] = a
    return preds, obs


def _parse(iso):
    if not iso:
        return None
    try:
        d = _dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=_dt.timezone.utc)
    except Exception:
        return None


def lifecycle_state(f, pred, obs, now):
    """Mirror of the runtime lifecycle, plus copy/source/archive/demo classification."""
    teams = (f.get("home"), f.get("away"))
    if any(t in ARCHIVE_TEAMS for t in teams):
        return "ARCHIVE_ONLY"
    if tuple(teams) in DEMO_PAIRS or tuple(reversed(teams)) in DEMO_PAIRS:
        return "EXCLUDED_DEMO"
    status = (f.get("status") or "").lower()
    life = f.get("lifecycle_state") or ""
    ko = _parse(f.get("kickoffUtc"))
    is_finished = status == "finished" or life in FINISHED
    if is_finished:
        if f.get("recapReady") or life == "RECAP_READY":
            return "FINISHED_RECAP_READY"
        if obs is not None:
            return "FINISHED_OBSERVATION_READY"
        return "FINISHED_RECAP_PENDING"
    # upcoming / live
    has_copy = bool(pred and (pred.get("copy_version") or ((pred.get("i18n") or {}).get("zh") or {}).get("prediction", {}).get("primary_direction")))
    if not pred:
        return "SOURCE_MISSING"
    if ko and now:
        mins = (ko - now).total_seconds() / 60.0
        if mins <= 0:
            return "LIVE_OR_LOCKED"
        if mins <= T30_MIN:
            t = (pred.get("t30") or {}).get("status")
            return "T30_READY" if t in ("ready", "skipped") else "T30_WINDOW_PENDING"
    return "UPCOMING_PREDICTION_READY" if has_copy else "UPCOMING_REVIEW_REQUIRED"


def model_source(pred):
    return (pred.get("model_fields") or {}).get("source") if pred else None


def build(date, now_iso=None):
    man = _load(MANIFEST) or _load(FALLBACK) or {}
    preds, obs = _preds_obs()
    now = _parse(now_iso) or _parse(man.get("generated_at")) or _parse(date + "T12:00:00+00:00")
    rows = []
    for f in man.get("fixtures", []):
        fk = str(f.get("id") or f.get("external_game_id"))
        pred = preds.get(fk) or preds.get(str(f.get("id")))
        ob = obs.get(fk) or obs.get(str(f.get("id")))
        st = lifecycle_state(f, pred, ob, now)
        rows.append({"fixture_id": fk, "match": "%s vs %s" % (f.get("home"), f.get("away")),
                     "kickoff_time": f.get("kickoffUtc"), "status": f.get("status"),
                     "lifecycle_state": st, "model_source": model_source(pred),
                     "has_copy": bool(pred), "has_observation": ob is not None,
                     "recap_ready": bool(f.get("recapReady")), "_ko": f.get("kickoffUtc")})

    def ko_key(r):
        d = _parse(r["_ko"]); return d or _dt.datetime.max.replace(tzinfo=_dt.timezone.utc)

    upcoming = sorted([r for r in rows if r["lifecycle_state"] in
                       ("UPCOMING_PREDICTION_READY", "UPCOMING_REVIEW_REQUIRED", "T30_WINDOW_PENDING", "T30_READY")], key=ko_key)
    finished = sorted([r for r in rows if r["lifecycle_state"] in
                       ("FINISHED_RECAP_READY", "FINISHED_OBSERVATION_READY", "FINISHED_RECAP_PENDING")], key=ko_key, reverse=True)

    # primary: earliest upcoming, source-qualified (NOT operator_estimated), has copy, ready (not review-required)
    primary = next((r for r in upcoming
                    if r["model_source"] in SOURCE_QUALIFIED and r["lifecycle_state"] in ("UPCOMING_PREDICTION_READY", "T30_WINDOW_PENDING", "T30_READY")), None)
    for r in rows:
        r["active_content_role"] = "watchlist"
        r["reason_for_role"] = ""
    blocked = []
    if primary:
        primary["active_content_role"] = "primary_prediction"
        primary["reason_for_role"] = "earliest upcoming source-qualified (%s) match with reviewed copy" % primary["model_source"]
    else:
        blocked.append({"item": "primary_prediction", "state": "PRIMARY_REVIEW_REQUIRED",
                        "reason": "no upcoming source-qualified match with reviewed copy"})
    # secondary: next upcoming with copy (incl operator_estimated, labelled), excluding primary, cap 2
    secondary = []
    for r in upcoming:
        if primary and r["fixture_id"] == primary["fixture_id"]:
            continue
        if r["has_copy"]:
            r["active_content_role"] = "secondary_prediction"
            r["reason_for_role"] = ("secondary upcoming with reviewed copy"
                                    + (" (operator_estimated — labelled, never primary)" if r["model_source"] == "operator_estimated" else ""))
            secondary.append(r)
        if len(secondary) >= 2:
            break
    # latest_recap: most recent finished with observation/recap; PENDING if no score
    latest_recap = None
    finished_pending = []
    for r in finished:
        if r["lifecycle_state"] in ("FINISHED_RECAP_READY", "FINISHED_OBSERVATION_READY"):
            if latest_recap is None:
                r["active_content_role"] = "latest_recap"
                r["reason_for_role"] = "most recent finished tracked match (%s)" % r["lifecycle_state"]
                latest_recap = r
        else:
            finished_pending.append(r)
    next_upcoming = next((r for r in upcoming if not (primary and r["fixture_id"] == primary["fixture_id"])), None)
    excl_arch = [r for r in rows if r["lifecycle_state"] == "ARCHIVE_ONLY"]
    excl_demo = [r for r in rows if r["lifecycle_state"] == "EXCLUDED_DEMO"]
    for r in excl_arch:
        r["active_content_role"] = "archive_only"; r["reason_for_role"] = "WC-2022 archive — excluded from active"
    for r in excl_demo:
        r["active_content_role"] = "excluded"; r["reason_for_role"] = "legacy demo fixture — excluded"

    nxt = ("review/select an upcoming source-qualified primary" if not primary
           else "build recap for finished tracked matches" if finished_pending
           else "primary set; confirm T-30 at KO-30; hold for Owner per-channel GO")
    out = {
        "active_date": date, "generated_at": now_iso or man.get("generated_at"),
        "current_time_basis": now.isoformat() if now else None,
        "built_by": "mvp2_homepage_lifecycle_selector.py",
        "primary_prediction": _slim(primary), "secondary_predictions": [_slim(r) for r in secondary],
        "latest_recap": _slim(latest_recap), "next_upcoming": _slim(next_upcoming),
        "finished_pending_recap": [_slim(r) for r in finished_pending],
        "excluded_archive": [_slim(r) for r in excl_arch], "excluded_demo": [_slim(r) for r in excl_demo],
        "blocked_items": blocked, "all_fixtures": [_slim(r) for r in rows],
        "operator_next_action": nxt, "send_status": "HOLD",
    }
    return out


def _slim(r):
    if not r:
        return None
    return {k: r.get(k) for k in ("fixture_id", "match", "kickoff_time", "status", "lifecycle_state",
                                  "model_source", "active_content_role", "reason_for_role",
                                  "has_copy", "has_observation", "recap_ready")}


def cmd_build(date, now_iso, write_fe=True):
    out = build(date, now_iso)
    OUT_DOCS.mkdir(parents=True, exist_ok=True)
    (OUT_DOCS / ("%s.json" % date)).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if write_fe:
        OUT_FE.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    p = out["primary_prediction"]
    print("LIFECYCLE · %s · basis=%s" % (date, out["current_time_basis"]))
    print("  primary:   %s" % (("%s [%s]" % (p["match"], p["lifecycle_state"])) if p else "PRIMARY_REVIEW_REQUIRED (blocked)"))
    print("  secondary: %s" % (" · ".join("%s(%s)" % (r["match"], r["model_source"]) for r in out["secondary_predictions"]) or "none"))
    print("  recap:     %s" % ((out["latest_recap"]["match"] + " [" + out["latest_recap"]["lifecycle_state"] + "]") if out["latest_recap"] else "RECAP_PENDING"))
    print("  next:      %s" % (out["next_upcoming"]["match"] if out["next_upcoming"] else "—"))
    print("  excluded:  archive=%d demo=%d · pending_recap=%d · NEXT: %s" %
          (len(out["excluded_archive"]), len(out["excluded_demo"]), len(out["finished_pending_recap"]), out["operator_next_action"]))
    return 0


def cmd_validate(date, now_iso):
    out = build(date, now_iso)
    fails = []
    p = out["primary_prediction"]
    if p and "FINISHED" in p["lifecycle_state"]:
        fails.append("primary is a FINISHED match")
    if p and p["model_source"] == "operator_estimated":
        fails.append("primary is operator_estimated")
    if p and p["lifecycle_state"] in ("ARCHIVE_ONLY", "EXCLUDED_DEMO"):
        fails.append("primary is archive/demo")
    if not p and not out["blocked_items"]:
        fails.append("no primary and no PRIMARY_REVIEW_REQUIRED block")
    for r in out["secondary_predictions"]:
        if "FINISHED" in r["lifecycle_state"]:
            fails.append("secondary %s is finished" % r["fixture_id"])
    if out["latest_recap"] and "FINISHED" not in out["latest_recap"]["lifecycle_state"]:
        fails.append("latest_recap is not a finished match")
    if out.get("send_status") != "HOLD":
        fails.append("send_status not HOLD")
    for x in fails:
        print("FAIL  %s" % x)
    if fails:
        print("LIFECYCLE VALIDATE FAIL — %d" % len(fails)); return 1
    print("LIFECYCLE VALIDATE PASS (primary upcoming+source-qualified · no finished/op-est/archive primary · recap finished · HOLD)")
    return 0


def cmd_report(date):
    out = _load(OUT_DOCS / ("%s.json" % date))
    if not out:
        print("FAIL  no lifecycle artifact (run build --date %s)" % date); return 1
    print(json.dumps(out, ensure_ascii=False, indent=2)); return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["build", "validate", "report"])
    ap.add_argument("--date", default="")
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    date = a.date or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    now_iso = a.now or None
    if a.cmd == "validate":
        return cmd_validate(date, now_iso)
    if a.cmd == "report":
        return cmd_report(date)
    return cmd_build(date, now_iso)


if __name__ == "__main__":
    sys.exit(main())
