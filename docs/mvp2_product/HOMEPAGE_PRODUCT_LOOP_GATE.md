# MVP2-P2 — Homepage Product Loop Reconstruction · Gate Doc

> Harness-X product/operability sprint (Owner brief 2026-06-14). Phases A (Architect Memo),
> B (Product Planner Plan), D (Operator Review Checklist), E (frozen Gate Spec) in one doc.
> Phase C preview: `HOMEPAGE_PRODUCT_LOOP_PREVIEW.md`. Phase F implemented (commit, NOT deployed).
> **Deploy is gated on Owner acceptance of this gate + preview. Send remains HOLD.**

---

## Phase A — Architect Decision Memo

**Classification:** Product / Operability Flow · **L2 primary-path impact** (the homepage is the
product's first screen and trust engine).

**Problem.** The homepage drifted into a status/recap/fixture list with a generic CTA. It no longer
tells the football-intelligence story: *predict the hotspot → track it → recap it → move to the next
hotspot → convert to group*. Concretely, the auto-selected hero (`pickActiveFixture`) and the recap
desk surfaced whichever fixture was `recap_ready`, so a finished non-hotspot (Mexico) could lead while
the tracked hotspot (Brazil) was demoted, and today's main prediction (Netherlands) was buried in a
generic "upcoming" list.

**Scope (in).** Homepage active-loop section reconstruction: explicit zones for yesterday's hotspot
recap, today's hotspot prediction, secondary schedule, other recaps, and a value-tied group CTA. An
editorial selection helper driven by the operator's slate order. zh/vi/my copy. A homepage product-loop
guard. Docs.

**Non-goals (out).** Backend schema change · auto-recap / content generation · external LLM API call ·
auto-send · betting/trading vocabulary · MTC economics or growth-attribution changes · referral/reward
mechanics · broad redesign beyond the two-line product (brand hero, demo fold, WC2022 archive untouched).

**Risks.**
- *Editorial mis-selection* → mitigated: selection is the operator's slate ORDER, not a hardcoded
  popularity ranking; the P1.5c editorial agent + operator confirm the order.
- *Fake recap* → mitigated: 查看复盘 only when `recapReady=true`; Brazil (RECAP_PENDING) shows
  赛后校准中 and NO recap link.
- *Internal-state leakage* → mitigated: no 生成中/待生成/自动生成; guarded by scanner.
- *Deploy regression on live* → mitigated: deploy gated on Owner acceptance; build + guards green first.

**Acceptance criteria.** (1) Homepage renders zones in order: 昨日热点复盘 → 今日热点预测 → 今日赛程 →
其他复盘 → group CTA. (2) Brazil 1-1 = lead recap, 赛后校准中, no 查看复盘. (3) Netherlands = first-screen
prediction block, not buried. (4) Mexico = secondary 其他复盘 with 查看复盘 (recap_ready). (5) zh/vi/my
consistent, no Chinese fallback. (6) build + all guards PASS. (7) no fake recap / generation wording /
betting vocab / auto-send.

**Release gates.** build PASS · `check_growth_copy.py` PASS · `check_homepage_product_loop.py` PASS ·
`check_runtime_daily_fixtures.py --base-url` PASS · Owner accepts gate+preview → operator deploys →
live visual PASS + `check_customer_visible_copy.py` 21/21 → (separately) Owner per-channel GO before any send.

---

## Phase B — Product Planner Workflow Plan (zones)

| # | Zone | Source data | Display condition | Customer copy (zh) | CTA | Forbidden |
|---|---|---|---|---|---|---|
| 1 | Brand / value prop | static | always | 俅哥说球 · 世界杯赛前判断 · 临场 30 分钟修正 | — | — |
| 2 | 昨日热点复盘 | manifest: first FINISHED fixture | a finished fixture exists | 昨日热点复盘 / 比赛已结束 · 赛后校准中 / 这是昨日主推的热点比赛，赛后观察已开启 | recapReady→查看复盘 + 加入情报群看赛后观察; else 加入情报群看赛后观察 only | 复盘生成中·待生成·查看复盘 when !recapReady (fake recap) |
| 3 | 今日热点预测 | manifest: first SCHEDULED fixture | a scheduled fixture exists | 今日热点预测 / 今日主推 · 开球前判断 / 今日主推比赛：开球前看方向，开球前 30 分钟修正 | renderable→进入今日判断 + 加入临场情报群; else 加入临场情报群 | burying in 即将开赛 only |
| 4 | 今日赛程 (secondary) | manifest: remaining SCHEDULED | ≥1 remaining | 今日赛程 / rows + 即将开赛 chip | none (lightweight) | promoting above zones 2/3 |
| 5 | 其他复盘 (secondary) | manifest: remaining FINISHED | ≥1 remaining | 其他复盘 / row + 查看复盘 if recapReady else 已完赛 | recapReady→查看复盘 | labeling as 今日热点复盘; placing above Brazil |
| 6 | Growth CTA | static | always | 想看临场 30 分钟修正和赛后观察，进群。 | 加入情报群 | money/reward/referral/betting |
| 7 | MTC / ambassador | existing token/community pages (unchanged) | n/a | (in demo fold / token page) | — | changing MTC economics |

vi/my mirror every zone (see `HomeProductLoop.tsx` L map). vi/my never fall back to Chinese.

---

## Phase E — Gate Spec (FROZEN, per Owner brief §1 Phase E)

Homepage required structure (top→bottom):

1. **Hotspot Recap** — title `昨日热点复盘`; fixture **Brazil 1-1 Morocco**; state `比赛已结束 · 赛后校准中`;
   explanation = previous featured match, post-match observation open, **no fake recap**; CTA
   `加入情报群看赛后观察`; **no 查看复盘 unless recapReady=true**.
2. **Today Hotspot Prediction** — title `今日热点预测`; fixture **Netherlands vs Japan**; state
   `今日主推 · 开球前判断`; explanation = today's main match, direction before kickoff, 30-min correction;
   CTA `进入今日判断` / `加入临场情报群`; lightweight tracking card when no full narrative (not a buried list item).
3. **Secondary schedule** — Germany vs Curaçao · Ivory Coast vs Ecuador · Sweden vs Tunisia · Australia vs Turkey.
4. **Other recap** — Mexico 2-0 South Africa; label `其他复盘` (NOT `今日热点复盘`, NOT above Brazil).
5. **Growth conversion** — CTA tied to the two stories: "想看临场 30 分钟修正和赛后观察，进群。"; no money/reward/betting/commission.

**Forbidden:** fake recap · 自动生成 · 生成中 · 复盘生成中 · 待生成复盘 · odds/betting/handicap ·
user-visible AI/model/process language · burying today's hotspot in 即将开赛 only · making Mexico the
lead recap while Brazil is the tracked hotspot.

**Editorial selection rule (no hardcoded ranking).** The operator expresses the daily editorial decision
through **slate ORDER** in `manual_scores_<date>.md` → registry → manifest. `selectProductLoop()` takes
the **first FINISHED** fixture as the yesterday-hotspot recap lead and the **first SCHEDULED** fixture as
today's hotspot prediction; the rest are secondary. The frontend renders the confirmed order; it never
ranks teams by popularity. (LLM/operator decide the hotspot via the P1.5c editorial agent.)

---

## Phase D — Operator / User Review Checklist (return for Owner review — do NOT self-approve)

Review the live homepage (after deploy) or the preview doc, zh + vi + my:

- [ ] A non-engineer immediately understands **yesterday's** prediction result (Brazil 1-1, tracked hotspot).
- [ ] A first-time user immediately identifies **today's** main match (Netherlands vs Japan).
- [ ] The closed loop is clear: predict → track → recap → next prediction.
- [ ] Secondary recaps (Mexico) and schedule (Germany/…) are visually **downgraded** (below, lighter).
- [ ] The CTA explains **why** to join (临场 30 分钟修正 + 赛后观察), not generic "join".
- [ ] **No** internal process words (生成中 / 待生成 / 自动生成 / 模型 / pipeline) anywhere customer-visible.
- [ ] **No** betting/trading language.
- [ ] zh / vi / my are understandable without any Chinese fallback in vi/my.
- [ ] Brazil shows **赛后校准中**, NOT a fake recap, NO 查看复盘.
- [ ] Mexico is labeled **其他复盘**, NOT 今日热点复盘, and is **below** Brazil.

Expected screenshots/text: see `HOMEPAGE_PRODUCT_LOOP_PREVIEW.md` (per-locale mock of the rendered order).

**Owner decision required:** accept this gate + preview → authorize operator deploy of the implemented
build; or request changes. No deploy and no send until Owner accepts.
