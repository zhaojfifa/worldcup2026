#!/usr/bin/env python3
"""
MVP2-P5 Prediction Artifact + StrongCopy guard (Owner: artifact → canonical strong-call → strong UI).

Asserts the daily hotspot resolves to STRONG artifact-level content (not a weak shell), and the
recap to a STRONG observation receipt, with the share/operation layer wired and compliant.

Predict route surface (ArtifactTacticalRoom.tsx + ShareBlock.tsx + prediction artifact JSON) must
carry:  俅哥强判断 · 主比分 or 比分待开球前 30 分钟确认 · 冷门风险 or 风险变量 · 最大变量 or 关键变量 ·
        为什么 · 外部预期 or 公开预测倾向 · T-30 or 开球前 30 分钟 · 复制情报链 · 复制分享文案 · 加入临场情报群
Recap observation surface (ObservationReceipt.tsx + ShareBlock.tsx + observation artifact JSON):
        昨日主推回执 · 实际比分 · 部分命中 or 校准 · 赛后校准关注 · 完整复盘确认后开放 ·
        复制观察链接 or 复制分享 · 加入情报群

Plus: artifacts wired into the canonical projection (buildStrongCallFromArtifact) and share layer;
numerics may be null (pending labels) — never invented; no betting/generation/de-model/fake-prob
vocab in rendered content; vi/my slices Han=0; external_expectation uses ONLY safe vocabulary.

Exit 0 = clean. --selftest runs embedded fixtures.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRED_ART_DIR = ROOT / "frontend" / "src" / "data" / "predictionArtifacts"
PRED = PRED_ART_DIR / "manual_Nether-Japan-20260614.json"   # selftest regression anchor
OBS = PRED_ART_DIR / "observation_1489371.json"             # selftest regression anchor
ROOM = ROOT / "frontend" / "src" / "components" / "ArtifactTacticalRoom.tsx"
RECEIPT = ROOT / "frontend" / "src" / "components" / "ObservationReceipt.tsx"
SHAREBLOCK = ROOT / "frontend" / "src" / "components" / "ShareBlock.tsx"
PROJ = ROOT / "frontend" / "src" / "growth" / "strongCallProjection.ts"
SHARETPL = ROOT / "frontend" / "src" / "growth" / "shareTemplates.ts"
PREDICT_PAGE = ROOT / "frontend" / "src" / "pages" / "PredictPage.tsx"
RECAP_PAGE = ROOT / "frontend" / "src" / "pages" / "RecapDetailPage.tsx"

CUST_LANGS = ["zh", "vi", "my", "en"]
HAN = re.compile(r"[一-鿿]")

BETTING = ["赔率", "盘口", "下注", "投注", "博彩", "竞猜", "让球", "大小球", "跟单", "串关", "返佣", "佣金",
           "odds", "handicap", "bookmaker", "wager", "betting",
           "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược",
           "လောင်းကစား", "လောင်းကြေး", "အလောင်းအစား", "လောင်းထား"]
GENERATION = ["复盘生成中", "待生成复盘", "生成中", "自动生成", "AI 正在生成",
              "đang tạo phục dựng", "đang dựng phục dựng", "ပြင်ဆင်နေသည်", "ထုတ်နေဆဲ"]
DEMODEL = {"zh": ["模型", "盲区", "数据缺失", "缺数据", "过程验证", "自证"],
           "vi": ["mô hình", "thiếu dữ liệu"],
           "my": ["မော်ဒယ်", "ဒေတာမရှိ"]}
FAKE_PROB = ["命中率", "胜率", "win rate", "tỷ lệ thắng"]
# external_expectation must speak in the Owner-approved safe vocabulary
SAFE_EXT = ["外部预期", "公开预测倾向", "市场共识", "热度集中", "冷门变量", "临场变量", "赛前参考",
            "Xu hướng công khai", "Độ nóng", "Biến số", "Kỳ vọng",
            "လူထုထင်မြင်ချက်", "အပူချိန်", "variable",
            "Public tendency", "Heat focus", "Upset variable", "External"]


def _strings(node):
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
        if lang in ("vi", "my") and HAN.search(blob):
            fails.append("%s[%s]: contains Han characters (vi/my must be Han=0)" % (label, lang))
    return fails


def scan_prediction(a):
    # P6 P0-7: generalized — validates ANY prediction artifact (not two hardcoded files). Identity
    # is presence-checked, not equality-pinned; the product-contract tokens below are required of
    # every prediction artifact so a new daily hotspot is held to the same bar.
    fails = []
    if not a.get("fixture_key"):
        fails.append("prediction artifact missing fixture_key")
    if not a.get("home") or not a.get("away"):
        fails.append("prediction artifact missing home/away (%s vs %s)" % (a.get("home"), a.get("away")))
    if not a.get("safety", {}).get("no_auto_send"):
        fails.append("prediction artifact safety.no_auto_send must be true")
    i18n = a.get("i18n", {})
    for lang in CUST_LANGS:
        s = i18n.get(lang)
        if not s:
            fails.append("prediction artifact missing locale %s" % lang)
            continue
        for k in ("pending_direction", "pending_score"):
            if not s.get(k):
                fails.append("prediction[%s] missing %s" % (lang, k))
        pred = s.get("prediction", {})
        for k in ("primary_direction", "score_call", "backup_score", "confidence"):
            if k not in pred:
                fails.append("prediction[%s].prediction missing key %s" % (lang, k))
            elif pred[k] is not None and not isinstance(pred[k], str):
                fails.append("prediction[%s].prediction.%s must be null or string" % (lang, k))
        for k in ("top_variable", "why"):  # MVP2-P5 strong fields
            if not pred.get(k):
                fails.append("prediction[%s].prediction.%s missing (strong field)" % (lang, k))
        an = s.get("analysis", {})
        for k in ("modeling_focus", "tactical_matchup", "risk_variables",
                  "external_expectation", "thirty_minute_checklist"):
            if not isinstance(an.get(k), list) or not an.get(k):
                fails.append("prediction[%s].analysis.%s must be a non-empty list" % (lang, k))
        # external_expectation must speak safe vocabulary
        for line in an.get("external_expectation", []):
            if not any(t.lower() in line.lower() for t in SAFE_EXT):
                fails.append("prediction[%s] external_expectation not in safe vocab: %r" % (lang, line))
        ops = s.get("operations", {})
        for k in ("share_title", "share_copy", "join_cta"):
            if not ops.get(k):
                fails.append("prediction[%s].operations.%s missing" % (lang, k))
    # Owner-required visible tokens (zh)
    zh = i18n.get("zh", {})
    if "比分待开球前 30 分钟确认" not in (zh.get("pending_score") or ""):
        fails.append("prediction zh pending_score must contain 比分待开球前 30 分钟确认")
    if "方向待临场确认" not in (zh.get("pending_direction") or ""):
        fails.append("prediction zh pending_direction must contain 方向待临场确认")
    if "加入临场情报群" not in (zh.get("operations", {}).get("join_cta") or ""):
        fails.append("prediction zh join_cta must be 加入临场情报群")
    # MVP2-P5b: the main expression must be a CONFIRMED strong call, not the weak pending default.
    zp = zh.get("prediction", {})
    if not zp.get("primary_direction"):
        fails.append("prediction zh primary_direction must be a confirmed direction (Owner P5b: no weak default)")
    if not zp.get("score_call"):
        fails.append("prediction zh score_call must be a confirmed main score (Owner P5b: no weak default)")
    if not zp.get("backup_score"):
        fails.append("prediction zh backup_score must be a confirmed backup (Owner P5b)")
    fails += scan_content_words(i18n, "prediction")
    return fails


def scan_observation(a):
    # P6 P0-7: generalized — validates ANY observation artifact. Identity is presence-checked;
    # recap_ready must stay false (an observation receipt is the pre-recap tier — no fake recap).
    fails = []
    if not a.get("id"):
        fails.append("observation artifact missing id")
    if not a.get("home") or not a.get("away"):
        fails.append("observation artifact missing home/away (%s vs %s)" % (a.get("home"), a.get("away")))
    if not a.get("score"):
        fails.append("observation artifact missing score")
    if a.get("recap_ready") is not False:
        fails.append("observation artifact recap_ready must be false (no fake recap)")
    i18n = a.get("i18n", {})
    for lang in CUST_LANGS:
        s = i18n.get(lang)
        if not s:
            fails.append("observation artifact missing locale %s" % lang)
            continue
        for k in ("receipt_title", "pre_match_call", "actual_line", "assessment",
                  "calibration_title", "pending_line", "state_line", "deviation",
                  "next_impact", "join_cta", "share_copy"):
            if not s.get(k):
                fails.append("observation[%s] missing %s" % (lang, k))
        if not isinstance(s.get("calibration_points"), list) or not s.get("calibration_points"):
            fails.append("observation[%s].calibration_points must be a non-empty list" % lang)
    zh = i18n.get("zh", {})
    checks = [
        ("昨日主推回执", zh.get("receipt_title")),
        ("实际比分", zh.get("actual_line")),
        ("赛后校准关注", zh.get("calibration_title")),
        ("完整复盘确认后开放", zh.get("pending_line")),
        ("加入情报群", zh.get("join_cta")),
    ]
    for token, val in checks:
        if token not in (val or ""):
            fails.append("observation zh must contain %s" % token)
    if "部分命中" not in (zh.get("assessment") or "") and "校准" not in (zh.get("assessment") or ""):
        fails.append("observation zh assessment must contain 部分命中 or 校准")
    if "偏差" not in (zh.get("deviation") or "") and "低于" not in (zh.get("deviation") or ""):
        fails.append("observation zh deviation must explain the deviation (偏差原因)")
    fails += scan_content_words(i18n, "observation")
    return fails


def scan_sources(srcs):
    """srcs: dict of name->text for ROOM/RECEIPT/SHAREBLOCK/PROJ/SHARETPL/PREDICT/RECAP."""
    fails = []
    room, receipt, share, proj, tpl, predict, recap = (
        srcs["room"], srcs["receipt"], srcs["share"], srcs["proj"], srcs["tpl"],
        srcs["predict"], srcs["recap"])
    room_required = ["俅哥强判断", "主比分", "冷门风险", "风险变量", "最大变量", "为什么",
                     "外部预期", "T-30", "今日热点预测", "今日建模关注", "战术对位"]
    for t in room_required:
        if t not in room:
            fails.append("ArtifactTacticalRoom missing strong label: %s" % t)
    if "ShareBlock" not in room:
        fails.append("ArtifactTacticalRoom must use ShareBlock (copy link/text/card + join)")
    for t in ("复制情报链", "复制分享文案"):
        if t not in share:
            fails.append("ShareBlock missing share label: %s" % t)
    if "buildStrongCallFromArtifact" not in proj:
        fails.append("strongCallProjection missing buildStrongCallFromArtifact (artifact source)")
    if "getPredictionArtifact" not in proj:
        fails.append("buildStrongCall not wired to the prediction artifact fallback")
    if "getObservationArtifact" not in tpl:
        fails.append("shareTemplates recapShareCopy not artifact-aware (getObservationArtifact)")
    if "下一场影响" not in receipt:
        fails.append("ObservationReceipt missing 下一场影响 (next-match impact)")
    if "deviation" not in receipt:
        fails.append("ObservationReceipt missing the deviation (偏差原因) render")
    if "ShareBlock" not in receipt:
        fails.append("ObservationReceipt must use ShareBlock (copy/share + join)")
    if "getPredictionArtifact" not in predict or "ArtifactTacticalRoom" not in predict:
        fails.append("PredictPage not wired to the prediction artifact tier")
    if "getObservationArtifact" not in recap or "ObservationReceipt" not in recap:
        fails.append("RecapDetailPage not wired to the observation artifact tier")
    return fails


def _read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def selftest():
    pred = json.loads(_read(PRED) or "{}")
    obs = json.loads(_read(OBS) or "{}")
    checks = []
    checks.append(("real prediction artifact clean", scan_prediction(pred) == []))
    checks.append(("real observation artifact clean", scan_observation(obs) == []))
    checks.append(("betting word caught", any("betting" in f for f in scan_content_words({"zh": {"x": "今天 赔率"}}, "t"))))
    checks.append(("unsafe ext caught", any("safe vocab" in f for f in scan_prediction({
        "fixture_key": "manual:Nether-Japan-20260614", "home": "Netherlands", "away": "Japan",
        "safety": {"no_auto_send": True},
        "i18n": {l: {"pending_direction": "方向待临场确认", "pending_score": "比分待开球前 30 分钟确认",
                     "prediction": {"primary_direction": None, "score_call": None, "backup_score": None,
                                    "confidence": None, "top_variable": "x", "why": "y"},
                     "analysis": {"modeling_focus": ["a"], "tactical_matchup": ["a"], "risk_variables": ["a"],
                                  "external_expectation": ["随便一句没有安全词"], "thirty_minute_checklist": ["a"]},
                     "operations": {"share_title": "t", "share_copy": "c", "join_cta": "加入临场情报群"}}
               for l in CUST_LANGS}}))))
    checks.append(("fake recap caught", any("recap_ready" in f for f in scan_observation(
        {"id": "1489371", "home": "Brazil", "away": "Morocco", "score": "1-1", "recap_ready": True, "i18n": {}}))))
    good = {"room": " ".join(["俅哥强判断", "主比分", "冷门风险", "风险变量", "最大变量", "为什么",
                              "外部预期", "T-30", "今日热点预测", "今日建模关注", "战术对位", "ShareBlock"]),
            "receipt": "下一场影响 deviation ShareBlock", "share": "复制情报链 复制分享文案",
            "proj": "buildStrongCallFromArtifact getPredictionArtifact", "tpl": "getObservationArtifact",
            "predict": "getPredictionArtifact ArtifactTacticalRoom", "recap": "getObservationArtifact ObservationReceipt"}
    checks.append(("good sources clean", scan_sources(good) == []))
    bad = dict(good, room=good["room"].replace("战术对位", ""))
    checks.append(("missing room label caught", any("战术对位" in f for f in scan_sources(bad))))
    bad2 = dict(good, share="复制情报链")
    checks.append(("missing share label caught", any("复制分享文案" in f for f in scan_sources(bad2))))
    ok = all(v for _, v in checks)
    for n, v in checks:
        sys.stdout.write("%s %s\n" % ("PASS" if v else "FAIL", n))
    sys.stdout.write("%d/%d checks pass\n" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def classify(a):
    """Observation artifacts carry recap_ready; prediction artifacts carry prediction_confirmed /
    an i18n[*].prediction block. Used to pick the right scanner per file (P6 P0-7 generalization)."""
    return "observation" if "recap_ready" in a else "prediction"


def main():
    if "--selftest" in sys.argv:
        return selftest()
    for p in (ROOM, RECEIPT, SHAREBLOCK, PROJ, SHARETPL, PREDICT_PAGE, RECAP_PAGE):
        if not p.exists():
            sys.stderr.write("missing file: %s\n" % p)
            return 1
    # P6 P0-7: validate EVERY artifact in the directory, not two hardcoded files.
    artifacts = sorted(PRED_ART_DIR.glob("*.json"))
    if not artifacts:
        sys.stderr.write("no prediction/observation artifacts found in %s\n" % PRED_ART_DIR)
        return 1
    fails = []
    n_pred = n_obs = 0
    for p in artifacts:
        rel = str(p.relative_to(ROOT))
        try:
            a = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            fails.append("%s: invalid JSON (%s)" % (rel, e))
            continue
        kind = classify(a)
        these = scan_observation(a) if kind == "observation" else scan_prediction(a)
        if kind == "observation":
            n_obs += 1
        else:
            n_pred += 1
        fails += ["%s: %s" % (rel, e) for e in these]
    fails += scan_sources({
        "room": _read(ROOM), "receipt": _read(RECEIPT), "share": _read(SHAREBLOCK),
        "proj": _read(PROJ), "tpl": _read(SHARETPL), "predict": _read(PREDICT_PAGE), "recap": _read(RECAP_PAGE)})
    for f in artifacts:
        sys.stdout.write("scanned  %s\n" % f.relative_to(ROOT))
    for f in fails:
        sys.stdout.write("FAIL  %s\n" % f)
    if fails:
        sys.stdout.write("PREDICTION ARTIFACT FAIL — %d issue(s)\n" % len(fails))
        return 1
    sys.stdout.write("PREDICTION ARTIFACT PASS (%d prediction + %d observation artifact(s); strong call + receipt wired; safe vocab)\n"
                     % (n_pred, n_obs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
