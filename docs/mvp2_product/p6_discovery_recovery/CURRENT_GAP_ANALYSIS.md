> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# P6 — Current Gap Analysis

## Overall finding: CLEAR RECOVERY PATH

The OLD product strength is **not lost** — it is on `main` but **under-surfaced**. P1.1c (strongcopy @0a73ee6) made the product a single-source PROJECTION: `frontend/src/growth/strongCallProjection.ts` (`buildStrongCall` / `buildRecapCall`) parses the guard-passed LLM narrative **once** (`splitScoreband`: first score = 主比分, rest = 备选; `harmonizedRisk`: 风险偏高 + bare 中 → 中高) and every surface (`/predict` StrongCallCard, `/share` cards, share copy, CLI) renders identical values — eliminating predict/share drift. Every OLD asset is **already merged to main** (`git log main..strongcopy` is empty); two files (`strongCallProjection.ts` +87, `check_growth_copy.py` +28) were extended **further** on main (P5 artifact fallback) — reuse main's version, never re-implement.

**P5b is thinner only because:** the strong-call hook is not surfaced on the homepage lead; the in-page T-30 rescore ladder + calibration-frame line were dropped from the new artifact tactical room; the `real_recap` recap tier lacks the full share kit; and rich per-fixture content is hand-authored one-offs (no generator) with a hardcoded `NEXT_HOOK 'Brazil vs Morocco'`.

**P6 is a copy/UI-first, frontend-only recovery** — surface StrongCallCard on a renderable homepage lead, restore the rescore/calibration affordances + ShareBlock to all recap/predict surfaces, de-hardcode `NEXT_HOOK`, complete the daily prediction/observation artifact schema, and tighten the three guards to require a score-call hook — **with NO backend or schema change required.**

---

### Homepage gaps — Is 今日热点预测 first? Does homepage expose score-call hook? Does it show enough to attract click? Is it too long or too weak?

**Is 今日热点预测 first? — YES within the loop, but NO above the fold.**
Within `HomeProductLoop` the hotspot PREDICTION renders first (P3 order: `HotspotPrediction` before `HotspotRecap`; guard check #8 enforces it). But on `HomePage.tsx` it sits **BELOW ~5 chrome blocks**: `ai-ticker` → `TrialStatusStrip` → hero-banner (俅哥说球 / GIÀNH CUP + 2 subtitles) → cap-bar → balance/check-in strip → daily-sync-line (⟳ 赛程更新…实时). It is the first product/match content but is **likely below the fold on mobile**.

**Does the homepage expose a score-call hook? — NO.**
The lead `HotspotPrediction` card = badge `今日主推·开球前判断` + teams + optional kickoff + **ONE** `predWhy` sentence + `FocusBlock` (today 建模关注 title + **3 GENERIC question bullets** 节奏差异 / 风险变量 / 临场修正 + a 30-min line) + 2 CTAs + CopyLink. **No score, no win-prob, no AI lean/pick, no upset-risk, no strong-call** (`score={null}` is passed deliberately).

The canonical hook (`StrongCallCard` / `buildStrongCall`: 主看 / 主比分 / 备选 / 冷门风险 / 最大变量 / why / T-30) **EXISTS** but is wired only to `/predict`, `/share`, recap, and the tactical strip — **NOT the homepage**. P1.5a explicitly *"cut Strong Calls"* from the landing; verified: `HomeProductLoop.tsx` has **NO strong-call import**. The only homepage win-prob/score hook (signal-card + WinBar + AI pick + stars + top-risk) is **MOCK**, hidden in the collapsed `home-demo-fold` 内部演示数据.

**Does it show enough to attract a click? — WEAK information scent.**
CTAs are clear (进入战术室 ▸ / 加入临场情报群 ▸ / CopyLink) but the scent is low: **every bullet is a question** (是否… / 会不会改判断), never an answer; no lean, no scoreline teaser, no surprising stat — nothing rewards the click *before* the click.

**Is it too long or too weak? — BOTH.**
Two hero cards are stacked (prediction + recap), each with a `FocusBlock` of 3 bullets + 30-min line + paragraph + 2 CTAs + share, then schedule + other recaps + growth = high vertical, repetitive generic copy meeting **zero concrete payload**. The lead optimizes for *"explains the framework"* over *"gives the answer."*

**Structural root cause.** Today's manifest promotes a **non-renderable** `id=null` manual fixture (Netherlands–Japan, `renderable=false`) to the lead via `selectProductLoop` `scheduled[0]`, so even `StrongCallCard` would return `null` there.

**Guard blind spot.** `check_homepage_product_loop.py` (13 checks, live PASS) asserts a TITLE + 进入战术室 CTA + CopyLink exist on the lead but asserts **NOTHING** about a score-call / lean / primary-score / win-prob hook → the weak-hook gap passes green.

---

### Predict page gaps — Does it match old strongcopy strength? Does it include score call, backup score, risk, why, external expectation, T-30? Enough tactical depth? Data-backed or hand-filled?

**Does it match old strongcopy strength? — YES for narrative fixtures, YES-AND-RICHER for the manual hotspot.**
Two strong paths:
- **(A) Fixture WITH a bundled LLM `ProductNarrative`** (`fixture_basis=real_scheduled`) → `StrongCallCard` + `ProductPredictView`, the **exact unchanged old-strongcopy code path** (`PredictPage.tsx` L216-221).
- **(B) Manual hotspot with no narrative** → `getPredictionArtifact(slug)` → `ArtifactTacticalRoom` (the P4/P5 net-new recovery tier the old branch had **no equivalent for** — a hotspot with no LLM narrative previously got only a weak generic shell).

**Element checklist on the live 06-14 surface (Netherlands vs Japan):**

| Element | Present | Notes |
|---|---|---|
| Strong call | ✓ | ⚡俅哥强判断, `main_lean` |
| Main score | ✓ | 主比分 2-1 in `sc-primary-score` |
| Backup score | ✓ | 备选 1-1 / 2-2 |
| Risk | ✓ | 冷门风险 中高 |
| Top variable | ✓ | 最大变量 |
| Why | ✓ | 为什么 |
| Tactical depth | ✓✓ | **Richer than old** — three list blocks below the card: `modeling_focus` 今日建模关注 + `tactical_matchup` 战术对位 + `risk_variables` 风险变量 (old StrongCallCard had none) |
| External expectation | ✓ | 外部预期·公开预测倾向, SAFE_EXT vocab |
| T-30 | ✓ | canonical `T30_HOOK` |
| Share / Join | ✓ | `ShareBlock` `kind=prematch`, 加入临场情报群 |

**Two genuine drops vs the old `StrongCallCard`:**
1. The **calibration frame line** 赛前看方向，临场看变量，赛后看校准 (replaced by `mainSub` 今日主推判断).
2. The dedicated `pp-cta-row` **rescore-scroll button to `#live30`** + the entire in-page **`RescoreBlock` T-30 decision-rules ladder** (free 3 triggers + in-group locked triggers + 5 group Qs + 2 condition→new-call rules). The artifact room has no `#live30` section and routes join through `ShareBlock` instead.

Both are **CTA/styling, not strong-call substance.**

**Data-backed vs hand-filled (the honesty point).**
- Path **(A)** is **DATA-BACKED** — projects guard-passed LLM fields (`scoreline_view` / `main_lean` / `hero_subtitle` / `risk_level` / `watch_next_signals[0]`) + `getExternalSignals`.
- Path **(B)**, which renders **TODAY**, is **HAND-FILLED operator JSON** — `manual_Nether-Japan-20260614.json` is `source=operator_confirmed`, `prediction_confirmed=true`, with its own note *"a qualitative scout call with a reference scoreline — not a precise probability,"* `confidence=null` in all 4 langs. A deliberate, disclosed exception to LLM-owns-narrative, used because no LLM narrative was bundled. `buildStrongCallFromArtifact` **merely maps fields**; nullable numerics fall back to 方向待临场确认 / 比分待开球前30分钟确认 — never invented.

---

### Recap page gaps — Does it read like a trust receipt? Does it show prediction receipt, actual score, hit/deviation, calibration, next impact? Still too light?

**Does it read like a trust receipt? — YES, strongly, on the tier that is actually live.**
The flagship 1489371 Brazil 1-1 Morocco renders via `ObservationReceipt` (artifact `recap_ready=false`). Every receipt field is present (quoting zh from `observation_1489371.json`):

- **RECEIPT (pre-match call):** `pre_match_call` = 赛前主推：偏向巴西，主比分参考 2-1，备选含 1-1
- **ACTUAL:** `actual_line` = 实际比分：1-1 + `art.score` by teams
- **HIT / PARTIAL / MISS:** `assessment` = 比分区间命中，但胜负方向未完全命中，按部分命中处理 (explicit PARTIAL-hit, **no brag**) + a dedicated DEVIATION line
- **CALIBRATION:** `calibration_title` + 3 `calibration_points` bullets (under-weighting named in deviation)
- **NEXT IMPACT:** `next_impact` = 下一场影响：巴西后续需要下调胜负确定性，摩洛哥韧性值得继续跟踪
- **NO FAKE RECAP:** `pending_line` = 完整复盘确认后开放。 + `safety.no_fake_recap=true`
- then `ShareBlock(kind=recap)`.

**The LLM `real_recap` tier is ALSO not light.** `buildRecapCall` summary card (result / what-was-right / why-deviated / calibration / next) leads, then `ProductRecapView` adds PRE-MATCH READ (`model_judgement` + scoreline), VALIDATED, UNDER-WEIGHTED, DECISIVE, EVIDENCE quote, WATCH NEXT.

**Two `real_recap`-tier gaps:**
1. The lead projection surfaces only **ONE** `what_was_right` (`validated_factors[0].name`) — the multi-factor validated/under-weighted lists live only further down, so the lead card is **thinner** than the artifact receipt's call + assessment + deviation + 3-bullet calibration.
2. `calibration_line` + `next_hook` are **FIXED per-language constants** in `strongCallProjection.ts`, and `NEXT_HOOK` is **HARDCODED** `下一场 Brazil vs Morocco` → for any `real_recap` other than the current fixture these go **generic/stale**. The artifact receipt's match-specific `calibration_points` / `next_impact` are the better pattern to propagate.

**Still too light?** Only the **minimal P0 safe-observation tier** is genuinely light (state / teams / lead / calib / join + CopyLink only) — but it is a **fallback** for predicted hotspots with no artifact, **not the receipt path.**

---

### Share / operation gaps — Copy link available? Share text available? Share card available? Join/ref preserved?

**Copy link — AVAILABLE on EVERY tier.**
`ObservationReceipt` → `ShareBlock` 🔗; `real_recap`/deterministic → `DetailShareRow` → `CopyLink` 🔗; P0 tier → `CopyLink`. All copy a ref-appended absolute URL via `shareLink()` with a clipboard + `execCommand` WebView fallback.

**Share text — PARTIALLY available. GAP.**
Available **ONLY** via `ShareBlock` (📋 `recapShareCopy` / `prematchShareCopy`; recap falls back to artifact `share_copy`). The artifact `ObservationReceipt` HAS it. But the `real_recap` recap page uses `DetailShareRow` (link + join **only**) → **NO share-text button.**

**Share card (/share routes + QR) — exists but UNDER-EXPOSED.**
Routes exist and are wired (`share/fixture/:id` `kind=fixture`, `share/recap/:id` `kind=recap` → `ShareCardPage` with `qrcode` QR encoding `SITE/join?ref=`, P1.2b kickoff-freeze + observation fallback, in-frame disclaimer 历史表现不代表未来结果…). Reachable from `ShareBlock` `cardTo` 🖼️ (artifact receipt + StrongCallCard) but **NOT from `DetailShareRow`** → under-exposed on the `real_recap` recap tier and predict pages.

**Join / ref preserved — YES, universally.**
`refCapture` stores `?ref=` first-touch (30-day localStorage, `CODE_RE ^(QG|TT|FO)-[A-Z0-9]{4,6}$`); `refFor` injects stored-or-`DEFAULT_REF` (zh `QG-TEST1` / vi `TT-VN88` / my `FO-MM21`) into every copied link, share-text link, and the share-card QR; join taps fire `recordJoinIntent({ref,surface,lang})` (silently skipped in mock, never blocks UI). Ref survives copy-link → visit → join AND share-card → QR-scan → join across all tiers, attribution-only (no money/identity fields by Owner design).

**Net actionable gap = affordance asymmetry.** Wire the `real_recap`/Tier-1 recap page + predict pages to `ShareBlock` (or add the share-text + share-card buttons to `DetailShareRow`) so every recap/predict surface gets copy-text + card/QR.

---

### Daily update gaps — Where does rich prediction content get lost? Which files are created daily now? Which should be created daily?

**Where rich content is lost day-to-day:**
1. **Strong-call depth is NOT regenerated per fixture.** Bundled `productNarratives` exist for **ONLY** `1489369`/`1489371` (LLM-generated 06-11); every new daily hotspot has no narrative → depends on a **HAND-AUTHORED** `predictionArtifacts/manual_<slug>.json`, and **NO generator script exists** (only validators) → does not scale past ~1 hand-written fixture/day.
2. **The homepage featured card is GENERIC boilerplate.** `HotspotPrediction` renders static `predWhy` / `predBullets` with `{home}`/`{away}` substitution + a fixed 30-min line, **NOT** the artifact's `score_call` / `top_variable` / `tactical_matchup`; the real strong call surfaces only one click deeper at `/predict/{key}` (`ArtifactTacticalRoom`) — a non-clicking reader **never sees** the daily judgment.
3. **Only Mexico/Brazil are `renderable=true`;** all 5 other fixtures today are `renderable=false` → lightweight status rows forever. The "daily" rich product is effectively **2 carried-over matches + 1 hand-authored artifact.**
4. **External signals are NOT refreshed** (frames exist only for 4 fixtures dated 06-12; new hotspots get `external_expectation` hand-typed into the artifact, bypassing `mvp2_project_external_signals.py` → **no provenance**).
5. **Full recap degrades to an observation receipt** (Brazil 1-1, `recap_ready=false`, no A4 `real_recap` bundled).
6. **The editorial decision is NOT persisted** — no `selected_hotspot_<date>.json`; it lives in `mvp2_editorial_agent.py` stdout (prompt-builder ONLY: prints to stdout, writes nothing, calls no API) + operator memory + hand-edited manifest flags that a **re-sync WIPES.**

**Files created daily NOW (automated):**
- `manual_scores_<date>.md` (manual input) → `mvp2_match_sync.py` writes:
  - `daily_fixtures_<date>.json` (registry)
  - `recap_queue_<date>.json`
  - `dailyFixtures.generated.json`
  - `frontend/public/data/daily-fixtures.json`
- `mvp2_fixture_lifecycle.py` writes `fixture_lifecycle_<date>_<hhmm>.json`
- `mvp2_growth_cli.py refresh` writes `growth_packages/{today,next,recap}_{fid}_{lang}_{REF}.md` + `refresh_summary`

**Hand-authored per day (then hardcoded into `predictionArtifacts.ts` imports + `check_prediction_artifact.py` paths + a frontend REBUILD):**
- `predictionArtifacts/manual_<slug>-<date>.json` (strong call)
- `observation_<fid>.json` (receipt)

**Which should be created daily (gap list):**
- A persisted `selected_hotspot_<date>.json` — **MISSING (ephemeral)**.
- A per-fixture prediction artifact with strong call via a **GENERATOR** (currently hand-authored one-off).
- A daily external-signal refresh **with provenance**.
- A regenerated T-30 placeholder (currently manual).
- A full recap artifact for the day's finished hotspot — **MISSING (needs A4 + redeploy)**.

**Note:** only the daily-fixtures manifest is **runtime-updatable** (backend upload, no rebuild); any new artifact/narrative requires a **frontend redeploy.**

---

## Cross-cutting notes for the recovery team

- **Single source of truth to reuse, never re-implement:** `frontend/src/growth/strongCallProjection.ts` (`buildStrongCall` / `buildStrongCallFromArtifact` / `buildRecapCall`). Use **main's** version (P5 artifact fallback already added); the strongcopy-branch snapshot is stale by ~87 lines.
- **Strong-call assembly is DUPLICATED** in `scripts/mvp2_growth_cli.py` and `strongCallProjection.ts` (scoreband split, 中高 harmonization) → any change must touch **both** or drift.
- **Dead code:** `frontend/src/components/MatchDesk.tsx` (P1.4 RecapDesk / UpcomingNeedsNarrative / OperatorStatusLine) is **not imported anywhere** — superseded by `HomeProductLoop`; candidate for deletion (defer).
- **External-signal pipeline is not generalized:** `mvp2_project_external_signals.py` hardcodes a `1489371`-only `TEAMS` dict + fixture-literal prose; new fixtures must edit the script.
- **No-send posture intact throughout:** all P6 P0 changes are additive frontend/docs/script edits — NO backend route, NO DB table, NO schema migration. The runtime daily-fixtures manifest shape is unchanged, so a UI rollback cannot corrupt live data.
- **Owner sign-off needed:** re-adding a homepage score-call hook **reverses the P1.5a decision** that cut Strong Calls from the landing.
