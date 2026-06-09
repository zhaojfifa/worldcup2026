# Real Data zh + vi — Operator Review

_Created 2026-06-10 · Real Data Verification Sprint (branch `feature/real-data-zh-vi-verification`).
Rollback tag: `v0.8-real-data-verify-start`. zh + vi are the verification languages; mm not broken._

> **Status: pending operator.** Engineer self-verification done (build PASS, vi Han=0, zh regression,
> 42.2% absent from UI). **Final PASS pending operator real-device review.** No screenshot = no PASS.

## Data-type legend
`current_preview` = seed scheduled (not real-synced) · `historical_recap` = WC-2022 finished (calibration,
not current) · `real_synced` = real fixtures pulled from provider · `seed_preview` = seed demo data.

## Data re-pull status (operator-run on Render; Claude has no token → not fabricated)
**`BLOCKED_OPERATOR_RENDER_SHELL` for Claude.** Last known gate result (2026-06-09, to be re-confirmed):
friendlies `10/2026` = **0**; WC `1/2026` = **0** (2026 unavailable); WC `1/2022` = **64/64/64**
(historical, backtest only). Re-run runbook: `docs/DATA_SOURCE_SYNC_VERIFICATION.md` §13. **Until a
re-pull returns current matches, current pages are `current_preview` (seed), not `real_synced`.**

## Engineer-captured screenshots (`docs/qa_screenshots/real_data_zh_vi_verification/`)
zh: `home-zh-390.png` · `detail-zh-current-390.png` · `report-zh-current-390.png` · `detail-zh-finished-recap-390.png`
vi: `home-vi-390.png` · `detail-vi-current-390.png` · `report-vi-current-390.png` · `community-vi-390.png` ·
`detail-vi-finished-recap-390.png` · `report-vi-finished-recap-390.png`
(Historical-recap shots captured with temporary injected finished mock matches — reverted; real finished
data lives on Render for the operator's real-device pass.)

## Review rows (operator fills)
| page | language | screenshot_path | data_type | operator_feedback | data_clarity | model_explainability | language_naturalness | emotional_hook | ui_flow | compliance_risk | recommended_fix | owner_decision |
|------|----------|-----------------|-----------|-------------------|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| / | zh | home-zh-390.png | current_preview |  |  |  |  |  |  |  |  |  |
| /detail | zh | detail-zh-current-390.png | current_preview |  |  |  |  |  |  |  |  |  |
| /report | zh | report-zh-current-390.png | current_preview |  |  |  |  |  |  |  |  |  |
| /detail (finished) | zh | detail-zh-finished-recap-390.png | historical_recap |  |  |  |  |  |  |  |  |  |
| / | vi | home-vi-390.png | current_preview + historical_recap |  |  |  |  |  |  |  |  |  |
| /detail | vi | detail-vi-current-390.png | current_preview |  |  |  |  |  |  |  |  |  |
| /report | vi | report-vi-current-390.png | current_preview |  |  |  |  |  |  |  |  |  |
| /community | vi | community-vi-390.png | current_preview |  |  |  |  |  |  |  |  |  |
| /detail (finished) | vi | detail-vi-finished-recap-390.png | historical_recap |  |  |  |  |  |  |  |  |  |
| /report (finished) | vi | report-vi-finished-recap-390.png | historical_recap |  |  |  |  |  |  |  |  |  |

## Engineer self-verification (this sprint)
- **Build:** `tsc -b && vite build` ✅. **vi Han = 0** (home/detail/report, current + finished). **zh** Chinese
  (regression). **mm** not broken (recap labels English by design).
- **Current vs historical separation:** Home current surfaces (signal/today/upsets) exclude finished matches;
  finished show only under the labelled **Historical Recap · WC2022** surface; Detail/Report show a recap banner.
- **Finished evidence caption fixed:** Report evidence-strip caption is now recap-aware — finished shows
  `Dữ liệu lịch sử · hiệu chỉnh mô hình · không phải trận hiện tại` (zh `历史数据 · 模型校准 · 非当前比赛`)
  instead of the pre-match preview caption.
- **42.2% / hit_rate:** **not in any customer UI** (the only "hit-rate" string is the negation "không phải
  tỷ lệ trúng thực tế"). No betting/profit/guaranteed-hit.
- **Backend/API/DB:** unchanged. Only frontend copy + one conditional (recap caption).

## Result fields (operator → owner)
```
overall_status: pending          # pending | pass | pass_with_issues | fail
current_preview_clear: ""        # is "current preview / not real-synced" clear? yes/no
historical_recap_clear: ""       # is WC2022 recap clearly "not current"? yes/no
vi_language_natural: ""           # yes/no + notes
no_chinese_in_vi: ""              # yes/no
no_hitrate_or_betting_risk: ""    # yes/no
willing_to_post_zalo: ""          # yes/no
top_fixes: ""                     # frontend-only copy/mapping/layout
owner_final_decision: ""
```
