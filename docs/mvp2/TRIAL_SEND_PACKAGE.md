# MVP-2 小范围试用 · 发送包（TRIAL SEND PACKAGE）

> **Date:** 2026-06-11 · **Owner verdict: PASS WITH CONDITIONS（小范围私域试用）**
> 范围：内部运营 / 少量可信球迷 / 1 个私域测试群 / 仅 Mexico vs South Africa 一场。
> 物料来源：当前 voice_v2 去模型化叙事与 rescore 工件（DeepSeek，guard + visible-copy 双 PASS）。
> 群链接一律 **[群链接由运营填写]**；开球 **2026-06-11 19:00 UTC** 前有效。

## 1. zh 群消息（Mexico vs South Africa，原样复制）
```text
🇲🇽墨西哥vs🇿🇦南非，俅哥判断方向偏主胜，但冷门风险高！首发没公布、门将没定、锋线效率不明——这些变量开球前30分钟会重新算。免费版看方向，群里等临场修正。

这场比赛变量太多，首发一出来，俅哥会在群里第一时间更新判断：墨西哥的中轴是否完整？南非的门将是不是爆种？免费看方向，群里等临场——想跟俅哥一起盯这场，点下方按钮进群。
👉 [群链接由运营填写]
历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。
```

## 2. vi 群消息（Telegram；Zalo 未激活）
```text
Tiên Tri Bóng Đá: Mexico chênh Elo 256 điểm, nhưng rủi ro cao vì đội hình chưa công bố. 30 phút trước giờ đá phải xem lại lineup và thủ môn. Vào nhóm để nhận bản cập nhật sát giờ.

Muốn biết chính xác ai đá chính, thủ môn nào bắt, và nhận định hiệu chỉnh sát giờ? Vào nhóm Tiên Tri Bóng Đá – nơi có bản cập nhật 30 phút trước kickoff.
👉 [群链接由运营填写]
Thành tích quá khứ không đại diện cho kết quả tương lai; chỉ mang tính phân tích dữ liệu và giải trí.
```

## 3. 社媒短帖（zh）
```text
墨西哥纸面强，但首发没定、门将未知、锋线效率成谜。俅哥把这场列为高风险——开球前30分钟，群里见分晓。
```

## 4. 截图推荐
首选 `docs/qa_screenshots/mvp2_june11_trial/predict_1489369_rescore_zh.png`（俅哥临场 30 分钟修正块——
产品差异点最强）；次选 `home_trialready_zh.png`（首屏 = 俅哥说球 + 今日看点）。vi 用对应 `_vi` 版本。

## 5. 开球前 30 分钟提醒模板
zh：
```text
【俅哥提醒】墨西哥vs南非首发即将公布！进群看俅哥第一时间解读——中轴线是否完整？门将是谁？冷门风险怎么变？今晚一起看球！
```
vi：
```text
⏰ Còn 30 phút nữa! Đội hình Mexico vs South Africa sắp có – thành viên nhóm sẽ nhận ngay bản rescore từ Tiên Tri Bóng Đá. Ai bắt chính? Ai ngồi ghế dự bị? Tất cả sẽ thay đổi nhận định. Vào nhóm để không lỡ!
```
（首发公布后的修正版判断 = 工程重跑 `mvp2_generate_rescore_models.py` + 人工核对再发。）

## 6. 开球后停发规则
19:00 UTC 开球后：以上赛前物料**全部作废**——不补发、不改写成「俅哥早就说过」、不发任何赛前判断；
可转发的只剩复盘素材（/recap/855737、/recap/979139）与 06-13 巴摩预热（需 Owner 另行确认）。

## 7. 运营可以说
数据分析 / 俅哥判断 / 冷门风险 / 临场变量 / 开球前 30 分钟重算 / 免费看方向、群里看修正 /
娱乐参考 / 历史表现不代表未来结果。

## 8. 运营不得说
任何博彩词（投注/下注/赔率/盘口/竞猜/串关/kèo/cá cược/nhà cái）· 稳赢/必中/包赢/保证/承诺收益 ·
命中率/胜率数字 · 「正式上线/全面发布」· 自行编造或修改俅哥的判断语句 · 引用内部工程词
（模型/管线/数据缺失/provider 等）· 未经 Owner 确认的群链接。
