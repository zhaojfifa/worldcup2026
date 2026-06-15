# P2 · SHARE_PACKAGE_REFRESH_SPEC

> Durable queue: `docs/data_audit/mvp2_share_packages/<date>.json`. Guard:
> `scripts/check_share_package_refresh.py`.

## Item status
`SHARE_READY` (the artifact carries `i18n.zh.operations.share_copy` and a `/share/fixture/<id>` route)
· `SHARE_MISSING` (no share copy — add it before publishing the card).

## Rule (guarded)
A `SHARE_READY` item must name its `/share/...` route in `next_action`. The share card + recap share
card render from the same artifacts (prediction `share_copy`; recap falls back to the observation
`share_copy`). No betting vocab, no fake probability — inherited from the artifact guards.

## Today (2026-06-15): 3 items (Belgium/Saudi/Spain) all SHARE_READY → /share/fixture/<id>.
