#!/usr/bin/env python3
"""
MVP-2 Track A — A4 real-recap factor-frame builder (design §3 A4; Owner A-GO-1).

For a FINISHED real 2026 fixture whose pre-match judgement was generated and
committed BEFORE kickoff, builds a recap factor frame with:
  mode = "real_recap"          (vs the WC2022 "historical_recap" replay mode)
  prematch_provenance = path + sha256 + generated_at of the ARCHIVED pre-match
  artifacts (trial frame + per-language narratives) + verbatim judgement quotes.
The narrative generator injects this provenance and the guard REQUIRES the
internal_notes citation (sha256 + docs/data_audit path) — replacing the
historical-replay disclaimer with real-prediction traceability.

Engineering = facts only (result/stats/events via the refreshed Scout Pack +
kaggle baseline reused from the v0.2 builder). The LLM writes the recap.

Preconditions (honest blocks, exit 2 with a JSON report on stdout):
  - fixture status is FT/AET/PEN (else blocked_by_time_or_data)
  - the Scout Pack sample was refreshed POST-match
    (backend/scripts/mvp2_ingest_scout_pack.py — pack must carry final_score/stats)
  - archived pre-match artifacts exist (frame + >=1 narrative)

Usage: python3 scripts/mvp2_build_recap_frame_real.py FIXTURE_ID
Output: docs/data_audit/mvp2_scoutscore_v0_2/{id}.real_recap.factor_frame.json
"""
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.api_football_client import APIFootballScoutClient  # noqa: E402

OUT = ROOT / "docs" / "data_audit" / "mvp2_scoutscore_v0_2"
FRAMES = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_frames"
NARR = ROOT / "docs" / "data_audit" / "mvp2_trial_prediction_narratives"
LANGS = ("zh-CN", "vi-VN", "my-MM")
FINISHED = ("FT", "AET", "PEN")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _load("opsq", ROOT / "scripts" / "mvp2_ops_queue.py")


def _provenance(fid):
    prov = {"note": "the pre-match judgement is a REAL archived prediction, committed to git before kickoff",
            "narratives": {}}
    fp = FRAMES / ("%s.json" % fid)
    if fp.exists():
        fr = Q.read_json(fp)
        prov["trial_frame"] = {"path": str(fp.relative_to(ROOT)), "sha256": Q.sha256_file(fp),
                               "generated_at": fr.get("generated_at")}
    for lang in LANGS:
        np = NARR / ("%s.%s.deepseek.json" % (fid, lang))
        if np.exists():
            n = Q.read_json(np)
            prov["narratives"][lang] = {
                "path": str(np.relative_to(ROOT)), "sha256": Q.sha256_file(np),
                "generated_at": n.get("generated_at"),
                "quotes": {k: n.get(k) for k in ("main_lean", "scoreline_view", "risk_level")},
            }
    return prov


def build(fid, run=None, client=None):
    fid = str(fid)
    client = client or APIFootballScoutClient()
    fx = (client.get_fixture(int(fid)).response or [{}])[0]
    if run:
        run.api("/fixtures")
    status = ((fx.get("fixture") or {}).get("status") or {}).get("short")
    if status not in FINISHED:
        return {"status": "blocked_by_time_or_data",
                "reason": "fixture status is %r — recap runs after FT/AET/PEN" % status}

    prov = _provenance(fid)
    if "trial_frame" not in prov or not prov["narratives"]:
        return {"status": "blocked_by_time_or_data",
                "reason": "archived pre-match artifacts missing (frame/narratives) — nothing real to recap"}

    v02 = _load("v02", ROOT / "scripts" / "mvp2_build_scoutscore_v0_2_factors.py")
    v02.RESULTS = rows = v02.load_results()
    try:
        frame = v02.recap_frame(fid, rows)
    except (FileNotFoundError, KeyError, TypeError) as e:
        return {"status": "blocked_by_time_or_data",
                "reason": "scout pack not refreshed post-match (%s: %s) — run "
                          "backend/scripts/mvp2_ingest_scout_pack.py %s first" % (type(e).__name__, e, fid)}
    score = (frame.get("fixture") or {}).get("final_score") or {}
    if score.get("home") is None:
        return {"status": "blocked_by_time_or_data",
                "reason": "scout pack carries no final score — refresh the pack post-match first"}

    frame["mode"] = "real_recap"
    frame["not_real_archived_prediction"] = False
    frame["prematch_provenance"] = prov
    frame["generated_by"] = "scripts/mvp2_build_recap_frame_real.py"
    out_path = OUT / ("%s.real_recap.factor_frame.json" % fid)
    Q.write_json(out_path, frame)
    return {"status": "ok", "artifact": str(out_path.relative_to(ROOT)),
            "final_score": score, "narrative_langs_archived": sorted(prov["narratives"].keys())}


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    res = build(sys.argv[1])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res["status"] == "ok" else 2)


if __name__ == "__main__":
    main()
