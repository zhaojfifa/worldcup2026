# LLM Prep — Schema & Guardrails (Harness-X · P-flow Prep, NOT production)

_Created 2026-06-08 · **Design only.** No LLM is wired to production by this document.
LLM Full Build remains Owner-gated._

## 1. Input / boundary
Design the output schema + guardrails so a future LLM explanation layer can be added safely.
**Not allowed this phase:** LLM production calls, auto-publish, payment, API shape change,
DB schema expansion (unless Owner approves). `AI_PROVIDER` stays `mock`.

## 2. Output field schema (target contract)
LLM (or rules) fills these; the frontend already consumes the rules equivalents today, so the
swap stays non-breaking. All fields are **localizable (zh/vi/mm + en fallback)**.

```jsonc
{
  "match_id": 1,
  "locale": "vi",                  // zh | vi | mm | en
  "reason_bullets": ["...", "..."],// 2-3 short bullets, AI-viewpoint framing
  "social_copy": "…",              // short push text for Zalo/Telegram
  "recap_copy": "…",               // post-match review (only after real result)
  "risk_copy": "…",                // risk note, viewpoint not guarantee
  "provenance": "rules|llm",       // for credibility marker
  "data_mode": "mock|real",        // mirrors data-source/status
  "disclaimer_required": true
}
```

## 3. Guardrails (must all pass before any generated text reaches users)
1. **Banned-word output filter** (post-generation, per locale):
   - zh: 下注/稳赚/必中/跟单/购彩/回报率/返奖/收益承诺/现金奖池/包赢/必赢/投注; `提现` only in `不可提现`.
   - vi: chắc thắng / đảm bảo thắng / cá cược / đặt cược / kiếm tiền / lợi nhuận chắc chắn
     (negation "Không phải dịch vụ cá cược" allowed).
   - mm: လောင်းကစား only in negation (မဟုတ်/မချိတ်).
   - en: betting / guaranteed win / sure win / wager / cash prize / withdraw (except "non-withdrawable").
2. **AI-viewpoint framing enforced** — reject "guaranteed/必中/sure win/chắc thắng" style outputs.
3. **No real hit-rate** unless `data_mode=real` AND `performance.hit_rate != null`.
4. **vi/mm fallback = English, never Chinese** (mirrors UI policy).
5. **Human review queue** — generated copy is staged, not auto-published; operator approves.
6. **Disclaimer auto-appended** where 战绩/命中/连胜 appears.
7. **MTC wording** stays platform-points-only.

## 4. Pipeline (future)
`rules baseline → (optional) LLM enrich → banned-word filter → human review queue → publish`.
Filter + review are mandatory gates; either failing blocks publish.

## 5. LLM Full-Build entry gate (Owner-gated)
- ≥1 real small-traffic trial completed (vi and/or mm).
- ≥1 active social channel (Telegram active ✓; Zalo pending).
- Human feedback samples collected.
- Banned-word filter implemented + tested across zh/vi/mm/en.
- Owner approval recorded.

## 6. Verdict
**PASS (prep)** — schema + guardrail spec defined; no production code. Awaiting Owner gate for build.

## 7. Next Owner decision needed?
**Yes (later):** approve LLM Full Build only after the entry gate is met. Not now.
