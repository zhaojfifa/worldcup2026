# Growth P1.2b — Runtime Freshness Guard (frontend + backend)

> Owner verdict 2026-06-13: P1.2 CLI gate was not enough — the live frontend/API still
> showed pre-match copy for stale/finished fixtures (kickoff in the past but status still
> "scheduled"). HOLD all marketing sends until runtime enforcement is live.
> Goal: **no customer surface may present a live/finished/stale fixture as an active
> pre-match prediction.** No betting/trading vocab · no auto-send · no DB schema change.

## Root cause (confirmed)

Surfaces only flipped to recap when the bundled narrative `mode` became `real_recap`
(i.e. AFTER the A4 recap was generated). Between kickoff and recap-bundle, the narrative was
still `pre_match_*`, so `/predict`, `/share/fixture`, the homepage hero and strong-call cards
rendered a FRESH pre-match prediction for a match that had already kicked off / finished.
Stored `status` was trusted and could read "scheduled" for a past fixture.

## The fix — one canonical lifecycle spec, three runtimes

| layer | file | role |
|---|---|---|
| CLI / packaging | `scripts/mvp2_fixture_lifecycle.py` | P1.2 gate (unchanged states; stale-status rule added) |
| backend API | `backend/app/services/lifecycle.py` | response-time normalization, additive fields |
| frontend | `frontend/src/lib/freshness.ts` | defensive guard, computes from kickoffUtc |

Shared rule (the P1.2b core): **trust only EXPLICIT live/finished/halted signals; a stale
`NS`/`scheduled` never blocks time inference.** A fixture whose kickoff has passed is
LIVE/FINISHED even if status says scheduled. States: SCHEDULED · T_MINUS_2H · T_MINUS_30 ·
LIVE · FINISHED · RECAP_PENDING · RECAP_READY · ARCHIVED.

### 1. Backend runtime normalization (additive — no schema change)
`MatchListItem`/`MatchDetail` gain optional fields: `lifecycle_state`, `pre_match_allowed`,
`today_package_allowed`, `recap_needed`, `recap_ready`, `freshness_reason`. `match_service`
computes them at response time from `kickoff_time` + stored `status` (stale status ignored).
A finished/past fixture returns `pre_match_allowed=false`.

### 2. Frontend defensive guard (works even if backend says scheduled)
`computeFreshness()` / `fixtureFreshness()` from `kickoffUtc` + bundled narrative recap flag.
Surfaces guarded:
- **HomePage hero**: `pickActiveFixture()` selects at runtime — earliest pre-match fixture →
  latest RECAP_READY → latest RECAP_PENDING → empty (今日暂无可用赛前情报). No hardcoded permanent hero.
- **TrialHeroCard**: kickoff passed → frozen / recap-pending / recap-ready (链接 /recap), never pre-match.
- **/predict/:id** (`PredictPage`): kickoff passed + not recap → frozen state (⏸️ 比赛进行中 / 🗂️ 复盘生成中);
  recap mode → redirect to /recap (existing).
- **/share/fixture/:id** (`ShareCardPage`): LIVE/FINISHED → frozen share card; RECAP_READY → redirect /share/recap.
- **UpcomingTacticalStrip / RescoreHookCard / HotTopicsSection**: exclude/guard kickoff-passed fixtures.

### 3. Scanner (`scripts/check_fixture_freshness.py`)
Now asserts the runtime guard is WIRED on every surface (HomePage pickActiveFixture; PredictPage,
ShareCardPage, home cards fixtureFreshness). If wired, a finished fixture with a stale pre-match
narrative is a WARN (runtime freezes it; recap still owed); if the guard is MISSING it is a FAIL.
Hardcoded permanent hero pin of a finished fixture = FAIL. Stale package files = FAIL (self-clear on refresh).

## Verification (2026-06-13, branch feature/mvp2-growth-p1-2b-runtime-freshness)

- Build: **PASS** (tsc -b + vite build; selftest excluded from app tsconfig — no @types/node leak).
- Lifecycle selftests: CLI **14/14**, backend **7/7**, frontend **8/8** — all include Owner §6 cases A/B/C/D.
- Backend integration: stale 8-day-past `scheduled` → `RECAP_PENDING`, `pre_match_allowed=false`.
- Visible-copy scan: **21/21 PASS** (7 routes × zh/vi/my, headless Chrome vs built dist).
- Freshness scanner: **PASS** (4 guards WIRED); forced-LIVE sim → only stale package files FAIL,
  which self-clear via `refresh` (proven: refresh under LIVE writes REFUSED stubs → scanner PASS).
- **Real browser (dev server, clock mocked to 2026-06-14T01:00Z, ~3h post-kickoff):**
  - `/predict/1489371` → frozen "🗂️ 比赛已结束 · 赛后复盘生成中", no StrongCallCard, no pre-match view.
  - Homepage hero → re-selected to recap-ready 1489369 "比赛已结束 · 查看复盘", no score, no rescore hook.
  - Console errors: none. After reload (mock cleared) real pre-match state intact (1489371 2-1).
- Guards: growth copy PASS · no betting/trading vocab in new files · no auto-send/network code.

## Owner §6 test cases
A future (1489371) → pre-match allowed · B past stale-scheduled (BRA-ARG/MAR-FRA/ESP-GER 06-05/06/07)
→ pre-match REFUSED · C finished recap-ready (1489369) → recap allowed, pre-match refused ·
D synthetic live (now-20min, scheduled) → LIVE, pre-match refused. All encoded in the three selftests.

## Deploy (operator — engineering holds no creds)
Backend changed (API normalization) + frontend changed (UI guard). Order: **backend → frontend →
live freshness scan**. No DB migration. After deploy: `check_customer_visible_copy.py` (21/21) +
re-run the mocked-clock /predict check on the live bundle.

## Not done / follow-up
- Backend `recap_ready` is conservative (kickoff+status only; recap availability not cross-checked
  against the recap service) — safe (never shows pre-match); frontend uses the bundled narrative for recap_ready.
- Live-URL DOM scanning of /predict & /share for finished fixtures still relies on
  `check_customer_visible_copy.py` (headless Chrome) — the freshness scanner stays source/manifest-based.
