# Product / Operation / Modeling Alignment Brainstorm (Draft)

> **Status:** design draft for human + designer review. **Not** an implementation
> spec, **not** a code task. Decisions here are proposals; engineering scope is
> confirmed only after review.
>
> **Grounded against:** MVP v0.4 (real code state this repo is actually in),
> `CLAUDE.md`, `docs/MVP_STATUS.md`, `docs/DAY4_DATA_AUTOMATION.md`, and the two
> uploaded operator docs (`AI世界杯预测程序设想.docx`, `AI足球预测运营框架.docx`).
>
> **Input note:** the older design `.md` files referenced in the brief
> (网站前端核心页面设计与功能.md, 2026 美加墨…设计方案.md, …数据分析与预测指南.md, …智慧体育引擎.md)
> are **not present** in either repo path. This draft is written without them;
> if they exist elsewhere they should be folded in at review time.

---

## 0. TL;DR — the core judgment

MVP v0.4 is a **working tool**, not yet a **product people return to**. The
engine (fixtures → baseline prediction → API → mobile UI) is wired and live, and
the UI sprint already gave it a sports-app skin. But three operator-critical
layers are missing, and all three are about **behaviour**, not visuals:

1. **Decision guidance** — the app shows probabilities; it does not yet say, in
   one glance, *"AI leans X, here's the confidence, here's the catch."*
2. **Emotional hooks** — no "今日最强信号" C-position, no upset board, no
   track-record, no social proof. SEA users are trend- and atmosphere-driven;
   a flat list does not trigger them.
3. **Return reason** — nothing changes day-to-day that pulls a user back: no
   daily record, no streak challenge, no ranking, no "what did AI get right
   yesterday."

**Good news:** ~70% of what the operator docs ask for can be built **on top of
existing Match / Prediction / Report data** as a derived "operations output
layer" + **aggregate read APIs**, *without* changing existing API shapes,
without new ML, and without touching the prediction core. The genuinely new
data (track record, community heat, rankings) is a small, well-bounded set of
additions that can start as mock and harden later.

**Recommended next scope:** do **Phase A (front-end re-layout on derived/mock
data)** first because it is the highest leverage and lowest risk, then **Phase
B (aggregate APIs)**, then **Phase C (ops output layer + LLM + share)**. Details
in §9.

---

## 1. Current product gaps (SEA user + operator lens)

| # | Gap | Verdict | Evidence in current build |
|---|-----|---------|---------------------------|
| 1 | **Decision guidance** | **Missing** | Home/Detail show win-prob bars + risk note, but never a single human verdict line ("AI 倾向：阿根廷不败"). User must interpret numbers themselves. |
| 2 | **Emotional stimulation** | **Mostly missing** | Ticker + hero exist, but there's no "今日最强信号" C-pick, no upset board, no streak/social proof. Atmosphere is cosmetic, not behavioural. |
| 3 | **Return reason** | **Missing** | No track-record, no daily settlement, no streak, no ranking. After one match, there is no reason to come back tomorrow. |
| 4 | **Home too flat** | **True** | Current home = ticker + hero + capability bar + date scroll + uniform match cards. Every match has equal weight → no focal point, no hierarchy of "what matters today." |
| 5 | **Detail prioritisation** | **Partially right** | Detail already puts win-prob and LINEUP WATCH high, but the **AI verdict / confidence / recommended score** is split across the page rather than a single top "结论卡". The most-wanted info isn't the first thing seen. |
| 6 | **Ops loop (Token / record / ranking / upset / community)** | **Not closed** | Token center exists (check-in, missions, shop, challenge) but is **isolated** — it doesn't connect to predictions, streaks, or social proof. No ranking, no upset board, no community heat. The loop that drives daily return + sharing isn't formed. |

**One-line diagnosis:** the app answers *"what are the probabilities?"* It does
not yet answer *"what does AI think, why should I care, and why come back
tomorrow?"* — which is exactly what the operator docs are asking for.

---

## 2. Positioning upgrade — tool → community

**Recommendation: YES — reposition from "AI 足球预测工具" to
"AI 足球情报社区 / AI Football Intelligence Community".** But treat "community"
as a **staged** claim, not a day-1 feature.

**Why:**
- The operator framework explicitly says the goal is a
  *"AI 驱动的足球比赛分析与决策社区"* with retention via daily record, user
  晒单, rankings — that is a **community/content** motion, not a tool motion.
- A tool is used and abandoned per task; a community/feed has daily ritual,
  social proof, and a streak to protect → matches the three missing layers in §1.
- It reframes monetisation honestly: you sell **access to an intelligence
  stream and a fan community**, not "winning picks" — which is also the safer
  compliance posture.

**Wording caution (compliance):** prefer **"情报 / 观点 / 研判 / 风险提示"** over
**"决策"**. "决策社区" leans toward implying we tell people what to bet. Use
**"AI 足球情报社区"** publicly; keep "决策" out of user-facing copy.

**Non-negotiable floor (unchanged, restate in product copy):**
不做博彩 · 不提供现金投注 · 不承诺收益 · 不承诺命中 · MTC 仅平台积分（不可提现/转让/交易）·
一切表达为「数据分析 / AI 观点 / 风险提示 / 球迷娱乐参考」.

**Staging:** Phase A/B can ship the "intelligence" half (signals, upsets,
track-record, feed) honestly today. The "community" half (user opinions,
rankings, 晒单) starts as light social proof (mock/aggregate) and only becomes
real UGC when there's a user base — don't build heavy social infra prematurely.

---

## 3. New home information architecture

**Principle:** one clear focal point, then scannable signals, then the loop
hooks. Replace the current "uniform card list" with a ranked feed.

### Proposed module order

| Order | Module | Purpose | Data source | New API? |
|-------|--------|---------|-------------|----------|
| 1 | **今日 AI 最强信号 (C-pick)** | decision guidance + emotion | derive: pick highest-confidence match | derive now / later `home/summary` |
| 2 | **今日比赛简表** | scannable, low cognitive load | existing `/matches` | none |
| 3 | **今日爆冷预警 TOP3** | curiosity + shareability | derive `upset_score` from prob/tag | derive now / later `upsets/today` |
| 4 | **AI 情报战绩** | trust + return reason | **needs result data** (mock first) | later `performance/daily` |
| 5 | **社区热门选择** | social proof / trend-follow | **needs heat data** (mock first) | later `community/heat` |
| 6 | **Token / 连胜挑战 / 排行榜入口** | retention loop entry | Token exists; ranking mock | later `rankings` |

### Module field specs + copy

**1. 今日 AI 最强信号 (C-position card)**
- Fields: `match (home vs away)`, `ai_pick_label`, `confidence_star`,
  `win_prob {home,draw,away}`, `top_risk` (one line), CTA.
- Copy:
  > 今日 AI 最强信号
  > 阿根廷 vs 法国
  > AI 倾向：**阿根廷不败**　信心：★★★★☆
  > 风险：法国反击强
  > [查看 AI 观点] [解锁完整分析]
- Derivable now: pick `max(confidence)` (or `tag=focus`); `ai_pick_label` and
  `confidence_star` are rules over existing `prob_*` + `confidence` (see §6).

**2. 今日比赛简表**
- Fields per row: `time`, `home/away (flag+name)`, `ai_pick_label`,
  `risk_chip`, `heat` (optional). **No** dense stats.
- Copy: `巴西 vs 日本 → 主胜偏强`,  `英格兰 vs 德国 → 可能爆冷`.
- Source: existing `/matches` — already has everything except `ai_pick_label`
  (derive client-side or via ops layer).

**3. 今日爆冷预警 TOP3**
- Fields: rank, `match`, `upset_score`, one-line hook.
- Copy: `1️⃣ 英格兰可能翻车 ⚠️`,  `2️⃣ 西班牙风险偏高 ⚠️` (avoid "稳/必").
- Derivable now from `risk_level` + prob spread + `tag=upset`.

**4. AI 情报战绩** *(trust engine — but the honest one)*
- Fields: `yesterday_hit/total`, `last7d_rate`, `live_corrected_uplift`.
- Copy: `昨日 3/5 命中 · 近 7 天 68%`
  **mandatory disclaimer:** `历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。`
- **Not derivable yet** — requires storing actual results vs predictions.
  Phase A = mock numbers clearly labelled demo; Phase B+ = real after results
  ingestion.

**5. 社区热门选择**
- Fields: `most_followed_match`, `hot_discussion`, `user_pick_split` (e.g.
  62% lean home).
- **Not derivable yet** — no engagement/UGC data. Phase A = mock/derived
  (e.g. show prob as "AI + 球迷共识" placeholder, clearly labelled). Real later.

**6. Token / 连胜挑战 / 排行榜入口**
- Entry tiles linking to Token center + a new streak/ranking surface.
- Token exists; streak/ranking = mock first.

**Can we build it now on mock/existing data?** Modules 1–3 = **yes, today, from
existing data + rules**. Modules 4–6 = **mock first**, real data in Phase B/C.

---

## 4. Detail page redesign (conversion core)

**Principle:** the AI verdict is the hero. Everything else supports it. Keep the
existing components (WinBar, LINEUP WATCH, FeatureBars) but **re-order and
re-frame**.

### Proposed module order

| Order | Module | Free vs Paid | Notes |
|-------|--------|--------------|-------|
| 1 | **AI 结论卡 (置顶)** | Free: label + star + blurred score · Paid: exact score + risk grade | `ai_pick_label`, `confidence_star`, `recommended_score`, `risk_level` |
| 2 | **胜率图 (主/平/客)** | Free | existing WinBar |
| 3 | **为什么 AI 这么判断** | Free: 1 teaser bullet · Paid: 2–3 full bullets | `reason_bullets` (rules now, LLM later) |
| 4 | **风险提示** | Free | reframed `risk_note` + tags (反击/伤病/首发/裁判/战意) |
| 5 | **LINEUP WATCH (临场30分钟修正)** | Free to see, Paid to get push | keep as-is |
| 6 | **付费解锁** | — | teaser of locked items |

### Free / Paid boundary

- **Free:** AI 倾向 label, confidence stars, win-prob bar, **one** reason teaser,
  basic risk tags, a **blurred/range** score (e.g. "比分倾向 2:x").
- **Paid:** exact `recommended_score`, full `reason_bullets`, `risk_level`
  grade + detailed risk, live-correction push subscription.
- This maps cleanly onto existing `free_note` (free) vs `Report` (paid) split —
  no schema change needed.

### SEA-friendly short copy (card + short sentence)
- `AI 倾向：主队不败`  ·  `信心：★★★★☆`  ·  `风险：客队反击强`
- `首发公布后 AI 会重算，记得回来看`  (return hook)
- `想看完整理由和精确比分？解锁 AI 战术底牌`

### Compliance risk points (detail page)
- Never phrase the pick as a bet/lock: use **倾向 / 偏强 / 不败趋势**, never
  **稳/必中/推荐下注/跟单**.
- "推荐比分" is fine as **AI 推荐比分 (数据推演)**; never attach odds or stake.
- Any "命中/战绩" reference triggers the mandatory disclaimer (§8).

---

## 5. Backend API design (aggregate layer)

**Guiding rule (from CLAUDE.md):** do **not** change existing response shapes.
New surfaces are **new endpoints**; existing `/matches`, `/matches/{id}`,
`/reports/{id}` stay byte-compatible so the frontend keeps working in both
`VITE_USE_MOCK` modes.

| Endpoint | Day 5 must? | Derivable from existing data? | New table? |
|----------|-------------|-------------------------------|------------|
| `GET /api/v1/home/summary` | **Recommended** | Yes — composes top_pick + today_matches + upset_alerts from Match/Prediction; performance/heat as mock fields | No |
| `GET /api/v1/upsets/today` | Optional (or fold into summary) | Yes — `upset_score` over prob/risk | No |
| `GET /api/v1/performance/daily` | **Defer** | No — needs actual results | Yes (result/settlement) |
| `GET /api/v1/community/heat` | **Defer** | No — needs engagement data | Yes (views/follows) |
| `GET /api/v1/rankings` | **Defer** | Partial — ChallengeEntry exists but no streak/settlement | Yes (streak/leaderboard) |

**Judgments:**
1. **Day 5 must:** `GET /api/v1/home/summary` as a single composing read (top
   pick + simple list + upset top3 + performance/heat placeholders). One call =
   one home render; reduces client round-trips; lets us ship the new home
   without 5 endpoints.
2. **Post-Day-5:** dedicated `upsets`, `performance`, `community/heat`,
   `rankings` once their data exists.
3. **Derivable now:** top_pick, today_matches, upset_alerts, ai labels — all
   from `Match`/`Prediction`. No new compute, just composition + rules.
4. **Shape safety:** `home/summary` is additive; it **reuses** existing
   `MatchListItem`-style sub-objects so `transform.ts` can largely reuse mappers.
5. **New tables (Phase C):** `MatchResult` (actual score/outcome → powers
   performance), `MatchEngagement` (views/follows → heat), `UserStreak`/
   leaderboard (rankings). All independent of the prediction core.

**`home/summary` proposed body (additive, mock-friendly):**
```
{
  "top_pick": { match fields + ai_pick_label, confidence_star, top_risk },
  "today_matches": [ MatchListItem... ],     // existing shape
  "upset_alerts": [ { match, upset_score, hook } ],
  "performance": { yesterday_hit, yesterday_total, last7d_rate, disclaimer },
  "community_heat": { most_followed, hot_discussion, pick_split }
}
```
`performance` and `community_heat` return clearly-labelled mock until their
tables exist — frontend renders the final layout from day one.

---

## 6. Modeling output layer (operations layer above baseline)

The baseline predictor already emits `prob_home/draw/away`, `confidence`,
`risk_level`, `risk_note`, `recommended_score`. The operator docs need a
**human-readable layer on top** — not a new model. Propose an
`ops_output` derivation (pure function of existing prediction fields).

| Field | How derived (Phase A/B rules) | LLM later (Phase C)? |
|-------|------------------------------|----------------------|
| `ai_pick_label` | from prob distribution: home≥48 & lead≥10 → "主胜偏强"; home+draw≥70 → "主队不败"; spread<8 → "难分胜负"; away strong → "客胜偏强"; underdog non-trivial → "可能爆冷" | no (keep deterministic) |
| `confidence_star` | map `confidence` 0–100 → 1–5 stars (e.g. <50→2, 50–60→3, 60–72→4, ≥72→5) | no |
| `upset_score` | f(prob spread small **and** favourite shaky, `tag=upset`, high `risk_level`) → 0–100 | refine w/ data later |
| `heat_score` | Phase A: derive from `tag=focus`/confidence as placeholder. Phase C: real engagement | data-driven later |
| `volatility_score` | from `Report.trend_history` variance, else `risk_level` mapping | data-driven later |
| `live_sensitive_score` | from `risk_level` + stage (knockout↑) now; from lineup dependence later | data-driven later |
| `reason_bullets` | Phase A/B: top contributors from `Report.features[]` rendered as templated short sentences | **Yes — Kimi/DeepSeek** in Phase C |
| `free_conclusion` | blurred label + star only (no exact score) | no |
| `premium_teaser` | count/labels of locked items ("精确比分 + 3 条理由 + 风险评级") | no |

**Judgments:**
1. All fields **derive from existing** `prob_*` / `risk_level` / `confidence` /
   `features` / `trend_history` — no new model, no schema change required (can
   be computed on read, or cached on `Prediction`/`Report` later).
2. **Rules-suitable now:** `ai_pick_label`, `confidence_star`, `upset_score`,
   `volatility_score`, `live_sensitive_score`, `free_conclusion`,
   `premium_teaser`.
3. **LLM-suitable later (Phase C, `AI_PROVIDER`→DeepSeek/Kimi):**
   `reason_bullets` (and a richer `premium` narrative) — natural language is
   where an LLM adds real value; everything numeric stays rules-based for
   determinism + auditability.
4. **Anti-gambling guardrail in generation:** a fixed system prompt + a
   **post-generation banned-word filter** (下注/稳赚/必中/跟单/购彩/回报率/返奖/
   收益承诺/提现…) that rejects or rewrites any output; never emit stake/odds;
   always frame as "数据观点 / 风险提示". Keep label vocabulary on an allow-list
   (倾向/偏强/不败趋势/可能爆冷/难分胜负).

---

## 7. Operations content system

Goal: the **website/API becomes the content factory** for TikTok / Facebook /
Telegram / Zalo, so operators publish 3–5×/day with minimal manual work.

| Operator need | Source | Auto from API? | Human edit? |
|---------------|--------|----------------|-------------|
| 今日 AI 三场速览 | top_pick + 2 next | **Auto** | light caption |
| 今日最强信号 | top_pick | **Auto** | hook title |
| 今日爆冷预警 | upsets/today | **Auto** | — |
| 临场修正截图 | LiveCorrection | **Auto (render card)** | — |
| 昨日战绩复盘 | performance/daily | Auto **once results exist** | tone |
| 用户连胜榜 | rankings | Auto once data exists | — |

**Recommendations:**
1. **"复制运营文案" button — YES (Phase A/C, cheap, high value).** A per-match /
   per-day "copy caption" that outputs a ready, compliant short post (with the
   mandatory disclaimer auto-appended). Pure front-end over existing data.
2. **"生成分享卡" — YES, Phase C.** Server- or client-rendered image card
   (signal/upset/correction/record). Needs a render path (and later R2 for
   hosting — currently off, so start with client-side canvas / on-the-fly PNG).
3. **Auto-generatable content:** signals, upsets, simple lists, lineup-correction
   cards, (later) record recaps — all from API.
4. **Human-edit content:** hook titles, localized phrasing, community posts,
   anything persuasive — operators add the "上头" layer machines shouldn't.
5. **Localization (VN / MM):**
   - Vietnamese first (larger, more football-online, Zalo-native) → Zalo +
     Facebook + TikTok VN.
   - Myanmar second (Facebook-dominant, Telegram for private) → lighter, Burmese
     copy, smaller initial scope.
   - Build i18n scaffolding so labels (`ai_pick_label`, risk tags, disclaimers)
     are translation keys, not hard-coded zh — this is the single most important
     prerequisite for the SEA motion (currently zh-CN only).

---

## 8. Compliance boundary (must-keep)

**Forbidden (any user-facing or generated copy):**
下注 · 稳赚 · 必中 · 跟单 · 购彩 · 回报率 · 返奖 · 收益承诺 · 现金奖池 ·
Token 提现/转让/交易. Also avoid borderline operator phrasings seen in the
docs: **"最稳一场" / "竞猜"** → rename to **"今日最高信心" / "AI 最强信号"**.

**Allowed framing:**
AI 倾向 · 数据观点 · 风险提示 · 社区热度 · 情报更新 · 积分挑战 · 球迷娱乐参考.

**Mandatory disclaimer rule:** any surface showing **"命中率 / 战绩 / 连胜"**
must render:
> 历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。

**MTC statement (every relevant surface):** 平台积分 / platform loyalty points —
不可提现 · 不可转让 · 不可交易 · 不作为金融资产 · 不承诺收益 · 不接入博彩.

**Enforcement proposals:**
- A shared `compliance.ts` (frontend) + `compliance.py` (backend) banned-word
  list, used by the LLM post-filter (§6) and a CI/test scan (already run ad-hoc).
- Track-record numbers must be **real or clearly labelled demo** — never
  fabricate a hit-rate as if real once we claim it publicly.
- The ¥399 "高级群" tier from the operator doc is acceptable **only** as a
  service/content subscription — never as a "pool" or "guaranteed" tier.

---

## 9. Implementation roadmap (3 phases)

### Phase A — Design + light front-end (derived/mock data, minimal/zero backend)
- **Goal:** ship the new home IA + detail re-order so the product *feels* like
  an intelligence community, using only existing data + rules + clearly-labelled
  mock for record/heat.
- **Scope:** Home C-pick, simplified list, upset TOP3 (derived), AI track-record
  (mock + disclaimer), detail "AI 结论卡" on top, `ai_pick_label` +
  `confidence_star` as a client-side `ops` derivation in `transform.ts`/a helper.
  Optional tiny backend: none, or only field additions that don't change shape.
- **Risk:** low. Main risk = mock record/heat misread as real → mitigate with
  explicit "示例/demo" + disclaimer.
- **Acceptance:** build passes; both `VITE_USE_MOCK` modes work; existing API
  untouched; 390/430px no overflow; no forbidden words; home shows a clear C-pick
  + upset board + (demo) record.
- **Affects live version?** Front-end only; safe, reversible.

### Phase B — Backend aggregate APIs
- **Goal:** back the new home with real composition + start real track-record.
- **Scope:** `GET /api/v1/home/summary` (compose existing data + ops layer);
  introduce `MatchResult` table + a results ingestion (via API-FOOTBALL finished
  fixtures) to make `performance/daily` real; optionally `upsets/today`.
- **Risk:** medium — new table + ingestion; keep all new endpoints additive.
- **Acceptance:** `home/summary` returns correct composed data; existing
  endpoints byte-identical; results ingestion idempotent; performance numbers
  reconcile to stored results; admin-protected where it writes.
- **Affects live version?** Additive endpoints; frontend opt-in. Low risk to
  existing flows.

### Phase C — Modeling ops layer + operations automation
- **Goal:** richer, partly-LLM intelligence + the content/share/community loop.
- **Scope:** persist/serve full `ops_output`; `reason_bullets` + premium
  narrative via Kimi/DeepSeek (`AI_PROVIDER` switch) **with banned-word
  post-filter**; `community/heat` + `rankings` (new tables, `UserStreak`);
  "复制运营文案" + "生成分享卡"; i18n (VN/MM); (optional) R2 for share-card
  hosting.
- **Risk:** higher — external LLM cost/latency, compliance of generated text,
  new social data. Gate behind feature flags + filters.
- **Acceptance:** generated copy passes compliance filter 100%; LLM failures
  fall back to rules; share cards render; i18n keys complete for VN; streak/
  ranking data consistent; live version unaffected when flags off.
- **Affects live version?** Only when flags enabled; default off → no impact.

---

## 10. Open questions for human ruling

1. **Positioning copy:** approve public rename to **"AI 足球情报社区"** (and keep
   "决策" out of user copy)? 
2. **Track-record honesty:** are we OK showing **mock** record in Phase A
   (clearly labelled demo), or must "战绩" wait until real results exist (Phase B)?
   This is the biggest trust/compliance call.
3. **Day 5 scope:** front-end-first (Phase A) vs build `home/summary` immediately
   (Phase A+B together)? Recommendation: Phase A first.
4. **Pricing tiers:** operator doc adds ¥19 single + ¥399 premium group on top of
   CLAUDE.md's ¥39 / ¥199. Confirm the canonical price ladder before it hits copy.
5. **Community half:** how real in v1 — light social proof (aggregate/mock) vs
   actual UGC (opinions/晒单/ranking)? Recommendation: light first.
6. **i18n priority:** Vietnamese-first confirmed? Myanmar timing?
7. **LLM provider:** DeepSeek vs Kimi for `reason_bullets` first, and acceptable
   per-match cost/latency budget?
8. **Share-card hosting:** enable R2 in Phase C, or ship client-rendered cards
   first to avoid unblocking R2?
