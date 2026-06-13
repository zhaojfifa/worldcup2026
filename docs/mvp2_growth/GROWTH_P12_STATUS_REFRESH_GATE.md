# Growth P1.2 — Status Refresh Gate（freshness over prediction）

> Owner instruction 2026-06-13: the critical product failure is FRESHNESS, not prediction
> accuracy. A finished or live match displayed as an active pre-match prediction collapses
> user trust. P1.2 builds the simplest reliable scheduled/manual status-refresh mechanism.
> Scope: CLI + lifecycle manifest + stale-surface scanner + local cron docs + reference
> template. NO auto-send · NO backend/DB change · NO dashboard change · NO frontend change.

## 1. Canonical fixture lifecycle

One source of truth: `scripts/mvp2_fixture_lifecycle.py` (pure `decide()` + `gates()`,
selftest embedded). States in order:

| state | meaning | pre-match/today pkg | recap pkg |
|---|---|---|---|
| SCHEDULED | pre-match prediction allowed | ✅ | ❌ |
| T_MINUS_2H | operator watch starts (≤120min) | ✅ | ❌ |
| T_MINUS_30 | A3 rescore path allowed (≤30min) | ✅ | ❌ |
| LIVE | pre-match copy FROZEN | ❌ | ❌ |
| FINISHED | final-whistle window (recap job not due, FT+45) | ❌ | ✅ |
| RECAP_PENDING | finished, recap not bundled — 赛后复盘生成中 | ❌ | ✅ |
| RECAP_READY | bundled real_recap exists | ❌ | ✅ |
| ARCHIVED | recap ready + kickoff >72h ago — 历史复盘档案 | ❌ | ❌ |

Safety decisions: kickoff passed without a finished signal → LIVE (freeze, even if the API
still says NS); API halted statuses (PST/CANC/ABD/AWD/WO) → all packaging refused; FINISHED
inferred from time alone ONLY when the API gave no status (kickoff +130min estimate).
Status sources recorded per fixture: `api_football` → `bundled_narrative` → `time_inference`.

## 2. Commands

```bash
python3 scripts/mvp2_growth_cli.py status-refresh [--no-api] [--fixture ID]
#   -> docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_YYYYMMDD_HHMM.json
#      (fixture_id/teams/kickoff_time_utc/current_time_utc/previous_state/new_state/
#       status_source/score_if_finished/pre_match_allowed/today_package_allowed/
#       recap_needed/recap_ready/recap_package_allowed/reason)
python3 scripts/check_fixture_freshness.py [--no-api]    # stale-surface scanner, exit 1 = stale
python3 scripts/mvp2_fixture_lifecycle.py --selftest      # 12 state cases + gate matrix
```

## 3. Package gating（wired into build_package/cmd_refresh）

- `package today|next`: lifecycle gate runs FIRST; refusal = `LIFECYCLE_GATE … state=… — reason`.
- `package recap`: only FINISHED / RECAP_PENDING / RECAP_READY.
- `refresh`: per-package `lifecycle_state` + `lifecycle_gate` in the .md body and summary JSON;
  today refused/unavailable → prints `NO_VALID_TODAY_FIXTURE` + `today_gate` field in summary;
  a lifecycle refusal OVERWRITES previously generated today/next files with a REFUSED stub
  (stale paste-ready copy physically removed).

## 4. Acceptance evidence（run 2026-06-13 ~01:31–01:35 UTC, branch feature/mvp2-growth-p1-2-status-refresh）

1. Finished fixture as today package → REFUSED:
   `package today --fixture 1489369` → `LIFECYCLE_GATE today refused: 1489369 state=RECAP_READY` (exit 1). ✅
2. Live fixture as fresh pre-match → REFUSED (in-process simulation, 1489371 forced LIVE):
   refresh → today+next `refused`, `NO_VALID_TODAY_FIXTURE`, REFUSED stub written over the
   today file (`今晚主看` gone). Simulation artifacts removed; real packages regenerated. ✅
3. Lifecycle JSON written: `docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_20260613_0131.json`. ✅
4. Package outputs carry the gate decision (`lifecycle_state`/`lifecycle_gate` in .md + summary). ✅
5. Stale scanner catches finished-as-prediction: synthetic stale `today_1489369_*.md` → 
   `STALE … still offers pre-match copy for a RECAP_READY match` (exit 1); cleaned up. ✅
6. Cron documented: `docs/mvp2_growth/GROWTH_P11B_SCHEDULED_REFRESH.md` §3b. ✅
7. No auto-send code anywhere (status-refresh/scanner only write/read local files). ✅
8. Growth copy guard: 13 files PASS + selftest 6/6 (guard caught and we removed a process word
   in a docstring — the .py-docstring lesson holds). ✅
9. External references reference-only + customer-safe: `EXTERNAL_REFERENCE_TEMPLATE.md` +
   `external_reference_20260613.md` (AWAITING OPERATOR DATA, nothing fabricated). ✅
10. Real lifecycle states @01:31 UTC: **1489369 RECAP_READY · 1489371 SCHEDULED (T-1229min) ·
    1539000 RECAP_PENDING** — all via `api_football`; `--no-api` fallback verified
    (`bundled_narrative` / `time_inference`). ✅

## 5. Live deploy impact

ZERO frontend/backend change — scripts + docs only. No deploy needed for P1.2 itself; the
pending main (0a73ee6) frontend deploy for canonical projection is unchanged and unaffected.
HomePage hero pins (`fixtureId="1489371"`) are deploy-bound: after 1489371 finishes, the hero
becomes stale-by-construction → `check_fixture_freshness.py` FAILs on it until an engineer
updates the pin + operator redeploys (this is the designed alarm, not a bug).

## 6. Known limits / P1 notes

- Refresh summary stamp is minute-granular: two `refresh` runs in the same minute overwrite one
  summary (cron spacing of 5min avoids it; pre-existing behavior, noted 2026-06-13).
- 1539000 is not bundled in the frontend (register-path A2 only) — scanner reports it as
  lifecycle-gate-only WARN, no customer surface exists.
- ARCHIVED recap refusal means very old fixtures need the recap page (历史复盘档案), not a
  recap share package — intentional per Owner §1.
