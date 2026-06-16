# Codex Adversarial Review — OPS patch: Brazil 1-1 Morocco (1489371) recap clickable

- Branch: `ops/patch-brazil-morocco-recap-clickable` · HEAD `d75a31d`
- Stacked on: `ops/patch-1489377-score-1-1` (Belgium 1-1)
- Reviewer: Codex (independent) · Date: 2026-06-16
- Local preview verified at `http://localhost:4342` (fresh `npm run build` → `vite preview`)

## OVERALL VERDICT: PASS_WITH_PATCHES

The feature itself is correct and verified end-to-end: the Brazil–Morocco yesterday-recap card is
clickable, `/recap/1489371` renders a safe OBSERVATION_ONLY receipt (recap_ready=false does NOT
block it), prediction↔actual is aligned, no fabricated event data, no fake-full-recap claim, and
Belgium vs Egypt stays 1-1. The implementer's "already worked, this patch hardens/clarifies/guards"
claim is ACCURATE for the primary card.

BUT one HIGH-severity defect blocks a clean PASS: this branch's single commit (`d75a31d`)
**reintroduces the literal admin token value `12344321` into a tracked file** —
`docs/reviews/codex_ops_patch_1489377_score_1_1_review_20260616.md:131`. The prior commit `d09fe2e`
scrubbed that value from two other docs; this commit added a new doc that quotes it again.
`git grep 12344321` now returns exactly one tracked hit, on this branch. **ADMIN_TOKEN_LEAK=true.**

Required patches before merge:
1. (HIGH) Scrub the literal token value from `codex_ops_patch_1489377_score_1_1_review_20260616.md`
   line 131 (replace with a placeholder); rotate the admin token (value is already in repo history).
2. (LOW, optional) Fix the latent OtherRecaps encoded-key re-check (see Check 2).
3. (NIT) The `codex_ops_patch_1489377_...` doc is the review of the PRIOR (Belgium) branch and is
   outside this patch's stated scope; it was committed here.

---

## Check 1 — Diff scope
`git diff ops/patch-1489377-score-1-1...HEAD --name-only` (this patch's OWN delta) =
- `frontend/src/components/HomeProductLoop.tsx` (16 lines)
- `scripts/check_ops_brazil_morocco_recap_clickable.py` (new, 109 lines)
- `docs/reviews/ops_patch_brazil_morocco_recap_clickable_claude_self_review.md` (self-review)
- `docs/reviews/codex_ops_patch_1489377_score_1_1_review_20260616.md` (PRIOR-branch review — extra)
- 5 local screenshots under `docs/qa_screenshots/ops_patch_brazil_morocco_recap_clickable/local/`

No `backend/`, no schema, no lifecycle-selector `.py`, no scheduler, no migration (grep = none).
No match-count expansion (`homepageLifecycle.json` / `dailyContentQueue.json` changes appear only in
`main...HEAD`, i.e. inherited from the stacked Belgium base — NOT in this patch's delta).
DEFECT (NIT, scope): the `codex_ops_patch_1489377_score_1_1_review_20260616.md` doc belongs to the
prior Belgium branch's review, not this patch — minor scope drift, and it carries the leak in Check 9.
**DIFF_SCOPE_LIMITED=yes** (runtime/backend/schema all clean; only an extra doc beyond stated scope).

## Check 2 — HomeProductLoop.tsx
- (a) HotspotRecap badge: `frontend/src/components/HomeProductLoop.tsx:182` now uses
  `{ready ? FZ.ready : C.recapState}` where `recapState` = `'比赛已结束 · 赛后观察 / 复盘校准中'`
  (zh, line 65) — CONFIRMED, with vi/my/en equivalents (no Han).
- (b) OtherRecaps (lines 350–362): `ready = !!f.recapReady && !!f.id`; new
  `rKey = recapKeyFor(f)`, `obs = !!rKey && hasObservationArtifact(rKey)`,
  `clickable = !!rKey && (ready || obs)`. CTA label = `ready ? C.viewRecap : C.viewObs`, so
  `查看复盘` (viewRecap) shows ONLY when `ready` (recap_ready=true). `查看赛后观察` (viewObs) shows
  for an observation artifact. A finished match with NO artifact → `obs=false`, `ready=false` →
  stays the `已完赛` done chip. recap_ready=false is NOT a hard gate for the observation CTA. CONFIRMED.
- DEFECT (LOW, latent): `recapKeyFor` (line 24) returns `f.id` for numeric ids, but for a MANUAL
  fixture (id=null) returns `encodeURIComponent(leadKey)` (e.g. `af%3A1489371`). OtherRecaps then
  re-checks `hasObservationArtifact(rKey)` with that ENCODED key, while `getObservationArtifact`
  matches the RAW `fixture_key` (`af:1489371`) — so a manual-fixture observation row would NOT be
  clickable, contradicting `recapKeyFor`'s P7-P0-5 carryover design and HotspotRecap (which only
  tests `rKey` truthiness, line 190). No live impact today (only observation artifact is numeric-id
  1489371; target fixture is the PRIMARY HotspotRecap, not OtherRecaps) and no regression vs prior
  behaviour (OtherRecaps previously keyed on `f.id` only). Recommend keying the re-check on the raw
  leadKey or trusting `recapKeyFor`'s guarantee.

## Check 3 — RecapDetailPage.tsx (unchanged by this patch — verified intact)
`frontend/src/pages/RecapDetailPage.tsx:156-158`: `obs = getObservationArtifact(fixtureId)`; if
`obs && !obs.recap_ready` → `return <ObservationReceipt art={obs} loc={loc} />` (not blank, not 404,
not a fake recap). The historical/real_recap branch (855737) is intact at lines 121-122
(`mode === 'historical_recap' || mode === 'real_recap'`) above the observation branch, so real
recaps do not regress. This page was NOT modified by this branch (not in the diff) — consistent with
the "already worked" claim. **RECAPREADY_FALSE_NOT_BLOCKING=yes · OBSERVATION_NOT_FAKE_RECAP=yes.**

## Check 4 — Observation artifact `observation_1489371.json` (pre-existing, ancestor commit)
`recap_ready=false`, `score="1-1"` / `score_home=1` / `score_away=1`, `result_judgment`=`部分命中
（PARTIAL）`, `source_label`=`来源：赛后观察回执（OBSERVATION_ONLY）· 完整事件数据未接入，不展开完整战术复盘`,
pre-match baseline `赛前主推：偏向巴西，主比分参考 2-1，备选含 1-1` (REAL in the artifact, not invented
in the component). zh carries what_was_right / what_was_wrong / model_correction / next_match_learning.
No fabricated event-level data (no possession/shots/lineups). `safety.no_fake_recap=true`,
`no_auto_send=true`. **PREDICTED_VS_ACTUAL_ALIGNED=yes.** (Note: vi/my locales omit some of the v2
fields — pre-existing artifact gap, not this patch; zh/en render fully.)

## Check 5 — Focused guard (`check_ops_brazil_morocco_recap_clickable.py`)
- `--selftest` → 5/5 PASS and is NON-VACUOUS: independently catches missing CTA, blank recap, fake
  full recap (`完整战术复盘已生成`), and Belgium regression.
- `--base-url http://localhost:4342` → PASS.
- Independent DOM dump (my own eyes, `scripts/_rendered_dom.py`):
  - HOME active surface: `Brazil`=T, `Morocco`=T, `1-1`=T, `查看赛后观察`=T, `Belgium`=T, `Egypt`=T.
  - `/recap/1489371`: Brazil=T, Morocco=T, 1-1=T, 赛后观察=T, OBSERVATION_ONLY=T, 部分命中=T, PARTIAL=T,
    赛前主推=T, 实际比分=T, 看对了什么=T, 看错了什么=T, 修正=T, 下一场=T; `完整战术复盘已生成`=F.
- The guard correctly does NOT rely on a literal `/recap/1489371` href (it documents the SPA onClick
  navigate and proves clickability via the CTA button + the recap page rendering). CONFIRMED.
**RECAP_CARD_CLICKABLE=yes · LINK_TARGET_RECAP_1489371=yes** (navigate target = `/recap/${rKey}`,
rKey=`1489371`).

## Check 6 — Belgium regression
`check_ops_prediction_score_override.py --fixture-id 1489377 --expected-score 1-1 --base-url ...` →
PASS (artifact-driven across reviewed/artifact/queue/recap + rendered home/predict). DOM dump of
`/predict/1489377`: 1-1 is the main score-call; `1-0` appears only as a labelled backup/path
(`备选: 1-0 / 2-1`), not the headline call. Homepage active surface still shows Belgium 1-1.
**BELGIUM_STILL_1_1=yes.**

## Check 7 — Regression reruns (all against local build)
| Guard | Result |
|---|---|
| `check_p5a_homepage_content_quality.py` | PASS |
| `check_p5a_recap_content_quality.py` | PASS |
| `check_p5b_recap_handoff.py --date 2026-06-15` | PASS |
| `check_p5b_homepage_lifecycle_rendering.py` | PASS |
| `check_growth_copy.py` | PASS (32 files) |
| `check_customer_visible_copy.py http://localhost:4342` | PASS |

## Check 8 — Compliance
- Changed copy scanned for 盘口/投注/下注/赔率/竞猜/betting/odds/handicap/kèo/cửa/稳赚/必中/跟单 → **none**.
- Fake-full-recap wording (完整战术复盘已生成 etc.) in customer copy → none. `完整复盘` appears only inside
  `完整复盘确认后开放` (the safe "opens once confirmed" pending line) — not a fake-ready claim. The
  FAKE_FULL strings appear only in the guard's banlist (intended).
- No auto-send / auto-publish code added (only doc annotations `no_auto_send`, `AUTO_SEND=none`).
- vi/my added `recapState` copy: Han scan = 0 for both.
**BETTING_VOCAB=none · AUTO_SEND=none · SEND_STATUS=HOLD.**

## Check 9 — Secret scan  ★ DEFECT (HIGH)
`git grep -nE "12344321|ADMIN_API_TOKEN *=" -- .` →
- The only `ADMIN_API_TOKEN=` hits are `<local>` / `<prod token>` / `…` placeholders in docs — OK.
- BUT the literal admin token VALUE `12344321` is present in a tracked file:
  `docs/reviews/codex_ops_patch_1489377_score_1_1_review_20260616.md:131`
  (the sentence `git grep "12344321" finds the admin token VALUE in TWO tracked files`). This file
  was ADDED by this branch's commit `d75a31d` (confirmed via `git log --oneline -- <file>`). The
  prior fix `d09fe2e` scrubbed the value from the two docs it pointed at, but this newly-committed
  review doc quotes the value, so the leak is reintroduced on this branch.
**ADMIN_TOKEN_LEAK=true** (do not print value). Remediation: scrub line 131 to a placeholder and
rotate the admin token (value already exists in git history).

---

## Explicit confirmation lines
- DIFF_SCOPE_LIMITED=yes (one extra prior-branch review doc beyond stated scope; no runtime/backend/schema)
- RECAP_CARD_CLICKABLE=yes
- LINK_TARGET_RECAP_1489371=yes
- RECAPREADY_FALSE_NOT_BLOCKING=yes
- OBSERVATION_NOT_FAKE_RECAP=yes
- PREDICTED_VS_ACTUAL_ALIGNED=yes
- BELGIUM_STILL_1_1=yes
- BETTING_VOCAB=none
- AUTO_SEND=none
- SEND_STATUS=HOLD
- ADMIN_TOKEN_LEAK=true
- BACKEND_SCHEMA_CHANGE=no

## Defects summary
| # | Severity | Defect |
|---|---|---|
| 1 | HIGH | Admin token value `12344321` reintroduced (tracked) at `codex_ops_patch_1489377_score_1_1_review_20260616.md:131`, added by `d75a31d`. Scrub + rotate. |
| 2 | LOW | OtherRecaps re-checks `hasObservationArtifact(rKey)` on the URL-ENCODED key → breaks manual-fixture (id=null) observation clickability; no current data triggers it, target fixture unaffected. |
| 3 | NIT | Prior-Belgium-branch review doc committed in this branch — minor scope drift. |
