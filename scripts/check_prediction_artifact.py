#!/usr/bin/env python3
"""
MVP2-P4 Prediction Artifact guard (Owner: restore the prediction/recap artifact chain).

Asserts the daily hotspot resolves to ARTIFACT-LEVEL content, not only a generic fallback:

  1. The prediction artifact (Netherlands vs Japan) exists with fixture identity, a per-locale
     pre-match read (prediction block + modeling_focus + tactical_matchup + risk_variables +
     30-minute checklist) + operator share/join copy. Numeric direction/score/confidence may be
     null (shown as 方向待临场确认) — null is allowed, but the analysis frames must be non-empty.
  2. The observation artifact (Brazil 1-1 Morocco) exists with the pre-match receipt, actual
     score 1-1, calibration focus, pending-recap line, recap_ready=false (no fake recap).
  3. The tactical-room + observation components render the required zh section labels.
  4. /predict + /recap pages are wired to the artifact loader.
  5. No betting/trading vocabulary, no internal generation wording, no de-model/process words,
     no fake-probability claims anywhere in the RENDERED artifact content; vi/my slices Han=0.

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRED = ROOT / "frontend" / "src" / "data" / "predictionArtifacts" / "manual_Nether-Japan-20260614.json"
OBS = ROOT / "frontend" / "src" / "data" / "predictionArtifacts" / "observation_1489371.json"
ROOM = ROOT / "frontend" / "src" / "components" / "ArtifactTacticalRoom.tsx"
RECEIPT = ROOT / "frontend" / "src" / "components" / "ObservationReceipt.tsx"
PREDICT_PAGE = ROOT / "frontend" / "src" / "pages" / "PredictPage.tsx"
RECAP_PAGE = ROOT / "frontend" / "src" / "pages" / "RecapDetailPage.tsx"

CUST_LANGS = ["zh", "vi", "my", "en"]
HAN = re.compile(r"[一-鿿]")

# forbidden across RENDERED artifact content (meta fields note/source/safety are NOT rendered)
BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "让球", "大小球", "跟单", "返佣", "佣金",
           "odds", "handicap", "bookmaker", "wager", "payout", "commission",
           "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược",
           "လောင်းကစား", "လောင်းကြေး", "အလောင်းအစား", "လောင်းထား"]
GENERATION = ["复盘生成中", "待生成复盘", "生成中", "自动生成", "AI 正在生成",
              "đang tạo phục dựng", "đang dựng phục dựng", "ပြင်ဆင်နေသည်", "ထုတ်နေဆဲ"]
DEMODEL = {"zh": ["模型", "盲区", "数据缺失", "缺数据", "过程验证", "自证"],
           "vi": ["mô hình", "thiếu dữ liệu"],
           "my": ["မော်ဒယ်", "ဒေတာမရှိ"]}
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]
ROOM_LABELS = ["今日热点预测", "建模关注", "战术对位", "风险变量", "开球前 30 分钟", "复制/分享"]


def _strings(node):
    """All string leaves under a node (recursive)."""
    out = []
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, list):
        for v in node:
            out.extend(_strings(v))
    elif isinstance(node, dict):
        for v in node.values():
            out.extend(_strings(v))
    return out


def scan_content_words(i18n, label):
    """Forbidden-word scan over the RENDERED i18n slices only."""
    fails = []
    for lang, slice_ in i18n.items():
        blob = " ".join(_strings(slice_))
        low = blob.lower()
        for w in BETTING:
            if (w.lower() in low) if w.isascii() else (w in blob):
                fails.append("%s[%s]: betting vocab %r" % (label, lang, w))
        for w in GENERATION:
            if w in blob:
                fails.append("%s[%s]: internal generation wording %r" % (label, lang, w))
        for w in FAKE_PROB:
            if (w.lower() in low) if w.isascii() else (w in blob):
                fails.append("%s[%s]: fake-probability claim %r" % (label, lang, w))
        for w in DEMODEL.get(lang, []):
            if (w.lower() in low) if w.isascii() else (w in blob):
                fails.append("%s[%s]: de-model/process word %r" % (label, lang, w))
        # vi/my customer slices must be Han-free
        if lang in ("vi", "my") and HAN.search(blob):
            fails.append("%s[%s]: contains Han characters (vi/my must be Han=0)" % (label, lang))
    return fails


def scan_prediction(a):
    fails = []
    if a.get("fixture_key") != "manual:Nether-Japan-20260614":
        fails.append("prediction artifact fixture_key wrong: %r" % a.get("fixture_key"))
    if a.get("home") != "Netherlands" or a.get("away") != "Japan":
        fails.append("prediction artifact teams wrong: %s vs %s" % (a.get("home"), a.get("away")))
    safety = a.get("safety", {})
    if not safety.get("no_auto_send"):
        fails.append("prediction artifact safety.no_auto_send must be true")
    i18n = a.get("i18n", {})
    for lang in CUST_LANGS:
        s = i18n.get(lang)
        if not s:
            fails.append("prediction artifact missing locale %s" % lang)
            continue
        if not s.get("pending_label"):
            fails.append("prediction[%s] missing pending_label" % lang)
        pred = s.get("prediction", {})
        for k in ("primary_direction", "score_call", "backup_score", "confidence"):
            if k not in pred:
                fails.append("prediction[%s].prediction missing key %s" % (lang, k))
            elif pred[k] is not None and not isinstance(pred[k], str):
                fails.append("prediction[%s].prediction.%s must be null or string" % (lang, k))
        an = s.get("analysis", {})
        for k in ("modeling_focus", "tactical_matchup", "risk_variables", "thirty_minute_checklist"):
            if not isinstance(an.get(k), list) or not an.get(k):
                fails.append("prediction[%s].analysis.%s must be a non-empty list" % (lang, k))
        ops = s.get("operations", {})
        for k in ("share_title", "share_copy", "join_cta"):
            if not ops.get(k):
                fails.append("prediction[%s].operations.%s missing" % (lang, k))
    fails += scan_content_words(i18n, "prediction")
    return fails


def scan_observation(a):
    fails = []
    if a.get("id") != "1489371":
        fails.append("observation artifact id wrong: %r" % a.get("id"))
    if a.get("home") != "Brazil" or a.get("away") != "Morocco":
        fails.append("observation artifact teams wrong: %s vs %s" % (a.get("home"), a.get("away")))
    if a.get("score") != "1-1":
        fails.append("observation artifact score must be 1-1, got %r" % a.get("score"))
    if a.get("recap_ready") is not False:
        fails.append("observation artifact recap_ready must be false (no fake recap)")
    i18n = a.get("i18n", {})
    for lang in CUST_LANGS:
        s = i18n.get(lang)
        if not s:
            fails.append("observation artifact missing locale %s" % lang)
            continue
        for k in ("receipt_title", "pre_match_call", "actual_line", "assessment",
                  "calibration_title", "pending_line", "state_line", "join_cta"):
            if not s.get(k):
                fails.append("observation[%s] missing %s" % (lang, k))
        if not isinstance(s.get("calibration_points"), list) or not s.get("calibration_points"):
            fails.append("observation[%s].calibration_points must be a non-empty list" % lang)
    # the zh receipt must carry the Owner-required visible tokens
    zh = i18n.get("zh", {})
    if "昨日主推回执" not in (zh.get("receipt_title") or ""):
        fails.append("observation zh receipt_title must contain 昨日主推回执")
    if "赛后校准" not in (zh.get("calibration_title") or "") + (zh.get("state_line") or ""):
        fails.append("observation zh must contain 赛后校准")
    if "完整复盘确认后开放" not in (zh.get("pending_line") or ""):
        fails.append("observation zh pending_line must contain 完整复盘确认后开放")
    if "加入情报群" not in (zh.get("join_cta") or ""):
        fails.append("observation zh join_cta must contain 加入情报群")
    fails += scan_content_words(i18n, "observation")
    return fails


def scan_sources(room_src, receipt_src, predict_src, recap_src):
    fails = []
    for lbl in ROOM_LABELS:
        if lbl not in room_src:
            fails.append("ArtifactTacticalRoom missing required label: %s" % lbl)
    if "DetailShareRow" not in room_src:
        fails.append("ArtifactTacticalRoom missing DetailShareRow (copy/share + join)")
    if "复制/分享" not in receipt_src:
        fails.append("ObservationReceipt missing 复制/分享 label")
    if "CopyLink" not in receipt_src:
        fails.append("ObservationReceipt missing CopyLink (copy/share)")
    if "recordJoinIntent" not in receipt_src or "join_cta" not in receipt_src:
        fails.append("ObservationReceipt missing the artifact join CTA")
    if "getPredictionArtifact" not in predict_src or "ArtifactTacticalRoom" not in predict_src:
        fails.append("PredictPage not wired to the prediction artifact tier")
    if "getObservationArtifact" not in recap_src or "ObservationReceipt" not in recap_src:
        fails.append("RecapDetailPage not wired to the observation artifact tier")
    return fails


def selftest():
    good_pred = json.loads(PRED.read_text(encoding="utf-8")) if PRED.exists() else {}
    good_obs = json.loads(OBS.read_text(encoding="utf-8")) if OBS.exists() else {}
    checks = []
    checks.append(("real prediction artifact clean", scan_prediction(good_pred) == []))
    checks.append(("real observation artifact clean", scan_observation(good_obs) == []))
    checks.append(("betting word caught", any("betting" in f for f in scan_content_words(
        {"zh": {"x": "今天看 赔率"}}, "t"))))
    checks.append(("generation word caught", any("generation" in f for f in scan_content_words(
        {"zh": {"x": "复盘生成中"}}, "t"))))
    checks.append(("vi han caught", any("Han" in f for f in scan_content_words(
        {"vi": {"x": "có 中文"}}, "t"))))
    checks.append(("fake recap caught", any("recap_ready" in f for f in scan_observation(
        {"id": "1489371", "home": "Brazil", "away": "Morocco", "score": "1-1", "recap_ready": True,
         "i18n": {}}))))
    checks.append(("missing room label caught", any("战术对位" in f for f in scan_sources(
        "今日热点预测 建模关注 风险变量 开球前 30 分钟 复制/分享 DetailShareRow", "复制/分享 CopyLink recordJoinIntent join_cta",
        "getPredictionArtifact ArtifactTacticalRoom", "getObservationArtifact ObservationReceipt"))))
    checks.append(("unwired predict caught", any("PredictPage not wired" in f for f in scan_sources(
        " ".join(ROOM_LABELS) + " DetailShareRow", "复制/分享 CopyLink recordJoinIntent join_cta",
        "nothing", "getObservationArtifact ObservationReceipt"))))
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fails = []
    for p in (PRED, OBS, ROOM, RECEIPT, PREDICT_PAGE, RECAP_PAGE):
        if not p.exists():
            sys.stderr.write("missing file: %s\n" % p)
            return 1
    fails += scan_prediction(json.loads(PRED.read_text(encoding="utf-8")))
    fails += scan_observation(json.loads(OBS.read_text(encoding="utf-8")))
    fails += scan_sources(ROOM.read_text(encoding="utf-8"), RECEIPT.read_text(encoding="utf-8"),
                          PREDICT_PAGE.read_text(encoding="utf-8"), RECAP_PAGE.read_text(encoding="utf-8"))
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("PREDICTION ARTIFACT FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("PREDICTION ARTIFACT PASS (predict + observation artifacts wired, no banned vocab)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
