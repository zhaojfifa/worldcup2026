#!/usr/bin/env python3
"""Build the MVP-2 productized scout report artifacts from a cached Scout Pack.

Pure offline transform (NO API calls): reads
``docs/data_audit/mvp2_scout_pack_samples/<fid>.json`` and writes:
  - docs/data_audit/mvp2_feature_snapshots/<fid>.json
  - docs/data_audit/mvp2_model_notes/<fid>.json
  - docs/data_audit/mvp2_productized_reports/<fid>.zh-CN.json
  - docs/data_audit/mvp2_productized_reports/<fid>.vi-VN.json

No prediction / odds / SHAP / xG / injury inference. vi output must be 0 Han.
Run:  python backend/scripts/mvp2_build_productized_report.py [fixture_id ...]
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
from app.services.scout_pack.report import build_report, localize  # noqa: E402

SAMPLES = os.path.join(REPO_DIR, "docs/data_audit/mvp2_scout_pack_samples")
FEAT_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_feature_snapshots")
NOTES_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_model_notes")
REPORT_DIR = os.path.join(REPO_DIR, "docs/data_audit/mvp2_productized_reports")
DEFAULT = ["855737"]


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return os.path.getsize(path)


def main():
    fixtures = sys.argv[1:] or DEFAULT
    for fid in fixtures:
        src = os.path.join(SAMPLES, f"{fid}.json")
        if not os.path.isfile(src):
            print(f"SKIP {fid}: no scout pack at {src}")
            continue
        pack = json.load(open(src, encoding="utf-8"))

        features = compute_feature_snapshot(pack)
        notes = build_model_notes(pack, features)
        report = build_report(pack, features, notes)
        zh = localize(report, "zh")
        vi = localize(report, "vi")

        s1 = _write(os.path.join(FEAT_DIR, f"{fid}.json"), features)
        s2 = _write(os.path.join(NOTES_DIR, f"{fid}.json"), notes)
        s3 = _write(os.path.join(REPORT_DIR, f"{fid}.zh-CN.json"), zh)
        s4 = _write(os.path.join(REPORT_DIR, f"{fid}.vi-VN.json"), vi)

        print(f"{fid}: features({s1}b) notes({s2}b) zh({s3}b) vi({s4}b)")
        print(f"  verdict[zh]: {zh['match_verdict']['text']}")
        print(f"  signals: " + ", ".join(f"{s['name']}={s['value']}" for s in notes["signals"]))
        print(f"  coverage={features['data_coverage_score']}% missing_injuries={features['missing_injuries']} missing_xg={features['missing_xg']}")


if __name__ == "__main__":
    main()
