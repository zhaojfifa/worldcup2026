# P5B · Phase 0 — Current Homepage Lifecycle Diagnosis

> Branch feature/mvp2-p5b-match-lifecycle-homepage-orchestration (off main @4162b66, P5A merged).

1. **Why still a fixed Belgium-Egypt primary?** `selectProductLoop` (dailyFixtures.ts) takes the primary
   from `getSelectedHotspot()` (a STATIC operator pick = Belgium 1489377). It does NOT rotate by kickoff/
   status — it is the editor's authority, not a lifecycle calculation.
2. **What determines the primary today?** selectedHotspot.fixture_key (Belgium) + a P6 gate that it has a
   prediction artifact. If the selection isn't in today's scheduled slate it falls back to the first
   artifact-backed scheduled fixture. Not lifecycle-driven.
3. **Is kickoff_time used to rotate primary?** NO. kickoff feeds the per-fixture lifecycle_state
   (freshness.ts / lifecycle.py: SCHEDULED/T_MINUS_30/LIVE/FINISHED…) but the PRIMARY pick ignores it.
4. **Is status used to move prediction → recap?** Partially: `featuredRecap = finished[0]` (first finished)
   drives the recap section, but the PRIMARY is not demoted to recap when it finishes — it just stays the
   selectedHotspot until the operator changes the file.
5. **Is recap_ready used?** Yes for the recap CTA (查看复盘 only when recapReady) — but not to rotate primary.
6. **Active package static or lifecycle-calculated?** dailyContentQueue + selectedHotspot are STATIC
   (operator/build-time). Lifecycle states are computed at render, but selection is not.
7. **Finished matches eligible for recap?** Those with status finished/RECAP_* + an observation/recap
   artifact (today: Brazil-Morocco OBSERVATION, Mexico-SA RECAP_READY, Sweden-Tunisia pending).
8. **Upcoming eligible for prediction?** Scheduled fixtures with a reviewed prediction artifact: Belgium
   (computed), Saudi-Uruguay (computed), Spain-CapeVerde (operator_estimated → secondary only).
9. **Archive/demo to exclude?** WC-2022 historical archive (Germany-Japan, Qatar-Ecuador 2022) + the
   legacy home-demo-fold mock (Brazil-Argentina) — must never be an active primary/secondary/recap.
10. **What must change?** Introduce a lifecycle SELECTOR that, from kickoff + status + recap_ready +
    model source, computes primary (earliest upcoming source-qualified, never finished, never op_estimated
    /archive/demo) + 1-2 secondary + latest finished recap, with roles/states/reasons; the homepage reads
    THAT artifact instead of the static selectedHotspot. When the primary finishes it rotates to recap and
    the next upcoming becomes primary.
