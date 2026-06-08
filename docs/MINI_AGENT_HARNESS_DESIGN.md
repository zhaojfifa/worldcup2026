# Mini-Agent Harness — Lightweight Design (draft-only)

_Created 2026-06-08 · Owner ruling: **Mini-Agent Harness = GO, lightweight only.**_

> **Scope guard:** this is a **design + prompt spec**, not a runtime. No complex orchestration
> framework, no new always-on service, no auto-publish, no DB writes, no payment, no scaling.
> Every stage is a pure function over JSON; the only side-effectful stage (real LLM call) reuses the
> existing **draft-only** `client.generate()` path. Output stays `draft_only` + human-review-required.

## 0. Why a pipeline (not one big prompt)
The goal is **data → model judgement → multi-angle explanation → operator-attractive copy**, with a
**compliance gate** and **human review** at the end. Splitting into small agents makes each step
inspectable, cheap to test, and easy to swap a provider per step (see
`docs/LLM_PROVIDER_COMPARISON_REPORT.md`). Stages 1–2 are deterministic (no LLM); stages 4–6 are the
only ones that need a model; stage 7 is the existing forbidden-phrase filter; stage 8 is a human.

## 1. Data flow (one match → one reviewed draft)

```
Match(id) ──▶ 1 Data Scout ──▶ 2 Baseline Model ──▶ 3 Risk Analyst ─┐
                                                                     ├─▶ 5 Explanation ──▶ 6 Copy ──▶ 7 Compliance ──▶ 8 Human Review
                                                     4 Contrarian ───┘
```

All payloads are JSON; `data_mode` (mock|real) and `language` (vi|mm|zh|en) ride along the whole chain.

## 2. Agents — I/O contracts + prompt intent

### 1 · Data Scout  *(deterministic — no LLM)*
- **Input:** match, fixture, result, status (from `match_service` / `data-source/status`).
- **Output:** `{ data_mode: "mock"|"real", freshness: {fixtures_at, results_at}, missing_fields: [...], usable_for_copy: bool }`.
- **Rule:** if `data_mode=mock` or results are seed → set `usable_for_copy=false` for any
  hit-rate/accuracy claim; copy may only use AI-viewpoint framing.

### 2 · Baseline Model Agent  *(deterministic — no LLM; reuses `match_service`/`ops`)*
- **Input:** `win_prob{home,draw,away}`, `confidence`, `risk_level`, `risk_note`, `recommended_score`.
- **Output:** `{ model_view: str, probability_summary: str, lead_side, confidence_band }`.
- **Rule:** numbers pass through verbatim; never invent probabilities.

### 3 · Risk Analyst  *(LLM optional; can run from `risk_note` deterministically)*
- **Input:** `risk_note`, team context, `risk_level`.
- **Output:** `{ top_risks: [≤3], upset_angle: str }`.

### 4 · Contrarian Agent  *(LLM)*
- **Input:** `model_view` (+ probability_summary).
- **Output:** `{ why_wrong: [≤2] }` — the strongest case the model is wrong (lineup, motivation, draw risk).
- **Rule:** a devil's-advocate, **not** a betting tip; no "bet the other side" framing.

### 5 · Explanation Agent  *(LLM)*
- **Input:** model_view + top_risks + why_wrong.
- **Output:** `{ reason_bullets: [2-3], risk_explanation: str }` in the target language.

### 6 · Copy Agent  *(LLM — this is today's `copy_service.generate_copy`)*
- **Input:** explanation + `language` + `copy_type` (preview|upset|live|recap).
- **Output:** `{ generated_text, provenance, data_mode }` — a **vi/mm social draft**.
- **Rule:** target-language only (no Chinese for vi/mm), team names in English, end with disclaimer.

### 7 · Compliance Agent  *(deterministic — existing `compliance.scan`)*
- **Input:** copy draft + locale.
- **Output:** `{ forbidden_hits: [...], warnings: [...], pass: bool }`.
- **Rule:** block on any forbidden hit; negations allowed (`Không phải dịch vụ cá cược`, `不可提现`,
  `လောင်းကစား မဟုတ်`). **Add a language-fidelity check** (target-language ratio) — see §4.

### 8 · Human Review  *(human — no automation)*
- **Input:** draft + filter result.
- **Output:** `approved | rejected | revised` + `reviewer_note`, logged in
  `docs/LLM_DRAFT_COPY_REVIEW_LOG.md` (`human_review_status`, `whether_sent_to_social=no`).
- **Rule:** only **approved** copy may be sent **manually** by the operator. The harness never sends.

## 3. Mapping to today's code (what already exists vs planned)
| Stage | Status | Where |
|-------|--------|-------|
| 1 Data Scout | partial (deterministic data exists) | `data-source/status`, `match_service` |
| 2 Baseline | **exists** | `match_service`, `frontend/src/ops/derive.ts` (mirror) |
| 3 Risk / 4 Contrarian / 5 Explanation | **planned (prompt-only)** | new prompt blocks (not wired) |
| 6 Copy | **exists (draft-only)** | `services/llm/copy_service.py` + `prompts.py` + `client.py` |
| 7 Compliance | **exists** | `services/llm/compliance.py` |
| 8 Human Review | process | `docs/LLM_DRAFT_COPY_REVIEW_LOG.md` |

**This round adds only:** `provider_override` (stage 6 can pick kimi/deepseek/gemini per the comparison)
and a hardened target-language instruction in `prompts.py`. Stages 3–5 remain **prompt drafts**, not runtime.

## 4. Language-fidelity gate (new review dimension)
Real comparison showed a provider (Kimi) can return **Chinese for vi/mm** while passing the
forbidden-phrase filter (it is not a betting violation). So a draft can be "compliant" yet wrong-language.
**Add to stage 7 / human review:** reject if the draft's target-language character ratio is low (e.g.
Han characters present in a vi/mm draft → reject/revise). For now this is a **manual reviewer check**
(documented), not new code.

## 5. Non-goals (explicit)
No autonomous multi-turn agent loop, no tool-calling runtime, no message-queue, no scheduler, no
auto-send to Telegram/Zalo, no DB writes, no payment, no scaling. Draft-only throughout.
