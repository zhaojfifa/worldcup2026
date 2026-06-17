# R6.1 · Claude Self-Review — Runtime Pre-upload Customer-visible Guard

Verdict: **OPERATE** — the runtime content cutover now blocks customer-visible/de-model/betting/fake-
probability violations BEFORE any production upload. No product/UI/backend/schema change. send HOLD.

## Problem (from R6)
An optional secondary card was generated with engineering wording (模型 / mô hình / thiếu dữ liệu). It was
removed before final live state, but only AFTER a post-upload customer-visible check caught it. The check
must run BEFORE upload so a bad package never reaches production.

## Fix (scripts only)
- NEW `scripts/check_r6_runtime_preupload_customer_visible_guard.py` — `scan_package(pkg)` walks every
  CUSTOMER-VISIBLE text field (prediction i18n prediction/analysis/operations/copy_v2, observation i18n,
  share copy, selectedHotspot team labels) for banned terms and structurally rejects any non-null numeric
  win_prob/confidence. Banned (Owner R6.1 list + existing de-model/betting bans): zh 模型/数据不足/缺少数据/
  数据缺失/置信度/胜率/盲区 + betting (盘口/投注/下注/赔率/竞猜/让球/必中/稳赚/跟单/回报率); vi mô hình/
  thiếu dữ liệu/xác suất/tỷ lệ thắng + kèo/cửa trên/cửa dưới; en model unavailable/insufficient data/win
  probability/confidence score + betting/odds/handicap/bookmaker; ms model tidak tersedia/data tidak
  mencukupi/kebarangkalian menang. NOTE: bare 概率 (generic "probability/likelihood") is NOT banned — it is
  colloquial football wording allowed by check_customer_visible_copy; only win-claim forms (胜率/置信度 +
  the en/vi/ms "win probability") are blocked.
- `scripts/mvp2_runtime_content_cutover.py` — after assembling the package and BEFORE the runtime-content
  POST, runs scan_package; on any violation it RESTORES bundled artifacts, writes a
  CUTOVER_BLOCKED_CUSTOMER_VISIBLE report (exact field path + term), uploads NOTHING (production stays on
  the previous runtime package), and returns. send HOLD always.

## Proof
- selftest 6/6 (clean passes; 模型 blocks; mô hình blocks; fake win_prob blocks; fake confidence blocks;
  betting odds blocks).
- CLEAN package (the live R6 England primary) → PASS.
- BAD package (the R6 first-attempt Portugal operator_estimated 'model unavailable' copy) → BLOCKED with
  30 violations + exact field paths (predictions.1539003.i18n.zh.copy_v2.hook_headline — 模型, etc.).
- cutover wiring: scan_package runs before the runtime-content _post() call; block path restores + returns
  without upload.
- production UNCHANGED by the dry-run: still 2026-06-17 England primary, send HOLD.
- ★ The guard surfaced a real over-ban (概率) on the live England copy → corrected (概率 removed; 胜率/置信度
  kept) so the guard matches the Owner list and does not false-block colloquial copy.

## Live regression
R4 runtime_content_cutover PASS · live source consistency PASS (sel_source=runtime; one transient FAIL on a
slow homepage render, clean re-run PASS) · P5A homepage(src=runtime)/predict/recap/share PASS · customer-
visible 21/21 PASS. Live bundle unchanged (no frontend deploy).

## Boundaries
No homepage UI / product logic / backend / schema / scheduler change; no auto-send; no fake data; no env/
token committed; send HOLD.

## Positive-behavior note
Cold-start / low-source cards must use persona-safe wording (e.g. "缺少历史交锋，俅哥保守看小比分" / "信息
有限，先按稳态判断") or be omitted — never expose engineering/source weakness as product copy. R6 already
applied this by dropping the Portugal card; R6.1 enforces it automatically before upload.
