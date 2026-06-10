from __future__ import annotations
"""
ScoutScore v0.1 — Replay ledger + Post-match Accountability report.

`build_replay`            -> English prediction-account ledger (historical replay).
`build_accountability_report` -> neutral report with localized text; project to
                            zh/vi with `report.localize`.

The narrative is the reasoning-layer output (deterministic/template, AI_PROVIDER=mock
fallback; DeepSeek/Gemini designated for production behind the draft-only path).
Hard rules: historical replay only (no real archived prediction), no win
probability, no SHAP, no xG, no odds/betting, no injury inference; every
conclusion carries source_refs or an assumption flag.
"""
from typing import Any, Optional

from app.services.scout_pack.contract import loc

SOURCE = "api-football"


def _ref(pack: dict, field: str, metric: Optional[str] = None, value: Any = None) -> dict:
    led = (pack.get("source_ledger") or {}).get(field) or {}
    return {"field": field, "metric": metric, "value": value,
            "source": led.get("source") or SOURCE, "endpoint": led.get("endpoint"),
            "fixture_id": pack.get("fixture_id")}


def _stat(pack: dict, team: str, key: str):
    for t in (pack.get("team_statistics", {}).get("value") or []):
        if t.get("team") == team:
            return (t.get("stats") or {}).get(key)
    return None


def build_replay(pack: dict, features: dict, factors: dict) -> dict:
    ctx = features.get("context") or {}
    home, away = ctx.get("home"), ctx.get("away")
    for_home, for_away = [], []
    for f in factors["factors"]:
        line = f"{f['factor']} (score {f['score']}, {f['data_status']}): {f['interpretation_pre_match']}"
        if f["score"] > 0:
            for_home.append(line)
        elif f["score"] < 0:
            for_away.append(line)
    known_missing = [f"{f['factor']}: {f.get('note') or f['interpretation_pre_match']}"
                     for f in factors["factors"] if f["data_status"] in ("missing", "replay_only")]
    return {
        "model_name": factors["model_name"],
        "fixture_id": pack.get("fixture_id"),
        "prediction_mode": "historical_replay",
        "not_real_archived_prediction": True,
        "model_view_before_match": (
            f"In replay, ScoutScore v0.1 leans {factors['expected_side']} "
            f"(aggregate {factors['aggregate_score']}), confidence {factors['confidence_tier']}; "
            "the view rests largely on a paper-strength assumption with key pre-match inputs missing."),
        "expected_side": factors["expected_side"],
        "confidence_tier": factors["confidence_tier"],
        "factor_reasons_for_argentina": for_home if home == "Argentina" else for_away,
        "factor_reasons_for_saudi_arabia": for_away if away == "Saudi Arabia" else for_home,
        "factor_reasons_for_home": for_home,
        "factor_reasons_for_away": for_away or ["(none — the model had no pre-match factor favouring the underdog; "
                                                "efficiency & momentum were blind spots, revealed only post-match)"],
        "known_missing_factors": known_missing,
        "actual_result": factors["actual_result"],
        "accountability_status": factors["accountability_status"],
        "disclaimer": "Historical replay sample to validate the product flow — NOT a claim of a pre-match hit.",
    }


_FACTOR_STATUS = {
    "team_strength": "invalidated", "recent_form": "not_available",
    "lineup_formation": "partial", "match_control": "invalidated_as_predictor",
    "efficiency": "missed", "event_momentum": "missed", "missing_risk": "confirmed_gap",
}


def build_accountability_report(pack: dict, features: dict, model_notes: dict, factors: dict, replay: dict) -> dict:
    ctx = features.get("context") or {}
    home, away = ctx.get("home"), ctx.get("away")
    sc = ctx.get("final_score") or {}
    status = factors["accountability_status"]
    exp = factors["expected_side"]
    gk = features.get("goalkeeper_rating") or {}
    gh = (gk.get("home") or {}).get("rating")
    ga = (gk.get("away") or {}).get("rating")
    pos_h, pos_a = _stat(pack, home, "Ball Possession"), _stat(pack, away, "Ball Possession")
    sh_h, sh_a = _stat(pack, home, "Total Shots"), _stat(pack, away, "Total Shots")
    sog_h, sog_a = _stat(pack, home, "Shots on Goal"), _stat(pack, away, "Shots on Goal")
    sv_h, sv_a = _stat(pack, home, "Goalkeeper Saves"), _stat(pack, away, "Goalkeeper Saves")
    second_half = [f"{g['minute']}' {g['team']}" for g in (features.get("goal_timeline") or [])
                   if (g.get("minute_num") or 0) > 45]
    winner = home if ctx.get("result_winner") == "home" else away

    def card(zh, vi, en, field, val, metric):
        return {"title": loc(zh, vi, en), "value": val, "source_refs": [_ref(pack, field, metric, str(val))]}

    return {
        "model_name": factors["model_name"],
        "fixture_id": pack.get("fixture_id"),
        "report_type": "prediction_accountability_v0",
        "prediction_mode": "historical_replay",
        "not_real_archived_prediction": True,
        "last_checked_at": pack.get("last_checked_at"),
        "public_ready": False,
        "operation_status": "paused",

        "model_recap_summary": loc(
            f"ScoutScore v0.1 历史回放:模型会把 {home} 视为优势方,但结果是 {home} {sc.get('home')}–{sc.get('away')} {away},{winner} 爆冷取胜——这是一个模型升级样本(判定:{status.upper()})。",
            f"ScoutScore v0.1 phát lại lịch sử: mô hình xem {home} là đội nhỉnh hơn, nhưng kết quả là {home} {sc.get('home')}–{sc.get('away')} {away}, {winner} thắng bất ngờ — đây là một mẫu để nâng cấp mô hình (kết luận: {status.upper()}).",
            f"ScoutScore v0.1 replay: the model leans {home}, but {home} {sc.get('home')}–{sc.get('away')} {away} — {winner} won. A model-upgrade sample (verdict: {status.upper()})."),

        "historical_replay_statement": loc(
            "历史回放样例,用于验证产品流程;非真实赛前存档预测,不代表赛前命中。",
            "Mẫu phát lại lịch sử, dùng để kiểm tra quy trình sản phẩm; không phải dự đoán lưu trữ trước trận, không phải là đã đoán trúng trước trận.",
            "Historical-replay sample to validate the product flow; not a real archived pre-match prediction, not a claim of a pre-match hit."),

        "pre_match_model_view": {
            "expected_side": exp, "confidence_tier": factors["confidence_tier"],
            "view": loc(
                f"赛前(回放)模型基于纸面强弱把 {home} 视为优势方,置信度 {factors['confidence_tier']}——因缺少近期状态/Elo/伤停/xG 等真实赛前数据,判断主要建立在假设上。",
                f"Trước trận (phát lại), mô hình dựa trên sức mạnh trên giấy xem {home} là đội nhỉnh hơn, độ tin cậy {factors['confidence_tier']} — do thiếu phong độ gần đây/Elo/chấn thương/xG, nhận định chủ yếu dựa trên giả định.",
                f"Pre-match (replay), the model rates {home} the stronger side on paper, confidence {factors['confidence_tier']} — lacking recent form/Elo/injuries/xG, the view rests mostly on assumption."),
            "reasons_favored": [loc(
                f"纸面强弱偏向 {home}(假设,非接入数据)。", f"Sức mạnh trên giấy nghiêng về {home} (giả định, không phải dữ liệu đã tích hợp).",
                f"Paper strength favours {home} (assumption, not ingested data).")],
            "source_refs": [_ref(pack, "team_statistics", "possession/shots", None)],
        },

        "actual_result": {
            "score": f"{home} {sc.get('home')}–{sc.get('away')} {away}", "winner": winner,
            "text": loc(f"{winner} 以 {sc.get('home')}–{sc.get('away')} 取胜。", f"{winner} thắng với tỷ số {sc.get('home')}–{sc.get('away')}.",
                        f"{winner} won {sc.get('home')}–{sc.get('away')}."),
            "source_refs": [_ref(pack, "fixture", "final_score", f"{sc.get('home')}-{sc.get('away')}")],
        },

        "accountability_verdict": {
            "status": status,
            "text": loc(
                f"判定:{status.upper()}。模型倾向 {exp},实际 {winner} 取胜。",
                f"Kết luận: {status.upper()}. Mô hình nghiêng về {exp}, thực tế {winner} thắng.",
                f"Verdict: {status.upper()}. Model leaned {exp}; {winner} actually won."),
        },

        "what_model_got_right": [{
            "point": loc(
                f"模型预期 {home} 控场——确实兑现(控球 {pos_h}、射门 {sh_h} 次)。",
                f"Mô hình kỳ vọng {home} kiểm soát thế trận — đã đúng (kiểm soát bóng {pos_h}, {sh_h} cú sút).",
                f"The model expected {home} to control the game — confirmed (possession {pos_h}, {sh_h} shots)."),
            "source_refs": [_ref(pack, "team_statistics", "Ball Possession / Total Shots", f"{pos_h} / {sh_h}")]},
        ],

        "what_model_missed": [
            {"point": loc(
                f"射门效率:{away} {sog_a} 射正 → {sc.get('away')} 球 vs {home} {sog_h} 射正 → {sc.get('home')} 球。",
                f"Hiệu suất dứt điểm: {away} {sog_a} sút trúng → {sc.get('away')} bàn so với {home} {sog_h} sút trúng → {sc.get('home')} bàn.",
                f"Finishing efficiency: {away} {sog_a} on target → {sc.get('away')} goals vs {home} {sog_h} → {sc.get('home')}."),
             "source_refs": [_ref(pack, "team_statistics", "Shots on Goal", f"{sog_h} / {sog_a}"),
                             _ref(pack, "fixture", "final_score", f"{sc.get('home')}-{sc.get('away')}")]},
            {"point": loc(
                f"门将:{away} 门将评分 {ga} + {sv_a} 次扑救,{home} 门将 {gh}。",
                f"Thủ môn: thủ môn {away} điểm {ga} + {sv_a} lần cứu thua, thủ môn {home} {gh}.",
                f"Goalkeeper: {away} keeper {ga} + {sv_a} saves vs {home} keeper {gh}."),
             "source_refs": [_ref(pack, "player_statistics", "goalkeeper rating", f"home {gh} / away {ga}"),
                             _ref(pack, "team_statistics", "Goalkeeper Saves", f"{sv_h} / {sv_a}")]},
            {"point": loc(
                f"事件动量:下半场 {', '.join(second_half)} 完成反超。",
                f"Động lượng sự kiện: lội ngược dòng ở hiệp hai {', '.join(second_half)}.",
                f"Event momentum: second-half turnaround {', '.join(second_half)}."),
             "source_refs": [_ref(pack, "events_summary", "second-half goals", "; ".join(second_half))]},
            {"point": loc(
                "过度依赖纸面强弱,且缺少近期状态/伤停/xG 数据。",
                "Phụ thuộc quá nhiều vào sức mạnh trên giấy, thiếu dữ liệu phong độ/chấn thương/xG.",
                "Over-relied on paper strength; missing recent-form/injuries/xG data."),
             "source_refs": [], "assumption": True},
        ],

        "key_evidence": [
            card("控球率", "Kiểm soát bóng", "Possession", "team_statistics", f"{pos_h} / {pos_a}", "Ball Possession"),
            card("总射门", "Tổng số cú sút", "Total shots", "team_statistics", f"{sh_h} / {sh_a}", "Total Shots"),
            card("射正", "Sút trúng đích", "Shots on goal", "team_statistics", f"{sog_h} / {sog_a}", "Shots on Goal"),
            card("门将评分", "Điểm thủ môn", "Goalkeeper rating", "player_statistics", f"{gh} / {ga}", "goalkeeper rating"),
            card("门将扑救", "Số lần cứu thua", "Goalkeeper saves", "team_statistics", f"{sv_h} / {sv_a}", "Goalkeeper Saves"),
        ],

        "factor_validation": [
            {"factor": f["factor"], "direction": f["direction"], "pre_score": f["score"],
             "status": _FACTOR_STATUS.get(f["factor"], "n_a"), "data_status": f["data_status"],
             "note": loc(f["post_match_validation"], f["post_match_validation"], f["post_match_validation"]),
             "source_refs": f["source_refs"], "assumption": f.get("assumption", False)}
            for f in factors["factors"]
        ],

        "model_correction": {
            "summary": loc(
                "下版需:下调纯纸面强弱权重;新增/上调 效率、门将、事件动量;接入 近期状态/Elo、伤停(P0)、xG(P1)。",
                "Bản tiếp theo cần: giảm trọng số sức mạnh trên giấy; thêm/tăng yếu tố hiệu suất, thủ môn, động lượng; tích hợp phong độ/Elo, chấn thương (P0), xG (P1).",
                "Next version: down-weight pure paper strength; add/up-weight efficiency, goalkeeper, event momentum; ingest recent-form/Elo, injuries (P0), xG (P1)."),
            "changes": [
                loc("下调 team_strength 权重", "Giảm trọng số team_strength", "Down-weight team_strength"),
                loc("新增并提高 efficiency / goalkeeper / event_momentum 权重", "Thêm và tăng trọng số efficiency / goalkeeper / event_momentum", "Add & up-weight efficiency / goalkeeper / event_momentum"),
                loc("接入 recent_form / Elo 基线", "Tích hợp đường cơ sở recent_form / Elo", "Ingest recent_form / Elo baseline"),
            ],
            "next_data": [
                loc("伤停(P0)", "Chấn thương (P0)", "Injuries (P0)"),
                loc("xG(P1)", "xG (P1)", "xG (P1)"),
                loc("近期状态 / Elo(P1)", "Phong độ gần đây / Elo (P1)", "Recent form / Elo (P1)"),
            ],
            "ref_doc": "docs/MVP2_NEXT_DATA_REQUIREMENTS.md",
        },

        "operator_recap_copy": {
            "text": loc(
                f"这场爆冷说明,单看纸面强弱很容易高估 {home}。ScoutScore v0.1 在历史回放中会把 {home} 作为优势方,但赛后证据显示,{away} 的下半场反超、门将高评分和射门效率,是模型必须提高权重的关键因素。也就是说,这场不是简单冷门,而是一个模型升级样本。历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。",
                f"Trận bất ngờ này cho thấy chỉ nhìn sức mạnh trên giấy rất dễ đánh giá quá cao {home}. Trong phát lại lịch sử, ScoutScore v0.1 xem {home} là đội nhỉnh hơn, nhưng bằng chứng sau trận cho thấy màn lội ngược dòng hiệp hai, điểm thủ môn cao và hiệu suất dứt điểm của {away} là những yếu tố mô hình phải tăng trọng số. Nói cách khác, đây không chỉ là một cú sốc, mà là một mẫu để nâng cấp mô hình. Thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.",
                f"This upset shows paper strength easily over-rates {home}. In replay, ScoutScore v0.1 leans {home}, but post-match evidence — {away}'s second-half turnaround, high keeper rating and finishing efficiency — are factors the model must weight higher. So this isn't just a shock; it's a model-upgrade sample. Past performance does not represent future results — for data analysis and fan entertainment only."),
            "source_refs": [_ref(pack, "team_statistics", "possession/shots/saves", None),
                            _ref(pack, "events_summary", "second-half goals", "; ".join(second_half))],
        },

        "customer_hook_copy": {
            "text": loc(
                "这不是预测失败就结束——模型据此锁定下一版要补强的关键变量:效率、门将、事件动量。看 AI 如何自我升级。",
                "Đây không phải là kết thúc sau một dự đoán sai — mô hình từ đó khóa lại các biến số cần bổ sung cho bản sau: hiệu suất, thủ môn, động lượng sự kiện. Hãy xem AI tự nâng cấp.",
                "It doesn't end at a wrong call — the model locks in the variables to strengthen next: efficiency, goalkeeper, event momentum. Watch the AI upgrade itself."),
        },

        "missing_data_boundary": [
            loc("伤停:0 条返回,需二次数据源或当前赛季复验", "Chấn thương: 0 kết quả, cần nguồn thứ hai hoặc mùa giải hiện tại", "Injuries: 0 results, second source / current-season re-check required"),
            loc("xG:本轮未接入", "xG: chưa tích hợp trong vòng này", "xG: not ingested this round"),
            loc("近期状态 / Elo:未接入", "Phong độ / Elo: chưa tích hợp", "Recent form / Elo: not ingested"),
        ],

        "ai_boundary": {
            "allowed_fields": pack.get("ai_allowed_explanations") or [],
            "forbidden_fields": (pack.get("ai_forbidden_explanations") or []) + [
                "claiming a real archived pre-match prediction", "match-result prediction or financial signal"],
            "note": loc("AI 仅可解释已验证字段,且必须声明历史回放。", "AI chỉ giải thích các trường đã xác minh và phải nêu rõ là phát lại lịch sử.", "AI may only explain verified fields and must state it is a historical replay."),
        },

        "source_refs": [
            {"field": "team_statistics", "endpoint": "/fixtures/statistics", "source": SOURCE},
            {"field": "player_statistics", "endpoint": "/fixtures/players", "source": SOURCE},
            {"field": "events_summary", "endpoint": "/fixtures/events", "source": SOURCE},
            {"field": "fixture", "endpoint": "/fixtures", "source": SOURCE},
        ],
        "disclaimer": loc(
            "历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。",
            "Thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.",
            "Past performance does not represent future results — for data analysis and fan entertainment only."),
    }
