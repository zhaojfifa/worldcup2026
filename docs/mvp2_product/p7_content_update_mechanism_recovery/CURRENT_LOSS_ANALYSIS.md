# P7 — CURRENT_LOSS_ANALYSIS

> What is currently lost or disconnected, by category. "Lost" here rarely means deleted — it almost always
> means **fixture-locked, dead, disconnected, or undocumented-as-a-page**.

## Content loss

**Which rich fields are NOT produced for daily manual fixtures?**
For a new id=null hotspot (Netherlands–Japan), the data/model + LLM pipeline produces **nothing**. It is locked
to ~5 sample fixtures by three gates a daily fixture fails: (1) the **Scout Pack gate** — the frame builders read
`docs/data_audit/mvp2_scout_pack_samples/{fid}.json`, which exists only for the samples; (2) the **known-id gate**
— `mvp2_match_sync.KNOWN` maps only 3 fixtures, so others get `internal_fixture_id=null` + `narrative_renderable=false`;
(3) the **bundled-data gate** — `getProductNarrative(manualFixture)` returns `null`. So none of `tactical_read`,
LLM `risk_factors` (with source_refs), the rescore model, or the A4 recap are produced for the daily hotspot.

**Which are hand-filled only?**
Everything rich on the live homepage lead: `score_call` (2-1), `backup_score` (1-1/2-2), `risk_level` (中高),
`primary_direction` (赛前倾向荷兰…), `top_variable`, `why`, `tactical_matchup[]`, `risk_variables[]`,
`external_expectation[]`, `thirty_minute_checklist[]` — all hand-typed in one flat file
`predictionArtifacts/manual_Nether-Japan-20260614.json` (`source:"operator_confirmed"`). **There is no generator
script for prediction artifacts** (grep for `operator_confirmed`/`prediction_confirmed` finds only the guard). The
recap is the same: `observation_1489371.json` is hand-"recovered", `recap_ready:false`.

**Which SHOULD come from data/model?** (deterministic, only need team names + the kaggle CSV — no Scout Pack strictly
required for Elo/form/H2H): `score_call`/`backup_score` (Poisson `poisson_bands`), `risk_level` (`upset_band`),
`main_lean`/`primary_direction` (Elo `favoured`), and a `source_ref` on every `risk_variable`. Today these are typed
by hand with no provenance and pass `check_prediction_artifact.py` identically to a model-derived value.

**Which SHOULD come from LLM/operator?** LLM: `tactical_matchup`, `why`/`risk_note`, `external_expectation` (only when
a recorded signal exists), the t30 rescore copy, the recap narrative — the contracts/prompts/guards already exist
(`mvp2_generate_*` + `check_mvp2_product_narrative_guard.py`), just not invoked for non-sample ids. Operator
(legitimately): which match is the hotspot (editorial selection) + per-channel GO. The current artifact tier
**deliberately accepts operator judgement as the source of truth** — which is exactly where the "data-backed" pillar
is lost for the daily loop.

## Update mechanism loss

**Where is daily update documented?** `docs/mvp2_product/P6_DAILY_WORKFLOW.md` (7 steps) + the (slightly stale)
`p6_discovery_recovery/DAILY_UPDATE_FLOW.md`. The SLATE pipeline is also documented in `GROWTH_P13*`/`GROWTH_P14`.

**Is there an update mechanism page?** **No.** The only internal page is `/internal/growth` (GrowthAdminPage), which
is the **ambassador** dashboard (codes/clicks/contributions), not a content/update-readiness page. There is no
`/internal/daily`, no content-readiness panel, no nav entry for one.

**Is selected_hotspot persisted?** Yes as a file (`docs/data_audit/mvp2_predictions/selected_hotspot_20260614.json`)
— but **read by no code** (grep: 0 hits in `.py/.ts/.tsx`). The homepage lead is bound INDIRECTLY by slate-order +
`hasPredictionArtifact(leadKey)`, not by reading that file. So the persisted editorial decision and the runtime lead
can drift apart silently.

**Is the T-30 artifact persisted?** **No.** For the sample fixtures there is a rescore model (`rescoreModels/{id}.{lang}.json`);
for a daily manual fixture there is only the static `thirty_minute_checklist` inside the prediction artifact and the
`#live30` anchor. The actual T-30 update is sent in-group manually and persisted nowhere.

**Is the recap artifact persisted?** Yes for the tracked fixture (`observation_1489371.json`), bundled at build time.
But it is hand-recovered, `recap_ready:false`, not the A4 pipeline output.

**Is tomorrow's recap tied to yesterday's prediction?** **Partially, and broken for manual fixtures.**
`selectProductLoop` makes `featuredRecap` = the first FINISHED fixture and `/recap/:id` resolves the observation
artifact — but **OBSERVATION is keyed by numeric id only** (`{'1489371':…}`) and the recap zone links via `f.id`.
A manual hotspot (id=null) has no numeric id, so its observation cannot be resolved/linked the next day without first
assigning a real id. The carryover works for real-id fixtures, not for the manual hotspots the daily loop actually uses.

## Page loss

**Which page used to explain/surface the update mechanism?** There never was a dedicated content/update page — the
update mechanism was always scripts + docs + the homepage sync line (`⟳ 赛程更新 … · 实时|静态备份|内置`). The closest
operator surface is `/internal/growth` (ambassador only).

**Is it missing from nav?** `/internal/growth` is intentionally unlinked (admin-gated). There is no content/update page
to be missing.

**Is it missing from the internal/operator page?** Yes — `/internal/growth` shows ambassador metrics, NOT: which fixture
is today's selected hotspot, whether its prediction artifact exists, whether T-30 / observation / recap are ready, or
the per-channel send-kit/QR links. An operator cannot see content readiness anywhere in the UI.

**Was it replaced by HomeProductLoop?** Partly. The P1.4 `MatchDesk.tsx` (RecapDesk / UpcomingNeedsNarrative /
OperatorStatusLine) — the closest thing to a content/update surface — is **dead code** (never imported), superseded by
`HomeProductLoop`. Its internal-state chips (复盘生成中 / 待生成复盘 / 待生成赛前判断) were exactly the leakage P3/P6
banned from the customer homepage, so it could not be the customer surface; but nothing replaced its operator-status role.

## Operations loss

**Are share copy/card/ref/join tied to the selected hotspot?** Tied to the **fixture**, not to the persisted
`selected_hotspot`. `shareTemplates`/`ShareBlock`/`ShareCardPage` build copy + `/share/{fixture|recap}/:id?ref=` + QR
from the fixture id/key and the canonical projection (or the artifact). The DEFAULT_REF codes (QG-TEST1/TT-VN88/FO-MM21)
are live in `shareTemplates.ts`. The `selected_hotspot` file is not consulted, so "today's official hotspot" and "what a
share link points to" are only coincidentally aligned.

**Can the operator know what to send today, at T-30, and after FT?**
- **Today (pre-match):** Yes, via the CLI — `mvp2_growth_cli.py refresh/package` writes lifecycle-gated send-kits to
  `docs/data_audit/mvp2_growth_packages/{today,next,recap}_<fid>_<lang>_<CODE>.md` + the `FIRST_SEND_RUNBOOK`. But it is
  CLI/file-only; there is no UI, and the send-kit is per-fixture-id (the manual hotspot needs the artifact/manifest to be present).
- **At T-30:** Only by hand. No persisted T-30 artifact, no UI prompt; the operator watches lineups and writes the group
  message themselves (the `#live30` anchor + static checklist are the only on-page support).
- **After FT:** The observation receipt exists for a tracked real-id fixture; for a manual hotspot the operator must
  hand-author an observation artifact (no generator, no UI), and it cannot be linked next-day until an id is assigned.
- **Residual hardcode:** `mvp2_growth_cli.py` recap branch still literally emits "Brazil vs Morocco" / 1489371 in the
  next-hook + video script (the frontend `NEXT_HOOK` was de-hardcoded in P6; the CLI mirror was not) — any non-1489371
  recap kit emits a wrong "next match".

## Net
The **update PLUMBING** (slate sync → registry → runtime → backend → homepage; share/ambassador) is intact and live.
The **content ENGINE** (data/model → LLM) is disconnected from the daily loop; the **editorial decision** is persisted
but unread; there is **no operator content-readiness page**; and the **manual-fixture recap carryover + CLI recap hook**
have concrete gaps. This is recoverable with existing assets — see TARGET_CONTENT_UPDATE_FLOW.md and P7_IMPLEMENTATION_PLAN.md.
