# MVP-2 — Evidence Board v2 Design (Closed)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) ·
> **Status:** **CLOSED design — gate-ready.** This document is the executable design baseline for an Evidence
> Board v2; the boundary freeze lives in
> [MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT](MVP2_EVIDENCE_BOARD_V2_GATE_SPEC_DRAFT.md).
> **Implementation status (2026-06-10): minimal implementation SHIPPED to the branch under Owner GO (Path A)** —
> additive `/evidence/855737` (zh/vi, vi Han=0); factor + evidence + missing-data + AI-boundary cards; tier+stars (no %);
> ledger/raw collapsed; bundled-only; recap entry link; homepage untouched. Review PASS WITH ISSUES (internal) —
> see [MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2](MVP2_USER_REVIEW_REPORT_EVIDENCE_BOARD_V2.md). Operation paused,
> PR #3 Draft, operator real-device review pending. This design doc remains the baseline for any further v2 work.
> Builds on ScoutScore v0.1 ([MVP2_SCOUTSCORE_V0_MODEL_CARD](MVP2_SCOUTSCORE_V0_MODEL_CARD.md)), the recap flow,
> and the accepted User Review ([MVP2_USER_REVIEW_REPORT_855737](MVP2_USER_REVIEW_REPORT_855737.md), PASS WITH ISSUES).

No code, no API change, no DB change, no public launch in this document.

---

## 1. v2 产品目标 (product goals)
- **闭环:** 把「当前预测」和「历史复盘」连成一个回路——AI 这样判断 → 它过去对/错在哪 → 它如何修正 → 回到当前判断。
- **证明不是泛泛 AI 文案:** 每条客户结论都挂证据卡 + `source_ledger`,或诚实标为缺口。
- **展示三件事:** 数据证据(真实统计)、模型因素(ScoutScore 因子)、缺失边界(injuries/xG/Elo 未接入)。
- 定位仍是 **AI 足球情报社区**(非博彩、不承诺命中/收益)。

## 2. v2 核心页面 (core pages)
| # | page | 一句话用途 | 复用 |
|---|---|---|---|
| 1 | **首页 AI 倾向卡** | 当前比赛的 AI 倾向 + 信心档位(非百分比),一眼可读 | 现有首页信号/简表(主逻辑不改) |
| 2 | **AI 观点详情** | 单场:AI 倾向 + 模型因素 + 证据卡 + 风险 + 缺失边界 | 现有 `/detail` 升级 |
| 3 | **历史复盘列表** | 已产品化复盘 + "复盘生成中" 的历史场次入口(无死胡同) | 首页历史复盘模块 + 复盘页"更多历史复盘" |
| 4 | **复盘详情** | 单场赛后问责:模型回放 vs 实际 → 命中/失误 → 修正 + 运营文案 | 现有 `/recap/:fixtureId`(已上线 mock) |
| 5 | **Evidence Board** | 把"模型因素卡 + 证据来源卡 + 缺失边界"做成一个统一的证据面板(预测页与复盘页共用) | 新 |
| 6 | **AI boundary / missing data** | AI 可解释 vs 禁止解释字段 + 缺失数据(injuries source required) | 现有复盘页 AI 边界块 |

## 3. v2 信息架构 (information architecture)
- **用户第一眼看什么:** 客户语言的「一句话结论 / AI 倾向」+ 信心档位;**不先给大表格**。
- **运营截图区域:** ① 强标题/AI 倾向卡;② 证据卡(控球/射门/门将);③(复盘)MISS 徽章 + 运营文案。这三块是固定的"可截图带"。
- **source ledger 放哪里:** 始终保留,但**折叠**在页面底部(`<details>`),不作为主视图。
- **raw data 是否折叠:** 是。原始 Scout Pack 折叠;主视图只放客户可读卡片。
- **zh / vi 如何切换:** 复用现有 `?lang=` + 顶栏 `CN · VI · MY`;**vi Han=0**,mm 回退英文(永不中文);所有动态值走 viMapping/英文 fallback。

## 4. v2 数据合同 (data contract)
所有数据经**后端**提供(前端不直连 vendor);每条结论挂 `source_refs` 或标 `assumption`。

| 数据 | 来源 / 产物 | 用途 |
|---|---|---|
| **ScoutScore v0.1** | `backend/app/services/scoutscore/*` | 因子评分 + 推理(模板/mock 回退;DeepSeek/Gemini draft-only,待 Render) |
| **prediction replay / accountability** | `docs/data_audit/mvp2_prediction_replay/*`, `mvp2_prediction_accountability_reports/*`;`GET /api/v1/recap/{id}` | 复盘详情(回放→命中/失误→修正) |
| **feature snapshot** | `docs/data_audit/mvp2_feature_snapshots/*` | 观测特征(覆盖度、差值、门将评分等) |
| **source_refs** | 各产物内嵌 | 每条结论的可追溯证据 |
| **missing_evidence** | Scout Pack / 报告内嵌 | 缺口卡(injuries source required、xG not ingested) |
| **ai_allowed / ai_forbidden** | Scout Pack / accountability 内嵌 | AI 边界卡 |
| **future(Owner-gated):** injuries(P0)/xG(P1)/Elo·form(P1)/squad value(P2) | 见 [MVP2_NEXT_DATA_REQUIREMENTS](MVP2_NEXT_DATA_REQUIREMENTS.md) | 解锁更多卡;未接入前一律诚实缺口 |

## 5. v2 guardrails
- **no betting / odds / market / 盘口 / 竞猜 / 投注** anywhere.
- **no fake probability**(信心用档位 + 星级,**不用百分比 / 命中率**)。
- **no fake archived prediction**(历史内容标 `historical_replay`,绝不写"赛前命中")。
- **no SHAP** · **no xG** unless a licensed source is ingested · **injuries = source required**(不推断缺阵)。
- **public operation paused**;vi Han=0;mm→English。

## 6. v2 不做的事 (out of scope for v2)
- **no payment / no unlock-to-pay** · **no Token / on-chain** · **no production public launch**.
- **no live prediction claim**(无临场胜率/走地信号)。
- **no second-source injuries integration yet**(P0 数据待 Owner GO)。
- no real LLM auto-publish(DeepSeek/Gemini 保持 draft-only + 禁词过滤 + 人审)。
- no XGBoost/LightGBM 训练(backbone 预留)。

---

## Owner Open Questions — Proposed Answers
**Q1. 置信度怎么表达？**
建议:短期**只用档位词 + 星级,不用百分比**。示例:`AI 倾向：主胜偏强` · `信心档位：低 / 中 / 高` · `★★★☆☆`。
**禁止** `49%` / `42.2%` / 命中率承诺。(vi 等价:`Xu hướng AI: nghiêng chủ nhà` · `Mức tin cậy: thấp/trung bình/cao` · 星级。)

**Q2. V2 前是否先产品化另外 3 场？**
建议:**先不全部产品化**。以 **855737** 为主样例;另外 3 场(855741/977345/979139)在"更多历史复盘"显示为「数据已接入 / 复盘生成中」。
若 Owner 要演示完整矩阵,**再选 1 场不同类型补做:979139(决赛 3–3 拉锯)**——与 855737 的"控球碾压却输"形成对比类型。

**Q3. continuation CTA 落点？**
建议:**短期回首页「今日 AI 观点」区**(现状,无付费);**中期设计独立「AI 观点详情页」**(core page #2)作为落点;**始终不接付费流**。

---

## Gate readiness
- 设计已收口为可执行基线;边界冻结见 Gate Spec Draft。
- **进入实现前需 Owner GO**(Gate Spec 的 acceptance criteria + rollback 已列)。

## Guardrails honored (this doc)
design only · no implementation · no API/DB change · no payment/token/public · odds/betting excluded ·
historical-replay framing · injuries source-required · external operation paused · PR #2 untouched · PR #3 Draft.
