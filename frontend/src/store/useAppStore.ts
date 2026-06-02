import { create } from 'zustand';
import { MOCK_MATCHES, MOCK_TASKS } from '../data/mock';
import type { Match, LiveCorrection, TokenTask } from '../types';

interface AppState {
  balance: number;
  checkedIn: boolean;
  tasks: TokenTask[];
  matches: Match[];
  selectedMatchId: string | null;
  unlockedMatchIds: Set<string>;
  subscribed: boolean;
  syncedAt: string;

  checkIn: () => void;
  addToken: (n: number) => void;
  spendToken: (cost: number) => boolean;
  setSelectedMatch: (id: string) => void;
  unlockMatch: (id: string) => void;
  applyLiveCorrection: (matchId: string, correction: LiveCorrection) => void;
  subscribe: () => void;
  completeTask: (taskId: string) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  balance: 520,
  checkedIn: false,
  tasks: MOCK_TASKS,
  matches: MOCK_MATCHES,
  selectedMatchId: MOCK_MATCHES[0].id,
  unlockedMatchIds: new Set(),
  subscribed: false,
  syncedAt: new Date().toISOString(),

  checkIn() {
    if (get().checkedIn) return;
    set(s => ({
      checkedIn: true,
      balance: s.balance + 10,
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

  subscribe() {
    set({ subscribed: true });
  },

  completeTask(taskId) {
    const task = get().tasks.find(t => t.id === taskId);
    if (!task || task.done) return;
    set(s => ({
      balance: s.balance + task.reward,
      tasks: s.tasks.map(t => t.id === taskId ? { ...t, done: true } : t),
    }));
  },
}));
