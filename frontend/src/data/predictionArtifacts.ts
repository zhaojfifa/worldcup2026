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
}
export interface ArtifactAnalysis {
  modeling_focus: string[];
  tactical_matchup: string[];
  risk_variables: string[];
  thirty_minute_checklist: string[];
}
export interface ArtifactOps { share_title: string; share_copy: string; join_cta: string; }
export interface PredictionArtifactLocale {
  pending_label: string;
  prediction: ArtifactPrediction;
  analysis: ArtifactAnalysis;
  operations: ArtifactOps;
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
  i18n: Partial<Record<Locale, PredictionArtifactLocale>>;
}

export interface ObservationArtifactLocale {
  receipt_title: string;
  pre_match_call: string;
  actual_line: string;
  assessment: string;
  calibration_title: string;
  calibration_points: string[];
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
const OBSERVATION: Record<string, ObservationArtifact> = {
  '1489371': observation1489371 as ObservationArtifact,
};

/** Resolve a prediction artifact by route key — matches the manifest fixture_key
 *  (external_game_id) or a numeric id. Used by /predict for the manual daily hotspot. */
export function getPredictionArtifact(key: string): PredictionArtifact | null {
  return PREDICTION.find(a => a.fixture_key === key || (a.id != null && a.id === key)) ?? null;
}

/** Locale slice with en fallback (vi/my/en customer langs; never falls back to zh for vi/my). */
export function predictionArtifactLocale(a: PredictionArtifact, loc: Locale): PredictionArtifactLocale {
  return a.i18n[loc] ?? a.i18n.en ?? (a.i18n.zh as PredictionArtifactLocale);
}

/** Recap/observation artifact by fixture id — used by /recap for a tracked hotspot whose
 *  full recap is not ready (recap_ready=false). Never a fake recap. */
export function getObservationArtifact(id: string): ObservationArtifact | null {
  return OBSERVATION[id] ?? null;
}
export function observationArtifactLocale(a: ObservationArtifact, loc: Locale): ObservationArtifactLocale {
  return a.i18n[loc] ?? a.i18n.en ?? (a.i18n.zh as ObservationArtifactLocale);
}
