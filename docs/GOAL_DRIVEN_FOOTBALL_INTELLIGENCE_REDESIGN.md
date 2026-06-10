# Goal-Driven Football Intelligence Redesign (Data-First)

> **Owner input:** the product framework stands, but the **content has no detailed-data backing**. Real football
> intelligence must reach player / coach / lineup / injury / tactics / xG / live-events / team-style / H2H levels.
> Without that data, AI copy is hollow — no operational value, no user trust.
> **Mandate:** stop packaging AI copy; stop generic "why the AI decided"; **redesign around real data sources and
> real analysis dimensions first.**
>
> **Owner:** ClaudeT · **Date:** 2026-06-10 · **Branch:** `feature/real-data-zh-vi-verification` (PR #2, Draft) · **Mode:** docs-first (no code).
> **Companions:** [FOOTBALL_INTELLIGENCE_DATA_REQUIREMENTS_MATRIX](FOOTBALL_INTELLIGENCE_DATA_REQUIREMENTS_MATRIX.md) ·
> [GOAL_DRIVEN_DATA_SOURCE_STRATEGY](GOAL_DRIVEN_DATA_SOURCE_STRATEGY.md) ·
> [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md) ·
> [REAL_INTELLIGENCE_SOURCE_MATRIX](REAL_INTELLIGENCE_SOURCE_MATRIX.md)
> **Guardrail:** reference sites below are **structure/field references only — NEVER scraped.** Any API / paid
> source / DB / backend work is **Owner-gated**. Odds/market **excluded** (no betting). `42.2%` stays internal.

---

## Competitive Data Benchmark from Owner

Broken down by **data capability**, not page styling. All are **reference-only** (no scraping); licensed/commercial
feeds are the actual integration path.

### 1. WhoScored — mass-market free analysis
- **Capabilities:** full squad list · live injuries · predicted lineup · team Strengths/Weaknesses/Styles · tactical
  tags (counter-attack, weak at long balls, prefers the middle) · tactic-based match lean.
- **Implication for us:** AI must not write generic conclusions — it must key off **tactical tags + player
  availability**. Report needs a **Team Style / Tactical Matchup** module. **Without tactical tags, no "tactical
  counter" copy.**
- **Source candidates:** TheSports / API-FOOTBALL / Sportmonks / Sportradar. WhoScored = reference only.

### 2. SofaScore / FotMob — top live + deep match analysis
- **Capabilities:** coach historical win-rate · usual formation · player technical stats · Attack Momentum ·
  heatmaps · live events · subs/cards/shots/possession dynamics.
- **Implication for us:** **live intelligence requires real-time events + dynamic stats.** Explaining a "second-half
  formation change" or "momentum shift" needs formation + subs + momentum data. **Without live events, no live-correction push.**
- **Source candidates:** TheSports · API-FOOTBALL · SofaScore commercial API (if available) · Sportradar.

### 3. Understat — xG / quantitative
- **Capabilities:** xG · xGA · shot quality · shot location · real conversion · spotting flat-track-bully / unlucky teams.
- **Implication for us:** score alone is insufficient. Won-but-low-xG → AI should flag "result may be
  unsustainable"; lost-but-high-xG → "performance wasn't bad, scoreline misleads."
- **Source candidates:** Understat reference-only · StatsBomb / FBref / Opta / Sportradar for licensed/safe advanced
  stats. No unapproved scraping.

### 4. Total Football Analysis — human deep tactics
- **Capabilities:** scouting reports · tactical analysis · build-up strategy · counter-pressing · formation
  matchups · pre-knockout tactical white-papers.
- **Implication for us:** high-value content is **tactical explanation**, not just tables. AI may summarize tactics —
  **only on real tactical data or human input.** Without coach/formation/style/key-role data, **no deep tactical analysis.**
- **Source candidates:** human operator input · The Analyst / Opta / Sportradar · internal scout notes. TFA = reference only (no copying).

### 5. The Analyst / Opta — official data lab
- **Capabilities:** passing networks · official quantitative analysis · prediction models · manager-evolution
  studies · large structured football database.
- **Implication for us:** true high-end intelligence = **structured data + models**, not copy. Long-term **enterprise
  route** (Opta / Sportradar / Stats Perform).
- **Source candidates:** Opta commercial · Sportradar · Stats Perform enterprise vendors.

### 6. Transfermarkt — people & fundamentals archive
- **Capabilities:** full squad · injury history · contract expiry · card suspensions · coach career · coach H2H ·
  player market value · squad depth.
- **Implication for us:** pre-match analysis must know **who can/can't play**; coach H2H + squad completeness are
  variables bettors-game users care about. **Without injuries/suspensions, no "squad intact / key absence" copy.**
- **Source candidates:** Transfermarkt commercial license (if available) · TheSports / API-FOOTBALL / Sportmonks /
  Sportradar. Transfermarkt = field reference only (no scraping).

### 7. FBref — advanced modeling data
- **Capabilities:** StatsBomb-grade advanced stats · pressures/90 · progressive passing distance · defensive-third
  duel win % · GK advanced save % · exportable tables.
- **Implication for us:** a real win-probability model needs **advanced quantitative fields**; AI must explain *why*
  a team is truly strong/weak (not just past scores). **Reserve an `advanced_stats` slot** in the model schema.
- **Source candidates:** FBref reference / manual sample · StatsBomb / Opta / Sportradar licensed. No mass scraping.

---

## Product Principle: Data First, AI Second

1. **AI is not a data source.**
2. **AI must not fill missing data with generic language.**
3. AI's job: **read data → identify variables → explain conflicts → generate a scout report.**
4. Any dimension without data must show **`missing` / `source required`**.
5. Without player / coach / lineup / injury / xG / live-events, **do not claim deep analysis.**
6. The current product can only prove **historical result alignment** — **not** full intelligence.
7. **Operational value rests on concrete detail, not fluent copy.**

---

## Minimum Credible Intelligence Standard

### Level 0 — Not credible
Only fixtures, win-prob, recommended score, risk, AI copy. **Most of the current product is still here.** Not fit
for external operation.

### Level 1 — Historical Recap Credible
Needs: `final_score` · `actual_winner` · AI baseline · model correct/wrong · upset/favorite_failed · basic H2H · recent form.
- **DONE now:** `final_score`/`actual_winner` for **match 8 & 13** (real, from Kaggle alignment) · AI baseline · model-wrong / upset tag (see
  [real_data_perception_mvp screenshots](qa_screenshots/real_data_perception_mvp/)).
- **NOT done:** H2H · recent_form · full-64 UI use · license/attribution confirmation.

### Level 2 — Pre-match Scout Credible
Needs: starting/predicted lineup · coach · formation · injuries/suspensions · key players · tactical style · recent
form · H2H · player availability.
- **NOT reached.** Must be validated via **TheSports / API-FOOTBALL / Sportmonks / Sportradar.**

### Level 3 — Live Intelligence Credible
Needs: live events · subs · cards · shots · xG · attack momentum · heatmap · live player ratings.
- **Not reached at all.** Requires a **paid real-time API.**

---

## Modules to downgrade / hide until Level 2/3 data exists

(Design recommendation — **implementation is Owner-gated; not changed this docs-only round.**)

| Module (current) | Page | Why downgrade | Target state |
|---|---|---|---|
| AI 战术底牌 / AI tactical insight | Detail PREMIUM | no tactical data behind it | hide or "source required" |
| 完整模型解释 / full model explanation | Detail/Report | no advanced stats / features | downgrade to baseline-only |
| 精准推荐比分 / precise recommended score | Detail/Report | a guess, not modeled | show "—" / remove on no-data |
| 临场修正推送 / live correction push | Detail LINEUP WATCH | no live events | hide until Level 3 |
| 为什么 AI 这么判断 / "why the AI decided" | Detail WHY | generic, no factor data | replace with data-status |
| 单纯风险文案 / pure risk copy | Detail/Report | not evidence-backed | tie to real factors or label generic |

**Unified fallback copy when Level 2/3 data is missing:**
- **zh:** 当前仅有基础模型判断和历史赛果，缺少首发、伤停、教练、球员状态、xG 与实时事件，不能生成完整战术解释。
- **vi:** Hiện chỉ có nhận định mô hình cơ sở và kết quả lịch sử; còn thiếu đội hình xuất phát, chấn thương, HLV, phong độ cầu thủ, xG và sự kiện trực tiếp — chưa thể tạo phân tích chiến thuật đầy đủ.

---

## Product Build Route — Owner recommendation

**Option A — Continue MVP-1 Historical Scout Recap.** Kaggle `final_score`/`actual_winner` + H2H/recent_form + 4
premium recaps; no pre-match prediction promise. *Value:* can trial operational content. *Con:* limited appeal.

**Option B — Jump to MVP-2 Pre-match Scout Pack.** Apply TheSports trial; buy/trial API-FOOTBALL / Sportmonks;
validate lineups/injuries/coach/formation/player. *Value:* real operational value. *Con:* cost + API verification.

**Option C — MVP-1 + MVP-2 in parallel (RECOMMENDED if budget allows).** Keep Kaggle historical recaps while
applying the TheSports trial and filling the **same page structure** with real Level-2 fields.
- **If budget allows → Option C.** If budget-limited → MVP-1 first, **but do not run external operation** until ≥ Level 2.

---

## TheSports 15-day Trial — Verification Checklist

Owner is preparing the TheSports 15-day trial. Operator must verify (yes/no + sample where possible):

1. FIFA World Cup 2022 historical match coverage
2. WC2022 lineups
3. WC2022 match events
4. WC2022 player stats
5. National-team coach data
6. Squad / player list
7. Injuries / suspensions
8. Predicted or confirmed lineup
9. Match timeline
10. Player ratings
11. Formations
12. H2H
13. Recent form
14. World Cup 2026 fixtures
15. Commercial-use permission
16. Rate limit
17. Pricing after trial
18. **Sample payload — match 8 Argentina vs Saudi Arabia (2022-11-22)**
19. **Sample payload — match 13 Germany vs Japan (2022-11-23)**

→ Record results in a new `docs/THESPORTS_TRIAL_VERIFICATION.md` when the trial runs (operator).

---

## Owner Decision Table

| Decision | Options | Recommended | Reason | Blocking risk | Owner action needed |
|---|---|---|---|---|---|
| Continue PR #2 | continue Draft / merge / close | **Continue (Draft)** | redesign in progress; not release-ready | none | keep Draft |
| External operation | run now / **pause** | **Pause until ≥ Level 2** | Level 0/1 not credible pre-match | trust/reputation | confirm pause |
| TheSports trial | yes / no | **Yes (15-day)** | cheapest Level-2 validation | needs operator signup | apply + run 19-pt checklist |
| API-FOOTBALL coverage check | yes / no | **Yes** | existing connector; paid unlocks Level 2 | needs paid plan + token on Render | verify WC2022 season + WC2026 + lineups |
| Introduce Sportmonks | yes / no / later | **Evaluate in parallel** | comparison for Level 2/3 (€29+/mo) | cost | optional free-plan test + trial |
| Odds / market | include / **exclude** | **Exclude** | compliance floor (no betting) | compliance | confirm exclusion |
| SerpApi | keep / drop | **Auxiliary only** | scraper; no lineups; final-score cross-check | none | keep optional or drop |
| Expand Kaggle recap | yes / no | **Yes (internal)** | free; fills result/H2H/form | CC0 license confirm for UI | confirm license for customer use |
| Frontend polish | continue / **hold** | **Hold deep polish** | avoid polishing Level-0 surfaces | wasted effort | focus on data first |

---

## Guardrails honored
docs-first · no frontend/backend/API/DB change · reference sites not scraped · odds excluded · `42.2%` internal ·
StatsBomb open data = non-commercial (offline calibration only) · PR #2 stays Draft.

## Sources (checked 2026-06-10)
Sportmonks [pricing](https://www.sportmonks.com/football-api/plans-pricing/) · StatsBomb [open-data](https://github.com/statsbomb/open-data)
(+ prior-sprint sources in [EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION](EXTERNAL_SPORTS_DATA_SOURCE_EVALUATION.md)).
