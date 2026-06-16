# Codex Independent Review — OPS Patch 1489377 Belgium vs Egypt score 1-0 → 1-1

Reviewer: Codex (independent adversarial). Branch `ops/patch-1489377-score-1-1`, HEAD `73647b3`.
Date: 2026-06-16. Local preview built fresh and driven for all rendered checks (dist built
16:39:31 AFTER the artifact edit 16:39:14, so the preview is NOT stale).

## OVERALL VERDICT: **PASS**

The score correction is fully artifact-driven, consistent on every rendering source and rendered
surface, compliant, win_prob/confidence stay null, send stays HOLD, and the diff scope is limited to
the correction (no backend/schema/lifecycle-logic change). The patch itself is clean.

One **separate, pre-existing HIGH security finding** surfaced during check 9 (admin token value
committed in two PRIOR review docs that are NOT part of this patch). It does not make this patch fail
but must be escalated/scrubbed independently. Two further minor nits (guard robustness + a frozen
prompt file retaining 1-0) are informational, not blockers.

---

## Check 1 — Diff scope
`git diff main...HEAD --stat` (20 files): prediction artifact
(`frontend/src/data/predictionArtifacts/match_Belgium-Egypt-20260615.json`), reviewed + generated
audit JSONs, `dailyContentQueue.json`, `homepageLifecycle.json` (rendering) +
`docs/data_audit/mvp2_homepage_lifecycle/2026-06-15.json` (audit rebuild), the new focused guard
`scripts/check_ops_prediction_score_override.py`, the self-review doc, and screenshots.
- `git diff main...HEAD --name-only | grep '\.py$'` → ONLY `check_ops_prediction_score_override.py`
  (a new guard). **No selector/lifecycle `.py` logic changed.**
- `grep -E '^backend/|schema|alembic|migration'` → NONE.
- The rendering lifecycle file (`frontend/src/data/homepageLifecycle.json`) changed only 10 lines
  (model_source `computed`→`operator_confirmed` + reason_for_role). Its primary was ALREADY
  Belgium-Egypt at time-basis `12:00` on `main` (confirmed via `git show main:`), so the patch does
  NOT change which match is primary in the rendering source — only the source label.
- The audit file `docs/data_audit/mvp2_homepage_lifecycle/2026-06-15.json` got a fuller rebuild
  (generated_at/current_time_basis 20:00→12:00, primary Saudi-Uruguay→Belgium, secondary list
  populated). On `main` that audit file was STALE/inconsistent with the rendering file; the rebuild
  brings the audit trace into agreement with the rendering file. No match-count or selector-logic
  change; it is an audit artifact, not load-bearing for rendering.

DIFF_SCOPE_LIMITED=yes · BACKEND_SCHEMA_CHANGE=no

## Check 2 — Artifact-driven, not UI-only
`match_Belgium-Egypt-20260615.json`:
- `model_fields.recommended_score` = **"1-1"** (line 281); `model_fields.backup_scores` =
  **["1-0","2-1"]** (282-285).
- Every `i18n.{zh,vi,my,en}.prediction.score_call` = **"1-1"** (zh L38, vi L94, my L150, en L207);
  every `backup_score` = **"1-0 / 2-1"** (zh L39, vi L95, my L151, en L208).
- `llm_judgment.primary_score` = **"1-1"** (L310).
- `model_fields.source` = **"operator_confirmed"** (L289) — a valid operator-correction tag (also in
  `field_sources.score_call/backup_score`, L12-13).
- `model_fields.win_prob` = null, `confidence` = null (L280/288); `safety.no_fake_probability` true.
- `model_fields.model_computed_score` = **"1-0"** retained (L292) + `operator_correction` note (L293)
  — honest computed baseline preserved.
- Component grep `grep -rn -e '1-1' -e '1489377' frontend/src --include='*.tsx' --include='*.ts'` →
  **NO matches**. The score is read via `strongCallProjection.ts` (L124-137:
  `const primary_score = (mfUsable && mf.recommended_score) || p.score_call;`) from the artifact, not
  a hardcoded component override.

ARTIFACT_DRIVEN=yes · UI_ONLY_OVERRIDE=no

## Check 3 — Reviewed source-of-truth
`docs/data_audit/mvp2_predictions/reviewed/20260615_1489377_reviewed.json`: `primary_score` = "1-1",
`backup_scores` = ["1-0","2-1"]; all copy fields (main_lean/risk_note/share_copy/hook_headline/
hidden_risk/confidence_language…) rewritten to the draw call. No stale "1-0" as primary.

## Check 4 — All surfaces agree on 1-1 (preview-driven)
`check_ops_prediction_score_override.py --fixture-id 1489377 --expected-score 1-1 --old-score 1-0
--base-url http://localhost:4341` → **OPS SCORE OVERRIDE PASS** (artifact-driven across reviewed/
artifact/queue/recap + rendered home/predict). Selftest 3/3 PASS.
- Independent DOM dump `/?lang=zh`: "1-1" ×3, "修正为平局" ×2, hook "俅哥把比利时" ×1,
  hidden_risk "若比利时早早破门" ×1; old hook "该赢"/"效率局" ×0; "2-0" ×0.
- Independent DOM dump `/predict/1489377?lang=zh`: STRONG CALL renders `主比分 … 1-1 … 备选: 1-0 / 2-1`;
  "1-1" ×5, "1-0" ×5 (backup + retained computed baseline only — never the main call), "2-0" ×0,
  win_prob ×0, 赔率 ×0, 盘口 ×0. `source = operator_confirmed` shown as provenance.
- Share copy (artifact `operations.share_copy`, zh/vi/my/en) uses 主比分 1-1 / 备选 1-0 / 2-1 — does
  not contradict.

ALL_SURFACES_1_1=yes

## Check 5 — No stale 1-0 as PRIMARY
`grep -rn '"score_call"|"recommended_score"|"primary_score": "1-0"' frontend/src/data
docs/data_audit/mvp2_predictions`:
- frontend/src/data → NONE.
- ONE hit: `docs/data_audit/mvp2_predictions/prompts/20260615_1489377_prompt.md:34`
  `"primary_score": "1-0"`. This is the FROZEN generation-input template (the prefilled computed
  ScoutScore baseline fed to the model), NOT a rendering source nor the reviewed source-of-truth, and
  it is NOT part of this patch's diff. It is consistent with the intentionally-retained
  `model_computed_score = "1-0"`. **Informational (LOW)** — recommend leaving as honest generation
  history or appending an ops-patch note; not a rendering/source-of-truth leak.

STALE_1_0_PRIMARY=none (in active rendering + source-of-truth surfaces; one in the frozen, by-design
generation prompt only)

## Check 6 — Recap / closure baseline
`docs/data_audit/mvp2_predictions/generated/20260615_1489377_generated.json` `draft.recap_seed`:
"赛后核对：主推已修正为 1-1 … 复盘基线＝1-1。" `draft.primary_score`/`backup_scores`/share_copy/
homepage_short all updated to 1-1; `_ops_patch_note` records the 1-0→1-1 closure-baseline correction.

RECAP_BASELINE_1_1=yes

## Check 7 — Guards (PASS/FAIL each)
- check_ops_prediction_score_override (JSON+rendered): **PASS**; --selftest 3/3 **PASS** (non-vacuous:
  3 distinct assertions, catches missing score).
- check_p5a_copy_contract: **PASS**
- check_prediction_artifact: **PASS** (4 prediction + 1 observation; safe vocab)
- check_growth_copy: **PASS** (32 files)
- check_content_queue: **PASS** (primary + 2 secondary; recap 3; t30 3; send HOLD)
- check_p5a_homepage_content_quality `--base-url http://localhost:4341`: **PASS**
- check_p5b_no_finished_primary: **PASS** (primary upcoming, matches lifecycle)
- check_p5b_homepage_lifecycle_rendering: **PASS** (rendered primary + latest_recap match lifecycle)
- check_customer_visible_copy `http://localhost:4341`: **PASS** (vi/my Han=0, persona present)

Invocation note (NOT a patch defect): the guards use inconsistent CLI conventions —
check_p5a_homepage_content_quality and check_ops require `--base-url URL` (else default to the LIVE
prod site), while check_customer_visible_copy takes a POSITIONAL base_url (`sys.argv[1]`; `--base-url`
breaks it). An initial mis-invocation produced false FAILs that vanished under correct invocation; all
green when invoked per each guard's own contract.

## Check 8 — Compliance
- Diff-added copy scanned for `盘口|投注|下注|赔率|必中|稳赚|betting|odds|handicap|kèo|cửa trên|cửa dưới`
  → **NONE**. No `盘面` added. `胜率`/`置信` appear on /predict only as the brand slogan
  ("不只看胜率，更看俅哥为什么这样判断") and the honest disclosure "暂无自动胜率 / 数值置信度" — no fake
  numeric probability/confidence.
- `safety.no_auto_send` = true; content-queue guard reports "send HOLD". No auto-publish.
- vi/my visible copy Han=0 (check_customer_visible_copy PASS).

BETTING_VOCAB=none · FAKE_DATA=none · AUTO_SEND=none · SEND_STATUS=HOLD

## Check 9 — Secret scan
- This patch's own additions (`git diff main...HEAD | grep '^+'`) contain **no** token/API key/.env →
  this patch introduces no leak.
- HOWEVER `git grep "<REDACTED_ADMIN_TOKEN — per Owner security boundary; value scrubbed 2026-06-16>"` finds the admin token VALUE in TWO tracked files:
  `docs/reviews/codex_p4r_live_source_of_truth_review_20260616.md` and
  `docs/reviews/codex_p5b_match_lifecycle_homepage_review_20260616.md`. These are PRIOR review docs,
  NOT part of this patch's diff (confirmed via `--name-only`). **HIGH-severity pre-existing leak** —
  the production admin token is committed in repo history from earlier reviews and should be rotated
  and scrubbed independently of this patch.

ADMIN_TOKEN_LEAK=false (for this patch's diff) — but SEE HIGH FINDING: a pre-existing token leak
exists in two tracked prior-review docs and must be escalated/rotated.

---

## Defects / Findings
1. **HIGH (pre-existing, out of this patch's scope):** admin token value committed in two tracked
   prior-review docs (`codex_p4r_live_source_of_truth_review_20260616.md`,
   `codex_p5b_match_lifecycle_homepage_review_20260616.md`). Rotate the token and scrub the files.
   Does not block this patch.
2. **LOW (informational):** the focused guard's rendered check only asserts `"1-1" in dom`; the OLD
   backup string was "2-0 / 1-1" (contains "1-1"), so that single check could not by itself
   distinguish a stale 1-0 bundle from a fresh 1-1 one. The patch is fine — freshness was confirmed
   independently (dist build time + absence of old hook "该赢"/"效率局" and old backup "2-0"). Consider
   strengthening the guard to also assert the old PRIMARY phrasing is absent from the main-call slot.
3. **LOW (informational):** `docs/data_audit/mvp2_predictions/prompts/20260615_1489377_prompt.md`
   retains `"primary_score": "1-0"` (frozen generation input / computed baseline). Consistent with
   the retained `model_computed_score=1-0`; optional to annotate.

## Confirmation lines
- DIFF_SCOPE_LIMITED=yes
- ARTIFACT_DRIVEN=yes
- UI_ONLY_OVERRIDE=no
- ALL_SURFACES_1_1=yes
- STALE_1_0_PRIMARY=none (active rendering + source-of-truth; one in the frozen by-design prompt only)
- RECAP_BASELINE_1_1=yes
- BETTING_VOCAB=none
- FAKE_DATA=none
- AUTO_SEND=none
- SEND_STATUS=HOLD
- ADMIN_TOKEN_LEAK=false (this patch) / a pre-existing leak exists in two prior-review docs (escalate)
- BACKEND_SCHEMA_CHANGE=no
