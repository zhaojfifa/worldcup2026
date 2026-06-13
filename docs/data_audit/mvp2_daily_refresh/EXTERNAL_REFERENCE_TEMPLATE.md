# External Strong-Information Reference — TEMPLATE（internal · reference-only）

> Copy this file to `external_reference_YYYYMMDD.md` (same directory) and fill it by hand.
> **INTERNAL OPERATOR DOCUMENT — never customer-facing, never linked from any customer surface.**
>
> Policy (Owner P1.2 §6): public prediction-market / forecast / expectation pages may be CHECKED
> as information references only. They never decide our call; they may inform the persona's
> 外部预期 framing. Raw source wording stays in `raw_signal_operator_note` (this file only).
> Customer copy may use ONLY the sanctioned vocabulary:
> 外部预期 · 公开预测倾向 · 市场共识 · 热度集中 · 情绪变化 · 冷门变量 · 临场变量
> — e.g. 「外部预期偏向 X」「公开倾向集中在热门方」「冷门变量被低估」「热度变化明显」.
> No external trading links, no raw market language, in anything a customer can see.

## Entry（repeat one block per signal）

```yaml
source_name:               # e.g. public prediction market / forecast page (name only)
source_url:                # operator reference only — NEVER pasted into customer copy
captured_at:               # 2026-06-13T08:00Z
fixture:                   # 1489371 Brazil vs Morocco
raw_signal_operator_note:  # what the source literally shows (internal wording allowed HERE only)
safe_customer_summary:     # sanctioned-vocabulary rewrite, e.g. 外部预期偏向巴西，热度集中在热门方
influence_on_our_call:     # none | framing-only | flagged-to-Owner（we never auto-adjust the model call）
```

## Rules checklist（tick before any of this informs customer copy）
- [ ] safe_customer_summary uses ONLY the sanctioned vocabulary above
- [ ] no source link / platform name in customer-facing output
- [ ] the persona judgement (main_lean / scoreline band) was NOT rewritten to match the source
- [ ] if the signal contradicts our call, it is recorded as 冷门变量/临场变量 framing, not a flip
