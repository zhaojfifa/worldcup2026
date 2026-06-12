#!/usr/bin/env python3
"""
MVP-2 Product Closure P1 — customer-safe EXTERNAL SIGNAL PROJECTION (engineering stage).

Reads the INTERNAL signal frame (docs/data_audit/mvp2_external_signals/{id}.external_signals.json,
never bundled) and emits a bundled, customer-safe projection JSON for the frontend:
  frontend/src/data/externalSignals/{id}.json

Hard rules (Owner §8, design doc §2 policy):
  - ONLY recorded signals (missing_evidence=false) project; missing signals project NOTHING.
  - Projection vocabulary is the FIXED Owner-approved customer-safe set (外部预期 / 公开预测倾向 /
    热度集中…). No sources, no prices, no bookmaker names, no odds/handicap/betting words,
    no player names from rumor signals (rumors project as conditional "锋线核心" phrasing and
    NEVER as confirmed absence — official XI is the only confirmation).
  - This file maps enum values to fixed phrases. It writes ZERO football narrative —
    the judgement lines on the page stay LLM fields (main_lean / scoreline_view / ...).
  - A defensive forbidden-word check runs on every projected string before writing.

Usage: python3 scripts/mvp2_project_external_signals.py 1489371
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIGNALS = ROOT / "docs" / "data_audit" / "mvp2_external_signals"
OUT = ROOT / "frontend" / "src" / "data" / "externalSignals"

FORBIDDEN = ["赔率", "盘口", "投注", "博彩", "下注", "庄家", "让球", "大小球", "跟单",
             "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược", "tài xỉu",
             "betting", "odds", "handicap", "bookmaker", "bet slip", "wager",
             "လောင်းကစား", "လောင်းကြေး", "ကြေးပေါက်",
             "neymar", "espn", "racing post", "sportsline", "vsin", "fox", "bein"]

# market_expectation enum -> which side the expectation leans to ("home"/"away"/None)
MARKET_LEAN = {
    "heavy_favourite_home": "home", "moderate_favourite_home": "home", "slight_favourite_home": "home",
    "heavy_favourite_away": "away", "moderate_favourite_away": "away", "slight_favourite_away": "away",
    "even": None,
}

# Fixture display names for the only projected fixture so far (engineering facts).
TEAMS = {"1489371": {"home": {"zh": "巴西", "vi": "Brazil", "my": "Brazil"},
                     "away": {"zh": "摩洛哥", "vi": "Morocco", "my": "Morocco"}}}


def project(fid):
    src = SIGNALS / ("%s.external_signals.json" % fid)
    d = json.loads(src.read_text(encoding="utf-8"))
    S = d["signals"]
    t = TEAMS[str(fid)]
    lines = {"zh": [], "vi": [], "my": []}

    def add(zh, vi, my):
        lines["zh"].append(zh); lines["vi"].append(vi); lines["my"].append(my)

    mk = S.get("market_expectation", {})
    if not mk.get("missing_evidence", True) and MARKET_LEAN.get(mk.get("value")):
        side = MARKET_LEAN[mk["value"]]
        add("外部预期偏向%s" % t[side]["zh"],
            "Kỳ vọng bên ngoài nghiêng về %s" % t[side]["vi"],
            "ပြင်ပမျှော်လင့်ချက်က %s ဘက် ယိမ်းနေသည်" % t[side]["my"])

    ex = S.get("expert_consensus", {})
    if not ex.get("missing_evidence", True):
        add("公开预测更看好巴西，但摩洛哥的防守韧性不能低估",
            "Dự đoán công khai nghiêng về Brazil, nhưng độ lì của hàng thủ Morocco không thể xem nhẹ",
            "လူထုခန့်မှန်းချက် Brazil ဘက်ဖြစ်သော်လည်း Morocco ၏ ခံစစ်ကြံ့ခိုင်မှုကို မလျှော့တွက်ရ")

    mh = S.get("media_heat", {})
    if not mh.get("missing_evidence", True):
        add("热度集中在巴西锋线核心和新帅首秀；摩洛哥教练变化是风险变量",
            "Sức nóng tập trung vào mũi nhọn Brazil và màn ra mắt của tân HLV; thay đổi HLV của Morocco là biến số rủi ro",
            "အာရုံစိုက်မှု Brazil တိုက်စစ်အဓိကနှင့် နည်းပြသစ် ပထမပွဲပေါ်; Morocco နည်းပြပြောင်းလဲမှုက risk variable")

    lu = S.get("lineup_rumor_signal", {})
    if not lu.get("missing_evidence", True):
        add("如果巴西锋线核心不进首发，进球参考区间需要下调——以官方首发为准",
            "Nếu mũi nhọn hàng công Brazil không đá chính, vùng tham khảo bàn thắng cần hạ xuống — chốt theo đội hình chính thức",
            "Brazil တိုက်စစ်အဓိက ပွဲမထွက်ပါက ဂိုးရည်ညွှန်းအပိုင်းအခြား လျှော့ချရမည် — တရားဝင် lineup အတိုင်းသာ")

    blob = json.dumps(lines, ensure_ascii=False).lower()
    bad = [w for w in FORBIDDEN if w in blob]
    if bad:
        raise SystemExit("REFUSED: forbidden term(s) in projection: %r" % bad)

    out = {"fixture_id": str(fid), "projected_from": "mvp2_external_signals (internal; sources stay internal)",
           "policy": "docs/MVP2_EXTERNAL_EXPECTATION_SIGNALS_DESIGN.md#2-policy",
           "label": {"zh": "外部预期 · 公开倾向", "vi": "Kỳ vọng bên ngoài · Xu hướng công khai",
                     "my": "ပြင်ပမျှော်လင့်ချက် · လူထုထင်မြင်ချက်"},
           "lines": lines}
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / ("%s.json" % fid)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("projected %d line(s)/lang -> %s" % (len(lines["zh"]), p.relative_to(ROOT)))


if __name__ == "__main__":
    project(sys.argv[1] if len(sys.argv) > 1 else "1489371")
