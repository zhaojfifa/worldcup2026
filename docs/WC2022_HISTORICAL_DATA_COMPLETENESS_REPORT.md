# WC2022 Historical Data — Completeness Report (Validation Pack v1)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft)
> **Sprint:** WC2022 Historical Validation Pack · **Source:** live Render API (read-only), `mock_mode=true`.
> **Machine-readable companion:** [`docs/data_audit/wc2022_historical_completeness.json`](data_audit/wc2022_historical_completeness.json)
> **Rule:** real API only, **no fabrication**. Fields unconfirmable via the public API are recorded `unknown`.

---

## 0. Headline

`total_matches=67` · `finished_count=64` (WC2022, id 4–67) · `scheduled_count=3` (seed, id 1–3).
**Verdict: `PASS WITH ISSUES`.** The WC2022 set is **complete at the fixture / result / baseline-prediction +
backtest level** and supports those validations. It is **NOT complete football-intelligence data**: every
finished match has **no detailed report** (0/64), no player/coach/lineup/injury/media/odds, and the **per-match
actual result is not exposed** via the public API (only aggregate settlement). This matches the Owner's
conclusion exactly.

---

## 1. Field-completeness audit (64 finished matches)

### 1a. Coverage table (live API, all 64)

| # | Field | Present | Missing | Unknown | Notes |
|---|-------|---------|---------|---------|-------|
| 1 | id / match_id | 64 | 0 | 0 | |
| 2 | external_id | 64 | 0 | 0 | `AF-xxxxxx` (API-FOOTBALL fixture id) |
| 3 | home_team (name) | 64 | 0 | 0 | |
| 4 | away_team (name) | 64 | 0 | 0 | |
| 5 | flags | 64 | 0 | 0 | **but 95/128 slots are generic `⚽` placeholders** (only mapped teams have real flags) |
| 6 | kickoff_time | 64 | 0 | 0 | |
| 7 | status | 64 | 0 | 0 | all `finished` |
| 8 | win_prob | 64 | 0 | 0 | baseline model, sums 100 |
| 9 | recommended_score | 64 | 0 | 0 | **a prediction (e.g. "2:1 / 1:1"), NOT the real scoreline** |
| 10 | risk_level | 64 | 0 | 0 | low/medium/high |
| 11 | risk_note | 64 | 0 | 0 | |
| 12 | confidence | 64 | 0 | 0 | |
| 13 | updated_at | 64 | 0 | 0 | |
| 14 | free_note | 64 | 0 | 0 | templated baseline note |
| 15 | live_correction | **1** | 63 | 0 | **only match 8** — a demo/simulate artifact; correctly hidden on recap |
| 16 | final result / actual winner | 0 | 0 | **64** | **not exposed via public API** (no score/winner field) |
| 17 | settled status (per match) | 0 | 0 | **64** | only aggregate `total_settled=64` is exposed |
| 18 | prediction outcome (per match) | 0 | 0 | **64** | only aggregate `hit_count=27` is exposed |
| 19 | report availability | **0** | **64** | 0 | every `/reports/{id}` → **404** |
| 20 | feature / factor availability | **0** | **64** | 0 | empty for all finished (depends on report) |
| – | tag | 0 | 64 | 0 | all null (informational) |

### 1b. missing_field_summary
- **Hard-missing (schema exists, empty for finished):** `report` (64/64), `feature_factors` (64/64),
  `live_correction` (63/64), `tag` (64/64).
- **Not exposed via public API (→ `unknown`):** per-match `final_result/actual_winner`, per-match
  `settled_status`, per-match `prediction_outcome`. (Aggregates exist; per-match does not.)
- **Data-quality:** 95/128 team-flag slots are the generic `⚽` placeholder; `recommended_score` is a
  prediction, not a real scoreline.

### 1c. report coverage
- `report_available_count = 0` · `report_missing_count = 64`. **100% of finished matches have no detailed
  report** — this is exactly the condition the Evidence Pack surfaces.

### 1d. fields_available_for_customer_ui (honest)
Fixture (teams + kickoff + `finished` status), baseline `win_prob` (win/draw/loss), `risk_level`,
`confidence`, recap status, and the **Evidence Pack missing-data notice**. (`recommended_score` is shown only
as a neutralized "—" on recaps because it is a prediction, not a result.)

### 1e. fields_missing_for_deep_intelligence
`report/feature_factors`, real `final_score/actual_winner` (customer-visible), coach, squad/player list,
starting XI, substitutes, injuries/suspensions, media/news signal, odds/market movement.

### 1f. recommended_next_step
1. **No UI change needed** — Evidence Pack already states this state correctly (verified, see §5).
2. To AUTO-select upset/favorite-fail stories: **expose per-match actual result via API** (backend/API change →
   **Owner gate**). Until then, recap stories stay **human-curated** (8/13/58/67).
3. Deep intelligence (coach/squad/XI/injury) requires the **operator** API-FOOTBALL paid sync — for **real
   WC2026**, not WC2022.
4. Optional polish: map remaining team flags (frontend dict) to remove `⚽` placeholders.

---

## 2. Machine-readable artifact
[`docs/data_audit/wc2022_historical_completeness.json`](data_audit/wc2022_historical_completeness.json) —
`source: render_api`, `checked_at` (UTC), `field_coverage`, `report_coverage`, `backtest_summary_internal_only`,
`not_exposed_via_public_api`, and `sample_matches` (8/13/58/67). Regenerated from the live API; nothing fabricated.

---

## 3. Backtest usability (INTERNAL ONLY — not customer-facing)

From `GET /performance/summary` over the 64 settled matches:

| metric | value |
|---|---|
| total_settled | 64 |
| hit_count | 27 |
| **hit_rate** | **42.2%** |
| high_confidence_hit_rate | 42.5% |
| live_correction_uplift | **-42.9%** (live correction *reduced* backtest accuracy) |
| risk low | 23 settled · 11 hit · 47.8% |
| risk medium | 24 settled · 12 hit · 50.0% |
| risk high | 17 settled · 4 hit · 23.5% |

**Reading (mandatory framing):**
- ✅ Usable for **internal model calibration** (risk-tier and confidence sanity checks).
- ❌ **Not** customer-facing accuracy. **`42.2%` is a technical backtest/settlement metric — do NOT add it to
  any UI and do NOT call it marketing accuracy.** (Verified absent from UI; see §5.)
- ❌ Does **not** prove current **2026** prediction ability (different competition, baseline model, n=64).
- ⚠️ `live_correction_uplift = -42.9%` confirms the live-correction logic is a **demo capability, not a
  validated edge** — another reason it is suppressed on recap surfaces.

---

## 4. Derived-capability assessment (from the 64-match set)

| capability | derivable_now | needs_new_source | sample_limitations | ui_candidate | zh_label | vi_label |
|---|---|---|---|---|---|---|
| recent_form_5 | **partial** | yes | single tournament; 3–7 matches/team; per-match result not exposed | no | 近 5 场战绩 | Phong độ 5 trận gần nhất |
| head_to_head_summary | **no** | yes | most pairs meet 0–1× in one tournament → insufficient | no | 历史交锋 | Lịch sử đối đầu |
| upset_cases | **no** | yes | needs per-match actual winner (not exposed); famous ones are human-curated | partial (curated) | 爆冷案例 | Các trận bất ngờ |
| favorite_failed_cases | **no** | yes | needs actual winner vs predicted favorite | no | 热门球队失手 | Đội được đánh giá cao thua trận |
| confidence_bucket_calibration | **partial** | no | only high-vs-overall exposed; n=64; INTERNAL only | no | 信心分桶校准 | Hiệu chỉnh theo nhóm độ tin cậy |
| risk_level_calibration | **yes** | no | n=64 (low 23 / med 24 / high 17); INTERNAL backtest only | no | 风险等级校准 | Hiệu chỉnh theo mức rủi ro |

**Conclusion:** the WC2022-only set yields **no new customer-UI intelligence field** on its own — it is an
**internal calibration asset** (risk/confidence) plus a **curated-story source**. `recent_form_5` and
`head_to_head` are blocked by sample size; `upset/favorite` derivation is blocked by the **unexposed per-match
result**. (No "last 5" is fabricated; nothing is extrapolated beyond the WC2022 range.)

---

## 5. Product validation conclusion

### Can validate now
- ✅ WC2022 historical recap entry (Home recap section → deep links).
- ✅ Fixture display + `finished` status (teams, kickoff). *Result = settled/recap state; **no real scoreline** shown.*
- ✅ Baseline probability display (win/draw/loss, confidence, risk).
- ✅ Technical backtest summary — **internal only** (42.2% family).
- ✅ Upset / favorite-fail **story selection** — via **human curation** (8/13/58/67), **not** API-derived.
- ✅ Evidence Pack missing-data honesty (validated: 0/64 reports → Evidence Pack on all recaps).

### Cannot validate yet
- ❌ player-level intelligence · ❌ coach-level intelligence · ❌ starting-XI impact ·
  ❌ injury/suspension impact · ❌ media/news signal · ❌ odds/market movement · ❌ live 2026 prediction.

---

## 6. Frontend check (this sprint)
Audit confirmed the Evidence Pack's claims are **accurate** (connected = fixture/settled-result/win-prob/recap;
missing = players/coach/XI/injury/media/odds; reports 0/64). **No Evidence Pack error found → no frontend change
this sprint** (docs/audit only). Build re-run for branch health (§ self-verify).

## 7. Guardrails honored
No backend/API/DB change · no operator sync run/faked · no fabricated data (`unknown` where unconfirmable) ·
`42.2%` kept docs/internal only (never UI) · vi Han unaffected (no frontend change) · PR #2 stays Draft.
