# LLM Render Verification — PENDING (operator/Owner)

**Status: PENDING — real provider call not yet verified on Render.**

The draft-only LLM endpoint is implemented and locally verified via the human-template fallback
(see `docs/LLM_REAL_INTEGRATION_PLAN.md`). The **real DeepSeek/Kimi call** can only be exercised on
Render, where the provider key lives. Claude has no provider key locally and **must not fabricate a
provider result.**

## Why pending
- Local/CI `AI_PROVIDER=mock` → `client.generate()` returns `None` → human-template fallback.
  `provenance` shows `human_template_fallback` (not a real LLM call).
- A real call requires Render env: `AI_PROVIDER=deepseek` (or `kimi`) + `DEEPSEEK_API_KEY` /
  `KIMI_API_KEY` set.

## Operator verification steps (Render)
1. Set Render backend env: `AI_PROVIDER=deepseek` (or `kimi`) and the matching key. Redeploy.
2. Confirm provider wiring (no secrets printed):
   ```bash
   curl https://worldcup2026-api-71n6.onrender.com/api/v1/data-source/status   # mock_mode reflects ai_provider
   ```
3. Call the draft endpoint (admin token from Render env):
   ```bash
   curl -X POST https://worldcup2026-api-71n6.onrender.com/api/v1/admin/llm/generate-copy \
     -H "x-admin-token: $ADMIN_API_TOKEN" -H "Content-Type: application/json" \
     -d '{"match_id":1,"language":"vi","copy_type":"preview"}'
   ```
4. Expect: `status:"draft_only"`, `publishable:false`, `provenance:"llm:deepseek"` (or `kimi`),
   `forbidden_hits:[]`. Repeat with `"language":"mm"`.
5. **Human-review** the draft text for compliance (AI-viewpoint only, no betting/hit-rate) before
   any manual send. Paste sanitized results below.

## Local verification done (2026-06-08) — contract / fallback / filter (NOT real provider)

Run: `PYTHONPATH=. python3 backend/scripts/llm_draft_verify.py` (`AI_PROVIDER=mock`, throwaway LOCAL
admin token — **not** a real secret). Exercises the **real endpoint** via FastAPI TestClient:

- **Auth gate:** no token → **401**; wrong token → **401**; valid token → **200**.
- **Contract (7 drafts: vi/mm/zh × preview/upset/live/recap):** every response
  `status=draft_only`, `publishable=false`, `provenance=human_template_fallback`, `data_mode=mock`,
  `forbidden_hits=[]`, warnings carry the fallback + mock-data notes. (Real LLM still pending — mock.)
- **Team-name localization fix verified:** vi/mm/en drafts now use English names (Brazil/Argentina…,
  **0 Han**); zh keeps Chinese. (`copy_service._localized_team_names`.)
- **Forbidden-phrase filter (9 cases, all PASS):**
  - dirty **caught** — vi `chắc thắng/cá cược/kiếm tiền/lợi nhuận chắc chắn`; zh `下注/包赢/必中/收益承诺/稳赚/跟单`;
    mm `လောင်းကစား`; en `betting/guaranteed win/sure win`.
  - clean vi/mm → `[]`.
  - **negation allowed** → vi `Không phải dịch vụ cá cược · Không nhận cược tiền mặt`, zh `不可提现`,
    mm `လောင်းကစား မဟုတ်` → all `[]`.
- Drafts recorded in `docs/LLM_DRAFT_COPY_REVIEW_LOG.md` (human_review_status=pending).

**Still PENDING:** the **real DeepSeek/Kimi provider call on Render** (operator + `$ADMIN_API_TOKEN`).
Claude has no provider key and does not fabricate a real-LLM result.

## Result log (fill on Render — real provider rows)
| Date | Provider | language | copy_type | provenance | forbidden_hits | reviewed | notes |
|------|----------|----------|-----------|------------|----------------|----------|-------|
|      |          |          |           | _(expect llm:deepseek / llm:kimi)_ |    | pending |       |

## Guardrails (unchanged)
- Draft-only; **no auto-publish, no DB write, no payment, no bot.**
- Rollback: set `AI_PROVIDER=mock` → instant fallback to human templates (no migration).
- **LLM production beyond draft-only is Owner-gated.**
