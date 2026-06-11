# MVP-2 — Trial Product Path Review（试运营产品路径评审）

> **Date:** 2026-06-11 · **Sprint:** Trial Homepage + Detail + Single-Match Replacement ·
> **Branch:** `feature/mvp2-api-football-ingestion`（PR #3 Draft，main 未动）· operation paused。
> Verdict：**Engineer self-verify PASS** — 试运营产品路径已闭环：
> **Home → 战术室 → 详情分层 → 入群 / 临场 30 分钟修正**，旧 mock 不再出现在真实比赛之上。

## 1. 路径逐站验证

| 站点 | 实现 | 验证 |
|---|---|---|
| 首页首屏 | ① status strip「中文先知已生成**今日**赛前判断 · 临场 30 分钟将重新计算 · 数据同步 HH:MM」② hero「AI 足球情报社区 / **中文先知赛前模型** / 不只看胜率，更看为什么这样判断。」③ 主卡 Mexico vs South Africa（进入中文先知战术室 / 加入赛前情报群）④ 次卡 Brazil vs Morocco（即将开球） | DOM + 截图：首屏即真实比赛；旧 mock 0 出现 |
| 今日热点（Task E） | 「🔥 中文先知今日热点」= 4 条**真实内容入口**（hook 全部为 LLM short_title）：墨南战术室 · 巴摩战术室 · 855737 复盘 · 979139 复盘；无任何虚假互动数（旧 mock 热度区已入折叠） | 链接逐条可达 |
| 历史复盘 | 保留在真实比赛区之下，定位=模型校准证明 | 位置正确 |
| 旧 mock | 信号卡 + 今日列表 + 爆冷 TOP3 + 社区热度 + 战绩占位 + MTC loop tiles 全部收进「内部演示数据（mock）」折叠（默认收起）；底部合规行保留 | DOM：demo fold ✓ |
| CTA 深路由（Task B） | 「查看今日 AI 观点」全量替换为「**查看中文先知判断** / Xem nhận định Tiên Tri Bóng Đá」→ `/predict/1489369`；recap 页同；predict 页第二按钮=「**查看临场修正逻辑** / Xem cập nhật 30 phút trước trận」→ 页内锚点滚动到临场 30 分钟区；底部 nav「AI预测」→「中文先知 / Tiên Tri / Scout」→ /detail → 战术室 | DOM：`查看今日 AI 观点` 0 残留；无 CTA 回首页 |
| /detail 替换（Task C，方案 A） | `TrialDetailGate`：试运营流量 → **redirect `/predict/1489369`**；仅 `?demo=1`（内部演示折叠的行）可达旧 DetailPage | DOM：/detail 渲染战术室，**Qatar/卡塔尔 0 出现**；demo=1 旧页可渲染 |
| 战术室分层（Task D） | 顺序=Owner 规范：一句话判断(hero) → 主倾向 → 比分区间(模型估计) → 风险评级 → **三个关键变量**（top-3 展开 + 「更多变量(n)」折叠）→ 中文先知战术解读 → 临场 30 分钟重算(锚点) → **免费版 vs 完整版对照卡**（免费：主倾向/风险/部分变量 ·完整：全部变量/30 分钟重算/比分深析）+ LLM subscription_hook/group_join_copy → 入群 CTA → 内部折叠 | 截图 cta_area_*.png |
| 叙事归属 | 客户叙事 100% DeepSeek（guard-passed；hot hooks=short_title；判断/战术/修正/群文案全 LLM）；工程仅 schema/guard/render/标签 | guard 28+8 PASS |

## 2. 截图包（docs/qa_screenshots/mvp2_june11_trial/）

home_first_{zh,vi}.png（首屏）· home_realmatch_{zh,vi}.png（真实比赛区+热点全景）·
predict_1489369_{zh,vi}_v2.png（战术室分层）· cta_area_{zh,vi}.png（免费 vs 完整 + CTA）·
**detail_redirect_zh.png（/detail 已渲染战术室，无 Qatar/Ecuador）** · recap_calibration_zh.png（复盘=校准证明）·
（上轮 6 张 trial 截图保留）

## 3. 检查结果

build PASS（tsc+vite）· `git diff --check` clean · 0 console errors（home/predict/detail）·
**vi 可见文本 Han=0** · forbidden/博彩/保证词/胜率话术 0（guard 36 份全 PASS：28 product_proof + 8 trial）·
无假链接（群链接占位符 [群链接由运营填写]）· frontend 不调 vendor · 未公开运营 · 未接支付 · 未发群。

## 4. 残余事项
- 旧 DetailPage 仅服务内部演示（demo=1）；正式试运营若不需要可后续整页隐藏（Owner 决策）。
- 30 分钟重算仍为人工重跑管线；揭幕战 19:00 UTC 截止后主发素材自动失效（运营包 Do-NOT-send 已列）。
- mm 语言未做（vi 优先策略不变）。
