# MVP-2 Track A — 自动化足球情报运营管线（重型设计 · DESIGN ONLY）

> **状态：设计稿，未实施。** Owner 批准本设计前，不写任何运行时代码。
> 分支 `feature/mvp2-api-football-ingestion` · PR #3 保持 Draft · main 不动 · 公开运营 paused ·
> 仅小范围私域试用。**任何 job 都不发送任何消息——发送永远是运营的人工动作。**
> 覆盖 Owner 八项交付：①架构 ②任务日程 ③工件结构 ④失败/重试 ⑤运营评审工作流
> ⑥最小实施计划 ⑦Guard 清单 ⑧试用运营清单。

---

## 0. 范围与复用地图

Track A 把今天「运营手工逐个跑脚本」的链路，升级为五个有名字的 job（A1–A5）+ 工件注册表 +
评审队列 + 清单——**不加服务器、不加调度器、不自动发送、不扩容**。LLM 仍是唯一叙事作者；
工程只做组织输入 / 调用 / 校验 / 登记 / 渲染（CLAUDE.md 硬规则不变）。

| 阶段（对应 MINI_AGENT_HARNESS_DESIGN 8 阶段） | 复用的现有资产 | Track A 角色 |
|---|---|---|
| Data Scout | `scripts/mvp2_verify_june11_fixtures.py` · `backend/scripts/mvp2_ingest_scout_pack.py` · `backend/app/services/api_football_client.py`（超时/429/预算已内建） | A1 扫描，A2/A3/A4 取数 |
| Baseline Model | `scripts/mvp2_build_trial_prediction_frame.py` · `scripts/mvp2_build_scoutscore_v0_2_factors.py`（Kaggle Elo/近10/H2H） | A2 帧，A4 复盘帧 |
| Explanation / Copy（LLM） | `mvp2_generate_trial_prediction_narratives.py` · `mvp2_generate_product_proof_narratives.py`（共享 GEN：providers/重试环/token 预算 incl. my=7800）· `mvp2_generate_rescore_models.py` | A2 叙事+rescore 模型，A3 重算更新，A4 复盘 |
| Compliance | `check_mvp2_product_narrative_guard.py`（check_obj 可 import）· rescore 内联 guard · `check_customer_visible_copy.py`（15 面） | 每个 job 的门；§7 小扩展 |
| Human Review | `docs/LLM_PREP_SCHEMA_AND_GUARDRAILS.md` §10 评审队列先例 · GO/NO-GO 清单 | A5 评审队列（文件型，状态机正式化） |
| Render | `frontend/src/data/productNarratives/` + `rescoreModels/` 静态 bundle · backend `/api/v1/recap/{id}` 双模式先例 | 页面更新路径（§2 决策 2） |

**全程不变量**：密钥只在 `backend/.env`/运营环境（不打印不提交）；前端永不调 LLM/vendor；
my-MM mock 永不落盘（zh/vi mock 仅页面标记回退、永不可发送）；赛前工件带 `expires_at=kickoff`
开球即死；没有任何自动发送，`sent` 只是运营人工粘贴后的记录。

---

## 1. 架构（交付 ①）

```
                    ┌────────────────────────────────────────────────────┐
                    │  scripts/mvp2_ops.py（P0 本地编排器，运营触发）       │
                    │  子命令: scan · prematch · watch · rescore ·        │
                    │          recap · bundle · queue · status            │
                    └──────┬───────────┬───────────┬─────────────────────┘
                           │ A1 扫描    │ A2 赛前    │ A3 重算 / A4 复盘
                           ▼           ▼           ▼
  API-FOOTBALL ─▶ verify/ingest ─▶ frames ─▶ LLM 叙事/rescore/update ─▶ GUARD
  （服务端密钥、     （现有脚本）     （现有）    （现有 GEN + 2 个新 builder）  （现有+扩展）
   预算+429 守护）                                                          │
                                                                           ▼
                       docs/data_audit/* 工件 + run manifest + guard report
                                                                           │
                                                                           ▼
                   A5 评审队列（文件型 JSON registry + CLI；状态机 §5）
                                                                           │
                 ┌──────────────────────┬────────────────────────────────┤
                 ▼                      ▼                                ▼
        运营 send-kit（.md，人工复制     前端 bundle（仅 guard-passed；    TRIAL_FEEDBACK_FORM /
        粘贴发送；工程不发送）           静态 build + 部署）               发送记录（人工填写）
```

---

## 2. 关键决策（建议 + 理由 + 取舍）

### 决策 1 · 编排运行时：P0 = 本地编排器（试用默认）

| 阶段 | 方案 | 裁定 |
|---|---|---|
| **P0（推荐，试用默认）** | `scripts/mvp2_ops.py` 单入口包装现有脚本，运营触发；`watch` 模式解决 T-35 时机 | **现在采用** |
| P1 | GitHub Actions 定时 workflow | **缓——两个硬伤（下）** |
| P2 | Render cron/worker | **缓——属扩容，需 Owner 基建审批** |

P0 胜出的根本原因：**禁自动发送 = 每个发送时刻必须有人在场**。调度器去不掉这个人，只去掉
「忘了跑」的风险——`watch` 模式在本地就解决了。30 分钟重算需要分钟级精度；按发送清单，运营
本来就在 T-90 在线。

**T-35 时机问题（无调度器解法）**：`mvp2_ops.py watch --fixture ID` 自 T-90 起每 5 分钟轮询
`/fixtures/lineups`（≤ ~12 次额外 API 调用），lineups>0 即本地告警（终端铃 + macOS 通知）并立刻
跑 A3 生成链——产物只进评审队列，**绝不自动发送**。运营不在场 → 什么都不发，这正是规则本身。

**P1 GitHub Actions 如实评估（写明，不采用）**：
- 硬伤一：GitHub `schedule` 触发**只跑默认分支**。试用在 feature 分支、main 不可动 → 定时
  workflow 对本试用结构性不可用；`workflow_dispatch` 可在 feature 分支跑但仍是人工触发，不优于本地。
- 硬伤二：共享 runner 的 cron 常漂移 3–15 分钟，对 T-35 触发不可接受。
- 密钥问题：Actions secrets 加密存于 GitHub 不进 git 历史，字面上不违反「不提交密钥」，但把密钥
  托管面从「运营本机 + Render env」扩大到 GitHub secret store 与 runner 日志 → **Owner 单独签字项**，
  不是工程默认。
- 工件回写：CI 提交回 Draft 分支会产生 bot 噪音；上传 artifact 又破坏 docs-as-truth 且前端 bundle
  需要文件在仓库内。两条路都弱于「本地跑 + 运营审后提交」。

**P2 Render cron/worker**：长期最干净（密钥已在 Render、A3 时机精准），但是新基建 → 卡在
「禁擅自扩容」规则；且只有与决策 2 的 (b) 端点配套才有意义。试用报告后再议。

### 决策 2 · A3/A4 页面更新路径：评审包优先，窗口外静态重部署，P1 双模式端点

| 选项 | 机制 | 分阶段裁定 |
|---|---|---|
| (a) 静态 bundle + 重部署 | 重生成 → guard → cp 到 `frontend/src/data/*` → build → Render 部署（~3–6 分钟 + CDN） | **P0 用于 A2（窗口前）与 A4（赛后无 deadline）** |
| (b) 后端叙事端点 + bundle 回退（双模式，同 `/api/v1/recap/{id}` 先例） | `GET /api/v1/narratives/{fixture}/{surface}?lang=` + admin `POST` 上传 guard-passed JSON；前端 fetch 优先、bundle 兜底 | **P1 — API 形状变更需 Owner；把部署移出重算路径** |
| (c) 仅评审包（窗口内不更新页面） | A3 产物 = 已评审的群修正消息 + 运营包；页面 rescore 块本来就承诺「修正在群里发」 | **P0 用于 A3 的 T-35 窗口内** |

A3 选 (c) 的理由：产品承诺是「开球前 30 分钟群内修正」——**群内消息才是交付物**；T-35→T-30
窗口内插入 3–6 分钟部署 + 中间还要人工评审，不可靠。与 Owner 条件「首发已出而页面未更新 → 停发
并重生成」一致：首发一出，赛前物料本来就停发，能发的只剩提醒模板 + 已评审的群内修正；页面的
rescore 块（「我会重算什么」）依然为真。页面在窗口允许（首发早出）或开球后再重生成+重部署。
**显式声明取舍**：P0 窗口内强刷页面的用户会看到 pre-XI 框架；小范围私域 + 群优先的产品流使其可接受；
P1 的 (b) 端点消除该窗口。

**P1 快赢（随 (b) 一起或单独）**：`productNarrativeData.ts`/`rescoreData.ts` 现为硬编码静态
import，新 fixture 要手改 TS——改 Vite `import.meta.glob(..., { eager: true })` 后丢文件即自动
打包（仅构建期，无 API 变化；改后重跑可见扫描）。

### 决策 3 · 评审队列存储：文件型 JSON registry + CLI

选 `docs/data_audit/mvp2_review_queue/`（index + 每条目文件）+ `mvp2_ops.py queue` CLI。理由：
契合 docs-as-truth 与 PR 可见性；git 历史即审计日志；零 DB-schema 扩展（那需要 Owner 批）；离线可用；
试用量级 ~几十条。取舍：无多运营并发安全、无远程视图——单运营可接受；P1/P2 与决策 2(b) 一起迁移到
后端表 + admin 端点（ContentAsset/admin 模式现成）。

### 决策 4 · 工件注册表：per-fixture manifest + per-run manifest（schema 见 §4）

### 决策 5 · 失败/重试：合并规则见 §7

### 决策 6 · A1 关键场判定：确定性规则 + 运营 override 文件（见 §3 A1）

### 决策 7 · 三语扇出：A2/A4 串行；仅 A3 按语言并行

A2/A4 无墙钟压力——保持现状串行（日志简单、重试归因清晰）。A3 是唯一时间敏感 job：zh/vi/my 并发
（ThreadPoolExecutor 3 workers，按语言隔离、各自沿用现有重试环）→ 最坏墙钟从 ~10–25 分钟降到
~4–8 分钟。成本备注：一场三语全量（含重试）DeepSeek-chat/Gemini-Flash 量级为几美分到 ~$0.15——
约束不是钱，是墙钟与运营评审带宽；3 并发远低于 provider 限速。

---

## 3. Job 规格

### A1 · 每日赛程扫描
- **触发**：运营每日跑（P0 目标 09:00 UTC；`mvp2_ops.py scan`）。
- **输入**：`/fixtures?league=1&season=2026`（1 次调用，复用 verify 脚本逻辑）；本地 Kaggle Elo
  快照；`key_match_overrides.json`。
- **关键场判定（确定性、有序、记录理由）**：
  1. 运营 override `force_key` / `force_skip`（永远最高）
  2. 淘汰赛 → key
  3. 揭幕日/揭幕战 → key
  4. 双方均 Elo Top-12 → key（marquee）
  5. Elo 差 ≥150 且热门方 Top-8 → key（爆冷观察位）
  6. 东道主（墨西哥/美国/加拿大）出场 → key
  7. 上限：2 场/日（试用评审带宽；override 可放开）
- **输出**：`docs/data_audit/mvp2_daily_scan/{YYYY-MM-DD}.json`（今日+次日赛程、key 标记+理由、
  每场管线状态：帧 fresh/stale/missing、各语言叙事状态、`actions_needed`）+ 配额账本。
  首页热点/战术室入口**不由 A1 写**——A1 只标记；A2 产出（short_title/public_teaser 本就在叙事
  契约里），经正常 bundle 上页。
- **失败模式**：API 不可用 → 输出 `degraded:true` 的扫描（复用上次 verification 并标 stale）；
  窗口内零赛程 → 合法空扫描。

### A2 · 赛前生成
- **触发**：运营对每个 key 场跑，目标窗口 T-24h…T-6h（`mvp2_ops.py prematch --fixture ID`）。
- **九步链（全现有脚本，逐步记入 run manifest）**：
  1 verify fixture → 2 ingest/refresh Scout Pack → 3 build trial frame →
  4 生成叙事 ×{zh-CN, vi-VN, my-MM}（DeepSeek 默认；Gemini 可选 benchmark）→
  5 生成 rescore 模型 ×3 语 → 6 独立 guard 全量复跑 → guard report 落盘 →
  7 拼装 send-kit `docs/data_audit/mvp2_send_kits/{ID}.prematch.md`——**仅由 guard-passed 的 LLM
  字段拼装**（operator_copy/social_post/group_join_copy/rescore teaser/reminder），沿
  TRIAL_SEND_PACKAGE 格式留 [群链接由运营填写] 位，无任何工程手写叙事 →
  8 登记队列条目（每工件×语言一条，`expires_at=kickoff`）→
  9 可选 `bundle` + 本地 build + 15 面可见扫描 + 部署（运营决定）。
- **输出**：帧、三语叙事+rescore 模型、guard report、send-kit、队列条目、run manifest。
- **失败模式**：单语言失败 → 其余语言照常上（§7）；guard 重试后仍 fail → 条目进 `needs_review`、
  永不 bundle；Scout Pack 预算超 → 阶段 abort，manifest 记 `blocked_budget`。

### A3 · 开球前 30 分钟重算
- **触发**：`mvp2_ops.py watch --fixture ID` 自 T-90（5 分钟轮询 + 本地告警）→ 首发一出自动跑
  `rescore`；手动 `mvp2_ops.py rescore --fixture ID` 等效。目标执行 T-45…T-35。
- **输入**：`/fixtures/lineups`（XI/阵型/门将）、`/injuries` 探针、`/fixtures`（状态校验）；
  原 trial frame + 原叙事判断 + 预生成 rescore 模型（rescore_decision_rules）。
- **新工程件 `scripts/mvp2_build_rescore_diff.py`（事实骨架，非叙事）**：把公布的 XI/GK/阵型与
  `team_baseline` 期望比对（GK 名单、中轴连续性、头号射手在否），评估哪些预生成 decision rules
  被触发，输出 facts-only 骨架。随后 LLM（现有 GEN + persona prompts）写重算更新：
  `what_changed[]`（before/now/effect）、`updated_lean/updated_risk_level/updated_score_range`
  （persona 参考区间句式）、无触发时 `no_change_note`、以及 **`group_update_message`——群内修正
  消息，即产品时刻**。按语言并行（决策 7）。
- **输出契约（新 surface `trial_rescore_update`）**：
  `docs/data_audit/mvp2_rescore_runs/{ID}.{lang}.{run_id}.json`，含 `based_on`（原判断 path +
  inputs_hash）、`lineup_facts`（内部块）、上述 LLM 字段、`expires_at=kickoff`、`guard_clean`。
  外加队列条目 + send-kit 更新节。页面更新：P0 仅评审包（决策 2c）。
- **失败模式**：T-15 仍无 XI → 运营只发 A2 预批的提醒/holding 模板（同 GO/NO-GO §2）；窗口内 LLM
  失败 → 同样仅模板，**未评审的修正永不发**；窗口内配额/429 → client 退避一轮后仅模板；
  **T-12 后 CLI 拒绝任何新生成（abort 线）**。

### A4 · 赛后复盘
- **触发**：终场后运营跑（状态 FT/AET/PEN），窗口 FT+45min…+12h（`mvp2_ops.py recap --fixture ID`），无 deadline 压力。
- **输入**：`/fixtures`（终比分/状态）、`/fixtures/events`、`/fixtures/statistics`、
  `/fixtures/players`（GK 评分/牌/换人/射门/控球）经 Scout Pack 刷新；**存档的赛前帧 + 赛前叙事
  （git 里真实留痕的判断）**。
- **新模式 `real_recap`（区别于现有 historical_recap）**：赛前判断是 git 时间戳存档的**真实预测**
  → 用「溯源要求」替代 replay 免责：internal_notes 必须引用存档赛前工件（path + inputs_hash +
  generated_at）。v0.2 因子构建器扩展出 trial fixture 的复盘因子帧（decisive/underweighted/
  verified/risk vs 实际结果），复用 recap 叙事生成器：抓对了什么 / 低估了什么 / 下次盯什么，
  persona 口吻，三语。
- **输出**：复盘因子帧、三语复盘叙事、recap send-kit、队列条目（无 kickoff 过期，supersede 过期）、
  静态 bundle + 重部署上页。
- **失败模式**：终场后 vendor 统计延迟（results=0）→ 30–60 分钟后重试，**绝不造数**；事件不全 →
  诚实 `missing_evidence` 降级（现有模式）。

### A5 · 运营评审队列
见 §5。状态（Owner 规定）：`generated / guard_passed / needs_review / approved / sent / expired`，
加终态卫生位 `rejected` 与 `superseded`（重生成永远 supersede，不改写历史）。

---

## 4. 数据工件结构（交付 ③）

目录布局（**粗体为新增**，其余沿用）：

```
docs/data_audit/
  mvp2_daily_scan/{YYYY-MM-DD}.json                      # A1（新目录）
  mvp2_ops_registry/
    key_match_overrides.json                              # 运营 override（新）
    {fixture_id}.manifest.json                            # per-fixture 各阶段 manifest（新）
  mvp2_ops_runs/{run_id}/run.json + guard_report.json     # per-run manifest（新）
  mvp2_review_queue/queue.json + items/{item_id}.json     # A5（新）
  mvp2_rescore_runs/{id}.{lang}.{run_id}.json             # A3 重算更新（新）
  mvp2_send_kits/{id}.{stage}.md                          # 拼装的运营 kit（新）
  mvp2_trial_prediction_frames/ · mvp2_trial_prediction_narratives/ ·
  mvp2_rescore_models/ · mvp2_product_proof_narratives/ ·
  mvp2_scout_pack_samples/ · mvp2_scoutscore_v0_2/        # 现有，不变
```

**per-fixture manifest**（`mvp2_ops_registry/{fixture_id}.manifest.json`）：

```jsonc
{
  "fixture_id": "1489371", "match": "Brazil vs Morocco",
  "kickoff_utc": "2026-06-13T22:00:00+00:00",
  "key_match": true, "key_reasons": ["marquee_pair_top12_elo"],
  "stages": {
    "verify":     {"run_id": "r20260612T0902Z-scan", "status": "ok", "artifact": "...", "generated_at": "..."},
    "scout_pack": {"run_id": "...", "status": "ok", "artifact": "...", "request_count": 9},
    "frame":      {"run_id": "...", "status": "ok", "artifact": "...", "inputs_hash": "sha256:..."},
    "prematch_narratives": {
      "zh-CN": {"status": "guard_passed", "provider": "deepseek", "artifact": "...",
                 "guard_report": "...", "queue_item": "...", "expires_at": "2026-06-13T22:00:00+00:00"},
      "vi-VN": {"...": "..."}, "my-MM": {"...": "..."}
    },
    "rescore_model":  {"zh-CN": {"...": "..."}, "...": "..."},
    "rescore_update": {"zh-CN": {"status": "approved", "run_id": "...", "fired_rules": ["favourite_spine_intact"]}},
    "recap":  {"...": "..."},
    "bundle": {"status": "deployed", "langs": ["zh-CN","vi-VN","my-MM"],
               "visible_copy_scan": "15/15 PASS", "deployed_at": "..."}
  },
  "lineups_released": false,
  "quota_ledger_day": {"date": "2026-06-13", "requests": 23, "daily_budget": 100}
}
```

**per-run manifest**（`mvp2_ops_runs/{run_id}/run.json`）：
`{run_id, job, fixtures, started_at, finished_at, git_rev, steps:[{name, script, args_redacted,
exit, artifact_paths, inputs_hash}], api_request_ledger:{count, by_endpoint},
llm_calls:{provider, attempts_by_lang}, guard_summary,
status: ok|partial|failed|blocked_quota|aborted_window}`；`run_id = r{YYYYMMDD}T{HHMM}Z-{job}`。

**评审队列条目**（`mvp2_review_queue/items/{item_id}.json`）：

```jsonc
{
  "item_id": "1489371.prematch.zh-CN.deepseek.r20260612T1410Z",
  "fixture_id": "1489371",
  "job": "A2_prematch",                  // A1_scan | A2_prematch | A3_rescore | A4_recap
  "surface": "trial_prediction",         // trial_prediction | trial_rescore | trial_rescore_update | recap | send_kit
  "language": "zh-CN", "provider": "deepseek",   // mock 条目永不可 approve
  "run_id": "r20260612T1410Z-prematch",
  "artifact_path": "docs/data_audit/mvp2_trial_prediction_narratives/1489371.zh-CN.deepseek.json",
  "artifact_sha256": "…",
  "guard_report_path": "docs/data_audit/mvp2_ops_runs/r20260612T1410Z-prematch/guard_report.json",
  "inputs_hash": "sha256:…",             // frame + prompt 文件 + 骨架 + git_rev 的规范哈希
  "status": "guard_passed",
  "status_history": [
    {"status": "generated", "at": "…", "by": "pipeline"},
    {"status": "guard_passed", "at": "…", "by": "guard"}
  ],
  "expires_at": "2026-06-13T22:00:00+00:00",   // 赛前 surface = kickoff；recap = null
  "approved_by": null, "review_note": null, "superseded_by": null,
  "sent_record": null                    // {at, channel, group, screenshot_path} — 运营经 CLI 填
}
```

`queue.json` 为再生成的索引（item_id → 状态摘要）；条目文件是 truth。**幂等**：同 `inputs_hash`
且已有 guard_passed 工件 → 编排器跳过重生成（`--force` 覆盖）；任何重生成都写新条目并把旧条目标
`superseded`，绝不改写历史。

---

## 5. 运营评审工作流（A5，交付 ⑤）— 状态机 + CLI

```
                  guard exit 0
 ┌───────────┐  ┌──────────────┐  运营 approve   ┌──────────┐  运营人工粘贴入群后登记  ┌──────┐
 │ generated │─▶│ guard_passed │───────────────▶│ approved │────────────────────────▶│ sent │
 └───────────┘  └──────────────┘                 └──────────┘                          └──────┘
       │ guard fail（best-effort 保留）  ▲              │
       ▼                                │ 运营复审       │   时钟 ≥ expires_at 即 sweep：
 ┌──────────────┐  运营 override        │ （--note 必填） │   未发出的赛前条目一律
 │ needs_review │────────────────────────┘              ▼   ┌─────────┐
 └──────────────┘                                           │ expired │（终态；禁止发送）
       │ reject              任意状态重生成 ─▶ 旧条目 superseded、└─────────┘
       ▼                     新条目从 generated 重新走
    rejected（终态）
```

**CLI 硬规则（由代码强制，不靠约定）**：
- `approve` 拒绝：mock 条目（llm_provider=mock）、已过期条目、**artifact_sha256 与文件不符的条目**
  （改文件即触发——落实 Owner「不得人工改写判断文案」；要改就重生成重新过 guard）。
- `mark-sent` 必填 `--channel --group --screenshot`，且只接受 `approved`；自动追加
  TRIAL_SEND_PACKAGE §9 发送记录表所需行。
- `sweep` 在每次 queue 命令前自动跑，开球即把赛前条目全部置 `expired`。
- `needs_review → approved` 必须 `--note`（override 理由进 status_history），对应先例
  「两次 label-only 后期修订记录于 internal_notes」。
- **CLI 不发送任何东西**；`sent` 是对人工动作的登记。

**CLI 面（P0）**：
```
mvp2_ops.py queue list [--fixture ID] [--status S]
mvp2_ops.py queue show ITEM
mvp2_ops.py queue approve ITEM --by NAME [--note "..."]
mvp2_ops.py queue reject  ITEM --by NAME --note "..."
mvp2_ops.py queue mark-sent ITEM --channel telegram --group "..." --screenshot PATH
mvp2_ops.py queue sweep
mvp2_ops.py status --fixture ID          # 渲染 per-fixture manifest 表格
```

---

## 6. 任务日程提案（交付 ② · P0 全部运营触发 · UTC）

**每日节奏**：

| 时间 | Job | 动作 |
|---|---|---|
| 09:00 | A1 | `scan` → 审阅扫描 JSON、确认 key 场、调 override |
| 09:30–16:00 | A2 | 逐 key 场 `prematch` → guard → 队列评审 → approve → 可选 bundle+部署 → send-kit 就绪 |

**比赛日（例：1489371，22:00 开球）**：

| 时刻 | 动作 |
|---|---|
| T-24h…T-6h | A2 完成且 approved；按 GO/NO-GO 允许赛前发送 |
| T-2h | 时效复查（verify lineups 仍 0 —— GO/NO-GO §0 的「2 小时陈旧规则」CLI 化） |
| T-90m | 启动 `watch`（5 分钟轮询；运营守在键盘前） |
| T-45…T-35 | XI 公布 → A3 自动跑（三语并行 ~4–8 分钟）→ guard → 运营评审 |
| T-30…T-20 | 运营发送提醒模板 + 已 approve 的 `group_update_message` |
| T-12 | abort 线：CLI 拒绝任何新 LLM 生成；此后仅模板 |
| T-0 | `queue sweep` —— 赛前条目全部过期；停发（现行规则） |
| FT+45m…+12h | A4 `recap` → guard → 评审 → bundle+重部署 → 复盘发送按既有 Owner 确认流程 |

P1（试用后、Owner 签字）：同一时间线，A3 页面刷新改走双模式端点而非重部署。
P2（Owner 基建审批）：Render cron 接管 A1 与 watch 启动；人工评审/发送时刻不变。

---

## 7. 失败 / 重试规则（交付 ④）

| 层 | 规则 |
|---|---|
| LLM 环内 | 维持现状：3 次（trial/rescore/update）/ 5 次（proof recap），guard-in-loop + STRICT RETRY 反馈 |
| LLM 编排级 | 每次 job 调用允许 1 次整体重跑（共 2 轮）。再失败：DeepSeek 不可用 → 可用 Gemini 生成，但条目强制带 `provider_fallback:true` 并进 `needs_review`（DeepSeek 仍是产品 provider；Gemini 产物只有运营显式 approve 才可用） |
| Mock 策略 | zh/vi mock 仅页面标记回退、永不可 approve/发送；**my mock 永不落盘**（现有硬规则，队列再兜一道） |
| API-FOOTBALL | 复用 client 守护（20s 超时、429 退避 ≤65s×2、单跑预算 200）。新增：分 job 预算（A1≈3 / A2≈15 每场 / A3≈4 / A4≈8）+ manifest 日账本 + `MVP2_AF_DAILY_BUDGET`（默认 100=免费档假设，**Owner 确认套餐档位**）。70% 警告；100% 即 `blocked_quota` 停——绝不造数据。watch 轮询计入预算（≤~12 次/场） |
| 语言独立 | my 失败 → 只上 zh/vi（前端 my 回退 en、永不 zh——现行政策，页面自然隐藏 my 入口）；vi 失败 → 上 zh；逐语言失败记入 manifest；首页热点只含 guard-passed 语言。**单一语言永不阻塞整场** |
| 开球窗口 abort | T-12 后禁新赛前生成；T-10 仍未评审完 → 仅发 A2 预批提醒模板；开球 sweep 全部赛前条目；「首发已出而页面未更新」→ 赛前发送停到重生成完成（Owner 条件 CLI 化：watch 置 manifest `lineups_released` 旗标，`queue approve` 对陈旧 trial_prediction 条目告警） |
| 幂等/重跑安全 | 生成器都是按 `{fixture}.{lang}.{provider}` 写文件；重跑覆盖工件但不改队列历史（新条目+supersede）；`inputs_hash` 短路未变更的重生成（`--force` 覆盖）；bundle 拷贝幂等且拒绝过期赛前工件与 guard-fail 文件 |
| 密钥卫生 | 密钥只走 `load_env_keys()`/client env；run manifest 记录参数时脱敏；提交前对新工件跑密钥形串扫描（`sk-`、`AIza`） |

---

## 8. Guard 清单（交付 ⑦ — 扩展而非替换现有门）

**机器门（编排器运行，写入 guard_report.json）**：
1. 叙事 guard `check_mvp2_product_narrative_guard.py` —— 全部叙事工件（现状基线 46/46）。
2. rescore 内联 guard（现有 check()），结果一并落盘。
3. **新 surface `trial_rescore_update` 规则**：必填字段（what_changed / updated_lean·risk·range 或
   no_change_note / group_update_message）；每条 what_changed 必须溯源到 fired_rule 或带
   assumption_flag；区间须带 persona 参考区间标记；沿用全部 forbidden/fake-prob/tone/de-model/URL
   禁令；Han=0（vi/my）；persona 在场。
4. **新模式 `real_recap` 规则**：internal_notes 必须引用存档赛前工件（path+hash+timestamp）；
   诚实度（非全中判定时 ≥1 条 missed/limit）；**马后炮禁腔**（「早就说过」/ "I told you so" 句式入禁列）。
5. bundle 后必跑可见扫描 `check_customer_visible_copy.py`（fixture 增加时扩 ROUTES）。
6. 过期戳：所有赛前工件带 `expires_at`；bundler + 队列双重强制。
7. 注册表完整性：artifact sha256 必须匹配；send-kit 只能由 guard-passed 路径拼装；mock 永不入 send-kit。
8. 链接政策：LLM 不写 URL（现有）；send-kit 只含 [群链接由运营填写] 占位。
9. 新工件密钥形串扫描（§7）。

**人工门（运营，记录于队列）**：persona 口吻自然（反馈 Q6「哪句像机器写的」回灌此处）；判断字段与
帧的 scoutscore_output 一致；无人工改写（sha 兜底）；截图与当前页面一致；GO/NO-GO §0 Owner 条件全绿。

---

## 9. 试用运营清单（交付 ⑧ — 并入 `docs/mvp2/TRIAL_GO_NO_GO_CHECKLIST.md` 新增「Track A 运行节」）

- [ ] 晨：A1 scan 已跑已审；key 场确认/override；配额账本 <70%。
- [ ] 每 key 场：A2 跑完；guard report 在档；三语队列全部评审（或部分语言决策已记录）；send-kit 仅由
      guard-passed 条目拼装；GO/NO-GO §0 Owner 条件仍全绿。
- [ ] T-2h 时效复查完成（lineups 仍 0 或已完成重生成）。
- [ ] T-90 watch 已启动；运营守到开球。
- [ ] A3 演练记录：XI 时刻 / 生成时长 / guard 结果 / 评审时长 / 发送时刻（每场一行——试用的核心时序证据）。
- [ ] 开球：queue sweep 已跑；确认无 approved-未发 赛前条目残留。
- [ ] 赛后：A4 跑完；复盘已评审；bundle + 15 面可见扫描 PASS 后才部署；复盘发送走既有 Owner 确认。
- [ ] 发送记录+截图入 TRIAL_FEEDBACK_FORM / `mvp2_trial_sends/`（不变）。
- [ ] 任何 guard override（needs_review→approved）连同 --note 列入当日记录。

---

## 10. 最小实施计划（交付 ⑥ — P0 获 Owner 批准后才动工）

**P0（下一冲刺；目标：批准后的下一个 key 场完成首次辅助运行）**

| 文件 | 内容 | 工作量 |
|---|---|---|
| `scripts/mvp2_ops.py` | 编排 CLI：scan/prematch/watch/rescore/recap/bundle/queue/status；run manifest；配额账本；abort 线 | 1.5–2 d |
| `scripts/mvp2_ops_queue.py` | registry + 队列库（条目、状态机、sweep、sha 校验） | 0.5 d |
| `scripts/mvp2_daily_scan.py` | A1 扫描 + key 规则 + override | 0.5 d |
| `scripts/mvp2_build_rescore_diff.py` | A3 首发对比骨架 + 重算更新 LLM 生成（复用 GEN + persona prompts） | 1 d |
| `scripts/mvp2_build_recap_frame_real.py`（或 v0.2 builder 加 `--real-recap` 旗标） | A4 真实复盘因子帧 | 0.5–1 d |
| `scripts/check_mvp2_product_narrative_guard.py` | 小扩展：trial_rescore_update + real_recap 规则（§8.3–8.4） | 0.5 d |
| 干跑演练 | 下一场 key 赛 A1→A5 全链路走一遍，时序记录 | 0.5 d |

合计 ≈ **5–6 人日**（最小裁剪 ≈4：A1 热点生成沿用 A2 字段、复盘帧用旗标复用 v0.2 脚本）。
注：**今晚揭幕场（19:00 UTC）继续走既有人工 GO/NO-GO 流程**；Track A 首个辅助目标是批准后的下一个
key 场（赶得上则 1489371 / 06-13，否则下一窗口）。

**P1（试用后，逐项需 Owner 签字）**：双模式叙事端点（API 形状变更）；`import.meta.glob` 打包；
GitHub Actions 仅作为手动 dispatch 远程 runner（密钥托管问题先行裁决；定时触发在 off-main 期间
结构性不可用）；评审队列镜像到后端表 + admin 端点（DB 扩展）。

**P2（规模阶段，Owner 基建审批）**：Render cron/worker 接管 A1 与 watch 启动；队列/管理 UI；
多联赛 A1。**所有人工评审/发送门不变。**

---

## 11. 明确不建（任何阶段，直至 Owner 另行裁决）

不自动发送到任何群/渠道（运营永远人工粘贴）。不公开发布；PR #3 保持 Draft；main 不动。
不碰支付/Token 经济。不扩容：不开 Render cron/worker/常驻进程、不加新服务（P0 watch 是运营
本机进程，不是基建）。P0 不做 DB-schema 扩展、不做 API 形状变更。LLM 不自动过审——guard pass
≠ 可发布，人工评审强制。my-MM mock 永不存在。密钥不进任何 CI secret store（除非 Owner 单独裁决）。
没有工程手写叙事——新 surface（rescore update / real recap）的客户语言作者仍然只有 LLM。
