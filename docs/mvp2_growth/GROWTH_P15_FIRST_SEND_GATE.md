# Growth P1.5 — First Send Gate Closure

> Owner verdict 2026-06-13: P1.4 PASS (能更新 delivered). Prepare the first controlled send —
> **do not send automatically.** This doc tracks the 7 gates. First send requires an explicit
> per-channel Owner GO (Gate 7). No auto-send anywhere.

## Gate status (2026-06-13, branch feature/mvp2-growth-p1-5-first-send-gate)

| gate | status | evidence |
|---|---|---|
| 1 — Ambassador codes | ⛔ **OPERATOR (prod token)** | live `/api/v1/growth/click QG-TEST1` → `attached:false` ⇒ QG-TEST1 not created yet. Admin create endpoint is token-walled (no prod token for engineering). |
| 2 — Growth smoke | ◑ **PARTIAL / OPERATOR** | public `POST /api/v1/growth/click` LIVE (200); admin `/growth/admin/dashboard` correctly 401 without token. Full smoke (attached:true + counters + dashboard) needs Gate 1 first. |
| 3 — Customer visible copy | ✅ **PASS** | live visible scan 21/21 PASS · `check_growth_copy.py` PASS · no betting/trading vocab · no external trading links · no fake recap · no auto-send. |
| 4 — 1489371 lifecycle | ✅ **pre-kickoff PASS** · LIVE/FT = scheduled | SCHEDULED, today=True, T-692min. Live `/predict/1489371` StrongCallCard not frozen; `/share/fixture/1489371` card+QR not frozen; homepage hero = Brazil. LIVE/FT plan below. |
| 5 — First-send package | ✅ **GENERATED (not sent)** | `refresh --lang zh --ref QG-TEST1`: today=Brazil (registry), recap=Mexico (recap_ready only), orchestration recap_pending=3 / upcoming_no_narrative=2. No fabricated copy. |
| 6 — Operator runbook | ✅ **WRITTEN** | `docs/mvp2/FIRST_SEND_RUNBOOK_1489371.md` (channel/fixture/ref/package/screenshot/paste copy/pre+post checklists/stop conditions). |
| 7 — Owner GO | ⏳ **PENDING OWNER** | no send until `GO zh_internal_group QG-TEST1 fixture 1489371` (or per-channel equivalent). |

## Gate 4 — 1489371 LIVE/FT validation plan (operator, match-day)

Pre-kickoff (verified live now): hero visible · `/predict` pre-match recommendation · `/share/fixture` card available.

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
1. **Gate 1 (operator)**: create QG-TEST1 / TT-VN88 / FO-MM21 via `/internal/growth` with the real
   prod ADMIN_API_TOKEN (e.g. `POST /api/v1/growth/admin/ambassadors {code, lang, channel}`).
2. **Gate 2 (operator)**: live smoke — `/join?ref=QG-TEST1` → click+join-intent counters increment,
   `attached:true`, dashboard shows the event.
3. **Gate 7 (Owner)**: explicit per-channel GO.
4. **Match-day**: tonight's 1489371 LIVE/FT lifecycle validation (operator, per the plan above).

Engineering holds no prod token and cannot create codes, run the authenticated smoke, or send.
Everything generatable/verifiable without the token is done and green.
