# P6 — Daily MVP Workflow (product · update · operation)

> Owner P6 (2026-06-15). The operational source of truth for running the AI football-intelligence
> product day to day. Consolidates the product/update/operation flow (discovery analysis lives in
> `docs/mvp2_product/p6_discovery_recovery/`: PRODUCT_FLOW_RECOVERY.md · DAILY_UPDATE_FLOW.md ·
> OPERATIONS_FLOW.md). MVP = manual + operator-confirmed; no auto-send, no fake recap, no invented
> score/probability, no betting/trading vocabulary, MTC = platform points (不可提现/不可转让/不可交易).

## Product flow (the loop)

今日热点预测（score-call teaser）→ 进入战术室（strong call + 深度分析 + T-30 #live30）→ 复制/分享/进群
→ 赛后回执（昨日主推回执 · 实际比分 · 部分命中 · 偏差原因 · 赛后校准关注 · 下一场影响）→ 次日热点。

## Daily steps (manual MVP)

1. **Sync daily fixtures.** `python3 scripts/mvp2_match_sync.py sync --date YYYYMMDD`
   (operator `manual_scores_YYYYMMDD.md` → `daily_fixtures_*.json` + runtime
   `frontend/public/data/daily-fixtures.json`). No score invented; unconfirmed = unknown.
2. **Choose the selected hotspot.** Editorial pick (operator, optionally LLM-assisted via
   `scripts/mvp2_editorial_agent.py prompt`). Persist it as
   `docs/data_audit/mvp2_predictions/selected_hotspot_YYYYMMDD.json` (durable + auditable — a
   re-sync no longer silently wipes the decision).
3. **Create the prediction artifact with an operator-confirmed score call.**
   `frontend/src/data/predictionArtifacts/manual_<slug>.json` — `source=operator_confirmed`,
   `prediction_confirmed=true`, a qualitative scout call with a reference scoreline (NOT a precise
   probability; `confidence=null`). Customer-safe vocabulary only; `external_expectation` uses safe
   terms only. The frontend NEVER invents score/probability — unconfirmed numerics render as the
   pending labels (方向待临场确认 / 比分待开球前 30 分钟确认).
4. **Homepage points ONLY to an artifact-backed hotspot.** `selectProductLoop` makes the lead the
   first scheduled fixture that resolves to a prediction artifact (`hasPredictionArtifact`). If no
   artifact exists, that match CANNOT be the lead prediction (no hollow score-call hook).
5. **T-30 update or placeholder.** The artifact carries the `thirty_minute_checklist` + T-30 hook
   (#live30 anchor in the tactical room). At kickoff −30 (lineups out) the operator re-confirms the
   call in-group; the pre-match surface freezes once kickoff passes (lifecycle guard).
6. **After the match, create the observation artifact.**
   `frontend/src/data/predictionArtifacts/observation_<id>.json` — 昨日主推回执 → 实际比分 →
   部分命中/偏差原因 → 赛后校准关注 → 下一场影响 → 完整复盘确认后开放. `recap_ready=false` until a full
   recap is confirmed; never a fake recap, no hindsight brag.
7. **Next day, the same fixture becomes the recap story.** Yesterday's hotspot leads
   昨日热点复盘 (trust receipt); the new selected hotspot leads 今日热点预测.

## Required daily artifacts

| # | artifact | path | manual/auto |
|---|---|---|---|
| 1 | daily fixture slate | `docs/data_audit/mvp2_match_sync/daily_fixtures_YYYYMMDD.json` + runtime `frontend/public/data/daily-fixtures.json` | auto (from manual scores) |
| 2 | selected hotspot key | `docs/data_audit/mvp2_predictions/selected_hotspot_YYYYMMDD.json` | manual (operator) |
| 3 | prediction artifact (strong call) | `frontend/src/data/predictionArtifacts/manual_<slug>.json` | manual (operator-confirmed) |
| 4 | share copy | embedded in the artifact `operations.share_copy` + `scripts/mvp2_growth_cli.py package` | manual/auto |
| 5 | T-30 placeholder/update | artifact `thirty_minute_checklist` + in-group T-30 message | manual |
| 6 | observation artifact | `frontend/src/data/predictionArtifacts/observation_<id>.json` | manual (post-match) |
| 7 | full recap artifact | when confirmed (`recap_ready=true`) | manual / deferred (P1) |

## Manual now vs automated later (P1)

- **Manual now:** editorial selection, operator-confirmed prediction/observation artifacts, T-30
  in-group re-confirmation, all sends (per the first-send gate + Owner per-channel GO).
- **Automated later (P1, NOT in P6):** LLM ProductNarrative generation, external-signal auto-refresh,
  a full daily artifact scaffolder CLI, a full recap pipeline.

## Operations (must preserve)

Send only on Owner per-channel GO. Pre-match: send the artifact's `share_copy` + `/share/fixture/<key>`
card (QR carries the ref code). T-30: send the in-group re-confirmation. After full time: send the
observation receipt (`/recap/<id>`). Do NOT: auto-send · use betting/trading vocabulary · publish a
fake recap · invent a score/probability · imply MTC is cash/withdrawable/transferable/tradeable.
Full operator detail: `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md` ·
`docs/mvp2_product/p6_discovery_recovery/OPERATIONS_FLOW.md`.
