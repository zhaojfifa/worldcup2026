# Growth P1.1b — Scheduled / Manual Package Refresh（operator-controlled）

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

## 4. Future options (documented only — DO NOT implement without explicit Owner GO)
- Render Cron Job running the same CLI against the repo (needs key custody decision).
- GitHub Actions scheduled workflow (off-main scheduling caveats per Track A design §1).

## 5. Match-day rhythm (manual, fits the runsheet)
T-12h: refresh → operator picks today-package → Owner GO → send. T-30 window: rescore send-kit
(NOT this CLI — A3 path). FT+recap approved: re-run refresh → recap package carries
`approval_status: approved` → recap follow-up send.
