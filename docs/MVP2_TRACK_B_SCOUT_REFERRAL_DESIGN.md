# MVP-2 Track B — 合规球迷增长 / 情报官推荐机制（重型设计 · DESIGN ONLY）

> **状态：设计稿，未实施。** Owner 批准本设计前不写任何运行时代码、不加表、不加端点、不改 guard。
> 产品名：**俅哥情报官 / Cộng tác viên Tiên Tri Bóng Đá / Football Oracle Scout**。
> 分支 `feature/mvp2-api-football-ingestion` · PR #3 Draft · main 不动 · 公开运营 paused · 仅小范围私域试用。
> 覆盖 Owner 九项交付：①产品决策 ②机制映射表 ③数据 schema ④前端 UX ⑤运营工作流
> ⑥奖励/积分规则 ⑦风险登记册 ⑧Guard 更新计划 ⑨最小试用实施计划。

---

## 1. 产品决策（交付 ① — 博彩代理参考如何改造为内容推荐）

**从参考机制保留的只有结构**：每个分享者一条专属链接/二维码、下游行为归因到分享者、周期性表现
汇总、以及「平台侧签发的高级链接」这条路径的**形**。

**硬拒（Owner 明令，逐条入 guard 与 schema 设计）**：充值返佣、输赢分成结算、博彩代理层级
（下线）、盘口/赔率推广、提现/收益承诺、「客服发博彩代理链接」；customer-facing 永不出现
投注/博彩/赔率/盘口/充值/输赢返点/亏损抽佣/月结佣金等词。

**改造后的概念**：分享者不是从玩家资金流抽成的"代理"，而是**内容情报官**——把朋友带到
**内容页**（home、/predict/1489369、/predict/1489371、群落地页 /community、recap 页），
赚的是**平台积分（MTC）、试用解锁、社区徽章、群内角色、早期访问**（MTC 不可提现/转让/交易，
现有合规地板不变）。被归因的价值是**注意力与参与**：点击、有效访问、入群、重算阅读、反馈、
赛后回访——**永远不是钱的进出**。"结算"改为**周增长报告**：只有计数，没有金额字段。
「联系客服申请高级代理链」改造为**运营签发的 campaign 链接**：内部运营（不是"客服"）为特定
比赛/群创建命名 campaign 链接——这是内容分发工具，**没有更高费率层、没有特权梯队**。

**为什么在本代码库上结构성成立（复用证据）**：闭环已经半存在——
`TokenLog.event_type` 已枚举 `share`/`invite`（`backend/app/models/token.py:47`）、
`config.py` 已定价 `mtc_share_reward=50` / `mtc_invite_reward=100`、TokenPage 已有分享/邀请任务位
（当前仅本地 completeTask）、`MatchEngagement` + `POST /events/track` 已是无 IP 匿名计数、
`/internal/scout-pack` 已确立 admin-token 门控的内部运营页模式。Track B 补的是归因层与运营评审面。

**身份决策（关键，按试用现实如实设计）**：现状 `DEMO_USER_ID=1` 硬编码
（`frontend/src/store/useAppStore.ts:9`），无登录。因此：
- **P0（对 ≤1 群试用诚实可信）：只做运营签发 invite_code。** 运营为可信用户/群签发码
  （"vi-group-A" / "trusted-fan-Minh"）。每码自动建 **shadow User**
  （`User.device_id="scout:<CODE>"`，nickname=别名），人工奖励经现有
  `wallet_service._credit` 写**真实 TokenLog**。被签发者在 MTC 页经码绑定的 summary 端点看到
  自己的记录（码存其浏览器 localStorage），无需登录。**不做假的"人均链接"**（那会把一切归因到
  user 1）。
- **P1（需 Owner 再批）：轻量自助码。** 前端生成稳定随机 UUID（localStorage `gc_device`），
  后端按 device_id get-or-create User，`POST /referrals/links` 绑定个人码。仍无密码/无 PII。

**命名**：zh **俅哥情报官**（与现有 `scoutVerdictTitle: '情报官结论'` 同脉）；
vi **Cộng tác viên Tiên Tri Bóng Đá**（Owner 原文"Tiên Tri cộng tác viên"，自然越语语序为
角色前置——已报 §14 命名归口确认）；my **Football Oracle Scout**（沿 §15 临时英文人格；CTA 缅语
动词短语 "Football Oracle Scout ဖြစ်ရန်"）。**代理 / agent / referral 永不出现在 customer-facing**
（内部代码与 admin 路由可用 referral）。

---

## 2. 机制映射表（交付 ②）

| # | 博彩代理原机制 | 拒绝部分 | 批准的足球内容等价物 |
|---|---|---|---|
| 1 | **注册**：平台为玩家自动生成链接/二维码 | 把用户注册为*博彩代理*；带资金归因的人均链接 | 邀请链接/二维码**只指向产品页**（`/`、`/predict/1489369`、`/predict/1489371`、`/community`、`/recap/*`）。P0 运营按可信粉丝/群签发码；P1 设备匿名身份自助码。target_path 服务端白名单校验 |
| 2 | **分享**：链接/二维码分享给朋友/社交软件 | （结构保留）分享本身没问题；拒绝的是分享文案中的博彩钩子 | 仅可用**运营包定稿文案**（§6b/§7/§15）+ 追加 `?ref=CODE&c=CAMPAIGN&lang=`。分享文案与 campaign 标题发送前过禁词 lint |
| 3 | **代理费**：点链接/扫码 → 注册、**充值**记到代理名下 | 充值返佣；一切资金流归因 | **归因事件**记到码名下：click / valid_visit / viewed_predict_page / viewed_rescore_section / joined_group / submitted_feedback / returned_after_match。计数喂 MTC 积分/解锁/徽章——**永远不是任何东西的百分比，没有钱进来** |
| 4 | **结算**：普通代理即时返现；高级代理每月 2 号按玩家**输赢的 ~30%** 结算 | 输赢抽佣、月度博彩结算、提现 | **周增长报告**（只有计数）：点击、有效访客、入群、判断页阅读、重算阅读、反馈数、获得 MTC、解锁通行证。没有"结算"、没有支付；**schema 里根本不存在充值/输赢/payout 字段** |
| 5 | **「联系客服申请高级代理链接」** | 客服签发的博彩代理条款；特权佣金层 | **运营签发 campaign 链接**：内部运营经 admin 端点（x-admin-token）创建命名 campaign（墨西哥-南非赛前 / 巴西-摩洛哥赛前 / 赛后复盘 / vi 群 / my 群）。是分发工具 + 评审日志，**没有更优"费率"、之上没有层级** |
| 6 | **代理层级**（代理发展下线、佣金逐层上抽） | 整个多层结构 | **扁平的个人成长等级**（Scout L1/L2/L3/Captain），只凭本人分享质量。无下线、不继承他人活动、不为利益招募其他情报官。等级只给非货币权益 |

---

## 3. 数据 Schema 提案（交付 ③）

**裁定：事件形数据用 DB 表，不用 JSON 工件**——去重与可疑标记需要查询；加表走现有
`Base.metadata.create_all` 模式零成本（新 model 文件 + `models/__init__.py` 一行 import，无
alembic）。JSON 工件**只用于周报快照**（沿 `docs/data_audit/*` 审计文化）。新增一个 model 文件
`backend/app/models/referral.py` + 一行 import。
（注：建表+端点属 DB/API 扩展，**P0 动工前需 Owner 批**——见 §9。）

### 3.1 `referral_campaigns`
| 列 | 类型 | 说明 |
|---|---|---|
| id | int PK | |
| campaign_key | String(60) unique index | 如 `mex-rsa-prematch` / `bra-mar-prematch` / `postmatch-recap` / `vi-group` / `my-group` |
| title_internal | String(200) | 内部标题；**创建时过禁词 lint（权威）** |
| target_path | String(200) | 必须 ∈ 代码常量 `REFERRAL_TARGET_ALLOWLIST = {"/", "/predict/1489369", "/predict/1489371", "/community", "/recap/855737", "/recap/979139"}` |
| locale | String(5) | zh / vi / my |
| status | String(20) | draft / active / paused / archived |
| created_by | String(60) · starts_at/ends_at DateTime? · notes Text? · created_at/updated_at | 沿 MatchEngagement 默认 |

### 3.2 `referral_links`
| 列 | 类型 | 说明 |
|---|---|---|
| id | int PK · invite_code String(20) unique index | 8 位、无歧义字母表（无 0/O/1/I） |
| campaign_id | FK nullable index | P0 链接必有；P1 个人码可无 |
| inviter_user_id | FK users.id nullable index | P0 shadow user `device_id="scout:<CODE>"`；P1 设备绑定真实用户 |
| inviter_alias | String(60) | 显示名："vi-group-A" / "trusted-fan-Minh" |
| owner_device_hash | String(64) nullable | 自点排除（持码人设备首次认领时写入） |
| link_type | String(20) | `operator_campaign`（P0）/ `user_invite`（P1） |
| status | active / paused / revoked · created_at/updated_at | |

### 3.3 `referral_events`
| 列 | 类型 | 说明 |
|---|---|---|
| id · link_id FK index · invite_code String(20) index（冗余便查） · campaign_id FK? index | | |
| event_type | String(30) | 集合 `REFERRAL_EVENTS = {click, valid_visit, viewed_predict_page, viewed_rescore_section, joined_group_click, joined_group_confirmed, submitted_feedback, returned_after_match}`（镜像 schemas/social.py 的 VALID_EVENTS 模式） |
| target_path · locale | | |
| device_hash | String(64) | 客户端随机 UUID 的加盐 SHA-256。**永不存 IP、永不存 UA**（沿 MatchEngagement 的隐私承诺原文） |
| event_date | String(10) | YYYY-MM-DD（去重键成分，沿 last_checkin_date 惯例） |
| is_self_click | Bool 默认 False | device_hash == link.owner_device_hash |
| is_suspect | Bool 默认 False | 突发流量启发式（§7 R4） |
| counted | Bool 默认 True | 去重/自点/可疑排除时置 False——**行保留供审计，不设唯一约束**；counted 在插入时按「当日同 (invite_code, device_hash, event_type, event_date) 无已计行」计算 |
| created_at | | |

### 3.4 `referral_rewards`
| 列 | 类型 | 说明 |
|---|---|---|
| id · link_id/invite_code · user_id FK?（收奖的 shadow/真实情报官） · recipient_alias | | |
| reward_type | String(30) | `mtc_points` / `trial_unlock` / `community_badge` / `early_access` / `group_role` / `manual_note`。**不存在任何现金类型** |
| amount | int 默认 0 | MTC 数或解锁次数 |
| status | proposed / granted / rejected | |
| token_log_id | FK token_logs.id nullable | MTC 实际经 `wallet_service._credit` 入账时回填——与现有账本的硬审计链接 |
| granted_by · reason · created_at/granted_at | | |

### 3.5 `scout_profiles`（表现在就定义；**P1 才填充**——P0 等级仅展示/人工）
id · user_id FK unique? · alias · primary_invite_code · level int(0/1/2/3/4) ·
level_name(scout_l1/l2/l3/scout_captain) · **level_granted_by（永远是运营 handle——无自动授予）** ·
total_clicks/valid_visitors/group_joins/feedback_count（缓存，truth=referral_events）· locale ·
joined_at · notes

### 3.6 `operator_review_logs`
id · subject_type(campaign/link/event/reward/level) · subject_id ·
action(flag_suspect/clear_suspect/grant_reward/reject_reward/grant_level/revoke_link/note) ·
operator · detail · created_at

**与现有模型的关系**：`referral_links.inviter_user_id → User`；
`referral_rewards.token_log_id → TokenLog`（MTC 写入全部走现有
`backend/app/services/token/wallet_service.py:42` 的 `_credit`，复用 token.py:47 已注册的
`"invite"/"share"` 事件类型与 config 定价）。`MatchEngagement` 不动——referral 事件是独立的、
按码 scope 的流；现有匿名 safeTrack 并行照跑。

**config 增项**（`backend/app/config.py`）：`enable_referral_program: bool = False`
（合规旗标模式——默认关，仅试用环境打开）、`referral_hash_salt: str = ""`、
`referral_valid_visit_dwell_seconds: int = 10`、`referral_suspect_device_clicks_per_day: int = 5`、
`referral_suspect_code_clicks_per_day: int = 20`、`referral_daily_group_join_reward_cap: int = 3`。

---

## 4. 前端 UX 提案（交付 ④ — 全部藏在试用旗标后，三语）

**试用旗标**：新 `?scout=1` URL 旗标持久化到 `localStorage gc_scout`（沿 `?demo=1`
TrialDetailGate / `?ops=1` PredictPage 模式）。所有情报官 UI 仅当旗标置位**且**服务端
`enable_referral_program=true` 才渲染（track 端点关闭时返回常形 ok:false）。

| 面 | 改动 | 文案（zh / vi / my） |
|---|---|---|
| `Layout.tsx` | `useReferralCapture()` hook：挂载即读 `?ref=` + `?c=` → 存 localStorage（gc_ref/gc_campaign/gc_ref_at）→ fire-and-forget `POST /api/v1/referrals/track {code, campaign_key, event_type:"click", path, locale, device_uuid}`（`api/client.ts` 克隆 safeTrack 为 `safeTrackReferral`）。**先于 TrialDetailGate 跳转执行**，归因在 /detail→/predict/1489369 重定向中存活 | （不可见） |
| `HomePage.tsx` | hero 下入口卡，旗标门控 | 成为俅哥情报官 · 分享判断，赚 MTC 积分 / Trở thành Cộng tác viên Tiên Tri Bóng Đá · chia sẻ nhận định, nhận điểm MTC / Football Oracle Scout ဖြစ်ရန် · အမြင်မျှဝေပြီး MTC ပွိုင့်ရယူပါ |
| `PredictPage` / `ProductProofViews` | (a) 分享 CTA（旗标门控）：复制当前 URL+绑定 `?ref=`+`?lang=` 到剪贴板，记现有 click_share + referral click（自点抑制）；(b) 10s 驻留计时 → `valid_visit`；现有 `<div id="rescore"/>` 上挂 IntersectionObserver → `viewed_rescore_section` | 分享本场判断，获得 MTC 积分 / Chia sẻ nhận định trận này, nhận điểm MTC / ဒီပွဲအမြင်ကို မျှဝေပြီး MTC ပွိုင့်ရယူပါ |
| 群 CTA（ProductProofViews joinGroup + CommunityPage） | 副标一行 + 存在 ref 时记 `joined_group_click` | 邀请朋友进群看 30 分钟临场修正 / Mời bạn vào nhóm xem hiệu chỉnh 30 phút trước giờ đá / မိတ်ဆွေတွေကို အဖွဲ့ထဲဖိတ်ပြီး မိနစ် ၃၀ ပြန်တွက်ချက်ကြည့်ပါ |
| `TokenPage.tsx` | 新「邀请记录」区（旗标门控）：显示绑定码 + `GET /api/v1/referrals/links/{code}/summary`（点击/有效访客/入群/已得 MTC/通行证）。复用现有卡片样式；合规行复用 `t.mtcStatement` | 我的邀请记录 / Lịch sử mời của tôi / ကျွန်ုပ်၏ ဖိတ်ကြားမှတ်တမ်း |
| `RecapDetailPage.tsx` | 存在 gc_ref → 记 `returned_after_match` | （不可见） |
| `i18n/dict.ts` + `copy/en.ts` + `copy/mm.ts` | ~12 个新键 ×4 层。**vi/my 必须全量——回退是 en，永不 zh**（FALLBACK_CHAIN 现行） | 同上 |

现有 TokenPage 分享/邀请任务位（mock.ts 本地 completeTask）P1 才接真流程；P0 保持展示位，
避免双重计奖混淆。

**QR 裁定：运营工具脚本** `scripts/mvp2_generate_referral_qr.py`（python `qrcode` 库，本地出 PNG
给运营发；可选 `--upload` 经现有 `r2_client.upload_asset` 传 `share-cards/referral/{code}.png`）。
理由：试用规模 QR 是运营需求；客户端 JS 库白白增大 bundle；服务端端点是零收益的新攻击面。
P1 自助链接上线再议。

---

## 5. 运营工作流（交付 ⑤）

全部 admin 端点沿 `require_admin` x-admin-token 依赖（admin.py:19）；看板沿 `/internal/scout-pack`
门控模式（dev 开放、生产 admin token；无公开导航、noindex）。

1. **建 campaign** — `POST /api/v1/admin/referrals/campaigns` `{campaign_key, title_internal,
   target_path, locale}`。服务端拒绝：target 不在白名单；标题含任何禁词（§8）——**创建时 lint 为
   权威**，脚本 lint 是第二道。试用期 campaign 计划：`mex-rsa-prematch`（→/predict/1489369）、
   `bra-mar-prematch`（→/predict/1489371）、`postmatch-recap`（→/recap/855737）、
   `vi-group`（→/community, vi）、`my-group`（→/community, my）。
2. **签发链接** — `POST /api/v1/admin/referrals/links` `{campaign_key, inviter_alias,
   create_shadow_user:true}` → 返回 invite_code + 完整 URL
   （`{app_base_url}{target_path}?ref=CODE&c=KEY&lang=LOCALE`）。自动建 shadow User + 钱包。
3. **分发** — 运营把链接缀到**未改动的运营包定稿文案**之后（运营包既有规则「文案原样复制，仅替换
   群链接」延伸为：**只有链接位可变**）。可选脚本出 QR。
4. **监控** — `GET /internal/referrals` 服务端渲染只读 HTML 看板：campaign 表、每码统计
   （点击/独立设备/有效访问/重算阅读/入群点击/可疑数）、等级达标提示（L1/2/3 阈值实时算）、
   待发奖提案、近期评审日志；页面印出 curl 配方（同 scout-pack 哲学）。
5. **确认入群** — 运营人工核对 Telegram 成员列表后
   `POST /api/v1/admin/referrals/events/confirm` `{invite_code, event_type:"joined_group_confirmed",
   count, note}`（写事件 + 评审日志）。
6. **发奖（人工奖励路径）** — `POST /api/v1/admin/referrals/rewards/grant`
   `{invite_code, reward_type, amount, reason}` → 写 referral_rewards(status=granted) +
   operator_review_logs；`reward_type=mtc_points` 时调现有
   `wallet_service._credit(db, wallet, amount, "invite"|"share", note=f"scout:{code} review:{log_id}")`
   → 真实 TokenLog 行，token_log_id 回填。上限在此强制（§6）。
7. **滥用评审** — 可疑行在看板呈现；flag_suspect/clear_suspect 动作写评审日志。可疑/自点行
   **永不计入**等级与发奖资格。
8. **每周** — 跑 `scripts/mvp2_build_referral_weekly_report.py` →
   `docs/data_audit/mvp2_referral_weekly/2026-Wnn.json` + `.md` 表（Owner 异步审阅；看板看实时数，
   工件是不可变记录）。

---

## 6. 奖励 / 积分规则表（交付 ⑥ — 任何地方都没有现金）

| 动作 | 奖励 | 日上限 | 反滥用条件 |
|---|---|---|---|
| 分享战术室/复盘链接（确实发到群） | +50 MTC（mtc_share_reward） | 1/日/情报官 | P0 运营看到帖子后人工发；自动化最早 P1 且服务端确认 1/日 |
| 朋友点击链接 | 0 MTC——只计 L1 | 按 (code, device, day) 计一次 | 自点排除；突发流量阈值标记 |
| 朋友成为有效访客（判断页驻留 ≥10s 或触发 viewed_rescore_section） | 0 MTC（P0）——只计 L2 | 每设备每日 1 次 valid_visit | 驻留客户端计、服务端去重；可疑设备排除 |
| 朋友入群（运营对成员列表人工确认） | +100 MTC（mtc_invite_reward） | 3/日；10/试用/情报官 | 确认必须人工；每 device_hash 一次；自己除外 |
| 提交反馈（试用清单 §13 条目） | +50 MTC | 1/场/情报官 | 运营先读后发——垃圾反馈走 reject + 评审日志 |
| 赛后回访（带 ref 访问 recap） | 0 MTC——仅周报指标 | 1/设备/日 | |
| Scout L1（3 个不同设备点过） | 社区徽章（群内显示名） | — | 仅 counted 事件；人工授予 |
| Scout L2（10 个有效访客） | +1 试用解锁通行证（trial_unlock，可抵一次报告解锁） | — | 人工授予 |
| Scout L3（5 次确认入群） | 完整战术室早期访问（运营开通） | — | 人工授予 |
| Scout Captain（高质量反馈 + 持续分享） | 私域群角色 | — | 纯人工判断 |
| 未来：订阅推荐积分 | **不在本设计内——需 Owner 单独批准** | — | — |

MTC 始终在现有地板之下：仅平台积分 · 不可提现 · 不可转让 · 不可交易（mtcStatement 原文）。
所有发放可溯源：`referral_rewards → token_log_id → TokenLog`。

---

## 7. 风险登记册（交付 ⑦）

| # | 风险 | 概率/影响 | 缓解 |
|---|---|---|---|
| R1 | **被误读为博彩代理**——尤其缅甸荐单（ဘောဆရာ tipster）文化里「贴士+代理+群」三件套强烈 pattern-match 赌球拉新 | 中 / 致命 | UI 零金钱用词（§8 guard）；分享文案只准运营包定稿模板；my 发送保留非博彩免责行；**扁平结构无下线**；奖励只是积分/徽章；my campaign 启动沿用现有「二次 GO」纪律需 Owner 单独 GO；命名永远内容向（情报官/Scout，绝不代理/agent） |
| R2 | **奖励入群被读成"付费拉人进贴士群"** | 中 / 高 | 入群奖小且封顶（3/日、10/试用）；群内容即已审产品内容；奖在人工核对成员列表后才发；不做公开推广（试用范围 §12 不变） |
| R3 | **隐私——设备追踪蔓延** | 低 / 高 | 设计性最小化：仅一个客户端随机 UUID、存加盐 SHA-256；**无 IP、无 UA、无指纹**（逐字延用 MatchEngagement 承诺）；原始 UUID 不可跨用户查询；试用后事件聚合即可清理；写入 COMPLIANCE 文档 |
| R4 | **刷量/自邀**（click farm、自己点自己） | 中 / 中 | counted 去重 (code, device, type, day)；owner_device_hash 自点排除；突发阈值（>5 点击/设备/日、>20/码/日 → is_suspect 排除并上看板）；**P0 零自动入账——每一分 MTC 都过运营之手** |
| R5 | **激励扭曲反馈质量**（为 MTC 灌水反馈） | 高 / 中 | 反馈奖先读后发、1/场封顶、reject 路径带评审日志；Captain 等级明确按*质量*人工评定 |
| R6 | **身份脆弱**——localStorage 清空/无痕造成少计，或一人多设备多计 | 高 / 低 | 接受少计；**绝不升级到更强指纹**（隐私地板优先）；上限+人工发放兜住多计损害 |
| R7 | **语言泄漏**——新 UI 串在 vi/my 回退到 zh（Owner 红线） | 中 / 高 | 所有新 dict 键四层全量；可见扫描扩到 /token + /community（§8）；FALLBACK_CHAIN 本就禁止 zh 回退 |
| R8 | **运营开销拖死闭环**（全人工） | 中 / 中 | 看板自动算等级达标+待发奖提案；周报脚本自动出件；看板印 curl 配方 |
| R9 | **码探测/track 端点垃圾流量** | 低 / 低 | track 为 fire-and-forget 常形响应；未知/revoked 码不落库；突发阈值即设备级节流；`enable_referral_program=False` 时端点关闭 |

---

## 8. Guard 更新计划（交付 ⑧）

**涉及文件**：`scripts/check_mvp2_product_narrative_guard.py`（FORBIDDEN 列表）、
`scripts/check_customer_visible_copy.py`（各语言列表 + ROUTES）、`docs/COMPLIANCE_RULES.md`、
**新** `scripts/check_referral_campaign_copy.py`，以及 campaign/link admin 端点内的
**服务端创建 lint（权威）**。

**zh 增项**（叙事 guard + 可见扫描 + 服务端 lint）：
`代理费`、`返佣`、`佣金`、`充值返利`、`充值送`、`输赢分成`、`月结佣金`、`提成`、`下线`、
`拉新返现`、`流水`、`代理等级`、`招代理`、`充值`
- 误报注：裸「代理」有技术语义（委托代理/代理服务器）→ **叙事层只禁上述复合词**；campaign 标题
  lint（语料小且可控）可禁裸「代理」。「充值」在客户文案无正当用途（产品只说解锁/订阅）可整词禁。
  「月结」理论上撞「本月结束」→ 以整 token「月结佣金」为主禁、「月结」单禁仅在 campaign 标题层。
- **「提现」特别条款：沿用既有否定豁免——仅允许出现在「不可提现」内**（backend
  `compliance.py` 已是 negation-aware；新静态 lint 必须照搬该逻辑，否则会误伤 MTC 合规声明
  `不可提现`）。

**vi 增项**：`hoa hồng`（佣金——误报注：也是"玫瑰"，足球文案中几乎不会正当出现，禁+注）、
`chiết khấu`（返点/折扣）、`nạp tiền`（充值）、`rút tiền`（提现/出金）、`đại lý`（代理——误报注：
也是"经销商"，本产品文案无正当用途，禁）、`tuyến dưới`（下线）、`ăn chia`（分成）、
`đại lý cá cược`（博彩代理，冗余保留以利文档 lint）。现有 kèo / cá cược / nhà cái / soi kèo 不变。

**my 增项**（⚠ 全部缅语词条**生效前必须缅语母语者复核**——与 §15 MY 管线同纪律）：
`ကော်မရှင်`（commission 借词）、`အေးဂျင့်`（agent 借词）、`ငွေဖြည့်`（充值）、
`ငွေထုတ်`（提现/出金）、`အမြတ်ခွဲဝေ`（利润分成）、`လောင်းဒိုင်`（赌庄）。
- 误报注：**裸 `ဒိုင်` 不可禁**——体育语境是"裁判"（ဒိုင်လူကြီး）；只禁复合 `လောင်းဒိုင်`。
  现有缅语博彩词表（လောင်းကစား 等）不变。

**en 增项**（SHARED + 叙事 guard）：`commission`, `rebate`, `recharge`, `cash out`, `cashout`,
`downline`, `agent link`, `betting agent`, `gambling referral`, `payout`, `profit share`。
- 误报注：`settlement` 是内部模型/端点名（PredictionSettlement / challenges settle）——**只在
  客户可见层禁**，叙事 guard 的 AUDIT_TOKENS 路径与内部代码豁免并注明。`commission` 在本产品
  无正当客户用途。

**可见扫描面扩展**：Track B 上线后 ROUTES 增 `/token` 与 `/community`（×3 语 = **21 面**），
覆盖邀请记录区与群 CTA。首页情报官入口在旗标后，默认面保持干净——QA 截图包另加每语言一张
`/?scout=1` 旗标态截图，不进硬门。

**campaign 标题 / 分享文案 lint**：`check_referral_campaign_copy.py` 校验 (a) docs/ 下 Track B
分享文案包、(b) 经 admin GET 拉取的在库 campaign 标题——对四语禁词全集；同一词表以常量形式进
后端创建端点，**被禁标题根本无法入库**。

---

## 9. 最小试用实施计划（交付 ⑨ — 获 Owner 批准后才动工）

### P0 — 最小诚实切片（≈ **2.5 人日**）

范围：仅运营签发链接；人工发奖；只读看板；周报工件。**不做**自助码、自动发奖、徽章 UI、QR 端点。
（**P0 含 DB 加表与 API 新增 → 属 L2 变更，本设计获批 = 该范围获批，动工前仍以 Owner 对本文档的
GO 为准。**）

| 步 | 文件（➕新 / ✏改） | 工作量 |
|---|---|---|
| 1 模型 | ➕ `backend/app/models/referral.py`（Campaign/Link/Event/Reward/OperatorReviewLog；ScoutProfile 定义未用）· ✏ `models/__init__.py` | 0.25 d |
| 2 配置+schema | ✏ `config.py`（旗标/盐/阈值）· ➕ `schemas/referral.py`（REFERRAL_EVENTS、请求/响应模型） | 0.25 d |
| 3 服务+路由 | ➕ `services/referral/referral_service.py`（track 去重+标记、summary、create、grant→wallet_service._credit）· ➕ `routers/referrals.py`（公开 track+summary；admin create/links/confirm/grant）· ➕ `routers/internal_referrals.py`（HTML 看板，克隆 scout-pack 门控）· ✏ `main.py` 挂载 | 0.75 d |
| 4 前端 | ✏ `api/client.ts`（safeTrackReferral、summary）· ➕ `hooks/useReferralCapture.ts` · ✏ `Layout.tsx` · ✏ `HomePage.tsx`（入口卡，旗标）· ✏ `PredictPage`/`ProductProofViews`（分享 CTA、驻留、rescore observer、群 CTA 行）· ✏ `TokenPage.tsx`（邀请记录）· ✏ `dict.ts`/`copy/en.ts`/`copy/mm.ts` | 0.75 d |
| 5 守卫+工具 | ✏ 两个 guard 脚本（词表、ROUTES）· ➕ `check_referral_campaign_copy.py` · ➕ `mvp2_generate_referral_qr.py` · ➕ `mvp2_build_referral_weekly_report.py` · ✏ `docs/COMPLIANCE_RULES.md` | 0.5 d |

**P0 验收**：重复点击实测去重；自点排除实测；禁词标题创建返回 400；21 面可见扫描 PASS；
一次完整运营干跑（建 campaign → 签链 → 点击 → 确认入群 → 发 100 MTC → TokenLog 行可见 →
周报工件生成）。

### P1 —— 试用后 + Owner 再批准
自助个人码（device 绑定 get-or-create User）、scout_profiles 填充缓存计数、TokenPage 等级
*展示*（授予仍人工）、自动 +50 分享奖（服务端确认 1/日）、R2 QR 上传、分享卡图、真实人均钱包
绑定替换 DEMO_USER_ID。

### 明确不建清单（任何阶段，customer-facing）
不做任何形式的支付/充值 · 不做现金或现金等价奖励 · MTC 不可提现/转让/交易 · 不做输赢的追踪/
展示/结算 · 不做任何形式的佣金 · 不做多层/下线结构 · 不做盘口/赔率/博彩内容或用词 · 不做
「客服高级链接」通道 · 不公开发布或大规模推广（试用范围 §12 不变）· 订阅推荐积分另案（Owner
单独批准）· 等级不自动授予 · 不采集 IP/UA/指纹。
