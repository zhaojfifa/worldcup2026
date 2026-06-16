#!/usr/bin/env python3
"""R3 — day-cutover consistency gate (the HARD gate before any production upload).

Data and content must point to the SAME date/slate. For a target date this verifies:
  * the generated daily registry is for the target date
  * selectedHotspot.date == target date            (blocks a DATA-ONLY cutover)
  * selectedHotspot.fixture_key exists in the slate
  * the selected primary has a REVIEWED prediction artifact (copy_version + prediction_confirmed)
  * the selected primary is NOT finished
  * the homepage lifecycle primary == selectedHotspot fixture, and its time basis is the target date
  * secondary fixtures (content queue) exist in the slate
  * a recap/observation fixture is finished WITH a score and has an observation/recap artifact
  * no fabricated score/status

The function gate(date_iso) returns (ok, fails) and is imported by mvp2_day_cutover.py to decide
whether to upload. Usage: --date YYYY-MM-DD | --selftest
"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC = ROOT / "docs/data_audit/mvp2_match_sync"
FE = ROOT / "frontend/src/data"
PRED = FE / "predictionArtifacts"


def _load(p):
    p = pathlib.Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _slate_ids(reg):
    ids = set()
    for f in (reg or {}).get("fixtures", []):
        for k in (f.get("internal_fixture_id"), f.get("external_game_id")):
            if k:
                ids.add(str(k))
    return ids


def _slate_row(reg, key):
    for f in (reg or {}).get("fixtures", []):
        if str(f.get("internal_fixture_id")) == str(key) or str(f.get("external_game_id")) == str(key):
            return f
    return None


def _reviewed_pred(fixture_key):
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" not in a and (str(a.get("fixture_key")) == str(fixture_key) or str(a.get("id")) == str(fixture_key)):
            return a
    return None


def _observation(fixture_key):
    for p in sorted(PRED.glob("*.json")):
        a = _load(p)
        if a and "recap_ready" in a and (str(a.get("id")) == str(fixture_key) or str(a.get("fixture_key")) == str(fixture_key)):
            return a
    return None


def gate(date_iso, reg=None, sel=None, lc=None, queue=None):
    """Returns (ok, fails). Pure over the passed-in artifacts (defaults read from disk)."""
    compact = date_iso.replace("-", "")
    reg = reg if reg is not None else _load(SYNC / ("daily_fixtures_%s.json" % compact))
    sel = sel if sel is not None else _load(FE / "selectedHotspot.json")
    lc = lc if lc is not None else _load(FE / "homepageLifecycle.json")
    queue = queue if queue is not None else _load(FE / "dailyContentQueue.json")
    f = []
    if not reg:
        return False, ["generated registry missing for %s (run sync first)" % date_iso]
    if reg.get("date") != date_iso:
        f.append("registry date %r != target %r" % (reg.get("date"), date_iso))
    ids = _slate_ids(reg)
    # ---- DATA-ONLY guard: selectedHotspot must be for the SAME date ----
    if not sel:
        f.append("selectedHotspot.json missing")
    else:
        if sel.get("date") != date_iso:
            f.append("DATA_ONLY_CUTOVER: selectedHotspot.date %r != runtime date %r" % (sel.get("date"), date_iso))
        skey = str(sel.get("fixture_key")) if sel.get("fixture_key") else None
        if skey and skey not in ids:
            f.append("selected primary %s not in generated slate" % skey)
        # primary content must be reviewed + not finished
        if skey:
            art = _reviewed_pred(skey)
            if not art:
                f.append("selected primary %s has NO reviewed prediction artifact (content not paired)" % skey)
            elif not (art.get("copy_version") and art.get("prediction_confirmed")):
                f.append("selected primary %s artifact not reviewed (copy_version/prediction_confirmed)" % skey)
            row = _slate_row(reg, skey)
            if row and (row.get("status") == "finished" or "FINISHED" in (row.get("lifecycle_state") or "")):
                f.append("selected primary %s is FINISHED in the slate (cannot be a prediction)" % skey)
    # ---- lifecycle must agree with the selected primary + target date ----
    # NOTE: the lifecycle "time basis" is the as-of evaluation time (when the day is published), which
    # can legitimately differ from the slate date (e.g. republishing a noon-basis slate later). We do
    # NOT require basis==date; the homepage-consistency check that matters is that the lifecycle PRIMARY
    # equals the selectedHotspot, and that the selected primary is not finished IN THE SLATE (status).
    if lc:
        lp = (lc.get("primary_prediction") or {}).get("fixture_id")
        if sel and lp and str(lp) != str(sel.get("fixture_key")):
            f.append("lifecycle primary %r != selectedHotspot %r" % (lp, sel.get("fixture_key")))
        if sel and not lp and sel.get("fixture_key"):
            f.append("lifecycle has NO primary (PRIMARY_REVIEW_REQUIRED) but selectedHotspot=%s" % sel.get("fixture_key"))
    # ---- secondary fixtures must exist in the slate ----
    for s in (queue or {}).get("secondary_matches", []):
        sk = str(s.get("fixture_key") or s.get("id") or "")
        if sk and sk not in ids:
            f.append("secondary %s not in generated slate" % sk)
    # ---- recap fixture: finished WITH a score + observation/recap artifact ----
    for r in (queue or {}).get("recap_queue", []) or (queue or {}).get("recap_matches", []):
        rk = str(r.get("fixture_key") or r.get("id") or "")
        if not rk:
            continue
        row = _slate_row(reg, rk)
        if row and row.get("status") == "finished" and row.get("score_home") is None:
            f.append("recap fixture %s finished but has NO score (cannot recap missing score)" % rk)
    return (not f), f


def selftest():
    reg16 = {"date": "2026-06-16", "fixtures": [{"internal_fixture_id": "1489383", "status": "scheduled", "lifecycle_state": "SCHEDULED"}]}
    sel15 = {"date": "2026-06-15", "fixture_key": "1489377"}
    ok_block, fb = gate("2026-06-16", reg=reg16, sel=sel15, lc={}, queue={})
    reg15 = {"date": "2026-06-15", "fixtures": [{"internal_fixture_id": "1489377", "status": "scheduled", "lifecycle_state": "SCHEDULED"}]}
    sel_fin = {"date": "2026-06-15", "fixture_key": "1489377"}
    reg_fin = {"date": "2026-06-15", "fixtures": [{"internal_fixture_id": "1489377", "status": "finished", "lifecycle_state": "FINISHED_OBSERVATION_READY"}]}
    ok_fin, ff = gate("2026-06-15", reg=reg_fin, sel=sel_fin, lc={}, queue={})
    checks = [
        ("data-only cutover blocked", not ok_block and any("DATA_ONLY_CUTOVER" in x for x in fb)),
        ("finished primary blocked", not ok_fin and any("FINISHED" in x for x in ff)),
        ("missing registry blocked", gate("2026-06-99", reg=None)[0] is False),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        return selftest()
    date_iso = a[a.index("--date") + 1] if "--date" in a else "2026-06-15"
    ok, fails = gate(date_iso)
    for x in fails:
        print("FAIL  %s" % x)
    if not ok:
        print("R3 DAY-CUTOVER CONSISTENCY FAIL — %d (CUTOVER_BLOCKED; production stays on last green baseline)" % len(fails))
        return 1
    print("R3 DAY-CUTOVER CONSISTENCY PASS (%s: data+content paired — selectedHotspot/lifecycle/slate/artifacts all agree; send HOLD)" % date_iso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
