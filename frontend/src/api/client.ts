/**
 * Thin API client — all calls go through here.
 * Never passes API keys; the backend handles all sensitive credentials.
 */

import type { RecapContent } from '../data/recapData';

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
  getRecap:        (fixtureId: string, lang: string) => request<RecapContent>(`/api/v1/recap/${fixtureId}?lang=${lang}`),

  getWallet:       (userId: number)                      => request<{ balance: number; total_earned: number; total_spent: number; last_checkin_date: string | null }>(`/api/v1/tokens/wallet/${userId}`),
  checkIn:         (userId: number)                      => request<{ success: boolean; earned: number; balance: number; message: string }>('/api/v1/tokens/checkin', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
  unlockReport:    (userId: number, matchId: number, method: string) => request<{ success: boolean; method: string; balance: number | null; message: string }>('/api/v1/tokens/unlock-report', { method: 'POST', body: JSON.stringify({ user_id: userId, match_id: matchId, method }) }),

  simulateCorrection: (matchId: number)                  => request<{ success: boolean; trigger: string; before: ApiWinProb; after: ApiWinProb; reason: string; timestamp: string }>(`/api/v1/corrections/${matchId}/simulate`, { method: 'POST', body: JSON.stringify({}) }),
  joinChallenge:   (challengeId: number, userId: number, option: string) => request<{ success: boolean; chosen_option: string; message: string }>(`/api/v1/challenges/${challengeId}/join`, { method: 'POST', body: JSON.stringify({ user_id: userId, chosen_option: option }) }),
  subscribe:       (userId: number)                      => request<{ success: boolean; plan: string; message: string }>('/api/v1/community/subscribe', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),

  // ── Day 6B: assets / R2 status ───────────────────────────────────────────
  getAssetsStatus:   () => request<ApiAssetsStatus>('/api/v1/assets/status'),

  // ── Day 6C: social channels + community heat ──────────────────────────────
  getSocialChannels: () => request<ApiSocialChannel[]>('/api/v1/social/channels'),
  getCommunityHeat:  () => request<ApiCommunityHeat>('/api/v1/community/heat'),
  getUserStreak:     (userId: number) => request<ApiStreak>(`/api/v1/users/${userId}/streak`),
  getRankings:       () => request<ApiRankings>('/api/v1/rankings'),
  trackEvent:        (eventType: string, matchId?: number, channelName?: string) =>
    request<{ ok: boolean; event_type: string; message: string }>('/api/v1/events/track', {
      method: 'POST',
      body: JSON.stringify({ event_type: eventType, match_id: matchId ?? null, channel_name: channelName ?? null }),
    }),
};

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

/** Fire-and-forget anonymous event tracking. No-op in mock mode; never throws. */
export function safeTrack(eventType: string, matchId?: number, channelName?: string): void {
  if (USE_MOCK) return;
  api.trackEvent(eventType, matchId, channelName).catch(() => { /* tracking must never break UI */ });
}

export interface ApiAssetsStatus {
  r2_configured: boolean;
  bucket: string | null;
  public_base_url_set: boolean;
  message: string;
}
export interface ApiSocialChannel {
  channel_name: string;
  display_name: string;
  status: string;            // coming_soon / active / disabled
  public_url: string | null;
  description: string | null;
  locale: string;
  is_enabled: boolean;
  sort_order: number;
}
export interface ApiCommunityHeat {
  top_matches: Array<{ match_id: number; home: string; away: string; interactions: number }>;
  total_interactions: number;
  hot_channels: string[];
  updated_at: string | null;
  message: string;
}
export interface ApiStreak {
  user_id: number;
  current_streak: number;
  best_streak: number;
  mtc_earned: number;
  last_participation_date: string | null;
  disclaimer: string;
}
export interface ApiRankings {
  top_users: Array<{ rank: number; display_name: string; current_streak: number; best_streak: number; mtc_earned: number }>;
  ranking_type: string;
  updated_at: string | null;
  disclaimer: string;
}
