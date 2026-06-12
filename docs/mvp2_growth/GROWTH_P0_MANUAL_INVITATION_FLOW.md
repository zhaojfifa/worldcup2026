# Growth P0 — Manual Invitation Flow (design-only, operator-executed)

> No code. No attribution runtime. No rewards. The entire flow is: operator shares a screenshot
> card + a link, by hand, into Owner-GO-approved channels, and logs it.

## 1. Flow

```
Owner GO (per fixture, per channel)
  → operator picks card (share-card design doc) + copy (CTA copy pack, verbatim)
  → operator screenshots the LIVE surface (zh/vi/my as target requires)
  → operator pastes: [card image] + [approved copy] + [group link] into the target channel
  → operator records the send in the queue (mark-sent) + operator log with channel/source tag
  → operator captures a SEND screenshot → docs/qa_screenshots/mvp2_trial_sends/
  → fan joins group via the pasted link (no tracking; the link is the plain group invite)
  → feedback collected per docs/mvp2/TRIAL_FEEDBACK_FORM.md
```

## 2. Operator steps (per send)
1. Confirm fixture window open (pre-match material dies at kickoff — CLI enforces expiry).
2. Confirm queue item `approved` (guard_passed + reviewer approve + Owner GO).
3. Screenshot the live surface fresh (never reuse stale screenshots after a rescore).
4. Paste copy verbatim from the send-kit; replace only [群链接由运营填写].
5. Send manually. NO scheduling tools, NO bots, NO bulk forwarding.
6. `python3 scripts/mvp2_ops.py queue mark-sent <ITEM> --channel <channel> --group "<group>" --screenshot <path>`
7. Append one line to the operator log (see channel tagging doc §3).

## 3. Channel/source naming
Use the fixed tag set from GROWTH_P0_CHANNEL_TAGGING_DESIGN.md (e.g. `telegram_group_1`,
`zalo_test_group`, `facebook_dm`, `operator_manual`). One tag per send, recorded manually.

## 4. Hard limits
- NO auto attribution: we never encode who invited whom; source = channel-level manual tag only.
- NO reward issuance for joining/inviting (no MTC grants, no unlocks, no badges in P0).
- NO wallet/commission/recharge/payout — not even as copy.
- NO per-user invite links or QR codes (P0 link = the one plain group invite per channel).
- Trial scope stays Owner-defined: zh internal group · vi Telegram trusted · my 1 test group.
