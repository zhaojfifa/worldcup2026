# Growth P1.5 — First Send Gate Closure

> Owner verdict 2026-06-13: P1.4 PASS (能更新 delivered). Prepare the first controlled send —
> **do not send automatically.** This doc tracks the 7 gates. First send requires an explicit
> per-channel Owner GO (Gate 7). No auto-send anywhere.

## Gate status (2026-06-13)

| gate | status | evidence |
|---|---|---|
| 1 — Ambassador codes | ✅ **PASS** | operator created QG-TEST1 / TT-VN88 / FO-MM21 in production (all active). Independently re-confirmed live: `POST /api/v1/growth/click` → `attached:true` for all three. |
| 2 — Growth smoke | ✅ **PASS** | click `attached:true` ×3 · join-intent `attached:true` ×3 · `/internal/growth` shows 3 active codes, click + join-intent counts visible, **3 pending test join-intents** · **contribution value = 0** (none issued) · **no send performed**. |
| 3 — Customer visible copy | ✅ **PASS** | live visible scan 21/21 PASS · `check_growth_copy.py` PASS · no betting/trading vocab · no external trading links · no fake recap · no auto-send. (P1.5b Daily Featured Copy Policy live: 今日复盘 = Mexico only / 今日赛况 已完赛 / 即将开赛; legacy 生成中/待生成 wording removed.) |
| 4 — 1489371 lifecycle | ✅ **pre-kickoff PASS** · LIVE/FT = scheduled tonight | SCHEDULED, today=True. Live `/predict/1489371` StrongCallCard not frozen (主看 / 主比分 2-1 / 备选); homepage hero = Brazil. LIVE/FT plan below — operator runs at the match window (KO 22:00 UTC). |
| 5 — First-send package | ✅ **GENERATED (not sent)** | `package today --fixture 1489371 --lang zh --ref QG-TEST1`: lifecycle_gate=allowed, today=Brazil (registry), recap=Mexico (recap_ready only); paste-ready copy + 30s script; no fabricated copy. `docs/data_audit/mvp2_growth_packages/today_1489371_zh_QG-TEST1.md`. |
| 6 — Operator runbook | ✅ **WRITTEN** | `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md` (channel/fixture/ref/package/screenshot/paste copy/pre+post checklists/stop conditions). |
| 7 — Owner GO | ⏳ **PENDING OWNER** | no send until `GO zh_internal_group QG-TEST1 fixture 1489371` (or per-channel equivalent). |

## Gate 1 / Gate 2 closure (2026-06-13)

**Gate 1 — PASS.** QG-TEST1 / TT-VN88 / FO-MM21 created in production and active.

**Gate 2 — PASS.**
- click `attached=true` for all three codes.
- join-intent `attached=true` for all three codes.
- `/internal/growth` dashboard shows 3 active codes with click + join-intent counts and **3 pending test join-intents**.
- **no contribution value issued** (contribution value = 0).
- **no send performed**.

Notes / engineering integrity:
- The pending test join-intents were **left unconfirmed** (not approved/rejected) — no MTC credit path triggered.
- Engineering holds no prod ADMIN_API_TOKEN: codes were created by the operator; engineering only
  re-confirmed `attached:true` via the public click endpoint. Those confirmation probes each added
  **one attached click** per code (same path as the smoke), so live click counts may read one higher
  than the operator's initial `click=1` snapshot — counters only, no contribution, no send.

## Gate 4 — 1489371 LIVE/FT validation plan (operator, match-day)

Pre-kickoff (verified live now): hero visible · `/predict` pre-match recommendation not frozen · `/share/fixture` card available.

At/after kickoff (22:00 UTC) — operator runs + records:
```bash
python3 scripts/mvp2_growth_cli.py status-refresh           # 1489371 -> LIVE (today_package_allowed=false)
python3 scripts/mvp2_growth_cli.py refresh --lang zh --ref QG-TEST1   # today REFUSED -> NO_VALID_TODAY_FIXTURE
python3 scripts/check_fixture_freshness.py
```
Expect: pre-match recommendation FREEZES (`/predict/1489371` → 比赛进行中/复盘生成中); today package
refused; `/share/fixture/1489371` shows frozen card (not a fresh pre-match QR).

At FT / FT+45: lifecycle → FINISHED → RECAP_PENDING (unless an A4 recap is bundled). After a daily
match-sync + upload, the live registry shows 1489371 recap-needed; `recap_queue` updates; **no fake
recap is generated** (recap-queue lists it as NEEDS_A4_RECAP).

## Remaining blockers to first send
1. **Gate 4 (operator, match-day)**: tonight's 1489371 LIVE/FT lifecycle validation per the plan above.
2. **Gate 7 (Owner)**: explicit per-channel GO (e.g. `GO zh_internal_group QG-TEST1 fixture 1489371`).

Gates 1, 2, 3, 5, 6 are closed/green. Gate 4 pre-kickoff is green; its LIVE/FT half runs tonight.
No send occurs until Gate 4 LIVE/FT validation passes **and** the Owner gives an explicit per-channel GO.
