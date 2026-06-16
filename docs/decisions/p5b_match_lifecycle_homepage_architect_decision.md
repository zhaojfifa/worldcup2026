# P5B · Architect Decision — Match-Lifecycle Homepage Orchestration

Verdict: **GO.**

Broken: the homepage primary is a STATIC operator pick (selectedHotspot), not lifecycle-driven, so it
does not follow match progress. Scope: a lifecycle SELECTOR (kickoff + status + recap_ready + model
source + now) that picks primary (earliest upcoming, source-qualified, never finished/op_estimated/
archive/demo) + 1-2 secondary + latest finished recap, with roles/states/reasons + blocking; homepage
reads the artifact. No 3-5 expansion, no scheduler, no backend deploy, no betting/fake data, operator_
estimated never primary, archive/demo never active, send HOLD. Source of truth: runtime manifest (kickoff/
status) + reviewed prediction artifacts (copy/model source) + observation/recap artifacts. Lifecycle states
frozen in the gate spec. BLOCKED if no valid primary (PRIMARY_REVIEW_REQUIRED, not stale fixed content).
Proven by rotation: at a pre-kickoff basis Belgium is primary; once Belgium finishes the selector rotates
the next upcoming to primary and Belgium → latest_recap.
