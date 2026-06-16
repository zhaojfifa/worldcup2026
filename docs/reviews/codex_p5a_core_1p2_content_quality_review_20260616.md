# Codex Independent Review — P5A Core 1P2 Content Quality

- Branch: `feature/mvp2-p5a-core-1p2-content-quality`
- Reviewer: Codex (independent / adversarial)
- Date: 2026-06-16
- Method: source inspection + local headless-Chrome rendered-DOM guards against a real `vite preview` build (bundle `index-CZFS7sOc.js`), not trusting the self-review.

---

## Item 1 — Copy v2 exists AND renders — PASS

All three artifacts carry `copy_version: "p5a_v2"` and `i18n.zh.copy_v2` with 7 non-empty fields (verified by reading the JSON):

- `match_Belgium-Egypt-20260615.json` — hook/main_reason/pressure_point/hidden_risk/tactical_watch/confidence_language/group_hook all non-empty, specific (e.g. hook "比利时该赢，但这是效率局不是碾压局——首球来得早不早是关键").
- `match_SaudiArabia-Uruguay-20260615.json` — 7/7 non-empty, specific (Elo 1872 vs 1645, 差 227).
- `match_Spain-CapeVerde-20260615.json` — 7/7 non-empty, and honest about cold-start ("佛得角是数据空白，比分是估的不是算的").

Rendering confirmed in code:
- `ArtifactTacticalRoom.tsx` lines 152-160 render all 7 copy_v2 fields.
- `HomeProductLoop.tsx` — HotspotPrediction renders hook_headline (226), main_reason (240), hidden_risk (241); SecondaryMatchCard renders main_reason (294), hidden_risk (295).
- `ObservationReceipt.tsx` renders the recap v2 fields (see Item 3).

Proof it renders (local `vite preview` on `http://127.0.0.1:4344`, headless Chrome rendered DOM):
- `check_p5a_homepage_content_quality.py --base-url` → **PASS**
- `check_p5a_predict_content_quality.py --base-url` → **PASS** (3 pages: hook+score+reason+pressure+risk+watch+share)
- `check_p5a_recap_content_quality.py --base-url` → **PASS**
- `check_p5a_share_content_quality.py --base-url` → **PASS**
- `check_p5a_copy_contract.py` → **PASS** (3 predictions p5a_v2 + copy_v2 complete · recap v2 · no forbidden)

Note: these guards take `--base-url` (not `--base`). An initial run with the wrong flag silently fell back to the production URL and reported FAIL — production still serves the OLD generic copy and lacks v2. Re-running with `--base-url http://127.0.0.1:4344` against the fresh local build gives PASS on all four. This is itself a useful finding: the new copy is NOT yet deployed; PASS is on the local build only.

## Item 2 — No forbidden generic phrases — PASS_WITH_PATCHES

Grep of the 3 zh artifacts + observation for the 5 listed phrases:
- `赛前倾向` — ABSENT
- `双方实力接近` — ABSENT
- `临场变量影响有限` — ABSENT
- `模型判断方向较为明确` — ABSENT
- `值得继续跟踪` — **PRESENT** in `observation_1489371.json` `i18n.zh.next_impact`: "下一场影响：巴西后续需要下调胜负确定性，摩洛哥韧性值得继续跟踪".

The phrase is embedded inside a substantive sentence (not standalone vague filler), and it is NOT in the P5A guard banlists, so `check_p5a_*`, `check_prediction_artifact.py`, and `check_growth_copy.py` all PASS. But the review explicitly asked to confirm this phrase absent, and it is present. Minor patch recommended: rephrase `next_impact` to drop "值得继续跟踪" for full compliance with the no-generic-filler intent.

`check_prediction_artifact.py` → **PASS** (4 prediction + 1 observation; strong call + receipt wired; safe vocab).
`check_growth_copy.py` → **PASS** (32 files).

## Item 3 — Recap quality — PASS

`observation_1489371.json` `i18n.zh` contains all required fields:
- `result_judgment`: "部分命中（PARTIAL）"
- `what_was_right`: "看对的：比分区间——赛前给的备选 1-1 正是终场比分…"
- `what_was_wrong`: "看错的：胜负方向——主推偏向巴西取胜，实际被摩洛哥逼平，把巴西的控制力高估了"
- `model_correction`: "修正：下调巴西这类强队对中下游强硬防反球队的胜负确定性…"
- `next_match_learning`: present
- `source_label`: "来源：赛后观察回执（OBSERVATION_ONLY）· 完整事件数据未接入，不展开完整战术复盘"

`/recap` rendering verified: `check_p5a_recap_content_quality.py --base-url` PASS (judgment+right+wrong+correction+share; observation labelled; no fake event). No fabricated minute-event: grep for `第N分钟/进球/射门/点球/红牌` found only "首粒进球时间" inside `next_match_learning` (generic "first-goal timing" reasoning, not a fabricated event). No "第N分钟…进球" pattern present.

## Item 4 — operator_estimated not primary; no fake data — PASS

- `dailyContentQueue.json`: `primary_hotspot.fixture_key = "1489377"` (Belgium-Egypt). Spain-CapeVerde (`1489380`) is in `secondary_matches`, NOT primary.
- `model_fields.source`: Belgium=`computed`, Saudi=`computed`, Spain-CapeVerde=`operator_estimated`. The operator-estimated match is the secondary one, and its copy is explicit about it ("来源是操作组估计，不是系统算出来的", "佛得角无历史数据").
- `win_prob` and `confidence` are `null` in all three model_fields.
- `confidence_language` is qualitative (e.g. "方向把握偏高、比分把握中等"); no `%` anywhere in the artifacts (grep: NO % in artifacts).

## Item 5 — No backend/schema/auto-send — PASS

`git diff --name-only main..HEAD` touches only `scripts/`, `frontend/src/`, and `docs/`. No `backend/`, no schema/migration files.
- `dailyContentQueue.json` `send_status: "HOLD"`.
- Build script `mvp2_build_daily_prediction_artifact.py` is explicitly NO-auto-LLM, NO-auto-send: `prompt` emits a prompt file, `apply` validates an operator-reviewed JSON and merges it (`reviewed_applied=true`). `validate_reviewed()` rejects any win_prob/numeric confidence/betting vocab and requires `safety.no_fake_probability/no_auto_send=true`. Reviewed-JSON gate intact (build artifacts only apply reviewed JSON from `docs/data_audit/mvp2_predictions/reviewed/`).
- Frontend build PASS (`npm run build`, 149 modules, bundle `index-CZFS7sOc.js`).

## Item 6 — Screenshots prove improvement — PASS

`docs/qa_screenshots/p5a_core_1p2_content_quality/local/` has 10 PNGs (01..10) as listed.
- `01-home-top-primary.png` spot-read: homepage primary = Belgium vs Egypt with strong hook ("比利时该赢，但这是效率局不是碾压局——首球来得早不早是关键"), 主比分 1-0 (参考 2-0/1-1), data reason ("Elo 1885 对 1756、近 10 场 7 胜进 37 球…"), named risk ("埃及 5-4-1 死守加一侧快反…拖成 1-1"), key watch. Specific + strong, not generic.
- `07-recap-upgraded.png` spot-read: recap shows 部分命中(PARTIAL), 看对了什么 (比分区间/备选 1-1), 看错了什么 (胜负方向高估巴西控制力), 判断修正 (下调强队对防反球队的确定性), 下一场要带走的, and OBSERVATION_ONLY source label. Right/wrong/correction all specific.

---

## Guard run summary
| Guard | Result |
|---|---|
| check_p5a_homepage_content_quality.py (local --base-url) | PASS |
| check_p5a_predict_content_quality.py (local --base-url) | PASS |
| check_p5a_recap_content_quality.py (local --base-url) | PASS |
| check_p5a_share_content_quality.py (local --base-url) | PASS |
| check_p5a_copy_contract.py | PASS |
| check_prediction_artifact.py | PASS |
| check_growth_copy.py | PASS |
| frontend npm run build | PASS |

## Findings
1. (Minor) Forbidden phrase `值得继续跟踪` is present in `observation_1489371.json` `i18n.zh.next_impact`. Not in any guard banlist (slips through), embedded in a substantive sentence, but the review explicitly required it absent. Recommend rephrasing.
2. (Context, not a defect) The new v2 copy is verified on the LOCAL build only. Production (`worldcup2026-izid.onrender.com`) still serves the old generic copy — deployment is pending. Running the guards without `--base-url` defaults to production and FAILs.

Codex verdict: PASS_WITH_PATCHES
