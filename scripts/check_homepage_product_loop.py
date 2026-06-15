#!/usr/bin/env python3
"""
MVP2-P2 Homepage Product Loop guard (Owner Harness-X brief 2026-06-14).

Asserts the homepage renders the football-intelligence CLOSED LOOP — yesterday's hotspot
recap → today's hotspot prediction → secondary schedule → other recaps → group CTA — and
NOT a generic status/recap/fixture list. Source-level (component) checks so it passes pre-deploy;
live DOM verification is done by scripts/check_customer_visible_copy.py + Owner visual review.

⚠️ VISUAL CONTRAST IS NOT PROVEN BY ANY SCANNER (P8a hotfix, Owner 2026-06-15). This guard and
check_customer_visible_copy.py both read TEXT ONLY — they cannot detect white-on-light / low-contrast
rendering (the P8a score-hook bug passed every scanner while being unreadable). The homepage
score-hook card (今日热点预测 · 俅哥主看 / 主比分 / 备选 / 冷门风险) MUST be screenshot-verified at
mobile scale on every visual change; a green scanner run is NECESSARY BUT NOT SUFFICIENT for sign-off.
Reference shot: docs/qa_screenshots/mvp2_p8a_contrast/.

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
  8. MVP2-P3: 今日热点预测 renders BEFORE 昨日热点复盘 (HotspotPrediction before HotspotRecap)
  9. MVP2-P3: lead prediction card has 进入战术室 (tactical-room CTA) + a copy/share entry (CopyLink)

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOOP = ROOT / "frontend" / "src" / "components" / "HomeProductLoop.tsx"
DATA = ROOT / "frontend" / "src" / "data" / "dailyFixtures.ts"
HOME = ROOT / "frontend" / "src" / "pages" / "HomePage.tsx"
MANIFEST = ROOT / "frontend" / "public" / "data" / "daily-fixtures.json"
PRED_ART_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
SELECTED = ROOT / "frontend" / "src" / "data" / "selectedHotspot.json"


def scan_selected(sel, m, art_keys):
    """P7 P0-1: selected_hotspot is the lead authority — it must be in the slate AND artifact-backed."""
    fails = []
    if not sel or sel.get("status") != "active" or not sel.get("fixture_key"):
        fails.append("selected_hotspot missing/inactive (P7 P0-1: homepage lead has no authority)")
        return fails
    key = sel["fixture_key"]
    fxs = m.get("fixtures", [])
    rows = [f for f in fxs if (f.get("id") or f.get("external_game_id")) == key]
    if not rows:
        fails.append("selected_hotspot %r is not in the runtime slate" % key)
    elif key not in art_keys:
        fails.append("selected_hotspot %r has no prediction artifact (lead would be hollow)" % key)
    return fails


def prediction_artifact_keys():
    """P6 P0-2: the fixture_keys/ids that resolve to a PREDICTION artifact (not an observation).
    The homepage lead prediction must be one of these."""
    import json
    keys = set()
    if PRED_ART_DIR.exists():
        for p in sorted(PRED_ART_DIR.glob("*.json")):
            try:
                a = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if "recap_ready" in a:  # observation artifact, not a prediction
                continue
            if a.get("fixture_key"):
                keys.add(a["fixture_key"])
            if a.get("id"):
                keys.add(str(a["id"]))
    return keys

# zone titles + MVP2-P2b modeling/analysis layer labels (all zh, source-level)
REQUIRED_TITLES = ["昨日热点复盘", "今日热点预测", "今日赛程", "其他复盘",
                   "赛后校准关注", "今日建模关注", "开球前 30 分钟"]
# current featured slate (manifest-level) — homepage OUTPUT must render these teams in these roles.
# Update when the operator changes the daily hotspot (slate order drives selection).
SCENARIO = {
    "featured_recap": ("Brazil", "Morocco"),
    "featured_prediction": ("Netherlands", "Japan"),
    "secondary_recap_team": "Mexico",
}
FINISHED_STATES = {"FINISHED", "RECAP_PENDING", "RECAP_READY", "ARCHIVED"}
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
        # P6 P0-2: featuredRecap = finished[0] (slate-first); featuredPrediction = the first
        # scheduled fixture that RESOLVES TO A PREDICTION ARTIFACT (hasPredictionArtifact), not
        # just scheduled[0]. A scheduled fixture with no artifact can never be the lead.
        if "finished[0]" not in data_src:
            fails.append("selectProductLoop featuredRecap is not slate-first (expected finished[0])")
        if "hasPredictionArtifact" not in data_src:
            fails.append("selectProductLoop lead prediction is not artifact-gated (P6 P0-2: hasPredictionArtifact)")
        # P7 P0-1: the lead is selected_hotspot-AUTHORITATIVE, not slate order.
        if "getSelectedHotspot" not in data_src:
            fails.append("selectProductLoop is not selected_hotspot-authoritative (P7 P0-1: getSelectedHotspot)")
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
    # 8. MVP2-P3 funnel order: hotspot PREDICTION renders before yesterday's RECAP.
    pi = loop_src.find("<HotspotPrediction")
    ri = loop_src.find("<HotspotRecap")
    if pi < 0:
        fails.append("HotspotPrediction is not rendered (今日热点预测 missing from the loop)")
    if ri < 0:
        fails.append("HotspotRecap is not rendered (昨日热点复盘 missing from the loop)")
    if pi >= 0 and ri >= 0 and pi > ri:
        fails.append("今日热点预测 must render BEFORE 昨日热点复盘 (HotspotPrediction before HotspotRecap)")
    # 9. MVP2-P3 lead prediction card: tactical-room CTA + copy/share entry.
    if "进入战术室" not in loop_src:
        fails.append("lead prediction card missing 进入战术室 (tactical-room CTA)")
    if "CopyLink" not in loop_src:
        fails.append("homepage loop missing a copy/share entry (CopyLink)")
    # 10. P6 P0-1: the lead prediction card exposes a COMPACT score-call hook (主比分 teaser
    #     projected via buildStrongCall) + the live-group CTA — not a generic question frame.
    if "buildStrongCall" not in loop_src:
        fails.append("lead prediction card not wired to the canonical strong-call projection (buildStrongCall)")
    if "主比分" not in loop_src:
        fails.append("lead prediction card missing 主比分 score-call teaser (P6 P0-1 hook)")
    if "加入临场情报群" not in loop_src:
        fails.append("lead prediction card missing 加入临场情报群 (live-group CTA)")
    return fails


def scan_manifest(m, art_keys=None):
    """Validate the homepage OUTPUT teams: featured recap = first finished fixture, featured
    prediction = first scheduled fixture THAT RESOLVES TO A PREDICTION ARTIFACT (P6 P0-2), and the
    secondary recap team is NOT the lead."""
    fails = []
    if art_keys is None:
        art_keys = prediction_artifact_keys()
    fx = m.get("fixtures", [])
    finished = [f for f in fx if f.get("lifecycle_state") in FINISHED_STATES]
    scheduled = [f for f in fx if f.get("lifecycle_state") not in FINISHED_STATES
                 and (f.get("preMatchAllowed") if f.get("preMatchAllowed") is not None
                      else f.get("lifecycle_state") == "SCHEDULED")]

    def lead_key(f):
        return f.get("id") or f.get("external_game_id")

    rec = finished[0] if finished else None
    # P6 P0-2: the lead prediction is the first scheduled fixture backed by a prediction artifact.
    pred = next((f for f in scheduled if lead_key(f) in art_keys), None)
    rh, ra = SCENARIO["featured_recap"]
    if not rec or rec.get("home") != rh or rec.get("away") != ra:
        fails.append("featured recap (first finished) must be %s vs %s, got %s" % (
            rh, ra, (rec.get("home"), rec.get("away")) if rec else None))
    ph, pa = SCENARIO["featured_prediction"]
    if not pred or pred.get("home") != ph or pred.get("away") != pa:
        fails.append("featured prediction (first artifact-backed scheduled) must be %s vs %s, got %s" % (
            ph, pa, (pred.get("home"), pred.get("away")) if pred else None))
    elif lead_key(pred) not in art_keys:
        fails.append("featured prediction %s vs %s has no prediction artifact (P6 P0-2)" % (ph, pa))
    # no fake recap: a featured recap with recapReady=false must not be a recap-ready lead
    if rec and not rec.get("recapReady") and rec.get("lifecycle_state") == "RECAP_PENDING":
        pass  # correct: 赛后校准中, handled by the component (no 查看复盘)
    # secondary recap team must be present but NOT the lead (i.e. not finished[0])
    sec = SCENARIO["secondary_recap_team"]
    if rec and rec.get("home") == sec:
        fails.append("%s must be a SECONDARY recap, not the hotspot recap lead" % sec)
    if not any(f.get("home") == sec for f in finished[1:]):
        fails.append("%s must appear as a secondary/other recap" % sec)
    return fails


def selftest():
    good_loop = ("昨日热点复盘 今日热点预测 今日赛程 其他复盘 赛后校准关注 今日建模关注 开球前 30 分钟 "
                 "selectProductLoop recapReady viewRecap 加入情报群看赛后观察 "
                 "<HotspotPrediction f={featuredPrediction}/> <HotspotRecap f={featuredRecap}/> "
                 "进入战术室 CopyLink buildStrongCall 主比分 加入临场情报群")
    TEST_ART = {"manual:Nether-Japan-20260614"}
    good_manifest = {"fixtures": [
        {"home": "Brazil", "away": "Morocco", "lifecycle_state": "RECAP_PENDING", "recapReady": False},
        {"home": "Mexico", "away": "South Africa", "lifecycle_state": "RECAP_READY", "recapReady": True},
        {"home": "Netherlands", "away": "Japan", "lifecycle_state": "SCHEDULED", "preMatchAllowed": True,
         "external_game_id": "manual:Nether-Japan-20260614"},
    ]}
    good_data = ("export function selectProductLoop(m){ const sel=getSelectedHotspot(); const finished=...; "
                 "finished[0]; scheduled.find(f=>hasPredictionArtifact(leadKey(f))); }")
    good_home = "<HomeProductLoop manifest={daily.manifest} loc={loc} />"
    good_sel = {"status": "active", "fixture_key": "manual:Nether-Japan-20260614"}
    checks = []
    checks.append(("clean passes", scan(good_loop, good_data, good_home) == []))
    checks.append(("missing title caught", any("今日热点预测" in f for f in scan("昨日热点复盘 今日赛程 其他复盘 selectProductLoop recapReady", good_data, good_home))))
    checks.append(("generation word caught", any("生成中" in f for f in scan(good_loop + " 复盘生成中", good_data, good_home))))
    checks.append(("今日热点复盘 caught", any("今日热点复盘" in f for f in scan(good_loop + " 今日热点复盘", good_data, good_home))))
    checks.append(("betting caught", any("赔率" in f for f in scan(good_loop + " 赔率", good_data, good_home))))
    checks.append(("ungated recap caught", any("recapReady" in f for f in scan("昨日热点复盘 今日热点预测 今日赛程 其他复盘 selectProductLoop 查看复盘", good_data, good_home))))
    checks.append(("home wiring caught", any("HomeProductLoop" in f for f in scan(good_loop, good_data, "no loop here"))))
    bad_order = ("昨日热点复盘 今日热点预测 今日赛程 其他复盘 赛后校准关注 今日建模关注 开球前 30 分钟 "
                 "selectProductLoop recapReady viewRecap "
                 "<HotspotRecap f={featuredRecap}/> <HotspotPrediction f={featuredPrediction}/> 进入战术室 CopyLink")
    checks.append(("recap-before-prediction order caught", any("render BEFORE" in f for f in scan(bad_order, good_data, good_home))))
    checks.append(("missing 进入战术室 caught", any("进入战术室" in f for f in scan(good_loop.replace("进入战术室", ""), good_data, good_home))))
    checks.append(("missing CopyLink caught", any("CopyLink" in f for f in scan(good_loop.replace("CopyLink", ""), good_data, good_home))))
    checks.append(("missing 主比分 hook caught", any("主比分" in f for f in scan(good_loop.replace("主比分", ""), good_data, good_home))))
    checks.append(("artifact-gating missing caught", any("artifact-gated" in f for f in scan(good_loop, "export function selectProductLoop(){ finished[0]; }", good_home))))
    checks.append(("selected-hotspot wiring missing caught", any("selected_hotspot-authoritative" in f for f in scan(good_loop, "export function selectProductLoop(){ finished[0]; scheduled.find(f=>hasPredictionArtifact(leadKey(f))); }", good_home))))
    checks.append(("manifest scenario passes", scan_manifest(good_manifest, TEST_ART) == []))
    checks.append(("selected_hotspot scenario passes", scan_selected(good_sel, good_manifest, TEST_ART) == []))
    checks.append(("missing selected_hotspot caught", any("no authority" in f for f in scan_selected(None, good_manifest, TEST_ART))))
    checks.append(("selected-not-artifact caught", any("hollow" in f for f in scan_selected(good_sel, good_manifest, set()))))
    checks.append(("non-artifact lead caught", any("featured prediction" in f for f in scan_manifest(good_manifest, set()))))
    checks.append(("wrong recap lead caught", any("featured recap" in f for f in scan_manifest(
        {"fixtures": [{"home": "Mexico", "away": "South Africa", "lifecycle_state": "RECAP_READY", "recapReady": True},
                      {"home": "Brazil", "away": "Morocco", "lifecycle_state": "RECAP_PENDING", "recapReady": False},
                      {"home": "Netherlands", "away": "Japan", "lifecycle_state": "SCHEDULED", "preMatchAllowed": True,
                       "external_game_id": "manual:Nether-Japan-20260614"}]}, TEST_ART))))
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
    if MANIFEST.exists():
        import json
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        fails += scan_manifest(manifest)
        # P7 P0-1: selected_hotspot must be the artifact-backed lead authority.
        sel = json.loads(SELECTED.read_text(encoding="utf-8")) if SELECTED.exists() else None
        fails += scan_selected(sel, manifest, prediction_artifact_keys())
    else:
        fails.append("runtime manifest %s missing (cannot validate homepage output teams)" % MANIFEST.name)
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("HOMEPAGE PRODUCT LOOP FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("HOMEPAGE PRODUCT LOOP PASS (zones: %s)\n" % " · ".join(REQUIRED_TITLES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
