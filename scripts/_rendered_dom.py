"""P4R shared — dump an SPA route's rendered DOM via headless Chrome (same approach as
check_customer_visible_copy.py). Returns the DOM text, or '' on failure."""
import subprocess

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def dump_dom(url, budget_ms=9000):
    try:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                            "--virtual-time-budget=%d" % budget_ms, "--dump-dom", url],
                           capture_output=True, text=True, timeout=90)
        return r.stdout or ""
    except Exception:
        return ""


def demo_pair_leak(text):
    """Return the demo PAIRING leaked into the text, or None. The concern is the DEMOTED demo
    content (Netherlands-vs-Japan as a today-hotspot, Qatar-vs-Ecuador demo detail) appearing in a
    critical section — NOT bare team names, which legitimately appear in the WC-2022 historical
    archive (e.g. Germany vs Japan, Qatar vs Ecuador 2022 opener). Match only when both sides of a
    demo pair appear ADJACENTLY (within 24 chars), in zh or en."""
    import re
    flat = re.sub(r"\s+", " ", text)
    pairs = [(["Netherlands", "荷兰"], ["Japan", "日本"]),
             (["Qatar", "卡塔尔"], ["Ecuador", "厄瓜多尔"])]
    for left, right in pairs:
        for lt in left:
            for m in re.finditer(re.escape(lt), flat):
                window = flat[m.start(): m.start() + 24 + len(lt)]
                if any(rt in window for rt in right):
                    return "%s vs %s" % (lt, next(rt for rt in right if rt in window))
    return None


def strip_folds(dom):
    """Remove collapsed <details> fold content before a customer-visible scan — matches the canonical
    check_customer_visible_copy convention (internal-demo / archive folds are NOT the active surface).
    Only strips folds that are NOT open (no ' open' attribute)."""
    import re
    return re.sub(r"<details(?![^>]*\sopen)[^>]*>.*?</details>", " ", dom, flags=re.S | re.I)
