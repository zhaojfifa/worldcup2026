> P6 Discovery Context Pack — generated 2026-06-14. Read-only discovery; NO implementation.
> Current main = b9b362a (main, P5b). Old refs inspected: feature/mvp2-growth-p0-design (5535c61) · feature/mvp2-growth-p1-1c-strongcopy (0a73ee6).

# OPERATIONS_FLOW — Per-Fixture, Per-Channel Operator Workflow

This document consolidates the canonical operator send workflow onto a main-tracked
page. It is the human discipline layer that sits on top of the runtime growth assets
(`/share` routes, `mvp2_growth_cli.py`, ref codes, ShareBlock/StrongCallCard) and the
compliance guards (`check_growth_copy.py`, `check_prediction_artifact.py`,
`check_homepage_product_loop.py`).

The authoritative source chain it preserves verbatim:

- `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md` (on **main**) — the fixture-specific first-send runbook (send target table, verbatim paste rule, PRE-SEND / POST-SEND checklists, STOP conditions).
- `docs/mvp2_growth/GROWTH_P0_OPERATOR_SOP.md` §1–8 (on `feature/mvp2-growth-p0-design`) — the non-fixture-specific per-fixture/per-channel SOP (6 checklists + T-30 watch + A4 recap follow-up + screenshot storage).
- `docs/mvp2_growth/GROWTH_P0_GROUP_CTA_COPY.md` — stage-by-stage group message pack (CTA labels, group intro, T-30 reminder, post-recap follow-up, send order, forbidden-copy list).
- `docs/mvp2_growth/GROWTH_P0_COMPLIANCE_NOTE.md` — what the growth layer IS / IS NOT, the 6 preconditions, MTC floor.
- `docs/mvp2_growth/GROWTH_P15_FIRST_SEND_GATE.md` (on **main**) — the 7-gate first-send readiness tracker.

> **Note on doc location.** As of main `b9b362a`, the canonical SOP / group-CTA pack / compliance note still live on `feature/mvp2-growth-p0-design`, **not on main** (main carries only the fixture-specific runbook + the gate doc). The `FIRST_SEND_RUNBOOK_1489371.md` pre-match half is now **stale** — 1489371 finished (Brazil 1-1 Morocco, RECAP_PENDING), so its pre-match send target must roll forward to the next pre-match fixture. P6 recovery item (D) proposes consolidating the SOP/CTA/compliance onto this main-tracked operations doc; that is a **zero-runtime, docs-only** change.

---

## 0. Posture — read before any step

Per-fixture, per-channel. The canonical chain is **GROWTH_P0_OPERATOR_SOP §1–8 + FIRST_SEND_RUNBOOK_1489371**. Everything below is manual. Nothing in this flow is sent by software.

- **No auto-send anywhere.** `mvp2_growth_cli.py` header states verbatim: *"NOTHING here sends anything."* The CLI only assembles paste-ready `.md` packages and writes files; the operator pastes by hand, one channel at a time, on explicit per-channel Owner GO.
- **Scope ceiling** (unchanged): zh internal group · vi trusted Telegram · my 1 test group. Public operation stays paused.
- **Engineering holds NO prod ADMIN_API_TOKEN.** Code creation, prod upload, and sends are all operator actions.

---

## 1. PRE-MATCH — assemble the send package

### Step 1 — Generate the paste copy (`mvp2_growth_cli.py package` / `refresh`)

Run `mvp2_growth_cli.py package today|recap|next` (or `refresh --lang`) to assemble the paste `.md` from **bundled, guard-passed LLM narratives**.

- The judgement lines are taken **verbatim** from the narrative; only the **ORDER** is engineered: **result → 主比分 / 备选 → 冷门风险 → 为什么 → ⏱️ T-30 hook → CTA** (strong-result-first, mirroring `frontend/src/growth/shareTemplates.ts::prematchShareCopy`).
- The **lifecycle gate fires FIRST** (`mvp2_fixture_lifecycle.py::decide/gates`): any live or finished fixture is **refused** as a pre-match package, and a stale pre-match `.md` is overwritten with a `REFUSED` stub (`_write_refused_stub`). A fixture must be genuinely pre-kickoff to emit a `today_`/`next_` package.
- Output: `docs/data_audit/mvp2_growth_packages/{today,next,recap}_{fid}_{lang}_{REF}.md` + `refresh_summary_*.json`.

> The package only exists for a fixture that already has a **bundled guard-passed narrative** (today: `1489369` / `1489371`). A manual hotspot with no narrative is **not** packaged by the CLI; its copy is the operator-confirmed prediction artifact JSON instead.

### Step 2 — Queue approve

The fixture's queue entry must reach status **`approved`** — `guard_passed` is **not** sufficient.
A `guard_passed` package carries the warning *"Verify queue approval before sending."*

> Live example on main: `docs/data_audit/mvp2_growth_packages/recap_1489369_zh_QG-TEST1.md` is **AVAILABLE** and lifecycle `RECAP_READY`, but `approval_status=guard_passed` → must clear **queue approve + Owner GO** before any send.

### Step 3 — PRE-SEND checklist (run on the CURRENT deploy)

- **Live visible scan PASS** — `check_customer_visible_copy.py` **21/21** on the current deploy.
- **Homepage source = 实时** (runtime manifest, not the static backup).
- **Fixture still pre-kickoff** (not frozen by the P1.2b kickoff freeze).
- **Copy verbatim** with persona + mandatory disclaimer present.
- **Fresh share-card screenshot** captured (persona + disclaimer **in frame** — see §5).

### Step 4 — Owner GO, per channel

Owner issues an explicit per-channel GO in the exact form:

```
GO <channel> <code> fixture <id>
```

Example: `GO zh_internal_group QG-TEST1 fixture 1489371`.
Scope ceiling enforced here: **zh internal group · vi trusted Telegram · my 1 test group**. No GO ⇒ no send.

### Step 5 — Manual paste, ONE channel

- Paste the copy + paste the **join link separately** + attach the **share-card screenshot**.
- **No bots / schedulers / bulk-forward.** Only the `[群链接由运营填写]` placeholder may be substituted.

---

## 2. SEND TARGETS — what to send (first zh send)

| Field | Value |
|---|---|
| **Channel** | `zh_internal_group` |
| **Ref code** | `QG-TEST1` |
| **Which link to send (join)** | `https://worldcup2026-izid.onrender.com/predict/<id>?ref=QG-TEST1` |
| **Which share card** | `https://worldcup2026-izid.onrender.com/share/fixture/<id>?ref=QG-TEST1&lang=zh` |
| **Which share copy** | The `today_<id>_zh_QG-TEST1.md` package body, verbatim (only `[群链接由运营填写]` editable) |
| **Group CTA** | `加入临场情报群` (group join) — fan-read label from `GROWTH_P0_GROUP_CTA_COPY.md` (`加入情报群 / 进群看完整版 / 看俅哥怎么校准`) |

### Ref-code map (per language; `frontend/src/growth/refCapture.ts` / `shareTemplates.ts` DEFAULT_REF)

| Language | Default ref code | Channel |
|---|---|---|
| zh | **QG-TEST1** | zh internal group |
| vi | **TT-VN88** | vi trusted Telegram |
| my | **FO-MM21** | my 1 test group |

The ref is appended to **every** shared link, the share-text link, and the share-card QR
(`SITE/join?ref=CODE`). First-touch `?ref=` is captured for 30 days
(`CODE_RE = ^(QG|TT|FO)-[A-Z0-9]{4,6}$`); attribution is **channel/attention only** —
no money, no identity fields (Owner design). vi/my each get their **own** Owner GO per channel.

### Which share CARD (the `/share` routes)

- **Pre-match card:** `/share/fixture/<id>?ref=<CODE>&lang=<lang>` → `ShareCardPage` renders the canonical `buildStrongCall` projection (brand + persona, 俅哥主看 / 参考比分 / 备选 / 冷门风险 / 最大变量 / first external line / ⏱️T-30 hook) + **QR to `SITE/join?ref=CODE`** + in-frame disclaimer.
- The operator **screenshots the in-frame card**; the join link is pasted **outside** the image.

---

## 3. AT T-30 (kickoff − 30, lineups out)

Send the **T-30 reminder message** ONLY after **all** of:

1. **A3 `guard_passed`** (the 30-min re-score / lineup update is generated and guard-clean), then
2. **queue approve**, then
3. **Owner GO**.

Hard gates around the window (from SOP §7):

- **T-12 = no new generation** (`mvp2_growth_cli`/queue freeze).
- **Kickoff = queue sweep** — all pre-match material dies (lifecycle freeze; pre-match cards auto-freeze, `mvp2_growth_cli refresh` neutralizes stale pre-match packages to `REFUSED` stubs).
- **Operator absent at the keyboard ⇒ nothing sends.** (Operator at keyboard from T-2h.)

The fan-read T-30 copy comes from the guard-passed A3 artifact (`group_update_message`),
never hand-written. The on-product hook is the T-30 ladder
(`RescoreBlock`: free 3 triggers + in-group locked triggers + 2 condition→new-call rules).

---

## 4. AFTER FULL TIME (+45) — close the loop

1. `mvp2_growth_cli.py refresh` → assembles the **recap package** (lifecycle now `RECAP_READY`).
2. **guard** (`check_growth_copy.py`) → **review** → **queue approve**.
3. **Owner GO** (per channel, same form as §1 Step 4).
4. **Recap follow-up into the SAME channels** (close the loop with the audience that saw the pre-match call) → then the **next-fixture hook**.
5. **mark-sent** + screenshot + a **SEND_LOG** row (`queue mark-sent --channel ...`).

Recap copy is taken **only** from a guarded `real_recap` narrative; if no full recap is
bundled, the surface renders the **recovered `ObservationReceipt`** (pre-match call →
actual score → hit/partial/miss → deviation → calibration → next impact, `recap_ready=false`)
— **never a synthesized result**. The recap queue lists a missing full recap as
`NEEDS_A4_RECAP`.

> The recap **share copy** falls back to the observation artifact's `share_copy`
> (`shareTemplates.ts::recapShareCopy`) when `recap_ready=false` — a recovered receipt,
> never a fake recap. The recap **share card** is `/share/recap/<id>?ref=<CODE>&lang=<lang>`.

---

## 5. WHAT NOT TO SEND

Do **not** send when ANY of the following is true:

- **Kickoff has passed** — the card freezes (P1.2b); a finished/live fixture must never go out as pre-match.
- **Ref `attached:false`** — the ref code is not yet created in prod (operational gate).
- **Any betting / odds / 盘口 / 投注 / handicap / bookmaker wording** in any language — even negated, in group copy.
- **No explicit per-channel Owner GO.**
- **Any copy that is not verbatim** from a guard-passed artifact.
- **Links inside the LLM prose** (links are pasted separately, outside the judgement body).
- **Fabricated urgency** (e.g. `最后 X 个名额`).
- **A fabricated score / fake recap** (recap only from a guarded `real_recap`, else the recovered `ObservationReceipt`).
- **A card missing the mandatory disclaimer in frame.**

---

## 6. MUST PRESERVE (non-negotiable)

- **NO auto-send anywhere.** CLI header: *"NOTHING here sends anything."* All sends are manual, one channel, on explicit per-channel Owner GO. No bots, no schedulers, no bulk-forward. Operator absent ⇒ nothing sends.
- **NO betting / trading vocabulary** in any language — no 盘口 / 投注 / 下注 / odds / handicap / bookmaker / 亚盘 / 让球盘 / kèo / cửa trên / cửa dưới / tài xỉu / chấp bóng, **even negated**, in any group copy. Enforced by `check_growth_copy.py` (5 forbidden classes × 4 languages: betting/odds/handicap · win-guarantee · commission/payout/recharge · agent-hierarchy · process/audit-leakage).
- **NO fake recap.** Recap copy comes only from a guarded `real_recap`; otherwise the recovered `ObservationReceipt` is shown (`recap_ready=false`), never a synthesized score. Card B (archived call vs honest outcome) is the **anti-pick-selling differentiator** — accountability, not a guaranteed pick.
- **MTC = 平台积分 only — non-cash, non-transfer, non-trade.** 不可提现 / 不可转让 / 不可交易, no yield/收益, no commission. `提现` is legal **only** inside `不可提现` (negation regex in the guard). Any growth credit is **manual-review, capped, non-cash** (existing wallet rails / `wallet_service._credit` → `TokenLog`).
- **Mandatory disclaimer in frame** on every screenshotted card: `历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。`
- **Judgement immutability** — sha256 tamper-reject; operators **never** rewrite judgement. Only `[群链接由运营填写]` may be substituted.

---

## 7. Tool ↔ Step map (current main)

| Step | Concrete current-main tool |
|---|---|
| Assemble pre-match / recap / next package | `scripts/mvp2_growth_cli.py package today\|recap\|next` · `refresh --lang` |
| Lifecycle gate (refuse live/finished as pre-match) | `scripts/mvp2_fixture_lifecycle.py` (`decide/gates`); `mvp2_growth_cli refresh` writes `REFUSED` stub |
| Compliance guard on growth copy | `scripts/check_growth_copy.py` (5 classes × 4 langs; `提现` only inside `不可提现`) |
| Strong-call / receipt projection (single source) | `frontend/src/growth/strongCallProjection.ts` (`buildStrongCall` / `buildStrongCallFromArtifact` / `buildRecapCall`) |
| Share copy structure | `frontend/src/growth/shareTemplates.ts` (`prematchShareCopy` / `recapShareCopy` / `joinShareCopy` / `nextFixtureCopy`; DEFAULT_REF QG-TEST1/TT-VN88/FO-MM21) |
| Ref capture / join intent (attribution-only) | `frontend/src/growth/refCapture.ts` (`captureRef` 30-day first-touch; `recordJoinIntent`) |
| Join link surface | `/predict/<id>?ref=<CODE>` (StrongCallCard / ArtifactTacticalRoom) |
| Share card + QR | `/share/fixture/<id>` · `/share/recap/<id>` → `frontend/src/pages/ShareCardPage.tsx` (QR → `SITE/join?ref=CODE`) |
| On-page share affordances | `frontend/src/components/ShareBlock.tsx` (🔗 link / 📋 copy text / 🖼️ share card / 👥 join) |
| Per-fixture first-send runbook | `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md` (target table / verbatim paste / checklists / STOP conditions) |
| Per-fixture/per-channel SOP | `docs/mvp2_growth/GROWTH_P0_OPERATOR_SOP.md` §1–8 (on p0-design branch) |
| Stage-by-stage group CTA copy | `docs/mvp2_growth/GROWTH_P0_GROUP_CTA_COPY.md` (on p0-design branch) |
| Compliance contract | `docs/mvp2_growth/GROWTH_P0_COMPLIANCE_NOTE.md` (on p0-design branch) |
| First-send gate tracker | `docs/mvp2_growth/GROWTH_P15_FIRST_SEND_GATE.md` (on main) |

---

## 8. CURRENT LIVE STATE (2026-06-14)

- **1489371** pre-match window is **CLOSED** — `today_`/`next_` packages auto-`REFUSED` after the 06-14 manual refresh (lifecycle: `1489371` finished, `RECAP_PENDING`). The `FIRST_SEND_RUNBOOK_1489371.md` pre-match half is therefore stale; the live pre-match target must roll forward to the next scheduled fixture.
- **`recap_1489369_zh_QG-TEST1.md`** is **AVAILABLE** (Mexico 2-0 South Africa, lifecycle `RECAP_READY`) but `approval_status=guard_passed` → must clear **queue approve + Owner GO** before any send.
- **Nothing sent.** No SEND_LOG row exists; **Gate 7 (Owner per-channel GO) is PENDING**.
- **Ref codes** `QG-TEST1 / TT-VN88 / FO-MM21` are **not yet created in prod** (live click probe `attached:false`) — an operational gate (operator creates them via `/internal/growth` with the prod token), not a code defect.

---

## 9. Compliance gate ladder (preconditions to any runtime growth — `GROWTH_P0_COMPLIANCE_NOTE.md` §5)

These 6 conditions gate ANY runtime growth feature and remain the binding contract:

1. ≥ 1 full fixture cycle of feedback with no incident.
2. Owner GO on a written runtime design naming exact tables/routes.
3. Guard implemented **first**.
4. Channel-level attribution is the ceiling **unless** Owner explicitly approves user-level (Owner-amended for P1 ref codes).
5. Rewards MTC-only, non-withdrawable, manual, capped.
6. Dedicated PR branch.

Growth P1 runtime (codes, `/share` + `/join`, QR) landed via a dedicated branch satisfying
these conditions; the no-money / no-identity / no-auto-send floor is fully intact. Track B
referral mechanics stay **design-only**.
