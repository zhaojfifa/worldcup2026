# R3 · MODEL_FIELD_COVERAGE

> Phase A — audit only. Audited 2026-06-15. Source of truth for fields:
> `scripts/mvp2_build_daily_prediction_artifact.py` (`model_lookup` / `build_model_fields` /
> `build_source_facts`), `frontend/src/data/predictionArtifacts.ts`, and the live artifact
> `frontend/src/data/predictionArtifacts/match_Belgium-Egypt-20260615.json`.

## Hard rule (Owner, non-negotiable)

Do not fake `win_prob` or `confidence`. If unavailable → `null` internally, hidden/explained
externally. Enforced in three places: the builder refuses to emit numbers; the TS type pins
`win_prob: null` / `confidence: null`; the guards (`check_prediction_artifact.py`,
`check_daily_content_flow.py`) FAIL on any non-null value.

## Coverage matrix

| Field | Available? | Source | Computed/manual/mock | Customer-visible? | Internal-visible? | In prompt? | In artifact? | On page? |
|-------|-----------|--------|----------------------|-------------------|-------------------|------------|--------------|----------|
| fixture_id | ✓ | API-FOOTBALL / manual slate | both | ✓ | ✓ | ✓ (fixture_key) | ✓ | ✓ |
| external_game_id | ✓ | API-FOOTBALL | computed | partial | ✓ | ✓ | ✓ | manifest |
| home / away | ✓ | API-FOOTBALL / manifest | computed | ✓ | ✓ | ✓ | ✓ | ✓ |
| kickoff_time | ✓ | API-FOOTBALL | computed | ✓ | ✓ | ✓ | ✓ | ✓ |
| status | ✓ | API-FOOTBALL / lifecycle | computed | ✓ | ✓ | ✓ | ✓ | ✓ |
| actual score | ✓ (post-match) | API-FOOTBALL | computed | ✓ (recap) | ✓ | n/a | observation/recap | ✓ (recap) |
| Elo (home/away) | ✓* | kaggle (offline) | computed | ✗ (internal only) | ✓ | ✓ as `source_refs` | ✓ in source_facts | ✗ never raw |
| ranking | ✗ | — (FIFA rank not ingested) | — | ✗ | ✗ | ✗ | ✗ | ✗ |
| form (last-10) | ✓* | kaggle (offline) | computed | ✗ | ✓ | ✓ as `source_refs` | ✓ | ✗ never raw |
| Poisson bands | ✓* | computed from Elo gap | computed | ✗ | ✓ | ✓ (drives recommended/backup) | ✓ source_refs | ✗ never raw |
| recommended_score / primary_score | ✓ | ScoutScore / operator | computed OR operator_estimated | ✓ | ✓ | ✓ | ✓ | ✓ |
| backup_scores | ✓ | ScoutScore / operator | computed OR operator_estimated | ✓ | ✓ | ✓ | ✓ | ✓ |
| risk_level | ✓ | ScoutScore / operator | computed OR operator_estimated | ✓ | ✓ | ✓ | ✓ | ✓ |
| risk_note | ✓ | ScoutScore / operator | computed OR operator_estimated | ✓ | ✓ | ✓ (template) | ✓ | ✓ |
| confidence | ✗ by rule | — | **intentionally null** | ✗ | ✗ (null) | ✗ forbidden | ✓ as null | shown as "暂无数值置信度" |
| win_prob | ✗ by rule | — | **intentionally null** | ✗ | ✗ (null) | ✗ forbidden | ✓ as null | shown as "暂无自动胜率" |
| source_refs | ✓ | builder | computed | ✗ | ✓ | implicit | ✓ source_facts | internal/daily |
| missing_fields | ✓ | builder | computed | ✗ | ✓ | ✓ (DO NOT INVENT) | ✓ source_facts | internal/daily |

`*` Cold-start teams (not in kaggle history) → `model_fields.source=operator_estimated`, with the
reason recorded in `content_chain.model_lookup_note`; numbers are never invented for them.

## Live evidence

**Belgium-Egypt (`model_fields.source=computed`):**
```json
"model_fields": {
  "win_prob": null, "recommended_score": "1-0", "backup_scores": ["2-0","1-1"],
  "risk_level": "中", "risk_note": "Belgium 实力领先（Elo 差 129，近 10 场 7W-3D-0L）…",
  "confidence": null, "source": "computed", "model_status": "scoutscore_v0_2_elo_form",
  "no_fake_probability": true
}
"source_facts": {
  "fixture_source": "api_football", "data_mode": "api", "has_model_fields": true,
  "source_refs": ["kaggle Elo: Belgium 1885 / Egypt 1756 (gap 129)",
                  "form10: Belgium 7W-3D-0L … · Egypt 5W-3D-2L …",
                  "poisson_bands(1.78,0.72)=1-0/2-0/1-1"],
  "missing_fields": ["win_prob","confidence"]
}
```

**Netherlands-Japan (`model_fields.source=operator_estimated`)** — manual slate, `source_refs:[]`,
`recommended_score:"2-1"`, win_prob/confidence null. Honest: no computed model was available.

## Coverage verdict

- **Strong & honest:** fixture identity, kickoff, status, score, recommended/backup score, risk
  level/note are present and source-tagged (`computed` vs `operator_estimated` vs `unavailable`).
- **Deliberately absent (correct):** win_prob, confidence — null everywhere; ranking — not ingested.
- **Internal-only (correct):** raw Elo / form / Poisson never reach the customer surface; they appear
  only as provenance text in `source_facts.source_refs` and on `/internal/daily`.
- **P1 gap:** `recommended_score`/`risk_level` are still single ScoutScore Poisson outputs, not a
  calibrated probability model — acceptable because they are presented as a *reference band*, not a
  probability, and `no_fake_probability=true` is asserted and guarded.
