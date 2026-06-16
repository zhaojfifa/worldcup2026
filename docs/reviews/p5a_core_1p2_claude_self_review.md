# P5A · Claude Self-Review — Core 1+2 Content Quality

Verdict: **PASS** (pending Codex independent review + Owner merge).

## 1 primary + 2 secondary only
Primary 1489377 Belgium-Egypt; secondary 1489379 Saudi-Uruguay + 1489380 Spain-CapeVerde. No match-count
expansion. Spain-CapeVerde stays SECONDARY + operator_estimated (no primary promotion, honest cold-start).

## Copy v2 projected
All 3 prediction artifacts carry copy_version=p5a_v2 + a complete zh copy_v2 (hook/reason/pressure/risk/
watch/confidence/group); vi/my/en copy_v2 added (Han=0). Rendered: homepage primary (hook + reason +
risk), secondary cards (reason + risk, not bare schedule rows), /predict (full v2 block), recap
(result_judgment + what_was_right/wrong + model_correction + next_match_learning + OBSERVATION label).
rendered via i18n sync (apply) — proven on local preview screenshots 01–10.

## No generic forbidden phrases
Stripped "赛前倾向" from all leans; check_p5a_copy_contract + check_prediction_artifact PASS; growth-copy
PASS (fixed a 模型 label leak in the recap chrome). check_p5a_homepage/predict/recap guards scan rendered
DOM for the forbidden list and PASS.

## No fake data / no betting / no auto-send
win_prob/confidence null; confidence_language qualitative only; no betting/odds; no fabricated event
(recap stays OBSERVATION_ONLY, labelled); send_status HOLD everywhere; reviewed-JSON gate intact.

## operator_estimated not primary
Spain-CapeVerde is secondary; its copy is explicit that the call is an operator estimate (no computed
model, cold-start), score is "估的不是算的".

## Screenshots prove visible improvement
docs/qa_screenshots/p5a_core_1p2_content_quality/local/ (01–10): homepage primary hook+reason+risk,
yesterday recap, two secondary cards, /predict ×3, recap right/wrong/correction, internal-daily copy
version, prediction + recap share.

## Rendered guards inspect live page areas
6 P5A guards: copy_contract (JSON), homepage/predict/recap/share (rendered DOM via headless Chrome),
internal_daily_trace (source). All --selftest pass; 4 rendered PASS on local preview.
