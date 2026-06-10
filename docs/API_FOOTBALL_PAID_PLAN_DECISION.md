# API-FOOTBALL — Paid-Plan Decision

> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-only.
> Decision brief for upgrading API-FOOTBALL from FREE to a paid plan. Pricing is **"as reported / verify before
> purchase"** — not a long-term commitment. Companions: [API_FOOTBALL_COVERAGE_CHECK](API_FOOTBALL_COVERAGE_CHECK.md) ·
> [MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE](MVP2_PREMATCH_SCOUT_PACK_ARCHITECTURE.md).

---

## 1. Why upgrade
The Day-2 real run proved API-FOOTBALL serves the **Level-2 pre-match scout core** for WC2022 (lineups/formation/
events/statistics/players/squad/coach/teams), with fixture ids aligned to our Render data (8→855737 = AF-855737).
**This is the cheapest, lowest-engineering path to credible pre-match intelligence.** But the FREE plan **cannot
operate**: WC2026 is locked and rate limits are too tight. A paid plan is the gate to a real MVP-2.

## 2. What the FREE plan already verified (PASS WITH CAVEATS)
✅ league_id=1 · ✅ WC2022 fixtures=64 · ✅ lineups (+formation) · ✅ events · ✅ statistics · ✅ fixture players ·
✅ squad · ✅ coach · ✅ teams · ✅ fixture-id alignment for matches 8/13/58/67.

## 3. FREE-plan limits (why it can't operate)
- 🔒 **WC2026 season locked** — "Free plans do not have access to this season, try from 2022 to 2024."
- ⏱️ **Rate limit ~10/min, 100/day** — hit HTTP 429; a single fixture's full pack is ~6–8 calls, so a handful of
  fixtures exhausts the daily budget.
- ⚠️ **injuries empty** for the WC2022 historical query (unconfirmed for current/live).
- ❓ **commercial-use terms** on FREE are not suitable for a paid product.

## 4. What a paid plan MUST re-verify (gate)
Re-run `scripts/verify_api_football_level2.py` on the paid key and confirm:
1. **WC2026 fixtures** return (or are confirmed not-yet-published).
2. **injuries** non-empty on a current/upcoming fixture.
3. **current-season** endpoints return data.
4. **rate limit** (req/min + req/day) sufficient for a World-Cup match-day load (with caching).
5. **commercial usage** permitted by the plan terms.
6. **Render env** key set server-side (gitignored; never in frontend).
7. **production request budget** — fixtures × endpoints × refresh ≤ plan/day with Redis cache.

## 5. Pricing (as reported 2026-06-10 — verify before purchase)
| plan | price/mo *(reported)* | req/day *(reported)* | note |
|---|---|---|---|
| Free | $0 | 100/day, ~10/min | current; WC2026 locked |
| **Pro** | **$19** *(verify)* | 7,500/day | **recommended low-tier for the gate re-verify** |
| Ultra | $29 *(verify)* | 75,000/day | higher live volume |
| Mega | $39 *(verify)* | 150,000/day | match-day scale |

→ **Recommend starting at Pro ($19, verify)** purely to clear the §4 gate; scale up only if the production budget
math (architecture §6) requires it.

## 6. Decision branches
- **Paid gate = PASS** → API-FOOTBALL becomes the **MVP-2 primary source** → open the implementation PR (backend
  schema + ingestion + Evidence Board v2). External operation still gated on a minimal Level-2 surface + license.
- **Paid gate = PARTIAL** (e.g. injuries weak, WC2026 sparse) → keep API-FOOTBALL as the base, **supplement** the
  gaps with a **TheSports trial / Sportmonks / Highlightly** comparison (per source matrix).
- **Paid gate = FAIL** (unlikely given FREE already passed core) → re-evaluate TheSports/Sportmonks as primary.

## 7. Owner budget decision items
- [ ] Approve **API-FOOTBALL paid plan** (Pro $19/mo tier, verify price) — **ClaudeT recommendation: GO** (lowest
  cost/risk; core already proven; TheSports failing should not block).
- [ ] Confirm this is **verification spend, not go-live** — paid plan → **Paid-Plan Verification**, then MVP-2.
- [ ] Confirm **operation stays paused** until the gate passes + schema/cache/ledger built + frontend downgrade.
- [ ] Confirm **odds excluded**; Kaggle CC0 + StatsBomb non-commercial license confirmations still pending.

## Guardrails honored
docs-only · pricing flagged verify-before-purchase · no token/payload committed · odds excluded · operation paused · PR #2 Draft.
