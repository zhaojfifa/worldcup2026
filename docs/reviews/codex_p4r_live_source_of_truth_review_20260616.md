# Codex Independent Review — P4R++ Live Source-of-Truth

- **Reviewer:** Codex (independent, adversarial)
- **Date:** 2026-06-16
- **Branch:** `fix/mvp2-p4r-live-source-of-truth`
- **Scope:** P4R++ live source-of-truth work — token safety, 5 owner-view guards, demo_pair_leak precision, live results, diff scope, screenshots.

---

## Item 1 — Token safety (CRITICAL) → PASS

- `git grep -n "12344321"` → **NO MATCH** in any tracked file.
- `grep -rn "12344321" docs/ scripts/ frontend/` → **NO MATCH**.
- `grep -c "12344321"` on `docs/qa_reports/p4r_live_source_of_truth_diagnosis.md` → **0**.
- `scripts/mvp2_match_sync.py` `cmd_upload`: token read via `os.environ.get("ADMIN_API_TOKEN")` (line 386); raises `SystemExit` if unset; sent only in the `x-admin-token` header. The two prints (`uploaded ...`, `response: <server body>`) do not include the token. No literal token anywhere.

**Verdict: PASS** — the admin token literal does not appear in any committed/new file; the sync script reads it from env and never prints it.

## Item 2 — Owner-view guards inspect the right thing → PASS

- `check_live_api_daily_source.py`: fetches live `GET /api/v1/daily-fixtures` JSON, asserts active slate contains no `Germany`/`Qatar` (WC-2022 archive opponents), asserts `freshness.stale` is not true, AND probes `POST /api/v1/admin/daily-fixtures/upload` with no token expecting **401** (any 2xx ⇒ "admin upload NOT protected"). Correct.
- `check_live_homepage_owner_view.py`: `dump_dom('/?lang=zh')`, asserts active primary + yesterday-recap team names present, reviewed lean (`llm_judgment.main_lean[:14]` or `REVIEW_REQUIRED`) projected, and `demo_pair_leak` clean. DOM-based. Correct.
- `check_live_predict_owner_view.py`: `dump_dom('/predict/<fk>?lang=zh')` per queued fixture, asserts reviewed copy + `recommended_score` + risk label (冷门风险/Upset) + share affordance (分享/复制/Share). DOM-based. Correct.
- `check_live_recap_owner_view.py`: `dump_dom('/recap/<fk>?lang=zh')`, asserts judgment + deviation + share + observation labelled + no fabricated event (regex `第\s*\d+\s*分钟.*(进球|破门|红牌|点球)`). DOM-based. Correct.
- `check_live_source_consistency.py`: fetches backend slate, compares `backend date` to frontend `selectedHotspot.date`, asserts primary `fixture_key` is in backend slate (id or `af:` prefixed), and renders homepage DOM to confirm primary teams present. Correct.

Selftest results (all exit 0):
- api_daily_source: 3/3 (clean / 2022-in-active caught / stale caught)
- homepage: 3/3 (clean / 2022-archive-not-flagged / demo-pairing-flagged)
- predict: 3/3 (clean / missing-copy caught / missing-score caught)
- recap: 3/3 (clean / fake-event caught / unlabelled caught)
- source_consistency: 1/1 (logic statement)

**Verdict: PASS** — API guard checks active slate + admin-401; the 3 frontend guards genuinely dump rendered DOM (`_rendered_dom.dump_dom`) and assert copy/score/label/no-fake-event; consistency guard compares backend date to the frontend active package.

**Minor note (not blocking):** `check_live_source_consistency.py --selftest` is a trivial print (no executed assertion), unlike the other four which run real cases. The live run is real and passed; recommend a real selftest case in a future patch.

## Item 3 — demo_pair_leak precision → PASS

- Direct test: `demo_pair_leak('德国 vs Japan')` → **None**; `demo_pair_leak('荷兰 vs Japan')` → **'荷兰 vs Japan'** (leak).
- Mechanism: only the demoted demo pairings (Netherlands/荷兰 + Japan/日本; Qatar/卡塔尔 + Ecuador/厄瓜多尔) flagged, and only when both sides appear within a 24-char adjacency window — so a legitimate WC-2022 archive recap like "德国 vs Japan" is not flagged.

**Verdict: PASS** — flags demoted demo pairings adjacently in zh/en; does not flag a legitimate archive recap.

## Item 4 — Live result is real → PASS

Raw live `GET /api/v1/daily-fixtures`: `date=2026-06-15`, `stale=False`, fixtures = Belgium-Egypt (**1489377** present), Saudi Arabia-Uruguay (1489379), Spain-Cape Verde (1489380), Brazil-Morocco (1489371), Mexico-South Africa (1489369), Sweden-Tunisia (1539002). No Germany / Qatar (2022) in the active slate.

Live guard runs (all exit 0 / PASS):
- `check_live_api_daily_source.py` (backend) → **PASS** — date=2026-06-15, 6 fixtures, stale=False, admin path protected.
- `check_live_homepage_owner_view.py` (frontend) → **PASS** — active primary + yesterday recap + reviewed lean; no demo.
- `check_live_predict_owner_view.py` (frontend) → **PASS** — 3 pages: reviewed copy + score + risk + share.
- `check_live_recap_owner_view.py` (frontend) → **PASS** — 1 page: judgment + deviation + share + observation labelled; no fake event.
- `check_live_source_consistency.py` → **PASS** — backend_date=2026-06-15 == active_date=2026-06-15; primary=1489377 rendered.

**Verdict: PASS** — live backend date is 2026-06-15, fixture 1489377 present, stale=false, active slate free of 2022 teams; all 5 owner-view guards pass against live.

## Item 5 — No backend/schema change → PASS

`git diff --name-only main..HEAD`:
```
docs/qa_reports/p4r_live_source_of_truth_diagnosis.md
docs/qa_screenshots/p4r_live_source_of_truth/live/01..08-*.png (8)
scripts/check_live_api_daily_source.py
scripts/check_live_homepage_owner_view.py
scripts/check_live_predict_owner_view.py
scripts/check_live_recap_owner_view.py
scripts/check_live_source_consistency.py
```
Only `scripts/` + `docs/` touched. No `backend/`, no schema. Working tree clean.

**Verdict: PASS.**

## Item 6 — Screenshots exist → PASS

`docs/qa_screenshots/p4r_live_source_of_truth/live/` contains **8 PNGs** (01-homepage-top, 02-homepage-yesterday-recap, 03-predict-1489377, 04-predict-1489379, 05-recap-1489371, 06-internal-daily-source-trace, 07-prediction-share, 08-recap-share), all non-zero size.

**Verdict: PASS.**

---

## Summary

Every claim verified with evidence, not trust. The admin token literal `12344321` is absent from all tracked/new files and the sync script reads it from `$ADMIN_API_TOKEN` and never prints it. All five owner-view guards inspect the correct surface (the API guard checks the live active slate excludes 2022 teams and that the admin POST is 401-protected; the homepage/predict/recap guards dump rendered DOM and assert reviewed copy/score/label/no-fake-event; the consistency guard ties backend date to the frontend active package). `demo_pair_leak` is precise (archive "德国 vs Japan" not flagged; demo "荷兰 vs Japan" flagged). All 5 selftests pass (15/16 real-case checks; the consistency selftest is a trivial print — minor, non-blocking) and all 5 live runs PASS, with the live backend at date 2026-06-15, fixture 1489377 present, stale=false, and no Germany/Qatar in the active slate. Diff scope is scripts/ + docs/ only (no backend/schema), and the 8 live screenshots exist.

Codex verdict: PASS
