# MVP-2 User Review v2 — Evidence Board (855737, minimal implementation)

> **Reviewer role:** User Reviewer / Operator Persona (NOT the developer hat). **Date:** 2026-06-10 ·
> **Branch:** `feature/mvp2-api-football-ingestion` (PR #3, Draft) · **Mode:** internal verification
> (mock / `VITE_USE_MOCK=true`, operation paused). Subject: the **Evidence Board v2 minimal implementation**
> — Home/Recap → `/recap/855737` → **`/evidence/855737`** (new additive surface), zh + vi.
> Evidence reviewed: `docs/qa_screenshots/mvp2_evidence_board_v2/{evidence_855737,recap_855737}_{zh,vi}*.png`.

This reviews the **implemented** Evidence Board (additive surface built under the Gate Spec Owner GO), not a
design. Verdicts are honest — a review, not a sign-off.

---

## Owner GO honored (2026-06-10)
- **GO received:** "Minimal Evidence Board v2 implementation" (Path A). Scope locked to: additive surface only,
  **855737 only**, reuse ScoutScore/recap artifacts, confidence as **tier + stars (no %)**, evidence / factor /
  missing-data / AI-boundary cards, source ledger + raw Scout Pack collapsed, zh/vi (vi Han=0), homepage main
  logic untouched, no payment/Token, operation paused, PR #3 stays Draft.
- **Delivered exactly that.** No 979139, no TheSports, no live DeepSeek/Gemini, no payment/public launch.

## What was built (additive only)
- **New route `/evidence/:fixtureId`** → `EvidenceBoardPage.tsx` (bundled-only; renders without a backend).
- **Reusable panel** `EvidenceBoard.tsx` composing new components: `FactorCard`, `EvidenceCard`,
  `MissingDataCard`, `AiBoundaryCard` (designed to be shared by a future prediction detail page).
- **Bundled data** `data/evidenceData.ts` (zh/vi/en) **derived from** the 855737 accountability artifacts
  (`mvp2_prediction_accountability_reports`, `mvp2_scoutscore_v0`) — no invented values.
- **Additive entry link** from `RecapDetailPage` ("查看完整证据面板 · 逐因子 ▸"); **homepage untouched.**
- Scoped CSS (`.eb-*` / `.factor-*`); `App.tsx` route mount only.

## Engineering verification (self-check)
- `npm run build` (`tsc -b && vite build`): **PASS** (60 modules, 0 TS errors).
- **vi Han = 0** at runtime: `document.body.innerText` Han count **0** on `/evidence/855737?lang=vi`
  (whole page incl. topbar); `.content` Han **0**. Static block scan of VI/EN content also clean.
- Forbidden-wording scan (betting/odds/盘口/竞猜/投注/命中率/赔率/42.2%/提现…): **clean** in EBv2 files.
  (Note: the brand topbar sub-copy "不只看胜率…" contains 胜率 in negation — pre-existing, approved, chrome-only.)
- Vendor-reference scan (`api-sports|apisports|v3.football|API_FOOTBALL`) in `frontend/`: **empty.**
- No console errors (zh + vi). `git diff --check`: clean. Structure: 7 factor cards + 5 evidence cards rendered.

---

## A. 普通球迷视角 (ordinary fan) — **PASS WITH ISSUES**
- **一眼读懂 AI 怎么判断？** ✅ 顶部「AI 倾向：Argentina · 历史回放 / 信心档位：低 ★★☆☆☆」+「未命中 · MISS」一眼可读,**无百分比**。
- **看得懂"为什么"吗？** ✅ 这是最大升级:**7 张因子卡**把"来源 / 影响 / 解读"摊开——「射门效率 · 决定性·漏判」「事件动量 · 决定性·漏判」直指反转原因。
- **相信不是泛泛 AI 文案吗？** ✅ 偏信——每张卡带真实来源(`/fixtures/...`)或诚实「假设」标记;证据卡 69%/31%、6.0/7.7、0/5 都可追溯。
- **困惑点?** ⚠️ 7 张因子卡信息密度偏高,普通球迷可能只读前 2–3 张;`/injuries(0 条)`「来源」对非技术用户略硬。
- **Verdict: PASS WITH ISSUES** — 解释力明显强于复盘页,但密度对纯球迷偏高。

## B. 私域运营视角 (operator) — **PASS**
- **可截图吗？** ✅ 紫色 hero + AI 倾向卡 + MISS + 因子卡是固定"可截图带";单屏即讲清"AI 判断 / 漏在哪 / 缺什么"。
- **讲得出"模型错了但值得看"吗？** ✅ 「决定性·漏判」+「已确认缺口(伤停 P0 / xG P1)」把失误转成"模型在升级"的故事,比复盘页更有方法论质感。
- **合规吗?** ✅ 无 betting/odds/盘口/竞猜/投注;无胜率/命中率/百分比;伤停标"source required"、绝不写"无伤停";满屏"历史回放"声明。
- **双语?** ✅ zh 自然;**vi 全页 0 汉字**,术语(AI / MISS / xG / Elo / 队名)按规则保留英文。
- **Verdict: PASS** — 本轮最成立视角:可直接做"AI 自我问责"系列封面与群文案。

## C. 付费前用户视角 (pre-paid) — **PASS WITH ISSUES**
- **比免费 AI 更有价值吗？** ✅ 因子级 + 来源级透明 + 诚实缺口,明显"像有方法论"。
- **看到证据 / 缺口 / 边界了吗？** ✅ 证据卡 + 缺失数据卡 + AI 边界(可解释 vs 禁止)三件套齐全。
- **有下一步钩子吗?** ⚠️ 按设计**不接付费流**;continuation 仅回「历史复盘 / 今日 AI 观点」。把"证据可信"转化为"付费意愿"的桥仍是后续设计题(非本轮)。
- **Verdict: PASS WITH ISSUES** — 说服力足,转化钩子按 Owner 边界留白。

## D. 产品流程视角 (product flow) — **PASS WITH ISSUES**
- **是否融入原体系?** ✅ 复用 Layout / i18n / 路由 / recap hero / ledger / pillv;`.eb-*` 作用域隔离;**首页预测主逻辑未改**(diff 仅新增)。
- **入口自然吗?** ✅ 复盘页证据卡下新增「查看完整证据面板 · 逐因子 ▸」→ `/evidence/855737`;back → 复盘页,不死胡同。
- **是否会被误读为公开上线?** ✅ mock / 历史回放声明 / 无付费 / PR Draft / 运营暂停。
- **小问题:** ⚠️ ① 目前仅从复盘页可达(首页未加链接,刻意最小化改动);② 仅 855737;③ 后端 `GET /api/v1/evidence/{id}` 本轮**未建**(前端 bundled,与 recap 起步方式一致,可作为后续 proxy)。
- **Verdict: PASS WITH ISSUES** — 流程干净、可回滚(卸路由即移除)。

---

## Overall Verdict: **PASS WITH ISSUES (internal)** — operator real-device review pending
证据面板把"AI 怎么判断 → 错在哪 → 缺什么"做成了一个**可追溯、诚实、双语**的统一面板,**因子卡**是相对复盘页的核心增量;合规、vi Han=0、构建通过、零控制台错误。**仍为内部验证**:`public_ready=false`、运营暂停、PR #3 Draft、仅 855737、后端 evidence 接口未建。**最终 PASS 待 operator 真机复核**(与既往 MVP-2 复核口径一致)。

### 最吸引用户的 3 个点
1. **7 张因子卡(来源 / 影响 / 解读 + 假设标记)**——把"为什么"摊开,明显区别于泛泛 AI 文案。
2. **AI 倾向 + 信心档位(★ 星级,无百分比)+ MISS**——一眼读懂且不过度承诺。
3. **AI 边界卡(可解释 ✓ vs 禁止 ✕)+ 缺失数据卡**——"敢说自己不知道什么"建立信任。

### 仍需打磨的 3 个点
1. 因子卡密度偏高(7 张),可考虑"决定性因子优先 / 其余折叠"。
2. 仅复盘页入口、仅 855737——首页链接与第二样例(如 979139)是后续 Owner 决策。
3. 后端 `GET /api/v1/evidence/{id}` 未建(bundled-only),真实部署前需补 proxy 以与 recap 对齐。

### Gate Spec acceptance criteria（逐条）
1. build PASS / `git diff --check` clean — ✅
2. vi Han=0 / 禁词扫描 clean — ✅
3. 每条结论挂 `source_refs` 或 `assumption` 标记 — ✅(因子卡 source 行 + 假设徽章)
4. 无 fake probability / SHAP / xG / injuries inference / fake archived prediction — ✅
5. 首页预测主逻辑未改(additive only) — ✅
6. 前端无 vendor 引用 — ✅
7. zh + vi 截图已采集 — ✅(`docs/qa_screenshots/mvp2_evidence_board_v2/`);**operator review PASS = 待记录**
8. `public_ready=false`,无付费/Token/公开 — ✅

---

## Guardrails honored (this round)
内部验证(mock) · 未改首页预测主逻辑 · 未接付费/Token · 未公开上线 · 无 betting/odds/盘口/竞猜/投注 ·
无 fake archived prediction(满屏历史回放声明) · 无 fake probability(档位+星级,无 %)· 无 SHAP/xG/injuries inference ·
vi Han=0 · 前端不直连 vendor(bundled / 后端) · 仅 855737 · PR #2 未动 · PR #3 Draft · 运营暂停。
