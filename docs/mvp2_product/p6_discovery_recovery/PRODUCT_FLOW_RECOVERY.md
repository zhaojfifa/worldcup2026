> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# PRODUCT_FLOW_RECOVERY.md — The CORRECT Product Flow

This document defines the **correct product flow** (the experience, not the implementation) that the
recovery (P6) should restore and surface. It is the Owner-specified ordering for each surface. It
describes what the customer should encounter, in what order, on each of the five surfaces:
**Homepage · Predict (tactical room) · Recap · Share · Join**.

The strong OLD product expression is **not lost** — it is already merged to `main` (`git log
main..strongcopy` is empty) and is reused on `/predict`, `/share`, and `/recap`. P5b reads thinner
only because:

- the strong-call score hook is **not surfaced on the homepage lead**;
- the in-page T-30 rescore ladder + the calibration-frame line were **dropped** from the new artifact
  tactical room;
- the `real_recap` recap tier **lacks the full share kit** (text + card/QR);
- rich per-fixture content is **hand-authored one-offs** (no generator) with a hardcoded
  `NEXT_HOOK` ("Brazil vs Morocco").

The flow below is therefore a **copy/UI-first, frontend-only** target — no backend, no schema, no DB
change is required to express it.

> **Canonical projection keystone.** Every score-call / recap value on every surface is produced by a
> single source: `frontend/src/growth/strongCallProjection.ts`
> (`buildStrongCall` / `buildStrongCallFromArtifact` / `buildRecapCall`). It parses the guard-passed
> LLM narrative (or operator-confirmed artifact) **once** — `splitScoreband` (first band score = 主比分,
> the rest = 备选), `harmonizedRisk` (lean says 风险偏高 + a bare 中 label → display 中高) — and orders the
> fields. Every surface renders **identical** values, eliminating predict/share drift. No judgement
> string is invented in engineering: the module only parses, merges, and orders LLM/artifact fields;
> nullable numerics fall back to honest pending labels (`方向待临场确认` / `比分待开球前30分钟确认`), never
> fabricated values.

---

## 1. Homepage (hotspot prediction FIRST, recap SECOND)

The homepage is the hotspot funnel entrance. The lead is **today's selected hotspot prediction**; the
recap comes **second**. The prediction lead must carry a **score-call hook** that is visible above the
fold and gives an *answer*, not a list of questions — enough information scent to earn the click into
the tactical room — and the copy / share / join affordances must be visible.

Correct ordered flow (the experience the customer should encounter top-to-bottom):

1. **Page chrome** (ai-ticker → trial-status strip → hero banner 俅哥说球 / GIÀNH CUP → cap bar →
   balance / check-in strip → daily-sync line `⟳ 赛程更新…实时`). Kept lean; this is stage furniture,
   not product payload. (Today it pushes the lead below the fold on mobile — the recovery should
   tighten it.)
2. **Hotspot PREDICTION lead (FIRST product block).** Today's selected hotspot. The lead must be a real
   **score-call hook**, not a generic question frame:
   - **主看 / lean** — the directional call (which side is favoured), visible.
   - **主比分 + 备选** — the primary score and the backup scores (the confidence the reader pays for),
     split by `splitScoreband`.
   - **冷门风险** — upset-risk level (harmonized, e.g. 中高).
   - **最大变量** — the single biggest variable, teased.
   - One concrete *why* sentence (an answer, not "是否…/会不会改判断").
   - The generic question-frame (建模关注 + 3 generic bullets) is kept **only** as the non-renderable
     fallback when the lead has no narrative/artifact.
3. **CTA to the tactical room + conversion + share, visible on the lead:**
   - `进入战术室 ▸` (into `/predict/{key}`),
   - `加入临场情报群 ▸` (join),
   - **Copy link** (CopyLink, ref-appended).
4. **Hotspot RECAP (SECOND product block).** Gated on `recapReady` — **never fake**. Shows a real recap
   entry only when one exists; otherwise the day's finished hotspot shows as a 赛后观察 / observation
   receipt, never a synthesized result.
5. **Secondary schedule** (`即将开赛` chips) — the rest of the slate as lightweight rows.
6. **Other recaps** — `查看复盘` shown **only** when `recapReady` for that item.
7. **Growth conversion** block.

**Recovery notes for this surface.**
- The score-call hook asset (`StrongCallCard` / `buildStrongCall`) already exists but is wired only to
  `/predict`, `/share`, recap, and the tactical strip — **not** the homepage (P1.5a explicitly *cut*
  Strong Calls from the landing; `HomeProductLoop.tsx` has no strong-call import). Re-adding a
  homepage score-call hook **reverses a P1.5a Owner decision and needs sign-off**.
- The lead must be a **renderable** fixture (has a bundled narrative or a registered prediction
  artifact). Today's manifest promotes a non-renderable `id=null` manual fixture (Netherlands–Japan,
  `renderable=false`) to the lead via `selectProductLoop` slate-order, so even `StrongCallCard` would
  return `null` there. Selection must guarantee a renderable lead, or the hook silently vanishes.
- Guard blind spot: `check_homepage_product_loop.py` (13 checks, PASS) asserts the lead has a
  **title + 进入战术室 CTA + CopyLink** but asserts **nothing** about a score-call / lean / primary-score /
  win-prob hook — so the weak-hook gap passes green. The guard must be tightened to require a
  score-call hook on a renderable lead, sequenced to land **with** the UI hook.

---

## 2. Predict — Tactical Room (`/predict/:slug`)

The tactical room is where the full pre-match judgement lives. The Owner-ordered elements are: strong
call → score / backup → risk / biggest variable → why → tactical analysis → external expectation →
T-30 → share / join. Two strong render paths exist, both reaching the same canonical strong call:

- **Path A — fixture WITH a bundled LLM `ProductNarrative`** (`fixture_basis=real_scheduled`):
  `StrongCallCard` + `ProductPredictView` — the exact unchanged old-strongcopy code path. This is
  **data-backed** (projects guard-passed LLM fields).
- **Path B — manual hotspot, no narrative** (`needsFallback`): `getPredictionArtifact(slug)` →
  `ArtifactTacticalRoom` — the P4/P5 **net-new recovery tier** the old branch had no equivalent for.
  This renders today (NL vs JP). It is **hand-filled operator JSON** (`source=operator_confirmed`,
  `confidence=null`, disclosed in-note as "a qualitative scout call with a reference scoreline — not a
  precise probability"); `buildStrongCallFromArtifact` merely maps fields, nullable numerics fall back
  to pending labels, nothing is invented.

Correct ordered flow:

1. **Banner** — 俅哥战术室（赛前判断）.
2. **Fixture meta card** — kickoff / venue / round (data-backed facts).
3. **Strong call** — the condensed call: kicker `⚡俅哥强判断` / STRONG CALL → **主看 / lean**.
4. **主比分 + 备选 (score / backup)** — primary score in `sc-primary-score`, backup scores split out.
5. **冷门风险 + 最大变量 (risk / biggest variable)** — harmonized upset risk + the single biggest variable.
6. **为什么 (why)** — the reasoning (`hero_subtitle` / artifact `why`).
7. **Tactical analysis (depth)** — three list blocks below the card, **richer than the old card**:
   `modeling_focus` (今日建模关注) + `tactical_matchup` (战术对位) + `risk_variables` (风险变量).
8. **🌐 外部预期 · 公开倾向 (external expectation)** — compliant public-consensus lines (SAFE_EXT vocab;
   direction + band enum only, **zero** odds / prices / sources / bookmaker names).
9. **⏱️ T-30** — the canonical `T30_HOOK`. **Recovery restores** the in-page `RescoreBlock` T-30
   decision-rules ladder + the `#live30` anchor + the `pp-cta-row` rescore-scroll CTA (free 3 triggers
   + in-group locked triggers + group questions + 2 condition→new-call rules). The artifact room
   currently drops this and routes join through `ShareBlock`.
10. **Calibration frame** — **recovery restores** the dropped line
    `赛前看方向，临场看变量，赛后看校准` (the artifact room replaced it with `mainSub` 今日主推判断).
11. **Share / join** — `ShareBlock` (copy link / copy text / share card / join).

**Post-match guard.** If the fixture's narrative `mode == real_recap`, `/predict` redirects to
`/recap/:id` — the pre-match room is over; **no stale pre-match is shown**.

**Two genuine drops vs the old `StrongCallCard` (both CTA/styling, not strong-call substance):**
(1) the calibration-frame line (#10 above); (2) the `#live30` rescore-scroll CTA + the whole in-page
`RescoreBlock` ladder (#9). Restoring both is gated on `getRescore` data existing for the fixture.

---

## 3. Recap (`/recap/:id`) — the Trust Receipt

The recap must read like a **trust receipt**: the prediction receipt (what was called pre-match) → the
actual score → a partial-hit / miss / deviation assessment (honest, no brag) → calibration → next
impact → share / join. The strongest live tier is `ObservationReceipt` (used by flagship
1489371 Brazil 1-1 Morocco, `recap_ready=false`). It is a complete receipt and never fakes a result.

Correct ordered flow:

1. **RECEIPT (pre-match call)** — `pre_match_call`, e.g.
   `赛前主推：偏向巴西，主比分参考 2-1，备选含 1-1`.
2. **ACTUAL score** — `actual_line` (e.g. `实际比分：1-1`) + the score by teams.
3. **HIT / PARTIAL / MISS + DEVIATION** — `assessment`, explicit and honest
   (e.g. `比分区间命中，但胜负方向未完全命中，按部分命中处理` — explicit PARTIAL-hit, no brag) plus a dedicated
   **deviation** line naming the under-weighting.
4. **CALIBRATION** — `calibration_title` + match-specific `calibration_points` (bullets).
5. **NEXT IMPACT** — `next_impact`
   (e.g. `下一场影响：巴西后续需要下调胜负确定性，摩洛哥韧性值得继续跟踪`).
6. **NO FAKE RECAP guard** — `pending_line` (`完整复盘确认后开放。`) + `safety.no_fake_recap=true`. When
   `recap_ready=false`, the page renders the observation receipt, **never** a synthesized result.
7. **Share / join** — `ShareBlock(kind=recap)` with join CTA.

Below the receipt, the **`real_recap` LLM tier** (`ProductRecapView`) adds depth: PRE-MATCH READ
(`model_judgement` + scoreline) → VALIDATED → UNDER-WEIGHTED → DECISIVE → EVIDENCE quote → WATCH NEXT.

**Recovery notes.**
- The `real_recap` lead projection (`buildRecapCall`) surfaces only **one** `what_was_right`
  (`validated_factors[0].name`); the multi-factor validated / under-weighted lists live further down,
  so the lead card is thinner than the artifact receipt's call + assessment + deviation + 3-bullet
  calibration. Recovery should **propagate the ObservationReceipt's match-specific
  `calibration_points` + `next_impact`** into the `real_recap` tier (it is the better pattern).
- `CALIBRATION_LINE` and `NEXT_HOOK` are **fixed per-language constants** in
  `strongCallProjection.ts`, and `NEXT_HOOK` is **hardcoded** `下一场 Brazil vs Morocco` → for any other
  `real_recap` these go generic/stale. **De-hardcode `NEXT_HOOK`** so the next-match pointer comes from
  the slate.
- Order discipline at the surface: recap tier wires the **full** `ShareBlock` kit, not just
  `link + join` (see §4).

---

## 4. Share — Operator Forward + QR / Ref

The operator can forward the prediction **and** the recap as branded, screenshot-ready cards; QR and
ref attribution are supported. Copy-link, share-text, share-card, and join must be available on **every**
tier (today the `real_recap` recap tier and predict pages are under-exposed — see gap).

Correct flow:

1. **From any surface → `ShareBlock`** (4 mini buttons): 🔗 copy link · 📋 copy share text ·
   🖼️ view share card · 👥 join.
2. **Share card** (`/share/{fixture,recap}/:id?ref=CODE`) → `ShareCardPage`: a branded card
   (Giành Cup · persona · teams · lean · scoreband (`shc-primary` + 备选) · risk · top variable · first
   external-expectation line · ⏱️ T-30 hook · calibration frame · **in-frame disclaimer**
   `历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。`) **plus a QR** (`qrcode`, 132px) encoding
   `SITE/join?ref=CODE`. P1.2b kickoff-freeze + observation fallback apply.
3. **Operator forward** — the operator **screenshots the in-frame card** (persona + disclaimer must
   stay in frame); the link is pasted **outside** the image. Pre-match card freezes after kickoff;
   `/share/fixture` auto-redirects to recap when `recapAllowed`.
4. **Ref / QR attribution** — `refCapture` stores first-touch `?ref=` (30-day localStorage,
   `CODE_RE ^(QG|TT|FO)-[A-Z0-9]{4,6}$`); `refFor` injects the stored ref (else per-lang `DEFAULT_REF`
   zh `QG-TEST1` / vi `TT-VN88` / my `FO-MM21`) into every copied link, share-text link, and the
   share-card QR. Ref survives copy-link → visit → join **and** share-card → QR-scan → join, across all
   tiers — **attribution only** (no money / identity fields, by Owner design).

**Recovery note (the net actionable share gap).** Affordance asymmetry: the artifact
`ObservationReceipt` (Tier 2) and `StrongCallCard` use the full `ShareBlock` (text + card/QR); the
`real_recap` recap page (Tier 1) and predict pages use `DetailShareRow` = **link + join only** — **no**
copy-share-text button, **no** share-card link. Wire the `real_recap`/Tier-1 recap page + predict
pages to `ShareBlock` (or add the 📋 share-text + 🖼️ share-card buttons to `DetailShareRow`) so every
recap/predict surface gets copy-text + card/QR.

---

## 5. Join — Group Conversion (NO auto-send)

Join is **group conversion**. Nothing is generated, scheduled, or sent by software — every send remains
manual, one channel, per Owner GO.

Correct flow:

1. **`加入临场情报群` CTA** (on lead, predict, recap, share) → `recordJoinIntent({ref, surface, lang})`
   → navigate `/join`.
2. **Ref preserved** — `refCapture` first-touch `?ref=` survives to attribution; `recordJoinIntent`
   posts only `{ref, surface, lang}` (no identity). Mock/offline silently skips the beacon — it
   **never blocks the UI**.
3. **No auto-send floor.** Software generates / schedules / sends **nothing**. All sends are manual,
   one channel, per explicit Owner per-channel GO (e.g. `GO zh_internal_group QG-TEST1 fixture <id>`).
   Scope ceiling: zh internal group · vi trusted Telegram · my 1 test group.

---

## Cross-surface invariants (preserve through recovery)

- **Single projection source.** All score-call / recap values come from `strongCallProjection.ts`; do
  not re-implement strong-call assembly. (It is currently **duplicated** in `mvp2_growth_cli.py` and
  `strongCallProjection.ts` — any change must touch both or they drift.)
- **No fake recap.** Recap copy renders only from a guarded `real_recap`, else the recovered
  `ObservationReceipt`; never a synthesized score.
- **No invented numerics.** Null score/direction surfaces as a pending label, never a fabricated value.
- **Compliance floor.** No betting / odds / 盘口 / 投注 / handicap / bookmaker vocab in any language
  (even negated) on any growth surface; MTC = 平台积分 (不可提现 / 不可转让 / 不可交易); mandatory disclaimer
  in-frame on every screenshotted card. Enforced by `check_growth_copy.py` (5 classes × 4 langs).
- **No auto-send anywhere.** Join + share are manual operator actions; software sends nothing.
- **en falls back to English, never Chinese.** Strong-call / share components return `null` for `en`
  (internal-fallback layer), not a Chinese surface.

---

## Owner decisions that gate this flow (for reference)

1. **Re-add a score-call hook to the homepage lead** (reverses P1.5a's "cut Strong Calls"). Recommended:
   **C then A** — ship a compromise teaser (lean + 主比分 only) first, then the full hook once a
   renderable lead is guaranteed.
2. **Force the homepage lead to be a RENDERABLE fixture** (`selectProductLoop` picks the first
   renderable scheduled fixture, frame-only fallback if none). Recommended: **A**.
3. **Allow operator-confirmed daily score calls** (hand-authored artifacts) as a disclosed
   LLM-owns-narrative exception + add a scaffolder/generator. Recommended: **A**.
4. **External-expectation block on the homepage lead, or detail-only?** Recommended: **A (detail-only)**
   until `mvp2_project_external_signals.py` is generalized.
5. **Persist the editorial hotspot selection** as `selected_hotspot_<date>.json`. Recommended: **A**.
6. **Scope P6 to UI/artifacts + docs consolidation, or UI only?** Recommended: **A (UI/artifacts +
   docs consolidation)**.
7. **Tighten `check_homepage_product_loop.py` to require a score-call hook + generalize
   `check_prediction_artifact.py`.** Recommended: **A (both)**, sequencing the homepage assertion to
   land with the UI hook.
