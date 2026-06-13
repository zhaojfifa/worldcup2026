# Growth P1.4 — Match-to-Product Orchestration

> Owner verdict 2026-06-13: P1.3c synced fixtures + live backend, but the product did not translate
> the registry into visible product flow — completed matches (Canada/USA/SK), recap-ready (Mexico),
> and upcoming-needs-narrative (Qatar/Haiti) were not surfaced. P1.4 connects the daily registry to
> the homepage, recap queue, package refresh, and operator actions. No auto-send · no betting vocab ·
> no fake recaps · no invented scores · no customer recap for a no-narrative fixture.

## Homepage product sections (§2)

The homepage now derives four sections from the runtime manifest fixtures (works across
backend/static/bundled tiers):
- **A. Current Hero** — earliest scheduled renderable pre-match fixture (Brazil vs Morocco).
- **B. Recap Desk** (`MatchDesk.RecapDesk`) — every finished fixture with the correct state:
  - RECAP_READY + mapped → **查看复盘** button → /recap/:id  (Mexico 2-0)
  - finished + mapped, no recap → **复盘生成中**  (Canada 1-1)
  - finished + unmapped → **待生成复盘**  (USA 4-1, South Korea 2-1)
- **C. Upcoming / Needs Pre-match** (`UpcomingNeedsNarrative`) — scheduled fixtures with no narrative:
  **待生成赛前判断**  (Qatar vs Switzerland, Haiti vs Scotland).
- **D. Operator Status Line** — `赛程已同步 · 复盘队列已更新 · 下一场赛前判断已就绪` (no source URLs, no betting wording).

The 查看复盘 button is gated on `recapReady` — a pending recap can NEVER be shown as ready.

## Recap queue command (§3)

`python3 scripts/mvp2_match_sync.py recap-queue --date 2026-06-13` →
`docs/data_audit/mvp2_match_sync/recap_queue_classified_YYYYMMDD.json` + console:
```
Mexico vs South Africa        2-0  RECAP_READY                复盘已就绪 — 可出复盘包 / 上首页查看复盘
Canada vs Bosnia...           1-1  NEEDS_A4_RECAP             已映射内部赛事，缺复盘叙事 — 运行 A4 (mvp2_ops.py recap --fixture 1539000)
United States vs Paraguay     4-1  NEEDS_MAPPING_OR_A4_RECAP  未映射内部赛事 — 先采集映射 internal_fixture_id，再运行 A4 复盘
South Korea vs Czechia        2-1  NEEDS_MAPPING_OR_A4_RECAP  未映射内部赛事 — 先采集映射 internal_fixture_id，再运行 A4 复盘
```

## Package refresh integration (§4)

`refresh` now emits an `orchestration` block in the summary JSON:
`today=Brazil`, `recap=Mexico (recap_ready)`, `recap_queue_pending=[Canada, USA, South Korea]`,
`upcoming_without_narrative=[Qatar, Haiti]`. No package is fabricated for Canada/USA/SK
(they have no narrative → `needs_narrative`; recap target stays Mexico).

## Backend shaping (§5)

`GET /api/v1/daily-fixtures` now includes product buckets: `completed_matches` (each with
`recap_status` RECAP_READY / NEEDS_A4_RECAP / NEEDS_MAPPING_OR_A4_RECAP), `upcoming_needs_narrative`,
and `product_status`. Additive response fields; the frontend derives the same buckets locally so it
works on the static/bundled tiers too.

## Scanner (§6)

`check_match_sync_freshness.py` extended — FAIL if HomePage does not render RecapDesk /
UpcomingNeedsNarrative / OperatorStatusLine, if RecapDesk does not iterate finished manifest
fixtures, if the 查看复盘 button is not gated on `recapReady`, or if the 待生成赛前判断 label is missing.
(Plus the existing P1.2/P1.3 checks: finished-as-today, completed-absent, hardcoded-hero, score-conflict.)

## Verification (2026-06-13, branch feature/mvp2-growth-p1-4-orchestration)

Real browser (homepage): hero Brazil vs Morocco; Recap Desk shows Canada 1-1 **复盘生成中**, USA 4-1
**待生成复盘**, Mexico 2-0 **查看复盘** (only RECAP_READY gets the button), South Korea 2-1 **待生成复盘**;
Upcoming shows Qatar/Haiti **待生成赛前判断**; operator status line present; 0 console errors.
Backend (TestClient): `completed_matches` + `upcoming_needs_narrative` + `product_status` correct.
recap-queue command + refresh orchestration block match the Owner's expected results.
Guards: match-sync 8/8 · backend lifecycle 7/7 · frontend freshness 8/8 · runtime scanner PASS ·
match-sync scanner PASS · P1.2 scanner PASS · growth copy guard PASS · build PASS · visible 21/21 ·
no betting vocab · no customer auto-send · no DB shape change (backend response is additive).

## Deploy impact
Backend response shape changed (additive buckets) → deploy backend first; frontend changed (sections) →
deploy frontend. After deploy + an operator upload, the live homepage shows the full orchestration view,
updatable without a frontend rebuild (backend tier). Recap narratives for Canada/USA/SK remain a
separate guard-gated A4 step (recap-queue lists them; never fabricated).
