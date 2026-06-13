# Track A · 1489371 Brazil vs Morocco — A3/A4 首次真实运行单（操作者执行）

> 开球：**2026-06-13 22:00 UTC** · 工具：`scripts/mvp2_ops.py` · 范围：A-GO-1（P0）。
> 铁律：**没有任何自动发送**——approve 后由运营人工粘贴，再 `queue mark-sent` 登记；
> A3 的 `group_update_message` 只有 **guard 通过 + 运营评审 approve** 之后才存在可发文本；
> A4 必须引用存档赛前工件（path + sha256 + generated_at，guard 强制）；开球后赛前物料全部作废。

## 1. T-90 watch 程序（22:00 开球 → 20:30 UTC 起）

```bash
# T-2h（20:00 UTC）时效复查：
python3 scripts/mvp2_ops.py watch --fixture 1489371 --once
# 期望：NS · lineups=0（若 lineups>0 而页面未更新 → 停发，先走 rescore 重生成）

# T-90（20:30 UTC）起常驻（5 分钟轮询；首发一出本地告警并自动跑 A3 生成 → 只进评审队列）：
python3 scripts/mvp2_ops.py watch --fixture 1489371
# 不想自动跑生成：加 --no-auto，首发出后手动执行：
python3 scripts/mvp2_ops.py rescore --fixture 1489371
```

窗口规则（CLI 强制）：T-12 后拒绝任何新生成；T-10 仍未评审完 → 只发 A2 预批的提醒模板
（运营包 §6b④/§15③）；运营必须全程在键盘前——人不在 = 不发送。

## 2. A3 评审与发送（人工）

```bash
python3 scripts/mvp2_ops.py queue list --fixture 1489371 --status guard_passed
python3 scripts/mvp2_ops.py queue show <ITEM>      # 逐语言审 group_update_message
python3 scripts/mvp2_ops.py queue approve <ITEM> --by <运营名>
# 人工粘贴到群（仅 Owner GO 范围内的群）后登记：
python3 scripts/mvp2_ops.py queue mark-sent <ITEM> --channel telegram --group "<群名>" --screenshot docs/qa_screenshots/mvp2_trial_sends/<file>.png
```

send-kit：`docs/data_audit/mvp2_send_kits/1489371.rescore_update.md`（A3 运行后生成）。
mock 永不可 approve；文件被手改（sha 不符）即拒——要改就重生成。

## 3. 开球与赛后

```bash
# 22:00 UTC 开球：
python3 scripts/mvp2_ops.py queue sweep            # 赛前条目全部过期
# FT+45min 起（约 2026-06-14 00:45 UTC 后）：
python3 backend/scripts/mvp2_ingest_scout_pack.py 1489371   # 赛后刷新 pack（事件/统计）
python3 scripts/mvp2_ops.py recap --fixture 1489371          # real_recap 帧 + 三语复盘 + guard + 注册
# 复盘评审 approve 后按 Owner 既有流程决定 bundle/部署/发送。
```

## 4. 计时表（Owner 要求逐项回填 — 试用核心时序证据）

| # | 事件 | 计划 (UTC) | 实际 (UTC) | 备注 |
|---|---|---|---|---|
| 1 | T-90 watch 启动 | 06-13 20:30 | | run_id: |
| 2 | 首发公布时刻（lineups>0） | ~20:45–21:20 | | watch 告警时间 |
| 3 | A3 生成开始 | 公布后即刻 | | run_id: |
| 4 | A3 生成结束（三语） | +4–8 min | | 各语言 guard_passed/failed: |
| 5 | guard 结果 | — | | zh / vi / my： |
| 6 | 运营评审完成（approve） | T-30 前 | | 条目 id： |
| 7 | 人工发送时刻（仅 Owner GO） | T-30…T-20 | | mark-sent 记录： |
| 8 | 开球 sweep | 22:00 | | 过期条目数： |
| 9 | FT 复盘开始（A4） | FT+45min | | run_id: |
| 10 | FT 复盘结束 + guard | +10–20 min | | 三语 guard： |

## 5. 检查清单（与 GO/NO-GO §0/§4b 并用）

- [ ] A2 工件全部 guard_passed 且已评审（当前队列 12 条 guard_passed，见 `queue list --fixture 1489371`）
- [ ] 发送范围 = Owner GO 范围（zh 内部群 · vi Telegram 可信 · my 1 测试群）；**1489371 预热发送需 Owner 另行确认**（运营包 §6 既有规则）
- [ ] 免责声明保留；只替换 [群链接由运营填写]；不得人工改写判断文案（sha 防篡改兜底）
- [ ] A3 三语并行约 4–8 分钟；若 my 失败只发 zh/vi（语言独立原则）
- [ ] 任何 needs_review override 必须 --note 并记入当日记录
- [ ] 配额账本 <70%（`status --fixture 1489371` 查看）
- [ ] 全部时刻回填 §4 表 → 试用反馈报告

## 6. P1.2 Status Refresh Gate — 赛日新鲜度校验（Owner verdict 2026-06-13 条件 1）

> 目的：完赛后产品不得再以「赛前预测」状态展示 1489371。本节为今晚 LIVE/FT 真实校验的逐步指令。
> 基线（开球前，2026-06-13T02:21Z 已验证）：1489371 = SCHEDULED · today_package_allowed=True ·
> package today 放行 · freshness PASS。

### 6a. 开球时 / LIVE 期间（22:00 UTC 起，每 30 分钟）
```bash
python3 scripts/mvp2_growth_cli.py status-refresh
python3 scripts/check_fixture_freshness.py
```
预期：
- lifecycle 1489371 = **LIVE**（API 报 1H/HT/2H 或 开球已过而无完赛信号 → 冻结）
- today_package_allowed = **false** · `package today --fixture 1489371` → REFUSED
- refresh 输出 **NO_VALID_TODAY_FIXTURE** · 旧 today/next 包被 REFUSED 桩覆盖
- ⚠️ HomePage hero 仍钉死 `fixtureId="1489371"` → 完赛后 freshness 扫描器 **预期 FAIL**（设计闹钟，
  非误报）。必须如实记录；修复 = 工程更新 hero 钉值 + 运营重新部署前端。

### 6b. FT / FT+45（约 00:00–00:45 UTC 06-14）
```bash
python3 scripts/mvp2_growth_cli.py status-refresh
python3 scripts/mvp2_growth_cli.py refresh --lang zh --ref QG-TEST1
python3 scripts/check_fixture_freshness.py
```
预期：
- lifecycle = **FINISHED**（FT+45 前）→ **RECAP_PENDING**（FT+45 后仍无复盘叙事）
- today/next 包 = refused · `NO_VALID_TODAY_FIXTURE`
- recap 包此时仍不可用（需先有 real_recap 叙事）；A4 复盘生成并 bundle 后 → **RECAP_READY** → recap 包放行

### 6c. A4 复盘 bundle 之后
```bash
python3 scripts/mvp2_growth_cli.py status-refresh    # 1489371 -> RECAP_READY
python3 scripts/mvp2_growth_cli.py refresh --lang zh --ref QG-TEST1   # recap 包可用，today 仍 refused
python3 scripts/check_fixture_freshness.py            # hero 修复+重部署后应回到 PASS
```

### 6d. 证据留存
- 当晚所有 `fixture_lifecycle_*.json` + `refresh_summary_*.json` 提交至 main 作为审计串。
- 扫描器任何 FAIL：记录 fixture/原因/是否预期（hero 钉值 = 预期）于本节回填。
