# R2 — DATA_MODEL_SOURCE_AUDIT

## Which existing sources can produce win_prob / recommended_score / risk_level / risk_note / confidence?

| Source | Produces | Nature | Maps to today's fixture? | Honest to surface? |
|---|---|---|---|---|
| **`backend/app/services/modeling/baseline.py`** (`predict` + `_stable_strength`) | win_prob, recommended_score, risk_level, risk_note, confidence | **mock/seed** — strengths are a **hash of the team name**, `ai_provider="mock"` | yes (by name) | **NO.** Output is noise: it scored Spain vs Cape Verde 40/22/38 (≈even — Spain is overwhelming). Surfacing it would be fabrication. |
| **`baseline` via DB `Match`→`Prediction`→`/api/v1/matches`** (`match_service.py`, `transform.ts`) | same five fields | seed (same model) + persisted | only fixtures seeded in the DB; today's are not | NO (same seed model) |
| **ScoutScore v0.2** (`scripts/mvp2_build_scoutscore_v0_2_factors.py`: `load_results`/`elo_snapshot`/`recent_form`/`upset_band`/`poisson_bands` over `data/external/kaggle/results.csv`) | recommended_score (Poisson band), risk_level (upset_band), risk_note (from Elo gap + form), an Elo-implied lean | **computed** from **real historical results** (Elo K=32, last-10 form, H2H) | **YES** when both teams are in kaggle (Belgium gap +129 etc.) | **YES** for recommended_score / risk_level / risk_note / lean. NOT for a precise win_prob/confidence number. |
| **ProductNarrative** (`productNarratives/*.json`) | main_lean, scoreline_view, risk word, tactical_read (LLM) | LLM over a ScoutScore frame | only the 5 hardwired ids (NOT today's) | yes (but not for today's fixture without generating) |
| **Operator** (artifact i18n) | all judgement fields | operator | always | yes, tagged operator_estimated |

## Real / seed / mock / computed / operator?
- `baseline.py` = **mock/seed** (name-hash placeholder). **Do not surface.**
- ScoutScore (kaggle Elo/form/Poisson) = **computed from real data**. **Use this.**
- ProductNarrative = **LLM** (real DeepSeek/Gemini, but only for old ids).
- Daily artifact judgement = **operator** (R1).

## Can they map to today's selected fixture (Belgium vs Egypt 1489377)?
- ScoutScore: **YES** — Belgium 1884.9 / Egypt 1755.6, gap +129; form10 7W-3D-0L vs 5W-3D-2L;
  `upset_band(129)`→medium; `poisson_bands(1.9,0.8)`→1-0/2-0/1-1. → `model_fields.source="computed"`.
- baseline.py: maps but noise → rejected.
- ProductNarrative: no (no id 1489377 narrative; generating one needs the manual LLM step = R2 chain).

## If not, why not?
- Spain vs Cape Verde: Cape Verde Islands **absent from kaggle** → Elo cold-start (None), 0 form matches
  → no honest computed model → that fixture would be operator_estimated only. (Not selected.)
- A precise **win_prob / numeric confidence**: Elo implies a probability, but per the compliance floor +
  Owner P8 Q1/Q3 it is **never shown as a customer number** → stays `null`.

## What minimum model/source fields can be honestly used today?
For Belgium vs Egypt (`source="computed"`, ScoutScore v0.2):
- `recommended_score` = "1-0" (Poisson primary), `backup_scores` = ["2-0","1-1"]
- `risk_level` = medium → "中"
- `risk_note` = derived from Elo gap +129 + Belgium GF37/GA6 vs Egypt's solidity
- `source_refs` = kaggle Elo (1884.9 / 1755.6, gap 129), form10 records, upset_band, Poisson bands
- `win_prob` = null, `confidence` = null (NOT surfaced)

## What should never be shown as real?
- `baseline.py` name-hash win_prob/scores (mock).
- Any numeric **win_prob** or numeric **confidence** to a customer (compliance floor — no fake probability).
- A computed source tag on a fixture whose teams are not in kaggle (e.g. Cape Verde) — that must read
  `unavailable` / `operator_estimated`, explained on `/internal/daily`.
