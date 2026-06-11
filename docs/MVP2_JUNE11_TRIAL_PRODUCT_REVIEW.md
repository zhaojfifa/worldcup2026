# MVP-2 June 11 Real Match Trial — Product Review

> **Date:** 2026-06-11 · **Branch:** `feature/mvp2-api-football-ingestion` · PR #3 **Draft** · main 未动 ·
> **operation paused（未发送任何内容）**。Verdict：**Engineer self-verify PASS — READY for Owner trial-send review**
> （试发包：`MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md`）。

## 1. 交付对照（Owner Tasks A–K）

| Task | 结果 |
|---|---|
| A 品牌清理 | 客户面扫描：frontend 无 Cloud、无「AI 分析」、无 AI analysis；`source required` 等审计词仅存于 evidence 内部折叠数据。产品面改用 persona：战术室入口/页面/区块标签 → **中文先知战术室 / Phòng chiến thuật Tiên Tri Bóng Đá / 中文先知临场 30 分钟修正 / Cập nhật 30 phút trước trận**；`<title>` 由中文改为英文品牌行（vi/mm 回退英文政策）。法务名仅存内部文档（CÔNG TY TNHH CÔNG NGHỆ SỐ LEIZE / LEIZE DIGITAL TECHNOLOGY COMPANY LIMITED）。 |
| B 真实赛程核验 | `scripts/mvp2_verify_june11_fixtures.py` → `docs/data_audit/mvp2_june11_real_fixture_verification.json`：league=1 season=2026（72 场）；**1489369 Mexico–South Africa 2026-06-11T19:00Z Estadio Azteca Group-1 Not Started**；1489371 Brazil–Morocco 06-13；lineups=false injuries=false squads/coach/teams=true；source_ledger 含 token 处理声明。 |
| C trial 帧 | `mvp2_trial_prediction_frames/{1489369,1489371}.json`：fixture basis + team baseline（coach/squad/GK 名/射手依赖）+ 12 因子（goal/defensive trend、squad stability、GK risk、striker risk、venue/altitude、lineup uncertainty、injury gap internal-only、30min trigger），每因子 source_refs + data_status(verified/partial/assumption/missing) + customer_visible + internal_note；ScoutScore 输出含 what_could_flip + recheck_30min。 |
| D persona 叙事 | `mvp2_trial_prediction_narratives/` 8 份（2 场 × zh/vi × DeepSeek+Gemini）**全真实 LLM、0 mock、GUARD PASS**；新增必填 `tactical_read`；persona 开口（中文先知判断… / Tiên Tri Bóng Đá nhận định…）；guard 新增 Cloud/AI 分析/缺数据表达（thiếu dữ liệu/缺数据）禁令 + persona 必现校验。两家 vi 初稿多次写 kèo/cửa trên/chắc thắng/thiếu dữ liệu → **全部被 in-loop guard 拦截重试**；旧 6 份 vi 资产同标准重生成，全库 28 份 PASS。 |
| E 战术室页 | `/predict/1489369`：比赛头卡（真实开球/球场/轮次）→ 中文先知主判断 → AI 倾向/比分区间（模型估计标）/风险评级 → **中文先知战术解读卡（tactical_read）** → 关键因子 → 临场 30 分钟修正 → 免费 vs 完整 + 入群/今日 CTA → 内部折叠（运营素材/来源/provider；`?ops=1` 展开供截图）→ disclaimer。raw pack/ledger 不在主视图。 |
| F 首页替换 | 层级=Owner 规范：① persona status strip「中文先知已生成赛前判断 · 临场 30 分钟将重新计算 · 数据同步 HH:MM」② 主卡 Real Match Tactical Room（揭幕战 + LLM hook + 进入中文先知战术室 / 加入赛前情报群）③ 次卡 Brazil–Morocco ④ **旧 mock（信号卡+今日列表+爆冷TOP3）整体降级进「内部演示数据（mock）」折叠**，不再占首屏；历史复盘保持可见。 |
| G 运营包 | `MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md`：目标/选定比赛/数据源/因子/provider 对比/最终 provider（DeepSeek）/zh+vi 可复制群消息（[群链接由运营填写]）/截图路径/发送 checklist/Do-NOT-send/Owner GO。 |
| H 截图 | `docs/qa_screenshots/mvp2_june11_trial/` 6 张（home zh/vi、predict 1489369 zh/vi、operator fold zh/vi）。 |
| I 检查 | build ✓（tsc+vite）· `git diff --check` clean · **vi 可见文本 Han=0**（title 修复后；dev 模式 dump 中的 22 字符证实为 `<title>`+CSS 注释，非渲染文本）· 无 Cloud · 博彩/保证词 0 · 无假链接（guard URL 禁令 + 占位符）· 无 token · frontend 不调 vendor（bundled）· mock 已降级（DOM 验证）· fixture 真实（API 核验件）· 终稿 LLM 生成（10 份页面绑定全 deepseek 标记）· DeepSeek/Gemini 双存档 · source_ledger 在 |
| J 文档 | 本文 + 运营包 + CLAUDE.md / MVP_STATUS / HANDOFF / PROJECT_INDEX 同步。 |
| K Git | 3 commits 推送 `feature/mvp2-api-football-ingestion`；PR #3 Draft。 |

## 2. 命名变更记录
- 移除客户面唯一中文 `<title>`（中文标签页标题 → 英文品牌行）；产品面未发现 Cloud（无需移除，记录在案）。
- persona 上屏位置：home status strip / 主卡 CTA / strip 行 CTA / predict backbar+banner / 区块标签
  （怎么判断 / 战术解读 / 临场 30 分钟修正）/ narrative 正文（hero/judgement/群文案，guard 强制）。
- en 层保持品牌中性（Giành Cup Tactical Room）——en 为系统回退层，无 persona。

## 3. 残余风险
1. **时效**：揭幕战 19:00 UTC 开球——开球后主发文案过期（运营包 §10 已设 Do-NOT-send）。
2. 既有 dev-only 噪音：内联 CSS 注释含中文（prod minify 后不存在）；浏览器 title 已改英文，分享卡 OG 标签未配置（后续）。
3. 临场 30 分钟修正当前为**人工重跑管线**（脚本可重生成），非自动调度——试发期由工程值守，规模化需调度器（Owner 决策项）。
4. 深链 404（Render dashboard SPA rewrite 待 operator 配置）——群消息引导以首页为入口或待 rewrite 配好。
5. mm 语言未做（按既定优先级 vi 先行）。

## 4. 合规
不博彩（含 vi 黑话全禁）· 不承诺命中/收益 · 比分区间一律「模型估计」· 免责声明三端齐（页面/群消息模板）·
MTC 未触碰 · 群链接不由 LLM 产生。**发送动作 100% 以 Owner GO 为前提。**
