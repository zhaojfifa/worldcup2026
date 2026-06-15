#!/usr/bin/env python3
"""
P7 P0-8 Daily readiness guard (Owner: the product must not depend on chat memory or slate order).

Enforces the daily content+update invariant END-TO-END from persisted artifacts:
  selected_hotspot → prediction artifact → score-call hook → share copy/card → T-30 slot →
  observation/recap for a completed selected hotspot → next-day carryover, with no forbidden
  vocabulary, no fake recap, no auto-send.

Checks (frontend-bundled artifacts + runtime manifest):
  1. selected_hotspot present for the current slate (status=active, fixture_key) — else FAIL/missing.
  2. selected hotspot resolves to a PREDICTION artifact (fixture_key match).
  3. the prediction artifact carries a SCORE-CALL hook (zh prediction.score_call) + field_sources
     tagging (operator_confirmed|operator_estimated|model|generated|unavailable); win_prob/confidence must
     be unavailable/null — the frontend never invents them.
  4. share copy (operations.share_copy) + share card route key (fixture_key) present.
  5. a T-30 slot exists with a valid status (pending|ready|skipped); pending => no faked update_text.
  6. the selected hotspot appears in the runtime slate as a scheduled fixture (homepage lead == it).
  7. every FINISHED fixture that is artifact-tracked has an observation/recap artifact (carryover by
     fixture_key OR id); recap_ready may be false (observation receipt) — never a fake recap.
  8. no betting/trading vocabulary; safety.no_auto_send true on artifacts.

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
FALLBACK_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"

FINISHED = {"FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}
BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "竞猜", "让球", "大小球", "跟单", "串关",
           "odds", "handicap", "bookmaker", "wager", "betting",
           "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược"]
VALID_SOURCES = {"operator_confirmed", "operator_estimated", "model", "generated", "unavailable"}
VALID_MODEL_SOURCES = {"computed", "seed", "operator_estimated", "operator_confirmed", "unavailable"}


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _lead_key(f):
    return f.get("id") or f.get("external_game_id")


def _classify(a):
    return "observation" if "recap_ready" in a else "prediction"


def scan(sel, predictions, observations, manifest):
    """sel: dict|None ; predictions/observations: list[dict] ; manifest: dict|None"""
    fails, warns = [], []

    # 1. selected hotspot present
    if not sel or sel.get("status") != "active" or not sel.get("fixture_key"):
        fails.append("selected_hotspot missing/inactive (no authoritative daily pick)")
        return fails, warns  # nothing else resolvable
    key = sel["fixture_key"]

    # 1b. R2 staleness gate — selected hotspot must not be older than the slate.
    slate_date = (manifest or {}).get("generated_for_date")
    if slate_date and sel.get("date") and sel["date"] < slate_date:
        fails.append("selected_hotspot is STALE: selection date %s < slate date %s (refresh the hotspot)"
                     % (sel["date"], slate_date))

    # 2. resolves to a prediction artifact
    pred = next((a for a in predictions if a.get("fixture_key") == key), None)
    if not pred:
        fails.append("selected_hotspot %r has NO prediction artifact" % key)
        return fails, warns
    zh = (pred.get("i18n") or {}).get("zh") or {}
    pz = zh.get("prediction") or {}

    # 3. score-call hook + field_sources + no fake numerics
    if not pz.get("score_call"):
        fails.append("prediction artifact %r missing the score-call hook (zh prediction.score_call)" % key)
    fs = pred.get("field_sources") or {}
    if not fs:
        fails.append("prediction artifact %r missing field_sources (P7 source tagging)" % key)
    for f, src in fs.items():
        if src not in VALID_SOURCES:
            fails.append("prediction artifact %r field_sources.%s=%r not a valid source tag" % (key, f, src))
    for numeric in ("win_prob", "confidence"):
        # if a model number is claimed, it must be genuinely model-sourced (P1) — operator-typed
        # numerics for these are NOT allowed (no fake probability). unavailable/null is the MVP norm.
        if fs.get(numeric) in ("operator_confirmed", "operator_estimated"):
            fails.append("prediction artifact %r %s must not be operator-typed (no fake probability)" % (key, numeric))
        if pz.get("confidence") not in (None, "") and numeric == "confidence":
            warns.append("prediction artifact %r has a non-null confidence — ensure it is model-sourced, not a probability promise" % key)

    # 3b. P8 P0 — the selected hotspot's artifact must carry the reconnected content-fact blocks.
    sf = pred.get("source_facts")
    if not isinstance(sf, dict) or not sf.get("fixture_source") or sf.get("data_mode") not in ("api", "seed", "manual", "operator"):
        fails.append("prediction artifact %r missing/invalid source_facts (P8 content-fact reconnection)" % key)
    mf = pred.get("model_fields")
    if not isinstance(mf, dict):
        fails.append("prediction artifact %r missing model_fields (P8 content-fact reconnection)" % key)
    else:
        if mf.get("source") not in VALID_MODEL_SOURCES:
            fails.append("prediction artifact %r model_fields.source=%r not a valid tag" % (key, mf.get("source")))
        # win_prob/confidence acceptable ONLY as null/unavailable (never an invented number).
        if mf.get("win_prob") is not None:
            fails.append("prediction artifact %r model_fields.win_prob must be null (no fake probability)" % key)
        if mf.get("confidence") is not None:
            fails.append("prediction artifact %r model_fields.confidence must be null (no numeric confidence)" % key)
        if mf.get("no_fake_probability") is not True:
            fails.append("prediction artifact %r model_fields.no_fake_probability must be true" % key)

    # 4. share copy + card key
    if not (zh.get("operations") or {}).get("share_copy"):
        fails.append("prediction artifact %r missing operations.share_copy (share copy)" % key)
    if not pred.get("fixture_key"):
        fails.append("prediction artifact %r missing fixture_key (share card route)" % key)

    # 5. T-30 slot
    t = pred.get("t30")
    if not isinstance(t, dict) or t.get("status") not in ("pending", "ready", "skipped"):
        fails.append("prediction artifact %r missing a valid t30 slot (status pending|ready|skipped)" % key)
    elif t.get("status") == "pending" and t.get("update_text"):
        fails.append("prediction artifact %r t30 is pending but has update_text (faked update)" % key)

    # 6. selected hotspot is in the runtime slate as a scheduled fixture (homepage lead == it).
    #    R2a: the LOCAL bundled/static manifest IS the fresh fallback the homepage uses when the
    #    backend is stale — so it MUST contain the selected hotspot (else the fallback is BLOCKED).
    if manifest:
        fxs = manifest.get("fixtures", [])
        row = next((f for f in fxs if _lead_key(f) == key), None)
        if not row:
            fails.append("selected_hotspot %r NOT in the bundled/static manifest — fresh fallback would be BLOCKED (R2a)" % key)
        elif row.get("lifecycle_state") in FINISHED:
            warns.append("selected_hotspot %r is already finished in the slate (lead should roll to the next pick)" % key)
        # 7. finished + artifact-tracked fixtures must have an observation (carryover)
        obs_keys = {o.get("fixture_key") for o in observations} | {str(o.get("id")) for o in observations}
        for f in fxs:
            if f.get("lifecycle_state") in FINISHED:
                lk = _lead_key(f)
                if lk and (lk in obs_keys or str(f.get("id")) in obs_keys):
                    continue
                # only a soft warning unless it is the selected hotspot itself
                msg = "finished fixture %s vs %s has no observation/recap artifact (carryover)" % (f.get("home"), f.get("away"))
                (fails if lk == key else warns).append(msg)

    # 8. no fake recap / no auto-send / no betting vocab
    for o in observations:
        if "recap_ready" not in o:
            fails.append("observation artifact missing recap_ready (fake-recap risk)")
    for a in predictions + observations:
        blob = json.dumps(a, ensure_ascii=False)
        low = blob.lower()
        for w in BETTING:
            if (w.lower() in low) if w.isascii() else (w in blob):
                fails.append("betting/trading vocab %r in artifact %s" % (w, a.get("fixture_key") or a.get("id")))
        safety = a.get("safety") or {}
        if "no_auto_send" in safety and safety.get("no_auto_send") is not True:
            fails.append("artifact %s safety.no_auto_send must be true" % (a.get("fixture_key") or a.get("id")))
    return fails, warns


def selftest():
    good_sel = {"status": "active", "fixture_key": "manual:X-Y-20260614", "home": "X", "away": "Y"}
    good_pred = {"fixture_key": "manual:X-Y-20260614", "prediction_confirmed": True,
                 "field_sources": {"score_call": "operator_confirmed", "win_prob": "unavailable", "confidence": "unavailable"},
                 "source_facts": {"fixture_source": "manual_slate", "data_mode": "manual",
                                  "has_model_fields": True, "source_refs": [], "missing_fields": ["win_prob", "confidence"]},
                 "model_fields": {"win_prob": None, "recommended_score": "2-1", "backup_scores": ["1-1"],
                                  "risk_level": "中高", "confidence": None, "source": "operator_estimated",
                                  "model_status": "operator_estimated", "no_fake_probability": True},
                 "t30": {"status": "pending", "update_text": None},
                 "safety": {"no_auto_send": True},
                 "i18n": {"zh": {"prediction": {"score_call": "2-1", "confidence": None},
                                 "operations": {"share_copy": "今日主推 X vs Y ..."}}}}
    good_obs = {"fixture_key": "af:1489371", "id": "1489371", "recap_ready": False, "safety": {"no_auto_send": True},
                "i18n": {"zh": {}}}
    good_manifest = {"fixtures": [
        {"external_game_id": "manual:X-Y-20260614", "home": "X", "away": "Y", "lifecycle_state": "SCHEDULED"},
        {"id": "1489371", "external_game_id": "af:1489371", "home": "Brazil", "away": "Morocco", "lifecycle_state": "RECAP_PENDING"},
    ]}
    checks = []
    f, w = scan(good_sel, [good_pred], [good_obs], good_manifest)
    checks.append(("clean passes", f == []))
    checks.append(("stale selection caught", any("STALE" in x for x in scan(
        dict(good_sel, date="2026-06-14"), [good_pred], [good_obs],
        dict(good_manifest, generated_for_date="2026-06-15"))[0])))
    checks.append(("missing selection caught", scan(None, [good_pred], [good_obs], good_manifest)[0] != []))
    checks.append(("no-artifact caught", any("NO prediction artifact" in x for x in scan(
        {"status": "active", "fixture_key": "manual:Z"}, [good_pred], [], good_manifest)[0])))
    checks.append(("missing score-call caught", any("score-call" in x for x in scan(
        good_sel, [dict(good_pred, i18n={"zh": {"prediction": {}, "operations": {"share_copy": "x"}}})], [good_obs], good_manifest)[0])))
    checks.append(("faked pending t30 caught", any("faked update" in x for x in scan(
        good_sel, [dict(good_pred, t30={"status": "pending", "update_text": "已改判"})], [good_obs], good_manifest)[0])))
    checks.append(("operator win_prob caught", any("no fake probability" in x for x in scan(
        good_sel, [dict(good_pred, field_sources={"score_call": "operator_confirmed", "win_prob": "operator_confirmed"})], [good_obs], good_manifest)[0])))
    checks.append(("betting vocab caught", any("betting" in x for x in scan(
        good_sel, [dict(good_pred, i18n={"zh": {"prediction": {"score_call": "2-1"}, "operations": {"share_copy": "看 赔率"}}})], [good_obs], good_manifest)[0])))
    fin_manifest = {"fixtures": [{"external_game_id": "manual:F-G-20260614", "id": None,
                                  "home": "F", "away": "G", "lifecycle_state": "RECAP_PENDING"}]}
    checks.append(("missing observation for finished selected caught", any("carryover" in x for x in scan(
        {"status": "active", "fixture_key": "manual:F-G-20260614", "home": "F", "away": "G"},
        [dict(good_pred, fixture_key="manual:F-G-20260614")], [], fin_manifest)[0])))
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    sel = _load(SEL)
    predictions, observations = [], []
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            try:
                a = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                sys.stdout.write("FAIL  %s invalid JSON (%s)\n" % (p.name, e))
                return 1
            (observations if _classify(a) == "observation" else predictions).append(a)
    manifest = _load(MANIFEST) or _load(FALLBACK_MANIFEST)
    fails, warns = scan(sel, predictions, observations, manifest)
    for w in warns:
        sys.stdout.write("WARN  %s\n" % w)
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("DAILY READINESS FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("DAILY READINESS PASS (selected_hotspot → artifact → score-call → share → t30 → carryover; %d warning(s))\n" % len(warns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
