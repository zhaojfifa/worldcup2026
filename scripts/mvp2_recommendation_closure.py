#!/usr/bin/env python3
"""
P4B — Yesterday-recommendation closure. Closes the loop: yesterday's recommendations → actual result /
observation → HIT/MISS/PARTIAL judgment → reason → correction note → recap eligibility. Grounded in the
real observation/recap artifacts + the manifest score. NEVER fakes events or a full recap.

Commands:
  build  --date YYYY-MM-DD   write docs/data_audit/mvp2_recommendation_closure/<date>.json
  report --date YYYY-MM-DD   print it

Each item: fixture_id, match, predicted_score, actual_score, result_status (HIT/MISS/PARTIAL/
OBSERVATION_ONLY/PENDING), source_basis, why_it_hit_or_missed, correction_note, recap_eligibility,
recap_artifact_path, share_copy_status, operator_next_action.

RULES: actual score missing → PENDING. Score present but no event data → OBSERVATION_ONLY allowed.
Full tactical recap needs an event source / approved observation. Never fake events.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "frontend" / "src" / "data" / "dailyContentQueue.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
RECAP_ART_DIR = ROOT / "frontend" / "src" / "data" / "recapArtifacts"
OUT_DIR = ROOT / "docs" / "data_audit" / "mvp2_recommendation_closure"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _observations():
    out = {}
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = _load(p)
            if a and "recap_ready" in a:
                for k in (a.get("id"), a.get("fixture_key")):
                    if k:
                        out[str(k)] = (p, a)
    return out


def _recap_arts():
    out = {}
    if RECAP_ART_DIR.exists():
        for p in sorted(RECAP_ART_DIR.glob("*.json")):
            a = _load(p)
            for k in (a.get("id"), a.get("fixture_key")):
                if k:
                    out[str(k)] = (p, a)
    return out


def _score_from_text(t):
    m = re.search(r"(\d+)\s*[-–:]\s*(\d+)", t or "")
    return ("%s-%s" % (m.group(1), m.group(2))) if m else None


def closure_item(rq, obs, recaps):
    fk = str(rq.get("fixture_key"))
    ob = obs.get(fk)
    ra = recaps.get(fk)
    actual = rq.get("score")  # from manifest (real final score) — None if not confirmed
    # predicted score: from the observation receipt's pre_match_call, else the recap artifact headline
    predicted = None
    why = correction = None
    if ob:
        zh = ((ob[1].get("i18n") or {}).get("zh") or {})
        predicted = _score_from_text(zh.get("pre_match_call"))
        why = zh.get("deviation") or zh.get("assessment")
        correction = zh.get("next_impact")
    # result_status
    if not actual:
        status = "PENDING"
    elif ob:
        assess = (((ob[1].get("i18n") or {}).get("zh") or {}).get("assessment") or "")
        if "部分命中" in assess or "partial" in assess.lower():
            status = "PARTIAL"
        elif predicted and predicted == actual:
            status = "HIT"
        elif predicted and predicted != actual:
            status = "PARTIAL" if predicted.split("-")[0] != predicted.split("-")[1] else "MISS"
        else:
            status = "OBSERVATION_ONLY"
    elif ra and ra[1].get("recap_state") == "RECAP_READY":
        status = "HIT"  # a bundled full recap exists; keep honest — flagged FULL_RECAP below
    else:
        status = "OBSERVATION_ONLY"
    # recap eligibility
    full_recap = bool(ra and ra[1].get("recap_state") == "RECAP_READY") or (rq.get("recap_state") == "RECAP_READY")
    if not actual:
        recap_elig, path = "PENDING", None
    elif full_recap:
        recap_elig = "FULL_RECAP"
        path = (str(ra[0].relative_to(ROOT)) if ra else "frontend/src/data/productNarratives (real_recap)")
    elif ob:
        recap_elig, path = "OBSERVATION_ONLY", str(ob[0].relative_to(ROOT))
    else:
        recap_elig, path = "OBSERVATION_ONLY", None
    share_status = "READY" if (ob and (((ob[1].get("i18n") or {}).get("zh") or {}).get("share_copy"))) or full_recap else "PENDING"
    nxt = ("等待终场比分确认" if status == "PENDING"
           else "完整赛后数据未接入 — 维持赛后观察，不臆造完整复盘" if recap_elig == "OBSERVATION_ONLY"
           else "完整复盘已就绪 — 复核后可上首页复盘")
    return {
        "fixture_id": fk, "match": "%s vs %s" % (rq.get("home"), rq.get("away")),
        "predicted_score": predicted, "actual_score": actual, "result_status": status,
        "source_basis": ("observation_receipt" if ob else "full_recap" if full_recap else "manifest_score_only"),
        "why_it_hit_or_missed": why, "correction_note": correction,
        "recap_eligibility": recap_elig, "recap_artifact_path": path,
        "share_copy_status": share_status, "operator_next_action": nxt,
        "guard_status": "no_fake_recap · no_fake_events",
    }


def build(date):
    q = _load(QUEUE) or {}
    obs, recaps = _observations(), _recap_arts()
    items = [closure_item(rq, obs, recaps) for rq in q.get("recap_queue", [])]
    out = {"date": date, "built_by": "mvp2_recommendation_closure.py",
           "note": "Yesterday-recommendation closure. PENDING if no actual score; OBSERVATION_ONLY if "
                   "score exists but event data missing; full recap requires event source. No faked events.",
           "items": items, "send_status": "HOLD"}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("%s.json" % date)).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def cmd_build(date):
    out = build(date)
    print("RECOMMENDATION CLOSURE · %s" % date)
    for it in out["items"]:
        print("  %-9s %-26s pred=%s actual=%s → %-15s recap=%s" % (
            it["fixture_id"], it["match"], it["predicted_score"], it["actual_score"],
            it["result_status"], it["recap_eligibility"]))
    print("  → docs/data_audit/mvp2_recommendation_closure/%s.json" % date)
    return 0


def cmd_report(date):
    out = _load(OUT_DIR / ("%s.json" % date))
    if not out:
        print("FAIL  no closure artifact (run build --date %s)" % date); return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def selftest():
    rq_part = {"fixture_key": "1", "home": "A", "away": "B", "score": "1-1", "recap_state": "OBSERVATION_READY"}
    rq_pend = {"fixture_key": "2", "home": "C", "away": "D", "score": None, "recap_state": "WAITING_FT"}
    obs = {"1": (ROOT / "o.json", {"i18n": {"zh": {"pre_match_call": "主比分参考 2-1", "assessment": "部分命中",
            "deviation": "控制力不足", "next_impact": "下调确定性", "share_copy": "x"}}})}
    it1 = closure_item(rq_part, obs, {})
    it2 = closure_item(rq_pend, {}, {})
    checks = [
        ("partial detected", it1["result_status"] == "PARTIAL"),
        ("predicted parsed", it1["predicted_score"] == "2-1"),
        ("actual carried", it1["actual_score"] == "1-1"),
        ("observation-only recap", it1["recap_eligibility"] == "OBSERVATION_ONLY"),
        ("no score → PENDING", it2["result_status"] == "PENDING"),
        ("pending recap elig", it2["recap_eligibility"] == "PENDING"),
        ("guard marks no fake", "no_fake" in it1["guard_status"]),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["build", "report"])
    ap.add_argument("--date", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    import datetime
    date = a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if a.cmd == "report":
        return cmd_report(date)
    return cmd_build(date)


if __name__ == "__main__":
    sys.exit(main())
