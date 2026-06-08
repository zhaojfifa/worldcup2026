# Operation Copy Library — Vietnamese & Burmese (Harness-X · P-flow Prep)

_Created 2026-06-08 · Human-authored (NO LLM). Expansion of the trial copy packs into a reusable
operator library for vi (Vietnam / Zalo) and mm (Myanmar / Telegram)._

Sources: `OPERATION_TRIAL_MESSAGES_VI.md`, `MM_OPERATION_TRIAL_MESSAGES.md`, `frontend/src/copy/{vi,mm}.ts`.

> **Compliance (both languages):** AI viewpoint framing only · no betting / guaranteed-profit /
> cash wording · MTC = platform points (not withdrawable/transferable/tradable) · carry the
> disclaimer where 战绩/命中/连胜 appears. vi forbidden: chắc thắng/đảm bảo thắng/cá cược/đặt cược/
> kiếm tiền/lợi nhuận chắc chắn (negation "Không phải dịch vụ cá cược" allowed).
> mm: လောင်းကစား only in negation (မဟုတ်/မချိတ်). Prices: vi VND/₫, mm MMK/Ks.

---

## Templates (5 categories × vi/mm)

### A. 今日三场速览 / Daily 3-match brief
- **vi title:** 🔥 3 trận AI đáng chú ý hôm nay
- **mm title:** 🔥 ယနေ့ AI ၃ ပွဲ
- Body pattern: `{Team} vs {Team} · {AI trend} · {★confidence} · {one-line reason} · {risk note}`
- CTA vi: `Vào nhóm xem nhận định AI đầy đủ 👉` · mm: `အပြည့်အစုံ ကြည့်ရန် အုပ်စုဝင်ပါ 👉`
- Always end with disclaimer.

### B. 爆冷风险 / Upset risk
- **vi:** ⚠️ Rủi ro bất ngờ: {Team} vs {Team}
- **mm:** ⚠️ အံ့အားသင့်နိုင်ခြေ: {Team} vs {Team}
- Body: risk point · why it matters · platform (TikTok/Telegram) · disclaimer.

### C. 临场修正 / Live correction (T-30min)
- **vi:** 📡 Cập nhật sát giờ · {Team} vs {Team}
- **mm:** 📡 ပွဲချိန် update · {Team} vs {Team}
- Body: trigger · before→after win-prob · AI reason · "AI tính lại / AI ပြန်တွက်" (NOT "sure win").

### D. 赛后复盘 / Post-match review
- **vi:** AI nhận định ban đầu → kết quả thực tế → đúng/sai → nguồn sai số → hướng điều chỉnh.
- **mm:** AI ၏ ပထမသုံးသပ်ချက် → တကယ့်ရလဒ် → မှန်/မှား → အမှားရင်းမြစ် → နောက်ပွဲ ပြင်ဆင်ချက်.
- Only after real results back-filled; else mark as illustrative.

### E. 社群引导 / Community CTA
- **vi:** Vào nhóm Zalo nhận thông tin AI sớm nhất · MTC không thể rút tiền.
- **mm:** Telegram အုပ်စုတွင် AI သတင်း အစောဆုံးရယူပါ · MTC ငွေထုတ်မရ.

---

## Ready-to-send sets
- **vi (Zalo):** `docs/OPERATION_TRIAL_MESSAGES_VI.md` (3 messages, compliance self-checked).
- **mm (Telegram):** `docs/MM_OPERATION_TRIAL_MESSAGES.md` (Burmese messages).

## Dispatch routing
- **Vietnam → Zalo** (primary). Status: **pending active** (no public_url yet).
- **Myanmar → Telegram** (active verified). Use mm set; record results in `OPERATION_TRIAL_RESULTS.md`.
- Channel clicks must carry `match_id` to register in `community/heat`.

## Pre-send checklist (operator)
1. Manual forbidden-word recheck (zh-internal + vi + mm).
2. Disclaimer present.
3. Price in correct currency (vi ₫ / mm Ks) — never RMB to customers.
4. AI-viewpoint framing, no result/profit promise.

---

## Filled copy from refreshed model output (2026-06-08, seed data)

> Based on the live refreshed baseline output (NOT real accuracy). Numbers are AI data view.

### Daily 3-match brief

**vi:**
```
🔥 3 trận AI đáng chú ý hôm nay
⚽ Brazil vs Argentina — Xu hướng AI: Chủ nhà nhỉnh nhẹ (49%) · ★★★☆☆ · rủi ro cao, phụ thuộc đội hình.
⚽ Morocco vs France — Xu hướng AI: Chủ nhà nhỉnh (50%) · ★★★★☆ · hướng khá rõ, biến số hạn chế.
⚽ Spain vs Germany — Xu hướng AI: Chủ nhà nhỉnh (52%) · ★★★★★ · hướng khá rõ.
Vào nhóm xem nhận định AI đầy đủ 👉
Kết quả trong quá khứ không đảm bảo kết quả tương lai. Chỉ phân tích dữ liệu & giải trí.
```

**mm:**
```
🔥 ယနေ့ AI ၃ ပွဲ
⚽ Brazil vs Argentina — AI အမြင်: အိမ်ရှင် အနည်းငယ်သာ (49%) · ★★★☆☆ · အန္တရာယ်မြင့်၊ လူစာရင်းပေါ်မူတည်။
⚽ Morocco vs France — AI အမြင်: အိမ်ရှင် သာ (50%) · ★★★★☆ · ဦးတည်ရှင်း၊ ပြောင်းလဲမှုနည်း။
⚽ Spain vs Germany — AI အမြင်: အိမ်ရှင် သာ (52%) · ★★★★★ · ဦးတည်ရှင်း။
အပြည့်အစုံ ကြည့်ရန် အုပ်စုဝင်ပါ 👉
အတိတ်ရလဒ်က အနာဂတ်ကို အာမမခံပါ။ ဒေတာ ခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဖျော်ဖြေရေးအတွက်သာ။
```

### Upset risk (highest = match 1, high risk)
- **vi:** ⚠️ Rủi ro cao: Brazil vs Argentina — hai đội sát nhau, kết quả phụ thuộc đội hình & chiến thuật. (disclaimer)
- **mm:** ⚠️ အန္တရာယ်မြင့်: Brazil vs Argentina — နှစ်သင်းနီးစပ်၊ ရလဒ်သည် လူစာရင်း/နည်းဗျူဟာပေါ် မူတည်။ (disclaimer)

### Live correction / model explanation
- Use match 1's real `live_correction` (Brazil 45%→49% after Argentina center-back out).
  vi: "AI tính lại"; mm: "AI ပြန်တွက်" — **not** "sure win".

### MTC Q&A (both langs)
- vi: "MTC là gì? → điểm tích lũy nền tảng, không rút tiền/chuyển nhượng/giao dịch."
- mm: "MTC ဆိုတာ? → ပလက်ဖောင်းပွိုင့်၊ ငွေထုတ်/လွှဲ/ရောင်း မရ။"

> All lines above are **AI data view / risk signal / pre-match update** — no hit-rate claim, no
> betting, no cash. Confidence shown as ★ (derived), not as a real success rate.

---

## Copy provenance & review workflow (2026-06-08)
- **Human template:** the filled copy above + `OPERATION_TRIAL_MESSAGES_VI.md` /
  `MM_OPERATION_TRIAL_MESSAGES.md`. Always available; used as the LLM fallback.
- **LLM draft:** generated via `POST /api/v1/admin/llm/generate-copy` (admin, draft-only) →
  `provenance: llm:deepseek|kimi`. **Every LLM draft is `status=draft_only`, `publishable:false`**
  and must pass the forbidden-phrase filter + **human review** before any manual send.
- Workflow: `generate draft → forbidden filter → human review → operator manually sends`.
  **No auto-publish, no bot.** Record which messages were human vs LLM-draft in `OPERATION_TRIAL_RESULTS.md`.
