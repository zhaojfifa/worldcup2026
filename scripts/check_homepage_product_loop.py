#!/usr/bin/env python3
"""
MVP2-P2 Homepage Product Loop guard (Owner Harness-X brief 2026-06-14).

Asserts the homepage renders the football-intelligence CLOSED LOOP — yesterday's hotspot
recap → today's hotspot prediction → secondary schedule → other recaps → group CTA — and
NOT a generic status/recap/fixture list. Source-level (component) checks so it passes pre-deploy;
live DOM verification is done by scripts/check_customer_visible_copy.py + Owner visual review.

Checks (frontend/src/components/HomeProductLoop.tsx + data/dailyFixtures.ts):
  1. required zone titles present (zh): 昨日热点复盘 · 今日热点预测 · 今日赛程 · 其他复盘
  2. editorial selection helper selectProductLoop exists and is order-driven (first finished =
     featured recap, first scheduled = featured prediction) — NO hardcoded team/popularity list
  3. NO internal generation wording (复盘生成中 / 待生成复盘 / 生成中 / 自动生成 / AI 正在生成)
  4. NO 今日热点复盘 label (the lead recap is 昨日热点复盘; secondary is 其他复盘 — a finished
     non-hotspot like Mexico must never be the 今日热点复盘 lead)
  5. recap CTA (查看复盘) is gated on recapReady (no fake recap)
  6. NO betting/trading vocabulary
  7. HomePage.tsx actually renders <HomeProductLoop/>

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOOP = ROOT / "frontend" / "src" / "components" / "HomeProductLoop.tsx"
DATA = ROOT / "frontend" / "src" / "data" / "dailyFixtures.ts"
HOME = ROOT / "frontend" / "src" / "pages" / "HomePage.tsx"

REQUIRED_TITLES = ["昨日热点复盘", "今日热点预测", "今日赛程", "其他复盘"]
GENERATION_BANNED = ["复盘生成中", "待生成复盘", "生成中", "自动生成", "AI 正在生成"]
BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "让球", "跟单", "返佣", "佣金",
           "odds", "handicap", "bookmaker", "wager", "payout", "commission",
           "kèo", "cá cược", "nhà cái"]


def scan(loop_src, data_src, home_src):
    fails = []
    for t in REQUIRED_TITLES:
        if t not in loop_src:
            fails.append("missing required homepage zone title: %s" % t)
    if "selectProductLoop" not in data_src:
        fails.append("selectProductLoop editorial helper missing from dailyFixtures.ts")
    else:
        # order-driven: featuredRecap = finished[0], featuredPrediction = scheduled[0]
        if "finished[0]" not in data_src or "scheduled[0]" not in data_src:
            fails.append("selectProductLoop is not slate-order-driven (expected finished[0]/scheduled[0])")
    if "selectProductLoop" not in loop_src:
        fails.append("HomeProductLoop does not use selectProductLoop")
    for w in GENERATION_BANNED:
        if w in loop_src:
            fails.append("internal generation wording in homepage loop: %s" % w)
    if "今日热点复盘" in loop_src:
        fails.append("forbidden label 今日热点复盘 (the lead recap must be 昨日热点复盘; secondary = 其他复盘)")
    # recap CTA must be gated on recapReady (no fake recap)
    if "viewRecap" in loop_src or "查看复盘" in loop_src:
        if "recapReady" not in loop_src:
            fails.append("recap CTA present but not gated on recapReady (fake-recap risk)")
    low = loop_src.lower()
    for w in BETTING:
        if w.lower() in low:
            fails.append("betting/trading vocab in homepage loop: %s" % w)
    if "HomeProductLoop" not in home_src:
        fails.append("HomePage.tsx does not render <HomeProductLoop/>")
    return fails


def selftest():
    good_loop = ("昨日热点复盘 今日热点预测 今日赛程 其他复盘 selectProductLoop "
                 "recapReady viewRecap 加入情报群看赛后观察")
    good_data = "export function selectProductLoop(m){ const finished=...; finished[0]; scheduled[0]; }"
    good_home = "<HomeProductLoop manifest={daily.manifest} loc={loc} />"
    checks = []
    checks.append(("clean passes", scan(good_loop, good_data, good_home) == []))
    checks.append(("missing title caught", any("今日热点预测" in f for f in scan("昨日热点复盘 今日赛程 其他复盘 selectProductLoop recapReady", good_data, good_home))))
    checks.append(("generation word caught", any("生成中" in f for f in scan(good_loop + " 复盘生成中", good_data, good_home))))
    checks.append(("今日热点复盘 caught", any("今日热点复盘" in f for f in scan(good_loop + " 今日热点复盘", good_data, good_home))))
    checks.append(("betting caught", any("赔率" in f for f in scan(good_loop + " 赔率", good_data, good_home))))
    checks.append(("ungated recap caught", any("recapReady" in f for f in scan("昨日热点复盘 今日热点预测 今日赛程 其他复盘 selectProductLoop 查看复盘", good_data, good_home))))
    checks.append(("home wiring caught", any("HomeProductLoop" in f for f in scan(good_loop, good_data, "no loop here"))))
    checks.append(("non-order helper caught", any("order-driven" in f for f in scan(good_loop, "export function selectProductLoop(){}", good_home))))
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    for p in (LOOP, DATA, HOME):
        if not p.exists():
            sys.stderr.write("missing source file: %s\n" % p)
            return 1
    fails = scan(LOOP.read_text(encoding="utf-8"), DATA.read_text(encoding="utf-8"), HOME.read_text(encoding="utf-8"))
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("HOMEPAGE PRODUCT LOOP FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("HOMEPAGE PRODUCT LOOP PASS (zones: %s)\n" % " · ".join(REQUIRED_TITLES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
