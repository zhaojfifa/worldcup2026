# P8 — TARGET_CONTENT_FACT_SCHEMA

> A single schema that combines the historical model fields and the current operator artifact. It
> **extends** today's `PredictionArtifact` (`frontend/src/data/predictionArtifacts.ts`) by formalising the
> already-declared-but-null sockets (`data_snapshot` → `source_facts`, `modeling_output` → `model_fields`,
> `generated_judgment` → `llm_judgment`). **Backward compatible**: the existing flat `i18n` judgement and
> `field_sources` map keep driving render; new consumers prefer `model_fields` when present.
>
> **Honesty rules baked in:** never require a fake `win_prob`/`confidence`; every model value carries a
> `source`; `source:"unavailable"` is a first-class state; numbers render only with their source tag.

```jsonc
{
  "fixture_identity": {
    "fixture_id": null,                 // internal numeric id, or null for an unmapped manual fixture
    "external_game_id": "manual:Nether-Japan-20260614",
    "fixture_key": "manual:Nether-Japan-20260614",  // == route key (leadKey: id ?? external_game_id)
    "home": "Netherlands",
    "away": "Japan",
    "kickoff_utc": null,                // null until known; never invented
    "status": "scheduled"               // mirrors lifecycle status
  },

  "source_facts": {
    "fixture_source": "manual_slate",   // KNOWN map | manual_slate | api_football
    "data_mode": "manual",              // api | seed | manual | operator
    "has_model_fields": false,          // true once model_fields.*.source != "unavailable"
    "source_refs": []                   // kaggle/api provenance handles when computed; [] when operator
  },

  // The historical numeric tier (Era 0 baseline.py / Era 1 ScoutScore). Provenance-first.
  // win_prob/confidence stay null + source "unavailable" unless a real source backs them.
  "model_fields": {
    "win_prob": null,                   // {home,draw,away} ints summing to 100, OR null
    "recommended_score": null,          // band string, e.g. "2-1 / 1-1", OR null
    "risk_level": null,                 // low|medium|high (or localized word), OR null
    "risk_note": null,
    "confidence": null,                 // numeric 0-100 ONLY if computed/seed; else null (no probability promise)
    "source": "unavailable"             // computed | seed | operator_estimated | unavailable
  },

  // The qualitative LLM/operator judgement (Era 1 narrative / Era 2 operator artifact).
  "llm_judgment": {
    "main_lean": "赛前倾向荷兰，但冷门风险不低",
    "primary_score": "2-1",
    "backup_scores": ["1-1", "2-2"],
    "top_variable": "日本反击效率与荷兰首发边路配置",
    "why": "荷兰整体推进和定位球更稳定，但日本转换速度会制造波动",
    "external_expectation": ["公开预测倾向偏向荷兰", "..."],   // safe vocab only
    "tactical_read": ["...", "..."],
    "risk_factors": ["...", "..."],     // each may carry {text, source_refs[], assumption_flag} when reconnected
    "t30_checklist": ["首发阵容与位置", "..."]
  },

  "operator_confirmation": {
    "confirmed": true,
    "confirmed_by": "",                 // operator handle; "" if not recorded
    "confirmed_at": "",                 // ISO; "" if not recorded
    "edited_fields": []                 // which fields the operator overrode vs the generated draft
  },

  "operations": {
    "share_copy": "今日主推：荷兰 vs 日本 …",
    "share_card_title": "俅哥今日热点 · 荷兰 vs 日本",
    "join_cta": "加入临场情报群"
  },

  "safety": {
    "no_betting_vocab": true,
    "no_fake_probability": true,        // enforced: win_prob/confidence numeric ONLY when source != operator/unavailable
    "no_auto_send": true
  }
}
```

## Field-by-field provenance contract (the `source` enum)

| Block.field | Allowed `source` values | Numeric render allowed? |
|---|---|---|
| `model_fields.win_prob` | `computed` (ScoutScore/Poisson), `seed` (baseline.py placeholder, **disclosed**), `unavailable` | only if `computed`/`seed` **and** Owner Q1/Q3 GO; else hidden |
| `model_fields.confidence` | `computed`, `seed`, `unavailable` | only if `computed`/`seed`; **never** `operator_estimated` as a number (Owner Q3) |
| `model_fields.recommended_score` | `computed`, `seed`, `operator_estimated`, `unavailable` | yes (a scoreline is a call, not a probability) |
| `model_fields.risk_level` / `risk_note` | `computed`, `operator_estimated`, `operator_confirmed`, `unavailable` | yes (qualitative band) |
| `llm_judgment.*` | LLM (with `source_refs`) or `operator_confirmed` | n/a (prose) |

## Mapping to the existing live artifact (no breaking change)

| Target schema block | Existing `PredictionArtifact` location |
|---|---|
| `fixture_identity` | top-level `id`/`external_game_id`/`fixture_key`/`home`/`away`/`kickoffUtc`/`status` |
| `source_facts` | NEW (derive from `source` + `field_sources`); supersedes ad-hoc `source` string |
| `model_fields` | the **already-declared `modeling_output`** socket (currently `null`) |
| `llm_judgment` | the existing `i18n[loc].prediction` + `analysis` (per-locale) and/or `generated_judgment` |
| `operator_confirmation` | existing `prediction_confirmed` + `field_sources` + `t30` |
| `operations` | existing `i18n[loc].operations` |
| `safety` | existing top-level `safety` |

**Localization note:** the current artifact nests judgement under `i18n[zh|vi|my|en]`. The target keeps
that (the table above shows the zh slice flattened for readability). `model_fields`/`source_facts` are
**locale-independent** and live at the top level (numbers and provenance are not translated).

**Do not require fake values.** A valid artifact may ship with `model_fields.source:"unavailable"` and
all numerics `null` — `has_model_fields:false`. The guard asserts the *object and its source tag exist*,
not that any number is present.
