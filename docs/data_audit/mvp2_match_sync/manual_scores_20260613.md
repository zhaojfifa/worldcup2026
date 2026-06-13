# Manual match input — 2026-06-13 (P1.3 Match Sync, manual source mode)

> Operator/Owner-provided slate. SOURCE OF TRUTH for P1.3 manual mode.
> Rules: do NOT invent scores. A score that is not confirmed = `unknown`.
> Format (one fixture per line, parsed by scripts/mvp2_match_sync.py):
>   `Home <h>-<a> Away — finished`     (final score known)
>   `Home vs Away — scheduled`         (no score)
>   `Home vs Away — unknown`           (status unconfirmed)
> Team names are matched against the alias table in the sync script.

Canada 1-1 Bosnia and Herzegovina — finished
United States 4-1 Paraguay — finished
Mexico 2-0 South Africa — finished
South Korea 2-1 Czechia — finished
Brazil vs Morocco — scheduled
Qatar vs Switzerland — scheduled
Haiti vs Scotland — scheduled

<!--
Provenance: Owner instruction 2026-06-13 (P1.3 verdict). Scores stated by Owner:
Canada 1-1 Bosnia, United States 4-1 Paraguay, Mexico 2-0 South Africa, South Korea 2-1 Czechia.
Scheduled (no score): Brazil vs Morocco (KO 22:00 UTC today), Qatar vs Switzerland, Haiti vs Scotland.
No score is invented here; scheduled fixtures carry no score.
-->
