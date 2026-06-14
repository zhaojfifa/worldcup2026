#!/usr/bin/env python3
"""
P1.5c — Agent-led Daily Editorial Selection (prompt builder ONLY).

Owner correction (2026-06-13): we are building an agent product on top of LLMs, NOT a
hand-coded sports ranking engine. So this helper does NOT score teams, rank countries,
or encode match-importance weights. It only:

  1. reads today's fixture slate from the EXISTING local daily-fixture data, and
  2. prints a clean, copy-paste prompt for an external LLM (DeepSeek / Gemini / Kimi).

The OPERATOR pastes that prompt into the LLM of their choice, reads back the structured
JSON recommendation, and decides manually what (if anything) becomes public. Engineering
provides facts + a safe prompt; the LLM provides editorial judgment; the operator confirms.

What this script will NEVER do:
  - call any external LLM / paid API
  - write any production state (no daily-fixtures upload, no manifest write)
  - send anything, confirm join-intents, or issue contribution value
  - hard-code popularity / ranking / hotspot / importance weights

Usage:
  python3 scripts/mvp2_editorial_agent.py prompt --date 2026-06-13 --lang zh
  python3 scripts/mvp2_editorial_agent.py prompt --date 2026-06-13 --lang vi
  python3 scripts/mvp2_editorial_agent.py --selftest

Reads (first that exists wins):
  docs/data_audit/mvp2_match_sync/daily_fixtures_YYYYMMDD.json   (richest registry)
  frontend/public/data/daily-fixtures.json                       (runtime manifest)
  frontend/src/data/dailyFixtures.generated.json                 (build-time fallback)
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SYNC_DIR = ROOT / "docs" / "data_audit" / "mvp2_match_sync"
RUNTIME_MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
GENERATED_MANIFEST = ROOT / "frontend" / "src" / "data" / "dailyFixtures.generated.json"

LANGS = ("zh", "vi", "my", "en")

# Forbidden vocabulary surfaced INTO the prompt as a hard constraint for the LLM. This is a
# representative list (not the full guard) — the operator still runs scripts/check_growth_copy.py
# on any copy before it is published.
FORBIDDEN_SURFACED = [
    "下注 / 投注 / 博彩 / 盘口 / 赔率 / 让球 / 竞猜 / 跟单 / 购彩",
    "稳赚 / 稳赢 / 必中 / 必赢 / 包赢 / 保赢",
    "返佣 / 佣金 / 提现 (except 不可提现) / 充值 / 派彩 / 分成",
    "kèo / cửa trên / cửa dưới / nhà cái / cá cược / soi kèo / tài xỉu",
    "betting / odds / handicap / bookmaker / wager / parlay / guaranteed win / payout",
]


# ---------------------------------------------------------------------------
# Fixture slate reading (existing local data only — no fetch, no fabrication)
# ---------------------------------------------------------------------------
def _norm_registry(raw):
    """Normalize the rich registry shape (daily_fixtures_YYYYMMDD.json)."""
    out = []
    for f in raw.get("fixtures", []):
        out.append({
            "fixture_id": f.get("internal_fixture_id") or f.get("external_game_id"),
            "match": "{} vs {}".format(f.get("home_team", "?"), f.get("away_team", "?")),
            "kickoff_utc": f.get("kickoff_time_utc"),
            "status": f.get("status"),
            "lifecycle_state": f.get("lifecycle_state"),
            "score": _score(f.get("score_home"), f.get("score_away")),
            "pre_match_allowed": f.get("pre_match_allowed"),
            "recap_ready": f.get("recap_ready"),
            "recap_needed": f.get("recap_needed"),
            "renderable": f.get("narrative_renderable"),
            "hero_candidate": f.get("hero_candidate"),
            "recap_candidate": f.get("recap_candidate"),
            "next_candidate": f.get("next_candidate"),
        })
    return out


def _norm_manifest(raw):
    """Normalize the frontend runtime/build manifest shape (daily-fixtures.json)."""
    out = []
    for f in raw.get("fixtures", []):
        out.append({
            "fixture_id": f.get("id") or f.get("external_game_id"),
            "match": "{} vs {}".format(f.get("home", "?"), f.get("away", "?")),
            "kickoff_utc": f.get("kickoffUtc"),
            "status": f.get("status"),
            "lifecycle_state": f.get("lifecycle_state"),
            "score": _score(f.get("scoreHome"), f.get("scoreAway")),
            "pre_match_allowed": f.get("preMatchAllowed"),
            "recap_ready": f.get("recapReady"),
            "recap_needed": f.get("recapNeeded"),
            "renderable": f.get("renderable"),
            "hero_candidate": f.get("heroCandidate"),
            "recap_candidate": f.get("recapCandidate"),
            "next_candidate": f.get("nextCandidate"),
        })
    return out


def _score(h, a):
    if h is None or a is None:
        return None
    return "{}-{}".format(h, a)


def load_slate(date):
    """Return (source_path, date_in_data, [fixture dicts]) from the first existing source."""
    registry = SYNC_DIR / "daily_fixtures_{}.json".format(date.replace("-", ""))
    if registry.exists():
        raw = json.loads(registry.read_text(encoding="utf-8"))
        return registry, raw.get("date", date), _norm_registry(raw)

    for manifest in (RUNTIME_MANIFEST, GENERATED_MANIFEST):
        if manifest.exists():
            raw = json.loads(manifest.read_text(encoding="utf-8"))
            in_data = raw.get("generated_for_date") or raw.get("date") or date
            return manifest, in_data, _norm_manifest(raw)

    return None, date, []


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------
def _slate_block(fixtures):
    lines = []
    for f in fixtures:
        bits = [
            "fixture_id={}".format(f["fixture_id"]),
            f["match"],
            "status={}".format(f["status"]),
            "lifecycle={}".format(f["lifecycle_state"]),
        ]
        if f["kickoff_utc"]:
            bits.append("kickoff_utc={}".format(f["kickoff_utc"]))
        if f["score"]:
            bits.append("score={}".format(f["score"]))
        bits.append("pre_match_allowed={}".format(f["pre_match_allowed"]))
        bits.append("recap_ready={}".format(f["recap_ready"]))
        bits.append("recap_needed={}".format(f["recap_needed"]))
        bits.append("renderable={}".format(f["renderable"]))
        lines.append("- " + " · ".join(str(b) for b in bits))
    return "\n".join(lines) if lines else "- (no fixtures found for this date)"


SCHEMA = """{
  "date": "YYYY-MM-DD",
  "featured_pre_match": {
    "fixture_id": "...",
    "match": "...",
    "reason": "...",
    "public_angle": "...",
    "score_call": "...",
    "risk_note": "..."
  },
  "featured_recap": {
    "fixture_id": "... or null",
    "match": "... or null",
    "reason": "...",
    "public_angle": "..."
  },
  "fallback_recap": {
    "fixture_id": "... or null",
    "match": "... or null",
    "reason": "..."
  },
  "group_only_suggestions": [
    { "fixture_id": "...", "match": "...", "reason": "..." }
  ],
  "hold_reason": null
}"""

LANG_LABEL = {
    "zh": "Write all human-readable fields (reason / public_angle / score_call / risk_note) in 简体中文 (Chinese).",
    "vi": "Write all human-readable fields (reason / public_angle / score_call / risk_note) in Vietnamese. Do NOT use Chinese.",
    "my": "Write all human-readable fields (reason / public_angle / score_call / risk_note) in Burmese (Myanmar). Do NOT use Chinese.",
    "en": "Write all human-readable fields in English.",
}


def build_prompt(date, lang, source_path, fixtures):
    src = source_path.relative_to(ROOT) if source_path else "(none found)"
    return """You are the daily football-editorial assistant for "Giành Cup", a World Cup 2026
AI football-intelligence community (NOT a betting product). Your job is to RECOMMEND today's
editorial selection. You do NOT publish anything — a human operator reviews your recommendation
and decides what becomes public. Give judgment, not certainty.

== TODAY ==
date: {date}
output language: {lang}  — {lang_label}

== TODAY'S FIXTURE SLATE (facts only; source: {src}) ==
{slate}

== PRODUCT POLICY (what "public" means) ==
- Exactly ONE public featured PRE-MATCH pick per day.
- Exactly ONE public featured RECAP per day.
- All other matches are lightweight STATUS only (completed → completed status; upcoming → upcoming status).
- Extra match service (more picks, more recaps) is handled MANUALLY inside the group, not on the public homepage.
- Your recommendation is NOT automatically public. The operator must confirm it before anything ships.

== CURRENT HOMEPAGE POLICY (the running editorial line — change only with a strong reason) ==
- Brazil vs Morocco should remain the daily story (featured pre-match) until its kickoff.
- Mexico vs South Africa may remain the secondary featured recap if no better recap-ready match exists.
- Completed non-featured matches remain completed status only.
- Upcoming non-featured matches remain upcoming status only.

== HARD CONSTRAINTS ==
- A pre-match pick is only valid for a fixture with pre_match_allowed=True (not yet kicked off / frozen).
- A featured/fallback recap is only valid for a fixture with recap_ready=True. If none is recap_ready,
  set featured_recap fields to null and explain in fallback_recap.reason.
- Never invent a score. Use ONLY the scores shown above. recap_needed=True with recap_ready=False means
  "finished but no recap available yet" — that is NOT publishable as a recap.
- If nothing should change / publish today, set "hold_reason" to a short explanation and leave the picks
  reflecting the current homepage policy.

== SAFETY (forbidden — never use this vocabulary in any field) ==
{forbidden}
Also: no invented scores, no fake recap, no auto-send, do not claim certainty, do not imply the pick is
already published. This is fan analysis & entertainment, not betting advice.

== OUTPUT ==
Respond with ONLY this JSON object (no prose before or after, no markdown fences):
{schema}
""".format(
        date=date,
        lang=lang,
        lang_label=LANG_LABEL[lang],
        src=src,
        slate=_slate_block(fixtures),
        forbidden="\n".join("- " + f for f in FORBIDDEN_SURFACED),
        schema=SCHEMA,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_prompt(args):
    if args.lang not in LANGS:
        sys.stderr.write("error: --lang must be one of {}\n".format(", ".join(LANGS)))
        return 2
    source_path, date_in_data, fixtures = load_slate(args.date)
    if source_path is None:
        sys.stderr.write(
            "error: no local daily-fixture data found for {} (looked in {} and {}).\n"
            "Run scripts/mvp2_match_sync.py first, or pass a date that has a registry file.\n".format(
                args.date, SYNC_DIR, RUNTIME_MANIFEST)
        )
        return 1
    if date_in_data != args.date:
        sys.stderr.write(
            "note: requested date {} but data source is for {} (fell back to the manifest).\n".format(
                args.date, date_in_data)
        )
    sys.stdout.write(build_prompt(args.date, args.lang, source_path, fixtures))
    return 0


def selftest():
    fixtures = _norm_manifest({"fixtures": [
        {"id": "1489371", "home": "Brazil", "away": "Morocco", "kickoffUtc": "2026-06-13T22:00:00+00:00",
         "status": "scheduled", "lifecycle_state": "SCHEDULED", "preMatchAllowed": True,
         "recapReady": False, "recapNeeded": False, "renderable": True,
         "heroCandidate": True, "recapCandidate": False, "nextCandidate": False,
         "scoreHome": None, "scoreAway": None},
        {"id": "1489369", "home": "Mexico", "away": "South Africa", "kickoffUtc": "2026-06-11T19:00:00+00:00",
         "status": "finished", "lifecycle_state": "RECAP_READY", "preMatchAllowed": False,
         "recapReady": True, "recapNeeded": False, "renderable": True,
         "heroCandidate": False, "recapCandidate": False, "nextCandidate": False,
         "scoreHome": 2, "scoreAway": 0},
    ]})
    checks = []
    p = build_prompt("2026-06-13", "zh", RUNTIME_MANIFEST, fixtures)
    checks.append(("schema keys present", all(k in p for k in (
        "featured_pre_match", "featured_recap", "fallback_recap", "group_only_suggestions", "hold_reason"))))
    checks.append(("slate fixtures rendered", "fixture_id=1489371" in p and "fixture_id=1489369" in p))
    checks.append(("score shown for finished", "score=2-0" in p))
    checks.append(("pre_match_allowed surfaced", "pre_match_allowed=True" in p))
    checks.append(("forbidden vocab block present", "betting" in p and "盘口" in p))
    checks.append(("score helper", _score(2, 0) == "2-0" and _score(None, 1) is None))
    checks.append(("lang label vi non-chinese", "Vietnamese" in LANG_LABEL["vi"]))
    ok = all(v for _, v in checks)
    for name, v in checks:
        sys.stdout.write("{} {}\n".format("PASS" if v else "FAIL", name))
    sys.stdout.write("{}/{} checks pass\n".format(sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="P1.5c daily editorial prompt builder (no external API, no send).")
    sub = ap.add_subparsers(dest="cmd")
    pp = sub.add_parser("prompt", help="print a copy-paste LLM prompt for the given date/lang")
    pp.add_argument("--date", required=True, help="YYYY-MM-DD")
    pp.add_argument("--lang", default="zh", help="zh|vi|my|en (default zh)")
    pp.set_defaults(func=cmd_prompt)
    ap.add_argument("--selftest", action="store_true", help="run embedded checks and exit")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
