// MVP2-P4 Prediction Artifact loader (Owner: restore the prediction artifact chain).
// A manual daily hotspot (id=null) has no bundled ProductNarrative, so /predict could only
// show a generic shell. A Prediction Artifact is the recovery layer: fixture identity + a
// pre-match WATCH read (modeling/tactical/risk frames + 30-minute checklist + operator share/
// join copy). Numeric direction/score/confidence may be null (pending lineups) — rendered as
// 方向待临场确认, never invented. Bundled at build time; the frontend never calls the LLM/vendor.
import type { Locale } from '../i18n/useLocale';
import netherJapan from './predictionArtifacts/manual_Nether-Japan-20260614.json';
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
export interface PredictionArtifactLocale {
  pending_direction: string;   // 方向待临场确认
  pending_score: string;       // 比分待开球前 30 分钟确认
  prediction: ArtifactPrediction;
  analysis: ArtifactAnalysis;
  operations: ArtifactOps;
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

const PREDICTION: PredictionArtifact[] = [netherJapan as PredictionArtifact];
const OBSERVATION: ObservationArtifact[] = [observation1489371 as ObservationArtifact];

/** Resolve a prediction artifact by route key — matches the manifest fixture_key
 *  (external_game_id) or a numeric id. Used by /predict for the manual daily hotspot. */
export function getPredictionArtifact(key: string): PredictionArtifact | null {
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
  return OBSERVATION.find(o => o.fixture_key === key || (o.id != null && o.id === key)) ?? null;
}
/** Does a finished fixture (by key or id) have an observation/recap artifact? (readiness page) */
export function hasObservationArtifact(key: string | null | undefined): boolean {
  return !!key && getObservationArtifact(key) != null;
}
export function observationArtifactLocale(a: ObservationArtifact, loc: Locale): ObservationArtifactLocale {
  return a.i18n[loc] ?? a.i18n.en ?? (a.i18n.zh as ObservationArtifactLocale);
}
