# MVP-2 External Expectation Signals — Design (INTERNAL-ONLY signal layer)

> Track A+ Evidence Expansion Sprint, Owner verdict 2026-06-12. Design + stub frame schema.
> Status: **DESIGN + manual-recording stub only.** No scraping runtime, no vendor integration,
> no customer surface, no betting features. PR #3 Draft · operation paused · small private trial only.

## 1. Purpose

API raw data + Elo + form + H2H is too narrow for a strong football-intelligence product. Global
expectation — what media, experts, crowds and markets *collectively price in* — is a real signal a
scout would never ignore. We ingest/record it as an **internal model input only**: it sharpens the
persona's pre-match lean and post-match recap ("热度集中在热门方，冷门变量被低估"), it never becomes
betting advice and never surfaces as odds.

## 2. Policy (hard lines)

| Allowed | Forbidden |
|---|---|
| Recording betting-market consensus as an INTERNAL expectation signal (crowd pricing) | ANY betting feature, advice, recommendation, link-out |
| Customer-safe phrasing: 外部预期 · 市场共识 · 公开预测倾向 · 热度集中在热门方 · 冷门变量被低估 (vi: kỳ vọng bên ngoài / đồng thuận thị trường; my: ပြင်ပမျှော်လင့်ချက်) | Customer-visible: 赔率 · 盘口 · 投注 · 博彩 · bookmaker · odds · handicap · kèo · cửa trên / cửa dưới · လောင်းကစား and equivalents (guard-enforced) |
| Internal fields naming sources for audit (`internal_note`) | Bookmaker names, prices, implied percentages, "value"/profit language anywhere customer-visible |
| Manual operator recording with `recorded_by` + `recorded_at` | Fabricated consensus ("experts say" with no source list) — guard bans unsourced exact claims |

The LLM receives these signals **flagged `internal_only: true`** and the prompt instructs it to
express them only in customer-safe expectation language. The visible-copy scanner + narrative guard
ban the forbidden vocabulary in all four languages (zh/vi/my/en).

## 3. Signals

| signal | what it captures | P0 source (manual) | future source | notes |
|---|---|---|---|---|
| `media_heat` | volume/intensity of mainstream coverage per side | operator 1-5 score + 2-3 headline refs | news API count | headlines listed as refs, never quoted to customers verbatim |
| `expert_consensus` | pundit/analyst lean | operator summary + named sources | curated expert panel feed | must list ≥2 named sources or stays missing |
| `social_buzz` | fan-volume asymmetry | operator 1-5 + platform noted | social API volume | zh/vi/my channels differ — record per region |
| `public_prediction_bias` | which side the public picks | public prediction polls (e.g. broadcaster polls) | poll aggregation | record N and source URL internally |
| `market_expectation` | crowd pricing direction (favourite strength, drift) | operator records direction + magnitude band (strong/moderate/slight favourite, drift toward X) | normalized feed | **direction + band only — NO prices, NO bookmaker names in the frame value**; raw references live in `internal_note` |
| `odds_implied_expectation` | implied win-expectation band derived from market consensus | derived from market_expectation band (e.g. "heavy favourite / moderate / coin-flip") | derived | stored as qualitative band; numeric implied % stays internal_note-only with source |
| `lineup_rumor_signal` | pre-official XI leaks/rumors | operator note + source | beat-reporter feed | feeds T-90 watch; NEVER stated as fact — `rumor` status until /lineups confirms |
| `injury_rumor_signal` | unconfirmed fitness doubts | operator note + source | vendor injury feed (TheSports, still gated) | complements the empty /injuries endpoint; rumor ≠ evidence, always `assumption_flag` |

## 4. Stub frame schema (manual recording)

Path: `docs/data_audit/mvp2_external_signals/{fixture_id}.external_signals.json`

```json
{
  "schema_version": "0.1",
  "fixture_id": "1489371",
  "internal_only": true,
  "policy_ref": "docs/MVP2_EXTERNAL_EXPECTATION_SIGNALS_DESIGN.md#2-policy",
  "recorded_by": null,
  "recorded_at": null,
  "signals": {
    "media_heat":              {"value": null, "scale": "1-5 per side", "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": "manual operator recording — not yet recorded"},
    "expert_consensus":        {"value": null, "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": ">=2 named sources required"},
    "social_buzz":             {"value": null, "scale": "1-5 per side + platform", "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": ""},
    "public_prediction_bias":  {"value": null, "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": "record poll N + URL"},
    "market_expectation":      {"value": null, "allowed_values": ["heavy_favourite_home", "moderate_favourite_home", "slight_favourite_home", "even", "slight_favourite_away", "moderate_favourite_away", "heavy_favourite_away"], "drift": null, "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": "direction+band only; NO prices/bookmaker names in value"},
    "odds_implied_expectation":{"value": null, "derived_from": "market_expectation", "confidence": "none", "missing_evidence": true, "internal_note": "qualitative band only"},
    "lineup_rumor_signal":     {"value": null, "status": "rumor", "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": "rumor until /fixtures/lineups confirms"},
    "injury_rumor_signal":     {"value": null, "status": "rumor", "sources": [], "confidence": "none", "missing_evidence": true, "internal_note": "always assumption_flag in narratives"}
  },
  "customer_safe_vocabulary": ["外部预期", "市场共识", "公开预测倾向", "热度集中在热门方", "冷门变量被低估"],
  "forbidden_customer_vocabulary_ref": "scripts/check_mvp2_product_narrative_guard.py BETTING_BANS"
}
```

Rules:
- Every recorded value carries `sources` + `recorded_by` + `recorded_at`; unrecorded = `missing_evidence: true`. No half-records.
- Frames feed the LLM input as `external_signals` with `internal_only: true`; the prompt maps them to customer-safe phrasing; the guard bans the forbidden vocabulary regardless.
- This file is data_audit (internal). It is never bundled to the frontend.

## 5. Integration points (current sprint = stub only)

1. **Pre-match (A2)**: trial frame may attach `external_signals` when a recorded file exists; signals appear in narratives only as 外部预期/市场共识 framing.
2. **Recap (A4)**: post-match, signals support "热度集中在热门方，冷门变量被低估" style honesty checks (did the crowd see what the persona saw?).
3. **Daily scan (A1)**: scan output may flag fixtures with no recorded signals as an operator TODO. (Not implemented this sprint.)

## 6. Not doing (this sprint and until Owner GO)

No scraping/automation, no vendor odds feed, no numeric odds storage in frames, no customer surface,
no schedule/cron, no Track B coupling. Recording is a manual operator act with named sources.
