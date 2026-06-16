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
