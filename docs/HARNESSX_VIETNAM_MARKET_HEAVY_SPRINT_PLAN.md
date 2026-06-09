# Harness-X Vietnam Market Heavy Sprint — PLAN (Owner review pending)

_Created 2026-06-08 · Harness-X flow: **PLAN → Owner review → Implementation → Engineer QA →
Operator Screenshot Review → Final Owner decision.** This is **Stage 1 (Plan only)** — no feature code._

> **Three roles drive this sprint:** **Engineering** (data / modeling / analysis) · **Product** (flow /
> expression / conversion) · **Operation** (Vietnam real-device screenshots / language / appeal).
> Vietnam (`vi`) is the **first priority**; warm-up / friendly real data is the **first data priority**.

> **Update (2026-06-09) — Owner correction folded in:** this sprint now requires **specific real matches**,
> not league-level guidance. Real Data Recon completed → `docs/REAL_MATCH_INTELLIGENCE_SELECTION.md`
> (upcoming Mexico v South Africa; finished Brazil-Egypt, Argentina-Honduras), modeling status in
> `REAL_MATCH_MODELING_REVIEW.md` (pending_api_sync), vi copy in `VI_REAL_MATCH_OPERATION_COPY.md`. Sync is
> `BLOCKED_OPERATOR_RENDER_SHELL` (operator-run; not faked).

## 1. Sprint Goal
Turn **Giành Cup** into a Vietnam-market **World Cup AI intelligence + fan prediction-game** product with:
real data sources · model-based judgement · Scout persona · natural Vietnamese impact · a complete user
flow · operator screenshot validation · community hand-off.

**What it IS:** AI football intelligence · Scout verdict · risk watch · pre-match update · data-backed
**prediction game** · **fan entertainment**.
**What it is NOT (hard compliance floor):** ❌ not a betting product · ❌ no guaranteed hit · ❌ no
profit/return promise. **Forbidden wording:** 博彩/下注/稳赚/必中/现金收益/保证命中 · cá cược/đặt cược/
chắc thắng/đảm bảo thắng/kiếm tiền/lợi nhuận chắc chắn · လောင်းကစား (negation only). Enforced by
`backend/app/services/llm/compliance.py` + a frontend forbidden-scan in QA.

## 2. Engineering Role Plan — data / modeling / analysis

### 2.1 Data acquisition (priority — warm-ups FIRST)
| Priority | Competition | `league_id` / `season` | Purpose |
|----------|-------------|------------------------|---------|
| **P1** | **Warm-ups / international friendlies** | `league_id=10, season=2026` | happening now → best for **pre-match real analysis + post-match recap** |
| **P2** | 2026 World Cup official fixtures | `league_id=1, season=2026` | formal WC operation prep |
| **P3** | 2022 World Cup backtest | `league_id=1, season=2022` | settled results → recap / settlement-chain validation |

**Engineering reality (verified):** `admin/sync/{fixtures,results}` already accept optional
`?league_id=&season=` (default `wc_league_id=1`/`wc_season=2026`; chain `admin.py` →
`jobs/fixtures_sync` / `services/results/result_sync` → `data_sources/api_football`). **No code/DB change
needed** to pull a competition. ⚠️ Operator must confirm the **API-FOOTBALL key plan covers league 10**;
if not, fall back to a covered competition (La Liga 140 / a covered friendly set) — **do not fabricate**.

**Operator Render Shell Runbook (do NOT fake results):**
```bash
BASE=https://worldcup2026-api-71n6.onrender.com
# P1 — warm-ups / friendlies
curl -X POST "$BASE/api/v1/admin/sync/fixtures?league_id=10&season=2026" \
  -H "Content-Type: application/json" -H "x-admin-token: $ADMIN_API_TOKEN"
curl -X POST "$BASE/api/v1/admin/sync/results?league_id=10&season=2026" \
  -H "Content-Type: application/json" -H "x-admin-token: $ADMIN_API_TOKEN"
curl "$BASE/api/v1/performance/summary"
curl "$BASE/api/v1/data-source/status"   # expect mock_mode=false, requests_used>0
```
**Record (→ `docs/DATA_SOURCE_SYNC_VERIFICATION.md`):** `competition_name · league_id · season · run_at ·
fixtures_inserted · fixtures_updated · fixtures_skipped · results_inserted · results_updated ·
results_settled · errors · requests_used_before · requests_used_after · data_mode_after ·
usable_for_operation · notes`.

### 2.2 Modeling → operation chain
Existing pipeline (no shape change): `match → win_prob → confidence → risk_level → risk_note →
feature impact → Scout verdict → copy draft`. Endpoints: `POST /matches/{id}/refresh` (shape unchanged),
`/performance/summary`. **Per selected match, output:** 1) Scout verdict · 2) win_prob · 3) confidence ·
4) risk_level · 5) **top-3 model signals** · 6) contrarian risk · 7) watch-before-kickoff · 8) operation
copy hooks. (Items 1/5/6/7/8 already render in the Scout layer; this sprint feeds **real** matches through it.)

### 2.3 Data-provenance grading (no seed-as-real)
Every surface tags data as one of: **real provider data · derived signal · seed/operator preview ·
community interaction · LLM draft.** The Evidence Strip caption already states "preview signals · not a
real hit-rate"; when `data_mode=real`, switch the caption to a real-data label (frontend copy only).
**Pages/docs must never present seed as real.**

### 2.4 ⚠️ Key engineering risk — seed-keyed localization vs real teams
`viMapping.ts`/`mmMapping.ts` Scout hook/contrarian/watch + factor source/interpretation are **keyed by
the 3 seed matchups and the seed factor labels** (`巴西|阿根廷`, `中场控制力`, …). **Real matches
(e.g. friendlies) will not match these keys** → they fall back to the **generic localized lines**
(vi/mm, never Chinese) — safe but generic. Also `teamVi` only maps the 6 seed teams; real team names come
from the API (English `name`) and render as-is (acceptable, not Chinese). **Mitigation options (Implementation):**
(a) accept generic fallback for real matches this sprint (lowest risk); (b) generate per-match Scout
hook/contrarian via the **draft-only LLM** (DeepSeek/Gemini) → **human review** → operator copy library
(no auto-publish); (c) add a few more matchup keys for the specific friendlies once fixtures are known.
**Recommended: (a)+(b)** — generic fallback in UI now, LLM drafts for operator forwarding. No DB change.

## 3. Product Role Plan — flow & conversion
Vietnam-priority path: `/?lang=vi → /detail?lang=vi → unlock modal → /report?lang=vi → /community?lang=vi
→ Zalo/Telegram`. Audit questions (answer with screenshots):
1. First glance — what does the user see? 2. Do they instantly know the match's hook? 3. Is the data
basis visible? 4. Is the model's "why" understandable? 5. Why tap the full report? 6. Why join Zalo?
7. Why come back tomorrow? 8. Do MTC / streak / leaderboard help retention?
**Page must surface:** Giành Cup Scout · Evidence Strip · Scout verdict · Risk watch · Contrarian angle ·
Watch before kickoff · Full-report value · Community value. **Conversion levers to sharpen
(frontend copy/layout only):** the unlock CTA should promise *specific* extra evidence (live correction,
full factor list); the community CTA should promise *the live-intel feed*; the home signal card should
lead with the **hook line**, not a flat probability.

## 4. Operation Role Plan — screenshots / review / fixes
Operator captures on a **real phone** (vi first): `/detail?lang=vi · /report?lang=vi · /community?lang=vi`.
**Required shots:** 1) first screen · 2) Evidence Strip · 3) Scout verdict · 4) factor source/impact/
interpretation · 5) Risk watch · 6) Watch before kickoff · 7) unlock modal · 8) full report · 9) community
entry · 10) bottom nav · 11) any toast/modal/action sheet. **Save to
`docs/qa_screenshots/vietnam_operator_heavy_sprint/`.**
**Operator judgement (per page):** vi natural? · acceptable to local users? · data-supported feel? ·
model-analysis feel? · tension/appeal? · willing to post to Zalo? · makes them want the full report? ·
makes them want to join? · any betting/profit/guaranteed-hit risk? · any Chinese / long-English residual?
**New doc `docs/VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md`** (template created this Stage; operator fills later)
with fields: `page · screenshot_path · operator_feedback · language_naturalness_score · data_trust_score ·
model_explainability_score · emotional_hook_score · ui_flow_score · compliance_risk · recommended_fix ·
owner_decision`.

## 5. Vietnamese market copy direction
Drop flat phrasing (`AI phân tích` / `AI cho rằng` / `Dữ liệu cho thấy`). Use intelligence-grade Scout voice:
- `Giành Cup Scout nhìn thấy tín hiệu...`
- `Điểm nóng của trận này là...`
- `Câu hỏi không phải là..., mà là...`
- `Nếu đội này chịu được 20 phút đầu, thế trận có thể đổi chiều.`
- `Đây là trận cần theo dõi rủi ro, không phải trận dễ đọc.`

Worked examples (already shipped for seed; extend pattern):
> `Không phải câu hỏi Brazil mạnh hơn không. Câu hỏi là hàng thủ Argentina chịu được bao lâu.`
> `Giành Cup Scout không xem đây là trận dễ đọc. Tín hiệu chính nằm ở cánh phải Brazil và sự thiếu ổn
> định của hàng thủ Argentina.`

Requirements: **evidence-based · with tension · with suspense · Scout persona · NOT betting · NO hit
guarantee.** New lines land in `dict.ts`/`viMapping.ts` (human-authored) + `OPERATION_COPY_LIBRARY_VI_MM.md`.

## 6. Multi-model / Mini-Agent strategy (explanation & copy, not showmanship)
**Provider roles:** DeepSeek = vi/mm primary draft · Gemini = quality benchmark / co-primary · **Kimi =
zh research / report-style explanation / internal only — not vi/mm output** · human template = fallback.
**Mini-Agent (rules + prompts + draft-only LLM, NO 300-agent runtime):** Data Scout → Baseline Model →
Risk Analyst → Contrarian → Explanation → Copy → Compliance → Human Review. This sprint realizes stages
3/4/5/6 as **per-match LLM drafts** (DeepSeek/Gemini) logged in `LLM_DRAFT_COPY_REVIEW_LOG.md`; **stage 7**
adds the **language-fidelity** check (Han in vi/mm = reject); **stage 8** is human. Nothing auto-published.

## 7. Implementation Proposal (for Owner approval — not executed in Stage 1)
**Frontend (copy/mapping/layout only):** `DetailPage.tsx`, `ReportPage.tsx`, `FeatureBars.tsx`,
`i18n/dict.ts`, `i18n/viMapping.ts`, `styles/global.css` — sharper vi Scout copy, real-data Evidence-Strip
caption, conversion-lever CTA copy, optional extra friendly-match matchup keys.
**Docs:** `OPERATION_COPY_LIBRARY_VI_MM.md`, `LLM_DRAFT_COPY_REVIEW_LOG.md`,
`VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md`, `DATA_SOURCE_SYNC_VERIFICATION.md`, `REAL_DATA_CALIBRATION_PLAN.md`.
**Backend:** **default NO change.** Only if the sync runbook exposes a real gap. **If backend is
proposed, the plan must state:** why · risk · API-shape impact · DB impact · rollback · *Owner approval
needed*. **Current assessment: NO backend/API/DB change required** (override already supported).

## 8. QA & Verification (three layers)
**8.1 Engineer QA:** `npm run build` · no console error · vi/mm Han scan = 0 on interactive path ·
price isolation (vi VND / mm MMK / zh RMB) · forbidden-phrase scan · 390 & 430 screenshots · modal/toast/
action-sheet interactive scan · **no backend/API diff.**
**8.2 Product QA:** Home→Detail→Report→Community path · unlock path · Zalo/Telegram entry · MTC/leaderboard/
retention entry.
**8.3 Operation QA (real device):** language · emotional hook · data trust · model explainability ·
screenshot shareability · Zalo readiness · compliance safety.
**Screenshots → `docs/qa_screenshots/vietnam_operator_heavy_sprint/`. No screenshot = no PASS.**

## 9. Acceptance Criteria
**PASS:** vi natural · page shows data sources · page shows model basis · copy is appealing · flow guides
to full report + community · screenshots usable for operation · no Chinese residual · no betting/hit/profit
risk · build passes · operator screenshot review passes.
**PASS WITH ISSUES:** engineering done, operator flags minor copy/crowding/redirect fixes.
**FAIL:** language unnatural · data basis still invisible · model explanation still flat · operator won't
forward · compliance risk · screenshots missing.

## 10. Required Documents (created/updated across the sprint)
`docs/HARNESSX_VIETNAM_MARKET_HEAVY_SPRINT_PLAN.md` (this) · `docs/VIETNAM_OPERATOR_SCREENSHOT_REVIEW.md`
(template now) · `docs/DATA_SOURCE_SYNC_VERIFICATION.md` · `docs/REAL_DATA_CALIBRATION_PLAN.md` ·
`docs/OPERATION_COPY_LIBRARY_VI_MM.md` · `docs/LLM_DRAFT_COPY_REVIEW_LOG.md` · `docs/MVP_STATUS.md` ·
`docs/HANDOFF_TO_NEXT_ENGINEERING_CHAT.md` · `CLAUDE.md`.

---

### Owner review checklist (Stage 2)
1. **Data priority** flipped to **warm-ups/friendlies first** (`league_id=10, season=2026`) — confirm,
   and confirm the API-FOOTBALL key covers league 10 (else pick a covered competition).
2. **Backend/API/DB:** **no change proposed** (sync override already exists). Confirm none is authorized
   without a return-to-Owner.
3. **Seed-keyed localization risk** (real matches → generic fallback + LLM drafts) — approve approach (a)+(b).
4. **vi/mm:** vi first priority; mm not broken; zh internal; en fallback. No Chinese on vi/mm.
5. **QA + operator screenshots** mandatory; `docs/qa_screenshots/vietnam_operator_heavy_sprint/`.
6. **Compliance:** prediction-game/entertainment framing only; no betting/hit-rate/profit.
7. Recommendation: **ready to enter Implementation on Owner approval** (frontend copy/mapping + docs;
   operator runs the real-data runbook on Render in parallel).
