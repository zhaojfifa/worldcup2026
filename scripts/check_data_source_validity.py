#!/usr/bin/env python3
"""
R3 — Data-source validity guard.

Proves the selected daily hotspot rests on a VALID, source-tagged data chain (not mock, not faked):
  - selected_hotspot present/active with a fixture_key;
  - its prediction artifact exists;
  - source_facts present with a valid fixture_source/data_mode;
  - model_fields.source is one of the honest tags (computed/seed/operator_estimated/
    operator_confirmed/unavailable) — never 'mock'/'baseline';
  - when source==computed, source_refs must be present (real provenance);
  - win_prob / confidence are null and no_fake_probability=true;
  - selected_hotspot date is not older than the slate date (no stale-as-ready).

Optional live probe (--base-url): echo the live /api/v1/daily-fixtures freshness. A stale backend is
a WARN (the R2a fallback keeps the homepage correct) unless --strict makes it a FAIL.

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEL = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"
PRED_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
FALLBACK_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"

VALID_MODEL_SOURCES = {"computed", "seed", "operator_estimated", "operator_confirmed", "unavailable"}
MOCK_TOKENS = {"mock", "baseline", "name-hash", "name_hash", "random"}
VALID_DATA_MODES = {"api", "seed", "manual", "operator"}


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def scan(sel, artifacts, slate_date=None):
    fails = []
    if not sel or sel.get("status") != "active" or not sel.get("fixture_key"):
        return ["selected_hotspot missing/inactive (no authoritative daily pick)"]
    key = sel["fixture_key"]
    if slate_date and sel.get("date") and sel["date"] < slate_date:
        fails.append("selected_hotspot STALE: selection date %s < slate date %s" % (sel["date"], slate_date))
    art = next((a for (_n, a) in artifacts if a.get("fixture_key") == key), None)
    if not art:
        return ["selected_hotspot %r has NO prediction artifact" % key]

    sf = art.get("source_facts")
    if not isinstance(sf, dict):
        fails.append("artifact %r missing source_facts" % key)
    else:
        if not sf.get("fixture_source"):
            fails.append("artifact %r source_facts.fixture_source missing" % key)
        if sf.get("data_mode") not in VALID_DATA_MODES:
            fails.append("artifact %r source_facts.data_mode=%r invalid" % (key, sf.get("data_mode")))

    mf = art.get("model_fields")
    if not isinstance(mf, dict):
        fails.append("artifact %r missing model_fields" % key)
    else:
        src = mf.get("source")
        if src not in VALID_MODEL_SOURCES:
            fails.append("artifact %r model_fields.source=%r invalid" % (key, src))
        # the model source must not be a mock/name-hash placeholder
        status = str(mf.get("model_status") or "").lower()
        if any(tok in status for tok in MOCK_TOKENS) or (src and str(src).lower() in MOCK_TOKENS):
            fails.append("artifact %r model source looks like mock/baseline noise (status=%r)" % (key, mf.get("model_status")))
        if src == "computed" and not (sf or {}).get("source_refs"):
            fails.append("artifact %r model_fields.source=computed but no source_refs (provenance missing)" % key)
        if mf.get("win_prob") is not None:
            fails.append("artifact %r win_prob must be null (no fake probability)" % key)
        if mf.get("confidence") is not None:
            fails.append("artifact %r confidence must be null (no numeric confidence)" % key)
        if mf.get("no_fake_probability") is not True:
            fails.append("artifact %r no_fake_probability must be true" % key)
    return fails


def live_probe(base_url, strict=False):
    out, warns = [], []
    url = base_url.rstrip("/") + "/api/v1/daily-fixtures"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        warns.append("live probe could not reach %s (%s)" % (url, e))
        return out, warns
    n = len(data.get("fixtures") or [])
    date = data.get("date") or data.get("generated_for_date")
    fresh = (data.get("freshness") or {})
    stale = bool(fresh.get("stale"))
    out.append("live GET %s -> %d fixtures · backend date=%s · stale=%s" % (url, n, date, stale))
    if stale:
        (out if not strict else warns).append(
            "live backend manifest is stale — R2a fallback (bundled/static) keeps the homepage correct"
            + (" [STRICT=FAIL]" if strict else " [WARN, P1: operator upload]"))
    return out, (warns if strict else [w for w in warns if "could not reach" in w] + ([] if not stale else []))


def _good():
    return {
        "fixture_key": "1489377",
        "source_facts": {"fixture_source": "api_football", "data_mode": "api",
                         "has_model_fields": True, "source_refs": ["kaggle Elo: …"], "missing_fields": ["win_prob", "confidence"]},
        "model_fields": {"win_prob": None, "recommended_score": "1-0", "backup_scores": ["2-0"],
                         "risk_level": "中", "confidence": None, "source": "computed",
                         "model_status": "scoutscore_v0_2_elo_form", "no_fake_probability": True},
    }


def selftest():
    sel = {"status": "active", "fixture_key": "1489377", "date": "2026-06-15"}
    good = _good()
    checks = [
        ("clean passes", scan(sel, [("g", good)]) == []),
        ("no selection caught", any("missing/inactive" in x for x in scan({"status": "retired"}, [("g", good)]))),
        ("no artifact caught", any("NO prediction artifact" in x for x in scan(
            {"status": "active", "fixture_key": "ZZZ"}, [("g", good)]))),
        ("computed-without-refs caught", any("source_refs" in x for x in scan(
            sel, [("g", dict(good, source_facts=dict(good["source_facts"], source_refs=[])))]))),
        ("mock model caught", any("mock" in x for x in scan(
            sel, [("g", dict(good, model_fields=dict(good["model_fields"], model_status="baseline-rules-v1", source="seed")))]))),
        ("fake win_prob caught", any("win_prob" in x for x in scan(
            sel, [("g", dict(good, model_fields=dict(good["model_fields"], win_prob={"home": 60})))]))),
        ("fake confidence caught", any("confidence" in x for x in scan(
            sel, [("g", dict(good, model_fields=dict(good["model_fields"], confidence=0.7)))]))),
        ("stale selection caught", any("STALE" in x for x in scan(
            dict(sel, date="2026-06-14"), [("g", good)], slate_date="2026-06-15"))),
        ("fresh selection passes", not any("STALE" in x for x in scan(
            dict(sel, date="2026-06-15"), [("g", good)], slate_date="2026-06-15"))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    strict = "--strict" in argv
    base_url = None
    if "--base-url" in argv:
        base_url = argv[argv.index("--base-url") + 1]

    sel = _load(SEL)
    artifacts = []
    if PRED_DIR.exists():
        for p in sorted(PRED_DIR.glob("*.json")):
            a = json.loads(p.read_text(encoding="utf-8"))
            if "recap_ready" in a:  # observation artifact — skip
                continue
            artifacts.append((p.name, a))
    man = _load(MANIFEST) or _load(FALLBACK_MANIFEST)
    slate_date = (man or {}).get("generated_for_date")
    fails = scan(sel, artifacts, slate_date=slate_date)

    if base_url:
        out, warns = live_probe(base_url, strict=strict)
        for line in out:
            sys.stdout.write(line + "\n")
        fails.extend(warns if strict else [])
        if not strict:
            for w in warns:
                sys.stdout.write("WARN  %s\n" % w)

    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("DATA SOURCE VALIDITY FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("DATA SOURCE VALIDITY PASS (selected_hotspot → artifact → source_facts → model_fields "
                     "source-tagged, not mock; win_prob/confidence null)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
