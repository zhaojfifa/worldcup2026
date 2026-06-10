# MVP-2 — Product Voice Guide (Customer / Operator / Internal)

> **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Status:** authoritative voice spec for the Evidence Board v2 / recap surface.
> **Context:** EBv2 engineering structure PASSED but customer-facing copy FAILED (see
> [MVP2_EVIDENCE_BOARD_V2_OPERATOR_REVIEW](MVP2_EVIDENCE_BOARD_V2_OPERATOR_REVIEW.md) §Owner Product Voice Review).
> This guide defines the three voices so the surface speaks to a **customer**, not to a reviewer.

The product gives an **AI judgement + post-match read**, not a model self-audit. The same fixture data is
expressed three ways depending on **where** it appears.

---

## 1. Customer Voice — the main view
**Principles**
- 少说过程，多给判断。 (Less process, more judgement.)
- 少说缺口，多给风险解释。 (Less "what we lack", more risk explanation.)
- 少说合规，多给可信感。 (Less compliance self-proof, more credibility.)

**Rewrite table (do NOT say → say):**
| ❌ engineering / audit | ✅ customer |
|---|---|
| MISS / 判定未命中 | 赛后验证：原始强弱判断被门将与效率变量改写 |
| historical replay / not real archived prediction (作为标题) | 小字或折叠的回放声明，不压主视觉 |
| injuries source required | 首发完整性是赛前 30 分钟重点关注项 |
| no xG / xG not ingested | 机会质量仍需持续跟踪 |
| assumption / replay_only / data_status | 已验证 / 需赛前重点关注 / 赛后影响明显 / 后续模型需(重新)加权 |
| 数据缺口 (deficit) | 下一版 AI 需重点补强的变量 (forward) |

**Where it renders:** first screen (title · subtitle · 4 cards = AI 赛前倾向 / 赛后验证 / 关键结论 / 用户价值),
the "AI 怎么看这场" lead paragraph, the 3 decisive factor cards, the real-evidence grid, the next-variables block.
**Confidence:** tier words only — **no probability / %, no win-rate.** **Guarantee words are forbidden even in a
negation** (no 稳赢 / 稳赚 / 必中 / 包赢); say "控球占优不等于一定能赢" instead.

## 2. Operator Voice — group-broadcast copy
**Principles:** 标题强 · 一句话抓人 · 三个因素解释结果 · 可截图 · 可发群 · 不像研究报告。
**Example (shipped, de-charged):**
> "这场爆冷给我们的启发很直接：强队控球不等于一定能赢。Argentina 控球占优，但 Saudi Arabia 靠门将表现、
> 射门效率和下半场反超改变比赛。我们的 AI 复盘重点不是事后解释比分，而是把这些风险因子沉淀到下一次赛前判断里。"

> ⚠ The Owner's draft used "稳赢"; shipped copy replaces it with "不等于一定能赢" — the compliance floor
> (no guarantee-of-winning wording) is non-negotiable, even inside a warning sentence.

## 3. Internal Voice — collapsed fold only
Lives in the `<details>` internal block (never a customer headline, never a selling point):
`source_refs` · `missing_evidence` (injuries unresolved / xG not ingested / form) · `historical_replay` ·
the MISS accountability statement · AI boundary (allowed vs forbidden fields) · `guardrails` / 禁词检查 ·
raw Scout Pack pointer · source ledger (raw endpoints).

## 4. Voice map for `/evidence/855737`
| Surface | Voice |
|---|---|
| Hero title + subtitle | Customer |
| Small replay note | Customer (minimal) |
| 4 first-screen cards + lead paragraph | Customer |
| 3 decisive factor cards (expanded) | Customer |
| "更多因子" (folded) | Customer |
| Real evidence grid | Customer (credibility) |
| "下一版 AI 需重点补强的变量" | Customer (forward) |
| "运营可发文案" box | Operator |
| "内部资料 / 数据来源" (collapsed) | Internal |
| Bottom disclaimer | Compliance (single line) |

## 5. Compliance placement
Compliance is enforced in **guard checks** (build-time forbidden/Han/vendor scans) and **internal docs**, plus the
**single bottom disclaimer** ("历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。"). It is **not** a customer
selling point — never headline "no betting / no odds / no fake probability / no SHAP". They stay true in the
guardrails and the internal fold, invisible to the customer main view.

## Localization
Every customer/operator string ships zh + vi (+ en fallback). **vi Han = 0** (runtime-verified); mm → English,
never Chinese. Team names / AI / MTC / xG / Elo / MISS(internal only) may stay Latin in vi/mm.

## Guardrails honored (this doc)
spec only · no runtime in this file · customer voice ≠ audit voice · compliance not a selling point ·
guarantee words banned · vi Han=0 rule · operation paused · PR #3 Draft.
