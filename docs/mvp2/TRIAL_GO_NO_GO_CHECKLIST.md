# MVP-2 小范围试用 · GO / NO-GO 清单

> 配合 `TRIAL_SEND_PACKAGE.md`（物料）与 `TRIAL_FEEDBACK_FORM.md`（回收）使用。
> 物料最终口径 = `docs/MVP2_JUNE11_TRIAL_OPERATOR_PACKAGE.md`（§6b/§7/§15，§14–§17）。

## ★ 0. Owner GO 记录（2026-06-11）
**Owner Verdict: PASS WITH CONDITIONS — 三语小范围私域试用放行。**
- 范围：zh = 内部中文群/可信用户 · vi = Telegram 可信球迷 · my = 1 个测试群或个位数可信缅甸球迷。
- 公开运营继续 paused；PR #3 不 merge / 不 mark ready / 不动 main / 不公开发布。
- 条件：运营包为唯一物料口径 · 仅替换 [群链接由运营填写] · 不得人工改写判断文案 ·
  免责声明保留 · 开球后不发 · 禁博彩/赔率/保证/荐单话术 ·
  **首发已公布而页面未更新 → 停发并先重生成** · 发送时间/群名/截图/点击/反馈全记录。
- 试用结束后产出 `TRIAL_FEEDBACK_REPORT.md`（截图 + 用户原话）。

**工程发送前校验（2026-06-11 08:53 UTC，API-FOOTBALL 实时）：**
- 1489369 Mexico–South Africa：kickoff 2026-06-11 **19:00 UTC**（约 10 小时后）· status NS ·
  **lineups posted = 0** → 页面「首发未公布」口径准确，无需重生成，窗口内可发。
- 1489371 Brazil–Morocco：kickoff 2026-06-13 **22:00 UTC** · status NS · lineups = 0（预热需 Owner 另行确认）。
- 技术门（本 sprint 既有证据）：narrative guard 46/46 PASS · rescore 12/12 guard_clean ·
  visible-copy 15/15 PASS（5 路由 × zh/vi/my）· build PASS · 截图 10/10
  （`docs/qa_screenshots/mvp2_locale_consolidation/`）。
- 工程未发送任何消息；发送 = 运营动作。临近发送若距本校验超过 2 小时，建议让工程复查一次 lineups。

## 1. 发送前（全部勾选才可发）
- [x] Owner 书面 GO 在手（2026-06-11 PASS WITH CONDITIONS，见 §0 — 本清单不替代 GO）
- [ ] 当前时间早于该场开球（1489369 = **2026-06-11 19:00 UTC**；1489371 = 06-13 22:00 UTC）
- [ ] 首发状态复查：lineups 仍未公布，或页面已按最新首发重生成（§0 校验超 2 小时则让工程复跑）
- [ ] 文案从运营包/`TRIAL_SEND_PACKAGE.md` 原样复制，仅替换 [群链接由运营填写]
- [ ] 免责声明行保留；无任何博彩/保证/荐单词被人工加入（zh/vi/my 三语禁词见发送包 §8）
- [ ] 群链接经运营本人验证可入
- [ ] 接收面 = 约定的小范围（zh 内部群 · vi Telegram 可信 · my ≤1 测试群），未扩散
- [ ] 截图包就绪（zh rescore 优先；my 用 predict_1489369_my_rescore.png）
- [ ] 反馈表（三语版，含发送记录表 §0 与缅甸加问 B 区）已建档，记录人明确

## 2. 开球前 30 分钟更新
- [ ] 首发公布后：工程重跑 rescore 管线（`mvp2_generate_rescore_models.py` → guard → 人工核对）
- [ ] 修正版判断与提醒模板一致后再发（不得在结果出来前手改判断方向）
- [ ] 若管线/人手来不及：只发提醒模板，不发未经核对的修正判断

## 3. 赛后停发规则
- [ ] 开球即停发所有赛前物料（含修正版）
- [ ] 不发「俅哥早就说过」式马后炮；复盘内容另走 /recap 路径，需 Owner 确认
- [ ] 群内如出现博彩/保证式讨论，运营按合规口径澄清并记录（反馈表 C 区）

## 4. 反馈回收（试用窗口结束 24h 内）
- [ ] 反馈表 0/A/B/C/D/E 各区填齐，原话留存（A = Owner 主 6 问；B = 缅甸加 5 问）
- [ ] 发送记录（时间/群名/截图/点击）+ 入群数据归档至 `docs/qa_screenshots/mvp2_trial_sends/`
- [ ] 合规区 C 任一命中 → 单独标红上报
- [ ] 汇总转入 `TRIAL_FEEDBACK_REPORT.md`（工程据此出试用反馈报告）

## 5. 试用裁决（Owner 在反馈汇总后选择其一）
| 裁决 | 含义 | 下一步 |
|---|---|---|
| **PASS** | 钩子成立、文案自然、无合规误读 | 进入 feedback-driven Product Trial Iteration Sprint（扩大场次/人群仍需单独 GO） |
| **PASS WITH ISSUES** | 方向成立但有明确修改清单 | 同上，但修改清单优先于新功能 |
| **FAIL** | 用户不点 / 不懂 / 不入群 | 回到产品假设层重新设计（不追加运营投放） |
| **BLOCKED** | 合规误读或渠道问题 | 立即停发，问题解除前不再试用 |
