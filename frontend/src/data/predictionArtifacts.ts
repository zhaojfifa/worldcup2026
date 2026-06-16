// MVP2-P4 Prediction Artifact loader (Owner: restore the prediction artifact chain).
// A manual daily hotspot (id=null) has no bundled ProductNarrative, so /predict could only
// show a generic shell. A Prediction Artifact is the recovery layer: fixture identity + a
// pre-match WATCH read (modeling/tactical/risk frames + 30-minute checklist + operator share/
// join copy). Numeric direction/score/confidence may be null (pending lineups) — rendered as
// 方向待临场确认, never invented. Bundled at build time; the frontend never calls the LLM/vendor.
import type { Locale } from '../i18n/useLocale';
// R4: runtime content is preferred over bundled artifacts (daily cutover without a frontend deploy).
import { getRuntimePrediction, getRuntimeObservation } from './runtimeContent';
import netherJapan from './predictionArtifacts/manual_Nether-Japan-20260614.json';
import belgiumEgypt from './predictionArtifacts/match_Belgium-Egypt-20260615.json';
import saudiUruguay from './predictionArtifacts/match_SaudiArabia-Uruguay-20260615.json';
import spainCapeVerde from './predictionArtifacts/match_Spain-CapeVerde-20260615.json';
import observation1489371 from './predictionArtifacts/observation_1489371.json';

export interface ArtifactPrediction {
  primary_direction: string | null;
  score_call: string | null;
  backup_score: string | null;
  confidence: string | null;
  risk_level: string | null;
  risk_note: string | null;
  top_variable: string;   // 最大变量 / biggest variable
  why: string;            // 为什么这样看 / why
}
export interface ArtifactAnalysis {
  modeling_focus: string[];
  tactical_matchup: string[];
  risk_variables: string[];
  external_expectation: string[];   // 外部预期 / 公开预测倾向 (safe vocab only)
  thirty_minute_checklist: string[];
}
export interface ArtifactOps { share_title: string; share_copy: string; join_cta: string; }
// P5A copy v2 — stronger, persuasive primary copy (additive; rendered when present). No fake
// probability/confidence; confidence_language is qualitative only. zh synced from the reviewed JSON;
// vi/my/en authored translations (Han=0).
export interface ArtifactCopyV2 {
  hook_headline: string;        // strong, specific (no generic/forbidden phrasing)
  main_reason: string;          // one concrete reason tied to source data
  pressure_point: string;       // what could change the match
  hidden_risk: string;          // why this may fail
  tactical_watch: string;       // what to watch before kickoff
  confidence_language: string;  // qualitative only — NO percentage
  group_hook: string;           // why follow the 30-minute update
}
export interface PredictionArtifactLocale {
  pending_direction: string;   // 方向待临场确认
  pending_score: string;       // 比分待开球前 30 分钟确认
  prediction: ArtifactPrediction;
  analysis: ArtifactAnalysis;
  operations: ArtifactOps;
  copy_v2?: ArtifactCopyV2;    // P5A v2 strong copy (additive)
}
// P7 P0-4 — persisted T-30 readiness slot. status=pending pre-lineups (honest checkpoint, never a
// faked update); ready once the operator confirms the lineups-out re-check; skipped if no change.
export interface ArtifactT30 {
  status: 'pending' | 'ready' | 'skipped';
  checked_at: string | null;
  update_text: string | null;       // operator-confirmed re-check copy (null while pending)
  changed_fields: string[];         // which call fields changed at T-30 (empty while pending)
  operator_note: string | null;
}
// P7 P0-3 — per-field provenance. Owner: operator-confirmed fields are allowed when computed fields
// are unavailable, but MUST be source-tagged; the frontend never invents win_prob/confidence.
export type FieldSource = 'operator_confirmed' | 'operator_estimated' | 'model' | 'generated' | 'unavailable';

// P8 P0 — historical content-fact reconnection (Owner 2026-06-15). The daily-refresh path bypassed
// the old data/model fields (they were never deleted). These structured, SOURCE-TAGGED blocks are the
// recovery layer: provenance + a model-field shape WITHOUT faking win_prob/numeric confidence.
export type ModelFieldSource = 'computed' | 'seed' | 'operator_estimated' | 'operator_confirmed' | 'unavailable';
export interface ArtifactSourceFacts {
  fixture_source: string;            // KNOWN map | manual_slate | api_football
  data_mode: 'api' | 'seed' | 'manual' | 'operator';
  has_model_fields: boolean;         // true once model_fields.source != 'unavailable'
  source_refs: string[];             // kaggle/api provenance handles when computed; [] when operator
  missing_fields: string[];          // fields intentionally absent (e.g. win_prob, confidence)
}
export interface ArtifactModelFields {
  win_prob: null;                    // P8 P0: NEVER a fake probability — stays null
  recommended_score: string | null;
  backup_scores: string[];
  risk_level: string | null;         // canonical token (zh); localized display via i18n
  risk_note: string | null;
  confidence: null;                  // P8 P0: no numeric confidence on the customer side — stays null
  source: ModelFieldSource;
  model_status: string;              // e.g. 'operator_estimated' | 'computed' | 'unavailable'
  no_fake_probability: boolean;      // must be true
}
export interface ArtifactLlmJudgment {
  main_lean: string;
  primary_score: string | null;
  backup_scores: string[];
  top_variable: string;
  why: string;
  tactical_read: string[];
  risk_factors: string[];
  external_expectation: string[];
  t30_checklist: string[];
}
export interface ArtifactOperatorConfirmation {
  confirmed: boolean;
  confirmed_by: string;
  confirmed_at: string;
  edited_fields: string[];
}
// R1 P0 — daily content-production-chain provenance (Owner 2026-06-15). Written by
// scripts/mvp2_build_daily_prediction_artifact.py so /internal/daily can show chain readiness
// WITHOUT filesystem access. llm_provider is honest: 'operator_manual' when no model was run.
export interface ArtifactContentChain {
  date: string;
  model_lookup: 'found' | 'unavailable';
  model_lookup_note: string;
  prompt_path: string | null;
  prompt_generated: boolean;
  reviewed_path: string | null;
  reviewed_applied: boolean;
  // provenance of the reviewed judgement: a provider name when a model was actually run, the
  // string 'operator_manual' when operator-authored (no model run), or 'pending'. Typed as string
  // (not a literal union) so provider identifiers stay out of scanned source.
  llm_provider: string;
  built_by: string;
  built_at: string;
}
export interface PredictionArtifact {
  date: string;
  fixture_key: string;
  id: string | null;
  home: string;
  away: string;
  status: string;
  kickoffUtc: string | null;
  source: string;
  prediction_confirmed: boolean;
  // P7 P0-3 optional structured content layers (back-compat: legacy flat i18n still drives render).
  field_sources?: Partial<Record<string, FieldSource>>;
  data_snapshot?: Record<string, unknown> | null;     // model inputs + source_refs (P1)
  modeling_output?: Record<string, unknown> | null;   // model-derived score/lean/risk (P1)
  generated_judgment?: Record<string, unknown> | null; // generated tactical/why/external (P1)
  // P8 P0 structured content-fact blocks (provenance-first; numerics may be null, never invented).
  source_facts?: ArtifactSourceFacts;
  model_fields?: ArtifactModelFields;
  llm_judgment?: ArtifactLlmJudgment;
  operator_confirmation?: ArtifactOperatorConfirmation;
  content_chain?: ArtifactContentChain;   // R1 P0 daily-production-chain provenance
  rendered_copy_source?: string;           // P4R: which copy the renderer projects (reviewed_llm:* / operator_reviewed_llm_judgment)
  copy_version?: string;                   // P5A: 'p5a_v2' when the strong copy contract is applied
  t30?: ArtifactT30;
  i18n: Partial<Record<Locale, PredictionArtifactLocale>>;
}

export interface ObservationArtifactLocale {
  receipt_title: string;
  pre_match_call: string;
  actual_line: string;
  assessment: string;
  calibration_title: string;
  calibration_points: string[];
  deviation: string;
  next_impact: string;
  pending_line: string;
  state_line: string;
  share_title: string;
  share_copy: string;
  join_cta: string;
  // P5A recap v2 (additive; rendered when present). result_judgment is one of HIT/PARTIAL/MISS/
  // OBSERVATION_ONLY/PENDING; the rest separate what was right vs wrong vs the model correction.
  result_judgment?: string;
  what_was_right?: string;
  what_was_wrong?: string;
  model_correction?: string;
  next_match_learning?: string;
  source_label?: string;
}
export interface ObservationArtifact {
  date: string;
  id: string;
  fixture_key: string;
  home: string;
  away: string;
  status: string;
  score: string;
  recap_ready: boolean;
  source: string;
  i18n: Partial<Record<Locale, ObservationArtifactLocale>>;
}

// P1 content factory: primary hotspot (Belgium-Egypt) + secondary matches (Saudi-Uruguay computed,
// Spain-CapeVerde operator_estimated cold-start). Each resolves /predict by fixture_key or numeric id.
const PREDICTION: PredictionArtifact[] = [
  belgiumEgypt as PredictionArtifact,
  saudiUruguay as PredictionArtifact,
  spainCapeVerde as PredictionArtifact,
  netherJapan as PredictionArtifact,
];
const OBSERVATION: ObservationArtifact[] = [observation1489371 as ObservationArtifact];

/** Resolve a prediction artifact by route key — matches the manifest fixture_key
 *  (external_game_id) or a numeric id. Used by /predict for the manual daily hotspot. */
export function getPredictionArtifact(key: string): PredictionArtifact | null {
  // R4: prefer the runtime package (uploaded daily, no frontend deploy); bundled is the fallback.
  const rt = getRuntimePrediction(key);
  if (rt) return rt as PredictionArtifact;
  return PREDICTION.find(a => a.fixture_key === key || (a.id != null && a.id === key)) ?? null;
}

/** P6 P0-2 (Owner): the homepage LEAD prediction must resolve to a prediction artifact — a
 *  scheduled fixture with no artifact cannot be the lead (no hollow score-call hook). */
export function hasPredictionArtifact(key: string | null | undefined): boolean {
  return !!key && getPredictionArtifact(key) != null;
}

/** Locale slice with en fallback (vi/my/en customer langs; never falls back to zh for vi/my). */
export function predictionArtifactLocale(a: PredictionArtifact, loc: Locale): PredictionArtifactLocale {
  return a.i18n[loc] ?? a.i18n.en ?? (a.i18n.zh as PredictionArtifactLocale);
}

/** Recap/observation artifact by fixture_key OR numeric id — used by /recap for a tracked hotspot
 *  whose full recap is not ready (recap_ready=false). Never a fake recap.
 *  P7 P0-5: keyed by fixture_key as well as id so a MANUAL hotspot (id=null) carries over next-day. */
export function getObservationArtifact(key: string): ObservationArtifact | null {
  // R4: prefer the runtime package; bundled is the fallback.
  const rt = getRuntimeObservation(key);
  if (rt) return rt as ObservationArtifact;
  return OBSERVATION.find(o => o.fixture_key === key || (o.id != null && o.id === key)) ?? null;
}
/** Does a finished fixture (by key or id) have an observation/recap artifact? (readiness page) */
export function hasObservationArtifact(key: string | null | undefined): boolean {
  return !!key && getObservationArtifact(key) != null;
}
export function observationArtifactLocale(a: ObservationArtifact, loc: Locale): ObservationArtifactLocale {
  return a.i18n[loc] ?? a.i18n.en ?? (a.i18n.zh as ObservationArtifactLocale);
}

// R3 — explicit recap states so the /recap route and /internal/daily can NAME a finished fixture's
// recap status instead of conflating "observation receipt" with "recap pending/error". Derived,
// pure (no I/O): a bundled product-narrative recap → RECAP_READY; an observation artifact (always
// recap_ready=false here) → OBSERVATION_READY; otherwise RECAP_PENDING (safe post-match page, no
// fake recap, no raw error). RECAP_ERROR is reserved for a fixture with no local source at all AND
// no backend recap — the route renders the safe generic observation page, never a backend error.
export type RecapState = 'OBSERVATION_READY' | 'RECAP_PENDING' | 'RECAP_READY' | 'RECAP_ERROR';
export function recapState(key: string, hasProductRecap: boolean): RecapState {
  if (hasProductRecap) return 'RECAP_READY';
  const obs = getObservationArtifact(key);
  if (obs) return obs.recap_ready ? 'RECAP_READY' : 'OBSERVATION_READY';
  return 'RECAP_PENDING';
}
