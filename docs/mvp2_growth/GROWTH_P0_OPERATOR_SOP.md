# Growth P0 — Operator SOP (single page, per fixture)

> Pairs with docs/mvp2/TRIAL_GO_NO_GO_CHECKLIST.md (compliance gate) and the fixture runsheet
> (e.g. docs/mvp2/TRACKA_1489371_A3A4_RUNSHEET.md). This SOP adds the growth-send discipline.

## 1. BEFORE SENDING (any material, any channel)
- [ ] Live scan passed on the CURRENT deploy (`check_customer_visible_copy.py` vs live = PASS)
- [ ] Fixture still pre-kickoff for pre-match material (CLI refuses expired items anyway)
- [ ] Queue item status = `approved` (not guard_passed, not needs_review)
- [ ] Copy taken verbatim from the send-kit; only [群链接由运营填写] replaced
- [ ] Card screenshot freshly taken from the live surface, persona + disclaimer in frame

## 2. OWNER GO CHECKLIST (per fixture, per channel)
- [ ] Owner has named the fixture AND the channels (tags) allowed
- [ ] Scope unchanged: zh internal · vi trusted Telegram · my 1 test group — anything else = NO
- [ ] GO reference (message/date) noted in the SEND_LOG row

## 3. QUEUE APPROVE CHECKLIST (reviewer)
- [ ] `queue show <ITEM>` read in full, per language
- [ ] guard_passed status genuine (no needs_review override without --note)
- [ ] facts spot-check: scoreline band vs page, event claims vs match facts (the vi
      "both goals vs 10 men" bug is the cautionary case)
- [ ] `queue approve <ITEM> --by <name>`

## 4. MANUAL PASTE CHECKLIST
- [ ] paste copy → paste link → attach card image → send — by hand, one channel at a time
- [ ] NO bots, NO schedulers, NO bulk forward, NO edits to the judgement text

## 5. MARK-SENT CHECKLIST (immediately after each send)
- [ ] `python3 scripts/mvp2_ops.py queue mark-sent <ITEM> --channel <tag> --group "<name>" --screenshot docs/qa_screenshots/mvp2_trial_sends/<file>.png`
- [ ] screenshot of the actual sent message saved at that path (file exists before mark-sent)
- [ ] SEND_LOG.md row appended (date/fixture/surface/lang/tag/group/screenshot/GO-ref)

## 6. SCREENSHOT STORAGE RULE
All send evidence in `docs/qa_screenshots/mvp2_trial_sends/` —
`{kind}_{fixture}_{lang}_{tag}_{YYYYMMDDTHHMM}.png`. Never delete; superseded sends stay.

## 7. T-30 WATCH RESPONSIBILITY (match day)
Operator AT KEYBOARD from T-2h. T-90 watch loop running. If lineups release: A3 auto-generates
into the queue → review → approve → Owner GO → send before T-20. T-12 = no new generation.
T-10 unreviewed = send only the pre-approved A2 reminder template. Kickoff = `queue sweep`,
all pre-match material dead. Operator absent = nothing sends.

## 8. A4 RECAP FOLLOW-UP RULE
FT+45: refresh pack → `recap` → guard → review → approve → Owner GO → recap follow-up message
(CTA pack §4) into the SAME channels that received the pre-match send (close the loop with the
same audience), then the next-fixture hook. Recap sends also get mark-sent + screenshot + log row.
