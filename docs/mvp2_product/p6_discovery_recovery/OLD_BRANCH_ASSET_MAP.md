> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# OLD_BRANCH_ASSET_MAP — P6 Discovery / Recovery

## Overall finding

**CLEAR RECOVERY PATH.** The OLD product strength is NOT lost — it is on main but
under-surfaced. P1.1c (strongcopy @`0a73ee6`) made the product a single-source
**PROJECTION**: `frontend/src/growth/strongCallProjection.ts` (`buildStrongCall` /
`buildRecapCall`) parses the guard-passed LLM narrative ONCE (`splitScoreband`: first
score = 主比分, rest = 备选; `harmonizedRisk`: 风险偏高 + bare 中 → 中高) and every surface
(`/predict` StrongCallCard, `/share` cards, share copy, CLI) renders identical values —
eliminating predict/share drift.

The strongest OLD moments:

1. **StrongCallCard** = the condensed call (主看 → 主比分/备选 → 冷门风险 → 最大变量 → 为什么 →
   🌐 外部预期 → ⏱️ T-30 → calibration frame → dual CTA → ShareBlock) above the long
   tactical body.
2. The **RescoreBlock T-30 decision-rules ladder** (free 3 triggers + in-group locked
   triggers + 2 condition → new-call rules) = the conversion engine.
3. The **recap RECEIPT card** (结果 → 看对 → 偏离 → 校准 → 下一场).
4. The compliant **external-expectation projection** (外部预期 / 公开倾向, direction+band enum
   only, zero odds/prices/sources, enforced at frame → script (`SystemExit` pre-write
   FORBIDDEN check) → guard).
5. The **share-card + ref capture QR loop**.

The OLD p0-design growth INTENT (7 `GROWTH_P0_*` docs, on main verbatim) set the
compliance contract: channel-not-user attribution, verbatim-artifact-only fan copy,
no-auto-send, MTC-non-withdrawable, no-fake-recap (Card B = archived call vs honest
outcome = the anti-pick-selling differentiator). P1 runtime (growth tables/routes,
`/share` + `/join`, codes `QG-`/`TT-`/`FO-`, QR) deliberately escalated past P0's
"no per-user codes/QR" line — NOT a violation but the Owner-approved §4 escalation path;
the no-money / no-identity / no-auto-send floor is fully intact.

**Every OLD asset is ALREADY MERGED TO MAIN** (`git log main..strongcopy` is empty);
two files (`strongCallProjection.ts` +87, `check_growth_copy.py` +28) were extended FURTHER
on main (P5 artifact fallback) — **reuse main's version, never re-implement.**

P6 is a **copy/UI-first, frontend-only recovery**: surface StrongCallCard on a renderable
homepage lead, restore the rescore/calibration affordances + ShareBlock to all recap/predict
surfaces, de-hardcode `NEXT_HOOK`, complete the daily prediction/observation artifact schema,
and tighten the three guards to require a score-call hook — with **NO backend or schema change
required.**

---

## Asset map

Each row is a faithful rendering of `master.asset_map`. Branch annotations carry the blob
note where the JSON recorded one (every p0-design doc is also present on main with an
identical blob).

### A1 — p0-design growth intent (compliance & operator contract)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| feature/mvp2-growth-p0-design (now on main, identical blob c4ea799) | docs/mvp2_growth/GROWTH_P0_CHANNEL_TAGGING_DESIGN.md | Defined channel-level (not user-level) source tagging: a fixed 6-tag set recorded manually via queue `mark-sent --channel` + a hand-appended SEND_LOG.md; explicitly banned ?src/UTM/per-user codes/QR/shortlinks; weekly counts read manually from group UI. | Establishes the privacy-safe attribution ceiling (know the channel, never the person) that lets the trial measure reach without building tracking. The baseline P1's per-ref codes had to stay compatible with. | reuse — channel_tag concept lives on in `GrowthClick.channel_tag` (main); tag discipline still the operator record format. The "no per-user codes/QR" clause was deliberately superseded by Owner-approved P1. | P1 added per-ref codes (QG-/TT-/FO-) + QR, exceeding this doc's stated ceiling; reconciled only by compliance-note §4 (Owner may approve user-level). Stale if read as still-binding "no codes". |
| feature/mvp2-growth-p0-design (on main, blob 853997d) | docs/mvp2_growth/GROWTH_P0_COMPLIANCE_NOTE.md | Stated what P0 IS (manual screenshot-share of guarded surfaces) vs IS NOT (referral/attribution/reward/payment/automation), why Track B stays design-only, and the 6 conditions to unlock ANY runtime growth feature. | The governing compliance contract for all growth work; its §5 conditions are the exact gate Growth P1 had to pass (Owner GO on tables/routes, guard-first, MTC-only capped manual rewards, dedicated PR). | reuse — still the authoritative posture; conditions #1-#6 are the checklist that authorized P1 runtime and still bound first-send (Owner per-channel GO, no incident). | None to the posture itself. Risk is drift: P1 lifted condition #4 (channel ceiling) — must be read as Owner-amended, not violated. |
| feature/mvp2-growth-p0-design (on main, blob 4f45c02) | docs/mvp2_growth/GROWTH_P0_GROUP_CTA_COPY.md | Locked the rule that every fan-read string is a verbatim guard-passed LLM artifact or an Owner-approved fixed label (operator edits only the group-link placeholder), with per-surface CTA labels, group intro/T-30/recap copy sourced to artifact paths, fixed send-order, and a forbidden-copy list. | Prevents hand-written judgement copy from leaking into growth sends; the 赛前看方向/临场看变量/赛后看校准 loop framing is the product's core narrative hook. | reuse — verbatim-artifact rule + send-order + loop framing remain in force; P1.1c `strongCallProjection.ts` and the growth_packages send-kits are the runtime realization of this copy intent. | Quoted artifact paths/fixtures (1489371, 1489369) are fixture-specific; copy must be regenerated per fixture, not reused verbatim across matches. |
| feature/mvp2-growth-p0-design (on main, blob 8545420) | docs/mvp2_growth/GROWTH_P0_GUARD_SPEC.md | Specified the 5 forbidden wordlist categories × 4 languages for share/growth material plus the single sanctioned replacement vocabulary, with language nuances (my referee vs bookmaker, 提现 only in 不可提现). | The compliance wordlist that keeps growth material betting-free and process-leak-free across zh/vi/my/en; defines the future `check_growth_material.py` scanner scope. | reuse — these lists are the source for the live guard scanners (`check_mvp2_product_narrative_guard.py`, strongCallProjection guard); the betting/commission/process bans are enforced runtime. | §8 scanner (`check_growth_material.py`) was never implemented in P0; P1 sends still rely on existing scanner + operator eyeball checklist — an OCR-of-card gap remains open. |
| feature/mvp2-growth-p0-design (on main, blob ece9220) | docs/mvp2_growth/GROWTH_P0_MANUAL_INVITATION_FLOW.md | Specified the entirely-manual invite flow (Owner GO → screenshot live surface → paste card+copy+plain link by hand → mark-sent+log → fan joins untracked) with hard limits: no auto-attribution, no reward for joining/inviting, no wallet/commission, no per-user links/QR. | Guarantees the trial cannot accidentally become an incentive/referral machine; the manual paste + mark-sent + send-screenshot evidence chain is the operator audit trail. | reuse (flow) / partially superseded (limits) — manual paste + mark-sent + Owner-GO-per-channel SOP is still the send path; the "no per-user link/QR/reward" hard limits were Owner-lifted for P1 (codes + QR + MTC manual-grant contributions now exist). | Reading this doc's hard limits as current would contradict shipped P1 runtime; it is the pre-P1 baseline, not the current ceiling. |
| feature/mvp2-growth-p0-design (on main, blob d8d0b73) | docs/mvp2_growth/GROWTH_P0_OPERATOR_SOP.md | Single-page per-fixture send discipline: before-send gates (live scan PASS, pre-kickoff, queue=approved, verbatim copy, fresh card), Owner-GO-per-channel checklist, queue approve, manual paste, mark-sent+screenshot+log, T-30 match-day watch, recap follow-up into same channels. | The operational runbook that makes sends safe and auditable; the T-30 watch + "operator absent = nothing sends" rule is the no-auto-send guarantee. | reuse — directly fed `FIRST_SEND_RUNBOOK_1489371.md` + `GROWTH_P15_FIRST_SEND_GATE.md`; the 4 first-send gates (operator creates codes → smoke → match-day lifecycle → Owner per-channel GO) are this SOP operationalized. | References scope (zh internal/vi trusted/my 1 group) and 18/18 scan count that have since evolved (live scan now 21/21); counts are point-in-time. |
| feature/mvp2-growth-p0-design (on main, blob 4219b90) | docs/mvp2_growth/GROWTH_P0_SHARE_CARD_DESIGN.md | Designed two share cards as SCREENSHOTS of live surfaces (no runtime): Card A pre-match StrongCallCard, Card B recap accountability card (archived judgement vs honest outcome), with strict forbidden/allowed field lists and "disclaimer must stay in frame". | Defines the two highest-value growth artifacts; Card B (accountability = archived call vs real result) is the explicit differentiator from pick-selling accounts. | discard (the screenshot-only mechanism) / reuse (the card content spec) — P1.1 shipped runtime `/share` routes + ShareBlock + QR, superseding the manual-screenshot approach; but the card structure, forbidden/allowed field lists, and the StrongCallCard/recap-card content map were carried into the runtime share surfaces. | The doc's "NO runtime, no share button, no QR" premise is now false on main; reusable only as the card content/compliance spec, not as the delivery mechanism. |

### A2 — strongcopy frontend (the projection keystone + product surfaces)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/growth/strongCallProjection.ts | Canonical single-source projection: `buildStrongCall` (pre-match) + `buildRecapCall` (post-match) parse the LLM narrative into ordered display fields — `splitScoreband` (first band score=主比分, rest=备选), `harmonizedRisk` (lean 风险偏高 + bare 中 label → 中高), top_variable, why=hero_subtitle, external_expectation merge, T-30/CTA/calibration/next-hook constants. | THE architectural keystone: every surface (`/predict` StrongCallCard, `/share` cards, share copy, CLI mirror) renders identical values — no storyline drift. Turns a vague 3-score band into a confident headline 主比分 + 备选, and a long risk sentence into a harmonized 中高 label, without inventing any judgement. | reuse | `NEXT_HOOK` is HARDCODED to "Brazil vs Morocco" and T30/CTA/CALIBRATION are per-lang static strings — must de-hardcode the next-fixture pointer on recovery (Brazil-Morocco is now past). Returns null for finished/missing narrative, so depends on upcomingFixtures + narrative being present. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/components/StrongSignalCard.tsx | The ⚡强判断 StrongCallCard: lean → 主比分+备选 split → 冷门风险 → 最大变量 → 为什么 → 🌐外部预期 lines → ⏱️T-30 hook → calibration frame → dual CTA (scroll to T-30 re-score / join group) → embedded ShareBlock. | The single strongest condensed product moment: one card delivers the call, the confidence (main+backup scores), the risk, the why, the public-consensus contrast, the conversion hook, and share — all above the long tactical body. This is the "recover this first" artifact. | reuse | Tightly coupled to `buildStrongCall` + ShareBlock + `.sc-*` CSS + `#live30` anchor; zh/vi/my only (en→null). Needs the projection + an external-signal JSON for the 外部预期 block to appear. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/components/ProductProofViews.tsx | `ProductPredictView` (tactical-room body: PRE-MATCH READ → Lean/参考区间/Risk cards → tactical_read → KEY FACTORS top-3+fold → RescoreBlock → FREE VS FULL tiers + subscription_hook → InternalFold) and `RescoreBlock` (T-30 engine: free 3 triggers + locked subscriber triggers + 5 group Qs + 2 decision rules + join CTA). Also `ProductRecapView`. | Full tactical depth + the T-30 conversion ladder (free direction → in-group live re-score). The decision-rules block (condition → new lean/risk/score) is a distinctive, defensible product mechanic. | reuse | Large multi-purpose file (predict+recap+rescore+internal fold). InternalFold dumps operator_copy/social_post/source_ref_map — keep behind `?ops=1` only. `riskClass` color heuristic relies on zh/vi/en keyword regex. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/growth/shareTemplates.ts | Assembles STRONG-RESULT-FIRST share copy (prematch/recap/join/next-fixture) from the projection + Owner framing, with per-lang labels and ref-appended links. | Makes the share message a faithful projection of the product call (result first, then scores/risk/why/T-30/CTA) — not a separate marketing voice. Guard-clean, no betting words. | reuse | Inline per-lang label literals (head/leanL/scoreL…) duplicate StrongCallCard labels; a future label change must touch both. DEFAULT_REF codes are operator-specific. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/pages/ShareCardPage.tsx | Screenshot-friendly branded `/share` card with QR to `/join?ref=`, rendering the same `buildStrongCall`/`buildRecapCall` projection (scoreband, risk, top variable, first external line, T-30, calibration frame, disclaimer). | The viral artifact — a self-contained, screenshot-shareable card carrying the call + QR attribution. Strong moment for organic spread. | reuse | Depends on qrcode lib + `.shc-*` CSS + a fixture/narrative. QR/ref only meaningful once operator codes exist. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/data/externalSignalData.ts | Loads customer-safe external-expectation/public-consensus lines projected (by script) from an internal signal frame; en→null. | Distinctive differentiator: shows "what the public/outside expects" contrasted with the model call, in compliant vocabulary (no odds/sources/prices, conditional-on-XI). Powers the 🌐 block on card + share + share-card. | reuse | Only 1489371 has data; every new fixture needs a re-run of `mvp2_project_external_signals.py`. If absent, the 外部预期 block silently disappears. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/pages/RecapDetailPage.tsx | Leads the recap page with a canonical RECEIPT card (结果 → 赛前看对了什么 → 比分为什么偏离 → 校准 → 下一场) from `buildRecapCall`, above `ProductRecapView`; redirect target when a pre-match fixture finishes. | The accountability payoff — closes the loop 赛前看方向/临场看变量/赛后看校准 with a tight receipt, the trust-building heart of the product. | reuse | Receipt only renders for `mode==real_recap` with `validated_factors` present; falls through to deprecated hand-written recapData (855737) otherwise. No fabricated recap (good). |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/data/rescoreData.ts | T-30 re-score model layer (triggers + decision rules + teaser/hook) consumed by RescoreBlock. | The "why join the group" engine — free shows direction + 3 variables, group shows the live 30-min re-score. The condition→new-call rules are a concrete, repeatable hook. | reuse | Per-fixture LLM JSON; only 1489369/1489371 exist (both past). Needs regen per new fixture. |

### A3 — strongcopy external-signal layer + guards

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| feature/mvp2-growth-p1-1c-strongcopy | docs/MVP2_EXTERNAL_EXPECTATION_SIGNALS_DESIGN.md | Design spec for an INTERNAL-only external-expectation signal layer: 8 signals, hard policy table (allowed vs forbidden), stub frame schema, market consensus recorded as direction+band enum only. | Lets the persona's lean/recap reference "what media/experts/crowd price in" (热度集中在热门方/冷门变量被低估) as a model input without ever exposing odds — sharpens the football-intelligence read. | reuse | Low. Policy is compliance-clean; identical copy already on main. Risk only if a future engineer mistakes the internal frame for a customer surface — design explicitly forbids bundling it. |
| feature/mvp2-growth-p1-1c-strongcopy | scripts/mvp2_project_external_signals.py | Reads internal signal frame → emits bundled customer-safe projection JSON; enum→fixed-vocab mapping; defensive FORBIDDEN-word check (betting + source/player names) raises before write. | The compliance firewall that turns raw odds/rumor intelligence into the 4 customer-safe expectation lines shown on the strong-call card. | reuse | Medium. NOT generalized: expert_consensus/media_heat/lineup lines + TEAMS dict are hardcoded for 1489371 only — a new fixture requires editing the script. Also the projected lines are engineering-authored prose with mild analytical content (e.g. 防守韧性不能低估), which sits in tension with the "no engineering string-concatenated football analysis / LLM owns judgement" rule the module comment claims to honor. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/data/externalSignals/1489371.json + externalSignalData.ts | Bundled projection (4 lines × zh/vi/my, label, en→null) + typed loader consumed by the strong-call card. | The only external-expectation block actually rendered to customers; clean i18n with vi/my never falling back to zh. | reuse | Low. Only 1489371 populated; all other fixtures render nothing (graceful null). No prices/sources leak. |
| feature/mvp2-growth-p1-1c-strongcopy | frontend/src/growth/strongCallProjection.ts | Canonical single-source strong-call projection: merges LLM narrative + external_expectation + deterministic risk/score harmonization for predict/share/home/copy/CLI. | Guarantees every surface shows identical judgement (no share-vs-predict drift) and folds external signals into the strong call. | reuse | Low/uncertain. Main already carries a NEWER version (P5 prediction-artifact fallback added). Reuse the main version, not the branch snapshot — the branch copy is stale (87-line diff). |
| feature/mvp2-growth-p1-1c-strongcopy | scripts/check_growth_copy.py | Guard scanning growth surfaces (incl. externalSignals/*.json) for betting/guarantee/money/hierarchy/leakage vocab in 4 langs; 提现 negation exemption; selftest. | Automated compliance gate that blocks build/share if any forbidden word reaches the projected copy. | reuse | Low/uncertain. Main already carries a NEWER version (P1.2/P1.3/P5 globs added). Use main's; branch copy is stale (28-line diff). |

### A4 — main homepage (the under-surfaced funnel)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| main | frontend/src/components/HomeProductLoop.tsx | Renders the live homepage funnel: HotspotPrediction (lead) → HotspotRecap → SecondarySchedule → OtherRecaps → GrowthConversion, driven by `selectProductLoop` slate order. Copy is L{zh,vi,my,en}. | This IS the current today-hotspot funnel entrance. Correctly never shows fake recap, never exposes generation state, compliance-clean. | reuse — this is the surface to upgrade; the lead card is where a score-call hook would be added | Lead card is title + generic question-bullets only; high word count, low information scent; no concrete pull into the tactical room. |
| main | frontend/src/components/StrongSignalCard.tsx + frontend/src/growth/strongCallProjection.ts | StrongCallCard + `buildStrongCall` produce the canonical score-call hook (lean / primary score / backup / upset risk / top variable / why / T-30) identical to `/share` and CLI packages. | Exactly the "main score / strong call above the fold" hook the homepage is missing. Already trusted/guarded and reused across predict+share. | reuse — candidate to surface on the homepage lead when the featured prediction is renderable (has a bundled narrative) | Returns null for manual id=null fixtures (today's Netherlands–Japan lead) → needs a renderable featured prediction in the manifest; P1.5a intentionally cut strong calls from the landing, so re-adding needs Owner sign-off. |
| main | frontend/src/data/dailyFixtures.ts (selectProductLoop) | Editorial slate-order selection: featuredPrediction = first SCHEDULED, featuredRecap = first FINISHED; rest = secondary. | Operator/LLM control the hotspot via slate order with no hardcoded ranking; clean separation of stage vs content. | reuse — selection logic is sound | Will happily promote a non-renderable manual fixture (id=null) to the lead, guaranteeing a frame-only card with no call; nothing forces the lead to be a fixture that can carry a real prediction/score-call. |
| main | frontend/src/components/MatchDesk.tsx | P1.4 RecapDesk/UpcomingNeedsNarrative/OperatorStatusLine orchestration components. | Holds the P1.5b "one featured recap + one featured pre-match, rest lightweight" policy comment, but renders nothing now. | discard — dead code, superseded by HomeProductLoop; not imported anywhere | Stale/confusing: looks like live homepage orchestration but is unused; candidate for deletion. |
| main | scripts/check_homepage_product_loop.py | Source+manifest guard for the loop (13 checks): zone titles, order, recap gating, no betting, no generation wording, P3 order, tactical CTA + CopyLink, featured teams. | Locks loop structure, P3 order, no-fake-recap, compliance; passes pre-deploy. | reuse — keep as the structural guard | Blind spot: asserts only a TITLE + CTA + share exist on the lead; does NOT require any score-call / lean / win-prob hook, so the weak-hook gap passes green. |

### A5 — main predict (StrongCallCard path + artifact tactical room)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| main | frontend/src/components/ArtifactTacticalRoom.tsx | Rich strong tactical room for manual hotspots (no LLM narrative): strong-call card + modeling/matchup/risk lists + 30-min checklist + ShareBlock, via canonical projection. | This is the surface today's `/predict` main hotspot (NL vs JP) actually renders; carries the strong-call expression for fixtures that have no bundled LLM narrative. | reuse | Strong-call content is operator hand-filled JSON, not LLM-generated — a deliberate exception to the LLM-owns-narrative rule; omits the old card's calibration frame line + rescore CTA button row / `#live30` anchor. |
| main | frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json | Operator-confirmed pre-match artifact (NL vs JP, lean NL, 2-1, backup 1-1/2-2, risk 中高) feeding the room in 4 langs. | The data that makes today's predict page "strong" instead of a weak pending shell. | reuse | Hand-authored qualitative call (source=operator_confirmed), not pipeline/LLM; confidence intentionally null; must stay safe-vocab + Han=0 vi/my or guard fails. |
| main | frontend/src/growth/strongCallProjection.ts | Canonical StrongCall projection; `buildStrongCallFromArtifact` maps artifact → same shape as narrative StrongCallCard. | Guarantees artifact path and narrative path render identical strong-call labels/values/styling. | reuse | Artifact branch skips external-signal merge and scoreband-from-narrative parsing; depends on operator JSON quality. |
| main | frontend/src/data/predictionArtifacts.ts | Artifact + observation schema/loader; `getPredictionArtifact` by fixture_key/id. | Defines the strong-call field contract the guard enforces. | reuse | i18n en/zh fallback for vi/my locale slices; only one PREDICTION artifact bundled (netherJapan). |
| main | scripts/check_prediction_artifact.py | P5b guard: confirmed strong call (non-null zh direction/score/backup) + deviation (recap) + safe-vocab + source-wiring asserts. | Blocks regression to a weak pending shell and enforces strong labels present in the room. | reuse | Asserts exact zh tokens; tightly coupled to the single NL-Japan + 1489371 artifacts (hardcoded fixture_key/id/score). |

### A6 — main recap + share (trust receipt + share affordances)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| main | frontend/src/components/ObservationReceipt.tsx + frontend/src/data/predictionArtifacts/observation_1489371.json | Renders a full post-match TRUST RECEIPT from a recovered artifact (pre-match call → actual score → hit/partial/miss assessment → deviation → calibration points → next-match impact) when the full recap is not yet ready; recap_ready=false so it never fakes a recap. | This IS the trust-receipt experience the area is asking for, and it is the LIVE surface for the flagship fixture 1489371. Strongest receipt tier on main. | reuse — this is the canonical receipt component; extend its field set to the real_recap tier rather than rebuild. | DEFAULT_REF codes baked into shared links (QG-TEST1/TT-VN88/FO-MM21) are not yet created in prod per handoff (attached:false) — operational gate, not a code defect. |
| main | frontend/src/growth/strongCallProjection.ts (buildRecapCall + CALIBRATION_LINE/NEXT_HOOK) | Single canonical recap projection (result/what-was-right/why-deviated/calibration/next-hook) shared by the recap detail card, the share card, and share text. | Guarantees the receipt reads identically across page + share card + copy text (no divergent storyline). | reuse projection plumbing; but tighten content. | `NEXT_HOOK` is a HARDCODED "Brazil vs Morocco" constant and `CALIBRATION_LINE` is a fixed generic framing string — for any real_recap other than the current fixture the "next-match impact" and "calibration" lines go stale/wrong. `what_was_right` surfaces only ONE validated factor. |
| main | frontend/src/components/ShareBlock.tsx vs frontend/src/components/DetailShareRow.tsx | Two share rows: ShareBlock (link + share-text + share-card + join) used by ObservationReceipt; DetailShareRow (link + join only) used by the LLM real_recap recap page and predict pages. | Copy-link + join + ref preservation are universal; full share kit (text + card/QR) is available on the artifact receipt. | reuse ShareBlock as the single share row; the gap is that the real_recap tier does not use it. | GAP: real_recap recap detail (Tier 1) exposes NO copy-share-text button and NO share-card link on-page — users must already know the `/share/recap` URL. Inconsistent with the artifact receipt tier. |
| main | frontend/src/pages/ShareCardPage.tsx | Screenshot-friendly `/share/{fixture,recap}/:id` card with QR-to-join (ref-embedded), kickoff-freeze, and observation-receipt fallback. | The shareable visual receipt + ambassador QR; carries the ref through the scanned join URL. | reuse — already artifact-aware and ref-aware. | Reachable only if a surface links to it; the real_recap recap page does not, so this asset is under-exposed in Tier 1. |
| main | frontend/src/growth/refCapture.ts | App-wide first-touch `?ref=` capture (30-day localStorage) + join-intent beacon; ref injected into every shareLink/QR. | Ambassador (情报官) attribution survives share → visit → join across all recap/share surfaces. | reuse as-is. | Attribution only (Owner-by-design, no money fields); mock/offline silently skips beacons. |

### A7 — main daily flow (slate / editorial / artifact pipeline)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| main | scripts/mvp2_match_sync.py | `sync --date`: parses manual_scores_<date>.md → writes daily_fixtures_<date>.json (rich registry), recap_queue_<date>.json, dailyFixtures.generated.json, public/data/daily-fixtures.json; `upload` subcommand POSTs registry to backend admin endpoint (no rebuild needed). | The daily slate generator and the no-redeploy live-update path. Each fixture is lifecycle-evaluated; candidate flags (hero/next/recap) set deterministically. | reuse — this is the spine of the daily flow. Add an explicit editorial-selection input so the manifest override stops being a hand-edit. | Only 3 fixtures are KNOWN (id/kickoff); new fixtures get id=null/kickoff=null → can never be a renderable hero. A re-run wipes hand-edited renderable/hero flags. `upload` needs a prod token engineering does not hold (operator-only). |
| main | scripts/mvp2_editorial_agent.py | Builds a copy-paste LLM prompt (slate facts + product policy + current editorial line + safety) for DeepSeek/Gemini/Kimi; prints to stdout only. | The "selected hotspot" mechanism — Agent-led, operator-confirmed. Keeps editorial judgment in the LLM, not a hardcoded ranking engine. | reuse — but it is the weakest link: it persists nothing. The LLM recommendation and the operator decision are not saved as an artifact. | No output file → the daily selection is ephemeral (stdout + operator memory + hand-edited manifest). No traceable selected_hotspot_<date>.json. Re-deriving the slate overwrites the human decision. |
| main | scripts/mvp2_fixture_lifecycle.py | Canonical `decide()`/`gates()` state machine SCHEDULED..ARCHIVED; `run_status_refresh` writes fixture_lifecycle_<date>_<hhmm>.json. | Single source of truth for freshness — guarantees no finished/live match is shown as an active pre-match, no fake recap. | reuse — already consumed by match_sync, growth_cli, freshness.ts. | Tracked-fixture discovery falls back to a hardcoded ['1489369','1489371'] when no registry manifests are present. |
| main | scripts/mvp2_growth_cli.py | `refresh` assembles lifecycle-gated today/next/recap share packages from bundled narratives → growth_packages/*.md + refresh_summary_*.json; REFUSED stubs overwrite stale pre-match copy. | Daily operator send-kit generator, gated so a finished match can never emit a pre-match package; ref-coded links for growth attribution. | reuse — but only works for fixtures that already have a bundled narrative (1489369/1489371). | Strong-call assembly logic (scoreband split, 中高 harmonization, per-lang copy) is DUPLICATED between this CLI and `frontend/src/growth/strongCallProjection.ts` — drift risk. |
| main | frontend/src/data/predictionArtifacts.ts + predictionArtifacts/*.json | Loader + two hand-authored artifacts: manual_Nether-Japan (today's strong pre-match call) and observation_1489371 (Brazil post-match receipt). | The recovery layer that gives a manual daily hotspot (id=null, no narrative) real depth at `/predict`, and a tracked finished hotspot a receipt at `/recap` without a fake recap. | reuse the SHAPE; the per-day instances are one-offs that must be regenerated/hand-authored daily. | Hardcoded imports + bundled at build time → every new day's artifact needs a code edit to predictionArtifacts.ts AND a frontend redeploy. No generator script exists — purely hand-authored, trilingual+en. Validator path is also hardcoded to today's filenames. |
| main | frontend/src/growth/strongCallProjection.ts | Canonical `buildStrongCall` / `buildStrongCallFromArtifact` / `buildRecapCall` consumed by `/predict`, `/share` cards, homepage, CLI mirror. | One projection so every surface renders the same strong call; artifact fallback wired in when no bundled narrative exists. | reuse — this is the right seam to plug a per-fixture generated artifact into. | `buildRecapCall` requires `mode==real_recap`; with only observation receipts (recap_ready=false) the full-recap surface stays empty day-to-day. |
| main | frontend/src/components/HomeProductLoop.tsx | Renders Zone 2 featured prediction + Zone 3 featured recap + secondary schedule/recaps from `selectProductLoop`. | The closed-loop homepage (predict → track → recap → next). | reuse, but the featured-prediction CARD is generic boilerplate — the depth is one click away at `/predict`. | HotspotPrediction shows static {home}/{away} placeholder bullets, NOT the artifact's real score_call/top_variable. A reader who never clicks `/predict` never sees the strong call. Rich content is effectively buried. |
| main | scripts/mvp2_project_external_signals.py + data/externalSignals | Projects internal signal frames → customer-safe externalSignals/{id}.json (外部预期/公开预测倾向/热度集中). | The compliant external-signal layer for the strong call. | reuse — but it is NOT run daily. | Frames exist only for 4 old fixtures (06-12); new daily hotspots have their external_expectation hand-typed into the artifact, bypassing this pipeline → no refresh, no provenance. |

### A8 — main operations + compliance (send discipline)

| Old branch | File/path | What it did | Product value | Reuse decision | Risk |
|---|---|---|---|---|---|
| main | docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md | Per-channel first-send runbook: send target table (channel/fixture/ref/lang/package/share-card URL/join link/screenshot dir), verbatim paste rule, PRE-SEND checklist, manual SEND step, POST-SEND mark-sent checklist, STOP conditions, vi/my later-each-own-GO note. | This IS the operator workflow to preserve verbatim in OPERATIONS_FLOW.md: what link to send, what copy, what card, what ref code, what NOT to send. | reuse | Fixture-specific (1489371) and now stale on the pre-match half — 1489371 finished; the structure is reusable but the live target must move to the next pre-match fixture/recap. |
| feature/mvp2-growth-p0-design | docs/mvp2_growth/GROWTH_P0_OPERATOR_SOP.md | Reusable per-fixture/per-channel SOP: 6 checklists + T-30 watch responsibility + A4 recap follow-up rule + screenshot-storage naming. | The non-fixture-specific operator discipline — Owner GO scope, queue-approve gate, manual paste, mark-sent, T-30/kickoff sweep, recap into same audience. | reuse | Lives on the p0-design branch (not main); must be quoted into the on-main operations doc since it is the canonical SOP referenced by the runbook. |
| feature/mvp2-growth-p0-design | docs/mvp2_growth/GROWTH_P0_GROUP_CTA_COPY.md | Stage-by-stage group message pack: on-product CTA labels, group intro (paste on join), T-30 reminder (A3-gated), post-recap follow-up, send-order, forbidden-in-all-group-copy list. | Answers "what to send into the group at each stage" incl. T-30 and after-FT messages, all sourced from guard-passed artifacts. | reuse | Design-only branch; copy examples are fixture-specific (1489371/1489369). Operators replace ONLY [群链接由运营填写]; hand-rewriting judgement is forbidden. |
| feature/mvp2-growth-p0-design | docs/mvp2_growth/GROWTH_P0_COMPLIANCE_NOTE.md | Declares what the growth layer IS/IS NOT and the 6 preconditions before any runtime growth feature; reaffirms MTC-only/no-cash/no-commission/no-betting floor. | The non-negotiable compliance frame for OPERATIONS_FLOW.md: manual-only, no auto-send, no referral/reward/payment runtime, Track B design-only. | reuse | Design-only branch; must be reflected on main's operations doc to keep the compliance frame visible. |
| main | scripts/check_growth_copy.py | Enforces forbidden-vocab compliance across all growth copy surfaces (5 classes, 4 languages) with a 提现-only-inside-不可提现 exemption. | The automated compliance gate that backs the "no betting/trading vocab" constraint; Gate 3 evidence. | reuse | Scanner only — does not stop a human pasting forbidden wording into a chat; the manual-paste verbatim rule is the real backstop. |
| main | scripts/mvp2_growth_cli.py | `package`/`refresh` subcommands assemble paste-ready md packages from bundled guard-passed LLM narratives; lifecycle gate refuses live/finished fixtures as pre-match and neutralizes stale package files. | The tool that produces the operator's send copy; encodes "no fabrication, judgement verbatim, only ORDER engineered, NOTHING sends". | reuse | Writes files only; relies on bundled narratives existing. Needs prod DB only for create-code/stats; package/refresh are file-only. |
| main | docs/data_audit/mvp2_growth_packages/recap_1489369_zh_QG-TEST1.md | Available Mexico 2-0 South Africa recap paste package (verbatim copy + 30s script). | The currently-AVAILABLE send package; shows the recap paste-copy shape and the queue-approval warning operators must clear first. | reuse | approval_status=guard_passed (NOT yet queue-approved) → must pass queue approve + Owner GO before any send. |

---

## Identified product elements (coverage checklist)

Each required element is confirmed covered by at least one asset-map row. Where the element
is a documented GAP on main (asset exists but is not surfaced), the "lives now" note records
where the canonical asset currently resides on main.

- [x] **homepage lead score hook** — the asset that produces it exists (StrongCallCard +
  `buildStrongCall`, A4 row 2 / A2). It is **NOT yet wired into the homepage lead** —
  P1.5a explicitly cut Strong Calls from the landing, so `HomeProductLoop.tsx` (A4 row 1 /
  A7) renders only a generic question-frame. **Lives now on main** in
  `frontend/src/components/StrongSignalCard.tsx` + `frontend/src/growth/strongCallProjection.ts`,
  wired to `/predict`, `/share`, recap and the tactical strip — the homepage is the single
  high-traffic surface missing it (the P6 recovery target).
- [x] **score-call display** (主比分 / 备选 split) — `splitScoreband` in
  `strongCallProjection.ts` (A2 / A3 / A5 / A7); rendered by StrongCallCard (A2) and
  ArtifactTacticalRoom (A5). The `sc-primary-score` marker is the canonical hook.
- [x] **strong call block** — StrongCallCard (A2, A4) and ArtifactTacticalRoom (A5) =
  ⚡强判断 condensed call; backed by `buildStrongCall` / `buildStrongCallFromArtifact`.
- [x] **risk/confidence section** — `harmonizedRisk` (风险偏高 + bare 中 → 中高) in
  `strongCallProjection.ts` + the 冷门风险 field on StrongCallCard/ArtifactTacticalRoom (A2,
  A5); confidence is intentionally `null` on operator-confirmed artifacts (A5 row 2,
  disclosed). Lean/risk cards also in `ProductProofViews.tsx` `LeanRiskCards` (A2).
- [x] **tactical analysis section** — `ProductPredictView` (PRE-MATCH READ / KEY FACTORS /
  tactical_read) in `ProductProofViews.tsx` (A2); ArtifactTacticalRoom modeling_focus /
  tactical_matchup / risk_variables lists (A5) — richer than the old StrongCallCard.
- [x] **external expectation / public consensus copy** — `externalSignalData.ts` +
  `externalSignals/1489371.json` (A2, A3, A7), projected by `mvp2_project_external_signals.py`
  (A3, A7); 🌐 外部预期·公开倾向 block; SAFE_EXT vocab, no odds/prices/sources.
- [x] **T-30 hook** — `T30_HOOK` constant in `strongCallProjection.ts` (A2) + the
  `RescoreBlock` decision-rules ladder in `ProductProofViews.tsx` backed by `rescoreData.ts`
  (A2). Old card had the `#live30` scroll CTA (dropped on ArtifactTacticalRoom — P6 restore
  target).
- [x] **share / copy / share-card operations** — `ShareBlock.tsx` (link + text + card + join),
  `DetailShareRow.tsx` (link + join only — the documented asymmetry GAP), `ShareCardPage.tsx`
  (QR card), `shareTemplates.ts` (copy assembler), `CopyLink.tsx` (A2, A6, A8).
- [x] **recap receipt logic** — `RecapDetailPage.tsx` `buildRecapCall` receipt card (A2),
  `ObservationReceipt.tsx` + `observation_1489371.json` full trust receipt (A6),
  `ProductRecapView` depth (A2/A6). No fake recap (recap_ready=false honored).
- [x] **growth / ref / join flow** — `refCapture.ts` first-touch ?ref= + recordJoinIntent
  (A6); the p0-design intent docs (A1: channel tagging, manual invitation flow, operator SOP);
  P1 runtime tables/routes referenced in the overall finding; DEFAULT_REF codes
  QG-TEST1/TT-VN88/FO-MM21.
- [x] **guards** — `check_growth_copy.py` (A3, A8), `check_homepage_product_loop.py` (A4,
  with the documented score-call blind spot), `check_prediction_artifact.py` (A5, P5b
  confirmed-strong-call + deviation rule), plus the `GROWTH_P0_GUARD_SPEC.md` wordlist source
  (A1) and the `mvp2_project_external_signals.py` pre-write FORBIDDEN `SystemExit` check (A3).

---

## Cross-cutting notes for P6

- **Do not re-implement the projection.** `strongCallProjection.ts` and `check_growth_copy.py`
  were extended FURTHER on main (P5 artifact fallback: +87 and +28 lines respectively over the
  strongcopy branch). Always reuse main's version; the `feature/mvp2-growth-p1-1c-strongcopy`
  snapshots are stale.
- **Everything is already merged.** `git log main..feature/mvp2-growth-p1-1c-strongcopy` is
  empty — there is nothing to cherry-pick; P6 is surfacing/wiring + de-hardcoding, not porting.
- **De-hardcode `NEXT_HOOK`.** The literal "Brazil vs Morocco" + the per-lang `CALIBRATION_LINE`
  constants in `strongCallProjection.ts` go stale for any recap other than the current fixture
  (Brazil–Morocco is now past). The `ObservationReceipt` match-specific `calibration_points` +
  `next_impact` are the better pattern to propagate up to the real_recap tier.
- **Two genuine drops vs the old StrongCallCard** (CTA/styling, not strong-call substance):
  (1) the calibration frame line 赛前看方向，临场看变量，赛后看校准; (2) the `#live30` rescore-scroll
  CTA + the in-page RescoreBlock ladder — both absent from `ArtifactTacticalRoom.tsx`.
- **Share affordance asymmetry** is the actionable share gap: wire the real_recap recap page +
  predict pages to `ShareBlock` (or add 📋 copy-text + 🖼️ share-card buttons to
  `DetailShareRow`).
- **Dead code:** `MatchDesk.tsx` (P1.4 orchestration) is no longer imported — discard candidate.
- **Daily-flow fragility:** the editorial selection persists nothing (stdout-only
  `mvp2_editorial_agent.py`); manifest hero/renderable hand-edits are wiped by any re-sync;
  per-fixture strong-call depth is hand-authored with no generator (does not scale past ~1
  fixture/day). A persisted `selected_hotspot_<date>.json` + a per-day artifact scaffolder are
  the recommended (script/docs-only) additions.
- **Compliance floor intact throughout:** no auto-send, no betting/odds vocab (even negated),
  MTC = 平台积分 不可提现/不可转让/不可交易, no fake recap, mandatory disclaimer in-frame. All P6
  recovery work is frontend/copy/UI + validator-only — **NO backend route, NO DB table, NO
  schema migration.**
