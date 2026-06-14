#!/usr/bin/env python3
"""
Customer-visible copy scan — unified zh / vi / my (VI Naming Consolidation +
MY Locale Replication sprint; extends the De-Modeling sprint scanner).

Renders the trial customer surfaces with headless Chrome, strips everything a
customer does NOT see as primary copy — <script>/<style>/<title>, ALL <details>
internal folds (allowed to keep technical terms), the footer disclaimer lines
(.muted-note/.compliance/.disclaimer-line) and the decorative English brand line
(.hero-en) — then fails if any forbidden model/process word remains visible.

Surfaces: / , /predict/1489369 , /predict/1489371 , /recap/855737 , /recap/979139
          × zh / vi / my  = 15 surfaces.

Per-language checks
  shared : LLM / DeepSeek / Gemini / pipeline / schema / provider / source ledger /
           internal_notes / evidence coverage / assumption / replay_only /
           source required / guardrail; case-sensitive whole-word "AI" must NOT
           appear in visible copy (lowercase Vietnamese "ai" = who is fine).
  zh     : 模型 / 数据缺失 / 缺数据 / 盲区 / 过程验证 / 自证 banned;
           persona naming present: 俅哥.
  vi     : mô hình / thiếu dữ liệu banned; Han = 0; naming standardized —
           "Tiên Tri Bóng Đá" present, retired "Nhà Tiên Tri" absent.
  my     : မော်ဒယ် (model) / ဒေတာမရှိ (we-lack-data) banned; Burmese gambling /
           odds / guarantee vocabulary banned (လောင်းကစား / လောင်းကြေး /
           အလောင်းအစား / လောင်းထား / ကြေးပေါက် / ပေါက်ကြေး / သေချာပေါက် / အာမခံ);
           Han = 0 (no Chinese anywhere); persona present: Oracle.

Usage: python3 scripts/check_customer_visible_copy.py [base_url]   (default http://localhost:4321)
Exit 0 = clean.
"""
import html
import re
import subprocess
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# /recap/1489369 = first REAL post-match recap surface (A4, Mexico 2-0 South Africa);
# /predict/1489369 stays listed — post-match it redirects there, both must scan clean.
# /join = Growth P1 ambassador landing (customer surface; QR/admin machinery must NOT appear)
ROUTES = ["/", "/predict/1489369", "/predict/1489371", "/recap/855737", "/recap/979139", "/recap/1489369", "/join"]
LANGS = ["zh", "vi", "my"]

ZH_FORBIDDEN = ["模型", "数据缺失", "缺数据", "盲区", "过程验证", "自证",
                # Owner hotfix 2026-06-14: RECAP_PENDING is an INTERNAL state — never expose
                # recap-generation / production status to customers.
                "复盘生成中", "待生成复盘", "生成中", "AI 正在生成", "自动生成",
                # Product Closure P1 §12: betting vocabulary banned visible, even negated
                "赔率", "盘口", "投注", "博彩", "下注", "庄家", "让球", "大小球", "跟单"]
SHARED_FORBIDDEN = ["LLM", "DeepSeek", "Gemini", "pipeline", "schema", "provider",
                    "source ledger", "internal_notes", "evidence coverage",
                    "assumption", "replay_only", "source required", "guardrail",
                    # §12 EN betting vocabulary + §11 process leakage
                    "betting", "odds", "handicap", "bookmaker", "bet slip", "wager",
                    "sha256", "artifact", "missing evidence", "data gap", "mock"]
VI_FORBIDDEN = ["mô hình", "thiếu dữ liệu", "Nhà Tiên Tri",  # incl. retired persona name
                # Owner hotfix 2026-06-14: no internal recap-generation wording
                "đang tạo phục dựng", "đang dựng phục dựng",
                "kèo", "cửa trên", "cửa dưới", "nhà cái", "cá cược"]
MY_FORBIDDEN = ["မော်ဒယ်", "ဒေတာမရှိ",
                # Owner hotfix 2026-06-14: no internal recap-generation wording
                "ပြင်ဆင်နေသည်", "ထုတ်နေဆဲ",
                "လောင်းကစား", "လောင်းကြေး", "အလောင်းအစား", "လောင်းထား",
                "ကြေးပေါက်", "ပေါက်ကြေး", "သေချာပေါက်", "အာမခံ"]
# Naming standardization: the persona must be visible on every customer surface.
REQUIRED_PERSONA = {"zh": "俅哥", "vi": "Tiên Tri Bóng Đá", "my": "Oracle"}
HAN = re.compile(r"[一-鿿]")


def visible_text(url):
    raw = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=6000", "--dump-dom", url],
        capture_output=True, text=True, timeout=60).stdout
    raw = re.sub(r"<(script|style|title)[^>]*>.*?</\1>", " ", raw, flags=re.S)
    raw = re.sub(r"<details\b.*?</details>", " ", raw, flags=re.S)  # internal folds allowed
    # strip footer/disclaimer/EN-brand nodes (single-div bodies, no nested divs)
    for cls in ("muted-note", "compliance", "disclaimer-line", "hero-en", "nv-prov"):
        raw = re.sub(r'<[a-z0-9]+ class="[^"]*\b%s\b[^"]*"[^>]*>(?:(?!<div)[^<]|<(?!/?div)[^>]*>)*?</[a-z0-9]+>' % cls,
                     " ", raw, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def lang_terms(lang):
    if lang == "zh":
        return ZH_FORBIDDEN
    if lang == "vi":
        return VI_FORBIDDEN
    return MY_FORBIDDEN


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4321"
    fails = 0
    for route in ROUTES:
        for lang in LANGS:
            sep = "&" if "?" in route else "?"
            t = visible_text(f"{base}{route}{sep}lang={lang}")
            errs = []
            for term in SHARED_FORBIDDEN + lang_terms(lang):
                n = t.count(term) if term not in ("provider", "schema", "assumption") else len(
                    re.findall(r"\b%s\b" % re.escape(term), t, flags=re.I))
                if n:
                    errs.append("%s ×%d" % (term, n))
            # ASCII-boundary pattern: \b misses zh-embedded AI (今日AI观点) because CJK is \w
            ai_hits = re.findall(r"(?<![A-Za-z0-9_])AI(?![A-Za-z0-9_])", t)
            if ai_hits:
                errs.append("AI ×%d (visible, outside allowed zones)" % len(ai_hits))
            if lang in ("vi", "my"):
                han = HAN.findall(t)
                if han:
                    errs.append("Han ×%d (%s)" % (len(han), "".join(han[:12])))
            if REQUIRED_PERSONA[lang] not in t:
                errs.append("persona %r missing (naming not standardized)" % REQUIRED_PERSONA[lang])
            tag = "%s?lang=%s" % (route, lang)
            if errs:
                fails += 1
                print("FAIL  %-28s %s" % (tag, "; ".join(errs)))
            else:
                print("PASS  %-28s" % tag)
    print("\n%s" % ("VISIBLE-COPY FAIL" if fails else "VISIBLE-COPY PASS"))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
