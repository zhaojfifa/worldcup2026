# MVP-2 — LLM Narrative Contract

> **Date:** 2026-06-10 · **Status:** executable contract for the narrative generator, the guard, and the pages.
> The LLM is given the **input** below and MUST return the **output** below as **JSON only** (no prose wrapper,
> no markdown fences). Pairs with `MVP2_LLM_NARRATIVE_ARCHITECTURE.md` and the prompts in `docs/prompts/`.

---

## Input (engineering → LLM)
Assembled by `scripts/mvp2_generate_scoutscore_narrative.py` from real artifacts. One call per language.
```jsonc
{
  "fixture_id": "855737",
  "product_name": "Giành Cup AI ScoutScore",
  "language": "zh-CN",                       // or "vi-VN"
  "mode": "historical_recap_product_validation",
  "fixture": { "home": "Argentina", "away": "Saudi Arabia", "competition": "...", "status": "finished" },
  "score": { "home": 1, "away": 2, "winner": "away", "text": "Argentina 1-2 Saudi Arabia" },
  "teams": { "home": {...}, "away": {...} },
  "scoutscore_factors": [                      // from ScoutScore factor_validation
    { "factor": "efficiency", "role": "decisive|underweighted|verified|context",
      "pre_status": "missed|invalidated|partial|confirmed_gap", "note": "...",
      "source_refs": [ { "field": "...", "endpoint": "...", "value": "..." } ], "assumption": false }
  ],
  "evidence_cards": [ { "label": "控球率", "value": "69% / 31%", "source": "/fixtures/statistics" } ],
  "source_refs": [ { "field": "...", "endpoint": "...", "source": "api-football" } ],
  "known_missing_or_unverified": [ "injuries: 0 results (source required)", "xG: not ingested", "recent form / Elo: not ingested" ],
  "product_goal": "帮助用户理解模型怎么看、哪些风险被验证、下一场该看什么"
}
```

## Output (LLM → engineering) — JSON only
```jsonc
{
  "hero_title": "",          // customer headline — the answer, NOT "MISS"/"ScoutScore replay"
  "hero_subtitle": "",       // one-line customer subtitle
  "model_judgement": "",     // "Giành Cup AI 怎么看" — the model's read, customer voice
  "validated_signals": [     // risks the model flagged that the match confirmed
    { "name": "", "text": "", "source_refs": [ {"field":"","endpoint":""} ], "assumption_flag": false }
  ],
  "underweighted_signals": [ // factors the model under-weighted / blind spots that landed
    { "name": "", "text": "", "source_refs": [ ... ], "assumption_flag": false }
  ],
  "customer_takeaway": "",   // what the user should watch next in a clearly-mismatched fixture
  "operator_copy": "",       // group-broadcast copy: strong, screenshot-able, not a research report
  "cta_copy": "",            // compliant continuation CTA text (no payment/Token)
  "internal_notes": [],      // historical_replay / MISS / missing_evidence — INTERNAL ONLY
  "source_ref_map": {},      // map of each customer field/signal -> its source_refs (traceability)
  "llm_provider": "deepseek",// "deepseek" | "gemini" | "mock"
  "model": "",               // model id used
  "language": "zh-CN",
  "generated_at": ""         // ISO8601 (stamped by the generator, not the model)
}
```

## Requirements
1. **JSON only.** No markdown, no prose, no code fences around the object.
2. **Customer-facing fields** (`hero_title`, `hero_subtitle`, `model_judgement`, `validated_signals[].text`,
   `underweighted_signals[].text`, `customer_takeaway`, `operator_copy`, `cta_copy`) MUST NOT contain engineering /
   audit words: **no** `MISS`, `historical replay`, `source required`, `assumption`, `replay_only`, `data_status`,
   field names, or `%` win-rate / probability.
3. **`internal_notes`** MAY (and should) keep `historical_replay`, the `MISS` accountability, `missing_evidence`,
   and `source_refs` — these are the engineering/compliance truth, shown only in the collapsed internal block.
4. **Every conclusion** in `validated_signals` / `underweighted_signals` carries `source_refs` (real) OR
   `assumption_flag: true` (when not source-backed). `source_ref_map` ties customer fields back to evidence.
5. **No fabrication.** Injuries / xG / suspensions may only be referenced as *not available / to watch next*
   (from `known_missing_or_unverified`); never assert "no injuries" or invent xG.
6. **Compliance:** no betting / odds / 盘口 / 竞猜 / 投注; no guarantee words (稳赢/稳赚/必中/包赢); no fake archived
   prediction. The single mandatory disclaimer is rendered by the page (not required in the JSON).
7. **Language:** `vi-VN` output has **zero Han characters**; mm → English. Team names / AI / xG / Elo / MTC may stay Latin.
8. **Engineering must not substitute its own template for the LLM output.** mock is allowed ONLY as a marked
   fallback (`llm_provider: "mock"`), used when the provider is unavailable or the guard fails.

## Consumers
- Generator: `scripts/mvp2_generate_scoutscore_narrative.py` → `docs/data_audit/mvp2_llm_narratives/{id}.{lang}.{provider}.json`.
- Guard: `scripts/check_mvp2_llm_narrative_guard.py` (must PASS before a narrative reaches a page).
- Pages: `/recap/:fixtureId`, `/evidence/:fixtureId` render the customer fields; `internal_notes`/`source_ref_map` go to the internal block.
