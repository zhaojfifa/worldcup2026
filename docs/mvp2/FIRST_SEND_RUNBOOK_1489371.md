# First-Send Runbook — 1489371 Brazil vs Morocco · zh_internal_group · QG-TEST1

> P1.5 First Send Gate Closure. **Generation is done; SENDING IS MANUAL and requires an explicit
> per-channel Owner GO.** Pairs with `GROWTH_P0_OPERATOR_SOP.md` + `TRIAL_GO_NO_GO_CHECKLIST.md` +
> the match-day runsheet `TRACKA_1489371_A3A4_RUNSHEET.md`. No auto-send, ever.

## Send target (first controlled send)
| field | value |
|---|---|
| channel | **zh_internal_group** (internal trial group only) |
| fixture | **1489371 Brazil vs Morocco** (KO 2026-06-13 22:00 UTC) |
| ref code | **QG-TEST1** |
| language | zh |
| package | `docs/data_audit/mvp2_growth_packages/today_1489371_zh_QG-TEST1.md` |
| share card | https://worldcup2026-izid.onrender.com/share/fixture/1489371?ref=QG-TEST1&lang=zh |
| join link | https://worldcup2026-izid.onrender.com/predict/1489371?ref=QG-TEST1 |
| screenshot dir | `docs/qa_screenshots/mvp2_trial_sends/` |

## Exact paste copy
Use the `copy_text` block verbatim from the package file above — **do not rewrite the judgement**.
The only allowed edit is substituting a real group link for any `[群链接由运营填写]` placeholder
(the current package already carries the live join link, so no edit is needed).

## PRE-SEND checklist (all must be ✅ before paste)
- [ ] **Owner GO received** for this exact channel+fixture+code (Gate 7): `GO zh_internal_group QG-TEST1 fixture 1489371`
- [ ] **Ambassador code QG-TEST1 exists** (Gate 1) — verify in `/internal/growth` or:
      `curl -s -X POST .../growth/click -d '{"ref":"QG-TEST1","surface":"join","lang":"zh"}'` → `"attached":true`
- [ ] **1489371 still pre-kickoff** — homepage hero shows it, `/predict/1489371` shows the StrongCallCard (NOT frozen). If kickoff has passed, **STOP** (the page freezes; do not send a pre-match card).
- [ ] **Live visible scan PASS** (`check_customer_visible_copy.py …` 21/21) on the current deploy
- [ ] **Live homepage source = 实时** (backend up-to-date)
- [ ] Copy taken **verbatim** from the package; persona + disclaimer intact; no betting/odds wording
- [ ] Fresh share-card screenshot taken from the live `/share/fixture/1489371` surface

## SEND (manual, one channel)
- [ ] Paste copy → paste/keep the join link → attach the share-card screenshot → send by hand to **zh_internal_group only**
- [ ] NO bots · NO schedulers · NO bulk forward · NO edits to the judgement text

## POST-SEND mark-sent checklist (immediately)
- [ ] Save the sent-message screenshot to `docs/qa_screenshots/mvp2_trial_sends/today_1489371_zh_QG-TEST1_<YYYYMMDDTHHMM>.png`
- [ ] `python3 scripts/mvp2_ops.py queue mark-sent <ITEM> --channel zh_internal_group --group "<name>" --screenshot <path>` (if a queue item is used)
- [ ] Append a `SEND_LOG.md` row: date / fixture 1489371 / surface today / lang zh / tag zh_internal_group / group / screenshot / Owner-GO reference
- [ ] Record first click/join-intent counts from `/internal/growth` (attribution to QG-TEST1)

## STOP conditions (do not send)
- Kickoff has passed (pre-match card is stale — the product freezes it; sending it anyway breaks trust)
- QG-TEST1 returns `attached:false` (code not created → clicks won't attribute)
- Any betting/odds/guarantee wording appears in the assembled message
- No explicit Owner GO for this exact channel

## vi / my (later, separate Owner GO each)
Same procedure with `today_1489371_vi_TT-VN88.md` → telegram_vi_trusted, and the my package →
telegram_group_1. Each channel needs its own `GO <channel> <code> fixture 1489371`.
