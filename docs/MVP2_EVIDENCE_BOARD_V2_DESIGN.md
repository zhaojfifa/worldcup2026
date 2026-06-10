# MVP-2 — Evidence Board v2 (Design Draft)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Mode:** **DESIGN ONLY — not implemented this round.** Follows the User Review (PASS WITH ISSUES) on the
> recap product flow. Goal: connect **current prediction ↔ historical recap ↔ model accountability** into one
> credible, compliant board. Builds on ScoutScore v0.1
> ([MVP2_SCOUTSCORE_V0_MODEL_CARD](MVP2_SCOUTSCORE_V0_MODEL_CARD.md)) and the recap flow
> ([MVP2_USER_REVIEW_REPORT_855737](MVP2_USER_REVIEW_REPORT_855737.md)).

This is a blueprint. No code, no API change, no DB change, no public launch in this document.

---

## 1. 设计目标 (goals)
- Tie the three threads into one story: **"AI 这样判断 (current) → 它过去对/错在哪 (recap) → 它怎么修正 (accountability)"**.
- Make credibility *visible*: every customer claim is backed by an evidence card + `source_ledger`, or shown as
  an honest gap — the same provenance discipline already shipped in the recap.
- Close the three User-Review gaps: (1) no dead-end → recap continuation; (2) no continuation CTA → "back to
  current AI view"; (3) weak current↔historical bridge → an explicit accountability thread on the match board.
- Stay an **AI football-intelligence community** product (not betting, not a results-guarantee).

## 2. 页面模块 (page modules)
Each module is a card with a localized title (zh/vi, vi Han=0) and an `available | source-required` state.

| module | shows | data state rule |
|---|---|---|
| **AI 倾向卡 / AI lean** | model lean + confidence tier (qualitative), no numeric win-probability | always; confidence is a tier, never a % "hit rate" |
| **模型因素卡 / Model factors** | the ScoutScore factor list (direction/weight/observed), each with `source_refs` or `assumption` | factor `missing/replay_only` rendered honestly |
| **证据来源卡 / Evidence cards** | real stats (possession/shots/keeper/events) home/away | `available=false` → "source required" |
| **历史复盘入口 / Recap entry** | link to the match's recap (if productized) or "recap in progress" | never a fake/empty recap |
| **赛后问责报告 / Accountability report** | hit/miss/partial + what right/missed + model correction (post-match only) | only for finished fixtures; historical-replay labelled |
| **缺失数据边界 / Missing-data boundary** | injuries (source required), xG (not ingested), Elo/form (pending) | always visible; never "no injuries" |
| **AI 不可解释边界 / AI boundary** | AI-allowed vs AI-forbidden fields + "verified fields only" | always visible |

The board renders **pre-match modules** for upcoming fixtures and **accountability modules** for finished ones;
both share the evidence/source/boundary cards so the customer sees one consistent provenance language.

## 3. 数据输入 (data inputs)
- **Now:** API-FOOTBALL Level-2 (fixtures/lineups/events/statistics/players/squad/coach) → Scout Pack →
  **ScoutScore v0.1** (rule-based factors + post-match accountability; reasoning layer template/mock, DeepSeek/Gemini
  draft-only pending Render).
- **Future (Owner-gated, see [MVP2_NEXT_DATA_REQUIREMENTS](MVP2_NEXT_DATA_REQUIREMENTS.md)):** injuries (P0),
  xG (P1), Elo/recent form (P1), squad value (P2). Each unlocks specific cards; until ingested they render as
  honest gaps, never fabricated.
- Frontend **never** calls the vendor — all data via the backend (`/api/v1/...`, e.g. the recap proxy).

## 4. 用户路径 (user path)
```
首页预测 (current matches)
  → 查看 AI 观点 (match board: AI lean + factors + evidence)
  → 历史复盘入口 (this team / similar upset)
  → 完整复盘 (accountability report: hit/miss → correction)
  → 回到当前比赛 AI 情报 (continuation CTA, no payment)
```
The loop is intentionally circular: the recap sends the user *back* to the current AI view, reinforcing
"the model that recaps itself is the model worth reading for the next match."

## 5. Guardrails
- **no betting / odds / market / 盘口 / 竞猜 / 投注** anywhere.
- **no fake probability** (confidence is a qualitative tier, not a % hit-rate or win-probability number).
- **no fake archived prediction** — historical content is labelled `historical_replay`; never "we called it".
- **no SHAP / no xG** unless a licensed source is ingested; **injuries = source required** (no absence inference).
- **public operation paused**; this board ships only after Owner sign-off + operator review.
- vi Han = 0; mm → English fallback (never Chinese).

## 6. V2 不做的事 (explicitly out of scope for V2)
- **No payment flow / no unlock-to-pay.** **No Token / on-chain.** **No production public launch.**
- **No live prediction claims** (no "live win-rate", no in-play signals).
- No real LLM auto-publish (DeepSeek/Gemini stay draft-only behind the forbidden filter, human-reviewed).
- No training of the XGBoost/LightGBM backbone (reserved for a later, data-sufficient phase).

## Open questions for Owner (before any V2 build)
1. Confidence representation — tier words only, or a bounded 1–5 star (still not a %)?
2. Recap coverage — productize the other three fixtures (855741/977345/979139) before V2, or design-first?
3. Where the continuation CTA lands — home, or a dedicated "current AI view" surface?

## Guardrails honored (this doc)
design only · no implementation · no API/DB change · no payment/token/public · odds/betting excluded ·
historical-replay framing · injuries source-required · external operation paused · PR #2 untouched · PR #3 Draft.
