#!/usr/bin/env python3
"""R2 guard — manual_scores_<date>.md is an OPTIONAL operator override, NOT a requirement.

--selftest (offline):
  * parse_manual_optional returns [] for a missing file (no raise)
  * apply_manual_override only CORRECTS a fixture the API returned; it never INVENTS a fixture the
    API did not return (an override for an unknown matchup is ignored)
  * an applied override corrects score/status and tags the row operator_override
  * the api-football sync source path does not call the required parse_manual
--date YYYY-MM-DD: a registry was generated for the date with source_mode=api-football AND there is
  no requirement that manual_scores_<date>.md exists (the registry generated regardless).
Usage: --selftest | --date 2026-06-16"""
import importlib.util, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC = ROOT / "docs/data_audit/mvp2_match_sync"


def _ms():
    spec = importlib.util.spec_from_file_location("ms", ROOT / "scripts" / "mvp2_match_sync.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def selftest():
    ms = _ms()
    # 1) missing file -> [] (no raise)
    missing_ok = ms.parse_manual_optional("29991231") == []
    # 2) override corrects an API fixture; 3) override for unknown matchup is ignored (no invention)
    raws = [{"home": "Iran", "away": "New Zealand", "score_home": None, "score_away": None, "status": "live",
             "kickoff_utc": "x", "api_fixture_id": 1},
            {"home": "France", "away": "Senegal", "score_home": None, "score_away": None, "status": "scheduled",
             "kickoff_utc": "x", "api_fixture_id": 2}]
    overrides = [{"home": "Iran", "away": "New Zealand", "score_home": 2, "score_away": 2, "status": "finished"},
                 {"home": "Ghost", "away": "Phantom", "score_home": 9, "score_away": 0, "status": "finished"}]
    out, applied = ms.apply_manual_override([dict(r) for r in raws], overrides)
    by = {r["home"]: r for r in out}
    corrected = by["Iran"]["score_home"] == 2 and by["Iran"]["status"] == "finished" and by["Iran"].get("operator_override")
    no_invent = "Ghost" not in by and applied == 1 and len(out) == 2
    untouched = by["France"]["score_home"] is None and not by["France"].get("operator_override")
    # 4) the api-football branch reads via parse_manual_optional, not the required parse_manual
    src = (ROOT / "scripts" / "mvp2_match_sync.py").read_text(encoding="utf-8")
    af_block = src.split('if source == "api-football":', 1)[-1].split("else:", 1)[0]
    uses_optional = "parse_manual_optional" in af_block and "parse_manual(compact)" not in af_block
    checks = [
        ("missing file -> [] (no raise)", missing_ok),
        ("override corrects API fixture + tags operator_override", bool(corrected)),
        ("override never invents a fixture", no_invent),
        ("non-overridden fixture untouched", untouched),
        ("api-football path uses optional override, not required parse_manual", uses_optional),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks: print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        return selftest()
    date_iso = a[a.index("--date") + 1] if "--date" in a else "2026-06-16"
    compact = date_iso.replace("-", "")
    reg = SYNC / ("daily_fixtures_%s.json" % compact)
    man = SYNC / ("manual_scores_%s.md" % compact)
    fails = []
    if not reg.exists():
        fails.append("registry not generated for %s (sync should run without a manual file)" % date_iso)
    else:
        d = json.loads(reg.read_text(encoding="utf-8"))
        if d.get("source_mode") != "api-football":
            fails.append("registry source_mode=%r (expected api-football)" % d.get("source_mode"))
    note = "manual_scores present (override)" if man.exists() else "manual_scores ABSENT — registry still generated (optional proven)"
    for x in fails: print("FAIL  %s" % x)
    if fails:
        print("R2 MANUAL-SCORES-OPTIONAL FAIL — %d" % len(fails)); return 1
    print("R2 MANUAL-SCORES-OPTIONAL PASS (%s · %s)" % (date_iso, note)); return 0


if __name__ == "__main__":
    sys.exit(main())
