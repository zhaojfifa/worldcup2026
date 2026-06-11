# MVP-2 Track A + Track B 联合工程评审（Owner 决策入口）

> 配套设计：`docs/MVP2_TRACK_A_AUTOMATED_OPERATION_DESIGN.md` ·
> `docs/MVP2_TRACK_B_SCOUT_REFERRAL_DESIGN.md`。
> **两份均为 DESIGN ONLY；本评审是 Owner 批/驳/改的决策入口。**
> 分支 `feature/mvp2-api-football-ingestion` · PR #3 Draft · main 不动 · 公开运营 paused。

---

## 1. 交付完整性对照（Owner 要求 → 文档章节）

**Track A（8 项）**

| Owner 交付项 | 章节 |
|---|---|
| 1 Architecture doc | Track A §0–§2 |
| 2 Job schedule proposal | Track A §6 |
| 3 Data artifact structure | Track A §4 |
| 4 Failure / retry rules | Track A §7 |
| 5 Operator review workflow | Track A §5 |
| 6 Minimal implementation plan | Track A §10 |
| 7 Guard checklist | Track A §8 |
| 8 Trial operation checklist | Track A §9（并入现有 GO/NO-GO，不另立门户） |

**Track B（9 项）**

| Owner 交付项 | 章节 |
|---|---|
| 1 Product decision doc | Track B §1 |
| 2 Mechanism mapping table | Track B §2（6 行：注册/分享/代理费/结算/客服高级链/层级） |
| 3 Data schema proposal | Track B §3（6 表 + config 旗标） |
| 4 Frontend UX proposal | Track B §4 |
| 5 Operator workflow | Track B §5 |
| 6 Reward / points rule | Track B §6 |
| 7 Risk register | Track B §7（9 项） |
| 8 Guardrail update plan | Track B §8（四语词表 + 误报分析 + 双 lint） |
| 9 Minimal trial implementation plan | Track B §9 |

Owner 首响五条（确认分支/PR、两轨理解、先查清单、设计先行、不实施声明）→ 见本文 §6 + 会话汇报。

## 2. 排序建议

**Track A 先行，Track B 紧随其后但独立 GO。**
- Track A 直接服务**正在进行的试用**：1489371（巴西-摩洛哥）06-13 22:00 UTC 开球，是 Track A
  首次辅助运行的天然目标；A 的 P0 不碰 DB/API（纯脚本+文件），审批面最小。
- Track B 的 P0 本身就含**加表 + 新端点**（L2 变更），无论如何需要单独 GO；且其分享链接最有价值的
  落点（战术室/重算页）依赖 Track A 持续产出内容。先 A 后 B 是产品逻辑顺序，不只是工程顺序。
- 两轨**可并行实施**（不同文件面，互不依赖），若 Owner 同时 GO。

## 3. 工作量与节奏

| 轨 | P0 范围 | 估算 |
|---|---|---|
| Track A P0 | mvp2_ops.py 编排器 + 队列库 + daily_scan + rescore_diff + real-recap 帧 + guard 小扩展 + 干跑演练 | ≈ 5–6 人日（最小裁剪 4） |
| Track B P0 | referral 模型/服务/路由 + 旗标 UX + guard 词表 + QR/周报工具 + 验收干跑 | ≈ 2.5 人日 |

## 4. Owner 待签字项（逐条，缺一不动工）

**Track A**
- [ ] **A-GO-1：P0 实施 GO**（纯脚本 + docs/data_audit 文件注册表；零 DB/API/基建变更）
- [ ] A-GO-2（P1）：双模式叙事端点 `GET /api/v1/narratives/...`（API 形状变更）
- [ ] A-GO-3（P1）：评审队列镜像后端表 + admin 端点（DB 扩展）
- [ ] A-GO-4（P1，可单独）：GitHub Actions 远程 runner 的密钥托管裁决（密钥进 GitHub secret store 与否）
- [ ] A-GO-5（P2）：Render cron/worker（基建扩容）
- [ ] A-CONF-1：API-FOOTBALL 套餐档位确认（日预算默认按 100 次保守设）

**Track B**
- [ ] **B-GO-1：P0 实施 GO**（含 6 张新表 + referral 路由 + 内部看板 = DB/API 扩展，一并批）
- [ ] B-GO-2：试用环境打开 `enable_referral_program` 旗标（默认关）
- [ ] B-GO-3：my 语 campaign 启动（缅甸荐单文化风险 R1，沿「二次 GO」纪律单独批）
- [ ] B-GO-4：customer-facing 名称确认（zh 俅哥情报官 / vi Cộng tác viên Tiên Tri Bóng Đá 语序 / my Football Oracle Scout）
- [ ] B-GO-5（另案，明确不在本设计内）：订阅推荐积分
- [ ] B-CONF-1：缅语禁词增项的母语者复核安排（生效前置条件）

## 5. 合规红线复述（两轨共同，写死在两份设计里）

不博彩 · 不现金投注 · 不承诺命中/收益 · 无盘口/赔率/荐单话术 · 无充值/返佣/输赢分成/月结佣金/
提现承诺（「提现」仅允许出现在「不可提现」）· MTC 仅平台积分不可提现转让交易 · 无代理层级/下线 ·
customer-facing 永不出现 代理/agent/referral/betting · 战绩类内容必带免责声明 · vi/my 永不回退
中文 · 不自动发送 · 不公开发布 · PR #3 不 ready 不 merge · main 不动。

## 6. 与现行试用的隔离声明

- 今晚揭幕场（1489369，19:00 UTC）与 06-13 场的小范围私域试用**继续走既有人工 GO/NO-GO 链路**
  （docs/mvp2/ 三件套 + 运营包 §14–§17），不依赖、不等待本设计。
- 本轮产出**只有文档**：零运行时代码、零 guard 改动、零表、零端点、零二维码、零自动发送。
  仓库内除三份设计文档与 CLAUDE.md 状态块外无任何行为变化；build/guard 基线不受影响。
- 实施在 Owner 对 §4 相应 GO 项签字后另开冲刺执行。
