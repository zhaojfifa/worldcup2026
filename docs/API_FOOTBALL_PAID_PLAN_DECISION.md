# API-FOOTBALL — Paid-Plan / Plan-Verification Decision

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only.
> Pricing is **"as reported / verify before purchase"** — not a long-term commitment. Companions:
> [API_FOOTBALL_COVERAGE_CHECK](API_FOOTBALL_COVERAGE_CHECK.md) · [MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE](MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE.md).
> **Updated:** the latest real run returns **WC2026 fixtures = 72**, so "unlock WC2026" is **no longer** a reason to upgrade.

---

## 1. What the real run already verified (PASS)
✅ league_id=1 · ✅ WC2022 fixtures=64 · ✅ **WC2026 fixtures=72** · ✅ lineups (+formation) · ✅ events · ✅
statistics · ✅ fixture players · ✅ squad · ✅ coach · ✅ teams (32) · ✅ fixture-id alignment (8/13/58/67).
→ **API-FOOTBALL is the confirmed MVP-2 primary-source candidate.** Coverage is **not** the blocker.

## 2. The one open data gap
⚠️ **injuries = 0** (HTTP 200, empty) on the WC2022 historical query — **unresolved** (historical not populated, or
needs current-season/fixture-level form). Must be re-verified on a current/upcoming fixture or covered by a second
source — this is a **data-resolution** task, not necessarily a plan-tier issue.

## 3. Why a paid plan may still be needed — REVISED rationale
WC2026 access is no longer a reason. A paid plan / plan-verification is now about **production readiness**, not coverage:
1. **Rate limit / production request budget** — a full fixture pack ≈ 6–8 calls; World-Cup match-day load across many
   fixtures must fit the plan's req/min + req/day (with Redis cache).
2. **Commercial use** — confirm the plan's terms permit a paid product.
3. **injuries / suspensions** — re-verify on current-season / supported competitions (or add a second source).
4. **Production stability** — uptime / consistency under load.
5. **2026 fixtures update SLA** — how fast WC2026 fixtures/lineups refresh as the tournament approaches.
6. **Live / event latency** (only if Level-3 live is pursued) — push/websocket or poll cadence.

## 4. Pricing (as reported 2026-06-10 — verify before purchase)
| plan | price/mo *(reported)* | req/day *(reported)* | note |
|---|---|---|---|
| Free | $0 | 100/day, ~10/min | core + (now) WC2026 verified; tight limits |
| **Pro** | **$19** *(verify)* | 7,500/day | likely sufficient for MVP-2 + injuries re-verify |
| Ultra | $29 *(verify)* | 75,000/day | higher live volume |
| Mega | $39 *(verify)* | 150,000/day | match-day scale |

→ **Recommend Pro ($19, verify)** for the production-budget + commercial-use + injuries re-verify, scaling only if
the budget math (architecture §6) requires it.

## 5. Decision branches
- **Plan re-verify = PASS** (rate limit + commercial + injuries OK) → API-FOOTBALL is the **MVP-2 primary source** →
  proceed with the implementation PR. Operation still gated on a minimal Level-2 surface + license.
- **PARTIAL** (e.g. injuries still weak) → keep API-FOOTBALL as the base; **supplement** injuries/lineups via a
  **TheSports trial / Sportmonks / Highlightly** comparison.
- **FAIL** (unlikely — coverage already PASS) → re-evaluate alternatives as primary.

## 6. Owner decision items
- [ ] Approve **API-FOOTBALL plan-verification spend** (Pro $19/mo tier, verify price) — **ClaudeT recommendation:
  GO**, but now for **rate-limit / commercial-use / injuries / stability**, not WC2026 access.
- [ ] Confirm this is **verification spend, not go-live** — re-verify → then MVP-2 implementation.
- [ ] Confirm **operation stays paused** until the gate passes + schema/cache/ledger built + frontend downgrade.
- [ ] Confirm **odds excluded**; Kaggle CC0 + StatsBomb non-commercial license confirmations still pending.
- [ ] Decide whether to start a **second-source injuries** trial (TheSports/Sportmonks/Highlightly) in parallel.

## Guardrails honored
docs-only · pricing flagged verify-before-purchase · no token/payload committed · odds excluded · operation paused · PR #2 Draft.
