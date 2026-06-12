#!/usr/bin/env python3
"""
Growth copy guard (Growth P1, Owner GO) — scans every growth-surface copy source for
forbidden vocabulary BEFORE build/share. Files scanned (globs, missing = skipped+listed):

  frontend/src/pages/JoinPage.tsx              (customer landing /join)
  frontend/src/pages/GrowthAdminPage.tsx       (operator dashboard — held to the same bar)
  frontend/src/components/StrongSignalCard.tsx (share-card source surface labels)
  frontend/src/data/externalSignals/*.json     (projected expectation lines)
  backend/app/routers/growth.py                (any string reaching a response)
  backend/app/services/growth/*.py

Forbidden classes (4 languages; substring match on source text, code identifiers excluded
via a small allowlist):
  betting/odds/handicap/bookmaker · win-guarantee · commission/payout/recharge/cash-reward ·
  agent hierarchy · process/audit leakage
提现 is legal ONLY inside 不可提现. Exit 0 = clean. --selftest runs the embedded fixtures.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GLOBS = [
    "frontend/src/pages/JoinPage.tsx",
    "frontend/src/pages/GrowthAdminPage.tsx",
    "frontend/src/components/StrongSignalCard.tsx",
    "frontend/src/data/externalSignals/*.json",
    "backend/app/routers/growth.py",
    "backend/app/services/growth/*.py",
    # Growth P1.1 share layer
    "frontend/src/growth/shareTemplates.ts",
    "frontend/src/components/ShareBlock.tsx",
    "frontend/src/pages/ShareCardPage.tsx",
    "scripts/mvp2_growth_cli.py",
]

BETTING = ["博彩", "赔率", "盘口", "下注", "投注", "庄家", "让球", "大小球", "跟单", "竞猜", "串关",
           "购彩", "彩票", "亚盘",
           "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược", "đặt cược", "soi kèo", "tài xỉu", "chấp bóng",
           "လောင်းကစား", "လောင်းကြေး", "အလောင်းအစား", "လောင်းထား", "ကြေးပေါက်", "ပေါက်ကြေး", "လောင်းဒိုင်",
           "betting", "odds", "handicap", "bookmaker", "bet slip", "wager", "parlay"]
GUARANTEE = ["稳赚", "稳赢", "必中", "必赢", "包赢", "保赢", "chắc thắng", "bao thắng", "ăn chắc",
             "သေချာပေါက်", "guaranteed win", "sure win"]
MONEY = ["返佣", "佣金", "充值返利", "充值", "返现", "提现", "派彩", "奖金池", "分成", "拉新奖励", "邀请返利",
         "代理佣金", "hoa hồng", "nạp tiền", "rút tiền", "commission", "payout", "recharge", "cash reward",
         "cashback", "withdrawal"]
HIERARCHY = ["代理", "总代", "下级", "上级代理", "团队长", "层级", "đại lý", "tuyến dưới",
             "agent tier", "sub-agent", "downline", "multi-level"]
LEAKAGE = ["模型", "盲区", "数据缺失", "缺数据", "过程验证", "自证", "mô hình", "thiếu dữ liệu",
           "မော်ဒယ်", "ဒေတာမရှိ", "sha256", "deepseek", "gemini", "llm", "pipeline", "guardrail",
           "missing evidence", "data gap"]
# negation exemption: 提现 inside 不可提现 / 不能提现 is the COMPLIANCE statement, keep it
WITHDRAW_OK = re.compile(r"(不可|不能|无法)提现")
# identifiers/comments legitimately contain English terms (e.g. schema names); allow ONLY
# these exact code tokens, never display strings
CODE_TOKEN_ALLOW = {"commission_free_note"}  # none currently; placeholder for explicit review

CLASSES = [("betting", BETTING), ("win-guarantee", GUARANTEE),
           ("commission/payout/recharge", MONEY), ("agent-hierarchy", HIERARCHY),
           ("process/audit-leakage", LEAKAGE)]


def scan_text(text, name):
    errs = []
    low = text.lower()
    neutral = WITHDRAW_OK.sub("", text)  # strip legal 不可提现 before the 提现 check
    for cls, terms in CLASSES:
        for t in terms:
            hay = neutral if t == "提现" else (low if t.isascii() else text)
            needle = t.lower() if t.isascii() else t
            i = hay.lower().find(needle) if t.isascii() else hay.find(needle)
            if i >= 0:
                ctx = hay[max(0, i - 30):i + len(needle) + 30].replace("\n", " ")
                errs.append("%s: [%s] %r … %r" % (name, cls, t, ctx.strip()))
    return errs


def main(paths=None):
    files = []
    missing = []
    for g in (paths or GLOBS):
        hits = sorted(ROOT.glob(g)) if any(c in g for c in "*?[") else ([ROOT / g] if (ROOT / g).exists() else [])
        if not hits:
            missing.append(g)
        files.extend(h for h in hits if h.is_file())
    errs = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        # code comments are not customer copy — strip for source files (display strings stay)
        if f.suffix in (".tsx", ".ts", ".py"):
            text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
            text = re.sub(r"(?m)^\s*//.*$|(?<=\s)//[^\n]*$", " ", text)
            if f.suffix == ".py":
                text = re.sub(r"(?m)#.*$", " ", text)
        errs.extend(scan_text(text, str(f.relative_to(ROOT))))
    for f in files:
        print("scanned  %s" % f.relative_to(ROOT))
    for g in missing:
        print("skipped  %s (not present yet)" % g)
    if errs:
        print("\nGROWTH COPY FAIL (%d)" % len(errs))
        for e in errs:
            print("  - %s" % e)
        return 1
    print("\nGROWTH COPY PASS (%d file(s))" % len(files))
    return 0


def _selftest():
    ok = 0
    cases = [
        ("进群看临场修正，赛前看方向，临场看变量，赛后看校准。贡献值与 MTC 积分不可提现。", 0),
        ("分享得返佣，下注稳赚！", 3),           # money + betting + guarantee
        ("xem kèo nhà cái, cửa trên ăn chắc", 4),
        ("invite friends for commission payout", 2),
        ("情报官邀请码 QG-AB12 · 专属二维码 · 月度榜单", 0),
        ("提现规则请咨询客服", 1),               # bare 提现 without negation
    ]
    for text, want in cases:
        got = len(scan_text(text, "selftest"))
        status = "PASS" if got == want else "FAIL"
        if got == want:
            ok += 1
        print("%s  expect %d got %d  %r" % (status, want, got, text[:36]))
    print("GROWTH GUARD SELFTEST %s (%d/%d)" % ("PASS" if ok == len(cases) else "FAIL", ok, len(cases)))
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main(sys.argv[1:] or None))
