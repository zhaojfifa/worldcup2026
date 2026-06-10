# MVP-2 — Operator Real-Data Review (API-FOOTBALL Level-2 Scout Pack)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (off `main`) ·
> **Mode:** implementation (backend ingestion + internal preview; **no public surface, no frontend change**).
> Trigger: **API-FOOTBALL Real Coverage = PASS** ([API_FOOTBALL_COVERAGE_CHECK](API_FOOTBALL_COVERAGE_CHECK.md)).
> This is the operator-facing evidence that **real** Level-2 data is now ingested, normalized, provenance-tagged,
> and viewable in zh + vi. **External operation stays paused.**
>
> **Updated 2026-06-10 (Operator Real-Data Acceptance Sprint):** four sample fixtures — **855737, 855741,
> 977345, 979139** — with a four-match comparison (§3.1) and an **Operator Acceptance Decision** form (§13).
>
> **Updated 2026-06-10 (Data-to-Scout-Report Productization Sprint):** 855737 now has a **productized operator
> report** (data → features → model notes → zh/vi report); the internal preview is **report-first** (raw + ledger
> collapsed). See the **Productized Scout Report Review** (§14), design
> [MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN](MVP2_PRODUCTIZED_SCOUT_REPORT_DESIGN.md), and next-data
> [MVP2_NEXT_DATA_REQUIREMENTS](MVP2_NEXT_DATA_REQUIREMENTS.md).

---

## 1. This round's goal
Let operations **see real API-FOOTBALL Level-2 data** — not more data-source verification, not AI copy packaging:
pull → normalize into an internal **Scout Pack** → tag every field with `source_ledger` → mark gaps as
`missing_evidence` → emit a **redacted** JSON → render an **internal** operator preview (zh + vi) → capture
screenshots. **Public operation is NOT resumed.**

## 2. Data source
- **Vendor:** API-FOOTBALL (`https://v3.football.api-sports.io`), header `x-apisports-key`.
- **Plan:** **Pro**, active (verified live via `/status`). Daily budget ≈ **7,500 req/day** (this round used ≈ 70).
- **Key handling:** read **server-side only** (gitignored `backend/.env`); **never printed / logged / committed /
  written into the Scout Pack**. The frontend never touches the vendor — the backend proxies + renders.
- **Server-side client:** `backend/app/services/api_football_client.py` (timeout · 429 backoff · request budget ·
  secret-free logging of endpoint/status/results/fixture only).

## 3. Sample fixtures (real) — four matches
| render match | fixture_id | match | result | sample JSON |
|---|---|---|---|---|
| 8 | **855737** | Argentina vs Saudi Arabia (WC2022, Group C) | **1–2** | `855737.json` |
| 13 | **855741** | Germany vs Japan (WC2022, Group E) | **1–2** | `855741.json` |
| 58 | **977345** | Morocco vs Spain (WC2022, Round of 16) | **0–0** (won on pens) | `977345.json` |
| 67 | **979139** | Argentina vs France (WC2022, Final) | **3–3** (won on pens) | `979139.json` |

Samples live in `docs/data_audit/mvp2_scout_pack_samples/`. All four are **redacted + bounded** (whitelisted
fields only, no image URLs, no raw vendor payload; ≈ 34–37 KB each), coverage = **100%** of the nine tracked
sections. Knockout matches 977345 / 979139 were decided on penalties — the score shown is regulation/extra-time.

### 3.1 Four-match comparison
Screenshot filenames below are under `docs/qa_screenshots/mvp2_real_data_operator_review/`.

| fixture_id | teams (score) | formations H/A | coaches H/A | lineup | events | stats | player stats | squad H/A | injuries | ledger | missing | zh shot | vi shot | vi Han |
|---|---|---|---|:--:|:--:|:--:|:--:|:--:|---|:--:|:--:|---|---|:--:|
| 855737 | Argentina 1–2 Saudi Arabia | 4-4-2 / 4-1-4-1 | L. Scaloni / H. Renard | yes | 20 | yes | yes | 26/26 | unresolved (0) | yes | yes | `zh_855737_scout_pack.png` | `vi_855737_scout_pack.png` | 0 |
| 855741 | Germany 1–2 Japan | 4-2-3-1 / 4-2-3-1 | H. Flick / H. Moriyasu | yes | 14 | yes | yes | 26/26 | unresolved (0) | yes | yes | `zh_855741_scout_pack.png` | `vi_855741_scout_pack.png` | 0 |
| 977345 | Morocco 0–0 Spain | 4-3-3 / 4-3-3 | W. Regragui / Luis Enrique | yes | 21 | yes | yes | 26/26 | unresolved (0) | yes | yes | `zh_977345_scout_pack.png` | `vi_977345_scout_pack.png` | 0 |
| 979139 | Argentina 3–3 France | 4-3-3 / 4-2-3-1 | L. Scaloni / D. Deschamps | yes | 35 | yes | yes | 26/26 | unresolved (0) | yes | yes | `zh_979139_scout_pack.png` | `vi_979139_scout_pack.png` | 0 |

## 4. API sections **available** (real data, per fixture)
`fixture` · `teams` · `lineups` (startXI + subs) · `formation` · `coach` · `squad` · `events_summary` ·
`team_statistics` · `player_statistics`. Spot-check (855737): formation Argentina **4-4-2** / Saudi Arabia
**4-1-4-1**; coaches **L. Scaloni** (Argentina) / **H. Renard** (France); events incl. min-10 Messi penalty after
VAR; top rating **Mohammed Al-Owais 7.7** (Saudi GK), **Lionel Messi 7.6** (Argentina). All values come straight
from API-FOOTBALL — nothing is AI-generated. **All four fixtures show the same 100% section coverage — see §3.1.**

## 5. API sections **missing**
- **`injuries` — UNRESOLVED.** `/injuries?fixture=` **and** `/injuries?league=1&season=2022` both returned
  **HTTP 200 with 0 results** for all four fixtures. Recorded as `missing_evidence.injuries` + `injuries_unresolved=true`.
  Rendered as **"source required"** (zh: 伤停数据未返回，需二次数据源或当前赛季复验 / vi: *Dữ liệu chấn thương chưa
  có, cần xác minh bằng nguồn thứ hai hoặc mùa giải hiện tại*). **It is NOT written as "no injuries", and no player
  absence impact is inferred.** Resolution path: second source or a current/upcoming-fixture check.

## 6. Internal preview
- **Route (not in public nav):** `GET /internal/scout-pack?fixture_id=<id>&lang=zh|vi`
  (`backend/app/routers/internal_scout_pack.py`). Server-side HTML; reads the cached sample JSON
  (**no vendor call at render, no DB, no key needed**); `noindex`; production-gated by admin token
  (header `x-admin-token` or `?token=`), open in dev/local for screenshots.
- Shows: data source · fixture_id · last_checked_at · plan · coverage · fixture · teams · formation · coach ·
  lineups · events summary · team statistics · player statistics summary · squad · **source ledger** ·
  **missing evidence (injuries source-required)** · **AI allowed / AI forbidden fields**. No AI deep analysis.

## 7. Screenshots
All under `docs/qa_screenshots/mvp2_real_data_operator_review/`.

| lang | fixture | file |
|---|---|---|
| 中文 (zh) | 855737 | `zh_855737_scout_pack.png` |
| 中文 (zh) | 855741 | `zh_855741_scout_pack.png` |
| 中文 (zh) | 977345 | `zh_977345_scout_pack.png` |
| 中文 (zh) | 979139 | `zh_979139_scout_pack.png` |
| Tiếng Việt (vi) | 855737 | `vi_855737_scout_pack.png` |
| Tiếng Việt (vi) | 855741 | `vi_855741_scout_pack.png` |
| Tiếng Việt (vi) | 977345 | `vi_977345_scout_pack.png` |
| Tiếng Việt (vi) | 979139 | `vi_979139_scout_pack.png` |

Capture tool (QA-only, not in the build): `scripts/qa/mvp2_scout_pack_shots.mjs` (headless Chrome CDP, full page;
accepts fixture-id args, defaults to all four).

## 8. vi Han check
- **vi rendered HTML Han count = 0** (programmatic, all four fixtures).
- **vi visible-text Han count = 0** (tag/style stripped, all four fixtures).
- Dynamic values (team/player/coach names, stat types, event types, positions, formations) arrive in Latin script
  from the vendor → no Chinese leaks into the vi page. zh pages render Chinese as intended (≈ 331–341 Han each).

## 9. Security check
- `git grep` finds **no real key** — only variable names (`API_FOOTBALL_KEY`) / the header name (`x-apisports-key`).
- `backend/.env` is gitignored and **not tracked**; `worldcup2026-api.env` not tracked.
- All four sample JSONs contain **0 URLs** and no `logo`/`photo`/`image` fields (whitelist redaction); bounded ≈ 34–37 KB.
- No raw vendor payload committed. Frontend bundle unchanged (the frontend never calls the vendor).

## 10. Compliance check
- **No** betting / odds / market / 盘口 / 竞猜 / 走地 / 滚球 / 大小球 / 让球 in any sample or page (4 samples, 8 pages scanned).
- **No `42.2%`** anywhere in the customer-/operator-visible surface.
- `coverage_score` is explicitly labelled **data-coverage only — not a prediction hit-rate, not a financial signal**.
- `injuries` → "source required" (never "no injuries"); AI restricted to **verified** fields only.
- MTC / payment / bot auto-publish / scaling: **untouched**. Compliance floor unaffected.

## 11. Operator conclusion
| question | answer |
|---|---|
| real data visible | **YES** (lineups / formation / coach / events / team & player stats, both fixtures, zh + vi) |
| source ledger visible | **YES** (per-field source / endpoint / results / http / confidence / license / available) |
| missing evidence visible | **YES** (injuries shown as source-required, unresolved) |
| **ready for public operation** | **NO** — internal verification only; commercial terms Owner-gated; injuries unresolved; operator real-device + Owner sign-off pending |

## 12. Next (Owner-gated, not in this round)
1. Operator real-device review of the zh + vi previews (Render), record decision.
2. Resolve `injuries` via a current/upcoming fixture or a second source before any availability feature.
3. Confirm API-FOOTBALL commercial terms for a paid product (plan is Pro, but terms are Owner-gated).
4. Only then consider the Phase-4 customer Evidence Board (still a separate, gated step).

## 13. Operator Acceptance Decision

> To be completed by the **operator** after reviewing the zh + vi previews (screenshots §7 / §3.1).
> The "engineer pre-assessment" column is verified evidence from this round; the **operator decision** column is
> the operator's to mark. `ready for public operation` is **locked NO** by Owner ruling.

| acceptance item | engineer pre-assessment (evidence) | operator decision |
|---|---|---|
| real data visible | **YES** — 4 fixtures, all 9 sections, zh + vi | ☐ yes ☐ no |
| zh readable | YES (engineer) — see zh screenshots | ☐ yes ☐ no |
| vi readable | YES (engineer) — see vi screenshots | ☐ yes ☐ no |
| vi Han = 0 | **YES** — verified (rendered + visible text, all 4) | ☐ yes ☐ no |
| source ledger understandable | YES (engineer) — per-field provenance table | ☐ yes ☐ no |
| missing evidence understandable | YES (engineer) — injuries shown source-required | ☐ yes ☐ no |
| injuries gap acceptable for MVP-2 prototype | engineer: acceptable — marked unresolved, never faked | ☐ yes ☐ no |
| ready for public operation | **NO** (Owner-fixed; operation paused) | ☑ no (locked) |
| ready for Evidence Board v2 design | engineer: data contract is sufficient to start design | ☐ yes ☐ no |
| ready for backend schema migration | engineer: schema proposal exists (architecture §3); needs Owner GO | ☐ yes ☐ no |

**Operator sign-off:** name ____________ · date ____________ · decision: ☐ accept ☐ accept-with-conditions ☐ reject
**Final Owner decision:** ____________________________________________

---

## 14. Productized Scout Report Review

The raw scout-pack page is engineer-facing; this round turns **855737 (Argentina 1–2 Saudi Arabia)** into an
operator-readable **product report**, proving the full flow `data → features → model notes → scout report →
zh/vi content → operator review → data gap list`.

**Artifacts (all real, derived offline from the cached pack):**
- Feature snapshot: `docs/data_audit/mvp2_feature_snapshots/855737.json`
- Model notes (post-match explanation, not prediction): `docs/data_audit/mvp2_model_notes/855737.json`
- Productized report: `docs/data_audit/mvp2_productized_reports/855737.zh-CN.json` · `855737.vi-VN.json`
- Screenshots: `docs/qa_screenshots/mvp2_real_data_operator_review/zh_855737_productized_report.png` ·
  `vi_855737_productized_report.png`
- Build script (offline, no API): `backend/scripts/mvp2_build_productized_report.py`

**What the report shows (real data):** verdict ("控球占优却 1–2 不敌 → 典型爆冷"); why (Messi 10' pen → Saudi
48'/53' second-half turnaround); evidence cards (possession 69%/31%, shots 15/3, pass acc 85%/68%, **GK rating
6.0/7.7, GK saves 0/5**); 8 explanation signals each with `source_refs`; an operator content draft (zh + vi);
missing data (injuries unresolved, xG not ingested); next data needed; AI boundary. Raw Scout Pack + Source
Ledger are retained but **collapsed**.

**Verified:** every conclusion carries `source_refs`; **no** win probability / odds / betting / market / SHAP /
xG value / injury inference; vi report Han = **0**; report-first preview confirmed; build/contract/route checks pass.

### Productized Scout Report — operator checklist
> Engineer pre-assessment = evidence from this round; **operator decision** is the operator's to mark.

| check item | engineer pre-assessment | operator decision |
|---|---|---|
| real report readable | YES — verdict-first, prose then cards | ☐ yes ☐ no |
| match verdict understandable | YES — one-line upset verdict | ☐ yes ☐ no |
| evidence cards understandable | YES — possession/shots/GK as home/away | ☐ yes ☐ no |
| model notes understandable | YES — 8 signals + interpretation + source | ☐ yes ☐ no |
| content draft useful | YES (engineer) — shareable zh/vi post + disclaimer | ☐ yes ☐ no |
| missing data clear | YES — injuries source-required, xG not ingested | ☐ yes ☐ no |
| next data needed clear | YES — P0 injuries, P1 xG, → requirements doc | ☐ yes ☐ no |
| AI boundary clear | YES — allowed vs forbidden fields shown | ☐ yes ☐ no |
| zh usable for operation | YES (engineer) | ☐ yes ☐ no |
| vi usable for operation | YES (engineer, Han=0) | ☐ yes ☐ no |
| ready for Evidence Board v2 design | engineer: yes — pipeline + contract proven | ☐ yes ☐ no |

**Operator sign-off:** name ____________ · date ____________ · decision: ☐ accept ☐ accept-with-conditions ☐ reject
**Final Owner decision:** ____________________________________________

---

## Guardrails honored
backend ingestion + internal preview only · **no frontend change** · **no public surface** · token never
printed/committed · no raw payload committed · redacted/bounded samples · odds/market excluded · `42.2%` internal ·
injuries unresolved (not "no injuries") · **external operation paused** · PR #2 untouched.
