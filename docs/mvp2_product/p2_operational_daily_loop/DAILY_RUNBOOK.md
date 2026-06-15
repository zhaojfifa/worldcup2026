# P2 · DAILY_RUNBOOK

> The operator's copy-paste daily sequence. All steps are LOCAL (no send, no auto-publish). Replace
> the date as needed. Nothing here sends to a customer channel.

## Morning → publish
```
python3 scripts/mvp2_daily_ops.py status         --date 2026-06-15   # what's the state?
python3 scripts/mvp2_daily_ops.py build-queue    --date 2026-06-15   # slate → priority → primary+secondary
python3 scripts/mvp2_daily_ops.py generate-drafts --date 2026-06-15 --provider deepseek   # LLM drafts (add --live for a real call)
python3 scripts/mvp2_daily_ops.py review-summary --date 2026-06-15   # what needs operator review?
#   → operator reviews each generated draft, writes/edits the reviewed JSON under
#     docs/data_audit/mvp2_predictions/reviewed/<YYYYMMDD>_<fixture>_reviewed.json
python3 scripts/mvp2_daily_ops.py build-artifacts --date 2026-06-15  # build ONLY from reviewed JSON (gate)
```

## Match day → close
```
python3 scripts/mvp2_daily_ops.py t30-status     --date 2026-06-15   # KO-30: confirm lineups, set t30
python3 scripts/mvp2_daily_ops.py recap-status   --date 2026-06-15   # FT: observation / full recap state
python3 scripts/mvp2_daily_ops.py share-refresh  --date 2026-06-15   # share cards ready?
python3 scripts/mvp2_daily_ops.py close-day      --date 2026-06-15   # day-close summary + next action
```

## Publish to the live site (operator, when content changes)
- Frontend bundles the artifacts + dailyOpsState.json at build → Render Manual Deploy.
- Runtime slate (backend): `ADMIN_API_TOKEN=<prod> python3 scripts/mvp2_match_sync.py upload --date 2026-06-15 --target production` (operator token; clears runtime MATCH).

## Verify
```
python3 scripts/check_runtime_daily_fixtures.py --base-url https://worldcup2026-api-71n6.onrender.com --expected-date 2026-06-15 --expected-fixture 1489377
python3 scripts/check_daily_ops_loop.py && python3 scripts/check_operator_review_queue.py && python3 scripts/check_t30_queue.py && python3 scripts/check_recap_queue.py && python3 scripts/check_share_package_refresh.py && python3 scripts/check_internal_daily_command_center.py
```
Open `/internal/daily` → command center shows runtime MATCH + all queues + next action + Send HOLD.

## Send (NEVER automatic)
Sending stays HOLD. A send happens only on explicit Owner per-channel GO, manually, outside this loop.
