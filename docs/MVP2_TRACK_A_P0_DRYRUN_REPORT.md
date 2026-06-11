# MVP-2 Track A P0 · 干跑报告（fixture 1489371 Brazil vs Morocco）

> 执行日 2026-06-11（UTC 15:14–15:35）· 分支 `feature/mvp2-api-football-ingestion` · A-GO-1 范围。
> 原则：真实数据真实跑；跑不到的环节**诚实标记 blocked_by_time_or_data**，不造数、不发送、不部署。

## 1. 干跑命令序列（全部真实执行）

| # | 命令 | 结果 |
|---|---|---|
| 1 | `python3 scripts/mvp2_ops_queue.py --selftest` | 队列状态机自测 **12/12 PASS**（sha 防篡改 / mock 拒批 / 过期拒批 / needs_review 需 note / sweep / supersede） |
| 2 | `python3 scripts/check_mvp2_product_narrative_guard.py --selftest-tracka` | 新 guard 规则自测 **6/6 PASS**（real_recap 溯源 ±、马后炮禁腔、rescore_update ±3） |
| 3 | `python3 scripts/mvp2_ops.py scan` | A1 真实扫描：today=1 / next=2 / **key=2**（1489369 揭幕+东道主 → 仅剩 watch 动作；**1539000 Canada vs Bosnia & Herzegovina 06-12 host_nation → 需 A2**）→ `mvp2_daily_scan/2026-06-11.json` |
| 4 | `python3 scripts/mvp2_ops.py prematch --fixture 1489371 --register-existing` | A2 注册路径（Owner 干跑指定）：**6 工件 6/6 guard-clean 注册**（叙事×3 + rescore 模型×3，expires=06-13T22:00Z）+ send-kit 拼装 |
| 5 | `python3 scripts/mvp2_ops.py watch --fixture 1489371 --once` | T-3285min 探针：NS · lineups=0 → 窗口未到，exit 0 |
| 6 | `python3 scripts/mvp2_ops.py rescore --fixture 1489371` | **blocked_by_time_or_data**（lineups not posted yet）· run manifest `r20260611T1515Z-rescore` · exit 2 · 未写任何工件 |
| 7 | `python3 scripts/mvp2_ops.py recap --fixture 1489371` | **blocked_by_time_or_data**（status NS — recap runs after FT/AET/PEN）· run `r20260611T1515Z-recap` · exit 2 |
| 8 | `python3 scripts/mvp2_ops.py status --fixture 1489371` / `queue list` | manifest 表 + 队列条目（含 expires）正常渲染 |
| 9 | 重注册（见 §3 修复后）`prematch --register-existing` ×2 | 旧条目 **superseded**、新条目 guard_passed（状态机不改写历史，实证） |
| 10 | `mvp2_ops.py bundle` ×4 fixtures | 1489369/1489371 各 copied 6、855737/979139 各 copied 3，refused none |
| 11 | `npm run build` + 15 面可见扫描 | **BUILD PASS · VISIBLE-COPY 15/15 PASS**（硬化正则后） |

A3/A4 的 LLM 生成环节因**时间与数据现实**（首发未公布 / 比赛未结束）无法在干跑日真实执行——
按 Owner 指令以 blocked manifest 诚实记录；代码路径已由 §1#6/#7 的阻塞分支 + guard 自测向量覆盖。
1489371 开球（06-13 22:00 UTC）时即为 A3/A4 的首次真实运行窗口。

## 2. 干跑产出工件

- `docs/data_audit/mvp2_daily_scan/2026-06-11.json`（A1，真实 API）
- `docs/data_audit/mvp2_ops_registry/{1489369,1489371,1539000}.manifest.json`（per-fixture manifest + 配额账本 3/100）
- `docs/data_audit/mvp2_ops_runs/r20260611T*/run.json`（scan / prematch×3 / rescore-blocked / recap-blocked / bundle×4 / watch — **失败与阻塞同样有 manifest**）+ prematch run 的 `guard_report.json`
- `docs/data_audit/mvp2_review_queue/`（queue.json + 24 条 items：12 现行 guard_passed + 12 superseded 历史）
- `docs/data_audit/mvp2_send_kits/{1489369,1489371}.prematch.md`（**只引用 guard-passed LLM 字段原文**；[群链接由运营填写] 占位；expires 头）
- `docs/data_audit/mvp2_rescore_runs/`：空（正确——A3 被时间阻塞，**guard 不过/未运行就不落盘**）

## 3. 干跑发现并修复的问题（含一个真实合规缺口）

| # | 发现 | 处置 |
|---|---|---|
| F1 | **`\bAI\b` 正则在 CJK 相邻时失效**（Python `\w` 含汉字 → 「今日AI观点」「每日多场AI战术解读」绕过 de-model 扫描）——4 份 zh 叙事（855737/979139/1489369/1489371）的客户字段携带 AI 字样，部分在 zh 页面真实可见。**这是 Owner de-AI 红线的实际缺口，由 send-kit 拼装时暴露** | 三处正则硬化为 ASCII 环视 `(?<![A-Za-z0-9_])AI(?![A-Za-z0-9_])`（叙事 guard 两个检查器 + 可见扫描）+ rescore 内联 gate 补 AI 检查；4 份 zh 叙事 DeepSeek 重生成 → 独立 guard 4/4 PASS → 重注册（supersede）→ 重打包 → build + 15 面扫描全 PASS。vi 小写 ai（=谁）不受影响 |
| F2 | 重生成首轮 5 次重试全败：**prompt 自冲突**（zh prompt schema 注释仍示例「今日 AI 观点」，与 de-model 硬规则相抵；与上轮 sprint 记录的教训同型） | 修 prompt 本身（3 处：hero 示例 / today_cta 注释 / operator_copy 用语）→ 重生成 1-2 次尝试即收敛 |
| F3 | rescore **model**（surface=trial_rescore）被叙事契约 `check_obj` 误判 needs_review；且落盘 meta（`model:"deepseek-chat"`）会误触 de-model 扫描 | ops 增加 `_check_artifact` 按 surface 分发：trial_rescore → 复用 rescore 生成器自己的 `check()`（剥离落盘 meta 后校验）；trial_rescore_update → 新检查器；其余 → check_obj |
| F4 | `bundle` 命令同病（直接 check_obj）+ **PROOF 目录旧版 proof-sprint 叙事覆盖了 FE 的 trial 版**（同名目标二次写入） | bundle 改用 `_check_artifact` + 同一目标本轮只写一次（NARR 优先于 PROOF）；重打包后实证 FE 文件 voice=qiuge_v2 / surface=trial_prediction |

## 4. 最终门禁状态（干跑结束时）

队列自测 12/12 · Track A guard 自测 6/6 · 叙事 guard 全量回归 **GUARD PASS**（proof+trial 全部文件，
含重生成的 4 份 zh）· rescore 12 文件 guard_clean · **BUILD PASS** · **可见扫描 15/15 PASS（硬化正则）**。
未发送任何消息；未部署；PR #3 Draft；main 未动。

## 5. 下一步（运营/Owner）

- 06-12：`scan` 后对 **1539000（Canada vs Bosnia & Herzegovina）跑首次全链 A2**（非 register-existing 的完整生成路径首演）。
- 06-13（1489371）：T-2h `watch --once` 复查 → T-90 `watch` 常驻 → 首发出 → **A3 首次真实运行** →
  评审 → 人工发送 → 开球 sweep → 赛后 **A4 首次真实运行**（A3 演练时序记录 = 试用核心证据）。
- 部署（含重打包后的 zh 修复上线）需 Owner 按既有流程单独确认。
