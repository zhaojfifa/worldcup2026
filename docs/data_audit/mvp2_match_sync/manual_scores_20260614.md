# Manual match input — 2026-06-14 (P1.3 Match Sync, manual source mode)

> Operator/Owner-provided slate. SOURCE OF TRUTH for P1.3 manual mode.
> Rules: do NOT invent scores. A score that is not confirmed = `unknown`.
> Format (one fixture per line, parsed by scripts/mvp2_match_sync.py):
>   `Home <h>-<a> Away — finished`     (final score known)
>   `Home vs Away — scheduled`         (no score)
>   `Home vs Away — unknown`           (status unconfirmed)
> Team names are matched against the alias table in the sync script.

Brazil 1-1 Morocco — finished
Mexico 2-0 South Africa — finished
Netherlands vs Japan — scheduled
Germany vs Curacao — scheduled
Ivory Coast vs Ecuador — scheduled
Sweden vs Tunisia — scheduled
Australia vs Turkey — scheduled

<!--
Provenance: Owner instruction 2026-06-14 (manual daily refresh). Owner-stated facts:
  - Brazil 1-1 Morocco (yesterday's hotspot, now FINISHED) — becomes the recap-priority story.
    Recap narrative is NOT yet bundled for 1489371 (only pre_match_2026_modeling exists) → it must
    render as 复盘准备中 / 等待赛后校准, NEVER a fabricated recap.
  - Netherlands vs Japan = today's featured pre-match (scheduled, no score-call invented here).
  - Mexico 2-0 South Africa carried over as the secondary recap only (real_recap bundled = recap_ready).
  - Germany vs Curaçao / Ivory Coast vs Ecuador / Sweden vs Tunisia / Australia vs Turkey = today's
    lightweight schedule (scheduled, no scores invented).
No score is invented; scheduled fixtures carry no score. Owner did NOT confirm scores for the new
06-14 fixtures, so they stay scheduled.
-->
