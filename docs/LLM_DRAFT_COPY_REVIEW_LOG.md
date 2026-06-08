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
