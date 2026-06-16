# P4R+ · Gate Spec — Page-Level Product Reality (frozen)

## Allowed areas
prediction artifact builder (apply i18n sync) · reviewed artifact projection · frontend artifact
interfaces · homepage content projection · predict page copy projection · recap page copy projection ·
internal daily source trace · rendered-DOM guards · screenshots.

## Forbidden
backend schema change (unless proven required — NOT required this sprint) · auto-send · auto-publish ·
scheduler · new payment/referral/token runtime · fake event/full recap · fake lineup/injury/
probability/confidence · broad redesign.

## Gate (READY_TO_MERGE)
diagnosis + architect + product + gate docs exist · reviewed LLM copy renders (or COPY_MISSING) ·
5 rendered-DOM guards pass locally · screenshots show corrected copy · Claude self-review PASS ·
independent (Codex) review PASS or Owner-accepted PASS_WITH_PATCHES · Send HOLD.

## Gate (READY_TO_DEPLOY)
merged ff-only · Render frontend deployed · live rendered guards PASS · live screenshots · Owner
confirms.

## HOLD triggers
reviewed LLM copy exists but not rendered · homepage shows stale as today · recap static/fallback
without label · guards only inspect JSON · independent review missing · screenshots missing · send not HOLD.
