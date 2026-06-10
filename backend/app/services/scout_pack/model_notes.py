from __future__ import annotations
"""
Model notes — a **post-match explanation** layer (model_type=post_match_explanation_v0).

This is NOT a prediction model. It derives *explanatory signals* about a match
that already happened, each carrying `source_refs` back to real pack fields.

Hard rules: no win probability · no odds/betting · no SHAP/feature-importance ·
no xG · no injury/absence impact. Every signal must cite source_refs; conclusions
the model may NOT draw are listed explicitly in `forbidden_conclusions`.
"""
from typing import Any, Optional

from app.services.scout_pack import contract as C
from app.services.scout_pack.contract import loc


def _ref(pack: dict, field: str, metric: Optional[str] = None, value: Any = None) -> dict:
    led = (pack.get("source_ledger") or {}).get(field) or {}
    return {"field": field, "metric": metric, "value": value,
            "source": led.get("source") or C.SOURCE_API_FOOTBALL,
            "endpoint": led.get("endpoint"), "fixture_id": pack.get("fixture_id")}


def build_model_notes(pack: dict, features: dict) -> dict:
    fid = pack.get("fixture_id")
    ctx = features.get("context") or {}
    home, away = ctx.get("home"), ctx.get("away")
    winner = ctx.get("result_winner")
    score = ctx.get("final_score") or {}
    poss = features.get("possession_difference")          # home - away
    shotd = features.get("shot_difference")
    dominant = "home" if (poss or 0) > 0 else "away"
    loser_won = winner in ("home", "away") and winner != dominant
    gk = features.get("goalkeeper_rating") or {}
    saves = features.get("goalkeeper_saves") or {}
    gh, ga = (gk.get("home") or {}).get("rating"), (gk.get("away") or {}).get("rating")

    turning = [f"{g['minute']}' {g['team']}" for g in (features.get("goal_timeline") or [])
               if (g.get("minute_num") or 0) > 45]

    signals = [
        {
            "name": "upset_case",
            "value": bool(loser_won),
            "interpretation": loc(
                f"控球占优的一方({home if dominant=='home' else away})未能取胜,符合爆冷复盘特征。",
                f"Đội kiểm soát bóng nhiều hơn ({home if dominant=='home' else away}) lại không thắng — đặc điểm của một trận gây bất ngờ.",
                f"The side dominating possession ({home if dominant=='home' else away}) did not win — an upset pattern.",
            ),
            "source_refs": [_ref(pack, "team_statistics", "Ball Possession", f"diff {poss}"),
                            _ref(pack, "fixture", "final_score", f"{score.get('home')}-{score.get('away')}")],
        },
        {
            "name": "second_half_turnaround",
            "value": bool(features.get("second_half_turnaround")),
            "interpretation": loc(
                "比分在下半场被反超,结果在下半场决定。",
                "Tỷ số bị lật ngược trong hiệp hai — kết quả được định đoạt ở hiệp hai.",
                "The scoreline was overturned in the second half — the result was decided after the break.",
            ),
            "source_refs": [_ref(pack, "events_summary", "second-half goals", "; ".join(turning))],
        },
        {
            "name": "possession_result_contradiction",
            "value": bool(loser_won and abs(poss or 0) >= 10),
            "interpretation": loc(
                f"控球差 {poss} 个百分点,但控球少的一方赢球 — 控球与结果背离。",
                f"Chênh lệch kiểm soát bóng {poss} điểm, nhưng đội kiểm soát ít hơn lại thắng — ưu thế kiểm soát không chuyển thành kết quả.",
                f"A {poss}-point possession gap, yet the side with less possession won — possession did not convert to result.",
            ),
            "source_refs": [_ref(pack, "team_statistics", "Ball Possession", f"diff {poss}"),
                            _ref(pack, "fixture", "result_winner", winner)],
        },
        {
            "name": "shot_efficiency_gap",
            "value": bool(loser_won and (shotd or 0) > 0),
            "interpretation": loc(
                f"射门差 {shotd},但射门少的一方进球更多 — 射门转化效率差异明显。",
                f"Chênh lệch số cú sút {shotd}, nhưng đội sút ít hơn lại ghi nhiều bàn hơn — hiệu suất dứt điểm chênh lệch rõ.",
                f"A {shotd}-shot gap, yet the side taking fewer shots scored more — a clear finishing-efficiency gap.",
            ),
            "source_refs": [_ref(pack, "team_statistics", "Total Shots", f"diff {shotd}"),
                            _ref(pack, "team_statistics", "Shots on Goal", f"diff {features.get('shots_on_goal_difference')}"),
                            _ref(pack, "fixture", "final_score", f"{score.get('home')}-{score.get('away')}")],
        },
        {
            "name": "event_turning_point",
            "value": bool(turning),
            "interpretation": loc(
                f"结果转折点出现在下半场进球:{', '.join(turning) if turning else '无'}。",
                f"Bước ngoặt nằm ở các bàn thắng hiệp hai: {', '.join(turning) if turning else 'không có'}.",
                f"The turning point was the second-half goal(s): {', '.join(turning) if turning else 'none'}.",
            ),
            "source_refs": [_ref(pack, "events_summary", "goal events", "; ".join(turning))],
        },
        {
            "name": "goalkeeper_impact_observed",
            "value": bool(gh is not None and ga is not None and (
                (ga > gh) if winner == "away" else (gh > ga))),
            "interpretation": loc(
                f"胜方门将评分更高(主 {gh} / 客 {ga}),扑救 主 {saves.get('home')} / 客 {saves.get('away')} — 门将表现在观测层面影响结果。",
                f"Thủ môn đội thắng có điểm cao hơn (nhà {gh} / khách {ga}), số lần cứu thua nhà {saves.get('home')} / khách {saves.get('away')} — màn trình diễn của thủ môn ảnh hưởng đến kết quả ở mức quan sát.",
                f"The winner's keeper rated higher (home {gh} / away {ga}); saves home {saves.get('home')} / away {saves.get('away')} — keeper performance observably affected the result.",
            ),
            "source_refs": [_ref(pack, "player_statistics", "goalkeeper rating", f"home {gh} / away {ga}"),
                            _ref(pack, "team_statistics", "Goalkeeper Saves", f"home {saves.get('home')} / away {saves.get('away')}")],
        },
        {
            "name": "data_coverage_sufficient",
            "value": bool((features.get("data_coverage_score") or 0) >= 70),
            "interpretation": loc(
                f"数据覆盖 {features.get('data_coverage_score')}%(9 项核心已接入),足以支撑赛后复盘解释。",
                f"Độ phủ dữ liệu {features.get('data_coverage_score')}% (9 mục cốt lõi đã có), đủ để giải thích sau trận.",
                f"Data coverage {features.get('data_coverage_score')}% (9 core sections present) — sufficient for a post-match read.",
            ),
            "source_refs": [_ref(pack, "fixture", "coverage_score", f"{features.get('data_coverage_score')}%")],
        },
        {
            "name": "injuries_missing",
            "value": bool(features.get("missing_injuries")),
            "interpretation": loc(
                "伤停数据未返回,不能解释主力缺阵/阵容完整性的影响。",
                "Dữ liệu chấn thương chưa có, không thể giải thích ảnh hưởng vắng mặt / độ đầy đủ đội hình.",
                "Injuries data is unavailable — absence / squad-completeness impact cannot be explained.",
            ),
            "source_refs": [_ref(pack, "injuries", "results", "0 (source required)")],
        },
    ]

    allowed_conclusions = [
        loc("可判断为控球占优但结果相反的爆冷复盘样例",
            "Có thể kết luận đây là mẫu trận gây bất ngờ: kiểm soát bóng tốt nhưng kết quả ngược lại",
            "May conclude this is an upset: strong possession but the opposite result"),
        loc("下半场进球是结果转折点",
            "Các bàn thắng hiệp hai là bước ngoặt của kết quả",
            "The second-half goals were the turning point"),
        loc("胜方门将表现在观测层面对结果有影响",
            "Màn trình diễn của thủ môn đội thắng ảnh hưởng đến kết quả ở mức quan sát",
            "The winning keeper's performance observably affected the result"),
        loc("现有数据足以支撑赛后复盘解释",
            "Dữ liệu hiện có đủ để giải thích sau trận",
            "Current data is sufficient for a post-match explanation"),
    ]
    forbidden_conclusions = [
        loc("不得预测比赛结果或给出任何资金、盈利相关建议",
            "Không dự đoán kết quả trận đấu hoặc đưa ra lời khuyên liên quan tiền bạc, lợi nhuận",
            "No match-result prediction or any money/profit-related advice"),
        loc("不得评估伤停或缺阵影响(无伤停数据)",
            "Không đánh giá ảnh hưởng chấn thương hay vắng mặt (chưa có dữ liệu chấn thương)",
            "No injury/absence impact (no injuries data)"),
        loc("不得量化运气或机会质量(本轮无 xG / 进阶数据)",
            "Không định lượng may rủi hay chất lượng cơ hội (vòng này không có xG / chỉ số nâng cao)",
            "No luck/chance-quality quantification (no xG / advanced stats this round)"),
        loc("不得输出特征重要度或权重解释(无真实预测模型)",
            "Không xuất mức quan trọng đặc trưng hay trọng số giải thích (không có mô hình dự đoán thật)",
            "No feature-importance or weight explanations (no real prediction model)"),
    ]
    missing_data = [
        loc("伤停 / 停赛:0 条返回,需二次数据源或当前赛季复验",
            "Chấn thương / treo giò: 0 kết quả, cần nguồn thứ hai hoặc mùa giải hiện tại",
            "Injuries / suspensions: 0 results, second source or current-season re-check required"),
        loc("xG / 进阶数据:本轮未接入",
            "xG / chỉ số nâng cao: chưa tích hợp trong vòng này",
            "xG / advanced stats: not ingested this round"),
    ]

    return {
        "fixture_id": fid,
        "model_type": "post_match_explanation_v0",
        "is_prediction": False,
        "signals": signals,
        "allowed_conclusions": allowed_conclusions,
        "forbidden_conclusions": forbidden_conclusions,
        "missing_data": missing_data,
        "disclaimer": dict(loc(
            "复盘解释信号,非赛前预测;历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。",
            "Tín hiệu giải thích sau trận, không phải dự đoán trước trận; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.",
            "Post-match explanation signals, not pre-match prediction; past performance does not represent future results — for data analysis and fan entertainment only.",
        )),
    }
