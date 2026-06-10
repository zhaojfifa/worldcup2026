/**
 * Maps API response shapes (snake_case) to frontend Match types (camelCase).
 * Keeps the store and components blissfully unaware of the wire format.
 */
import type { Match, WinProb, LiveCorrection } from '../types';
import type {
  ApiMatchListItem, ApiMatchDetail, ApiReport,
  ApiWinProb, ApiLiveCorrection,
} from './client';

function toWinProb(p: ApiWinProb): WinProb {
  return { home: p.home, draw: p.draw, away: p.away };
}

function toCorrection(c: ApiLiveCorrection | null): LiveCorrection | undefined {
  if (!c) return undefined;
  return {
    trigger: c.trigger,
    before: toWinProb(c.before),
    after: toWinProb(c.after),
    reason: c.reason,
    timestamp: c.timestamp,
  };
}

/** Convert a list-item (no features/tactics) to a Match with empty rich fields */
export function listItemToMatch(m: ApiMatchListItem): Match {
  return {
    id: String(m.id),
    externalId: m.external_id,
    homeTeam: { name: m.home_team.name, flag: m.home_team.flag },
    awayTeam: { name: m.away_team.name, flag: m.away_team.flag },
    kickoffTime: m.kickoff_time,
    status: m.status,
    tag: (m.tag as Match['tag']) ?? undefined,
    winProb: toWinProb(m.win_prob),
    recommendedScore: m.recommended_score ?? '',
    riskLevel: m.risk_level as Match['riskLevel'],
    riskNote: m.risk_note ?? '',
    confidence: m.confidence,
    // Rich fields not present in list endpoint — filled in by detailToMatch / reportToMatch
    features: [],
    tacticsNote: '',
    freeNote: '',
    trendHistory: [],
    liveCorrection: undefined,
    updatedAt: m.updated_at,
  };
}

/** Merge detail fields (free_note, live_correction) into a Match */
export function mergeDetail(base: Match, d: ApiMatchDetail): Match {
  return {
    ...base,
    winProb: toWinProb(d.win_prob),
    freeNote: d.free_note ?? '',
    liveCorrection: toCorrection(d.live_correction),
    updatedAt: d.updated_at,
  };
}

/** Merge full report fields (features, tactics, trend) into a Match */
export function mergeReport(base: Match, r: ApiReport): Match {
  return {
    ...base,
    winProb: toWinProb(r.win_prob),
    features: r.features,
    tacticsNote: r.tactics_note ?? '',
    trendHistory: r.trend_history,
    liveCorrection: toCorrection(r.live_correction),
  };
}
