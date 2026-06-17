# Codex Independent Adversarial Review — R6.1 Runtime Pre-upload Customer-visible Guard

- Sprint: R6.1 · Branch: `ops/r6_1-runtime-preupload-cv-guard` · HEAD `a04ced0`
- Reviewer: Codex (independent adversarial) · Date: 2026-06-17
- Scope rule honored: modified NO file except this review doc.

## Overall Verdict: **PASS**

The PRE-upload customer-visible guard is correctly implemented, wired before the
runtime-content POST, empirically blocks de-model/betting wording and fabricated
probability/confidence, restores bundled artifacts on block without uploading anything,
and leaves production unchanged. No UI/product/backend/schema/scheduler change. send HOLD.
No defects of any severity found. The 概率 over-ban fix is correct.

---

## Check 1 — Diff scope · DIFF_SCOPE_OK=yes

`git diff main...HEAD --stat` (HEAD = a04ced0):
- `scripts/check_r6_runtime_preupload_customer_visible_guard.py` (NEW, +138)
- `scripts/mvp2_runtime_content_cutover.py` (+15)
- `docs/reviews/...claude_self_review.md` (NEW, +51)
- evidence txt (+22) + 1 screenshot png (binary)
- Total 226 insertions, 0 deletions.

`git diff main...HEAD -- frontend/` → EMPTY. `git diff main...HEAD -- backend/` → EMPTY.
No scheduler: `git diff main...HEAD | grep -iE "crontab|schedule|APScheduler|cron|while True|sleep("`
returns only the self-review doc line *stating* the absence ("...no scheduler change..."), no
runtime scheduler code. **Confirmed limited to the declared files; no UI/product/backend/schema change.**

## Check 2 — Guard scan_package + selftest · DEMODEL_TERMS_BLOCK=yes · FAKE_PROB_CONFIDENCE_BLOCKS=yes

`scripts/check_r6_runtime_preupload_customer_visible_guard.py`:
- (a) `scan_package` (line 62) walks prediction i18n keys `("prediction","analysis","operations","copy_v2")`
  (TEXT_KEYS_PRED, line 37; scanned at lines 68-71), observations i18n (lines 81-85), selectedHotspot
  home/away (lines 86-87), and shares (lines 88-90). Uses recursive `_walk_strings` (line 40) for nested text.
- (b) Banned terms (BANNED, lines 17-35): de-model zh 模型/数据不足/缺少数据/数据缺失/置信度/胜率/盲区;
  vi mô hình/thiếu dữ liệu/xác suất/tỷ lệ thắng; en model unavailable/insufficient data/win probability/
  confidence score; ms model tidak tersedia/data tidak mencukupi/kebarangkalian menang; betting
  盘口/投注/下注/赔率/竞猜/让球/必中/稳赚/跟单/回报率 + kèo/cửa trên/cửa dưới/tỷ lệ cược +
  betting/odds/handicap/bookmaker. Matched case-insensitively (line 57).
- (c) Structural rejection of non-null numeric win_prob/confidence in model_fields (lines 73-76) and
  i18n prediction.confidence (lines 77-80) via `isinstance(..., (int,float))`.
- Bare 概率 intentionally NOT banned — code comment lines 18-21 documents this ("bare 概率 ... is NOT
  banned — common colloquial football wording ... banned win-claim terms are 胜率/置信度").

`--selftest` → **6/6 PASS** (clean passes; 模型 blocks; mô hình blocks; fake win_prob blocks; fake
confidence blocks; betting odds blocks). Selftest is NON-VACUOUS — verified by separate empirical runs
(Check 4): a clean package passes and each violation class independently fails, so the asserts are not
trivially true.

## Check 3 — Guard runs BEFORE upload · GUARD_RUNS_BEFORE_UPLOAD=yes · BLOCK_RESTORES_NO_UPLOAD=yes

In `mvp2_runtime_content_cutover.py::run`:
- Guard call `cvg.scan_package(pkg)` is at the inserted block (diff lines after package assembly,
  before `if do_upload and target:` at file line 146).
- The actual upload `_post(base, "/api/v1/admin/runtime-content/upload", pkg, token)` is at **line 153**
  (slate `_post(... "/api/v1/admin/daily-fixtures/upload" ...)` at line 152). Both POSTs are strictly
  AFTER the guard. The endpoint string in the module docstring (lines 5-6) is documentation, not a call.
- On violation: calls `_restore(snap)` (snapshot taken at line 108), writes
  `<date>_blocked_customer_visible.json` report with result `CUTOVER_BLOCKED_CUSTOMER_VISIBLE`,
  `send_status:"HOLD"`, `uploaded:false`, and per-violation `{field, reason}`; prints the violations;
  **`return 4`** — exits before reaching the upload block, so NEITHER slate NOR content is POSTed.
  Production stays on the previous runtime package. send HOLD always.

## Check 4 — Empirical block proof (NO upload) · all confirmed

Standalone runs (no production POST):
- `/tmp/cdx_bad.json` (copy_v2 hook_headline "模型不可用") → **FAIL rc=1**,
  field `predictions.X.i18n.zh.copy_v2.hook_headline — banned term '模型'`.
- `/tmp/cdx_clean.json` (clean copy "低比分缠斗概率高", null win_prob/confidence) → **PASS rc=0**.
- `/tmp/cdx_fakeprob.json` (win_prob 0.62) → **FAIL rc=1**,
  field `predictions.X.model_fields.win_prob — fabricated win_prob (must be null)`.
- Additional coverage proofs: observations i18n "盘口分析" → FAIL (`observations.O.i18n.zh.text — 盘口`);
  shares "投注必中" → FAIL (2 violations). Confirms obs + share scanning is live, not dead code.

## Check 5 — Production unchanged & live · PRODUCTION_UNCHANGED=yes

`GET /api/v1/runtime-content` → date **2026-06-17**, primary **1489384 (England, away Croatia)**,
send_status **HOLD**, predictions count **1**. selectedHotspot keys: date/fixture_key/home/away/source/
operator_confirmed/status — only home/away are customer-visible team labels (scan target is correct).
- `check_live_source_consistency.py` → **PASS** (backend_date=2026-06-17, active_date=2026-06-17,
  sel_source=runtime, primary=1489384). No re-run needed (passed first attempt).
- `check_r4_runtime_content_cutover.py` → **PASS** (endpoint live · stored=True · predictions=1 · HOLD).

## Check 6 — Regression · NO_UI_PRODUCT_BACKEND_CHANGE=yes

- `check_p5a_homepage_content_quality.py` → **PASS** (hook+reason+risk on primary; src=runtime).
- `check_p5a_predict_content_quality.py` → **PASS** (3 pages).
- `check_p5a_recap_content_quality.py` → **PASS**.
- `check_p5a_share_content_quality.py` → **PASS**.
- `check_customer_visible_copy.py` → FAIL, but **TRANSIENT** and **out of R6.1 scope**: FAILs are only
  persona-naming-missing on `/recap/*` and `/join` (cold-start render). The failing set differed between
  two runs (run 1: /recap/1489369 my + /join zh/vi/my; run 2 added /recap/979139 vi/my, /recap/1489369
  zh/vi) → render-timing flakiness, exactly the transient cold-start FAILs the brief flagged for
  /recap/979139, /recap/1489369, /join. No homepage FAIL; the R6.1 change is frontend-untouched. Not a
  regression introduced by this branch.

## Check 7 — Compliance / over-ban fix · OVERBAN_概率_FIXED=yes · FAKE_DATA=none · AUTO_SEND=none

- Guard introduces no fake data (it only rejects non-null win_prob/confidence — it never fabricates),
  no betting promotion (it bans betting vocab), no auto-send (no network/POST in the guard module; the
  cutover gates on `--target`/`--do_upload` and the guard short-circuits before any POST). send HOLD.
- Over-ban fix correct: the LIVE England copy "低比分缠斗概率高" (bare 概率) PASSES (Check 4 clean run),
  while win-rate claims 胜率/置信度 (and en/vi/ms "win probability") remain blocked (BANNED lines 22/26/30/34).

## Check 8 — Secret scan · ADMIN_TOKEN_LEAK=false

- `git grep -lc <pattern> -- . ':!*.png'` → returned exit code 1 (NO matching tracked files;
  filenames/counts mode only, value never printed). Token VALUE absent from all tracked files on this branch.
- `backend/.env` → NOT tracked (`git ls-files backend/.env` empty).
- `git diff main...HEAD --name-only` introduces no `.env`/token files.
- This review doc contains no token value.

---

## Defects
None (no Critical/High/Medium/Low defects found).

## Minor observations (non-blocking, no patch required)
- selectedHotspot scan covers only home/away. The other keys (source `api_football_scoutscore`,
  status, fixture_key) are structural and not rendered as customer copy on the homepage card, so the
  narrowed scan is acceptable.
- Quota/coverage of any future new customer-visible i18n key would need TEXT_KEYS_PRED extension; today's
  package shape (prediction/analysis/operations/copy_v2) is fully covered.

## Confirmation lines
- DIFF_SCOPE_OK=yes
- GUARD_RUNS_BEFORE_UPLOAD=yes
- DEMODEL_TERMS_BLOCK=yes
- FAKE_PROB_CONFIDENCE_BLOCKS=yes
- BLOCK_RESTORES_NO_UPLOAD=yes
- PRODUCTION_UNCHANGED=yes
- NO_UI_PRODUCT_BACKEND_CHANGE=yes
- OVERBAN_概率_FIXED=yes
- FAKE_DATA=none
- AUTO_SEND=none
- SEND_STATUS=HOLD
- ADMIN_TOKEN_LEAK=false
