# MVP-2 — Operator Real-Data Review (API-FOOTBALL Level-2 Scout Pack)

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/mvp2-api-football-ingestion` (off `main`) ·
> **Mode:** implementation (backend ingestion + internal preview; **no public surface, no frontend change**).
> Trigger: **API-FOOTBALL Real Coverage = PASS** ([API_FOOTBALL_COVERAGE_CHECK](API_FOOTBALL_COVERAGE_CHECK.md)).
> This is the operator-facing evidence that **real** Level-2 data is now ingested, normalized, provenance-tagged,
> and viewable in zh + vi. **External operation stays paused.**

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

## 3. Sample fixtures (real)
| render match | fixture_id | match | result | sample JSON |
|---|---|---|---|---|
| 8 | **855737** | Argentina vs Saudi Arabia (WC2022, Group C) | **1–2** | `docs/data_audit/mvp2_scout_pack_samples/855737.json` |
| 13 | **855741** | Germany vs Japan (WC2022, Group E) | **1–2** | `docs/data_audit/mvp2_scout_pack_samples/855741.json` |

Both JSON samples are **redacted + bounded** (whitelisted fields only, no image URLs, no raw vendor payload;
≈ 34–36 KB each). Coverage score = **100%** of the nine tracked sections for both.

## 4. API sections **available** (real data, per fixture)
`fixture` · `teams` · `lineups` (startXI + subs) · `formation` · `coach` · `squad` · `events_summary` ·
`team_statistics` · `player_statistics`. Spot-check (855737): formation Argentina **4-4-2** / Saudi Arabia
**4-1-4-1**; coaches **L. Scaloni** (Argentina) / **H. Renard** (France); events incl. min-10 Messi penalty after
VAR; top rating **Mohammed Al-Owais 7.7** (Saudi GK), **Lionel Messi 7.6** (Argentina). All values come straight
from API-FOOTBALL — nothing is AI-generated.

## 5. API sections **missing**
- **`injuries` — UNRESOLVED.** `/injuries?fixture=` **and** `/injuries?league=1&season=2022` both returned
  **HTTP 200 with 0 results** for both fixtures. Recorded as `missing_evidence.injuries` + `injuries_unresolved=true`.
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
| lang | fixture | path |
|---|---|---|
| 中文 (zh) | 855737 | `docs/qa_screenshots/mvp2_real_data_operator_review/zh_855737_scout_pack.png` |
| 中文 (zh) | 855741 | `docs/qa_screenshots/mvp2_real_data_operator_review/zh_855741_scout_pack.png` |
| Tiếng Việt (vi) | 855737 | `docs/qa_screenshots/mvp2_real_data_operator_review/vi_855737_scout_pack.png` |
| Tiếng Việt (vi) | 855741 | `docs/qa_screenshots/mvp2_real_data_operator_review/vi_855741_scout_pack.png` |

Capture tool (QA-only, not in the build): `scripts/qa/mvp2_scout_pack_shots.mjs` (headless Chrome CDP, full page).

## 8. vi Han check
- **vi rendered HTML Han count = 0** (programmatic, both fixtures).
- **vi visible-text Han count = 0** (tag/style stripped, both fixtures).
- Dynamic values (team/player/coach names, stat types, event types, positions, formations) arrive in Latin script
  from the vendor → no Chinese leaks into the vi page. zh page renders Chinese as intended (≈ 331 Han).

## 9. Security check
- `git grep` finds **no real key** — only variable names (`API_FOOTBALL_KEY`) / the header name (`x-apisports-key`).
- `backend/.env` is gitignored and **not tracked**; `worldcup2026-api.env` not tracked.
- Sample JSON contains **0 URLs** and no `logo`/`photo`/`image` fields (whitelist redaction); size bounded (~35 KB).
- No raw vendor payload committed. Frontend bundle unchanged (the frontend never calls the vendor).

## 10. Compliance check
- **No** betting / odds / market / 盘口 / 竞猜 / 走地 / 滚球 / 大小球 / 让球 in any sample or page (scanned).
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

## Guardrails honored
backend ingestion + internal preview only · **no frontend change** · **no public surface** · token never
printed/committed · no raw payload committed · redacted/bounded samples · odds/market excluded · `42.2%` internal ·
injuries unresolved (not "no injuries") · **external operation paused** · PR #2 untouched.
