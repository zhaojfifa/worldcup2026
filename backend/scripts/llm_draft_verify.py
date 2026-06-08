#!/usr/bin/env python3
"""
Local LLM draft-only verification (no real key, no network, no DB writes).

Exercises the REAL admin endpoint via FastAPI TestClient with:
  - AI_PROVIDER=mock           → forces human_template_fallback (no real LLM key needed)
  - ADMIN_API_TOKEN=<local>    → a throwaway LOCAL token (NOT a real secret) to test the auth gate

It does NOT and CANNOT verify the real DeepSeek/Kimi provider — that runs only on Render
with real keys and the operator's $ADMIN_API_TOKEN (see docs/LLM_RENDER_VERIFICATION.md).
This script validates the contract (draft_only / publishable=false), the fallback path,
the response shape, and the forbidden-phrase filter (dirty / clean / negation).

Usage: python backend/scripts/llm_draft_verify.py
"""
import json
import logging
import os

# Must be set BEFORE importing the app (settings/router read these at import time).
os.environ["AI_PROVIDER"] = "mock"
os.environ["ADMIN_API_TOKEN"] = "local-qa-token-not-a-secret"
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # quiet SQL echo

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.services.llm import compliance  # noqa: E402

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # quiet SQL echo (post-import)

client = TestClient(app)
TOKEN = os.environ["ADMIN_API_TOKEN"]
URL = "/api/v1/admin/llm/generate-copy"

out = {"auth": {}, "drafts": [], "filter": []}

# ── 1. Auth gate ──
out["auth"]["no_token"] = client.post(URL, json={"match_id": 1, "language": "vi", "copy_type": "preview"}).status_code
out["auth"]["bad_token"] = client.post(URL, headers={"x-admin-token": "wrong"},
                                       json={"match_id": 1, "language": "vi", "copy_type": "preview"}).status_code

# ── 2. Draft generation (mock → fallback) ──
CASES = [
    (1, "mm", "preview"), (1, "vi", "preview"),
    (2, "vi", "upset"), (2, "mm", "upset"),
    (1, "zh", "preview"), (3, "vi", "live"), (3, "mm", "recap"),
]
for mid, lang, ctype in CASES:
    r = client.post(URL, headers={"x-admin-token": TOKEN},
                    json={"match_id": mid, "language": lang, "copy_type": ctype})
    out["drafts"].append({"req": {"match_id": mid, "language": lang, "copy_type": ctype},
                          "http": r.status_code, "body": r.json() if r.status_code == 200 else r.text})

# ── 2b. provider_override (backward compat + unknown + unavailable→fallback) ──
out["provider_override"] = []
OVERRIDE_CASES = [
    ("omitted", {"match_id": 1, "language": "vi", "copy_type": "preview"}),
    ("kimi", {"match_id": 1, "language": "vi", "copy_type": "preview", "provider_override": "kimi"}),
    ("deepseek", {"match_id": 1, "language": "mm", "copy_type": "preview", "provider_override": "deepseek"}),
    ("gemini", {"match_id": 1, "language": "vi", "copy_type": "preview", "provider_override": "gemini"}),
    ("bogus", {"match_id": 1, "language": "vi", "copy_type": "preview", "provider_override": "bogus"}),
]
for tag, payload in OVERRIDE_CASES:
    r = client.post(URL, headers={"x-admin-token": TOKEN}, json=payload)
    b = r.json() if r.status_code == 200 else {"_text": r.text}
    out["provider_override"].append({
        "tag": tag, "http": r.status_code,
        "provenance": b.get("provenance"), "status": b.get("status"),
        "publishable": b.get("publishable"), "warnings": b.get("warnings"),
    })

# ── 3. Forbidden-phrase filter: dirty / clean / negation ──
FILTER_CASES = [
    ("dirty-vi", "vi", "Cá cược chắc thắng, kiếm tiền dễ mỗi ngày, lợi nhuận chắc chắn."),
    ("dirty-zh", "zh", "稳赚必中，跟单下注，收益承诺包赢。"),
    ("dirty-mm", "mm", "ဒီပွဲမှာ လောင်းကစား လုပ်ပါ။"),
    ("dirty-en", "en", "Guaranteed win, sure win, place your bet now (betting)."),
    ("clean-vi", "vi", "⚽ Brazil vs Argentina — Xu hướng AI: Brazil nhỉnh (45%). Đây là góc nhìn dữ liệu AI."),
    ("clean-mm", "mm", "⚽ Brazil vs Argentina — AI အမြင်: Brazil သာ (45%)။ ဤသည် AI ဒေတာအမြင်ဖြစ်သည်။"),
    ("negation-vi", "vi", "Đây là phân tích dữ liệu AI · Không phải dịch vụ cá cược · Không nhận cược tiền mặt."),
    ("negation-zh", "zh", "MTC 为平台积分，不可提现、不可转让，仅供娱乐。"),
    ("negation-mm", "mm", "ဤသည် လောင်းကစား မဟုတ်ပါ။ MTC ငွေသား မထုတ်နိုင်ပါ။"),
]
for tag, lang, text in FILTER_CASES:
    hits = compliance.scan(text, lang)
    expect_clean = tag.startswith(("clean", "negation"))
    ok = (len(hits) == 0) == expect_clean
    out["filter"].append({"case": tag, "lang": lang, "hits": hits,
                          "expect_clean": expect_clean, "pass": ok})

_dest = os.environ.get("LLM_VERIFY_OUT", "/tmp/llm_verify.json")
with open(_dest, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(f"WROTE {_dest}")
