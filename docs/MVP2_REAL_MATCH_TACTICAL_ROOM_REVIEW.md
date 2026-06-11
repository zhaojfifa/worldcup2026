# MVP-2 — Real-Match AI Tactical Room: Operator Preview & Send-Readiness Review

> **Date:** 2026-06-11 (World Cup 2026 opening day) · **Branch:** `feature/mvp2-api-football-ingestion`
> (PR #3 **still Draft**) · **Operation: still paused — nothing has been posted anywhere.**
> Verdict (engineer self-verify): **READY TO SEND, pending Owner GO** (§5).

## 1. Pipeline proven end-to-end (Owner 链路 → 实现)

| Owner 链路 | 实现 | 状态 |
|---|---|---|
| 首页今日比赛 → 真实即将开赛比赛 | Home 新增「World Cup 2026 · 真实赛程 AI TACTICAL ROOM」strip（信号卡之后、今日比赛简表之前，原区块零改动），行内「今日开球/即将开球」chip → `/predict/:id` | ✅ |
| API-FOOTBALL 拉真数据 | `GET /fixtures league=1 season=2026` (HTTP 200, 72 fixtures) → 选 **1489369 Mexico–South Africa（揭幕战，今天 19:00 UTC，Estadio Azteca）** + **1489371 Brazil–Morocco（06-13，MetLife）**；`mvp2_ingest_scout_pack.py` Level-2 ingest（squads 26 人/coach/teams 真实；lineups/events/stats/injuries 赛前为空 → missing_evidence，未伪造） | ✅ |
| ScoutScore v0.2 建模 | `prematch_real_frame()`（`fixture_basis=real_scheduled`）：Kaggle Elo 快照（Mexico 1880 vs SA 1624 gap 256；Brazil 1964 vs Morocco 1899 gap 65）+ 近10场（**Morocco 7W-3D-0L 不败、仅失 3 球**）+ H2H（2010 揭幕 1-1；**Morocco 2-1 Brazil 2023**）+ 点球史 + 射手分布；首发/门将/战术 = assumption_context + live-30min triggers | ✅ |
| DeepSeek/Gemini 生成战术室 | 8 份（2 场 × zh/vi × 2 provider）**全真实 LLM、0 mock**；两家 vi 初稿再次写出 cửa trên，被 in-loop guard 拦截后重试通过 → guard 是必经层再次验证 | ✅ |
| 运营预览 | §3（operator_copy / social_post / group_join_copy / today_cta 全 LLM 生成，页面内部折叠同样可见） | ✅ |
| 截图验证 | `docs/qa_screenshots/mvp2_realmatch_tactical_room/`：home zh/vi（844 视口 + 1600 全景）、predict 1489369/1489371 zh/vi；DOM 校验 strip/比赛行/CTA/免责齐全；0 console errors | ✅ |
| 判断是否能发群/引导订阅 | §4 checklist + §5 verdict | ✅（READY，待 Owner GO） |

Guard 总态：**20/20 PASS**（12 旧样例 + 8 新战术室）。

## 2. 两场比赛的模型故事（数据全真实）

- **1489369 揭幕战 Mexico vs South Africa**：Elo 差 256 的「大热」，但模型风险评级=高（首发/伤病/xG 盲区
  ×大热=盲区陷阱），H2H 有 2010 揭幕战 1-1 的回声；比分区间 1-0/1-1/0-1（模型估计）。订阅钩子=开球前
  30 分钟首发重算。
- **1489371 Brazil vs Morocco**：Elo 仅差 65，摩洛哥近 10 场不败/仅失 3 球、2023 真实击败过巴西、点球史
  占优——「热门不稳」的中险叙事；区间 2-1/1-1/2-2（模型估计）。

## 3. 运营预览（全部 LLM 生成，guard-passed；链接由产品端注入，文案不含 URL）

**zh 群播（1489369）**
> 🇲🇽🇿🇦 墨西哥 vs 南非，ScoutScore 模型预警：Elo 差 256 分，但风险等级高！首发阵容和门将成最大变量，订阅用户将在开球前 30 分钟收到重算后的判断。入群看完整因子拆解 👉

**zh 群播（1489371）**
> 🇧🇷🇲🇦 巴西 vs 摩洛哥，ScoutScore 模型赛前判断：巴西 Elo 领先 65 点，但摩洛哥近 10 场不败、防守仅失 3 球，冷门风险中档。开球前 30 分钟，模型将根据首发 XI 重算倾向。入群看完整因子和临场更新。

**vi 群播（1489369）**
> 🔥 ScoutScore: Mexico mạnh hơn (Elo 1880 vs 1624), phong độ 10 trận 6 thắng, nhưng rủi ro CAO vì chưa có đội hình chính thức. South Africa có thể tạo địa chấn nếu Mexico thiếu trụ cột. Theo dõi bản cập nhật 30 phút trước giờ bóng lăn để biết chắc chắn! #WorldCup2026

**vi 群播（1489371）**
> ScoutScore: Brazil thắng nhờ Elo + phong độ, nhưng Morocco bất bại 10 trận, đã thắng Brazil 2023. Rủi ro trung bình. Đội hình chưa có – theo dõi bản cập nhật 30 phút trước giờ bóng lăn để biết chắc. Vào nhóm Telegram nhận ngay!

短帖（social_post）与入群文案（group_join_copy）、今日观点 CTA 均已生成（zh/vi 各 2 场），存
`docs/data_audit/mvp2_product_proof_narratives/14893*.json` 并渲染于页面内部折叠「运营素材」。

## 4. 发群 / 引导订阅 checklist

| 项 | 结果 |
|---|---|
| 博彩/保证词扫描（zh 投注/盘口/稳赚…；vi kèo/cửa trên/cửa dưới/nhà cái…；en odds/betting…） | ✅ 0 命中（guard + repo grep） |
| 无胜率/命中率话术；比分区间带「模型估计/ước tính」 | ✅ |
| 无编造事实（伤病/xG/首发未公布 → assumption_flag + 内部披露「首发未公布」） | ✅ guard 强制（real_scheduled 分支） |
| 免责声明（历史表现不代表未来结果…）在页 | ✅ 3 页渲染 |
| vi Han=0（narrative 全文件） | ✅ guard |
| 订阅/入群 CTA 自然、无收益承诺；30 分钟重算=核心钩子 | ✅ |
| 截图可用、页面无 console error、build PASS | ✅ |
| 内容时效（揭幕战今日 19:00 UTC 开球） | ⚠️ 开球后此条转为复盘素材；发群窗口=赛前 |

## 5. 判断（engineer）

**能发群 / 能引导订阅：READY。** 文案合规、有真数据钩子（Elo 256 / 摩洛哥不败）、有明确订阅理由
（开球前 30 分钟重算）。**但 operation 仍是 paused 状态——本轮没有发出任何内容**；实际发群需要：
1. **Owner GO**（解除本场景的运营暂停，或批准单次试发）；
2. 操作者在 Telegram 群手工粘贴（文案不含链接，入口由群上下文自带）；
3. 若要发 vi：Zalo 仍 pending，Telegram 群可用；
4. 注意揭幕战时效窗口（开球前发出，否则改用 855737/979139 复盘素材 + 1489371 预热）。

已知小瑕疵（不阻塞）：1489371 internal_notes 回显了一段英文工程指令（仅内部折叠可见）；订阅层
（支付/Token）本轮未触碰——CTA 指向社群与今日观点，无价格表述。

## 5b. ★ Frontend Deployment Truth Check（2026-06-11 02:50 UTC，Owner 人工验证 FAIL 后复查）

**结论：代码/构建/线上 bundle 三层全部包含本轮功能；Owner 验证 FAIL 的原因 = 部署时间窗口。**
push `22a4f52` 在 **00:48 UTC**，Render 线上产物 `last-modified` = **02:44:09 UTC**（部署延迟约 2 小时）；
Owner 在 02:44 之前验证 → 看到旧 bundle（属实）。02:50 UTC 复测已翻转：

| 层 | 证据 | 结果 |
|---|---|---|
| Git | 本地 HEAD = 远端 feature 分支 = `22a4f52`；PR #3 Draft/OPEN/未 merge；`origin/main = e372616`，`merge-base --is-ancestor` 证明 22a4f52 不在 main | ✅ |
| 源码 | `UpcomingTacticalStrip.tsx`（'World Cup 2026 · 真实赛程' + 'AI TACTICAL ROOM' 分属两个 span——grep 连续串「真实赛程 AI」不命中是检索词问题，非缺码）；HomePage 已挂载；1489369/Mexico 在 src | ✅ |
| 本地 dist | `npm run build` → `index-DgoxAbWb.js` 含 真实赛程/Mexico/1489369/Brazil | ✅ |
| 线上 bundle | `index-DDGqZfVZ.js`（02:44 UTC 部署）grep 全部命中：1489369 ·Mexico · 真实赛程 · AI TACTICAL ROOM · 1489371 · Morocco（JS hash 与本地不同属构建环境差异，内容为准；CSS hash 与本地完全一致） | ✅ |
| 线上渲染 | headless Chrome dump-dom + 截图 `live_home_zh_22a4f52.png`：strip + Mexico（今日开球）+ Brazil（即将开球）全部渲染；旧 mock 信号卡/列表按要求保留 | ✅ |
| 深链 | `/predict/1489369` `/predict/1489371` `/recap/855737` 直接访问 **HTTP 404** —— Render dashboard SPA rewrite（`/* → /index.html`）仍未配置（2026-06-10 已记录的 operator 待办）；从首页点击进入（client-side 路由）不受影响 | ⚠️ |
| 缓存注意 | `cf-cache-status: HIT` + `s-maxage=300`：边缘缓存最长 5 分钟 + 浏览器缓存可能继续短暂呈现旧页 — Owner 复验请强刷或带 `?v=22a4f52` | ⚠️ |

Render dashboard 侧（分支绑定确认 / latest deploy commit 显示 / Clear build cache 按钮）需 operator 在
dashboard 核对——但从行为可推断：frontend service 绑定 feature 分支且 auto-deploy 生效（push 后自动出现
含本轮内容的新产物）。backend `/api/v1/health` 正常（`ai_provider=mock`、合规 flags 关闭）。

## 6. 工件清单

Scout Packs `docs/data_audit/mvp2_scout_pack_samples/{1489369,1489371}.json` · frames
`docs/data_audit/mvp2_scoutscore_v0_2/{1489369,1489371}.factor_frame.json` · narratives ×8
`docs/data_audit/mvp2_product_proof_narratives/14893*` · 页面 `/predict/{1489369,1489371}` + Home strip ·
截图 `docs/qa_screenshots/mvp2_realmatch_tactical_room/` ×8 · guard 20/20 PASS。
