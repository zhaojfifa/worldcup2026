> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# P6 Implementation Plan — Product-Strength Recovery (copy/UI-first, frontend-only)

## 0. Overall finding

**CLEAR RECOVERY PATH.** Every strong OLD product asset already lives on main and is
reused on `/predict`, `/share`, and `/recap`. P5b reads thinner only because the strong
moments are **under-surfaced**, not lost:

- the strong-call hook is **not surfaced on the homepage lead**;
- the in-page **T-30 rescore ladder + calibration-frame line** were dropped from the new
  artifact tactical room;
- the `real_recap` recap tier **lacks the full share kit**;
- rich per-fixture content is **hand-authored one-offs** (no generator) with a hardcoded
  `NEXT_HOOK` = "Brazil vs Morocco".

P6 is therefore a **copy/UI-first, frontend-only recovery**: surface `StrongCallCard` on a
renderable homepage lead, restore the rescore/calibration affordances + `ShareBlock` to all
recap/predict surfaces, de-hardcode `NEXT_HOOK`, complete the daily prediction/observation
artifact schema, and tighten the three guards to require a score-call hook.

**Backend / schema change required: NO.** P6 P0 is copy / UI / artifact / validator only —
no backend route, no DB table, no schema migration. (See §6 Deploy impact and the explicit
statement in §8.)

---

## 1. P0 scope

All of P0 is **FRONTEND / COPY / UI + VALIDATOR ONLY — NO backend, NO schema.**

### (A) Homepage score-call hook
Upgrade the `HotspotPrediction` lead (`HomeProductLoop.tsx`) from a generic question-frame
to a real **score-call teaser** by surfacing `buildStrongCall(fixture_id, loc)` output
(主看 lean + 主比分 / 备选 + 冷门风险 + 最大变量) **WHEN the featured prediction is renderable**;
keep the generic frame only as the **non-renderable fallback**.

Why: today's lead card = badge `今日主推·开球前判断` + teams + optional kickoff + ONE
`predWhy` sentence + `FocusBlock` (title + 3 **generic question bullets** 节奏差异 / 风险变量 /
临场修正 + 30-min line) + 2 CTAs + CopyLink. It deliberately passes `score={null}`: no score,
no win-prob, no lean/pick, no upset-risk, no strong-call. The canonical hook
(`StrongCallCard` / `buildStrongCall`: 主看 / 主比分 / 备选 / 冷门风险 / 最大变量 / why / T-30)
**exists** but is wired only to `/predict`, `/share`, recap, and the tactical strip — **not the
homepage**. Information scent is low: every bullet is a question (是否… / 会不会改判断), never an
answer; nothing rewards the click before the click.

### (B) Stronger tactical depth / restore dropped affordances
Re-add to `ArtifactTacticalRoom` the **calibration frame line**
(赛前看方向，临场看变量，赛后看校准) + the **rescore-scroll CTA / `#live30` anchor** so the manual
hotspot reaches the **T-30 `RescoreBlock` ladder** (free 3 triggers + in-group locked triggers
+ 5 group questions + 2 condition→new-call rules). Gate the CTA on `getRescore` existing.

Why: the two genuine drops in `ArtifactTacticalRoom` vs the old `StrongCallCard` are
(1) the calibration frame line (replaced by `mainSub` 今日主推判断) and (2) the dedicated
`pp-cta-row` rescore-scroll button to `#live30` + the entire in-page `RescoreBlock` ladder.
Both are **CTA/styling, not strong-call substance** — the strong call itself is intact (and the
artifact room is actually **richer** than the old card: it adds three list blocks below the call
— `modeling_focus` 今日建模关注 + `tactical_matchup` 战术对位 + `risk_variables` 风险变量 — which
the old `StrongCallCard` had none of).

### (C) Richer recap receipt
Propagate the `ObservationReceipt`'s **match-specific** `calibration_points` + `next_impact`
into the `real_recap` tier; **de-hardcode `NEXT_HOOK`** in `strongCallProjection.ts` so the
下一场 pointer comes from the slate, not the literal "Brazil vs Morocco".

Why: the `ObservationReceipt` tier (live for flagship 1489371 Brazil 1-1 Morocco) is already a
complete trust receipt — pre_match_call → actual_line → assessment (explicit 部分命中, no brag)
→ dedicated deviation line → calibration_title + 3 match-specific calibration_points →
next_impact → `pending_line` (完整复盘确认后开放。, `no_fake_recap=true`) → `ShareBlock(kind=recap)`.
The `real_recap` tier has **two gaps**: (1) `buildRecapCall` surfaces only **one**
`what_was_right` (`validated_factors[0].name`) on the lead card — the multi-factor lists live
only further down; (2) `calibration_line` + `next_hook` are **fixed per-language constants**
and `NEXT_HOOK` is **hardcoded** "下一场 Brazil vs Morocco" → for any other real_recap they go
generic/stale. The artifact receipt's match-specific points are the better pattern to propagate.

### (D) Share / operator completeness
Swap `DetailShareRow` → `ShareBlock` (or add 📋 copy-text + 🖼️ share-card buttons) on the
`real_recap` recap page **and** predict pages; consolidate the design-branch SOP / CTA /
compliance onto a **main-tracked operations doc**.

Why — affordance asymmetry: **CopyLink** is on every tier; **share text** is available ONLY via
`ShareBlock` (so the artifact `ObservationReceipt` has it, but the `real_recap` page uses
`DetailShareRow` = link + join only → NO share-text button); **share card + QR** (`/share` routes)
is reachable from `ShareBlock` `cardTo` 🖼️ but NOT from `DetailShareRow` → under-exposed on the
real_recap recap tier and predict pages. Wiring those surfaces to `ShareBlock` (or adding the two
buttons to `DetailShareRow`) closes the gap. Ref/join is already preserved universally
(refCapture first-touch ?ref=, 30-day localStorage, injected into every link / share-text / QR).

### (E) Daily artifact schema completeness
Add a per-day **prediction-artifact scaffolder** + **persist the editorial selection** as
`selected_hotspot_<date>.json` (script / docs only).

Why — where rich content is lost day-to-day:
- Strong-call depth is **not regenerated per fixture**: bundled `productNarratives` exist for
  ONLY 1489369 / 1489371; every new daily hotspot depends on a **hand-authored**
  `predictionArtifacts/manual_<slug>.json`, and **no generator script exists** (only validators)
  → does not scale past ~1 hand-written fixture/day.
- The homepage featured card is **generic boilerplate** — `HotspotPrediction` renders static
  `predWhy` / `predBullets` with `{home}`/`{away}` substitution, NOT the artifact's
  `score_call` / `top_variable` / `tactical_matchup`; the real call surfaces only one click
  deeper at `/predict`.
- The **editorial decision is not persisted** — there is no `selected_hotspot_<date>.json`; it
  lives in `mvp2_editorial_agent.py` stdout (prompt-builder only: prints, writes nothing, calls
  no API) + operator memory + hand-edited manifest flags **that a re-sync WIPES**.

P0 ships a **scaffolder + persisted selection**, NOT the full LLM generator (that is P1).

---

## 2. P1 (deferred)

- A real **per-fixture LLM prediction-artifact GENERATOR** wired through the existing
  scoutscore v0.2 → narrative → guard → bundle pipeline (P0 ships a scaffolder +
  validator-generalization, not the full generator).
- **A4 full-recap generation** + a **daily external-signal refresh with provenance** (so
  `externalSignals` stops being 4 stale 06-12 frames).
- **Generalize `mvp2_project_external_signals.py`** off its 1489371-only `TEAMS` dict and
  fixture-literal prose (expert_consensus / media_heat / lineup lines are hardcoded for 1489371).
- Make `predictionArtifacts` **runtime-loadable** so a new artifact does not require a redeploy
  (touches manifest/loader — defer unless redeploy cadence is the bottleneck).
- **Delete dead `MatchDesk.tsx`** (P1.4 RecapDesk/UpcomingNeedsNarrative/OperatorStatusLine —
  not imported anywhere; superseded by `HomeProductLoop`).
- Any growth **RUNTIME** expansion (Track B referral mechanics stay **design-only**).

---

## 3. Files likely to change (concrete current-main paths)

| Path | Change |
|---|---|
| `frontend/src/components/HomeProductLoop.tsx` | lead → score-call hook (A) |
| `frontend/src/data/dailyFixtures.ts` | `selectProductLoop` must NOT promote a non-renderable fixture to the lead (A, renderable-first) |
| `frontend/src/components/StrongSignalCard.tsx` | restore calibration line (B) — shared strong-call card |
| `frontend/src/components/ArtifactTacticalRoom.tsx` | restore calibration line + rescore CTA / `#live30` anchor (B) |
| `frontend/src/growth/strongCallProjection.ts` | de-hardcode `NEXT_HOOK`; propagate match-specific recap calibration/next (C) |
| `frontend/src/pages/RecapDetailPage.tsx` | `ShareBlock` / share-text + card buttons on real_recap tier (D) |
| `frontend/src/components/DetailShareRow.tsx` | add 📋 copy-text + 🖼️ share-card buttons, OR be replaced by `ShareBlock` (D) |
| `frontend/src/components/ProductProofViews.tsx` | optional: recap lead multi-factor surfacing (C) |
| `frontend/src/data/predictionArtifacts.ts` + new `predictionArtifacts/manual_<slug>-<date>.json` + `observation_<fid>.json` | daily content + scaffolder output (E) |
| `scripts/mvp2_editorial_agent.py` / `scripts/mvp2_match_sync.py` | persist `selected_hotspot_<date>.json` (E — script/docs only) |
| docs operations consolidation (`FIRST_SEND_RUNBOOK` + on-main SOP/CTA/compliance) | consolidate design-branch SOP/CTA/compliance onto a main-tracked operations doc (D) |

**Reuse, never re-implement:** both `strongCallProjection.ts` (+87 lines on main, P5 artifact
fallback) and `check_growth_copy.py` (+28 lines on main, P1.2/P1.3/P5 globs) were extended
**further on main** than the strongcopy branch snapshot — use **main's** version; the branch
copies are stale. (`git log main..strongcopy` is empty — every OLD asset is already merged.)

---

## 4. Guards to update

### `scripts/check_homepage_product_loop.py`
**ADD** an assertion that a **renderable lead carries a score-call hook**
(`sc-primary-score` / 主比分 marker OR a lean token) to close the documented blind spot.
Keep the existing 13 structural / order / no-fake-recap / no-betting checks.

> Blind spot today: the 13 checks assert a TITLE + `进入战术室` CTA + CopyLink exist on the lead,
> but assert **NOTHING** about a score-call / lean / primary-score / win-prob hook → the weak-hook
> gap passes green. This is exactly why the weak hook shipped.

### `scripts/check_prediction_artifact.py`
**GENERALIZE** off the two hardcoded filenames (`manual_Nether-Japan-20260614.json`,
`observation_1489371.json`) to **glob the artifact dir** so each day's artifact + observation
validates without editing the validator. **Keep** the P5b rules:
- confirmed strong call: zh `prediction.primary_direction` / `score_call` / `backup_score`
  all **non-null** (no weak default);
- per-lang `top_variable` + `why` required; `analysis` 5 lists non-empty;
- deviation rule: deviation must contain `偏差` or `低于`; assessment `部分命中` or `校准`;
  `recap_ready` MUST be **false** (no fake recap);
- `external_expectation` lines must hit the **SAFE_EXT** vocab; Han = 0 for vi / my.

### `scripts/check_growth_copy.py`
**EXTEND GLOBS** to cover any new `HotspotPrediction` score-call copy + the `RecapDetailPage`
real_recap share affordances. Note: `RecapDetailPage.tsx` is currently **NOT** in `GLOBS`
(its 模型回放 / 模型修正 labels live in a folded internal block, covered by the separate
`check_customer_visible_copy.py`); if **new customer-visible copy** lands on the recap lead, add
it to one scanner. Use **main's** newer `check_growth_copy.py` (already has P1.2/P1.3/P5 globs).

**Optional P1:** implement the long-deferred `check_growth_material.py` (OCR-of-card; the
`GROWTH_P0_GUARD_SPEC.md` §8 scanner never built — P0 was checklist-only).

> **Sequencing rule (critical):** the homepage score-call assertion must land **WITH** the UI
> hook, not before it — otherwise the guard turns the build red while the hook is still missing.

---

## 5. Deploy impact

- **FRONTEND-ONLY** for all rendered changes: every touched component + new artifact JSON is
  **bundled at build** → a frontend redeploy ships them. Backend is **not touched and not needed**.
- **DOCS / SCRIPT-ONLY** for the operations-doc consolidation, editorial-selection persistence,
  and guard updates (no runtime).
- The runtime **daily-fixtures manifest is unchanged in shape**.
- **EXPLICIT:** P6 P0 requires **NO backend route, NO DB table, NO schema migration.**

---

## 6. Risks

1. **P1.5a explicitly CUT Strong Calls from the landing** — re-adding a homepage score-call hook
   reverses an Owner decision (needs sign-off; see OWNER_DECISIONS #1).
2. `buildStrongCall` returns **null** for a non-renderable `id=null` lead — if `selectProductLoop`
   keeps promoting one (today's Netherlands–Japan), the hook **silently vanishes**; the selection
   must guarantee a renderable lead (OWNER_DECISIONS #2).
3. **Strong-call assembly is DUPLICATED** in `mvp2_growth_cli.py` and `strongCallProjection.ts`
   (scoreband split, 中高 harmonization, per-lang copy) → changes must touch **both** or drift.
4. **External-signal + rescore data exist for one/two fixtures only** (06-12); without a daily
   refresh the 🌐 and T-30 blocks vanish on new fixtures.
5. Hand-authored artifact content is an **LLM-owns-narrative exception** — scaling risks
   engineering-authored football prose (the soft-judgement tension already flagged).
6. **Guard tightening could break PASS state** if the score-call assertion lands before the UI
   hook — sequence guard + UI together (see §4).
7. `DEFAULT_REF` codes (QG-TEST1 / TT-VN88 / FO-MM21) are **not yet created in prod**
   (attached:false) — an **operational gate**, not a code defect.

---

## 7. Rollback plan

All P0 changes are **additive frontend / docs / script edits** on a **dedicated branch** with
**per-step backup tags** (per the `main-backup-pre-*` convention).

- Rollback = **revert the frontend commit + redeploy the prior bundle**:
  - homepage → generic-frame lead;
  - recap → `DetailShareRow`;
  - `ArtifactTacticalRoom` → no rescore CTA.
- **NO data migration to undo** because no backend / schema changed.
- **Guard changes revert independently** (stateless scanners).
- The runtime **daily-fixtures manifest is untouched**, so a UI rollback **cannot corrupt live
  data**. If a new artifact JSON misbehaves, **remove its import from `predictionArtifacts.ts`**
  and the loader falls back to the generic shell.
- **No-send posture is preserved throughout** — rollback never sends anything.

---

## 8. Explicit backend/schema statement

**NO backend or schema change is required for P6 P0.** P6 P0 is **copy / UI / artifact /
validator only**. The default and the decision: **NO backend route, NO DB table, NO schema
migration, NO change to the runtime daily-fixtures manifest shape.** Any growth runtime
expansion (Track B referral mechanics) stays **design-only** and is deferred to P1+ behind its
own Owner GO.
