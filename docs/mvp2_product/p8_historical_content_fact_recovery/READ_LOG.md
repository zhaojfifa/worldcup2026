# P8 Discovery — READ_LOG

> Every file inspected, with reason / key finding / reuse-discard-uncertain.
> Refs: tag = `main-backup-pre-p15b-daily-featured-copy-20260613` (`e3c73a3`) · current main = `be09770`.

---

### Backend — historical structured model-field producers

**Source:** current main `be09770` (identical on the tag — `git diff` shows no change to these files)
**File:** `backend/app/services/modeling/baseline.py`
**Reason:** primary producer of `win_prob`/`recommended_score`/`risk_level`/`risk_note`/`confidence`.
**Key finding:** `predict(PredictorInput)` is a **deterministic RULES model, NOT ML** (docstring line 4).
Returns `prob_home/draw/away` (sum 100 via largest-remainder), `confidence` (45–88 from decisiveness
margin), `risk_level` (low/medium/high from margin+volatility), hand-mapped Chinese `risk_note`,
`recommended_score` (band string), `model_version="baseline-rules-v1"`, `ai_provider="mock"`.
`build_input_for_match()` derives strengths from `_stable_strength(team.name)` — a **seed hash in
[40,72]**, i.e. placeholder, not real form/xG/injuries. **These historical numbers are computed but
from placeholder inputs (seed-grade), not real data.**
**Reuse / discard:** **REUSE** as a P1 reference (the only place a numeric `confidence`/`win_prob` is
honestly producible). For P0 it is the candidate "seed/computed" source if Owner allows a band.

**File:** `backend/app/schemas/match.py`
**Reason:** the wire contract that carried model fields to the frontend.
**Key finding:** `MatchListItem` (lines 53-76) carries `win_prob` (WinProbOut), `recommended_score`,
`risk_level`, `risk_note`, `confidence`, **plus the P1.2b lifecycle block** (`lifecycle_state`,
`pre_match_allowed`, `today_package_allowed`, `recap_needed`, `recap_ready`, `freshness_reason` — all
Optional, "computed at response time, not stored"). `MatchDetail` adds `free_note` + `live_correction`.
**This single schema is where the model-field layer AND the lifecycle layer coexisted.**
**Reuse / discard:** **REUSE** — it is the canonical shape the target P8 schema should mirror.

**File:** `backend/app/models/prediction.py` · `backend/scripts/seed.py` · `backend/app/jobs/fixtures_sync.py`
**Reason:** DB persistence + seeding + sync of the model fields.
**Key finding (grep):** `recommended_score`/`risk_note` live on the `Prediction` ORM model, are seeded by
`seed.py`, and refreshed by `fixtures_sync.py`. So historically the fields were **DB-persisted per match**
and refreshed on sync — a real runtime store existed (Render Postgres), just for the OLD `/matches` path.
**Reuse / discard:** **UNCERTAIN / P1** — a backend runtime store for daily artifacts is the P1 end-state
(option E), but reusing the OLD `Prediction` table for `id=null` manual fixtures is not directly possible
(no fixture row). Note for P1.

**File:** `backend/app/services/match_service.py`
**Reason:** assembles `MatchListItem`/`MatchDetail` from ORM + predictor.
**Key finding (grep):** references all five model fields; this is the service that joined a `Match` to its
`Prediction` and computed the freshness block. The `/api/v1/matches` endpoint reads from here.
**Reuse / discard:** REUSE as the reference for "how the fields reached the API".

**File:** `backend/app/services/daily_fixtures_service.py` · `backend/app/services/lifecycle.py`
**Reason:** the NEW (P1.3c) backend source for the daily manifest.
**Key finding:** `daily_fixtures_service` carries the **lifecycle** fields but **ZERO model fields**
(`git grep win_prob|recommended_score|risk_level|confidence` over it = empty). This is the exact boundary
where the model-field layer is dropped: the daily manifest backend deliberately serves identity+lifecycle
only. `lifecycle.py` owns the freshness/lifecycle computation (healthy, canonical).
**Reuse / discard:** **REUSE the lifecycle half; the model-field gap is THE breakage** (see
`CURRENT_DAILY_REFRESH_BREAKAGE.md`).

---

### Frontend — how model fields reached the screen (historical path)

**File:** `frontend/src/api/transform.ts` + `frontend/src/api/client.ts`
**Reason:** snake_case API → camelCase `Match` mapping.
**Key finding:** `listItemToMatch()` maps `win_prob→winProb`, `recommended_score→recommendedScore`,
`risk_level→riskLevel`, `risk_note→riskNote`, `confidence→confidence`. `mergeDetail`/`mergeReport` add
`free_note`, `live_correction`, features, trend. **This is intact and still imported.**
**Reuse / discard:** REUSE (this is the live consumer of the OLD model-field layer).

**File:** `frontend/src/store/useAppStore.ts`
**Reason:** does any page still consume the model-field path?
**Key finding (grep lines 64-87):** `api.getMatches()` → `items.map(listItemToMatch)` → store; falls
back to mock on failure. **`HomePage` imports `useAppStore` and still loads these matches** — but they
render the **legacy/folded mock tiles** (WinBar etc.), NOT the daily hotspot loop. So the model-field
layer is **alive but pointed at the deprecated surface**.
**Reuse / discard:** REUSE — proves the loss is "bypass", not "deletion".

**File:** `frontend/src/pages/HomePage.tsx`
**Reason:** does the homepage join the manifest to model fields?
**Key finding:** imports BOTH `useAppStore` (legacy matches) AND `fetchDailyManifest` + `HomeProductLoop`
(daily loop). The two are **parallel, not joined** — the product loop renders from the manifest +
artifacts; the model fields from the store feed only the demoted tiles.
**Reuse / discard:** REUSE as the integration point for P8 (where a `model_fields` block would surface).

---

### Frontend — the daily-refresh path (current product)

**File:** `frontend/src/data/dailyFixtures.ts`
**Reason:** the manifest schema + product-loop selection.
**Key finding:** `DailyFixtureRow` = `id`, `external_game_id`, `home`, `away`, `kickoffUtc`, `status`,
`lifecycle_state`, `preMatchAllowed`, `recapReady`, `recapNeeded`, `renderable`, hero/recap/next
candidates, `scoreHome/scoreAway`. **NO model fields.** `fetchDailyManifest()` = backend → static →
bundled fallback. `selectProductLoop()` + `leadReadiness()` choose the lead via `selected_hotspot` +
`hasPredictionArtifact()`. `leadKey()` = `id ?? external_game_id`.
**Reuse / discard:** REUSE the structure; **the missing model-field columns are the recovery target**.

**File:** `frontend/src/data/predictionArtifacts.ts`
**Reason:** the P4/P5/P7 recovery layer for an `id=null` hotspot.
**Key finding:** already has the scaffolding for recovery — `field_sources?: Partial<Record<string,
FieldSource>>` where `FieldSource = 'operator_confirmed'|'operator_estimated'|'model'|'generated'|
'unavailable'`, plus **`data_snapshot`/`modeling_output`/`generated_judgment` optional objects already
declared but documented as "stay null until the P1 model + generation bridge fills them"** (lines 59-62)
and `t30` slot. `ArtifactPrediction` carries `primary_direction/score_call/backup_score/confidence/
risk_level/risk_note/top_variable/why`. Resolves by `fixture_key` or `id`.
**Reuse / discard:** **REUSE — this is the designated socket.** P8 P0 = populate `modeling_output` /
the `model_fields` block + flip `field_sources` from `unavailable` to a real provenance.

**File:** `frontend/src/data/predictionArtifacts/manual_Nether-Japan-20260614.json`
**Reason:** the live daily hotspot — what is actually produced today.
**Key finding:** `id:null`, `source:"operator_confirmed"`, **all judgement fields
`field_sources=operator_confirmed`; `win_prob` & `confidence` = `"unavailable"`;
`data_snapshot`/`modeling_output`/`generated_judgment` all `null`.** `score_call:"2-1"`,
`risk_level:"中高"`, `confidence:null` — hand-typed, no model provenance. The `note` explicitly says the
structured blocks "stay null until the P1 model + generation bridge fills them." Confirms the owner's
"only identity/status, lacks prediction/model fields" observation **at the structured level** (the
qualitative judgement IS present, the numeric/provenanced model layer is not).
**Reuse / discard:** REUSE as the worked example the schema must upgrade.

**File:** `frontend/src/data/selectedHotspot.json` + `selectedHotspot.ts`
**Reason:** P7 editorial-selection mechanism.
**Key finding:** tiny pointer — `date`, `fixture_key`, `home/away`, `source`,
`prediction_artifact_path`, `operator_confirmed`, `status:"active"`. This is the P7 mechanism the owner
wants **preserved**. No model fields here (by design — it is a selector, not content).
**Reuse / discard:** REUSE / **PRESERVE** (Owner Q5/Q6).

**File:** `frontend/src/data/productNarrativeData.ts` + a sample `productNarratives/1489371.zh-CN.json`
**Reason:** the LLM narrative layer — does it carry the numeric model fields?
**Key finding:** `ProductNarrative` carries `main_lean`, `scoreline_view` (a band STRING, e.g.
"2-1、1-1、2-2"), `risk_level` (a WORD), `risk_factors[]` (ProductFactor with `source_refs` +
`assumption_flag`), `tactical_read`, `validated_factors`, etc. — **but NO `win_prob`, NO numeric
`confidence`, NO `recommended_score` field.** So even historically, the numeric trio came ONLY from the
backend `baseline.py` path; the LLM layer always expressed the call qualitatively. `DATA` is a **hard
map of 5 fixture ids** → fixture-locked.
**Reuse / discard:** REUSE the qualitative layer; **note that numeric win_prob/confidence never lived
here** — important for honest schema design.

**File:** `frontend/src/growth/strongCallProjection.ts`
**Reason:** the canonical merge that every surface renders.
**Key finding:** `buildStrongCall()` tries `ProductNarrative` first (→ `splitScoreband(scoreline_view)`,
`harmonizedRisk`), else `buildStrongCallFromArtifact()` (artifact `score_call`/`risk_level`/etc.).
`StrongCall` has NO win_prob/confidence — it is score/lean/risk-label only. Confirms the live product
already deliberately omits probability.
**Reuse / discard:** REUSE — the projection is the right place to read a future `model_fields` block.

**File:** `frontend/src/pages/PredictPage.tsx`
**Reason:** how `/predict/:id` resolves and renders.
**Key finding:** resolution order = `getProductNarrative(id)` → `getUpcomingFixture(id)` → else
`getPredictionArtifact(slug)` → `ArtifactTacticalRoom` → else generic `FALLBACK` shell. A manual hotspot
(id=null, no narrative) lands on `ArtifactTacticalRoom`, which renders the **operator** artifact only.
There is **no data-backed model block** anywhere on this path.
**Reuse / discard:** REUSE — this is where P8 P0 adds a data-backed content block.

---

### Scripts — producers and guards

**File:** `scripts/mvp2_match_sync.py`
**Key finding:** P1.3 daily slate. `KNOWN` map = the only place a real internal id/kickoff/flags exists
(3 fixtures). Writes `daily_fixtures_<date>.json`, `recap_queue_<date>.json`,
`dailyFixtures.generated.json`. **It does NOT compute or attach win_prob/score/risk/confidence** — it is
identity + lifecycle + manual score only. This is the script that established the model-field-free manifest.
**Reuse / discard:** REUSE the slate backbone; **the model-field attach step is the missing generator**.

**File:** `scripts/mvp2_build_scoutscore_v0_2_factors.py` + `mvp2_generate_product_proof_narratives.py` +
`mvp2_generate_trial_prediction_narratives.py` + `mvp2_project_external_signals.py` (grep + headers)
**Key finding:** the **historical ScoutScore frame generator** (kaggle Elo/form/H2H + Poisson bands →
factor frame → DeepSeek/Gemini → guard-passed narrative JSON). This is the model+LLM pipeline that
produced the rich fields for the 5 fixed fixtures. **Still present, still runnable locally** (per memory:
DeepSeek/Gemini keys local) — it was never wired to the daily slate.
**Reuse / discard:** **REUSE — this is the generator to adapt** for option C (daily prediction-data
generator), keyed off the daily fixture instead of a hardcoded id.

**File:** `scripts/check_prediction_artifact.py` · `check_daily_readiness.py` · `check_homepage_product_loop.py`
**Key finding (grep):** validators assert artifact shape, lifecycle, and readiness, and reference
`win_prob`/`confidence`/`field_sources`. They check **structure/provenance**, not values — already aligned
with "require source_facts/model_fields status, not fake values." `check_homepage_product_loop.py` has the
known blind spot (asserts a hook exists but not a score-call) noted in P6.
**Reuse / discard:** REUSE — extend to assert `source_facts` + `model_fields.source` presence (P8 P0).

---

### Prior discovery packs (reused, not re-derived)

**File:** `docs/mvp2_product/p7_content_update_mechanism_recovery/DATA_CONTENT_FIELD_MAP.md`
**Key finding:** already maps every field's historical source vs current source vs daily-manual reality.
P8 reuses it wholesale and adds the **route-resolution / bypass** framing + the target schema.
**File:** `docs/mvp2_product/p6_discovery_recovery/STATUS.md` (+ READ_LOG, OWNER_DECISIONS)
**Key finding:** established "NOT lost, under-surfaced", the homepage guard blind spot, the
`NEXT_HOOK` de-hardcode, "no generator → hand-authoring doesn't scale past ~1 fixture/day", and
`MatchDesk.tsx` = dead code. All consistent with P8.
**Reuse / discard:** REUSE — P8 is the **content-fact** successor to P6 (surfacing) and P7 (update
mechanism): P6/P7 fixed the *shell*; P8 targets the *data layer behind the shell*.
