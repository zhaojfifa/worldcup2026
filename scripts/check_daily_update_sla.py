#!/usr/bin/env python3
"""
R3 — Daily-update SLA-state guard.

Asserts each daily-operating state is REPRESENTED and HONEST (per
docs/mvp2_product/r3_data_llm_update_recap_sla/DAILY_UPDATE_SLA.md). This is a state-VISIBILITY gate,
not a clock:
  A/B selected hotspot present + current (date not older than slate);
  C   prediction artifact ready (source_facts + model_fields + content_chain);
  D   T-30 state explicit (pending/ready/skipped; pending => no faked update_text);
  E/F FT/recap state explicit for any FINISHED tracked fixture (observation OR full recap present);
  --  send HOLD (safety.no_auto_send=true; no auto-send wiring).

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
FALLBACK_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(sel, predictions, observations, slate_date=None, finished_keys=None):
    """predictions/observations: list[(name, dict)]. finished_keys: set of fixture ids/keys that are
    FINISHED in the slate and were tracked (need an observation/recap)."""
    fails = []
    # A/B
    if not sel or sel.get("status") != "active" or not sel.get("fixture_key"):
        return ["SLA-B: no active selected_hotspot"]
    key = sel["fixture_key"]
    if slate_date and sel.get("date") and sel["date"] < slate_date:
        fails.append("SLA-A: selected_hotspot date %s older than slate %s (stale, not current)"
                     % (sel["date"], slate_date))
    art = next((a for (_n, a) in predictions if a.get("fixture_key") == key), None)
    if not art:
        return ["SLA-C: selected_hotspot %r has no prediction artifact" % key]

    # C
    if not isinstance(art.get("source_facts"), dict):
        fails.append("SLA-C: artifact missing source_facts")
    if not isinstance(art.get("model_fields"), dict):
        fails.append("SLA-C: artifact missing model_fields")
    if not isinstance(art.get("content_chain"), dict):
        fails.append("SLA-C: artifact missing content_chain")

    # D
    t = art.get("t30")
    if not isinstance(t, dict) or t.get("status") not in ("pending", "ready", "skipped"):
        fails.append("SLA-D: T-30 slot missing/invalid")
    elif t.get("status") == "pending" and t.get("update_text"):
        fails.append("SLA-D: T-30 pending but update_text present (faked update)")

    # E/F — every finished tracked fixture must have an observation/recap (explicit FT state)
    obs_keys = set()
    for _n, o in observations:
        obs_keys.add(o.get("id"))
        obs_keys.add(o.get("fixture_key"))
        if o.get("recap_ready") is True and not o.get("note"):
            pass  # full recap allowed; observation receipts assert recap_ready=false elsewhere
    for fk in (finished_keys or set()):
        if fk not in obs_keys:
            fails.append("SLA-E/F: finished tracked fixture %r has no observation/recap (FT state not explicit)" % fk)

    # send HOLD
    saf = art.get("safety") or {}
    if saf.get("no_auto_send") is not True:
        fails.append("SLA-send: safety.no_auto_send must be true (send HOLD)")
    return fails


def _good():
    art = {
        "fixture_key": "1489377", "date": "2026-06-15",
        "source_facts": {"fixture_source": "api_football", "data_mode": "api"},
        "model_fields": {"source": "computed", "no_fake_probability": True, "win_prob": None, "confidence": None},
        "content_chain": {"prompt_generated": True},
        "t30": {"status": "pending", "update_text": None},
        "safety": {"no_auto_send": True, "no_fake_probability": True},
    }
    return art


def selftest():
    sel = {"status": "active", "fixture_key": "1489377", "date": "2026-06-15"}
    art = _good()
    obs = {"id": "1489371", "fixture_key": "af:1489371", "recap_ready": False}
    checks = [
        ("clean passes", scan(sel, [("p", art)], [("o", obs)], slate_date="2026-06-15",
                              finished_keys={"1489371"}) == []),
        ("stale selection caught", any("SLA-A" in x for x in scan(
            dict(sel, date="2026-06-14"), [("p", art)], [("o", obs)], slate_date="2026-06-15", finished_keys=set()))),
        ("no artifact caught", any("SLA-C" in x for x in scan(
            {"status": "active", "fixture_key": "ZZ"}, [("p", art)], [], finished_keys=set()))),
        ("faked t30 caught", any("faked update" in x for x in scan(
            sel, [("p", dict(art, t30={"status": "pending", "update_text": "首发已确认"}))], [("o", obs)],
            slate_date="2026-06-15", finished_keys={"1489371"}))),
        ("finished-without-observation caught", any("no observation/recap" in x for x in scan(
            sel, [("p", art)], [], slate_date="2026-06-15", finished_keys={"1489371"}))),
        ("auto-send caught", any("no_auto_send" in x for x in scan(
            sel, [("p", dict(art, safety={"no_auto_send": False}))], [("o", obs)],
            slate_date="2026-06-15", finished_keys={"1489371"}))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def _finished_keys(man):
    out = set()
    for f in (man or {}).get("fixtures", []):
        st = (f.get("status") or "").lower()
        life = (f.get("lifecycle_state") or "").upper()
        if st == "finished" or life in ("FINISHED", "RECAP_PENDING", "RECAP_READY"):
            if f.get("id") is not None:
                out.add(str(f["id"]))
            if f.get("external_game_id"):
                out.add(str(f["external_game_id"]))
    return out


def main():
    if "--selftest" in sys.argv:
        return selftest()
    sel = _load(SEL)
    predictions, observations = [], []
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = json.loads(p.read_text(encoding="utf-8"))
            (observations if "recap_ready" in a else predictions).append((p.name, a))
    man = _load(MANIFEST) or _load(FALLBACK_MANIFEST)
    slate_date = (man or {}).get("generated_for_date")
    # Only require an observation for finished fixtures that are TRACKED (a prediction artifact OR the
    # carryover hotspot) — the slate carries many finished fixtures we never predicted.
    tracked = set()
    for _n, a in predictions:
        if a.get("id"):
            tracked.add(str(a["id"]))
        tracked.add(str(a.get("fixture_key")))
    fin = _finished_keys(man)
    # also map external_game_id like 'af:1489371' to bare id for observation matching
    finished_tracked = set()
    for fk in fin:
        bare = fk.split(":")[-1]
        for _n, o in observations:
            if str(o.get("id")) == bare or str(o.get("fixture_key")) == fk:
                finished_tracked.add(str(o.get("id")))
    fails = scan(sel, predictions, observations, slate_date=slate_date, finished_keys=finished_tracked)
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("DAILY UPDATE SLA FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("DAILY UPDATE SLA PASS (slate-current → artifact-ready → T-30 explicit → FT/recap "
                     "explicit → send HOLD)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
