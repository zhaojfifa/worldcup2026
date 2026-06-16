# Codex Independent Review — P4R Page-Level Product Reality

- **Reviewer role:** Independent adversarial reviewer ("Codex"), evidence-based, did NOT trust the self-review.
- **Branch:** `fix/mvp2-p4r-page-level-product-reality`
- **Diff base:** `mvp2-p4-critical-daily-recap-copy-loop-live-baseline-20260615..HEAD`
- **Date:** 2026-06-16
- **Method:** read the implementation at file:line, ran every guard `--selftest`, parsed the artifact JSON, visually inspected page-level screenshots, and diffed the whole branch for backend/schema/secret leakage.

---

## Item 1 — Reviewed LLM copy is actually RENDERED

**Verdict: PASS.**

The previous defect (renderer read `i18n`, `apply` only wrote `llm_judgment` → reviewed copy was dead) is fixed.

- `scripts/mvp2_build_daily_prediction_artifact.py` `cmd_apply` now writes BOTH:
  - `llm_judgment` (lines 372–378), and
  - the zh `i18n` slice the renderer actually reads (lines 379–411): `i18n.zh.prediction.primary_direction = rev["main_lean"]` (387), plus `score_call`, `backup_score`, `risk_level`, `risk_note`, `top_variable`, `why`, and `i18n.zh.analysis.{tactical_matchup,risk_variables,external_expectation,thirty_minute_checklist}` (400–408). `rendered_copy_source` is set at line 414. The comment at 379–383 explicitly documents the dead-render root cause.
- The renderer chain reads `i18n`, not `llm_judgment`:
  - `frontend/src/growth/strongCallProjection.ts` `buildStrongCallFromArtifact` resolves `A = predictionArtifactLocale(art, lang)` (117) and takes `main_lean = A.prediction.primary_direction` (134), score/backup/risk/top_variable/why from `A.prediction` / `A.analysis` (126–141).
  - `frontend/src/components/ArtifactTacticalRoom.tsx` likewise renders from `A = predictionArtifactLocale(art, loc)` (107): `A.analysis.modeling_focus` / `tactical_matchup` / `risk_variables` / `thirty_minute_checklist` (151–166). Since `apply` now populates that zh slice, what renders IS the reviewed copy.
- Artifact data confirms the sync for all three same-day fixtures (parsed independently):
  - `match_SaudiArabia-Uruguay-20260615.json`: `i18n.zh.prediction.primary_direction == llm_judgment.main_lean` = `赛前倾向乌拉圭，沙特需压低节奏才有机会`; `rendered_copy_source = operator_reviewed_llm_judgment`.
  - `match_Belgium-Egypt-20260615.json`: MATCH (`赛前倾向比利时，但埃及有能力压低比分`); source set.
  - `match_Spain-CapeVerde-20260615.json`: MATCH (`赛前明显倾向西班牙，但佛得角缺乏历史数据…`); source set.
- Screenshot `02-predict-primary-llm.png` shows the rendered `/predict` page (Belgium vs Egypt) carrying the reviewed strong-call copy (俅哥强判断 main lean, 主比分 1-0, 数据与建模依据 = model_fields computed, tactical/risk/T-30 sections) — i.e. the synced zh copy renders.

---

## Item 2 — Rendered guards inspect the DOM, not only JSON

**Verdict: PASS.**

- `scripts/_rendered_dom.py` dumps the SPA route's rendered DOM via headless Chrome (`--headless=new … --dump-dom`, `--virtual-time-budget`) and returns the DOM text (lines 8–15). This is real rendered HTML, not the source JSON.
- All five guards `from _rendered_dom import dump_dom`, fetch the live route DOM, and assert that expected strings are PRESENT in the rendered text (the JSON is only used to derive the expected reviewed `main_lean`/`score`, then checked against the DOM — exactly the right comparison):
  - `check_rendered_daily_freshness.py` — dumps `/?lang=zh` (75), asserts primary/yesterday teams present and demo absent (34–43).
  - `check_rendered_llm_prediction_copy.py` — dumps `/predict/<fk>` , fails if reviewed `main_lean[:14]` not in DOM and no `COPY_MISSING/REVIEW_REQUIRED` (45–60); also catches the fallback frame and missing score.
  - `check_rendered_llm_recap_copy.py` — dumps `/recap/<fk>` (93), asserts pre-match call/actual line/deviation present, fails on a fabricated-event regex and on a missing observation label (45–58).
  - `check_homepage_live_content_wiring.py` — dumps `/?lang=zh` (91), asserts reviewed lean projected onto the homepage card (50–51) and no demo leak (59).
  - `check_page_level_source_trace.py` — dumps home + `/predict` + `/recap` + `/share/fixture` (62–113), asserts the same reviewed lean substring traces across pages and demo is absent.
- Each guard has a `--selftest`. I ran all five:

```
check_rendered_daily_freshness     --selftest → 3/3 checks pass   (exit 0)
check_rendered_llm_prediction_copy --selftest → 5/5 checks pass   (exit 0)
check_rendered_llm_recap_copy      --selftest → 4/4 checks pass   (exit 0)
check_homepage_live_content_wiring --selftest → 4/4 checks pass   (exit 0)
check_page_level_source_trace      --selftest → 4/4 checks pass   (exit 0)
```

The selftests exercise the negative cases too (missing main_lean caught, missing score caught, fallback frame caught, fabricated event caught, demo-leak caught), so the assertions are real, not vacuous.

---

## Item 3 — Active-day source / yesterday observation / explicit (non-silent) fallback

**Verdict: PASS WITH MINOR NOTE.**

- `frontend/src/data/dailyFixtures.ts` `selectProductLoop` (186–218): `selected_hotspot` (`getSelectedHotspot()`) is the AUTHORITY for the lead (192–207). Crucially, when the selection is in the slate but has NO prediction artifact, `featuredPrediction = null` — it does **NOT** silently swap in a different match as the official pick (205–207); the comment + `/internal/daily` readiness (`leadReadiness`, 220–230) flag the failure. `featuredRecap = finished[0]` (213). This is honest: the official pick is never silently substituted.
- `frontend/src/pages/RecapDetailPage.tsx` labels the yesterday hotspot as a post-match OBSERVATION, not a full recap: the `OBSERVATION` block (22–38) renders `赛后观察` / `比赛已结束 · 赛后校准中` / `完整复盘尚未就绪…` and is selected when `obs && !obs.recap_ready` (157, 161–176). Screenshot `04-recap-observation-llm.png` confirms the rendered observation page (Brazil–Morocco 1-1: pre-match call → actual line → deviation → next-match focus → 完整复盘尚未就绪), never a fabricated recap. `HomeProductLoop.tsx` only shows `查看复盘` when `recapReady && id` (160, 170–174), else `查看赛后观察` / `赛后校准中`.

**Minor note (overclaim, not a blocker):** the self-review states missing copy "shows COPY_MISSING/OBSERVATION_ONLY rather than a silent generic fallback." `OBSERVATION_ONLY` is real (recap path, labeled as above; the token also lives in `dailyOpsState.json`). However the literal `COPY_MISSING` / `REVIEW_REQUIRED` label is **never rendered anywhere in `frontend/src/`** — it exists only as a *tolerance* branch in two guards. In `HomeProductLoop.tsx` the lead-card branch where `call` is null (224–228) falls back to a generic `predWhy` + `FocusBlock`, not an explicit "copy missing" label. In practice this path is narrow (the lead is already gated to artifact-backed fixtures, so a null `call` from a valid applied artifact should not occur), so it is defensive dead-code rather than a live silent-fallback bug. The honest mechanism that matters — selection-without-artifact → `null` lead + internal flag, never a silent swap — is correct.

---

## Item 4 — No backend / schema / secrets / auto-send changes

**Verdict: PASS.**

- `git diff --name-only mvp2-p4-critical-daily-recap-copy-loop-live-baseline-20260615..HEAD` touches only `scripts/`, `frontend/src/`, `docs/`. Filtering for `backend/|migration|schema|alembic|.sql|.env` → **NONE**.
- No hardcoded secrets: grep for `sk-…`, `api_key="…"`, `AIza…`, `ADMIN_API_TOKEN="…"` across the changed scripts → none.
- The builder is offline by design: no `subprocess`/`requests`/`httpx`/`urllib`/network and no LLM SDK call. The flow is prompt → operator pastes to DeepSeek/Gemini/Kimi MANUALLY → reviewed JSON → `apply` (docstring 8, prompt 224). No auto-send / auto-publish path.
- `cmd_apply` REQUIRES a reviewed JSON: it FAILs if `--reviewed` is missing/not found (365) and runs `validate_reviewed` (366–370). Validation enforces `safety.no_fake_probability` and `safety.no_auto_send` are true (306–307); `apply` re-stamps `no_auto_send=True` / `no_fake_probability=True` (430–431). Artifacts cannot be built without an operator-reviewed file.
- `frontend/src/data/dailyOpsState.json` `send_status = "HOLD"` (line 4).

---

## Item 5 — Page-level screenshots exist

**Verdict: PASS.**

`docs/qa_screenshots/p4r_page_level_product_reality/local/` contains all 7, all non-trivial real PNGs:

```
01-home-today-yesterday.png        1,101,738 B
02-predict-primary-llm.png           660,135 B
03-predict-secondary-llm.png         673,256 B
04-recap-observation-llm.png         412,640 B
05-internal-daily-source-trace.png   684,947 B
06-share-prediction.png              361,210 B
07-share-recap.png                   331,222 B
```

Visually inspected 02 (predict page, reviewed strong-call copy rendered) and 04 (recap page, explicit 赛后观察 / 完整复盘尚未就绪) — both are genuine page-level captures, not crops of JSON.

---

## Defects found

1. **(Minor / cosmetic)** `COPY_MISSING` / `REVIEW_REQUIRED` is referenced as a tolerated honest-state label in `check_rendered_llm_prediction_copy.py` (48) and `check_page_level_source_trace.py` (71, 87) but is never rendered in `frontend/src/`. The homepage lead's null-`call` branch (`HomeProductLoop.tsx` 224–228) uses a generic `FocusBlock` fallback instead of an explicit missing-copy label. Suggested patch (optional, non-blocking): either render an explicit `COPY_MISSING` label on that branch, or drop the dead tolerance and the corresponding self-review wording. The core anti-silent-fallback guarantee (selection-without-artifact ⇒ `null` lead, flagged in `/internal/daily`, never a silent match swap) is intact, so this is not a product-reality failure.

No defects found on Items 1, 2, 4, 5.

---

## Summary

The headline claim is real and independently verified: `cmd_apply` now syncs the reviewed judgement into the exact `i18n.zh.prediction/analysis` slice the React renderer consumes (`predictionArtifactLocale` → `buildStrongCallFromArtifact` / `ArtifactTacticalRoom`), all three same-day artifacts show `primary_direction == main_lean` with `rendered_copy_source` set, and the screenshots show the reviewed copy actually on `/predict`. The five new guards genuinely dump the rendered DOM via headless Chrome and assert on rendered text (not JSON), each ships a `--selftest`, and all five selftests pass with working negative cases. The homepage lead is anchored to `selected_hotspot` with no silent swap to a different match, yesterday is an explicitly-labeled post-match observation (not a fake recap), the branch is frontend/scripts/docs-only with no backend/schema/secret changes, the builder has no network/auto-send path and requires an operator-reviewed JSON, and `send_status` stays HOLD. The single defect is cosmetic — a `COPY_MISSING` label the guards tolerate but the UI never renders.

Codex verdict: PASS_WITH_PATCHES

---

## Patch re-verification (2026-06-16)

Re-verified ONLY the single defect from Item 3 / "Defects found" #1: the null-`call` lead branch in `frontend/src/components/HomeProductLoop.tsx` previously fell back to a generic `FocusBlock` template instead of rendering an explicit missing-copy label, so the `COPY_MISSING` / `REVIEW_REQUIRED` state the guards tolerated was never actually surfaced.

**Resolved.** In `HotspotPrediction` the `call ? (...) : (...)` branch (lines 210–234) now renders, in the else-branch, an EXPLICIT review notice instead of the generic `FocusBlock`:

- `<div className="th-meta" data-state="REVIEW_REQUIRED">` (line 228) — the machine-readable honest-state marker the rendered-DOM guards key on is now present in the DOM.
- Localized "pending review" copy in all four locales (lines 229–232): zh `今日主推文案待复核（REVIEW_REQUIRED）— 复核通过后展示俅哥判断。`, vi `Nội dung trận chính chờ duyệt (REVIEW_REQUIRED) …`, my `… စစ်ဆေးဆဲ (REVIEW_REQUIRED) …`, en `Today’s main read is pending review (REVIEW_REQUIRED) — shown once approved.`
- The comment at 225–227 documents that this is the honest "copy not yet reviewed" notice, not a silent demo/generic fallback.

`FocusBlock` (defined 139–150) is still used in `HotspotRecap` (line 168) for the recap focus block, so the shared template is intact and nothing else breaks. The generic-fallback path that masked the missing state is gone.

This was the only outstanding defect; Items 1, 2, 4, 5 were already PASS and the core anti-silent-fallback guarantee (selection-without-artifact ⇒ `null` lead, flagged in `/internal/daily`, never a silent match swap) was already intact.

Codex verdict (post-patch): PASS
