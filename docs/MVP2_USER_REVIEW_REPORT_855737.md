# MVP-2 User Review Report — Historical Recap Product Flow (855737)

> **Reviewer role:** User Reviewer / Operator Persona (NOT the developer hat). **Date:** 2026-06-10 ·
> **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) · **Mode:** internal verification (mock,
> operation paused). Subject: **Home → Historical Recap · WC2022 → Argentina vs Saudi Arabia → recap detail**.
> Evidence reviewed: `docs/qa_screenshots/mvp2_historical_recap_product_flow/{home_recap_entry,recap_855737}_{zh,vi}.png`.

I evaluated the actual product path (frontend), not the internal engineering preview. Verdicts are honest —
this is a review, not a sign-off.

---

## A. 普通用户视角 (ordinary football fan) — **PASS WITH ISSUES**
- **第一眼是否知道这场为什么值得看？** ✅ 强标题「这场爆冷不是偶然：ScoutScore 发现传统强弱判断的三个盲区」一眼抓住。
- **是否理解模型原来怎么判断？** ✅「模型回放：偏 Argentina」直白。
- **是否理解结果为什么反转？** ✅ 三个漏项（门将 / 效率 / 下半场动量）+ 证据卡解释清楚。
- **是否相信这不是普通 AI 文案？** ✅ 偏信——真实证据卡（控球 69%/31%、门将 6.0/7.7）+ 可展开的数据来源,明显不是空话；但普通用户不一定会展开 Source Ledger。
- **是否愿意继续看下一场？** ⚠️ **目前只有一场复盘,看完无处可去**（没有"下一场 / 更多复盘"入口）。
- **Verdict: PASS WITH ISSUES** — 单页表达力强,但缺少"看完之后去哪"的延续。

## B. 私域运营视角 (private-domain operator) — **PASS**
- **可截图标题？** ✅ 强标题适合做封面。
- **可发群文案？** ✅「运营可用文案」是一段可直接复制 / 截图的中文,自带免责声明。
- **清楚的爆冷故事？** ✅ 爆冷 + 三盲区,叙事完整。
- **能解释"模型错了但为什么还值得看"？** ✅ 这是最强点——MISS + 「模型升级样本」把"判断未命中"转成"模型在进步"的故事。
- **是否有违规词或投注导向？** ✅ 无（无 betting/odds/盘口/竞猜/投注；"博彩"仅出现在"不做博彩"否定句）。
- **是否适合中文运营？** ✅。 **是否适合越南语运营？** ✅ vi 全页 0 汉字,越南语自然。
- **Verdict: PASS** — 运营可直接拿来讲故事 + 发群,合规。这是本轮最成立的视角。

## C. 付费前用户视角 (pre-paid user) — **PASS WITH ISSUES**
- **完整分析是否比免费 AI 文案更有价值？** ✅ 偏信——因子级解释 + 真实证据 + 下版修正,比泛泛文案更"像有方法论"。
- **是否看到数据证据？** ✅ 证据卡 + Source Ledger。
- **是否看到模型修正能力？** ✅「下版模型修正」清楚。
- **是否愿意点击"查看完整分析"或继续看历史复盘？** ⚠️ **复盘页没有任何"解锁/查看更多"CTA**——内容一次给全,付费前用户没有"下一步"的钩子,也没有从复盘桥接到"当前比赛付费分析"。
- **Verdict: PASS WITH ISSUES** — 内容有说服力,但缺少把"复盘可信度"转化为"付费意愿"的衔接 CTA。

## D. 产品流程视角 (product flow) — **PASS WITH ISSUES**
- **首页历史复盘入口是否自然？** ✅ 复用既有「历史复盘 · World Cup 2022」模块 + 「查看复盘 ▸」CTA。
- **点击路径是否清楚？** ✅ 首页 → 复盘行 → `/recap/855737`。
- **详情页是否和首页预测逻辑衔接？** ⚠️ 复盘明确标注"历史 / 模型校准,非当前预测",与当前预测卡分离（好）；但"当前预测 ↔ 历史问责"作为一个产品故事的桥还偏弱。
- **是否没有脱离原产品体系？** ✅ 用既有 Layout / i18n / 路由 / 首页模块,未改首页预测主逻辑。
- **是否仍然只是内部验证,不会误导为公开上线？** ✅ 满屏"历史回放"声明、无付费流、PR Draft、运营暂停；但它现在确实在前端产品路径里（mock）,真实部署即可见——目前靠 mock + Draft + 暂停 控制。
- **Verdict: PASS WITH ISSUES** — 流程自然且融入原体系,小问题是只有一场 + 当前↔历史叙事桥。

---

## Overall User Review Verdict: **PASS WITH ISSUES**
产品表达成立、合规、双语可用,**爆冷问责闭环作为产品概念已被验证**;但还需打磨"延续路径 / CTA / 叙事桥"。不是 FAIL,也不到无条件 PASS。

### 1. 最吸引用户的 3 个点
1. 强标题「爆冷不是偶然 · 三个盲区」——一句话就有点进去的理由。
2. 模型回放 vs 实际 + **MISS 徽章**——"敢认错"反而建立信任。
3. 真实证据卡（69%/31%、门将 6.0/7.7、48'/53'）+ 数据来源——明显区别于泛泛 AI 文案。

### 2. 最让用户困惑的 3 个点
1. 只有一场复盘,看完是"死胡同"(无"下一场 / 更多复盘")。
2. 没有"查看完整分析 / 继续"的 CTA,付费前用户没有下一步。
3. 首页"当前预测"与"历史复盘"是两块,缺少"模型会复盘 → 所以当前预测更可信"的叙事桥。

### 3. 运营最可能截图的 3 个区域
1. 强标题 hero(封面）。
2. 三个关键漏项 + MISS 徽章(爆冷故事核心)。
3. 「运营可用文案」box(直接发群)。

### 4. 必须修改的 3 个问题
1. **加"更多历史复盘"列表 / 下一场入口**,消除死胡同。
2. **复盘页底部加一个合规的 continuation CTA**(如"看当前比赛 AI 情报"),把复盘桥接回产品主体（本轮不接付费流）。
3. **首页复盘模块加一句衔接文案**,把"复盘能力"与"当前预测可信度"联系起来。

### 5. 是否建议进入 Evidence Board v2 design
**YES（建议进入）。** 闭环表达（赛前观点 → 结果 → 命中/失误 → 修正 → 运营文案）作为产品概念成立,可进入 Evidence Board v2 设计;并把上面的 continuation / CTA / 多场复盘 纳入 v2 范围。**仍为内部验证,不对外运营,PR #3 保持 Draft。**

---

## Guardrails honored (review round)
内部验证(mock) · 未改首页预测主逻辑 · 未接付费/Token · 未公开上线 · 无 betting/odds/盘口/竞猜/投注 ·
无 fake archived prediction(满屏历史回放声明)· 无 fake probability/SHAP/xG/injuries inference ·
vi Han=0 · 前端不直连 API-FOOTBALL(mock / 后端 `/api/v1/recap`)· PR #2 未动 · PR #3 Draft。
