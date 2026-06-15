> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# P6 Discovery — READ LOG

This log records every file inspected during P6 discovery, grouped by branch. Each entry follows the exact format: Branch / File / Reason for reading / Key finding / Reuse-discard-uncertain. All 91 read entries from the discovery are rendered below, including repeat reads of the same file under different analysis areas (A1–A8); no entry is merged or dropped. Area headers are navigation only.

---

## feature/mvp2-growth-p0-design

### A1 — p0-design intent

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_CHANNEL_TAGGING_DESIGN.md
Reason for reading: channel/ref tagging intent
Key finding: Intent = know CHANNEL not USER. Fixed 6-tag set (telegram_group_1, zalo_test_group, telegram_vi_trusted, zh_internal_group, facebook_dm, operator_manual). Recorded manually via queue mark-sent --channel + a hand-appended SEND_LOG.md. EXPLICITLY no ?src=/UTM/per-user codes/QR/shortlinks; joins counted manually as group member delta. Zero runtime.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_COMPLIANCE_NOTE.md
Reason for reading: compliance posture / gate to any runtime
Key finding: Defines P0 as manual screenshot-share of already-guarded surfaces, NOT referral/attribution/reward/payment/automation. §5 lists the 6 CONDITIONS to unlock ANY runtime growth: (1) >=1 full fixture cycle feedback no incident, (2) Owner GO on a written runtime design naming exact tables/routes, (3) guard implemented FIRST, (4) channel-level attribution is the CEILING unless Owner explicitly approves user-level, (5) rewards MTC-only non-withdrawable/manual/capped, (6) dedicated PR branch. This doc is the contract P1 had to satisfy.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_GROUP_CTA_COPY.md
Reason for reading: group CTA copy intent
Key finding: Every fan-read string must come from a guard-passed LLM artifact (quoted with source path) or an Owner-approved fixed label; operators replace ONLY [群链接由运营填写], sha256 tamper-reject backstop. Send-order: pre-match→T-30 reminder(A3-gated)→kickoff STOP→FT recap follow-up+next hook. Loop framing fixed label: 赛前看方向，临场看变量，赛后看校准. §6 forbids betting/odds (even negated), win-guarantees, reward-for-invite, 提现/commission, fabricated urgency, links inside LLM prose.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_GUARD_SPEC.md
Reason for reading: guard wordlist spec
Key finding: 5 forbidden categories x 4 langs (betting/odds; win-guarantee; commission/reward/recharge; agent/proxy hierarchy; process/audit-leakage incl 模型/AI/sha256/artifact/guard/mock). §6 = the ONLY sanctioned replacement vocabulary (俅哥判断/赛前参考区间/冷门风险/临场变量/外部预期/市场共识). Notes my ဒိုင်=referee allowed but လောင်းဒိုင်=bookmaker banned; 提现 only in 不可提现. §8 future check_growth_material.py deferred (P0 = checklist only).
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_MANUAL_INVITATION_FLOW.md
Reason for reading: manual invitation flow intent
Key finding: Flow = Owner GO (per fixture per channel) → operator picks card+verbatim copy → screenshots LIVE surface → pastes card+copy+plain group link by hand → queue mark-sent + log + send screenshot → fan joins via plain invite (no tracking). Hard limits: NO auto-attribution, NO reward for joining/inviting (no MTC/unlock/badge in P0), NO wallet/commission/recharge, NO per-user links or QR (P0 link = one plain group invite per channel).
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_OPERATOR_SOP.md
Reason for reading: operator SOP intent
Key finding: Single-page per-fixture discipline: BEFORE-SEND (live scan PASS on current deploy, pre-kickoff, queue=approved not guard_passed, copy verbatim, fresh card w/ persona+disclaimer) → Owner GO checklist (fixture+channels named, scope unchanged zh internal/vi trusted/my 1 group, GO ref in SEND_LOG) → queue approve → manual paste (no bots/schedulers/bulk) → mark-sent+screenshot+log. §7 T-30 watch (operator at keyboard T-2h; T-12 no new gen; absent=nothing sends). §8 recap follow-up into SAME channels.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_SHARE_CARD_DESIGN.md
Reason for reading: share-card design intent
Key finding: Cards = SCREENSHOTS of existing live surfaces, NO runtime (no share button, no generator endpoint, no QR). Card A = 1489371 pre-match StrongCallCard (brand row/fixture/俅哥主看 main_lean/参考比分/冷门风险/最大变量/外部预期/hook+CTA/disclaimer MUST stay in frame). Card B = 1489369 recap trust card (archived judgement vs honest 2-0 outcome = accountability proof vs pick-selling). §4-§5 forbidden/allowed field lists; link pasted OUTSIDE image, no QR.
Reuse / discard / uncertain: discard
---

### A8 — operations + compliance (p0-design canonical, not on main)

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_OPERATOR_SOP.md
Reason for reading: Single-page per-fixture operator SOP (the discipline layer)
Key finding: 6 checklists: BEFORE-SEND, OWNER-GO (per fixture+channel, scope=zh internal/vi trusted Telegram/my 1 test group), QUEUE-APPROVE (status must=approved), MANUAL-PASTE, MARK-SENT, SCREENSHOT-STORAGE; T-30 watch (operator at keyboard T-2h, T-12 no new gen, kickoff=queue sweep, operator absent=nothing sends); A4 recap follow-up into SAME channels.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_COMPLIANCE_NOTE.md
Reason for reading: Defines what Growth P0 IS/IS NOT + compliance floor rationale
Key finding: P0 = manual operator-executed sharing of already-guarded surfaces; NOT a referral/attribution/reward/payment/automation system; no message generated/scheduled/sent by software; Track B (referral mechanics) stays DESIGN-ONLY; 6 conditions before any runtime growth feature; rewards if ever = MTC-only 不可提现/不可转让/不可交易, manual, capped, never cash/commission/betting-tied.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p0-design
File: docs/mvp2_growth/GROWTH_P0_GROUP_CTA_COPY.md
Reason for reading: Group CTA copy pack — what to send at each stage into the group
Key finding: On-product CTA labels (加入情报群/进群看完整版/看俅哥怎么校准); group intro msg (paste once on join, from LLM group_join_copy); T-30 reminder (send ONLY after A3 guard_passed+approve+Owner GO); post-recap follow-up; send-order = pre-match→T-30(A3-gated)→kickoff STOP→FT+recap follow-up+next hook; §6 forbidden-in-all-group-copy list.
Reuse / discard / uncertain: reuse
---

## feature/mvp2-growth-p1-1c-strongcopy

### A2 — strongcopy frontend

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/growth/strongCallProjection.ts
Reason for reading: Named canonical projection — the keystone the whole area orbits
Key finding: buildStrongCall()/buildRecapCall() are THE single source: parse scoreband (splitScoreband: first score=主比分, rest=备选), harmonize risk (harmonizedRisk: lean says 风险偏高 + label bare 中 -> display 中高, deterministic merge of two model statements, not a new judgement), order fields. Every judgement string stays a guard-passed LLM narrative field; module only parses/merges/orders. Per-lang Owner framing constants (T30_HOOK/CTA_LINE/CALIBRATION_LINE/NEXT_HOOK) live here hardcoded.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/growth/shareTemplates.ts
Reason for reading: Share-copy assembler — proves 'share = projection of main product'
Key finding: prematchShareCopy STRONG-RESULT-FIRST order (1 result->2 主比分/备选->3 risk->4 why->5 T-30->6 CTA), all from buildStrongCall; recapShareCopy from buildRecapCall (recap line = LLM screenshot_line verbatim); joinShareCopy + nextFixtureCopy. refFor() uses stored ref else per-lang operator default (QG-TEST1/TT-VN88/FO-MM21). No betting/odds words; ref appended to every shareLink.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/components/StrongSignalCard.tsx
Reason for reading: The strong-call block UI (StrongCallCard) on the predict page
Key finding: Renders buildStrongCall: ⚡强判断 kicker -> 俅哥主看(lean) -> 主比分 sc-primary-score + 备选 split -> 冷门风险 -> 最大变量 -> 为什么 -> 🌐外部预期·公开倾向 lines -> ⏱️T-30 hook -> calibration frame -> dual CTA (scroll to #live30 re-score / nav /community) -> embedded ShareBlock. Labels are stage chrome; all values are projected. zh/vi/my only, en->null.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/components/ShareBlock.tsx
Reason for reading: Lightweight share buttons reused under StrongCallCard + recap
Key finding: 4 mini buttons: 复制情报链(link) / 复制分享文案(prematch|recap|join copy) / 查看分享卡(nav /share/...?ref=) / 加入情报群(recordJoinIntent + nav /join). clipboard with execCommand fallback for http. No QR here (QR lives on /share/* + admin).
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/pages/PredictPage.tsx
Reason for reading: The strongcopy tactical-room page shell
Key finding: /predict/:slug. isReal = fixture_basis real_scheduled || has upcoming fixture -> renders StrongCallCard ABOVE ProductPredictView. Post-match guard: if narrative mode==real_recap, redirect to /recap/:id (pre-match room is over, no fake pre-match). fixture meta card (kickoff/venue/round). ?ops=1 opens internal fold. en = neutral none-state.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/components/ProductProofViews.tsx
Reason for reading: ProductPredictView + RescoreBlock = the full tactical-room body + T-30 layer
Key finding: ProductPredictView: hero -> PRE-MATCH READ (model_judgement) -> LeanRiskCards (lean/参考区间+参考 chip/risk pill w/ riskClass color) -> tactical_read card -> KEY FACTORS top-3 + more-fold -> #live30 RescoreBlock OR watch_next fallback -> FREE VS FULL tier card (freeItems/fullItems + subscription_hook + group_join_copy + dual CTA) -> InternalFold (ops-only). RescoreBlock = T-30 engine: 现在怎么看 teaser, free 3 triggers (name/status/free_copy/possible_impact), locked subscriber triggers + 5 group questions + 2 decision rules + group_join_hook CTA. Also ProductRecapView (结果->validated->underweighted->decisive->evidence->watch-next) + MoreAndtoday.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/pages/ShareCardPage.tsx
Reason for reading: Screenshot/QR share card — the viral artifact
Key finding: /share/fixture|recap/:id. Renders buildStrongCall (pre) or buildRecapCall (recap) into a branded card: Giành Cup·persona, kicker, teams, lean, scoreband (shc-primary + 备选 alts), risk, top variable, first external_expectation line, ⏱️T-30 hook, QR to /join?ref=CODE (qrcode lib, 132px), scan CTA, calibration frame, disclaimer. ref from ?ref= upcased else DEFAULT_REF. QR allowed here by Owner rule (share route, not match page).
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/pages/RecapDetailPage.tsx
Reason for reading: Recap receipt logic — the accountability payoff surface
Key finding: Preferred branch: getProductNarrative mode historical_recap|real_recap. For real_recap, leads with a canonical recap RECEIPT card from buildRecapCall: 结果(result_title) -> 赛前看对了什么(what_was_right) -> 比分为什么偏离(why_deviated) -> 校准 frame -> 下一场 hook (blueMid), then ProductRecapView. Falls back to LLM NarrativeView, then deterministic hand-written recapData. EVIDENCE_AVAILABLE -> /evidence link.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/externalSignalData.ts
Reason for reading: External-expectation / public-consensus projection loader
Key finding: getExternalSignals(id,loc) returns customer-safe {label,lines} from bundled per-fixture JSON, generated by scripts/mvp2_project_external_signals.py from INTERNAL signal frame (never bundled). Owner-approved customer-safe vocabulary only (外部预期/公开倾向); NO sources/prices/odds/betting; rumors only as conditional '锋线核心 pending official XI'. en->null (internal layer). Only 1489371 wired.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/externalSignals/1489371.json
Reason for reading: The only external-signal data instance — shows the actual customer copy
Key finding: 4 zh/vi/my lines per fixture: '外部预期偏向巴西' / '公开预测更看好巴西，但摩洛哥防守韧性不能低估' / '热度集中在巴西锋线核心和新帅首秀；摩洛哥教练变化是风险变量' / '如果巴西锋线核心不进首发，进球参考区间需要下调——以官方首发为准'. Customer-safe, conditional-on-XI, no odds. Single-fixture only.
Reuse / discard / uncertain: uncertain
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/productNarrativeData.ts
Reason for reading: Narrative loader + v2 ProductNarrative contract that every projection consumes
Key finding: getProductNarrative(id,loc). Contract fields the projection reads: main_lean, scoreline_view, risk_level, hero_subtitle, watch_next_signals[], risk_factors[], validated_factors[], short_title, screenshot_line, tactical_read, model_judgement, mode (pre_match_2026_modeling|historical_recap|real_recap), fixture_basis. JSON regenerated by script + guard, never hand-edited; bundled at build (frontend never calls LLM/vendor). zh/vi/my wired for 1489369/1489371/855737/979139; 2026 sample zh/vi.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/productNarratives/1489371.zh-CN.json
Reason for reading: Sample to confirm what real LLM content backs each projected field
Key finding: main_lean='赛前倾向巴西胜，但冷门风险偏高'; scoreline_view='俅哥给出的赛前参考区间：2-1、1-1、2-2' (splitScoreband -> 主比分 2-1 / 备选 1-1,2-2); risk_level='中——巴西纸面强...' (harmonized -> 中高); hero_subtitle='巴西Elo领先65分、近10场6胜，但摩洛哥7场不败+7场零封——不是强弱对话，是效率对决'; watch_next[0]='首发11人（开球前30分钟）'. Factors carry source_refs + assumption_flag (kaggle derived vs api-football assumption). tactical_read present. Fixture is now PAST (06-13).
Reuse / discard / uncertain: uncertain
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/recapData.ts
Reason for reading: Hand-written deterministic recap fallback (pre-LLM voice)
Key finding: RecapContent for 855737 only (zh/vi/en, no my). This is the DEPRECATED hand-written voice that LLM narrative replaced — used only when no productNarrative/narrative exists. Carries 模型校准 badge + MISS verdict + source ledger. Lower product value than projection path.
Reuse / discard / uncertain: discard
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/upcomingFixtures.ts
Reason for reading: Fixture facts that back teams/kickoff/venue + drive isReal
Key finding: Only 1489369 (Mexico-S.Africa 06-11) + 1489371 (Brazil-Morocco 06-13) — BOTH now past (today 06-14). getUpcomingFixture drives StrongCallCard rendering; if fixture missing AND narrative missing, buildStrongCall returns null. Hard static list, no runtime source on this branch.
Reuse / discard / uncertain: uncertain
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/growth/refCapture.ts
Reason for reading: Ref-capture backing share attribution (recap/share receipt growth loop)
Key finding: captureRef first-touch wins, localStorage 30d, CODE_RE /^(QG|TT|FO)-[A-Z0-9]{4,6}$/. Posts only {ref,surface,lang,device_class} — NO identity. recordJoinIntent on group CTA. Mock/offline silently skipped, never blocks UI.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/rescoreData.ts
Reason for reading: T-30 re-score model layer backing the live30 hook
Key finding: getRescore(id,loc) -> RescoreModel (pre_match_lean, score_range_before, rescore_triggers[name/current_status/free_copy/subscriber_copy/possible_impact], rescore_decision_rules[condition->lean/risk/score], public_teaser, group_join_hook). LLM-written on engineering trigger skeleton, guard-gated, bundled. Wired for 1489369/1489371 zh/vi/my.
Reuse / discard / uncertain: reuse
---

### A3 — strongcopy external-signal + guards

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: docs/MVP2_EXTERNAL_EXPECTATION_SIGNALS_DESIGN.md
Reason for reading: Authoritative design for the external-expectation signal layer
Key finding: 8 signals recorded as INTERNAL model input only; market/odds = direction+band enum, NO prices/bookmaker names in frame value; customer-safe fixed vocab (外部预期/市场共识/公开预测倾向); guard bans betting vocab in zh/vi/my/en; manual operator recording w/ named sources, missing_evidence:true until recorded.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: scripts/mvp2_project_external_signals.py
Reason for reading: The enum→fixed-vocab projection from internal frame to bundled customer JSON
Key finding: Only recorded (missing_evidence=false) signals project; market_expectation enum→MARKET_LEAN side; defensive FORBIDDEN list (incl. odds/kèo/bookmaker AND player/source names neymar/espn/bein) raises SystemExit on any hit before write. BUT expert_consensus/media_heat/lineup lines are hardcoded literal strings for 1489371 (巴西/摩洛哥); TEAMS dict has only 1489371 — not generalized.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: docs/data_audit/mvp2_external_signals/1489371.external_signals.json
Reason for reading: Only fully-recorded signal frame (the real data sample)
Key finding: recorded_by=engineering via named-source web search; market_expectation=moderate_favourite_home (sources carry numeric odds 'deliberately not copied'); lineup/injury rumor = Neymar calf doubt status=rumor w/ assumption_flag; 4 of 8 signals recorded, social_buzz/public_prediction_bias still missing.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: docs/data_audit/mvp2_external_signals/{1489369,1539000,979139}.external_signals.json
Reason for reading: Verify other frames are empty stubs
Key finding: All 3 are empty stubs: recorded_by=null, every signal missing_evidence:true — confirms 'no half-records' rule and that only 1489371 projects.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/externalSignals/1489371.json
Reason for reading: The bundled customer-safe projection output
Key finding: 4 projected lines/lang (zh/vi/my), label '外部预期 · 公开倾向'; no sources/prices; rumor surfaces only as conditional '如果巴西锋线核心不进首发…以官方首发为准' — never confirmed absence.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/data/externalSignalData.ts
Reason for reading: Frontend loader for projection
Key finding: getExternalSignals(fixtureId,loc) returns {label,lines}; en→null (internal fallback layer, no surface); empty lines→null; comment forbids hand-editing JSON (re-run script).
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: frontend/src/growth/strongCallProjection.ts
Reason for reading: Canonical strong-call projection that consumes external signals
Key finding: buildStrongCall() merges LLM ProductNarrative + external_expectation (ext?.lines??[]) + T30/CTA into ONE StrongCall for predict/share/home/copy/CLI; harmonizedRisk (lean 偏高 + label 中→中高) and splitScoreband are deterministic parse/merge only, no new judgement. NOTE: main has SINCE extended this (P5 prediction-artifact fallback).
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: backend/app/models/prediction.py
Reason for reading: Check whether external signals live in the DB prediction model
Key finding: Prediction model has prob_home/draw/away, recommended_score, risk_level(low/med/high), confidence, free_note, risk_note, ai_provider — NO external-signal fields. External signals are entirely a FILE layer (internal data_audit frame + bundled projection JSON), decoupled from the DB.
Reuse / discard / uncertain: discard
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: scripts/check_growth_copy.py
Reason for reading: The guard protecting the projected copy
Key finding: Scans externalSignals/*.json + StrongSignalCard.tsx; 5 forbidden classes (betting/guarantee/money/hierarchy/leakage) in 4 langs; 提现 legal only inside 不可提现 (negation regex); strips code comments; selftest 6 cases. main has SINCE added P1.2/P1.3/P5 globs.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy
File: docs/MVP2_TRACKA_EVIDENCE_EXPANSION_REVIEW.md
Reason for reading: The sprint report documenting external signals + guard
Key finding: Confirms 8 signals all missing_evidence:true until operator records w/ named sources; internal-only direction+band, no prices/bookmaker names; guard adds external-expectation-claim-without-recorded-signal ban + handicap vocab (亚盘/让球盘/tài xỉu/chấp bóng/handicap); 'odds/market data is stub only — operator manual recording is the P0 path'.
Reuse / discard / uncertain: reuse
---

### A5 — strongcopy baseline (read at 0a73ee6 for gap-compare)

Branch: feature/mvp2-growth-p1-1c-strongcopy @ 0a73ee6
File: frontend/src/components/StrongSignalCard.tsx
Reason for reading: Baseline old-strength strong card to gap-compare
Key finding: Old StrongCallCard fields: kicker 俅哥强判断, 主看/主比分(+备选)/冷门风险/最大变量/为什么/外部预期/T-30 + frame line (赛前看方向，临场看变量，赛后看校准) + pp-cta-row (rescore-scroll-to-#live30 btn + join btn) + ShareBlock. Renders ONLY from a bundled LLM ProductNarrative via buildStrongCall.
Reuse / discard / uncertain: reuse
---

Branch: feature/mvp2-growth-p1-1c-strongcopy @ 0a73ee6
File: frontend/src/pages/PredictPage.tsx
Reason for reading: Confirm old predict had no artifact tier
Key finding: Old predict strong path = StrongCallCard + ProductPredictView ONLY (no getPredictionArtifact, no ArtifactTacticalRoom, no manual-hotspot fallback). Required a real_scheduled LLM narrative to be strong. Artifact tier is the P4/P5 net-new recovery layer.
Reuse / discard / uncertain: reuse
---

## current main (b9b362a)

### A1 — verify P1 runtime escalation (on main)

Branch: main
File: backend/app/models/growth.py
Reason for reading: verify whether P1 runtime escalated past P0 'NOT in P0' boundaries
Key finding: P1 ADDED 5 tables that P0 explicitly excluded: GrowthAmbassador (operator-issued codes QG-/TT-/FO-, no self-serve), GrowthClick (per-ref landing, but header comment: NO ip/raw UA/names/phones/emails/per-user identity columns), GrowthJoinIntent (confirm/reject manual review), GrowthContribution (MTC via existing wallet rails, token_log_id, pending|approved manual), GrowthAuditLog. Compliance preserved: no money/price/odds columns possible, MTC non-cash/non-withdrawable/non-transferable/non-tradable.
Reuse / discard / uncertain: reuse
---

Branch: main
File: backend/app/routers/growth.py
Reason for reading: confirm P1 endpoints escalated past P0 zero-runtime intent
Key finding: P1 ADDED public rate-limited /click + /join-intent (invalid refs counted not rejected) and x-admin-token admin CRUD (ambassadors create/patch, dashboard, intents confirm, contributions create/review, export). Same admin lock pattern as routers/admin.py (401 if ADMIN_API_TOKEN unset). This is the runtime P0 §3 said required its own Owner GO + guard-first; it landed via Growth P1 on a dedicated branch per compliance-note condition #6.
Reuse / discard / uncertain: reuse
---

### A4 — main homepage

Branch: main
File: frontend/src/components/HomeProductLoop.tsx
Reason for reading: Primary target — the rendered homepage funnel (P2/P3 loop)
Key finding: 6-zone loop. Render order = HotspotPrediction → HotspotRecap → SecondarySchedule → OtherRecaps → GrowthConversion. Lead prediction card = badge + teams + (kickoff) + 1 predWhy sentence + FocusBlock (title + 3 GENERIC question bullets + 30-min line) + 2 CTAs + CopyLink. NO score, NO win-prob, NO lean/pick, NO strong-call anywhere. recap CTA correctly gated on recapReady (no fake recap).
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/pages/HomePage.tsx
Reason for reading: Where the loop is mounted and what sits above/around it
Key finding: Above HomeProductLoop sit ~5 chrome blocks: ai-ticker, TrialStatusStrip, hero-banner (俅哥说球/GIÀNH CUP + 2 subtitles), cap-bar, balance/check-in strip, then daily-sync-line (⟳ 赛程更新…实时), THEN <HomeProductLoop/>. The ONLY score-call/win-prob hook (signal-card + WinBar + AI pick + confidence stars + top-risk) is mock and buried inside collapsed <details home-demo-fold> '内部演示数据' at L237-268. WC2022 archive also collapsed below the loop.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/MatchDesk.tsx
Reason for reading: Listed target — verify if it still drives the homepage
Key finding: DEAD CODE. RecapDesk/UpcomingNeedsNarrative/OperatorStatusLine (P1.4 orchestration) are NOT imported anywhere in frontend/src (grep clean). Superseded by HomeProductLoop in P2/P3. Contains the P1.5b 'one featured recap + one featured pre-match' policy comment, but is unused.
Reuse / discard / uncertain: discard
---

Branch: main
File: scripts/check_homepage_product_loop.py
Reason for reading: Listed target — what the guard actually asserts
Key finding: 13 checks, all PASS live. Asserts: zone titles present; selectProductLoop exists & order-driven (finished[0]/scheduled[0]); no generation wording; no 今日热点复盘 label; recap CTA gated on recapReady; no betting vocab; HomePage renders loop; P3 order (Prediction before Recap); lead has 进入战术室 + CopyLink; manifest output teams (Brazil/Morocco recap, Netherlands/Japan pred, Mexico secondary). Crucially asserts NOTHING about a score-call/strong-call/lean/win-prob hook — only that a TITLE + CTA + share exist.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/dailyFixtures.ts
Reason for reading: selectProductLoop editorial selection that picks the two featured slots
Key finding: featuredRecap = first FINISHED fixture, featuredPrediction = first SCHEDULED fixture (slate-order-driven, no team ranking). The featured prediction can be a manual id=null fixture with renderable=false (no narrative) → only a frame card is possible, not a real call.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/public/data/daily-fixtures.json
Reason for reading: Runtime manifest = the actual homepage OUTPUT today
Key finding: 7 fixtures (2026-06-14). Lead prediction = Netherlands vs Japan (id=null, manual, kickoffUtc=null, renderable=false → NO narrative, NO kickoff line). Lead recap = Brazil 1-1 Morocco (RECAP_PENDING, recapReady=false → shows 赛后校准中 + 查看赛后观察, NOT a real recap). The ONLY recap-READY item, Mexico 2-0 South Africa, is demoted to #4 其他复盘. So both featured slots are non-renderable/pending; the click-worthy real recap is below the fold.
Reuse / discard / uncertain: uncertain
---

Branch: main
File: frontend/src/components/StrongSignalCard.tsx
Reason for reading: The asset that produces a score-call hook — is it on the homepage?
Key finding: StrongCallCard renders exactly the missing hook: 主看(lean) + 主比分(primary_score) + 备选(backup) + 冷门风险 + 最大变量 + why + T-30. But it needs a ProductNarrative (bundled). It is wired into PredictPage/ShareCard/recap/tactical strip — NOT into HomeProductLoop. P1.5a explicitly 'cut Strong Calls' from the landing. With today's manual id=null lead it would return null anyway.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/growth/strongCallProjection.ts
Reason for reading: Canonical score-call projection backing the strong-call hook
Key finding: Confirmed present (7.5KB) and imported by 8 surfaces (predict/share/recap/tactical/upcoming) but NOT the homepage. buildStrongCall(fixture_id, loc) is the reusable bridge if a homepage score-call hook is wanted for a renderable lead.
Reuse / discard / uncertain: reuse
---

### A5 — main predict

Branch: main
File: frontend/src/pages/PredictPage.tsx
Reason for reading: Resolve which component renders the predict route and its branches
Key finding: Two strong-render paths: (1) fixture WITH bundled LLM ProductNarrative → StrongCallCard + ProductPredictView (lines 216-221, IDENTICAL to old strongcopy); (2) manual hotspot, no narrative (needsFallback) → getPredictionArtifact(slug) → ArtifactTacticalRoom (lines 147-161). Also a generic FALLBACK shell (lines 17-46) only when no artifact exists. P1.2b freeze gate (frozen, lines 113-144) hides stale pre-match after kickoff; real_recap redirects to /recap.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/ArtifactTacticalRoom.tsx
Reason for reading: The P5 rich tactical room for manual hotspots — the surface in question
Key finding: Renders via buildStrongCallFromArtifact → sc-card with kicker 俅哥强判断/STRONG CALL, mainSub 今日主推判断, 主看/主比分(+备选)/冷门风险/最大变量/为什么/外部预期/T-30, then th-hero lists modeling_focus + tactical_matchup + risk_variables + 30-min checklist, then ShareBlock(kind=prematch, join). Same sc-* styling + canonical projection as StrongCallCard. OMITS old card's calibration frame line and the pp-cta-row rescore/join buttons + #live30 anchor.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/predictionArtifacts.ts
Reason for reading: Artifact schema + loader the room consumes
Key finding: PredictionArtifact schema: date, fixture_key, id, home, away, status, kickoffUtc, source, prediction_confirmed, i18n. Per-locale: pending_direction, pending_score, prediction{primary_direction,score_call,backup_score,confidence,risk_level,risk_note,top_variable,why}, analysis{modeling_focus[],tactical_matchup[],risk_variables[],external_expectation[],thirty_minute_checklist[]}, operations{share_title,share_copy,join_cta}. Numerics nullable → surface as pending labels.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json
Reason for reading: The actual today (06-14) artifact content — is it data-backed or hand-filled
Key finding: source=operator_confirmed, prediction_confirmed=true, safety.operator_confirmed/no_auto_send=true. note: 'Operator-confirmed initial pre-match judgment ... A qualitative scout call with a reference scoreline — not a precise probability.' Content (NL vs JP: lean NL, 2-1, backup 1-1/2-2, risk 中高) is HAND-AUTHORED operator JSON, NOT LLM-generated nor pipeline-derived. confidence=null in all 4 langs.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/growth/strongCallProjection.ts
Reason for reading: The canonical projection both cards use
Key finding: buildStrongCall (narrative path) parses LLM fields (n.scoreline_view via splitScoreband, n.main_lean, harmonizedRisk, n.watch_next_signals[0], n.hero_subtitle) + getExternalSignals → StrongCall. buildStrongCallFromArtifact (P5) maps artifact JSON fields → same StrongCall shape; canonical T30_HOOK/CTA_LINE per lang. Numerics stay null → pending labels, never invented.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/check_prediction_artifact.py
Reason for reading: What the P5b guard requires of the strong call + deviation
Key finding: P5b core: zh prediction.primary_direction + score_call + backup_score must ALL be non-null confirmed values ('no weak default'); per-lang prediction.top_variable+why required (strong fields); analysis 5 lists non-empty; external_expectation lines must hit SAFE_EXT vocab; zh pending tokens + join_cta 加入临场情报群; safety.no_auto_send=true. Observation/recap side: deviation must contain 偏差 or 低于, assessment 部分命中 or 校准, recap_ready MUST be false (no fake recap). Source asserts ArtifactTacticalRoom carries all strong labels + ShareBlock wired.
Reuse / discard / uncertain: reuse
---

### A6 — main recap + share

Branch: main
File: frontend/src/pages/RecapDetailPage.tsx
Reason for reading: Primary recap surface — determine which tiers render a trust receipt
Key finding: 5 ordered tiers: (1) ProductNarrative real_recap -> buildRecapCall projection card + ProductRecapView; (2) ObservationReceipt artifact (recap_ready=false); (3) P0 safe-observation minimal card; (4) getNarrative historical main view; (5) deterministic eb/recap fallback with model-replay/verdict folded internal. Tier 1 uses DetailShareRow (copy-link+join ONLY); Tier 2 uses full ShareBlock; Tier 3 uses CopyLink only.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/ObservationReceipt.tsx
Reason for reading: The strongest trust-receipt tier (live for flagship fixture 1489371)
Key finding: Renders the FULL receipt: state_line, teams+score, receipt_title, pre_match_call (predicted scoreline), actual_line, assessment (hit/partial/miss verdict), deviation, calibration_title+points (bullets), next_impact, pending_line, then ShareBlock(kind=recap) with join CTA. This is a complete trust receipt.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/predictionArtifacts/observation_1489371.json
Reason for reading: Verify actual receipt field content for the live flagship recap
Key finding: Brazil 1-1 Morocco, recap_ready=false. zh receipt: pre_match_call='赛前主推：偏向巴西，主比分参考 2-1，备选含 1-1'; actual_line='实际比分：1-1'; assessment='比分区间命中，但胜负方向未完全命中，按部分命中处理' (explicit PARTIAL-HIT); deviation explains under-weighting; 3 calibration_points; next_impact present. safety block: no_fake_recap/no_auto_send/vocabulary_compliant=true. 4 langs zh/vi/my/en.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/growth/strongCallProjection.ts
Reason for reading: Canonical projection feeding both recap card and share card
Key finding: buildRecapCall returns {result_title=short_title, what_was_right=validated_factors[0].name (ONE factor only), why_deviated=screenshot_line, calibration_line=GENERIC constant, next_hook=GENERIC constant}. CALIBRATION_LINE/NEXT_HOOK are fixed per-language strings; NEXT_HOOK is HARDCODED 'Brazil vs Morocco' — staleness risk for any other real_recap. buildStrongCall/FromArtifact are artifact-aware; null numerics surface as pending labels, never invented.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/ShareBlock.tsx
Reason for reading: The full share affordance set
Key finding: 4 buttons: 🔗 copy link, 📋 copy share text (only if text present), 🖼️ share card -> /share/recap|fixture/:id?ref=, 👥 join (recordJoinIntent + navigate). cardTo always appends ?ref=refFor(loc). zh/vi/my only (en returns null).
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/DetailShareRow.tsx
Reason for reading: Share row used by the LLM real_recap tier and predict pages
Key finding: ONLY CopyLink + join button — NO copy-share-text, NO share-card link. So Tier-1 real_recap recap pages lack the share-text and share-card affordances that the artifact ObservationReceipt (Tier 2) has. Asymmetry/gap. Both carry ref (CopyLink via shareLink, join via recordJoinIntent).
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/ProductProofViews.tsx
Reason for reading: Verify depth below the real_recap projection card
Key finding: ProductRecapView is rich: PRE-MATCH READ (model_judgement), LeanRiskCards withScoreline, VALIDATED factors, UNDER-WEIGHTED factors, DECISIVE factors, EVIDENCE quote (screenshot_line), WATCH NEXT signals, join CTA, internal fold. So real_recap tier is NOT light: got-right + under-weighted + watch-next are all present.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/pages/ShareCardPage.tsx
Reason for reading: Screenshot share card with QR (the /share routes)
Key finding: Renders branded card + QR (joinUrl=SITE/join?ref). recap path renders buildRecapCall (result/right/deviation/calibration/next) OR obsCard observation-receipt fallback (receipt_title/pre_match_call/actual_line/assessment). P1.2b freeze: pre-match card frozen after kickoff, auto-redirects fixture->recap when recapAllowed. QR encodes ref. Disclaimer present per lang.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/growth/shareTemplates.ts
Reason for reading: Share TEXT copy generators + ref/link helpers
Key finding: recapShareCopy: buildRecapCall lines OR observation share_copy fallback. prematchShareCopy strong-result-first. shareLink appends ?ref=refFor (stored ref or per-lang DEFAULT_REF QG-TEST1/TT-VN88/FO-MM21). joinShareCopy/nextFixtureCopy present. All judgement strings sourced from LLM/projection fields, framing is Owner vocab.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/growth/refCapture.ts
Reason for reading: Confirm ambassador code survives share->visit->join
Key finding: captureRef stores ?ref= first-touch 30 days (CODE_RE ^(QG|TT|FO)-[A-Z0-9]{4,6}$); refFor returns stored or DEFAULT_REF; recordJoinIntent posts {ref,surface,lang} on join tap (skipped in mock). Ref IS preserved through copy-link, share-card QR, and join across all tiers.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/CopyLink.tsx
Reason for reading: Copy-link mechanism + ref
Key finding: Copies shareLink(path,loc) absolute URL (ref-appended) with clipboard + execCommand WebView fallback; label supplied by caller for honest per-surface wording.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/check_growth_copy.py
Reason for reading: Compliance guard coverage over the receipt+share copy
Key finding: GLOBS cover ObservationReceipt.tsx, ShareBlock.tsx, ShareCardPage.tsx, shareTemplates.ts, predictionArtifacts.ts + predictionArtifacts/*.json. Bans betting/guarantee/money/hierarchy/leakage in 4 langs; 提现 legal only in 不可提现. NOTE: RecapDetailPage.tsx is NOT in GLOBS (its 模型回放/模型修正 labels live in folded internal block, covered by the separate check_customer_visible_copy.py).
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/App.tsx
Reason for reading: Confirm /share + /recap + /join routes wired
Key finding: Routes confirmed: recap/:fixtureId, share/fixture/:fixtureId (kind=fixture), share/recap/:fixtureId (kind=recap), join. Share card reachable via ShareBlock cardTo; /recap deep links work (SPA).
Reuse / discard / uncertain: reuse
---

### A7 — main daily flow

Branch: main
File: scripts/mvp2_match_sync.py
Reason for reading: P1.3 daily registry generator named in task
Key finding: sync --date reads hand-written manual_scores_<date>.md → writes daily_fixtures_<date>.json (rich registry), recap_queue_<date>.json, frontend/src/data/dailyFixtures.generated.json AND frontend/public/data/daily-fixtures.json. Only 3 fixtures are KNOWN (1539000/1489369/1489371 → internal id+kickoff+flags); everything else gets internal_id=null + manual slug. renderable = has a bundled productNarratives/{id}.{lang}.json (only 1489369/1489371). select_candidates sets hero/next/recap by live→pre→recap_ready→recap_pending. upload subcommand POSTs registry to backend (needs prod ADMIN_API_TOKEN eng does not hold).
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/mvp2_editorial_agent.py
Reason for reading: P1.5c selected-hotspot mechanism named in task
Key finding: PROMPT BUILDER ONLY — prints a copy-paste LLM prompt to stdout, writes NOTHING, calls no API. Reads the slate (registry→runtime manifest→generated). Hard-codes the current homepage editorial line ('Brazil vs Morocco = daily story until kickoff; Mexico = secondary recap') as prompt text. Operator pastes into DeepSeek/Gemini/Kimi, reads back JSON (featured_pre_match/featured_recap/fallback_recap/group_only/hold_reason), and confirms MANUALLY. No persisted selected-hotspot artifact exists.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/mvp2_fixture_lifecycle.py
Reason for reading: canonical lifecycle gate consumed by every other script
Key finding: Pure decide(now,kickoff,api_short,recap_ready)→state (SCHEDULED..ARCHIVED) + gates(). Stale 'NS' past kickoff is overridden to LIVE/FINISHED by time inference (P1.2b). run_status_refresh writes timestamped docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_YYYYMMDD_HHMM.json (the untracked file in git status is exactly this). recap_ready_for() = productNarratives/{id}.zh-CN.json mode==real_recap.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/mvp2_growth_cli.py
Reason for reading: daily share-package generator + lifecycle gating
Key finding: refresh --lang assembles today/next/recap packages ONLY from bundled guard-passed narratives, lifecycle-gated; writes growth_packages/{kind}_{fid}_{lang}_{REF}.md + refresh_summary_*.json; a lifecycle refusal overwrites stale pre-match .md with REFUSED stub. _registry_fixtures() derives today/next/recap fids from the latest daily registry candidate flags. Strong-call structure (主比分/备选 split, 中高 risk harmonization) duplicated here AND in strongCallProjection.ts.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/dailyFixtures.ts
Reason for reading: runtime manifest loader + product-loop selector
Key finding: fetchDailyManifest priority backend→static→bundled. selectProductLoop() picks featuredPrediction = FIRST non-finished preMatchAllowed fixture in SLATE ORDER, featuredRecap = FIRST finished fixture; ordering IS the editorial lever (no ranking engine). heroEntries filters renderable+id.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/lib/freshness.ts
Reason for reading: client hero selection
Key finding: pickActiveFixture ranks pre_match → recap_ready → recap_pending. This is why a recap_ready Mexico would mechanically outrank a recap_pending Brazil — the reason the operator had to HAND-EDIT manifest flags (Mexico renderable=false) for the 06-14 override.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/predictionArtifacts.ts
Reason for reading: prediction/observation artifact loader named in task
Key finding: PREDICTION array + OBSERVATION map are HARD-CODED imports: today only manual_Nether-Japan-20260614.json and observation_1489371.json. Adding a new day's artifact requires editing this file + a frontend rebuild (bundled at build time, not runtime). getPredictionArtifact resolves by fixture_key or id; numerics may be null → pending labels, never invented.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json
Reason for reading: the day's featured pre-match strong call
Key finding: HAND-AUTHORED trilingual+en artifact: prediction{primary_direction, score_call 2-1, backup 1-1/2-2, risk_level 中高, top_variable, why} + analysis{modeling_focus, tactical_matchup, risk_variables, external_expectation(safe vocab), thirty_minute_checklist} + operations{share_title/copy/join_cta}. This is the rich depth — but it is written by a human, no generator exists.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/data/predictionArtifacts/observation_1489371.json
Reason for reading: post-match receipt for the finished hotspot
Key finding: HAND-AUTHORED observation receipt: pre_match_call → actual 1-1 → 部分命中 → deviation → calibration_points → next_impact, recap_ready=false (explicit no-fake-recap). This is the degraded recap tier when no A4 full recap is bundled.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/check_prediction_artifact.py
Reason for reading: validator that defines what a strong artifact must contain
Key finding: Asserts the strong-call + observation contract but HARD-CODES the two filenames (manual_Nether-Japan-20260614.json, observation_1489371.json). P5b rule: zh primary_direction/score_call/backup_score must be CONFIRMED (no weak pending default). external_expectation must use the SAFE_EXT vocab. So per new day, both the artifact AND this validator path must be updated by hand.
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/growth/strongCallProjection.ts
Reason for reading: canonical projection consumed by /predict, /share, homepage, CLI
Key finding: buildStrongCall tries bundled ProductNarrative first, else falls back to getPredictionArtifact → buildStrongCallFromArtifact. So a manual daily hotspot with no narrative still yields a strong call FROM the hand-authored artifact. buildRecapCall requires mode==real_recap (none for Brazil today).
Reuse / discard / uncertain: reuse
---

Branch: main
File: frontend/src/components/HomeProductLoop.tsx
Reason for reading: how the homepage renders featured prediction/recap
Key finding: HotspotPrediction card renders GENERIC localized boilerplate (predWhy, predBullets with {home}/{away} substitution, thirtyMin) — NOT the artifact's real strong call. The depth (score_call/top_variable/tactical_matchup) only appears one click deeper at /predict/{predictKey} via ArtifactTacticalRoom. predictKey = id ?? encodeURIComponent(external_game_id).
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/data_audit/mvp2_daily_refresh/REFRESH_20260614.md
Reason for reading: the actual 06-14 daily-refresh runbook
Key finding: Documents the manual override: on the deployed bundle pickActiveFixture would make Mexico (recap_ready) both hero and featured recap, demoting Brazil — forbidden. Fix = HAND-EDIT manifest: Brazil renderable=true/recapReady=false/hero, Mexico renderable=false. Notes a re-run of sync RESETS these flags (one-shot, not durable). Honest limitation: Netherlands can only be a lightweight 即将开赛 strip row without a bundled narrative + redeploy.
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/data_audit/mvp2_match_sync/daily_fixtures_20260614.json
Reason for reading: today's generated+hand-edited registry
Key finding: 7 fixtures; only Brazil/Mexico carry internal ids + the EDITORIAL OVERRIDE reasons. Netherlands/Germany/Ivory Coast/Sweden/Australia all internal_id=null, kickoff=null, renderable=false → lightweight status only. Confirms only 2 fixtures can carry depth.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/mvp2_project_external_signals.py
Reason for reading: external-signal refresh path
Key finding: Projects an INTERNAL signal frame → customer-safe externalSignals/{id}.json. But the only frames present are 1489369/1489371/1539000/979139 dated 06-12 — NOT refreshed for new daily fixtures. New hotspots get their external_expectation hand-typed into the artifact instead.
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/mvp2_growth/GROWTH_P15C_EDITORIAL_AGENT.md
Reason for reading: editorial-selection design doc
Key finding: Owner correction 2026-06-14: daily story must be Agent-led/LLM-assisted, NOT mechanical recap_ready promotion. P1.5c deliberately has NO scoring engine, NO persisted output, NO production write. Selection lives in prompt wording + operator confirmation. Flags 'if recurring, fold an explicit editorial-selection field into P1.5c (Owner-gated)' — i.e. the persisted-selection artifact is a known missing piece.
Reuse / discard / uncertain: reuse
---

### A8 — main operations + compliance

Branch: main
File: docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md
Reason for reading: Canonical first-send operator runbook (which link/copy/card/ref/CTA + checklists)
Key finding: Defines the exact send target: channel=zh_internal_group, fixture=1489371, ref=QG-TEST1, lang=zh; share card URL /share/fixture/1489371?ref=QG-TEST1&lang=zh; join link /predict/1489371?ref=QG-TEST1; copy taken VERBATIM from package file, only [群链接由运营填写] may be edited; PRE-SEND + POST-SEND(mark-sent) checklists; STOP conditions; manual one-channel send, NO bots/schedulers/bulk-forward.
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/mvp2_growth/GROWTH_P15_FIRST_SEND_GATE.md
Reason for reading: 7-gate first-send gate tracker (current send readiness state)
Key finding: Gates 1-3,5,6 closed; Gate 4 pre-kickoff PASS, LIVE/FT operator match-day; Gate 7 Owner GO PENDING. No send until 'GO zh_internal_group QG-TEST1 fixture 1489371'. P1.5b Daily Featured Copy Policy: 今日复盘=Mexico only, 今日赛况 已完赛/即将开赛. P1.5c editorial agent = prompt builder only (no scoring/API/write/send).
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/check_growth_copy.py
Reason for reading: Growth copy guard scanner — compliance enforcement on all growth surfaces
Key finding: Substring scan over JoinPage/GrowthAdmin/StrongSignalCard/shareTemplates/ShareBlock/ShareCardPage/growth backend + CLI for 5 forbidden classes in 4 langs: betting/odds/handicap, win-guarantee, commission/payout/recharge, agent-hierarchy, process/audit-leakage. 提现 legal ONLY inside (不可/不能/无法)提现. exit0=clean; --selftest 6 cases.
Reuse / discard / uncertain: reuse
---

Branch: main
File: scripts/mvp2_growth_cli.py
Reason for reading: Operator CLI: package/refresh assembles the paste-ready send packages
Key finding: package today|recap|next assembles share package from BUNDLED guard-passed LLM narratives (judgement lines verbatim, only ORDER engineered: result→主比分/备选→risk→why→T-30→CTA); lifecycle gate FIRST refuses live/finished fixture as pre-match; refresh writes md packages + neutralizes stale files via _write_refused_stub on refusal; header rule 'NOTHING here sends anything; MTC stays 平台积分(不可提现/不可转让/不可交易)'.
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/data_audit/mvp2_growth_packages/today_1489371_zh_QG-TEST1.md
Reason for reading: The actual first-send package file (paste copy source)
Key finding: NOW REFUSED — DO NOT SEND. Lifecycle gate auto-neutralized it: '1489371 finished (RECAP_PENDING) — pre-match send window closed (Owner manual daily refresh 2026-06-14)'. Pre-match send window for 1489371 has CLOSED; today+next packages both stubbed; recap path only.
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/data_audit/mvp2_growth_packages/recap_1489369_zh_QG-TEST1.md
Reason for reading: Available recap package (verbatim recap paste copy)
Key finding: AVAILABLE, lifecycle RECAP_READY, but approval_status=guard_passed with warning 'Verify queue approval before sending' (NOT yet queue-approved). Copy: 俅哥复盘 墨西哥2-0南非 / 赛前看对了什么 / 比分为什么偏离 (参考区间1-1/1-0/0-1 实际2-0) / 校准 / next hook + link. Carries operator_next_step: 人工审核→Owner GO→手动粘贴→mark-sent+截图+SEND_LOG(绝不自动发送).
Reuse / discard / uncertain: reuse
---

Branch: main
File: docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_20260613_1255.json
Reason for reading: Lifecycle snapshot (untracked) confirming pre-refresh state
Key finding: 06-13 12:55 snapshot: 1489371 SCHEDULED, today_package_allowed=true (T-545min); 1489369 RECAP_READY, recap_package_allowed=true. This predates the 06-14 manual refresh that flipped 1489371 to finished/REFUSED.
Reuse / discard / uncertain: uncertain
---

Branch: main
File: frontend/src/pages/ShareCardPage.tsx
Reason for reading: Verify share-card surface carries mandatory disclaimer
Key finding: shc-disclaimer renders zh '历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。' — mandatory disclaimer is in-frame on the share card the operator screenshots.
Reuse / discard / uncertain: reuse
---
