#!/usr/bin/env python3
"""Build ScoutScore v0.1 prediction-accountability artifacts from a cached pack.

Pure offline transform (NO API, NO live LLM): reads
``docs/data_audit/mvp2_scout_pack_samples/<fid>.json`` and writes:
  - docs/data_audit/mvp2_scoutscore_v0/<fid>.factor_scores.json
  - docs/data_audit/mvp2_prediction_replay/<fid>.scoutscore_v0.replay.json
  - docs/data_audit/mvp2_prediction_accountability_reports/<fid>.zh-CN.json
  - docs/data_audit/mvp2_prediction_accountability_reports/<fid>.vi-VN.json

Historical replay only (not a real archived prediction). No fake probability,
no SHAP, no xG, no injuries inference, no betting.
Run:  python backend/scripts/mvp2_build_scoutscore.py [fixture_id ...]
"""
import json
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.scout_pack.features import compute_feature_snapshot  # noqa: E402
from app.services.scout_pack.model_notes import build_model_notes  # noqa: E402
from app.services.scout_pack.report import localize  # noqa: E402
from app.services.scoutscore.factors import compute_factor_scores  # noqa: E402
from app.services.scoutscore.accountability import build_replay, build_accountability_report  # noqa: E402

SAMPLES = os.path.join(REPO_DIR, "docs/data_audit/mvp2_scout_pack_samples")
FACTOR_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_scoutscore_v0")
REPLAY_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_prediction_replay")
ACCT_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_prediction_accountability_reports")
DEFAULT = ["855737"]


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return os.path.getsize(path)


def main():
    for fid in (sys.argv[1:] or DEFAULT):
        src = os.path.join(SAMPLES, f"{fid}.json")
        if not os.path.isfile(src):
            print(f"SKIP {fid}: no scout pack at {src}")
            continue
        pack = json.load(open(src, encoding="utf-8"))
        features = compute_feature_snapshot(pack)
        notes = build_model_notes(pack, features)
        factors = compute_factor_scores(pack, features, favored_side="home")
        replay = build_replay(pack, features, factors)
        report = build_accountability_report(pack, features, notes, factors, replay)

        s1 = _write(os.path.join(FACTOR_DIR, f"{fid}.factor_scores.json"), factors)
        s2 = _write(os.path.join(REPLAY_DIR, f"{fid}.scoutscore_v0.replay.json"), replay)
        s3 = _write(os.path.join(ACCT_DIR, f"{fid}.zh-CN.json"), localize(report, "zh"))
        s4 = _write(os.path.join(ACCT_DIR, f"{fid}.vi-VN.json"), localize(report, "vi"))

        print(f"{fid}: factors({s1}b) replay({s2}b) zh({s3}b) vi({s4}b)")
        print(f"  expected_side={factors['expected_side']} confidence={factors['confidence_tier']} "
              f"status={factors['accountability_status']} mode={factors['prediction_mode']} "
              f"not_real_archived={factors['not_real_archived_prediction']}")
        print("  factors: " + ", ".join(f"{f['factor']}={f['score']}({f['data_status']})" for f in factors["factors"]))


if __name__ == "__main__":
    main()
