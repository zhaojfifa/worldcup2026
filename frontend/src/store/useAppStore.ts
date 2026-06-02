import { create } from 'zustand';
import { MOCK_MATCHES, MOCK_TASKS } from '../data/mock';
import type { Match, LiveCorrection, TokenTask } from '../types';
import { api } from '../api/client';
import { listItemToMatch, mergeDetail, mergeReport } from '../api/transform';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
// Demo user id — replaced by real auth in a future milestone
const DEMO_USER_ID = 1;

interface AppState {
  balance: number;
  checkedIn: boolean;
  tasks: TokenTask[];
  matches: Match[];
  matchesLoading: boolean;
  selectedMatchId: string | null;
  unlockedMatchIds: Set<string>;
  subscribed: boolean;
  syncedAt: string;
  apiError: string | null;

  // Data loading
  loadMatches: () => Promise<void>;
  loadDetail: (matchId: string) => Promise<void>;
  loadReport: (matchId: string) => Promise<void>;

  // Token actions
  checkIn: () => Promise<void>;
  addToken: (n: number) => void;
  spendToken: (cost: number) => boolean;
  unlockWithToken: (matchId: string) => Promise<{ success: boolean; message: string }>;
  unlockWithCash: (matchId: string) => Promise<{ success: boolean; message: string }>;
  completeTask: (taskId: string) => void;

  // Match actions
  setSelectedMatch: (id: string) => void;
  unlockMatch: (id: string) => void;
  applyLiveCorrection: (matchId: string, correction: LiveCorrection) => void;
  simulateCorrection: (matchId: string) => Promise<void>;

  // Community
  subscribe: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  balance: 520,
  checkedIn: false,
  tasks: MOCK_TASKS,
  matches: MOCK_MATCHES,
  matchesLoading: false,
  selectedMatchId: MOCK_MATCHES[0].id,
  unlockedMatchIds: new Set(),
  subscribed: false,
  syncedAt: new Date().toISOString(),
  apiError: null,

  // ─── Data loading ───────────────────────────────────────────────────────

  async loadMatches() {
    if (USE_MOCK) return;
    set({ matchesLoading: true, apiError: null });
    try {
      const items = await api.getMatches();
      const matches = items.map(listItemToMatch);
      set({
        matches,
        selectedMatchId: matches[0]?.id ?? null,
        syncedAt: new Date().toISOString(),
        matchesLoading: false,
      });
    } catch (err) {
      console.warn('[API] getMatches failed — using mock data:', err);
      set({ matchesLoading: false, apiError: String(err) });
      // fallback: keep existing mock data, no white screen
    }
  },

  async loadDetail(matchId) {
    if (USE_MOCK) return;
    try {
      const numId = Number(matchId);
      if (isNaN(numId)) return;
      const detail = await api.getMatch(numId);
      set(s => ({
        matches: s.matches.map(m =>
          m.id === matchId ? mergeDetail(m, detail) : m
        ),
        syncedAt: new Date().toISOString(),
      }));
    } catch (err) {
      console.warn('[API] getMatch failed — using cached data:', err);
    }
  },

  async loadReport(matchId) {
    if (USE_MOCK) return;
    try {
      const numId = Number(matchId);
      if (isNaN(numId)) return;
      const report = await api.getReport(numId);
      set(s => ({
        matches: s.matches.map(m =>
          m.id === matchId ? mergeReport(m, report) : m
        ),
        syncedAt: new Date().toISOString(),
      }));
    } catch (err) {
      console.warn('[API] getReport failed — using cached data:', err);
    }
  },

  // ─── Token actions ───────────────────────────────────────────────────────

  async checkIn() {
    const { checkedIn, tasks } = get();
    if (checkedIn) return;

    if (!USE_MOCK) {
      try {
        const res = await api.checkIn(DEMO_USER_ID);
        if (res.success) {
          set(s => ({
            checkedIn: true,
            balance: res.balance,
            tasks: s.tasks.map(t => t.id === 'checkin' ? { ...t, done: true } : t),
          }));
        }
        return;
      } catch (err) {
        console.warn('[API] checkIn failed — applying locally:', err);
      }
    }
    // mock / fallback path
    const reward = tasks.find(t => t.id === 'checkin')?.reward ?? 10;
    set(s => ({
      checkedIn: true,
      balance: s.balance + reward,
      tasks: s.tasks.map(t => t.id === 'checkin' ? { ...t, done: true } : t),
    }));
  },

  addToken(n) {
    set(s => ({ balance: s.balance + n }));
  },

  spendToken(cost) {
    if (get().balance < cost) return false;
    set(s => ({ balance: s.balance - cost }));
    return true;
  },

  async unlockWithToken(matchId) {
    const { balance } = get();
    const cost = 390;
    if (balance < cost) return { success: false, message: 'MTC 球迷积分不足，请先完成任务积累积分' };

    if (!USE_MOCK) {
      try {
        const res = await api.unlockReport(DEMO_USER_ID, Number(matchId), 'token');
        if (res.success) {
          set(s => ({
            balance: res.balance ?? s.balance - cost,
            unlockedMatchIds: new Set([...s.unlockedMatchIds, matchId]),
          }));
          return { success: true, message: res.message };
        }
        return { success: false, message: res.message };
      } catch (err) {
        console.warn('[API] unlockReport(token) failed — applying locally:', err);
      }
    }
    // mock / fallback
    set(s => ({
      balance: s.balance - cost,
      unlockedMatchIds: new Set([...s.unlockedMatchIds, matchId]),
    }));
    return { success: true, message: `已消耗 ${cost} MTC 积分，完整 AI 报告已解锁` };
  },

  async unlockWithCash(matchId) {
    if (!USE_MOCK) {
      try {
        const res = await api.unlockReport(DEMO_USER_ID, Number(matchId), 'cash');
        if (res.success) {
          set(s => ({ unlockedMatchIds: new Set([...s.unlockedMatchIds, matchId]) }));
          return { success: true, message: res.message };
        }
        return { success: false, message: res.message };
      } catch (err) {
        console.warn('[API] unlockReport(cash) failed — applying locally:', err);
      }
    }
    set(s => ({ unlockedMatchIds: new Set([...s.unlockedMatchIds, matchId]) }));
    return { success: true, message: '支付成功，完整 AI 报告已解锁（演示模式）' };
  },

  completeTask(taskId) {
    const task = get().tasks.find(t => t.id === taskId);
    if (!task || task.done) return;
    set(s => ({
      balance: s.balance + task.reward,
      tasks: s.tasks.map(t => t.id === taskId ? { ...t, done: true } : t),
    }));
  },

  // ─── Match actions ───────────────────────────────────────────────────────

  setSelectedMatch(id) {
    set({ selectedMatchId: id });
  },

  unlockMatch(id) {
    set(s => ({ unlockedMatchIds: new Set([...s.unlockedMatchIds, id]) }));
  },

  applyLiveCorrection(matchId, correction) {
    set(s => ({
      matches: s.matches.map(m =>
        m.id === matchId
          ? { ...m, winProb: correction.after, liveCorrection: correction }
          : m
      ),
      syncedAt: new Date().toISOString(),
    }));
  },

  async simulateCorrection(matchId) {
    if (!USE_MOCK) {
      try {
        const res = await api.simulateCorrection(Number(matchId));
        if (res.success) {
          get().applyLiveCorrection(matchId, {
            trigger: res.trigger,
            before: res.before,
            after: res.after,
            reason: res.reason,
            timestamp: res.timestamp,
          });
          return;
        }
      } catch (err) {
        console.warn('[API] simulateCorrection failed — applying locally:', err);
      }
    }
    // mock / fallback: compute locally
    const match = get().matches.find(m => m.id === matchId);
    if (!match) return;
    const correction: LiveCorrection = {
      trigger: `${match.awayTeam.name}主力中卫未进入首发`,
      before: { ...match.winProb },
      after: {
        home: Math.min(match.winProb.home + 4, 99),
        draw: Math.max(match.winProb.draw - 1, 1),
        away: Math.max(match.winProb.away - 3, 1),
      },
      reason: `${match.awayTeam.name}后场出球稳定性下降，${match.homeTeam.name}右路进攻优势扩大。`,
      timestamp: new Date().toISOString(),
    };
    get().applyLiveCorrection(matchId, correction);
  },

  // ─── Community ───────────────────────────────────────────────────────────

  async subscribe() {
    if (get().subscribed) return;
    if (!USE_MOCK) {
      try {
        await api.subscribe(DEMO_USER_ID);
      } catch (err) {
        console.warn('[API] subscribe failed — applying locally:', err);
      }
    }
    set({ subscribed: true });
  },
}));
