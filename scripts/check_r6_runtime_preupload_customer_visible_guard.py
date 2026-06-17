#!/usr/bin/env python3
"""R6.1 — PRE-UPLOAD customer-visible guard for the runtime content package.

The runtime content cutover MUST run this BEFORE POST /api/v1/admin/runtime-content/upload. It scans
every customer-visible TEXT field of the package (prediction + observation i18n copy, share copy,
selectedHotspot labels) for engineering/de-model wording, betting vocabulary, and fabricated
probability/confidence; and it structurally rejects any non-null numeric win_prob/confidence. If any
violation is found the package must NOT be uploaded (production stays on the previous runtime package).

scan_package(pkg) -> list of (field_path, reason) violations (empty = clean). Pure, no I/O.
Usage: --selftest
"""
import json, pathlib, re, sys

# Banned in CUSTOMER-VISIBLE copy (Owner R6.1 list + existing de-model/betting bans). These expose
# engineering/source weakness or gambling framing and must never be product copy.
BANNED = [
    # zh de-model / process (Owner R6.1 list + existing de-model bans). NOTE: bare 概率 (generic
    # "probability/likelihood") is NOT banned — it is common colloquial football wording (e.g.
    # "缠斗概率高") allowed by check_customer_visible_copy; banned win-claim terms are 胜率/置信度
    # plus the en/vi/ms "win probability" forms below.
    "模型", "数据不足", "缺少数据", "数据缺失", "置信度", "胜率", "盲区",
    # zh betting
    "盘口", "投注", "下注", "赔率", "竞猜", "让球", "必中", "稳赚", "跟单", "回报率",
    # vi de-model / process
    "mô hình", "thiếu dữ liệu", "xác suất", "tỷ lệ thắng",
    # vi betting
    "kèo", "cửa trên", "cửa dưới", "tỷ lệ cược",
    # en de-model / process
    "model unavailable", "insufficient data", "win probability", "confidence score",
    # en betting
    "betting", "odds", "handicap", "bookmaker",
    # ms (Owner-listed)
    "model tidak tersedia", "data tidak mencukupi", "kebarangkalian menang",
]
# customer-visible text lives under i18n[lang] in these keys (NOT note/field_sources/model_fields.source).
TEXT_KEYS_PRED = ("prediction", "analysis", "operations", "copy_v2")


def _walk_strings(obj, path):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, "%s.%s" % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, "%s[%d]" % (path, i))


def _scan_text_block(block, path):
    out = []
    low = None
    for fp, s in _walk_strings(block, path):
        sl = s.lower()
        for term in BANNED:
            if term.lower() in sl:
                out.append((fp, "banned customer-visible term %r" % term))
    return out


def scan_package(pkg):
    """Return [(field_path, reason)] for every customer-visible violation. Empty list = clean."""
    v = []
    preds = (pkg or {}).get("predictions") or {}
    for fk, art in preds.items():
        i18n = (art or {}).get("i18n") or {}
        for lang, loc in i18n.items():
            for key in TEXT_KEYS_PRED:
                if key in loc:
                    v += _scan_text_block(loc[key], "predictions.%s.i18n.%s.%s" % (fk, lang, key))
        # structural: a presented prediction must NOT carry a numeric win_prob / confidence
        mf = (art or {}).get("model_fields") or {}
        for nf in ("win_prob", "confidence"):
            if isinstance(mf.get(nf), (int, float)):
                v.append(("predictions.%s.model_fields.%s" % (fk, nf), "fabricated %s (must be null)" % nf))
        for lang, loc in i18n.items():
            p = (loc or {}).get("prediction") or {}
            if isinstance(p.get("confidence"), (int, float)):
                v.append(("predictions.%s.i18n.%s.prediction.confidence" % (fk, lang), "fabricated confidence (must be null)"))
    obs = (pkg or {}).get("observations") or {}
    for fk, o in obs.items():
        i18n = (o or {}).get("i18n") or {}
        for lang, loc in i18n.items():
            v += _scan_text_block(loc, "observations.%s.i18n.%s" % (fk, lang))
    sel = (pkg or {}).get("selectedHotspot") or {}
    v += _scan_text_block({k: sel.get(k) for k in ("home", "away") if sel.get(k)}, "selectedHotspot")
    shares = (pkg or {}).get("shares") or {}
    if shares:
        v += _scan_text_block(shares, "shares")
    return v


def selftest():
    def pred(copy_v2):
        return {"predictions": {"X": {"model_fields": {"win_prob": None, "confidence": None},
                "i18n": {"zh": {"copy_v2": copy_v2, "prediction": {"confidence": None}}}}},
                "observations": {}, "selectedHotspot": {"home": "A", "away": "B"}}
    clean = pred({"hook_headline": "甲队该赢但这是效率局", "main_reason": "硬实力高一档"})
    bad_zh = pred({"hook_headline": "模型不可用，按估计", "main_reason": "x"})
    bad_vi = {"predictions": {"X": {"model_fields": {"win_prob": None, "confidence": None},
              "i18n": {"vi": {"copy_v2": {"hook_headline": "mô hình không khả dụng", "main_reason": "y"}}}}}}
    bad_prob = {"predictions": {"X": {"model_fields": {"win_prob": 0.62, "confidence": None}, "i18n": {}}}}
    bad_conf = {"predictions": {"X": {"model_fields": {"win_prob": None, "confidence": None},
                "i18n": {"zh": {"prediction": {"confidence": 0.7}}}}}}
    checks = [
        ("clean package passes", scan_package(clean) == []),
        ("模型 blocks", any("模型" in r for _, r in scan_package(bad_zh))),
        ("mô hình blocks", any("mô hình" in r for _, r in scan_package(bad_vi))),
        ("fake win_prob blocks", any("win_prob" in r for _, r in scan_package(bad_prob))),
        ("fake confidence blocks", any("confidence" in r for _, r in scan_package(bad_conf))),
        ("betting odds blocks", any("odds" in r for _, r in scan_package(pred({"hook_headline": "best odds today"})))),
    ]
    ok = all(v for _, v in checks)
    for n, v in checks:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d checks pass" % (sum(1 for _, v in checks if v), len(checks)))
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        return selftest()
    if "--package" in a:
        p = pathlib.Path(a[a.index("--package") + 1])
        pkg = json.loads(p.read_text(encoding="utf-8"))
        v = scan_package(pkg)
        for fp, r in v:
            print("FAIL  %s — %s" % (fp, r))
        if v:
            print("R6.1 PRE-UPLOAD CUSTOMER-VISIBLE GUARD FAIL — %d (do NOT upload)" % len(v)); return 1
        print("R6.1 PRE-UPLOAD CUSTOMER-VISIBLE GUARD PASS (no banned terms; win_prob/confidence null)"); return 0
    print("usage: --selftest | --package <file.json>"); return 2


if __name__ == "__main__":
    sys.exit(main())
