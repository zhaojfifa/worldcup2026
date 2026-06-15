// P7 P0-1 — the persisted daily editorial selection becomes the AUTHORITY for the homepage lead
// (Owner: the product must not depend on chat memory or slate order). Bundled at build time (artifacts
// stay frontend-bundled for MVP; backend runtime store is P1). The mirror of record lives at
// docs/data_audit/mvp2_predictions/selected_hotspot_<date>.json; this is the build-time copy.
import selected from './selectedHotspot.json';

export interface SelectedHotspot {
  date: string;
  fixture_key: string;
  home: string;
  away: string;
  source: string;          // operator_confirmed | operator_estimated
  prediction_artifact_path: string;
  operator_confirmed: boolean;
  status: string;          // active | retired
}

/** The current selected hotspot, or null if none is bundled (→ /internal/daily flags it missing). */
export function getSelectedHotspot(): SelectedHotspot | null {
  const s = selected as SelectedHotspot;
  return s && s.fixture_key && s.status === 'active' ? s : null;
}
