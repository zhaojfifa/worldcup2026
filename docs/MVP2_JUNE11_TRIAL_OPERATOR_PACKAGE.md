# MVP-2 June 11 Trial — Operator Package（运营试发包）

> **Date:** 2026-06-11 · **Branch:** `feature/mvp2-api-football-ingestion`（PR #3 Draft）
> **状态：READY FOR OWNER TRIAL-SEND REVIEW —— operation 仍 paused，本包未发出任何内容。**
> 群链接占位符一律为 **[群链接由运营填写]**（LLM 被 guard 禁止编造链接）。
> **★ QiuGe 更新：zh 人格 = 俅哥说球（§6b 为最终 zh 物料；§6 为中文先知旧版存档）。**

## 1. 试发目标
用 6 月 11 日揭幕窗口的真实比赛，验证「中文先知 / Tiên Tri Bóng Đá 赛前判断 → 群内临场 30 分钟修正」
的产品钩子能否让球迷愿意看、愿意入群。免责原则：数据分析 / AI 判断 / 风险观察 / 娱乐参考，无博彩表达。

## 2. 选定比赛（source of truth = API-FOOTBALL，见 §3）
- **主发：fixture 1489369 — Mexico vs South Africa**，2026-06-11 19:00 UTC（揭幕战，Estadio Azteca,
  Mexico City，Group Stage-1，Not Started）。**发送窗口：开球前。**
- **预热：fixture 1489371 — Brazil vs Morocco**，2026-06-13 22:00 UTC（MetLife Stadium）。

## 3. 数据源
API-FOOTBALL `/fixtures league=1 season=2026`（72 场，HTTP 200）+ Level-2 packs（squads 26 人/coach 真实；
lineups/injuries 赛前为 0 → 转写为「临场盯防变量」，从不冒充）→
`docs/data_audit/mvp2_june11_real_fixture_verification.json`。本地 Kaggle 国际赛 49k 行 → Elo（墨西哥
1880 vs 南非 1624 差 256；巴西 1964 vs 摩洛哥 1899 差 65）、近 10 场、H2H（含 2010 揭幕 1-1、摩洛哥
2-1 巴西 2023）、零封/射手依赖。帧：`docs/data_audit/mvp2_trial_prediction_frames/`。

## 4. ScoutScore 因子（trial 帧）
baseline_strength · recent_form · h2h · goal_trend · defensive_trend（摩洛哥近 10 场 7 零封）·
squad_stability · goalkeeper_risk（GK 名单真实，首发未知）· striker_finishing_risk（南非锋线依赖
Appollis/Makgopa）· travel_venue_context（Azteca 海拔≈2200m，scenario）· lineup_uncertainty ·
injury_gap（internal-only）· live_30min_trigger。每因子带 source_refs + data_status + customer_visible。

## 5. Provider 对比（trial 8 份全 PASS）
DeepSeek：persona 语感强（「免费版看方向，群内看临场修正」精准落位）、群文案短带数字；vi 初稿仍会
盘口黑话（kèo/cửa trên）→ in-loop guard 全拦截。Gemini：结构稳、稍长稍正式；vi 同样犯黑话被拦。
**最终选用：DeepSeek（页面与群消息）；Gemini 留档 benchmark。**

## 6. zh 群消息（可直接复制；发送前 Owner GO）

**主发 · 揭幕战（开球前发）**
```text
中文先知看墨西哥vs南非：Elo 差 256，但风险高！首发、门将、锋线效率三个盲区，开球前 30 分钟名单一出，判断可能翻转。免费版看方向，群内看临场修正。

想第一时间拿到中文先知对这场墨西哥vs南非的临场修正？开球前 30 分钟，首发名单一出，模型会重新算一遍主倾向和比分区间。群里直接看更新，不用等赛后。
👉 [群链接由运营填写]
历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。
```

**预热 · 巴西 vs 摩洛哥（06-13）**
```text
🇧🇷巴西 vs 🇲🇦摩洛哥，中文先知赛前判断：巴西 Elo 领先 65 分，但摩洛哥 7 场零封、近 10 场不败。风险中，冷门密码在防守。开球前 30 分钟看首发，群内发临场修正。
👉 [群链接由运营填写]
历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。
```


## 6b. ★ 俅哥说球 · 最终试发物料（QiuGe sprint — 以本节为准）

**① zh 群消息（开球前发）**
```text
俅哥看这场：墨西哥 vs 南非，Elo 差 256 分但风险标「高」。阵容没公布、门将不确定、南非有硬解射手——大热翻车密码已浮现。免费版看方向，群内等 30 分钟首发重判。

想看俅哥在首发公布后怎么修正判断？群内 30 分钟临场重判——门将谁上、阵型怎么摆、风险升还是降。扫码进群，开球前收到更新。
👉 [群链接由运营填写]
历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。
```

**② zh 社媒短帖**
```text
墨西哥 vs 南非：Elo 差 256 分但风险标「高」。阵容盲区 + 门将未知 + 南非有冷枪手。开球前 30 分钟，俅哥在群内重判。
```

**③ 截图推荐**：`home_qiuge_zh.png`（首屏=俅哥说球+今日看点）或 `predict_1489369_rescore_zh.png`
（俅哥临场 30 分钟修正块——产品差异点最强一张）。

**④ 30 分钟重算提醒（首发公布后群内发）**
```text
【俅哥提醒】墨西哥vs南非首发已出！群内已推送重算判断，快去看最新分析。
```

**⑤ 开球后停发规则**：19:00 UTC 开球后，①②④ 全部作废——不补发、不改写成"俅哥早就说过"；
改用 06-13 巴摩预热 + 复盘素材。

**vi 对应物料**（persona: Tiên Tri Bóng Đá，临时）
```text
Tiên Tri Bóng Đá: Mexico mạnh hơn trên giấy (Elo +256, phong độ 6-3-1), nhưng rủi ro CAO vì chưa rõ đội hình và thủ môn. 30 phút trước giờ đá, bản cập nhật trong nhóm sẽ hiệu chỉnh nhận định. Theo dõi để không bất ngờ!
👉 [群链接由运营填写]
Thành tích quá khứ không đại diện cho kết quả tương lai; chỉ mang tính phân tích dữ liệu và giải trí.
```
30-min reminder (vi): Đội hình Mexico vs Nam Phi vừa ra! Vào nhóm xem phân tích điều chỉnh ngay – Tiên Tri Bóng Đá cập nhật nhận định trong 5 phút.

## 7. vi 群消息（Telegram 可用；Zalo pending）

**Mexico vs South Africa（gửi trước giờ bóng lăn）**
```text
Tiên Tri Bóng Đá: Mexico mạnh hơn trên giấy (Elo +256, phong độ 6-3-1), nhưng rủi ro CAO vì chưa rõ đội hình và thủ môn. 30 phút trước giờ đá, bản cập nhật trong nhóm sẽ hiệu chỉnh nhận định. Theo dõi để không bất ngờ!

Muốn biết liệu Mexico có vấp ngã ngay trận ra quân? Vào nhóm để xem bản cập nhật 30 phút trước giờ đá – Tiên Tri Bóng Đá sẽ hiệu chỉnh nhận định dựa trên đội hình thực tế.
👉 [群链接由运营填写]
Thành tích quá khứ không đại diện cho kết quả tương lai; chỉ mang tính phân tích dữ liệu và giải trí.
```

**Brazil vs Morocco（13/06）**
```text
Tiên Tri Bóng Đá: Brazil nhỉnh hơn về Elo (1964 vs 1899) và ghi bàn ổn, nhưng Morocco đang bay cao với 7 trận sạch lưới gần nhất. Đội hình ra sân sẽ quyết định tất cả – cập nhật 30 phút trước giờ bóng lăn trong nhóm. Vào nhóm để xem hiệu chỉnh sát giờ!
👉 [群链接由运营填写]
Thành tích quá khứ không đại diện cho kết quả tương lai; chỉ mang tính phân tích dữ liệu và giải trí.
```

## 8. 截图包
`docs/qa_screenshots/mvp2_june11_trial/`：
- 试发素材：home_zh_trial / home_vi_trial / predict_1489369_{zh,vi}_trial / operator_copy_{zh,vi}_trial（`?ops=1`）
- **试看产品路径**（2026-06-11 shell v2）：home_first_{zh,vi}（首屏=真实比赛）· home_realmatch_{zh,vi}
  （主卡+次卡+中文先知今日热点全景）· predict_1489369_{zh,vi}_v2（战术室分层）· cta_area_{zh,vi}
  （免费 vs 完整 + 入群 CTA）· **detail_redirect_zh（/detail 已重定向战术室，无 Qatar/Ecuador 旧占位）**
  · recap_calibration_zh（复盘=模型校准证明）。
产品路径：首页 → 中文先知战术室 → 详情分层（免费试看→完整入群）→ 临场 30 分钟修正（群内）——
全路径评审见 `MVP2_TRIAL_PRODUCT_PATH_REVIEW.md`。

## 9. 发送 checklist（操作者逐项勾选）
1. Owner GO 已取得（书面）。
2. 当前时间 **早于 19:00 UTC（揭幕战开球）**；过点改发 §7 预热 + 复盘素材。
3. 文案原样复制（不增改判断措辞），仅替换 [群链接由运营填写]。
4. 免责声明行保留。
5. vi 走 Telegram（Zalo 未激活）；zh 走内部/中文群。
6. 发送后回填：发送时间、群名、截图 → 运营记录。

## 10. Do-NOT-send 条件（任一命中即停）
- Owner 未 GO；或 operation pause 未解除。
- 开球后仍未发出（赛前判断过期 → 改复盘路径）。
- 文案被人工改写出「必中/稳赢/赔率/盘口/kèo/cá cược」等词。
- 直发链接为未验证的群链接。
- 首发名单已公布但产品页未更新（与「30 分钟修正」承诺冲突时，先重生成再发）。

## 11. Owner 裁决（2026-06-11 更新）
**小范围私域试用 = PASS WITH CONDITIONS（Owner verdict）。** 公开运营仍 paused。

**★ 第二次 GO（2026-06-11，三语试用授权）：** PASS WITH CONDITIONS —— zh 内部中文群/可信用户 ·
vi Telegram 可信球迷 · my 1 个测试群或个位数可信缅甸球迷；本包为唯一物料口径，仅替换
[群链接由运营填写]，不得人工改写判断文案，免责声明保留，开球后不发，禁博彩/赔率/保证/荐单话术，
**首发已公布而页面未更新 → 停发先重生成**，发送时间/群名/截图/点击/反馈全记录
（发送记录与回收表：`docs/mvp2/TRIAL_FEEDBACK_FORM.md`；试用后产出
`docs/mvp2/TRIAL_FEEDBACK_REPORT.md`）。工程发送前校验 2026-06-11 08:53 UTC：
两场均 NS、lineups=0、1489369 窗口剩约 10 小时（GO/NO-GO 清单 §0 有完整记录）。

## 12. 小范围试用规则（Owner 授权范围）
允许：发给内部运营 · 发给少量可信球迷 · 发 1 个群做测试 · 收集截图/点击/反馈 · 人工记录用户反应。
不允许：大规模公开推广 · 说成正式上线 · 承诺命中 · 博彩/盘口/稳赚/胜率承诺话术 · **开球后继续发赛前判断**。

## 13. 试用反馈清单（运营逐项记录）
| # | 观察项 | 记录 |
|---|---|---|
| 1 | 用户是否记住「俅哥说球」 | |
| 2 | 用户是否点击战术室 | |
| 3 | 用户是否理解「临场 30 分钟修正」 | |
| 4 | 用户是否愿意入群等待修正 | |
| 5 | 哪句话最吸引人 | |
| 6 | 哪句话像机器写的 | |

核心三问：看到「俅哥说球」会不会点？看到「冷门密码」会不会看？看到「开球前 30 分钟重算」会不会入群？

---

## 14. ★ 越南语命名定稿（VI Naming Consolidation sprint，2026-06-11）

**对客命名锁定为：`Giành Cup · Tiên Tri Bóng Đá`。**
- 完整页头：`Giành Cup · Tiên Tri Bóng Đá · Tin trước trận World Cup`
- 短头/ticker：`Tin Tiên Tri` · 底部导航：`Trang chủ / Tiên Tri / Điểm MTC / Cộng đồng`
- 主 CTA：`Vào phòng chiến thuật Tiên Tri` / `Vào nhóm tin báo trước trận`
- 预测页标题：`Phòng chiến thuật Tiên Tri Bóng Đá` · 赛前判断：`Tiên Tri nhận định thế nào`
- 30 分钟重算：`Cập nhật 30 phút trước trận của Tiên Tri` · 今日热点：`Điểm nóng hôm nay của Tiên Tri`
- 历史复盘：`Phục dựng lịch sử · Nhật ký hiệu chỉnh của Tiên Tri`
- 运营发文一律使用以上写法；禁写：AI phân tích / mô hình / kèo / cửa trên / cửa dưới /
  chắc thắng / thiếu dữ liệu；「Nhà Tiên Tri AI」为已废弃旧名，不得再出现。

## 15. ★ 缅甸语（MY）试发物料（LLM 生成 · guard 已过 · persona = Football Oracle 临时名）

> 缅语人格名为**临时名 Football Oracle**，正式缅语名待 Owner 决策：
> `docs/MVP2_MYANMAR_PERSONA_NAMING_OPTIONS.md`。以下文案均为 DeepSeek 生成、guard_clean，
> 来源：`frontend/src/data/productNarratives/1489369.my-MM.json` ·
> `frontend/src/data/rescoreModels/1489369.my-MM.json`。原样复制，仅追加群链接。

**① 群消息（赛前主推，开球前发）**
```text
🔥 Football Oracle ရဲ့ Mexico vs South Africa ပွဲကြို သုံးသပ်ချက် — Elo 256 ကွာဟပေမယ့် လူစာရင်းမထွက်သေးတဲ့အတွက် အန္တရာယ်မြင့်မားတယ်။ ပွဲမစခင် မိနစ် ၃၀ မှာ လူစာရင်းနဲ့ ဂိုးသမားကို ပြန်စစ်ပြီး အမြင်ကို ပြန်ရေးမယ်။ အခမဲ့ဗားရှင်းက ဦးတည်ချက်ပြတယ် — အဖွဲ့ထဲမှာ နောက်ဆုံးပြန်တွက်ချက် စောင့်ကြည့်ပါ။
👉 [群链接由运营填写] · [产品链接 /predict/1489369?lang=my]
```

**② 短社媒帖（Telegram/Facebook）**
```text
🔥 Mexico vs South Africa: Football Oracle ရဲ့ ပွဲကြိုသုံးသပ်ချက် — Elo 256 ကွာဟပေမယ့် အန္တရာယ်မြင့်မား။ လူစာရင်းမထွက်သေး၊ ပွဲမစခင် မိနစ် ၃၀ မှာ ပြန်စစ်မယ်။ အဖွဲ့ထဲမှာ နောက်ဆုံးပြန်တွက်ချက် စောင့်ကြည့်ပါ။
```

**③ 30 分钟重算提醒（首发公布后群内发）**
```text
လူစာရင်းထွက်ပြီးပြီ — Football Oracle ရဲ့ ပြန်လည်အကဲဖြတ်ချက်ကို ချက်ချင်းရယူလိုက်ပါ။ မက္ကဆီကို vs တောင်အာဖရိက အတွက် နောက်ဆုံးရ ခန့်မှန်းချက်ကို ဒီမှာကြည့်ပါ။
```

**④ 入群钩子（备用）**
```text
ဒီည ပွဲကြီးအတွက် လူစာရင်းထွက်ပြီး ၅ မိနစ်အတွင်း ပြန်လည်အကဲဖြတ်ချက်ကို အဖွဲ့ထဲမှာ ရယူလိုက်ပါ — မက္ကဆီကို vs တောင်အာဖရိက အတွက် နောက်ဆုံးရ ခန့်မှန်းချက်ကို မလွတ်စေနဲ့။
```

**⑤ 开球后禁发规则（与 §10 同级，MY 同样适用）**
- 开球后赛前判断一律**不发**（缅语同样过期）；只能转复盘路径 `/recap/...?lang=my`。
- 文案不得人工改写出任何缅语博彩/保证词（လောင်းကစား / လောင်းကြေး / ကြေးပေါက် /
  သေချာပေါက် / အာမခံ 等）；改一个字都要重新过 guard。
- MY 页面出现任何中文字符 = 立即停发并回报工程。

**⑥ MY 试用反馈清单（运营逐项记录）**
| # | 观察项 | 记录 |
|---|---|---|
| 1 | 「Football Oracle」这个名字听起来自然吗？需要缅语名吗？ | |
| 2 | 足球判断（倾向/风险/区间）能看懂吗？ | |
| 3 | 「开球前 30 分钟重算」对入群的吸引力够不够？ | |
| 4 | 有没有任何句子听起来像赌球/博彩（ဘောဆရာ 荐单感）？ | |
| 5 | 有没有句子语气过猛/过度承诺？ | |
| 6 | 有没有看到中文或乱码/英文残留？ | |

## 16. 语言切换验收 checklist（操作者逐项勾选）

| # | 检查项 | 期望 | 结果 |
|---|---|---|---|
| 1 | 浏览器语言自动识别 | 首次打开（无 URL 参数、无本地记录）时 zh*/vi*/my* 浏览器各自落到对应语言，其余落 zh | |
| 2 | 手动选择是否持久 | 选择后刷新/重开仍保持（localStorage `giandcup_lang`） | |
| 3 | 直链 `?lang=my` 是否生效 | 直接打开 `/predict/1489369?lang=my` 即缅语整页；旧链 `?lang=mm` 同样落到缅语 | |
| 4 | 切换语言是否停留当前页 | 在 /predict/:id 切语言不回首页、不丢路由，URL lang 参数同步更新 | |
| 5 | 移动端选择器是否比旧三按钮干净 | 顶栏单个 🌐 控件；点开为底部弹层（中文 / Tiếng Việt / မြန်မာ），当前项带 ✓ | |

## 17. 三语发送顺位（小范围试用）

zh = 内部/中文群（俅哥说球） · vi = Telegram 可信粉丝（Tiên Tri Bóng Đá；Zalo pending） ·
my = 1 个测试群或个位数可信缅甸球迷（Football Oracle 临时名 — 同步收 §15⑥ 反馈）。
全部仍受 §10/§12 约束：Owner GO 前一律不发；开球后过期不发；公开运营继续 paused。
