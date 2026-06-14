# MVP2-P2 — Homepage Product Loop · Phase C Static Preview

> Low-cost documented mock of the reconstructed homepage for the **current real 2026-06-14 scenario**.
> Does NOT connect to backend; does NOT write runtime data. Shows the new ZONE ORDER and copy as
> `HomeProductLoop.tsx` renders it from the committed manifest (verified by `selectProductLoop`).
> Scenario facts: Brazil 1-1 Morocco finished (tracked hotspot, recap NOT ready → no fake recap);
> Mexico 2-0 South Africa has a real recap (secondary); Netherlands vs Japan = today's hotspot.

## Selection result (verified against `frontend/public/data/daily-fixtures.json`)
```
featuredRecap      = Brazil vs Morocco 1-1   [RECAP_PENDING, recapReady=false]
featuredPrediction = Netherlands vs Japan    [SCHEDULED]
otherRecaps        = [ Mexico vs South Africa 2-0  (RECAP_READY, recapReady=true) ]
secondarySchedule  = [ Germany vs Curaçao, Ivory Coast vs Ecuador, Sweden vs Tunisia, Australia vs Turkey ]
```

## Rendered order — zh
```
┌───────────────────────────────────────────────┐
│ 俅哥说球  · 世界杯赛前判断 · 临场 30 分钟修正      │  ① brand / value prop (existing hero)
├───────────────────────────────────────────────┤
│ ⟳ 赛程更新 06-14 … · 实时                        │  sync line (source + freshness)
├───────────────────────────────────────────────┤
│ 🔥 昨日热点复盘          YESTERDAY · HOTSPOT RECAP│  ② Zone 2
│ [比赛已结束 · 赛后校准中]                          │
│ Brazil vs Morocco　1 - 1                         │
│ 这是昨日主推的热点比赛，赛后观察已开启。           │
│ [ 加入情报群看赛后观察 ▸ ]   ← NO 查看复盘         │
├───────────────────────────────────────────────┤
│ 🎯 今日热点预测       TODAY · HOTSPOT PREDICTION  │  ③ Zone 3
│ [今日主推 · 开球前判断]                            │
│ Netherlands vs Japan                            │
│ 今日主推比赛：开球前看方向，开球前 30 分钟修正。   │
│ [ 加入临场情报群 ▸ ]   (进入今日判断 hidden: no narrative yet) │
├───────────────────────────────────────────────┤
│ 🗓️ 今日赛程              TODAY · SCHEDULE         │  ④ Zone 4 (secondary, lightweight)
│ Germany vs Curaçao              [即将开赛]        │
│ Ivory Coast vs Ecuador          [即将开赛]        │
│ Sweden vs Tunisia               [即将开赛]        │
│ Australia vs Turkey             [即将开赛]        │
├───────────────────────────────────────────────┤
│ 🗂️ 其他复盘                 OTHER RECAPS          │  ⑤ Zone 5 (secondary)
│ Mexico vs South Africa　2 - 0     [ 查看复盘 ▸ ]  │  ← recap_ready ⇒ 查看复盘 allowed
├───────────────────────────────────────────────┤
│ 想看临场 30 分钟修正和赛后观察，进群。            │  ⑥ Zone 6 growth CTA (value-tied)
│ [ 加入情报群 ▸ ]                                  │
└───────────────────────────────────────────────┘
  (历史复盘档案 · WC2022 ›  and 内部演示数据 ›  remain collapsed below — unchanged)
```

## vi (same order, no Chinese fallback)
```
🔥 Phục dựng điểm nóng hôm qua   — [Trận đã kết thúc · Đang hiệu chỉnh sau trận]
   Brazil vs Morocco 1-1 · Đây là trận điểm nóng được chọn hôm qua; quan sát sau trận đã mở.
   [ Vào nhóm xem quan sát sau trận ▸ ]      (no "Xem phục dựng")
🎯 Dự đoán điểm nóng hôm nay      — [Trận chính hôm nay · nhận định trước trận]
   Netherlands vs Japan · Trận chính hôm nay: xem hướng trước trận, hiệu chỉnh 30 phút trước giờ bóng lăn.
   [ Vào nhóm sát giờ ▸ ]
🗓️ Lịch hôm nay: Germany–Curaçao, Ivory Coast–Ecuador, Sweden–Tunisia, Australia–Turkey  [Sắp đá]
🗂️ Phục dựng khác: Mexico vs South Africa 2-0  [ Xem phục dựng ▸ ]
   "Muốn xem hiệu chỉnh 30 phút trước trận và quan sát sau trận, vào nhóm."  [ Vào nhóm ▸ ]
```

## my (same order, Burmese; concise product terms kept)
```
🔥 မနေ့ အဓိကပွဲ ပြန်သုံးသပ်  — [ပွဲ ပြီးဆုံးပြီ · ပွဲပြီး ပြန်ညှိနေဆဲ]
   Brazil vs Morocco 1-1 · ဒါက မနေ့ ရွေးချယ်ထားသော အဓိကပွဲ; ပွဲပြီးသုံးသပ်ချက် စတင်ဖွင့်ပြီ။
   [ ပွဲပြီးနောက် သုံးသပ်ချက်ကြည့်ရန် အဖွဲ့ဝင်ပါ ▸ ]
🎯 ဒီနေ့ အဓိကပွဲ ခန့်မှန်း   — [ဒီနေ့ အဓိကပွဲ · ပွဲမစခင် အမြင်]
   Netherlands vs Japan · ပွဲမစခင် ဦးတည်ချက်၊ ပွဲမစခင် မိနစ် ၃၀ ပြန်ညှိ။   [ ပွဲနီး အဖွဲ့ ဝင်ရန် ▸ ]
🗓️ ဒီနေ့ ပွဲစဉ်: Germany–Curaçao, Ivory Coast–Ecuador, Sweden–Tunisia, Australia–Turkey  [မကြာမီ]
🗂️ အခြား ပြန်သုံးသပ်ချက်: Mexico vs South Africa 2-0  [ ပြန်သုံးသပ်ချက် ကြည့်ရန် ▸ ]
   "ပွဲနီး မိနစ် ၃၀ ပြန်ညှိချက်နှင့် ပွဲပြီးသုံးသပ်ချက် ကြည့်ချင်ရင် အဖွဲ့ဝင်ပါ။"  [ အဖွဲ့ဝင်ရန် ▸ ]
```

## Before → After
| | Before (live `index-s_THNLrz.js`) | After (this build) |
|---|---|---|
| Lead | auto-hero (recap_ready could win) + recap desk 今日复盘/今日赛况 + 即将开赛 + operator status | explicit **昨日热点复盘** (Brazil) then **今日热点预测** (Netherlands) |
| Today's main match | buried in 即将开赛 list | first-screen **今日热点预测** block |
| Mexico | featured 今日复盘 (could read as the lead) | **其他复盘** (secondary, below Brazil) |
| CTA | generic 加入情报群 / 更多场次… | value-tied 想看临场 30 分钟修正和赛后观察，进群。 |
| Feel | status / recap / fixture list | predict → track → recap → next loop |

**This preview is for Owner review (Phase D). Deploy is gated on Owner acceptance.**
