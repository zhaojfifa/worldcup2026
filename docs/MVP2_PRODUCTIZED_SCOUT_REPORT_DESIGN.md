# MVP-2 — Productized Scout Report Design

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Mode:** implementation (backend transform + internal preview; **no public surface, no frontend change**).
> Purpose: define how raw API-FOOTBALL Level-2 data becomes an **operator-readable product report**, proving
> `data → features → model notes → scout report → zh/vi content → operator review → data gap list`.

This is **not** a prediction product. It is a **post-match explanation** product built only from data that
already exists. Reference fixture: **855737 — Argentina 1–2 Saudi Arabia** (a textbook upset).

## Pipeline & files
```
scout pack (real)          backend/app/services/scout_pack/builder.py  → docs/data_audit/mvp2_scout_pack_samples/<fid>.json
  → feature snapshot       backend/app/services/scout_pack/features.py → docs/data_audit/mvp2_feature_snapshots/<fid>.json
  → model notes            backend/app/services/scout_pack/model_notes.py → docs/data_audit/mvp2_model_notes/<fid>.json
  → productized report     backend/app/services/scout_pack/report.py   → docs/data_audit/mvp2_productized_reports/<fid>.{zh-CN,vi-VN}.json
  → operator preview       backend/app/routers/internal_scout_pack.py  (GET /internal/scout-pack, report-first)
build script: backend/scripts/mvp2_build_productized_report.py (pure offline transform — no API calls)
```

## Global rules (every module)
- **No fabrication.** Every conclusion cites `source_refs` back to a real pack field + endpoint.
- **Forbidden everywhere:** win probability · odds / betting / market / 盘口 / 竞猜 / 走地 / 滚球 / 大小球 / 让球 ·
  SHAP / feature-importance · xG values · injury/absence impact · `42.2%`.
- **injuries = source required** (never "no injuries"). **xG = not used** this round (may be stated as absent).
- **vi output = 0 Han** (Latin only); zh = internal management language; en = fallback.
- Mandatory disclaimer on recap content: 历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。

---

## Module structure (9)

### 1. Match Verdict / 比赛结论
- **输入数据:** fixture (teams, final_score, result_winner), team_statistics (possession/shots).
- **输出内容:** one-line plain verdict (e.g. "控球占优却 1–2 不敌 → 典型爆冷").
- **允许写:** what happened (score, who dominated, upset/normal). **禁止写:** prediction, odds, "should have won", luck/xG.
- **source_refs:** team_statistics, fixture.final_score (required).
- **zh/vi:** templated from team names + values; vi 0 Han.

### 2. Why It Happened / 结果原因
- **输入:** events (goal timeline), team_statistics, player_statistics (goalkeeper).
- **输出:** 3–4 narrative points (goal sequence, second-half turnaround, possession/shots contradiction, goalkeeper).
- **允许写:** observed sequence + observed stat gaps. **禁止写:** "因为伤停", xG/luck, betting reasoning.
- **source_refs:** per point (events / team_statistics / player_statistics). **required per point.**
- **zh/vi:** localized; values inline.

### 3. Evidence Board / 证据板
- **输入:** team_statistics, player_statistics, events.
- **输出:** factual cards (possession, total shots, shots on goal, pass accuracy, GK rating, GK saves, goal timeline) shown as home / away.
- **允许写:** raw verified values only. **禁止写:** derived/predicted values, xG, odds.
- **source_refs:** per card (required).
- **zh/vi:** card titles localized; numbers are language-neutral.

### 4. Feature Snapshot / 特征快照
- **输入:** the whole pack.
- **输出:** observed features (availability flags, goal_timeline, lead_change, second_half_turnaround, event_density, card/sub counts, shot/SoG/possession/pass-accuracy differences, top_player_rating, goalkeeper_rating, data_coverage_score, missing_injuries, missing_xg).
- **允许写:** observed/derived-from-real-data only. **禁止写:** win probability, betting signal, odds, SHAP, xG, injury/absence impact.
- **source_refs:** `derived_from` endpoints; each summary item references a field.
- **zh/vi:** labels localized; values neutral. Carries a "not a prediction / not a financial signal" disclaimer.

### 5. Model Notes / 模型解释笔记
- **输入:** feature snapshot + pack. `model_type = post_match_explanation_v0`, `is_prediction = false`.
- **输出:** explanation **signals** (upset_case, second_half_turnaround, possession_result_contradiction, shot_efficiency_gap, event_turning_point, goalkeeper_impact_observed, data_coverage_sufficient, injuries_missing) + `allowed_conclusions` + `forbidden_conclusions`.
- **允许写:** post-match explanation with evidence. **禁止写:** pre-match prediction, win probability, odds, SHAP, xG, injury impact, betting advice.
- **source_refs:** **required per signal.**
- **zh/vi:** signal name = ASCII key; interpretation localized.

### 6. Content Draft / 可运营文案
- **输入:** verdict + key evidence + goal timeline.
- **输出:** a short, shareable operator post (zh-CN.json / vi-VN.json), ending with the mandatory disclaimer.
- **允许写:** factual recap + "数据-结果背离" framing + disclaimer. **禁止写:** betting/odds/竞猜, "稳/必中", profit, injury impact, xG.
- **source_refs:** fixture + events + team_statistics (required).
- **zh/vi:** two separate localized drafts; vi 0 Han, no betting wording.

### 7. Missing Data / 缺失数据
- **输入:** missing_evidence + policy (xG not ingested).
- **输出:** explicit gap list (injuries unresolved; xG not ingested).
- **允许写:** "source required" / "not ingested". **禁止写:** "no injuries", inferred impact.
- **source_refs:** injuries → source_ledger (results=0).
- **zh/vi:** localized.

### 8. Next Data Needed / 下一步数据需求
- **输入:** the gap list + product goals.
- **输出:** prioritized data needs (injuries, xG) with purpose, pointing to `MVP2_NEXT_DATA_REQUIREMENTS.md`.
- **允许写:** what data unlocks which explanation. **禁止写:** committing to a vendor/price/launch.
- **source_refs:** ref to the requirements doc.
- **zh/vi:** localized item + purpose.

### 9. AI Boundary / AI 解释边界
- **输入:** pack `ai_allowed_explanations` / `ai_forbidden_explanations`.
- **输出:** allowed fields (verified) vs forbidden fields (injuries, financial/profit, prediction, etc.) + "AI 仅可解释已验证字段".
- **允许写:** the boundary itself. **禁止写:** anything outside the allowed fields.
- **source_refs:** the source_ledger backs the allowed set.
- **zh/vi:** localized note; field keys ASCII.

---

## Preview rendering (operator-first)
`GET /internal/scout-pack?fixture_id=855737&lang=zh|vi` renders, in order: **(1) 情报摘要 → (2) 结果原因 →
(3) 关键证据卡 → (3.5) 特征快照 → (4) 模型解释笔记 → (5) 可运营文案草稿 → (6) 缺失数据 → (7) 下一步需要的数据
→ (8) AI 边界 → (9) 原始 Scout Pack(折叠) → (10) Source Ledger(折叠)**. First screen is readable prose,
not a table; raw data + ledger are retained but collapsed. `noindex`, not in public nav, admin-token gated in
production, `public_ready=false`, `operation_status=paused`.

## Guardrails honored
backend transform + internal preview only · no frontend change · no public surface · every conclusion has
source_refs · no prediction/odds/market/SHAP/xG/injury-inference · vi 0 Han · external operation paused · PR #2 untouched.
