from __future__ import annotations
"""
Productized Scout Report — assembles an operator-readable report from the Scout
Pack + feature snapshot + model notes. Text is built from real values (templated
by team/score/diffs), so it generalizes beyond one fixture.

Sections: match_verdict · why_it_happened · evidence_board · feature_snapshot_summary
· model_notes · operator_content_draft · missing_data · next_data_needed ·
ai_boundary · source_refs.

Rules: every conclusion carries `source_refs`. No win probability, no odds/betting,
no SHAP, no xG, no injury/absence impact. Built neutral with localized text; call
``localize(report, lang)`` to project a single-language report (vi must be 0 Han).
"""
from typing import Any, Optional

from app.services.scout_pack import contract as C
from app.services.scout_pack.contract import loc


def _t(zh: str, vi: str, en: str = "") -> dict:
    return loc(zh, vi, en)


def _ref(pack: dict, field: str, metric: Optional[str] = None, value: Any = None) -> dict:
    led = (pack.get("source_ledger") or {}).get(field) or {}
    return {"field": field, "metric": metric, "value": value,
            "source": led.get("source") or C.SOURCE_API_FOOTBALL,
            "endpoint": led.get("endpoint"), "fixture_id": pack.get("fixture_id")}


def build_report(pack: dict, features: dict, notes: dict) -> dict:
    fid = pack.get("fixture_id")
    ctx = features.get("context") or {}
    home, away = ctx.get("home"), ctx.get("away")
    score = ctx.get("final_score") or {}
    hs, as_ = score.get("home"), score.get("away")
    name = {"home": home, "away": away}
    poss = features.get("possession_difference")
    dominant_side = "home" if (poss or 0) > 0 else "away"
    dominant = name[dominant_side]
    winner_side = ctx.get("result_winner")
    winner = name.get(winner_side)
    upset = winner_side in ("home", "away") and winner_side != dominant_side

    ts = {t.get("team"): (t.get("stats") or {}) for t in (pack.get("team_statistics", {}).get("value") or [])}
    hst, ast = ts.get(home, {}), ts.get(away, {})
    gk = features.get("goalkeeper_rating") or {}
    gh = (gk.get("home") or {}).get("rating")
    ga = (gk.get("away") or {}).get("rating")
    svh, sva = hst.get("Goalkeeper Saves"), ast.get("Goalkeeper Saves")
    goals = features.get("goal_timeline") or []
    goal_line = "; ".join(f"{g['minute']}' {g['team']} {g['player']}" for g in goals) or "—"
    second_half = [f"{g['minute']}' {g['team']}" for g in goals if (g.get("minute_num") or 0) > 45]

    # ---- match verdict ----
    if upset:
        verdict = _t(
            f"赛后复盘 · {home} {hs}–{as_} {away}。{dominant} 在控球与射门上占优却未取胜,属于典型爆冷。",
            f"Phân tích sau trận · {home} {hs}–{as_} {away}. {dominant} vượt trội về kiểm soát bóng và số cú sút nhưng không thắng — một bất ngờ điển hình.",
            f"Post-match · {home} {hs}–{as_} {away}. {dominant} dominated possession and shots but did not win — a classic upset.",
        )
    else:
        verdict = _t(
            f"赛后复盘 · {home} {hs}–{as_} {away}。数据优势与比赛结果基本一致。",
            f"Phân tích sau trận · {home} {hs}–{as_} {away}. Ưu thế dữ liệu phù hợp với kết quả trận đấu.",
            f"Post-match · {home} {hs}–{as_} {away}. The data edge broadly matches the result.",
        )

    # ---- why it happened (narrative points, each with source_refs) ----
    why = [
        {"point": _t(f"进球顺序:{goal_line}。", f"Diễn biến bàn thắng: {goal_line}.", f"Goal sequence: {goal_line}."),
         "source_refs": [_ref(pack, "events_summary", "goal events", goal_line)]},
    ]
    if features.get("second_half_turnaround"):
        why.append({"point": _t(
            f"结果在下半场被反超:{', '.join(second_half)}。",
            f"Kết quả bị lật ngược trong hiệp hai: {', '.join(second_half)}.",
            f"The result was overturned in the second half: {', '.join(second_half)}."),
            "source_refs": [_ref(pack, "events_summary", "second-half goals", "; ".join(second_half))]})
    why.append({"point": _t(
        f"控球 {hst.get('Ball Possession')} vs {ast.get('Ball Possession')}、射门 {hst.get('Total Shots')} vs {ast.get('Total Shots')},数据占优方为 {dominant}。",
        f"Kiểm soát bóng {hst.get('Ball Possession')} so với {ast.get('Ball Possession')}, số cú sút {hst.get('Total Shots')} so với {ast.get('Total Shots')}; đội nhỉnh hơn về dữ liệu là {dominant}.",
        f"Possession {hst.get('Ball Possession')} vs {ast.get('Ball Possession')}, shots {hst.get('Total Shots')} vs {ast.get('Total Shots')}; the data edge belongs to {dominant}."),
        "source_refs": [_ref(pack, "team_statistics", "Ball Possession / Total Shots",
                             f"{hst.get('Ball Possession')}/{ast.get('Ball Possession')}, {hst.get('Total Shots')}/{ast.get('Total Shots')}")]})
    why.append({"point": _t(
        f"门将:评分 主 {gh} / 客 {ga},扑救 主 {svh} / 客 {sva}。",
        f"Thủ môn: điểm nhà {gh} / khách {ga}, cứu thua nhà {svh} / khách {sva}.",
        f"Goalkeepers: rating home {gh} / away {ga}, saves home {svh} / away {sva}."),
        "source_refs": [_ref(pack, "player_statistics", "goalkeeper rating", f"home {gh} / away {ga}"),
                        _ref(pack, "team_statistics", "Goalkeeper Saves", f"home {svh} / away {sva}")]})

    # ---- evidence board (factual cards; values are home / away) ----
    def card(title_zh, title_vi, title_en, field, hv, av, refmetric):
        return {"title": _t(title_zh, title_vi, title_en),
                "home": home, "away": away, "value": f"{hv} / {av}",
                "source_refs": [_ref(pack, field, refmetric, f"{hv} / {av}")]}
    evidence_board = [
        card("控球率", "Kiểm soát bóng", "Possession", "team_statistics", hst.get("Ball Possession"), ast.get("Ball Possession"), "Ball Possession"),
        card("总射门", "Tổng số cú sút", "Total shots", "team_statistics", hst.get("Total Shots"), ast.get("Total Shots"), "Total Shots"),
        card("射正", "Sút trúng đích", "Shots on goal", "team_statistics", hst.get("Shots on Goal"), ast.get("Shots on Goal"), "Shots on Goal"),
        card("传球成功率", "Tỷ lệ chuyền chính xác", "Pass accuracy", "team_statistics", hst.get("Passes %"), ast.get("Passes %"), "Passes %"),
        card("门将评分", "Điểm thủ môn", "Goalkeeper rating", "player_statistics", gh, ga, "goalkeeper rating"),
        card("门将扑救", "Số lần cứu thua", "Goalkeeper saves", "team_statistics", svh, sva, "Goalkeeper Saves"),
        {"title": _t("进球时间线", "Diễn biến bàn thắng", "Goal timeline"),
         "home": home, "away": away, "value": goal_line,
         "source_refs": [_ref(pack, "events_summary", "goal events", goal_line)]},
    ]

    # ---- feature snapshot summary (selected) ----
    def feat(label_zh, label_vi, label_en, value, field="fixture", metric=None):
        return {"label": _t(label_zh, label_vi, label_en), "value": value,
                "source_refs": [_ref(pack, field, metric, str(value))]}
    feature_summary = [
        feat("数据覆盖", "Độ phủ dữ liệu", "Data coverage", f"{features.get('data_coverage_score')}%", "fixture", "coverage_score"),
        feat("控球差(主-客)", "Chênh kiểm soát (nhà-khách)", "Possession diff (H-A)", features.get("possession_difference"), "team_statistics", "Ball Possession"),
        feat("射门差(主-客)", "Chênh số cú sút (nhà-khách)", "Shot diff (H-A)", features.get("shot_difference"), "team_statistics", "Total Shots"),
        feat("下半场反超", "Lật ngược hiệp hai", "Second-half turnaround", features.get("second_half_turnaround"), "events_summary", "goals"),
        feat("最高球员评分", "Điểm cầu thủ cao nhất", "Top player rating", features.get("top_player_rating"), "player_statistics", "rating"),
        feat("伤停缺失", "Thiếu dữ liệu chấn thương", "Injuries missing", features.get("missing_injuries"), "injuries", "results"),
        feat("xG 缺失", "Thiếu xG", "xG missing", features.get("missing_xg"), "team_statistics", "advanced stats not ingested"),
    ]

    # ---- operator content draft (shareable copy) ----
    if upset:
        draft = _t(
            f"【赛后情报】{home} {hs}–{as_} {away}。这是一场典型爆冷复盘:{dominant} 控球 "
            f"{hst.get('Ball Possession') if dominant_side=='home' else ast.get('Ball Possession')}、"
            f"射门占优,却被 {winner} 拿下。进球:{goal_line}。"
            "⚠ 伤停数据缺失,不写主力缺阵影响;无 xG,不写运气成分。"
            "历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。",
            f"[Tin sau trận] {home} {hs}–{as_} {away}. Một trận gây bất ngờ điển hình: {dominant} kiểm soát bóng và "
            f"số cú sút nhỉnh hơn nhưng {winner} mới là đội thắng. Bàn thắng: {goal_line}. "
            "⚠ Thiếu dữ liệu chấn thương — không viết về ảnh hưởng vắng mặt; không có xG — không viết về yếu tố may mắn. "
            "Thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.",
            f"[Post-match] {home} {hs}–{as_} {away}. A classic upset: {dominant} led possession and shots yet {winner} won. "
            f"Goals: {goal_line}. Injuries unavailable (no absence claims); no xG (no luck claims). "
            "Past performance does not represent future results — for data analysis and fan entertainment only.",
        )
    else:
        draft = _t(
            f"【赛后情报】{home} {hs}–{as_} {away}。进球:{goal_line}。数据与结果基本一致。"
            "⚠ 伤停数据缺失;无 xG。历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。",
            f"[Tin sau trận] {home} {hs}–{as_} {away}. Bàn thắng: {goal_line}. Dữ liệu phù hợp với kết quả. "
            "⚠ Thiếu dữ liệu chấn thương; không có xG. Thành tích quá khứ không đại diện cho kết quả tương lai, "
            "chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.",
            f"[Post-match] {home} {hs}–{as_} {away}. Goals: {goal_line}. Data matches the result. "
            "Injuries unavailable; no xG. Past performance does not represent future results — fan entertainment only.",
        )
    content_draft = {"text": draft, "source_refs": [
        _ref(pack, "fixture", "final_score", f"{hs}-{as_}"),
        _ref(pack, "events_summary", "goals", goal_line),
        _ref(pack, "team_statistics", "possession/shots", None)]}

    # ---- missing data + next data needed ----
    missing_data = notes.get("missing_data") or []
    next_data_needed = [
        {"item": _t("伤停 / 停赛", "Chấn thương / treo giò", "Injuries / suspensions"),
         "purpose": _t("解释主力缺阵、阵容完整性、首发变化", "Giải thích vắng mặt trụ cột, độ đầy đủ đội hình, thay đổi đội hình", "Explain absences, squad completeness, lineup changes"),
         "ref_doc": "docs/MVP2_NEXT_DATA_REQUIREMENTS.md"},
        {"item": _t("xG / 进阶数据", "xG / chỉ số nâng cao", "xG / advanced stats"),
         "purpose": _t("解释机会质量与控球-结果背离", "Giải thích chất lượng cơ hội và việc kiểm soát bóng không thành kết quả", "Explain chance quality and the possession-vs-result gap"),
         "ref_doc": "docs/MVP2_NEXT_DATA_REQUIREMENTS.md"},
    ]

    # ---- ai boundary ----
    ai_boundary = {
        "allowed_fields": pack.get("ai_allowed_explanations") or [],
        "forbidden_fields": pack.get("ai_forbidden_explanations") or [],
        "note": _t(C.AI_ONLY_VERIFIED["zh"], C.AI_ONLY_VERIFIED["vi"], C.AI_ONLY_VERIFIED["en"]),
    }

    # ---- aggregate source_refs ----
    agg = {}
    def collect(refs):
        for r in (refs or []):
            agg[(r.get("field"), r.get("metric"))] = {"field": r.get("field"), "endpoint": r.get("endpoint"),
                                                       "source": r.get("source")}
    for blk in why:
        collect(blk["source_refs"])
    for c in evidence_board:
        collect(c["source_refs"])
    for f in feature_summary:
        collect(f["source_refs"])
    for s in (notes.get("signals") or []):
        collect(s.get("source_refs"))
    collect(content_draft["source_refs"])
    source_refs = list(agg.values())

    return {
        "fixture_id": fid,
        "source": C.SOURCE_API_FOOTBALL,
        "report_type": "productized_scout_report_v0",
        "last_checked_at": pack.get("last_checked_at"),
        "public_ready": False,
        "operation_status": "paused",
        "match_verdict": {"text": verdict, "source_refs": [
            _ref(pack, "team_statistics", "possession/shots", None),
            _ref(pack, "fixture", "final_score", f"{hs}-{as_}")]},
        "why_it_happened": why,
        "evidence_board": evidence_board,
        "feature_snapshot_summary": feature_summary,
        "model_notes": {
            "model_type": notes.get("model_type"),
            "is_prediction": notes.get("is_prediction"),
            "signals": notes.get("signals"),
            "allowed_conclusions": notes.get("allowed_conclusions"),
            "forbidden_conclusions": notes.get("forbidden_conclusions"),
        },
        "operator_content_draft": content_draft,
        "missing_data": missing_data,
        "next_data_needed": next_data_needed,
        "ai_boundary": ai_boundary,
        "source_refs": source_refs,
        "disclaimer": dict(_t(
            "历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。",
            "Thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.",
            "Past performance does not represent future results — for data analysis and fan entertainment only.",
        )),
    }


def _is_loc(o: Any) -> bool:
    return isinstance(o, dict) and "zh" in o and "vi" in o and set(o.keys()) <= {"zh", "vi", "en"}


def localize(obj: Any, lang: str) -> Any:
    """Project all localized {zh,vi,en} dicts down to a single language."""
    if _is_loc(obj):
        return obj.get(lang) or obj.get("en") or obj.get("zh")
    if isinstance(obj, dict):
        return {k: localize(v, lang) for k, v in obj.items()}
    if isinstance(obj, list):
        return [localize(v, lang) for v in obj]
    return obj
