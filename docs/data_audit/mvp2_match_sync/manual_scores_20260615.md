# Manual match input — 2026-06-15 (P1.3 Match Sync, manual source mode)

> Operator/Owner-provided slate. SOURCE OF TRUTH for P1.3 manual mode.
> Rules: do NOT invent scores. A score that is not confirmed = `unknown`.
> Format (one fixture per line, parsed by scripts/mvp2_match_sync.py):
>   `Home <h>-<a> Away — finished`     (final score known)
>   `Home vs Away — scheduled`         (no score)
>   `Home vs Away — unknown`           (status unconfirmed)
> Team names are matched against the alias table in the sync script.

Belgium vs Egypt — scheduled
Saudi Arabia vs Uruguay — scheduled
Spain vs Cape Verde Islands — scheduled
Brazil 1-1 Morocco — finished
Mexico 2-0 South Africa — finished
Sweden vs Tunisia — unknown

<!--
Provenance: matches the deployed 2026-06-15 slate (frontend/public/data/daily-fixtures.json +
bundled prediction artifacts). Real API-FOOTBALL fixture IDs (Belgium-Egypt 1489377, Saudi-Uruguay
1489379, Spain-CapeVerde 1489380, Brazil-Morocco 1489371, Mexico-SA 1489369, Sweden-Tunisia 1539002).
  - Belgium vs Egypt = today's primary hotspot (selectedHotspot authority); scheduled, no score.
  - Saudi Arabia vs Uruguay + Spain vs Cape Verde Islands = today's secondary content-factory matches
    (scheduled, prediction artifacts bundled). No scores invented.
  - Brazil 1-1 Morocco = yesterday's hotspot, FINISHED → recap-priority (observation receipt only;
    full recap blocked, NOT fabricated).
  - Mexico 2-0 South Africa = secondary recap (real_recap bundled → recap_ready).
  - Sweden vs Tunisia = finished status unconfirmed → `unknown` (no score invented).
No score is invented; scheduled/unknown fixtures carry no score.
-->
