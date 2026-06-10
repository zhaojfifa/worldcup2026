# MVP-2 — LLM Narrative Architecture

> **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) · **Status:** design baseline.
> **Principle:** **Engineering builds the stage. The LLM writes the football intelligence.**
> Product defines flow / structure / boundaries; the **model** does the reasoning, content organization, and
> expression. Engineering must NOT hand-write the narrative or string-concatenate football analysis.

Five layers. Each owns a clear contract; the narrative crosses from data → factors → **LLM** → guard → render.

---

## 1. Data Layer (engineering)
Real, provenance-tagged inputs only. No invented values.
- **API-FOOTBALL** (server-side; key server-only; frontend never calls the vendor).
- **Scout Pack JSON** — `docs/data_audit/mvp2_scout_pack_samples/{id}.json` (redacted/bounded).
- **source_ledger** — every field's `{field, endpoint, source}`.
- **missing_evidence** — honest gaps (injuries unresolved, xG not ingested, recent form / Elo).

## 2. Factor Layer (engineering)
Rule-based scoring + validation; no narrative here.
- **ScoutScore v0.1 / v0.2 factors** — `docs/data_audit/mvp2_scoutscore_v0/{id}.factor_scores.json`.
- **decisive factors** — post-match-validated as result-deciding (keeper / finishing / momentum for 855737).
- **underweighted factors** — pre-match under-weighted / blind spots that landed.
- **verified signals** — observed, source-backed.
- **risk signals** — what the model should watch pre-match next time.

## 3. LLM Narrative Layer (the model — DeepSeek / Gemini)
**This is where the product narrative is created.** Engineering only assembles the input and parses the output.
- **Providers:** DeepSeek (primary), Gemini (benchmark). Kimi excluded (leaks Chinese for vi/mm — see prior comparison).
- **prompt contract** — `docs/prompts/mvp2_scoutscore_narrative_{zh,vi}.md`.
- **structured JSON output** — per `MVP2_LLM_NARRATIVE_CONTRACT.md` (JSON only, no prose wrapper).
- **zh / vi generation** — separate generation per language; **vi Han = 0**; mm → English (never Chinese).
- **operator copy generation** + **customer judgement generation** — produced by the model, not engineering.

## 4. Guard Layer (engineering)
Output is rejected from the page unless it passes `scripts/check_mvp2_llm_narrative_guard.py`:
- no betting / odds / 盘口 / 竞猜 / 投注 · no guarantee words (稳赢 / 稳赚 / 必中 / 包赢)
- no fake probability / win-rate / `%` judgement · no fake archived prediction
- no unsupported injuries / xG claims (only what `source_refs` / `known_missing_or_unverified` support)
- **no "source required" / "MISS" / "historical replay" wording in customer-facing fields** (those belong in `internal_notes`)
- **vi Han = 0**
- **every conclusion carries `source_refs` or an `assumption_flag`**
- output JSON schema valid (all required fields, correct types)

## 5. Rendering Layer (engineering)
- **Pages:** `/recap/:fixtureId`, `/evidence/:fixtureId`.
- Main view renders the **LLM narrative JSON** fields only (`hero_title`, `hero_subtitle`, `model_judgement`,
  `validated_signals`, `underweighted_signals`, `customer_takeaway`, `operator_copy`, `cta_copy`).
- `internal_notes` + `source_ref_map` + raw Scout Pack / ledger stay in the **collapsed internal block**.
- **Deterministic engineering copy is a FALLBACK only** — used when the LLM is unavailable or the guard fails,
  and the surface is marked `llm_provider=mock`. It must never be the default path.

---

## Data flow
```text
API-FOOTBALL ─▶ Scout Pack + source_ledger + missing_evidence            (Data Layer · engineering)
            ─▶ ScoutScore factors (decisive / underweighted / verified / risk)   (Factor Layer · engineering)
            ─▶ LLM input JSON  ── prompt ──▶ DeepSeek/Gemini ──▶ narrative JSON   (LLM Layer · model)
            ─▶ guard checks (forbidden / vi Han=0 / source_refs|assumption / schema)   (Guard Layer · engineering)
            ─▶ /recap + /evidence main view (LLM JSON) · internal block (notes/ledger)   (Render Layer · engineering)
            ─▶ fallback: deterministic copy ONLY if LLM unavailable/guard-fail, marked llm_provider=mock
```

## Boundaries (this phase)
internal LLM generation support only · no public launch · no payment/Token · no 979139 / TheSports / second-source
injuries · frontend never calls the vendor or the LLM directly · no token / raw payload committed · PR #3 Draft.
