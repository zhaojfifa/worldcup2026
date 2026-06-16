# NORMAL OPS R3 · Claude Self-Review — Content-Paired Day Cutover

Verdict: **OPERATE** — paired data+content cutover with a hard pre-upload gate; production protected.
Scope honored: NO homepage/product/UI/prediction-card/recap-page/share-page change; no scheduler; no
auto-send. R3 only coordinates artifacts to the same date + gates the upload.

## What changed (scripts only)
- NEW `scripts/mvp2_day_cutover.py` — orchestrates: sync (R2 source, api-football default; honors an
  editorial `--now` basis) → build homepage lifecycle for the SAME date → run the HARD GATE → upload to
  the backend ONLY if the gate passes (`--target`). On gate FAIL it RESTORES the bundled artifacts to
  their pre-cutover bytes (so a blocked cutover changes NO homepage build), writes a CUTOVER_BLOCKED
  report, and does NOT upload. send_status=HOLD always. Token (upload only) from $ADMIN_API_TOKEN, never
  printed.
- NEW `scripts/check_r3_day_cutover_consistency.py` — the gate: registry date == target; selectedHotspot
  date == target (blocks DATA-ONLY cutover); selected primary in slate + reviewed (copy_version +
  prediction_confirmed) + NOT finished (slate status); lifecycle primary == selectedHotspot; secondaries
  in slate; a finished recap fixture has a score + observation artifact.
- NEW `scripts/check_r3_no_data_only_cutover.py` + `scripts/check_r3_selected_content_matches_slate.py`.

## Command
`python3 scripts/mvp2_day_cutover.py --date YYYY-MM-DD --source api-football --target production`
(add `--now <ISO>` to set the editorial as-of basis; omit `--target` for a gate-only dry run.)

## Proof — both paths
- **PASS (paired):** `--date 2026-06-15 --source manual --now 2026-06-15T12:00:00+00:00 --target
  production` → lifecycle primary Belgium UPCOMING, secondary Spain/Saudi, recap Brazil-Morocco →
  **GATE PASS** → upload `{stored:true, fixture_count:6}`. Live consistency PASS (prod re-aligned to the
  committed baseline registry afterward).
- **BLOCK (data-only / no content):** `--date 2026-06-16 --source api-football --target production` →
  gate caught 4 failures (DATA_ONLY_CUTOVER: selectedHotspot 06-15 != 06-16; primary 1489377 not in slate;
  secondaries not in slate) → **CUTOVER_BLOCKED**, bundled artifacts restored (hashes unchanged), NO
  upload, production stayed on the green 06-15 baseline.

## Hard-gate guarantee
A new slate cannot reach production unless its selected primary/secondary/recap are present in the slate
AND backed by reviewed content for the same date. This closes the R2 gap (backend 06-16 vs frontend 06-15).

## Product/UI unchanged
Only scripts changed; no frontend/src component/page, no backend, no schema, no scheduler. P5A/P5B guards
unchanged and PASS live. Bundled FE artifacts left at the committed baseline (cutover restores on block;
the PASS demo's incidental timestamp diffs were reverted).

## Compliance
No fake score/event/lineup/injury/probability/confidence; no betting/odds/handicap language; no auto-send/
publish; send HOLD. Token never printed/committed; no env/secret committed.

## Guards
R3: consistency (selftest 3/3 + 06-15 PASS / 06-16 BLOCK), no-data-only (selftest 4/4 + 06-16 blocked),
selected-content-matches-slate (selftest 2/2 + 06-15 PASS). Reruns: R2 auto-refresh + manual-optional;
live API daily-source + source-consistency; P5A ×5; P5B lifecycle-rendering/no-finished-primary/recap-
handoff; customer-visible-copy — ALL PASS.

## Evidence
docs/qa_screenshots/normal_ops_r3_content_paired_day_cutover/ (01 paired cutover gate-pass · 02 consistency
gate before upload · 03 upload-only-after-gate · 04 internal-daily target date · 05 homepage target-date
primary · 06 predict · 07 recap observation · 08 share prediction · 09 share recap).

## Carryover
- Content-cutover to a genuinely NEW future date still needs reviewed prediction content + a selectedHotspot
  prepared for that date (content-factory/R1 work) — the gate correctly BLOCKS until that exists. The PASS
  path is demonstrable today only for 06-15 (the date with prepared content) via the editorial `--now`.
- LOW (inherited): sync side-writes the bundled FE manifest; the cutover snapshots+restores it on block,
  but ad-hoc direct `sync` still needs a manual restore.
