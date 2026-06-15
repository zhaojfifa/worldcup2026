# R1 — UPDATE_AND_OPERATIONS_FLOW

> The daily operational mechanism. Operation remains **PAUSED / small private trial only**; all sends
> manual + Owner per-channel GO; engineering holds no prod token. Nothing here sends anything.

## Morning (slate + content build)
1. `python3 scripts/mvp2_match_sync.py sync --date YYYYMMDD` — refresh the daily slate (manifest +
   recap queue). Backbone unchanged.
2. Confirm / set `frontend/src/data/selectedHotspot.json` to today's hotspot (P7 mechanism, unchanged).
3. `python3 scripts/mvp2_build_daily_prediction_artifact.py prompt --date YYYYMMDD` — model-lookup +
   write `source_facts`/`model_fields` + generate the prompt file.
4. Paste the prompt into DeepSeek/Gemini/Kimi (manual). Review the JSON for facts, compliance, language.
5. Save reviewed JSON to `docs/data_audit/mvp2_predictions/reviewed/...`.
6. `python3 scripts/mvp2_build_daily_prediction_artifact.py apply --reviewed <file>` — merge into the
   artifact.
7. `npm run build` + run all guards (incl. `check_daily_content_flow.py`). Operator deploys frontend.
8. Open `/internal/daily` — confirm: model facts found/unavailable · prompt exists · reviewed exists ·
   artifact ready · share kit ready · T-30 pending · send=HOLD.

## Before kickoff
- Re-open `/internal/daily`; confirm the lead == selected_hotspot and the score hook reads correctly on
  the homepage (screenshot — text scanners do NOT prove contrast).

## T-30 (30 minutes before kickoff)
- Operator re-checks the released lineups. If the call changes: set `artifact.t30` status→`ready` with
  `update_text` (P1: `mvp2_generate_rescore_models.py` for a live diff). If unchanged: status→`skipped`.
  Never write a faked `update_text` while `pending`.

## After full-time (FT)
- Operator writes the observation receipt artifact (`recap_ready=false`): pre-match call → actual score
  → partial-hit assessment → deviation → calibration points → next impact. NEVER a fabricated full recap.
  (P1: `mvp2_build_recap_frame_real.py` → LLM `real_recap` with archived-prediction sha256 provenance.)
- Next day, the finished hotspot becomes the recap lead (carryover by fixture_key/id).

## What `/internal/daily` MUST show
selected_hotspot ready · source_facts (data_mode) · model_fields readiness + source tag · model-lookup
found/unavailable · LLM prompt exists · reviewed JSON exists · artifact ready · win_prob/confidence
null=acceptable · no_fake_probability=true · share kit (copy + card route) · T-30 status · observation/
recap status + carryover · send=HOLD.

## Share / copy / join
- Prediction: `/share/fixture/<fixture_key>` card + `ShareBlock` copy link / copy share text / QR →
  `/join?ref=CODE`. Recap: `/share/recap/<key>`. Copy source = the artifact `operations.share_copy` /
  canonical projection — operator replaces only `[群链接由运营填写]`; no manual judgement rewrite.

## Must remain HOLD / forbidden
- **HOLD:** all sends — manual only, one channel, Owner per-channel GO; no auto-send.
- **Forbidden:** auto-calling DeepSeek/Gemini/Kimi; backend schema change; backend deploy; faking
  win_prob / numeric confidence; fake recap; betting/trading vocabulary (赔率/盘口/投注/kèo/cửa trên…);
  treating a UI-only artifact (no content chain) as product recovery.
