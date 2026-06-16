# P5A · Architect Decision — Core 1+2 Content Quality

Verdict: **GO.**

What's broken: copy quality (weak/hedgy/forbidden phrases), not the mechanism. Scope: STRONGER copy
for 1 primary + 2 secondary + yesterday recap + share + internal trace. NO match-count expansion, NO
scheduler, NO backend deploy, NO payment/token, NO auto-send/publish, operator_estimated stays
secondary. Source-of-truth chain unchanged (reviewed JSON → i18n sync → render). Add a `copy_v2` block
(copy_version=p5a_v2) carrying the v2 fields, synced by `apply`, rendered additively (no redesign).
Must be proven on screenshots: visibly stronger primary/secondary/recap/share, no forbidden phrases,
rendered-DOM guards PASS. BLOCKED if weak copy renders or v2 exists but isn't projected.
