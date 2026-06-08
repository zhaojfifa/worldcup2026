# LLM Real Integration — Draft-Only (Harness-X · Owner-approved bounded L2-lite)

**Verdict: PASS (draft-only).** Real DeepSeek/Kimi client implemented behind an admin-only,
draft-only endpoint with a forbidden-phrase filter and human-template fallback. **No auto-publish,
no DB writes, no payment, no scaling, no public API-shape change.**

## 1. Input / boundary
Owner裁决: real data/model/LLM GO, but resource scaling NO-GO, payment NO-GO, bot/auto-publish
NO-GO, unreviewed LLM output NO-GO. LLM output is **draft_only** and requires human review.

## 2. What was built (backend, additive)
```
app/services/llm/
  compliance.py    # forbidden-phrase filter (zh/vi/mm/en), allows negations (不可提现, Không phải dịch vụ cá cược…)
  prompts.py       # system+user prompt builder per copy_type/language; embeds hard compliance rules
  client.py        # real provider call: deepseek (api.deepseek.com) / kimi (api.moonshot.cn); None on any failure
  copy_service.py  # orchestrate: fetch match → LLM → fallback human template → filter → draft payload
app/routers/llm.py # POST /api/v1/admin/llm/generate-copy  (x-admin-token; draft_only)
```
- `httpx` already in `requirements.txt` (no new dependency). No DB model added. No existing
  endpoint/schema changed.

## 3. Endpoint contract
```
POST /api/v1/admin/llm/generate-copy        (header: x-admin-token)
body: { "match_id": int, "language": "vi|mm|zh|en", "copy_type": "preview|upset|live|recap" }
200 → {
  match_id, language, copy_type,
  generated_text,            // draft text
  provenance,                // "llm:deepseek" | "llm:kimi" | "human_template_fallback"
  data_mode,                 // "mock" | "real" (mirrors /data-source/status)
  warnings: [...],           // e.g. fallback used, data_mode=mock, forbidden detected
  forbidden_hits: [...],     // non-empty ⇒ must revise before publish
  disclaimer, status: "draft_only", publishable: false
}
400 → invalid language/copy_type or match not found
401 → missing/invalid x-admin-token (or ADMIN_API_TOKEN unset)
```

## 4. Provider dispatch & fallback
- `settings.ai_provider` selects provider: `deepseek` → DeepSeek, `kimi` → Moonshot/Kimi,
  else / missing key / any error → **None → human-template fallback** (current rules copy).
- Client uses a 20s timeout, no retries, never raises, never logs secrets.
- **Rollback:** set `AI_PROVIDER=mock` → all drafts come from human templates again. No migration.

## 5. Guardrails (verified locally)
- Forbidden filter: `稳赚/必中/提现`(zh), `chắc thắng/cá cược`(vi), `လောင်းကစား`(mm),
  `guaranteed win/wager`(en) flagged; negations allowed (`不可提现`, `Không phải dịch vụ cá cược`,
  `လောင်းကစား မဟုတ်`). Verified: clean→[], dirty→hits, negations→[].
- `status` always `draft_only`, `publishable: false` — **never auto-published**.
- `data_mode=mock` adds a "do not present as real accuracy" warning.
- Output fields cover the schema: reason/social/recap/risk copy via `copy_type`; vi & mm supported.

## 6. Output field coverage vs Owner's list
| Requested | Covered by |
|-----------|-----------|
| reason_bullets | `copy_type=preview` text |
| risk_explanation | `copy_type=upset` / risk note in preview |
| social_copy_vi / social_copy_mm | `language=vi` / `language=mm` |
| recap_copy | `copy_type=recap` (meaningful only when real result exists) |
| title_options | (future: add `copy_type=title`; not in this minimal loop) |

## 7. Verification commands
```
# local: import + auth + filter (done)
python3 -c "from app.main import app"                      # import OK
# 401 without token, 400 bad language, 200 draft with token (TestClient) — verified
# real call (on Render, AI_PROVIDER=deepseek|kimi + key):
curl -X POST .../api/v1/admin/llm/generate-copy \
  -H "x-admin-token: $ADMIN_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"match_id":1,"language":"vi","copy_type":"preview"}'
```

## 8. Risk / blocker
- **Real LLM call not exercised locally** (no key; `AI_PROVIDER=mock`). Path verified via
  fallback + unit tests; **real-provider call must be validated on Render** — steps + result log in
  **`docs/LLM_RENDER_VERIFICATION.md`** (status: PENDING).
- Until then drafts come from human templates (compliant, fallback path).

## 9. Next Owner decision needed?
**Yes (ops):** on Render, set `AI_PROVIDER=deepseek` (or `kimi`) + key to exercise the real call,
then review drafts before any manual publish. Full auto-publish remains NO-GO.
