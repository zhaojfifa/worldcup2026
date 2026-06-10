from __future__ import annotations
"""
Internal operator preview — MVP-2 Scout Pack (NOT a public/customer surface).

`GET /internal/scout-pack?fixture_id=855737&lang=zh|vi`

- Renders the **already-ingested**, redacted Scout Pack sample as a server-side
  HTML page so operators can see real API-FOOTBALL Level-2 data in zh + vi.
- The backend reads a local JSON sample (no vendor call at render time, no DB,
  no API key needed to render) → the **frontend never calls the vendor**.
- Not mounted under `/api/v1`, not linked from any public nav, `noindex`.
- Light safety gate: in production, requires the admin token (header
  `x-admin-token` or `?token=`); open in dev/local so screenshots are frictionless.
- No betting / odds / market wording. injuries render "source required",
  never "no injuries". No AI deep analysis — only AI allowed/forbidden fields.
"""
import html
import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings

router = APIRouter(prefix="/internal", tags=["internal"])

SAMPLES_DIR = Path(__file__).resolve().parents[3] / "docs" / "data_audit" / "mvp2_scout_pack_samples"
SUPPORTED_LANGS = ("zh", "vi", "en")

LABELS: dict[str, dict[str, Any]] = {
    "zh": {
        "page_title": "真实数据情报包", "internal_banner": "内部预览 · 请勿对外分发 · 数据仅供内部验证",
        "data_source": "数据源", "fixture_id": "赛事 ID", "last_checked": "数据核对时间",
        "plan": "数据套餐", "operation_status": "运营状态", "operation_paused": "暂停（仅内部验证）",
        "coverage": "数据覆盖评分",
        "s_fixture": "赛事信息", "s_teams": "球队资料", "s_formation": "阵型", "s_coach": "教练",
        "s_lineups": "首发阵容", "s_events": "比赛事件", "s_team_stats": "球队统计",
        "s_player_stats": "球员统计", "s_squad": "球员名单", "s_ledger": "证据来源",
        "s_missing": "缺失证据", "s_ai": "AI 解释边界",
        "ai_allowed": "AI 可解释字段", "ai_forbidden": "AI 禁止解释字段", "ai_note": "AI 仅可解释已验证字段",
        "injuries_label": "伤停数据",
        "home": "主队", "away": "客队", "date": "日期", "venue": "球场", "league": "赛事",
        "round": "轮次", "status": "状态", "score": "最终比分", "result": "结果",
        "country": "国家", "founded": "成立", "formation": "阵型", "age": "年龄", "nationality": "国籍",
        "number": "号", "pos": "位置", "minute": "分钟", "type": "类型", "detail": "详情",
        "team": "球队", "assist": "助攻", "starters": "首发", "subs": "替补", "minutes": "出场",
        "rating": "评分", "goals": "进球", "assists": "助攻", "count": "人数", "total": "总数",
        "by_type": "按类型", "field": "字段", "source": "来源", "endpoint": "接口", "results": "结果数",
        "http": "状态码", "confidence": "置信度", "license": "授权", "available": "可用",
        "yes": "是", "no": "否",
        "winner": {"home": "主队胜", "away": "客队胜", "draw_or_unknown": "平局/未确认"},
    },
    "vi": {
        "page_title": "Gói dữ liệu trinh sát", "internal_banner": "Xem nội bộ · Không phân phối ra ngoài · Dữ liệu chỉ để kiểm tra nội bộ",
        "data_source": "Nguồn dữ liệu", "fixture_id": "Mã trận đấu", "last_checked": "Thời điểm kiểm tra dữ liệu",
        "plan": "Gói dữ liệu", "operation_status": "Trạng thái vận hành", "operation_paused": "Tạm dừng (chỉ kiểm tra nội bộ)",
        "coverage": "Điểm độ phủ dữ liệu",
        "s_fixture": "Thông tin trận đấu", "s_teams": "Thông tin đội", "s_formation": "Sơ đồ chiến thuật",
        "s_coach": "Huấn luyện viên", "s_lineups": "Đội hình xuất phát", "s_events": "Sự kiện trận đấu",
        "s_team_stats": "Thống kê đội", "s_player_stats": "Thống kê cầu thủ", "s_squad": "Danh sách cầu thủ",
        "s_ledger": "Nguồn dữ liệu", "s_missing": "Dữ liệu còn thiếu", "s_ai": "Giới hạn giải thích của AI",
        "ai_allowed": "Trường AI được giải thích", "ai_forbidden": "Trường AI không được giải thích",
        "ai_note": "AI chỉ được giải thích các trường đã được xác minh",
        "injuries_label": "Dữ liệu chấn thương",
        "home": "Đội nhà", "away": "Đội khách", "date": "Ngày", "venue": "Sân", "league": "Giải",
        "round": "Vòng", "status": "Trạng thái", "score": "Tỷ số cuối", "result": "Kết quả",
        "country": "Quốc gia", "founded": "Thành lập", "formation": "Sơ đồ", "age": "Tuổi", "nationality": "Quốc tịch",
        "number": "Số áo", "pos": "Vị trí", "minute": "Phút", "type": "Loại", "detail": "Chi tiết",
        "team": "Đội", "assist": "Kiến tạo", "starters": "Xuất phát", "subs": "Dự bị", "minutes": "Phút thi đấu",
        "rating": "Điểm", "goals": "Bàn thắng", "assists": "Kiến tạo", "count": "Số lượng", "total": "Tổng",
        "by_type": "Theo loại", "field": "Trường", "source": "Nguồn", "endpoint": "Endpoint", "results": "Số kết quả",
        "http": "Mã HTTP", "confidence": "Độ tin cậy", "license": "Giấy phép", "available": "Có sẵn",
        "yes": "Có", "no": "Không",
        "winner": {"home": "Đội nhà thắng", "away": "Đội khách thắng", "draw_or_unknown": "Hòa/chưa rõ"},
    },
}
LABELS["en"] = {**LABELS["zh"], **{
    "page_title": "Real-data Scout Pack", "internal_banner": "Internal preview · do not distribute · internal verification only",
    "data_source": "Data source", "fixture_id": "Fixture ID", "last_checked": "Data checked at",
    "plan": "Data plan", "operation_status": "Operation status", "operation_paused": "Paused (internal verification only)",
    "coverage": "Data-coverage score",
    "s_fixture": "Fixture", "s_teams": "Teams", "s_formation": "Formation", "s_coach": "Coach",
    "s_lineups": "Starting lineup", "s_events": "Match events", "s_team_stats": "Team statistics",
    "s_player_stats": "Player statistics", "s_squad": "Squad", "s_ledger": "Source ledger",
    "s_missing": "Missing evidence", "s_ai": "AI explanation boundary",
    "ai_allowed": "AI-explainable fields", "ai_forbidden": "AI-forbidden fields", "ai_note": "AI may only explain verified fields",
    "injuries_label": "Injuries", "home": "Home", "away": "Away", "date": "Date", "venue": "Venue",
    "league": "League", "round": "Round", "status": "Status", "score": "Final score", "result": "Result",
    "country": "Country", "founded": "Founded", "formation": "Formation", "age": "Age", "nationality": "Nationality",
    "number": "No.", "pos": "Pos", "minute": "Min", "type": "Type", "detail": "Detail", "team": "Team",
    "assist": "Assist", "starters": "Starters", "subs": "Subs", "minutes": "Minutes", "rating": "Rating",
    "goals": "Goals", "assists": "Assists", "count": "Count", "total": "Total", "by_type": "By type",
    "field": "Field", "source": "Source", "endpoint": "Endpoint", "results": "Results", "http": "HTTP",
    "confidence": "Confidence", "license": "License", "available": "Available", "yes": "Yes", "no": "No",
    "winner": {"home": "Home win", "away": "Away win", "draw_or_unknown": "Draw/unconfirmed"},
}}

_CSS = """
*{box-sizing:border-box}body{margin:0;background:#0b1f3a;color:#0b1f3a;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,'Noto Sans',sans-serif}
.wrap{max-width:1140px;margin:0 auto;padding:20px}
.banner{background:#b54708;color:#fff;padding:8px 14px;border-radius:8px;font-weight:700;font-size:13px;letter-spacing:.3px}
.head{background:#0e2a52;color:#fff;border-radius:14px;padding:18px 20px;margin:12px 0}
.head h1{margin:0 0 6px;font-size:22px}
.meta{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;color:#cfe0f7;margin-top:8px}
.meta b{color:#fff}
.note{font-size:12px;color:#9fb8db;margin-top:8px}
.card{background:#fff;border-radius:14px;padding:16px 18px;margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,.15)}
.card h2{margin:0 0 12px;font-size:17px;color:#0e2a52;border-left:4px solid #1f6feb;padding-left:10px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.kv{font-size:13px;line-height:1.7}.kv .k{color:#5b6b82}.kv .v{color:#0b1f3a;font-weight:600}
.team-col h3{margin:2px 0 8px;font-size:15px;color:#1f6feb}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #eef1f6}
th{color:#5b6b82;font-weight:600;background:#f7f9fc}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700}
.ok{background:#e6f4ea;color:#1a7f37}.bad{background:#fde8e8;color:#b42318}.warn{background:#fef3c7;color:#92400e}
.miss{background:#fff7ed;border:1px dashed #f59e0b;border-radius:10px;padding:10px 12px;color:#92400e;font-size:13px}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{background:#eef2ff;color:#1e3a8a;border-radius:8px;padding:4px 9px;font-size:12px}
.chip.bad{background:#fde8e8;color:#b42318}
.score{font-size:26px;font-weight:800;color:#0e2a52}
small.mut{color:#7a8aa0}
"""


def _esc(v: Any) -> str:
    return html.escape("" if v is None else str(v))


def _load_pack(fixture_id: str) -> Optional[dict]:
    path = SAMPLES_DIR / f"{fixture_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _loc(obj: Any, lang: str) -> str:
    if isinstance(obj, dict):
        return obj.get(lang) or obj.get("en") or obj.get("zh") or ""
    return _esc(obj)


def _kv(k: str, v: Any) -> str:
    return f'<div><span class="k">{_esc(k)}:</span> <span class="v">{_esc(v)}</span></div>'


def _fallback(env: dict, lang: str) -> str:
    return f'<div class="miss">⚠ {_esc(_loc(env.get("fallback_text"), lang))}</div>'


def _render(pack: dict, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    p: list[str] = []
    fx = pack.get("fixture", {})
    fxv = fx.get("value") or {}

    p.append(f'<div class="banner">⛔ {_esc(L["internal_banner"])}</div>')
    # header
    p.append('<div class="head">')
    title = _esc(L["page_title"])
    if fxv:
        title += f' — {_esc(fxv.get("home_team",{}).get("name"))} vs {_esc(fxv.get("away_team",{}).get("name"))}'
    p.append(f"<h1>{title}</h1>")
    p.append('<div class="meta">')
    p.append(f'<span><b>{_esc(L["data_source"])}:</b> API-FOOTBALL</span>')
    p.append(f'<span><b>{_esc(L["fixture_id"])}:</b> {_esc(pack.get("fixture_id"))}</span>')
    p.append(f'<span><b>{_esc(L["last_checked"])}:</b> {_esc(pack.get("last_checked_at"))}</span>')
    p.append(f'<span><b>{_esc(L["plan"])}:</b> {_esc(pack.get("plan"))}</span>')
    p.append(f'<span><b>{_esc(L["coverage"])}:</b> {_esc(pack.get("feature_snapshot",{}).get("coverage_score"))}%</span>')
    p.append(f'<span><b>{_esc(L["operation_status"])}:</b> {_esc(L["operation_paused"])}</span>')
    p.append("</div>")
    p.append(f'<div class="note">{_esc(_loc(pack.get("license_note"), lang))}</div>')
    p.append(f'<div class="note">{_esc(_loc(pack.get("feature_snapshot",{}).get("coverage_score_note"), lang))}</div>')
    p.append("</div>")

    # fixture
    p.append(f'<div class="card"><h2>{_esc(L["s_fixture"])}</h2>')
    if fx.get("available"):
        winner = L["winner"].get(fxv.get("result_winner"), fxv.get("result_winner"))
        p.append('<div class="grid2"><div class="kv">')
        p.append(_kv(L["date"], fxv.get("date")))
        p.append(_kv(L["league"], (fxv.get("league") or {}).get("name")))
        p.append(_kv(L["round"], (fxv.get("league") or {}).get("round")))
        p.append(_kv(L["status"], fxv.get("status")))
        p.append('</div><div class="kv">')
        p.append(_kv(L["venue"], f'{(fxv.get("venue") or {}).get("name")}, {(fxv.get("venue") or {}).get("city")}'))
        sc = fxv.get("final_score") or {}
        p.append(f'<div class="score">{_esc(fxv.get("home_team",{}).get("name"))} '
                 f'{_esc(sc.get("home"))}–{_esc(sc.get("away"))} {_esc(fxv.get("away_team",{}).get("name"))}</div>')
        p.append(_kv(L["result"], winner))
        p.append("</div></div>")
    else:
        p.append(_fallback(fx, lang))
    p.append("</div>")

    # teams + formation + coach (combined row)
    teams = pack.get("teams", {}); tv = teams.get("value") or {}
    formation = pack.get("formation", {}); fv = formation.get("value") or {}
    coach = pack.get("coach", {}); cv = coach.get("value") or {}
    p.append('<div class="card"><div class="grid2">')
    for side in ("home", "away"):
        p.append('<div class="team-col">')
        team = tv.get(side) or {}
        p.append(f'<h3>{_esc(L[side])}: {_esc(team.get("name"))}</h3><div class="kv">')
        if teams.get("available"):
            p.append(_kv(L["country"], team.get("country")))
            p.append(_kv(L["founded"], team.get("founded")))
            v = team.get("venue") or {}
            p.append(_kv(L["venue"], f'{v.get("name")}, {v.get("city")}'))
        p.append(_kv(L["formation"], (fv.get(side) or {}).get("formation") if formation.get("available") else "—"))
        co = cv.get(side) or {}
        if coach.get("available"):
            p.append(_kv(L["s_coach"], f'{co.get("name")} · {co.get("nationality") or ""} · {co.get("age") or ""}'))
        p.append("</div></div>")
    p.append("</div>")
    if not formation.get("available"):
        p.append(_fallback(formation, lang))
    if not coach.get("available"):
        p.append(_fallback(coach, lang))
    p.append("</div>")

    # lineups
    lineups = pack.get("lineups", {})
    p.append(f'<div class="card"><h2>{_esc(L["s_lineups"])}</h2>')
    if lineups.get("available"):
        p.append('<div class="grid2">')
        for team in lineups.get("value") or []:
            p.append('<div class="team-col">')
            p.append(f'<h3>{_esc((team.get("team") or {}).get("name"))} · {_esc(team.get("formation"))}</h3>')
            p.append(f'<table><tr><th>{_esc(L["number"])}</th><th>{_esc(L["pos"])}</th><th>{_esc(L["starters"])}</th></tr>')
            for pl in team.get("startXI") or []:
                p.append(f'<tr><td>{_esc(pl.get("number"))}</td><td>{_esc(pl.get("pos"))}</td><td>{_esc(pl.get("name"))}</td></tr>')
            p.append("</table>")
            subs = ", ".join(_esc(s.get("name")) for s in (team.get("substitutes") or []))
            p.append(f'<div class="kv" style="margin-top:6px"><span class="k">{_esc(L["subs"])}:</span> <small class="mut">{subs}</small></div>')
            p.append("</div>")
        p.append("</div>")
    else:
        p.append(_fallback(lineups, lang))
    p.append("</div>")

    # events
    events = pack.get("events_summary", {}); ev = events.get("value") or {}
    p.append(f'<div class="card"><h2>{_esc(L["s_events"])}</h2>')
    if events.get("available"):
        chips = " ".join(f'<span class="chip">{_esc(k)}: {_esc(v)}</span>' for k, v in (ev.get("by_type") or {}).items())
        p.append(f'<div class="chips" style="margin-bottom:10px"><span class="chip">{_esc(L["total"])}: {_esc(ev.get("total"))}</span>{chips}</div>')
        p.append(f'<table><tr><th>{_esc(L["minute"])}</th><th>{_esc(L["type"])}</th><th>{_esc(L["detail"])}</th><th>{_esc(L["team"])}</th><th>{_esc(L["pos"])}/{_esc(L["assist"])}</th></tr>')
        for e in ev.get("timeline") or []:
            who = _esc(e.get("player"))
            if e.get("assist"):
                who += f' <small class="mut">({_esc(L["assist"])}: {_esc(e.get("assist"))})</small>'
            p.append(f'<tr><td>{_esc(e.get("minute"))}\'</td><td>{_esc(e.get("type"))}</td><td>{_esc(e.get("detail"))}</td><td>{_esc(e.get("team"))}</td><td>{who}</td></tr>')
        p.append("</table>")
    else:
        p.append(_fallback(events, lang))
    p.append("</div>")

    # team statistics
    tstats = pack.get("team_statistics", {})
    p.append(f'<div class="card"><h2>{_esc(L["s_team_stats"])}</h2>')
    if tstats.get("available"):
        cols = tstats.get("value") or []
        keys = list((cols[0].get("stats") if cols else {}).keys())
        p.append(f'<table><tr><th>{_esc(L["field"])}</th>')
        for c in cols:
            p.append(f'<th>{_esc(c.get("team"))}</th>')
        p.append("</tr>")
        for k in keys:
            p.append(f'<tr><td>{_esc(k)}</td>')
            for c in cols:
                p.append(f'<td>{_esc((c.get("stats") or {}).get(k))}</td>')
            p.append("</tr>")
        p.append("</table>")
    else:
        p.append(_fallback(tstats, lang))
    p.append("</div>")

    # player statistics
    pstats = pack.get("player_statistics", {})
    p.append(f'<div class="card"><h2>{_esc(L["s_player_stats"])} <small class="mut">(top by {_esc(L["rating"])})</small></h2>')
    if pstats.get("available"):
        p.append('<div class="grid2">')
        for col in pstats.get("value") or []:
            p.append('<div class="team-col">')
            p.append(f'<h3>{_esc(col.get("team"))} <small class="mut">({_esc(L["count"])}: {_esc(col.get("players_count"))})</small></h3>')
            p.append(f'<table><tr><th>{_esc(L["pos"])}</th><th>player</th><th>{_esc(L["minutes"])}</th><th>{_esc(L["rating"])}</th><th>{_esc(L["goals"])}</th></tr>')
            for pl in col.get("top_by_rating") or []:
                p.append(f'<tr><td>{_esc(pl.get("pos"))}</td><td>{_esc(pl.get("name"))}</td><td>{_esc(pl.get("minutes"))}</td><td>{_esc(pl.get("rating"))}</td><td>{_esc(pl.get("goals"))}</td></tr>')
            p.append("</table></div>")
        p.append("</div>")
    else:
        p.append(_fallback(pstats, lang))
    p.append("</div>")

    # squad (availability summary)
    squad = pack.get("squad", {}); sv = squad.get("value") or {}
    p.append(f'<div class="card"><h2>{_esc(L["s_squad"])}</h2>')
    if squad.get("available"):
        p.append('<div class="chips">')
        for side in ("home", "away"):
            s = sv.get(side) or {}
            if s:
                p.append(f'<span class="chip">{_esc(s.get("team"))}: {_esc(s.get("players_count"))} {_esc(L["count"])}</span>')
        p.append("</div>")
    else:
        p.append(_fallback(squad, lang))
    p.append("</div>")

    # missing evidence (injuries highlighted)
    p.append(f'<div class="card"><h2>{_esc(L["s_missing"])}</h2>')
    me = pack.get("missing_evidence") or {}
    if me:
        for k, m in me.items():
            label = L["injuries_label"] if k == "injuries" else k
            p.append(f'<div class="miss"><b>{_esc(label)}</b> — {_esc(_loc(m.get("fallback_text"), lang))}'
                     f'<br><small class="mut">{_esc(m.get("reason"))} · {_esc(m.get("endpoint"))}</small></div>')
    else:
        p.append('<div class="kv">—</div>')
    p.append("</div>")

    # source ledger
    p.append(f'<div class="card"><h2>{_esc(L["s_ledger"])}</h2>')
    p.append(f'<table><tr><th>{_esc(L["field"])}</th><th>{_esc(L["source"])}</th><th>{_esc(L["endpoint"])}</th>'
             f'<th>{_esc(L["results"])}</th><th>{_esc(L["http"])}</th><th>{_esc(L["confidence"])}</th>'
             f'<th>{_esc(L["license"])}</th><th>{_esc(L["available"])}</th></tr>')
    for fkey, row in (pack.get("source_ledger") or {}).items():
        av = row.get("available")
        pill = f'<span class="pill {"ok" if av else "bad"}">{_esc(L["yes"] if av else L["no"])}</span>'
        p.append(f'<tr><td>{_esc(fkey)}</td><td>{_esc(row.get("source"))}</td><td>{_esc(row.get("endpoint"))}</td>'
                 f'<td>{_esc(row.get("results"))}</td><td>{_esc(row.get("http_status"))}</td>'
                 f'<td>{_esc(row.get("confidence"))}</td><td>{_esc(row.get("license_status"))}</td><td>{pill}</td></tr>')
    p.append("</table></div>")

    # AI boundary
    p.append(f'<div class="card"><h2>{_esc(L["s_ai"])}</h2>')
    p.append(f'<div class="note" style="color:#0e2a52;font-weight:700">{_esc(L["ai_note"])}</div>')
    p.append(f'<div style="margin:8px 0 4px"><b>{_esc(L["ai_allowed"])}</b></div><div class="chips">')
    for a in pack.get("ai_allowed_explanations") or []:
        p.append(f'<span class="chip">{_esc(a)}</span>')
    p.append("</div>")
    p.append(f'<div style="margin:10px 0 4px"><b>{_esc(L["ai_forbidden"])}</b></div><div class="chips">')
    for a in pack.get("ai_forbidden_explanations") or []:
        p.append(f'<span class="chip bad">{_esc(a)}</span>')
    p.append("</div></div>")

    body = "\n".join(p)
    return (
        f'<!doctype html><html lang="{_esc(lang)}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="robots" content="noindex,nofollow">'
        f'<title>{_esc(L["page_title"])} · {_esc(pack.get("fixture_id"))}</title>'
        f"<style>{_CSS}</style></head><body><div class=\"wrap\">{body}</div></body></html>"
    )


def _authorized(request: Request, token: Optional[str]) -> bool:
    """In production, require the admin token (header or ?token=). Open in dev."""
    settings = get_settings()
    if settings.app_env != "production" or not settings.admin_api_token:
        return True
    provided = request.headers.get("x-admin-token") or token or ""
    return provided == settings.admin_api_token


@router.get("/scout-pack", response_class=HTMLResponse)
def scout_pack_preview(
    request: Request,
    fixture_id: str = Query("855737"),
    lang: str = Query("zh"),
    token: Optional[str] = Query(None),
):
    if not _authorized(request, token):
        return HTMLResponse("<h1>401 — internal preview requires admin token</h1>", status_code=401)
    if lang not in SUPPORTED_LANGS:
        lang = "zh"
    pack = _load_pack(fixture_id)
    if pack is None:
        return HTMLResponse(
            f"<h1>404 — no ingested Scout Pack for fixture {_esc(fixture_id)}</h1>"
            "<p>Run: <code>python backend/scripts/mvp2_ingest_scout_pack.py "
            f"{_esc(fixture_id)}</code></p>",
            status_code=404,
        )
    return HTMLResponse(_render(pack, lang))
