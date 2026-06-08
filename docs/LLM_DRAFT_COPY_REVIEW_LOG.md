# LLM Draft Copy — Human Review Log

_Created 2026-06-08. Every draft below is **draft-only** (`status=draft_only`, `publishable=false`),
**not auto-published**, and **requires human review** before any manual operator send._

> **Provenance honesty:** the rows below were generated **locally** with `AI_PROVIDER=mock`, so the
> provider fell back to the human template (`provenance=human_template_fallback`). They are **NOT real
> DeepSeek/Kimi output.** The real provider call runs only on Render (operator + `$ADMIN_API_TOKEN`);
> when executed, paste those rows here with `provenance=llm:deepseek|kimi`. Claude has no provider key
> and **does not fabricate** a real-LLM result. See `docs/LLM_RENDER_VERIFICATION.md`.

## Common fields (this batch)
- **generated_at:** 2026-06-08 (local verification run, `backend/scripts/llm_draft_verify.py`)
- **provider / model:** mock → fallback (no real provider; real run pending on Render: deepseek-chat / moonshot-v1-8k)
- **provenance:** `human_template_fallback`
- **data_mode:** `mock`
- **status:** `draft_only` · **publishable:** `false`
- **warnings (all rows):** `LLM unavailable or returned empty; used human template fallback.` +
  `data_mode=mock: do not present as real accuracy / hit-rate.`
- **forbidden_hits (all rows):** `[]`
- **whether_sent_to_social:** **no** (none sent)
- **human_review_status:** **pending** · **reviewer_note:** _(awaiting reviewer)_

---

## Drafts

### 1 · vi / preview / match 1
> ⚽ Brazil vs Argentina — Xu hướng AI: Brazil nhỉnh (49.0%).
> Đây là góc nhìn dữ liệu AI, không phải cam kết kết quả.
> Kết quả trong quá khứ không đảm bảo kết quả tương lai. Chỉ phân tích dữ liệu & giải trí.

### 2 · mm / preview / match 1
> ⚽ Brazil vs Argentina — AI အမြင်: Brazil သာ (49.0%)။
> ဤသည် AI ဒေတာအမြင်ဖြစ်ပြီး ရလဒ် အာမခံချက် မဟုတ်ပါ။
> အတိတ်ရလဒ်က အနာဂတ်ကို အာမမခံပါ။ ဒေတာ ခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဖျော်ဖြေရေးအတွက်သာ။

### 3 · vi / upset / match 2
> ⚠️ Rủi ro bất ngờ: Morocco vs France — mức rủi ro low, cần theo dõi đội hình.
> Đây là góc nhìn dữ liệu AI, không phải cam kết kết quả.
> Kết quả trong quá khứ không đảm bảo kết quả tương lai. Chỉ phân tích dữ liệu & giải trí.

### 4 · mm / upset / match 2
> ⚠️ အံ့အားသင့်နိုင်ခြေ: Morocco vs France — အန္တရာယ် low၊ လူစာရင်း စောင့်ကြည့်ပါ။
> ဤသည် AI ဒေတာအမြင်ဖြစ်ပြီး ရလဒ် အာမခံချက် မဟုတ်ပါ။
> အတိတ်ရလဒ်က အနာဂတ်ကို အာမမခံပါ။ ဒေတာ ခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဖျော်ဖြေရေးအတွက်သာ။

### 5 · vi / live / match 3
> 📡 Cập nhật sát giờ · Spain vs Germany: AI tính lại theo đội hình.
> Đây là góc nhìn dữ liệu AI, không phải cam kết kết quả.
> Kết quả trong quá khứ không đảm bảo kết quả tương lai. Chỉ phân tích dữ liệu & giải trí.

### 6 · mm / recap / match 3
> 📊 Spain vs Germany ပြန်သုံးသပ်: AI သုံးသပ်ချက်နှင့် တကယ့်ရလဒ် နှိုင်းယှဉ်။
> ဤသည် AI ဒေတာအမြင်ဖြစ်ပြီး ရလဒ် အာမခံချက် မဟုတ်ပါ။
> အတိတ်ရလဒ်က အနာဂတ်ကို အာမမခံပါ။ ဒေတာ ခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဖျော်ဖြေရေးအတွက်သာ။

### 7 · zh / preview / match 1 (internal management; Chinese expected)
> ⚽ 巴西 vs 阿根廷 — AI 倾向：巴西略占优（49.0%）。
> 这是 AI 数据观点，并非结果承诺。
> 历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。

---

## Notes for the reviewer
- **Team-name localization fixed this round:** vi/mm/en drafts now use the **English** team name
  (Brazil/Argentina, Morocco/France, Spain/Germany) — previously they leaked the Chinese name
  (巴西/阿根廷). zh drafts keep Chinese. (Backend `copy_service._localized_team_names`.)
- All drafts already carry the AI-viewpoint disclaimer and contain **no** betting / guaranteed-hit /
  profit / withdrawal-incentive wording (filter `forbidden_hits=[]`).
- **Approval workflow:** set `human_review_status` to `approved` / `revised` / `rejected` and add a
  `reviewer_note`. Only **approved** copy may be sent by the operator; this engine never sends.

---

## Batch 2 — REAL provider drafts (2026-06-08, draft-only)

> **provenance = real LLM** (`provider_override` against keys already in the local `.env`, pre-existing;
> **no keys printed/committed**). Still `status=draft_only`, `publishable=false`, `data_mode=mock`,
> `whether_sent_to_social=no`, `human_review_status=pending`. `forbidden_hits=[]` for every row.
> Full comparison: `docs/LLM_PROVIDER_COMPARISON_REPORT.md`.

### B2-1 · provider=gemini · provenance=llm:gemini · vi / preview / match 1
> AI xu hướng trận Brazil vs Argentina: Brazil thắng 49.0% / Hòa 26.0% / Argentina thắng 25.0%.
> Độ tin cậy AI: Trung bình cao (61/100). Lý do AI: Brazil có lợi thế sân nhà và phong độ ổn định hơn
> một chút. Tín hiệu rủi ro AI: Cao — hai đội thực lực tương đồng, kết quả phụ thuộc đội hình & chiến
> thuật. Tỷ số AI gợi ý: 2:1 / 1:1. _Lưu ý: Hiệu suất trong quá khứ không đảm bảo kết quả tương lai._

### B2-2 · provider=gemini · provenance=llm:gemini · mm / preview / match 1
> ဘရာဇီး vs အာဂျင်တီးနား ပွဲကြို AI အချက်ပြမှု — AI နိုင်ခြေ: ဘရာဇီး 49.0% | သရေ 26.0% | အာဂျင်တီးနား 25.0%။
> AI ယုံကြည်မှု ၃/၅ ကြယ်ပွင့်။ အန္တရာယ်အဆင့် မြင့်မား — အသင်းနှစ်သင်း အင်အားတူညီနီးပါး၊ ရလဒ်သည် လူစာရင်း/
> နည်းဗျူဟာအပေါ် မူတည်။ AI ခန့်မှန်းရလဒ် 2:1 / 1:1။ _ယခင်စွမ်းဆောင်ရည်များသည် အနာဂတ်ရလဒ်ကို အာမမခံပါ။_ (0 Han)

### B2-3 · provider=deepseek · provenance=llm:deepseek · vi / upset / match 2
> **Cảnh báo bất ngờ: Morocco vs France** — Theo góc nhìn dữ liệu AI, Morocco có 50% cơ hội thắng, Pháp
> 31%. Dù rủi ro thấp (80/100), các yếu tố chính đồng thuận cao. Morocco có thể tạo bất ngờ nếu tận dụng
> tốt cơ hội đầu trận (2:0 / 2:1). Theo dõi lối chơi pressing & chuyển trạng thái.
> _Lưu ý: Dữ liệu mô phỏng, hiệu suất quá khứ không đảm bảo kết quả tương lai._

### B2-4 · provider=deepseek · provenance=llm:deepseek · mm / upset / match 2
> **Morocco vs France — AI Data Signal** — AI မော်ဒယ်က ရှင်းလင်းသော ဦးတည်ချက်ပြထားပြီး အဓိကအချက်များ
> တည်ငြိမ်နေသည်။ သတိပြုရန်: Morocco အိမ်ကွင်းအားသာချက် · France ၏ ဖိအားခံနိုင်စွမ်း။ အဓိကအချက်တူညီသော်လည်း
> လက်တွေ့ပြောင်းလဲမှုက ရလဒ်ကို လွှမ်းမိုးနိုင်သည်။ _မှတ်ချက်: အတိတ်စွမ်းဆောင်ရည်သည် အနာဂတ်ရလဒ်ကို အာမမခံပါ။_

### B2-5 · provider=kimi · provenance=llm:kimi · vi / upset / match 2 — **REJECT (wrong language)**
> _(Kimi returned full Chinese for a Vietnamese request — `han≈112`.)_ **reviewer_note:** rejected —
> language-fidelity failure (Chinese in a vi draft). Do not use Kimi for vi/mm until prompt work closes
> the leak. Compliance still passed (`forbidden_hits=[]`), proving compliant ≠ correct-language.

> **Reviewer reminder:** add a **language-fidelity** check (Han chars in vi/mm = reject) per
> `docs/MINI_AGENT_HARNESS_DESIGN.md` §4. All Batch-2 rows remain `human_review_status=pending`
> except B2-5 (illustrative reject). None sent.
