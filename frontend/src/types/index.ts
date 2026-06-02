export type RiskLevel = 'low' | 'medium' | 'high';

export interface WinProb {
  home: number;   // 0-100
  draw: number;
  away: number;
}

export interface FeatureFactor {
  label: string;
  value: number; // positive = favors home, negative = risk
}

export interface LiveCorrection {
  trigger: string;
  before: WinProb;
  after: WinProb;
  reason: string;
  timestamp: string;
}

export interface Match {
  id: string;
  homeTeam: { name: string; flag: string };
  awayTeam: { name: string; flag: string };
  kickoffTime: string;        // ISO string
  tag?: 'focus' | 'upset' | 'live' | 'high-conf';
  winProb: WinProb;
  recommendedScore: string;   // e.g. "2:1 / 1:1"
  riskLevel: RiskLevel;
  riskNote: string;
  confidence: number;         // 0-100
  features: FeatureFactor[];
  tacticsNote: string;
  freeNote: string;
  trendHistory: { label: string; prob: number }[];
  liveCorrection?: LiveCorrection;
  updatedAt: string;          // ISO string
}

export interface TokenTask {
  id: string;
  icon: string;
  label: string;
  reward: number;
  done: boolean;
}

export interface ShopItem {
  id: string;
  icon: string;
  label: string;
  cost: number;
}
