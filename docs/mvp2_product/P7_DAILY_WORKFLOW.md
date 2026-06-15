# P7 — Daily MVP Workflow (content + update mechanism)

> Owner P7 P0 (2026-06-15). The product no longer depends on chat memory or slate order: the
> persisted **selected_hotspot** is the authority, and **/internal/daily** surfaces readiness.
> MVP = manual + operator-confirmed; no auto-send, no fake recap, no invented score/probability,
> no betting/trading vocabulary, MTC = platform points (不可提现/不可转让/不可交易). Automated
> model/LLM execution is P1.

## The invariant

selected_hotspot → prediction artifact → homepage lead → /predict tactical room → T-30 readiness
→ observation/recap artifact → next-day recap lead → share/join operations.

## Daily steps

1. **Sync daily fixtures.** `python3 scripts/mvp2_match_sync.py sync --date YYYYMMDD` from
   `manual_scores_YYYYMMDD.md` → registry + recap_queue + runtime `frontend/public/data/daily-fixtures.json`.
   No score invented.
2. **Choose the selected hotspot.** Editorial pick (operator, LLM-assisted via
   `scripts/mvp2_editorial_agent.py prompt` — prompt-only, no API call, P1 for automation). Persist
   `docs/data_audit/mvp2_predictions/selected_hotspot_YYYYMMDD.json` AND update the bundled
   `frontend/src/data/selectedHotspot.json` (the build-time authority the homepage reads).
   `fixture_key` MUST equal the fixture's `leadKey` — the numeric `id` for a real fixture, the
   `manual:<H6>-<A6>-<date>` external_game_id for a manual one.
3. **Create the prediction artifact with data_snapshot + operator-confirmed strong call.**
   `frontend/src/data/predictionArtifacts/manual_<slug>.json`. Structured layers: `field_sources`
   (per-field source tags), `data_snapshot`/`modeling_output`/`generated_judgment` (null until the P1
   model+generation bridge fills them), `operator_confirmation` via the i18n `prediction` block. For
   MVP, `score_call`/`backup_score`/`risk_level`/`primary_direction` are `operator_confirmed`;
   `win_prob`/`confidence` stay `unavailable` (the frontend NEVER invents them — no fake probability).
4. **Homepage reads selected_hotspot.** `selectProductLoop` leads with the selected fixture when it is
   in the slate AND resolves to a prediction artifact. If the selection has no artifact, there is NO
   silent fallback to a different match as the official lead — `/internal/daily` flags it.
5. **/internal/daily checks readiness.** The operator opens the (unlinked, internal) readiness panel:
   selected==lead, artifact present, score-call present, share copy/card, T-30 status, observation/
   recap status, carryover, slate freshness, send=HOLD, and the operator links. Read-only; never sends.
6. **Operator shares the pre-match link/card** on Owner per-channel GO: `/predict/<key>?ref=<CODE>`,
   `/share/fixture/<key>?ref=<CODE>&lang=<l>` (QR), and the `mvp2_growth_cli.py package today` send-kit.
7. **T-30 artifact is updated or marked pending.** The artifact's `t30` slot is `pending` (honest
   checkpoint, no faked update) until lineups drop; the operator confirms `ready` (with `update_text`
   + `changed_fields`) or `skipped` (no change). The `#live30` block shows the pending/ready state.
8. **After full time create the observation artifact.** `observation_<id-or-fixture_key>.json` keyed by
   the SAME key the slate uses (P7 P0-5 carryover): pre_match_call → actual → 部分命中/偏差原因 →
   赛后校准关注 → 下一场影响 → 完整复盘确认后开放. `recap_ready:false` until a real recap exists (P1 A4).
9. **Next day the observation becomes the recap lead.** `featuredRecap` = the first finished fixture;
   its observation resolves by key (works for manual fixtures now). A new selected_hotspot becomes the
   prediction lead. The loop closes.
10. **Send remains manual only.** No auto-send anywhere; first send only on explicit Owner per-channel
    GO (see `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md`). MTC stays 不可提现/不可转让/不可交易.

## Guards (run before deploy)

`npm run build` · `check_homepage_product_loop.py` (lead == selected_hotspot, artifact-backed, score
teaser) · `check_prediction_artifact.py` (structure + field_sources + t30 + safe vocab) ·
`check_daily_readiness.py` (the end-to-end invariant) · `check_growth_copy.py` (no forbidden vocab;
scans the readiness page + selected_hotspot) · `check_customer_visible_copy.py <live>` (21/21) ·
`check_runtime_daily_fixtures.py --base-url <backend>`.

## P1 (deferred — separate Owner GO + API budget)

Automated model computation (Elo/form/H2H/Poisson for the daily hotspot) · automated DeepSeek/Gemini/
Kimi narrative execution · external-signal refresh · backend runtime artifact store (no-redeploy content
updates) · full A4 recap pipeline · advanced dashboard UI.
