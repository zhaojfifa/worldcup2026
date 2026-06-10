from __future__ import annotations
"""
MVP-2 Pre-match Scout Pack — internal data contract (Phase 0).

Every leaf field is wrapped in an **Evidence Field envelope** so the internal
operator preview can render real data OR an honest "source required" for the
rest. Hard rules baked into this contract:

- **No fabrication.** A field is `available=True` only when a real source
  returned a non-empty payload. Otherwise `value=None` and a localized
  `fallback_text` / `missing_reason` is shown.
- **injuries are never assumed.** `injuries` returning 0 results is recorded as
  *unresolved* (source required) — never written as "no injuries".
- **AI is restricted.** AI explanation may only cite fields that are
  `available=True && license_status in {ok}`; everything else is forbidden.
- Pure data/contract logic — **no network, no DB, no secrets** in this module.

The envelope follows the Owner Phase-0 shape; `fallback_text` is a localized
object (`{zh, vi, en}`) per the architecture (Evidence Board v2 §5), so a single
language-agnostic JSON sample can drive both the zh and vi operator previews.
"""
from typing import Any, Literal, Optional

SCOUT_PACK_SCHEMA_VERSION = "mvp2-scout-pack/1.0"
SOURCE_API_FOOTBALL = "api-football"

Confidence = Literal["high", "medium", "low"]
LicenseStatus = Literal["ok", "pending", "non_commercial", "excluded"]

# Top-level Scout Pack sections (Owner Phase-0 contract order).
SECTION_KEYS = [
    "fixture",
    "teams",
    "lineups",
    "formation",
    "coach",
    "squad",
    "events_summary",
    "team_statistics",
    "player_statistics",
]

# --- Bounding / redaction limits (keep the sample small; no raw vendor dump) ---
MAX_EVENTS = 30
MAX_PLAYER_STATS_PER_TEAM = 6      # top-N by rating
MAX_SQUAD_SAMPLE_PER_TEAM = 11     # count is always kept; only the sample is bounded
MAX_TEAM_STATS_PER_TEAM = 20


def loc(zh: str, vi: str, en: str = "") -> dict:
    """Localized string object. `vi` MUST contain zero Han characters."""
    return {"zh": zh, "vi": vi, "en": en or vi}


def evidence_field(
    value: Any = None,
    available: bool = False,
    *,
    source: Optional[str] = SOURCE_API_FOOTBALL,
    endpoint: str = "",
    fixture_id: Any = "",
    last_checked_at: str = "",
    confidence: Confidence = "low",
    license_status: LicenseStatus = "pending",
    fallback_text: Optional[dict] = None,
    missing_reason: str = "",
) -> dict:
    """Build one Evidence Field envelope (Owner Phase-0 shape).

    When ``available`` is False the ``value`` is forced to ``None`` and the
    consumer renders ``fallback_text`` (never AI prose). ``confidence`` only
    carries meaning for available fields.
    """
    return {
        "value": value if available else None,
        "available": bool(available),
        "source": source,
        "endpoint": endpoint,
        "fixture_id": "" if fixture_id in ("", None) else str(fixture_id),
        "last_checked_at": last_checked_at,
        "confidence": confidence if available else "low",
        "license_status": license_status,
        "fallback_text": fallback_text or FALLBACK_GENERIC,
        "missing_reason": "" if available else missing_reason,
    }


# --- Canonical localized strings (shared by builder data + preview chrome) ----
# vi strings are authored Vietnamese with zero Han; en is the system fallback.
FALLBACK_GENERIC = loc(
    "数据未接入，需数据源",
    "Chưa có dữ liệu, cần nguồn dữ liệu",
    "Source required",
)
FALLBACK_LINEUPS = loc(
    "首发未接入，需数据源",
    "Chưa có đội hình xuất phát, cần nguồn dữ liệu",
    "Lineup source required",
)
FALLBACK_FORMATION = loc(
    "阵型未接入，需首发数据",
    "Chưa có sơ đồ chiến thuật, cần dữ liệu đội hình",
    "Formation source required",
)
FALLBACK_COACH = loc(
    "教练未接入，需数据源",
    "Chưa có huấn luyện viên, cần nguồn dữ liệu",
    "Coach source required",
)
FALLBACK_EVENTS = loc(
    "比赛事件未接入",
    "Chưa có sự kiện trận đấu",
    "Events source required",
)
FALLBACK_TEAM_STATS = loc(
    "球队统计未接入",
    "Chưa có thống kê đội",
    "Team statistics source required",
)
FALLBACK_PLAYER_STATS = loc(
    "球员统计未接入",
    "Chưa có thống kê cầu thủ",
    "Player statistics source required",
)
FALLBACK_SQUAD = loc(
    "球员名单未接入",
    "Chưa có danh sách cầu thủ",
    "Squad source required",
)

# injuries: the verified gap — must read "source required", never "no injuries".
MISSING_INJURIES = loc(
    "伤停数据未返回，需二次数据源或当前赛季复验",
    "Dữ liệu chấn thương chưa có, cần xác minh bằng nguồn thứ hai hoặc mùa giải hiện tại",
    "Injuries data not returned — second source or current-season re-check required",
)

# AI guardrail note shown on the preview.
AI_ONLY_VERIFIED = loc(
    "AI 仅可解释已验证字段",
    "AI chỉ được giải thích các trường đã được xác minh",
    "AI may only explain verified fields",
)

# License posture for this internal round. The account is a paid Pro plan
# (commercial-capable), but external operation stays paused and commercial
# terms are Owner-gated, so the ledger carries an explicit note.
LICENSE_NOTE_INTERNAL = loc(
    "内部预览：API-FOOTBALL Pro 套餐，对外商用条款由 Owner 复核，运营暂停",
    "Xem nội bộ: gói API-FOOTBALL Pro, điều khoản thương mại do Owner duyệt, vận hành tạm dừng",
    "Internal preview: API-FOOTBALL Pro plan; commercial terms Owner-gated; operation paused",
)


def missing_field(
    fallback_text: dict,
    missing_reason: str,
    *,
    endpoint: str = "",
    fixture_id: Any = "",
    last_checked_at: str = "",
    source: Optional[str] = SOURCE_API_FOOTBALL,
    license_status: LicenseStatus = "pending",
) -> dict:
    """Shortcut for an unavailable Evidence Field (honest empty)."""
    return evidence_field(
        value=None,
        available=False,
        source=source,
        endpoint=endpoint,
        fixture_id=fixture_id,
        last_checked_at=last_checked_at,
        license_status=license_status,
        fallback_text=fallback_text,
        missing_reason=missing_reason,
    )
