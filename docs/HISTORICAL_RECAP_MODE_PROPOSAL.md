# Historical Recap Mode — Proposal (Plan only, no code)

_Created 2026-06-09 · After the Fast Real Data Gate: 2026 unavailable, **WC-2022 synced (64/64/64)**._

> **Owner rulings carried here:** 2026 fixtures unavailable; **WC-2022 usable for backtest/recap/
> calibration only**; **do NOT market `hit_rate` (42.2%)** as real predictive accuracy; **do NOT treat
> 2022 as live/current**; need a clear **data-layer + product-layer distinction: current preview vs
> historical recap.** This document is a **plan** — no code, no DB/API change.

## 0. The problem (grounded in code)
`GET /matches` now returns **historical finished WC-2022 matches (id 4–67)** alongside the **seed
scheduled previews (id 1–3)**. `HomePage` builds its surfaces from the **whole list**:
`pickTopSignal(matches)`, `topUpsets(matches, 3)`, `matches.filter(...)`. So a **finished 2022 match
could surface as "today's top signal" / "today's matches" / upset** — misleading users into thinking a
2022 result is a current fixture. This must be separated **before** any operator screenshot/trial.

## 1. Q1 — How to avoid the Home page being polluted by 2022 historical finished data?
**Filter the operational surfaces to non-historical matches.** The API already returns `status` and
`kickoff_time` per match (`MatchListItem`), so the Home "today signal / today matches / upsets" should
include **only** `scheduled`/upcoming matches (or `kickoff_time` in the future), and **exclude
`finished`**. Historical finished matches are routed to a separate Recap surface (Q3). No data is
deleted; it is just **filtered by layer**.

## 2. Q2 — Need a frontend filter by status/date?
**Yes — frontend filter, small + safe.** Current state: `frontend/src/api/transform.ts` keeps
`kickoffTime` but **drops `status`**, and the `Match` type has no `status` field. Minimal change
(frontend only): (a) carry `status` through `transform.ts` into the `Match` type; (b) on Home, filter
`matches` to `status !== 'finished'` (and/or `kickoffTime >= now`) for signal/today/upsets. Fallback if
we prefer **zero type change**: filter purely by `kickoffTime > Date.now()` (already available) — but
carrying `status` is cleaner and future-proof. Either way: **no API change** (server already exposes both).

## 3. Q3 — Need a new Historical Recap tab/page?
**Recommended: a dedicated Recap surface**, so historical lives in its own clearly-labelled context.
Options (Implementation, on approval):
- **Option A (lightest):** a **Recap section** on an existing page (e.g. a "Phục dựng / Recap" block)
  that lists `status === 'finished'` matches → reuses the existing Report/recap rendering. No new route.
- **Option B:** a **new route** `/recap?lang=vi` (Historical Recap tab) listing finished matches with a
  clear "Historical · model calibration" banner. Slightly more UI, clearest separation.
**Either is frontend-only**, reusing existing components. Start with **Option A** (lowest risk), promote
to B if operators want a standalone tab.

## 4. Q4 — Can this be done by frontend filter without changing the API?
**Yes.** The API already returns `status` + `kickoff_time`; no new endpoint, no response-shape change, no
DB change is required. The whole separation (Home filter + Recap surface + labels) is **frontend copy /
mapping / filter / layout only**. (If later we want server-side filtering for efficiency, that would be a
new optional query param — **Owner-gated**, not needed now.)

## 5. Q5 — How to express "historical recap / model calibration" on vi pages without misleading users?
- **Explicit historical label** on every recap surface (vi):
  `Phục dựng lịch sử · World Cup 2022` and a sub-line `Dùng để hiệu chỉnh mô hình — không phải trận hiện tại.`
- **Never present `hit_rate` as accuracy.** If any backtest number is shown at all, frame it as a
  **technical calibration metric**, e.g. `Kết quả đối chiếu kỹ thuật trên dữ liệu lịch sử (không phải tỷ
  lệ trúng được cam kết).` Default: **do not surface the number** to customers.
- **Current vs historical never mixed in one list.** Home = "current preview" (scheduled only);
  Recap = "historical model calibration" (finished only), each with its own banner.
- **Compliance unchanged:** no betting/profit/guaranteed-hit; mm fallback English; vi no Chinese.

## 6. Candidate historical samples (WC-2022, for recap/calibration)
| id | match | why |
|----|-------|-----|
| **8** | Argentina vs Saudi Arabia | famous upset → great "model miss vs reality" recap |
| **13** | Germany vs Japan | upset → risk-watch / contrarian storytelling |
| **58** | Morocco vs Spain | knockout drama → narrative + calibration |
| **67** | Argentina vs France | the final → flagship recap |
> These are **historical** examples for recap/calibration storytelling — **not** current matches and
> **not** a hit-rate advertisement. Confirm each `match_id`/teams against the synced `/matches` before use.

## 7. Data-layer vs product-layer distinction (summary)
| Layer | Current preview | Historical recap |
|-------|-----------------|------------------|
| Data | seed scheduled (id 1–3); real 2026 fixtures **when available** | WC-2022 finished (id 4–67), settled |
| Status filter | `scheduled` / upcoming | `finished` |
| Product surface | Home signal / today / upsets · Detail · Report (pre-match) | Recap section/tab · Report (recap framing) |
| vi label | live/preview Scout | `Phục dựng lịch sử · WC2022 · hiệu chỉnh mô hình` |
| hit_rate | n/a | **internal calibration only — not marketed** |

## 8. Recommendation / next step
- **This round: docs only** (no code). Separation **plan approved → Implementation** would be a small
  frontend change: carry `status` in transform → filter Home to non-finished → add a labelled Recap
  surface (Option A) → vi historical labels. **No backend/API/DB change.**
- Until implemented, **do not run operator screenshots on the polluted Home**, and **do not market
  2022 numbers**. Await Owner go for the frontend separation.
