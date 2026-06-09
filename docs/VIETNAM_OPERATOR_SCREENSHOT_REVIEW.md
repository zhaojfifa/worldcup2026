# Vietnam Operator Screenshot Review — Heavy Sprint

_Template created 2026-06-08 (Stage 1, plan). **Status: pending** — operator fills after Implementation +
real-device capture. Shots → `docs/qa_screenshots/vietnam_operator_heavy_sprint/`. No screenshot = no PASS._

Paths (vi first): `/detail?lang=vi` · `/report?lang=vi` · `/community?lang=vi`
(then mm as a non-breaking check). Scores are **1–5** (5 = best). `compliance_risk` = none | low | med | high.

## Review rows (operator fills)
| page | screenshot_path | operator_feedback | language_naturalness | data_trust | model_explainability | emotional_hook | ui_flow | compliance_risk | recommended_fix | owner_decision |
|------|-----------------|-------------------|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| /detail?lang=vi |  |  |  |  |  |  |  |  |  |  |
| /report?lang=vi |  |  |  |  |  |  |  |  |  |  |
| /community?lang=vi |  |  |  |  |  |  |  |  |  |  |
| unlock modal (vi) |  |  |  |  |  |  |  |  |  |  |
| report after unlock (vi) |  |  |  |  |  |  |  |  |  |  |

## Required captures (checklist)
- [ ] first screen · [ ] Evidence Strip · [ ] Scout verdict · [ ] factor source/impact/interpretation ·
- [ ] Risk watch · [ ] Watch before kickoff · [ ] unlock modal · [ ] full report · [ ] community entry ·
- [ ] bottom nav · [ ] any toast / modal / action sheet.

## Historical Recap separation — added checks (2026-06-09)
- [ ] **Home current section shows ONLY current/preview matches** (no finished WC-2022 match appears as
      today's signal / today list / top-upset).
- [ ] **Historical Recap is clearly labelled** as `Phục dựng lịch sử · World Cup 2022` /
      `Hiệu chỉnh mô hình · không phải trận hiện tại` (model calibration, **not a current match**).
- [ ] **No hit-rate / 42.2% / accuracy number** shown anywhere in the customer UI.
- [ ] **Would the user tap a recap row** to see a full recap? (signal for the optional recap-row→detail link)
- [ ] If the operator wants it, **recap-row → detail/report link** is a later small polish (**not blocking**).
- Result: `recap_separation_ok: ""` (yes/no) · `recap_label_clear: ""` (yes/no) ·
  `wants_recap_link: ""` (yes/no) · `notes: ""`

## Operator judgement summary (fill after review)
```
overall_status: pending        # pending | pass | pass_with_issues | fail
vi_language_natural: ""        # yes/no + notes
data_supported_feel: ""        # yes/no
model_analysis_feel: ""        # yes/no
tension_and_appeal: ""         # yes/no
willing_to_post_zalo: ""       # yes/no
drives_full_report: ""         # yes/no
drives_community_join: ""      # yes/no
betting_profit_risk: ""        # none/low/med/high
chinese_or_longEnglish_residual: ""   # none / details
top_fixes: ""                  # frontend-only copy/mapping/layout
owner_final_decision: ""
```

> If issues are found, fixes stay **frontend-only** (copy / mapping / layout). Any API/DB need stops and
> returns to Owner. Final PASS is granted only after operator screenshots are reviewed and
> `owner_final_decision` is recorded.
