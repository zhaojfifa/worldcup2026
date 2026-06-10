from __future__ import annotations
"""
Customer recap view — maps a cached ScoutScore accountability report into the
compact RecapContent shape the frontend renders. Server-side only (backend
proxy): the frontend never touches API-FOOTBALL.

Reads docs/data_audit/mvp2_prediction_accountability_reports/<fid>.<tag>.json
(localized zh-CN / vi-VN). Returns None if unavailable (caller → 404; frontend
falls back to its bundled mock recap). No fabrication, no probability/odds/xG.
"""
import json
from pathlib import Path
from typing import Optional

_REPO = Path(__file__).resolve().parents[4]  # scoutscore → services → app → backend → repo
ACCT_DIR = _REPO / "docs" / "data_audit" / "mvp2_prediction_accountability_reports"
LANG_TAG = {"zh": "zh-CN", "vi": "vi-VN"}  # customer langs; en/mm → frontend bundled fallback

_BADGE = {
    "zh": "历史复盘 · 模型校准",
    "vi": "Phục dựng lịch sử · Hiệu chỉnh mô hình",
}


def build_recap_view(fixture_id: str, lang: str) -> Optional[dict]:
    tag = LANG_TAG.get(lang)
    if not tag:
        return None
    path = ACCT_DIR / f"{fixture_id}.{tag}.json"
    if not path.is_file():
        return None
    try:
        a = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None

    verdict = (a.get("accountability_verdict") or {})
    pmv = (a.get("pre_match_model_view") or {})
    actual = (a.get("actual_result") or {})
    mc = (a.get("model_correction") or {})
    return {
        "fixtureId": fixture_id,
        "badge": _BADGE.get(lang, ""),
        "headline": a.get("model_recap_summary"),
        "oneLiner": verdict.get("text"),
        "modelReplay": pmv.get("view"),
        "actualResult": actual.get("text"),
        "replayConclusion": (mc.get("summary")),
        "verdict": verdict.get("status") or "miss",
        "verdictLabel": (verdict.get("status") or "miss").upper(),
        "keyMisses": [b.get("point") for b in (a.get("what_model_missed") or []) if b.get("point")],
        "evidence": [{"label": c.get("title"), "value": c.get("value")} for c in (a.get("key_evidence") or [])],
        "modelCorrection": list(mc.get("changes") or []),
        "nextData": list(mc.get("next_data") or []),
        "operatorCopy": (a.get("operator_recap_copy") or {}).get("text"),
        "dataGaps": list(a.get("missing_data_boundary") or []),
        "aiBoundary": (a.get("ai_boundary") or {}).get("note"),
        "sourceLedger": [{"field": r.get("field"), "endpoint": r.get("endpoint")}
                         for r in (a.get("source_refs") or []) if r.get("field")],
        "disclaimer": a.get("disclaimer"),
    }
