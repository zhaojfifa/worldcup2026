# LLM Provider Comparison — Kimi / DeepSeek / Gemini (draft-only)

_Created 2026-06-08 · Owner ruling: **Kimi / DeepSeek / Gemini comparison = GO.**_
_Goal: find the **operator-usable** option for vi/mm draft copy — not a leaderboard #1._

> **Draft-only.** All calls below went through the admin-only, draft-only endpoint
> (`status=draft_only`, `publishable=false`, no DB write, no publish). **No keys are printed or
> committed.** Real-provider calls were run **locally** (provider keys already present in the local
> `.env`, pre-existing — not added for this task) via `provider_override`. Outputs are real, not fabricated.

## 1. Providers & assumed roles
| Provider | Model (code) | Assumed role (Owner) | Cost/latency note |
|----------|--------------|----------------------|-------------------|
| **Kimi** (Moonshot) | `moonshot-v1-8k` | primary candidate | mid latency |
| **DeepSeek** | `deepseek-chat` | low-cost fallback | low cost |
| **Gemini** | `gemini-2.5-flash` | benchmark / pending | thinking model — needs `thinkingBudget=0` |

## 2. Comparison dimensions
language_naturalness · football_understanding · explainability · risk_control · brevity ·
operator_usability · cost_latency · consistency.

## 3. Method
- Endpoint `POST /api/v1/admin/llm/generate-copy` with `provider_override`.
- Cases: 3 providers × {vi, mm} × {preview, upset} = 12 real draft calls (seed matches; `data_mode=mock`).
- Each draft auto-scanned: `forbidden_hits`, Han-character count (vi/mm should be 0), latency.
- Two passes: **before** and **after** a prompt hardening (`Respond ONLY in {lang}…`) + Gemini
  `thinkingBudget=0` / `maxOutputTokens=600`.

## 4. Results (real, after hardening)

| Provider | vi/preview | mm/preview | vi/upset | mm/upset | Han leak (vi/mm) | forbidden_hits | latency |
|----------|-----------|-----------|----------|----------|------------------|----------------|---------|
| **Gemini** | ✅ clean, structured | ✅ full Burmese | ✅ clean | ✅ clean | **0** (all) | `[]` | ~2.9–4.3s |
| **DeepSeek** | ✅ clean, structured | ✅ full Burmese | ✅ clean | ✅ (1 EN label) | **0** (all) | `[]` | ~2.8–4.3s |
| **Kimi** | ⚠️ mostly vi (han≈4) | ❌ **fully Chinese** (han≈123) | ❌ **fully Chinese** (han≈112) | ⚠️ Burmese but repetitive/garbled | **high on 2/4** | `[]` | ~2.1–7.1s |

### Per-dimension (1–5, operator lens)
| Dimension | Gemini | DeepSeek | Kimi |
|-----------|:------:|:--------:|:----:|
| language_naturalness (vi/mm) | 5 | 5 | 2 |
| football_understanding | 4 | 5 | 4 |
| explainability | 4 | 5 | 3 |
| risk_control (compliance) | 5 | 5 | 5 |
| brevity | 4 | 3 (verbose, markdown) | 3 |
| operator_usability | 4 | 5 | 2 |
| cost_latency | 4 | 4 | 3 |
| consistency | 4 | 5 | 2 |

## 5. Key findings (honest, contradicts the assumed roles)
- **DeepSeek is the most operator-usable today** — consistently clean vi **and** mm, structured,
  0 Han, compliant. (Slightly verbose / markdown-heavy; trim in review.)
- **Gemini is now strong** after the `thinkingBudget=0` fix (before the fix its output was truncated).
  Cleanest plain-text structure; good benchmark and a viable primary.
- **Kimi underperforms for vi/mm**: even with a hardened "respond only in {lang}" prompt it returned
  **full Chinese** for mm/preview and vi/upset, and repetitive Burmese for mm/upset. **Not reliable
  as-is** for the vi/mm customer path — needs more prompt work or is better kept for zh.
- **Compliance held everywhere** (`forbidden_hits=[]`) — but note a draft can be *compliant yet
  wrong-language* (Kimi's Chinese-in-vi). → add a **language-fidelity gate** (Han ratio) at review
  time (see `docs/MINI_AGENT_HARNESS_DESIGN.md` §4).

## 6. Recommendation (draft-only; Owner decides production)
- **Primary (operator drafts, vi/mm): DeepSeek** — best consistency/usability now; low cost.
- **Benchmark / co-primary: Gemini** — clean output post-config; keep for quality comparison.
- **Kimi:** keep available via `provider_override` but **do not use for vi/mm** until prompt work
  closes the Chinese-leak; acceptable for internal zh.
- This is **not** an auto-routing decision: provider is chosen per call (`provider_override`), every
  draft is human-reviewed, nothing is auto-published. Owner makes the production-provider call.

## 7. Repro
`provider_override` field on `POST /api/v1/admin/llm/generate-copy` (admin, draft-only). Manual local
capture used `backend/scripts/llm_draft_verify.py` (contract/filter) + an ad-hoc compare run. Real
provider keys live in Render (and, locally, in the developer's `.env`); **never committed**. Gemini
remained **pending** until the `thinkingBudget=0` fix; now configured.

## 8. Sample drafts (real, draft-only, human_review_status=pending)
- **Gemini · mm/preview:** `ဘရာဇီး vs အာဂျင်တီးနား ပွဲကြို AI အချက်ပြမှု …` (full Burmese, 0 Han, + disclaimer).
- **DeepSeek · vi/upset:** `**Cảnh báo bất ngờ: Morocco vs France** … *Lưu ý: Dữ liệu mô phỏng…*` (clean vi).
- Full texts logged in `docs/LLM_DRAFT_COPY_REVIEW_LOG.md`.
