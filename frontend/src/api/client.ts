/**
 * Thin API client — all calls go through here.
 * Never passes API keys; the backend handles all sensitive credentials.
 */

const BASE = (import.meta.env.VITE_API_BASE_URL as string) ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Matches ────────────────────────────────────────────────────────────────

export interface ApiTeam { name: string; flag: string }
export interface ApiWinProb { home: number; draw: number; away: number }
export interface ApiLiveCorrection {
  trigger: string;
  before: ApiWinProb;
  after: ApiWinProb;
  reason: string;
  timestamp: string;
}
export interface ApiMatchListItem {
  id: number;
  external_id: string | null;
  home_team: ApiTeam;
  away_team: ApiTeam;
  kickoff_time: string;
  tag: string | null;
  status: string;
  win_prob: ApiWinProb;
  recommended_score: string | null;
  risk_level: string;
  risk_note: string | null;
  confidence: number;
  updated_at: string;
}
export interface ApiMatchDetail extends ApiMatchListItem {
  free_note: string | null;
  live_correction: ApiLiveCorrection | null;
}
export interface ApiFeatureFactor { label: string; value: number }
export interface ApiTrendPoint    { label: string; prob: number  }
export interface ApiReport {
  match_id: number;
  features: ApiFeatureFactor[];
  trend_history: ApiTrendPoint[];
  tactics_note: string | null;
  verdict_summary: string | null;
  win_prob: ApiWinProb;
  recommended_score: string | null;
  risk_level: string;
  confidence: number;
  live_correction: ApiLiveCorrection | null;
}

export const api = {
  getMatches:      ()             => request<ApiMatchListItem[]>('/api/v1/matches'),
  getMatch:        (id: number)   => request<ApiMatchDetail>(`/api/v1/matches/${id}`),
  getReport:       (id: number)   => request<ApiReport>(`/api/v1/reports/${id}`),

  getWallet:       (userId: number)                      => request<{ balance: number; total_earned: number; total_spent: number; last_checkin_date: string | null }>(`/api/v1/tokens/wallet/${userId}`),
  checkIn:         (userId: number)                      => request<{ success: boolean; earned: number; balance: number; message: string }>('/api/v1/tokens/checkin', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
  unlockReport:    (userId: number, matchId: number, method: string) => request<{ success: boolean; method: string; balance: number | null; message: string }>('/api/v1/tokens/unlock-report', { method: 'POST', body: JSON.stringify({ user_id: userId, match_id: matchId, method }) }),

  simulateCorrection: (matchId: number)                  => request<{ success: boolean; trigger: string; before: ApiWinProb; after: ApiWinProb; reason: string; timestamp: string }>(`/api/v1/corrections/${matchId}/simulate`, { method: 'POST', body: JSON.stringify({}) }),
  joinChallenge:   (challengeId: number, userId: number, option: string) => request<{ success: boolean; chosen_option: string; message: string }>(`/api/v1/challenges/${challengeId}/join`, { method: 'POST', body: JSON.stringify({ user_id: userId, chosen_option: option }) }),
  subscribe:       (userId: number)                      => request<{ success: boolean; plan: string; message: string }>('/api/v1/community/subscribe', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
};
