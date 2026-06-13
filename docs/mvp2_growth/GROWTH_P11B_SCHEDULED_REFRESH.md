# Growth P1.1b/P1.2 — Scheduled / Manual Package & Status Refresh（operator-controlled）

> Owner revision 2026-06-12: keep it simple. CLI is the source of truth; refresh = wrapper that
> writes paste-ready package files. **Generation is automated; SENDING IS ALWAYS MANUAL**
> (Owner GO per fixture/channel → approve → paste → mark-sent + screenshot).

## 1. Commands

```bash
# all packages for one language (today + next + latest recap), files + summary:
python3 scripts/mvp2_growth_cli.py refresh --lang zh --ref QG-TEST1
python3 scripts/mvp2_growth_cli.py refresh --lang vi --ref TT-VN88
python3 scripts/mvp2_growth_cli.py refresh --lang my --ref FO-MM21

# single package with manual fixture override (enough for P1.1b — no auto-discovery):
python3 scripts/mvp2_growth_cli.py package today --fixture 1489371 --lang zh --ref QG-TEST1
python3 scripts/mvp2_growth_cli.py package recap --fixture 1489369 --lang zh --ref QG-TEST1
python3 scripts/mvp2_growth_cli.py package next  --fixture 1489371 --lang zh --ref QG-TEST1
```

Per-package status in the summary: `available` · `unavailable` · `refused` (e.g. today on a
finished fixture) · `needs_fixture` (no bundled narrative — pass `--fixture`) ·
recap additionally carries `approval_status` (read-only queue lookup; `guard_passed` ≠ approved →
warning "Verify queue approval before sending."; generation is never blocked).

## 2. Output

`docs/data_audit/mvp2_growth_packages/`
- `{kind}_{fixture}_{lang}_{ref}.md` — fixture_id / lang / ref / share_link / share_card_url /
  package_status / approval status+warning (recap) / generated_at / operator_next_step +
  paste-ready copy_text (judgement lines = bundled guard-passed LLM fields, verbatim).
- `refresh_summary_YYYYMMDD_HHMM.json` — machine-readable status per kind.

After a fixture finishes or new narratives are bundled, just re-run refresh — files are
overwritten per (kind, fixture, lang, ref); summaries accumulate as the audit trail.

## 3. Local cron (operator machine; the ONLY approved scheduling for now)

```cron
0 10 * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py refresh --lang zh --ref QG-TEST1 >> logs/growth_refresh_zh.log 2>&1
5 10 * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py refresh --lang vi --ref TT-VN88 >> logs/growth_refresh_vi.log 2>&1
10 10 * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py refresh --lang my --ref FO-MM21 >> logs/growth_refresh_my.log 2>&1
```
(`mkdir -p logs` first. Cron only WRITES files — it cannot send anything; there is no send code.)

## 3b. P1.2 Status Refresh Gate（freshness first — supersedes nothing, gates everything）

> Owner priority 2026-06-13: **the critical failure is freshness, not prediction accuracy.**
> A finished/live match must never be displayed or packaged as an active pre-match prediction.

Canonical lifecycle (one source of truth: `scripts/mvp2_fixture_lifecycle.py`):
`SCHEDULED → T_MINUS_2H → T_MINUS_30 → LIVE → FINISHED → RECAP_PENDING → RECAP_READY → ARCHIVED`

- `package today` / `next` refuse LIVE, FINISHED, RECAP_PENDING, RECAP_READY, ARCHIVED.
- `package recap` allows only FINISHED / RECAP_PENDING / RECAP_READY (ARCHIVED = 历史复盘档案).
- `refresh` on a refused today fixture prints **`NO_VALID_TODAY_FIXTURE`**, records the gate in
  the summary JSON, and overwrites any previously generated today/next package file with a
  REFUSED stub so stale pre-match copy cannot be pasted.
- Status sources per fixture (recorded in the lifecycle JSON): `api_football` →
  `bundled_narrative` → `time_inference` (graceful fallback; never crashes the refresh).

```bash
# lifecycle snapshot (writes docs/data_audit/mvp2_daily_refresh/fixture_lifecycle_YYYYMMDD_HHMM.json):
python3 scripts/mvp2_growth_cli.py status-refresh
# stale-surface scan (bundled manifests + HomePage pins + package files; exit 1 = stale found):
python3 scripts/check_fixture_freshness.py
```

### Match-day cron（local cron only — the ONLY approved scheduling）

```cron
# every 30 minutes on match days — lifecycle snapshot + gate state:
*/30 * * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py status-refresh >> logs/fixture_status_refresh.log 2>&1

# daily package refresh (lifecycle-gated; a finished fixture yields NO_VALID_TODAY_FIXTURE):
0 8 * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py refresh --lang zh --ref QG-TEST1 >> logs/growth_refresh_zh.log 2>&1
5 8 * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py refresh --lang vi --ref TT-VN88 >> logs/growth_refresh_vi.log 2>&1
10 8 * * * cd /path/to/worldcup2026 && python3 scripts/mvp2_growth_cli.py refresh --lang my --ref FO-MM21 >> logs/growth_refresh_my.log 2>&1
```
(These 08:00 UTC lines supersede the §3 10:00 examples. `mkdir -p logs` first. Cron only WRITES
files — there is no send code anywhere; FT+45 recap refresh stays manual or cron-assisted with
the same `refresh` command, **no auto-send**.)

### External strong-information reference（reference-only, P1.2 §6）
Manual template per day: `docs/data_audit/mvp2_daily_refresh/external_reference_YYYYMMDD.md`
(see `EXTERNAL_REFERENCE_TEMPLATE.md` in the same dir). Public prediction/forecast pages may be
READ as references only; raw wording never reaches customers — convert to the sanctioned
vocabulary (外部预期 / 公开预测倾向 / 市场共识 / 热度集中 / 情绪变化 / 冷门变量 / 临场变量),
no external trading links in customer copy.

## 4. Future options (documented only — DO NOT implement without explicit Owner GO)
- Render Cron Job running the same CLI against the repo (needs key custody decision).
- GitHub Actions scheduled workflow (off-main scheduling caveats per Track A design §1).

## 5. Match-day rhythm (manual, fits the runsheet)
T-12h: refresh → operator picks today-package → Owner GO → send. T-30 window: rescore send-kit
(NOT this CLI — A3 path). FT+recap approved: re-run refresh → recap package carries
`approval_status: approved` → recap follow-up send.
