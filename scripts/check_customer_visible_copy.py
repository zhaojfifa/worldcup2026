#!/usr/bin/env python3
"""
Customer-visible copy scan (De-Modeling sprint, Implementation A).

Renders the trial customer surfaces with headless Chrome, strips everything a
customer does NOT see as primary copy — <script>/<style>/<title>, ALL <details>
internal folds (allowed to keep technical terms), the footer disclaimer lines
(.muted-note/.compliance/.disclaimer-line) and the decorative English brand line
(.hero-en) — then fails if any forbidden model/process word remains visible.

zh forbidden: 模型 / 数据缺失 / 缺数据 / 盲区 / 过程验证 / 自证
shared forbidden: LLM / DeepSeek / Gemini / pipeline / schema / provider /
  source ledger / internal_notes / evidence coverage / assumption / replay_only /
  source required / guardrail
vi forbidden: mô hình / thiếu dữ liệu
AI policy: case-sensitive whole-word "AI" must NOT appear in visible copy
  (allowed only in the stripped footer/EN-line/folds). Lowercase Vietnamese "ai" (= who) is fine.

Usage: python3 scripts/check_customer_visible_copy.py [base_url]   (default http://localhost:4321)
Routes: / , /predict/1489369 , /predict/1489371 , /recap/855737 , /recap/979139  × zh/vi
Exit 0 = clean.
"""
import html
import re
import subprocess
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROUTES = ["/", "/predict/1489369", "/predict/1489371", "/recap/855737", "/recap/979139"]
LANGS = ["zh", "vi"]

ZH_FORBIDDEN = ["模型", "数据缺失", "缺数据", "盲区", "过程验证", "自证"]
SHARED_FORBIDDEN = ["LLM", "DeepSeek", "Gemini", "pipeline", "schema", "provider",
                    "source ledger", "internal_notes", "evidence coverage",
                    "assumption", "replay_only", "source required", "guardrail"]
VI_FORBIDDEN = ["mô hình", "thiếu dữ liệu"]


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


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4321"
    fails = 0
    for route in ROUTES:
        for lang in LANGS:
            sep = "&" if "?" in route else "?"
            t = visible_text(f"{base}{route}{sep}lang={lang}")
            errs = []
            terms = SHARED_FORBIDDEN + (ZH_FORBIDDEN if lang == "zh" else VI_FORBIDDEN)
            for term in terms:
                n = t.count(term) if term not in ("provider", "schema", "assumption") else len(
                    re.findall(r"\b%s\b" % re.escape(term), t, flags=re.I))
                if n:
                    errs.append("%s ×%d" % (term, n))
            ai_hits = re.findall(r"\bAI\b", t)
            if ai_hits:
                errs.append("AI ×%d (visible, outside allowed zones)" % len(ai_hits))
            if lang == "vi":
                han = re.findall(r"[一-鿿]", t)
                if han:
                    errs.append("Han ×%d" % len(han))
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
