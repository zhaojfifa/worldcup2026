# MVP-2 — LLM-Driven Product Proof Sprint (Plan)

> **Date:** 2026-06-11 · **Owner ruling:** 进入重型工程。Engineering builds the stage; **the LLM writes
> the football intelligence.** · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3 stays **Draft**).
> This sprint answers the 2026-06-10 Owner verdict that the v1 narrative read like post-match journalism:
> the fix is **prediction-first-principles prompt + product contract v2 + product guard**, proven on
> **three real product samples** (2 historical recaps + 1 pre-match 2026 modeling sample).

---

## 0. Goal — three product samples, one product pipeline

| # | Sample | fixture | Mode | Theme |
|---|--------|---------|------|-------|
| A | 历史复盘 · 爆冷 | `855737` Argentina 1–2 Saudi Arabia (WC2022) | `historical_recap` | 模型如何识别强队风险 |
| B | 历史复盘 · 决赛拉锯 | `979139` Argentina 3–3 France (WC2022 final, pens) | `historical_recap` | 强强对话：动量、门将、球星、点球风险 |
| C | 2026 赛前建模 | `2026_brazil_argentina` Brazil vs Argentina | `pre_match_2026_modeling` | ScoutScore 胜平负倾向、比分区间、风险、临场 30 分钟更新、订阅钩子 |

(B fallback if 979139 data unavailable: 855741 Germany 1–2 Japan — **not needed**, 979139 Scout Pack is ingested.)

Unified pipeline (every sample flows through all stages):

```
Data (Scout Pack / Kaggle baseline / assumption_context)
→ ScoutScore v0.2 factor frame            (engineering, real refs + flagged assumptions)
→ LLM input JSON                          (engineering assembles; no hand-written intelligence)
→ DeepSeek / Gemini product narrative     (the LLM writes ALL football intelligence + ops copy)
→ product narrative guard                 (engineering gate)
→ /recap/:id + /predict/:slug pages       (engineering renders the LLM JSON — no template main path)
→ operator copy + subscription / group CTA (LLM-written, page-framed)
→ review report                           (docs/MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md)
```

## 1. Hard rules (Owner)

Engineering MAY build: ingestion, cleaning, Scout Pack, source_ledger, factor extraction, LLM input
JSON, prompt contract, guard, cache/fallback, page rendering.

Engineering MUST NOT hand-write: AI 怎么看 / 用户价值 / 运营文案 / 模型复盘 / 比赛判断 / 风险解释 /
订阅转化话术. Those are **LLM output only**. Mock fallback allowed only as marked `llm_provider: "mock"`;
DeepSeek/Gemini keys exist locally → real calls are the default.

Forbidden this sprint: mark PR ready · merge · public operation · payment/Token runtime · TheSports
runtime · betting/odds/盘口/投注建议 · passing LLM assumptions off as real data · frontend calling the
LLM/vendor directly · committing tokens or raw payloads · engineering-template copy as the main path.

## 2. Roles (one Claude, five hats — outputs kept separate)

- **A Product Architect** — page paths + free/full split + CTA placement (§5, §6).
- **B Data Engineer** — Scout Packs (855737/979139), Kaggle baseline (Elo / recent form / H2H),
  assumption_context flags (§3).
- **C Model Designer** — ScoutScore v0.2 factor frame (`MVP2_SCOUTSCORE_V0_2_MODELING_FRAME.md`).
- **D LLM Narrative Architect** — product narrative contract v2 + zh/vi prompts
  (`docs/prompts/mvp2_scoutscore_product_narrative_{zh,vi}.md`).
- **E Growth Operator** — growth fields inside the same LLM contract (short_title / screenshot_line /
  social_post / subscription_hook / group_join_copy / today_cta). Engineering only frames them.

## 3. Data source matrix

### Available now (real, source_ref-backed)
| Source | Use | Provenance |
|---|---|---|
| API-FOOTBALL Scout Packs `docs/data_audit/mvp2_scout_pack_samples/{855737,979139}.json` | lineups, formation, coach, events timeline, team/player statistics, squad | `source_ledger` per field |
| `data/external/kaggle/results.csv` (49k internationals, **through 2026-06**, untracked raw) | derived Elo-like baseline_strength, recent_form (last 10), H2H Brazil–Argentina | `kaggle_intl_results · derived` |
| `data/external/kaggle/shootouts.csv` | 979139 shootout outcome; pens-risk context | `kaggle_intl_results` |
| `data/external/kaggle/goalscorers.csv` | recent scorers per team (form texture) | `kaggle_intl_results` |
| Existing ScoutScore v0.1 + accountability artifacts (855737) | replay verdict continuity | docs/data_audit |

### Missing → LLM `assumption_context` (flagged, never dressed as real data)
Elo official/FIFA rank (we use Kaggle-derived instead) · Transfermarkt squad value · FBref/xG ·
injuries/suspensions · 2026 venue/travel/altitude/climate specifics · live 30-min lineup changes ·
2026 Brazil–Argentina is **not a scheduled fixture** (both are in groups; a meeting is a hypothetical
knockout scenario — the sample says so internally, the customer view says "若两队在淘汰赛相遇").

Rule: real data → `source_refs`; gaps → `assumption_flag: true` + `assumption_context`; the customer
main view phrases gaps as **赛前需要重点跟踪的变量**, never "we have no data".

## 4. Deliverables

Docs (new): this plan · `MVP2_SCOUTSCORE_V0_2_MODELING_FRAME.md` ·
`MVP2_THREE_SAMPLE_PRODUCT_PROOF_REVIEW.md` · `docs/prompts/mvp2_scoutscore_product_narrative_{zh,vi}.md`.
Docs (updated): `CLAUDE.md` · `MVP_STATUS.md` · `HANDOFF_TO_NEXT_ENGINEERING_CHAT.md` ·
`MVP2_LLM_NARRATIVE_CONTRACT.md` (v2 section) · `MVP2_LLM_NARRATIVE_PROVIDER_REVIEW.md` (3-sample re-run).

Scripts: `scripts/mvp2_build_scoutscore_v0_2_factors.py` (factor frames) ·
`scripts/mvp2_generate_product_proof_narratives.py` (3 × zh/vi × DeepSeek real + Gemini benchmark →
`docs/data_audit/mvp2_product_proof_narratives/`) · `scripts/check_mvp2_product_narrative_guard.py`.

Pages: `/recap/855737` · `/recap/979139` · `/predict/2026-brazil-argentina` render the **LLM narrative
JSON** as the main view (evidence pages optional). Screenshots → `docs/qa_screenshots/mvp2_product_proof/`.

## 5. Page structure (Product Architect)

**Recap** (§ trust-building): 强标题 → ScoutScore 怎么判断 → 模型抓对了什么 → 模型低估了什么 →
决定性因子 → 数据证据 → 下次该盯什么 → 完整分析入群 CTA → 更多复盘 / 今日 AI 观点 CTA → 内部来源折叠.

**Predict 2026** (§ subscription motive): 强标题 → AI 倾向 → 推荐比分区间 → 风险评级 → 关键因子 →
临场 30 分钟会重新计算什么 → 免费版可见内容 → 完整分析入群 / 订阅 CTA → 模型依据折叠 → disclaimer.

Free vs full: recap 全文免费（信任资产）；predict 免费层 = 倾向 + 风险评级 + 部分因子；完整因子拆解、
临场 30 分钟更新、比分区间深度解读 = 入群 / 订阅层（本轮只做 CTA 框架，不接支付）。

## 6. Acceptance (report all 16)

1. 两个历史复盘完成 2. 一个 2026 赛前建模样例完成 3. 真实数据源清单 4. assumption_context 清单
5. DeepSeek + Gemini 双生成 6. 默认 provider 推荐 7. narrative guard 通过 8. 页面渲染 LLM narrative
9. 订阅/入群 CTA 在页 10. 无 AI 味 / 无工程审计味 11. zh/vi 截图路径 12. vi Han=0 13. forbidden scan
14. build/test 结果 15. PR #3 仍 Draft 16. operation 仍 paused.

Compliance floor unchanged: 不博彩 · 不现金投注 · 不承诺命中/收益 · MTC 仅平台积分 · 历史表现免责声明。
