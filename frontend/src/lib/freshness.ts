// P1.2b — RUNTIME FRESHNESS GUARD (frontend defensive layer, Owner verdict 2026-06-13).
//
// Trust-critical: no customer surface may present a live/finished/stale fixture as an
// active pre-match prediction. Stored status is NOT trusted — a fixture whose kickoff
// has passed is treated as live/finished even if the API/bundle still says "scheduled".
//
// This is the browser mirror of scripts/mvp2_fixture_lifecycle.py (same states, same
// thresholds). Pure + self-contained: pass `now` for testability; recapReady comes from
// whether the bundled narrative has flipped to real_recap (a recap exists).

export type Lifecycle =
  | 'SCHEDULED' | 'T_MINUS_2H' | 'T_MINUS_30'
  | 'LIVE' | 'FINISHED' | 'RECAP_PENDING' | 'RECAP_READY' | 'ARCHIVED';

export interface Freshness {
  state: Lifecycle;
  preMatchAllowed: boolean;   // may a surface show 今晚主看 / 赛前判断 / 主比分 as CURRENT?
  recapAllowed: boolean;      // may a surface show / link the recap?
  recapPending: boolean;      // finished but no recap bundled yet -> 复盘生成中
  reason: string;
}

const WATCH_MIN = 120;        // T-2h
const RESCORE_MIN = 30;       // T-30
const FT_ESTIMATE_MIN = 130;  // kickoff + ~130min ≈ final whistle
const RECAP_GRACE_MIN = 45;   // A4 recap due from FT+45
const ARCHIVE_AFTER_MIN = 72 * 60;

// API status shorts (optional — usually absent on the frontend; bundle has no live status)
const FINISHED_SHORT = new Set(['FT', 'AET', 'PEN']);
const LIVE_SHORT = new Set(['1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']);
const HALTED_SHORT = new Set(['PST', 'CANC', 'ABD', 'AWD', 'WO']);

export interface FreshnessInput {
  kickoffUtc: string | null;
  now?: Date;
  recapReady?: boolean;   // bundled narrative is real_recap
  apiStatusShort?: string | null;
}

export function computeFreshness({ kickoffUtc, now, recapReady = false, apiStatusShort = null }: FreshnessInput): Freshness {
  const n = now ?? new Date();
  const mins = kickoffUtc == null ? null : (new Date(kickoffUtc).getTime() - n.getTime()) / 60000;

  // Trust only EXPLICIT live/halted signals; a stale "NS"/"scheduled" must not block
  // time inference (that stale status is exactly the bug P1.2b exists to defeat).
  const trustedLive = apiStatusShort != null && LIVE_SHORT.has(apiStatusShort);
  const halted = apiStatusShort != null && HALTED_SHORT.has(apiStatusShort);
  const finished = recapReady
    || (apiStatusShort != null && FINISHED_SHORT.has(apiStatusShort))
    || (!trustedLive && !halted && mins != null && mins <= -FT_ESTIMATE_MIN);

  const mk = (state: Lifecycle, reason: string): Freshness => ({
    state,
    preMatchAllowed: (state === 'SCHEDULED' || state === 'T_MINUS_2H' || state === 'T_MINUS_30')
      && !(apiStatusShort != null && HALTED_SHORT.has(apiStatusShort)),
    recapAllowed: state === 'RECAP_READY',
    recapPending: state === 'FINISHED' || state === 'RECAP_PENDING',
    reason,
  });

  if (finished) {
    if (recapReady) {
      if (mins != null && mins <= -ARCHIVE_AFTER_MIN) return mk('ARCHIVED', 'recap ready, kickoff >72h ago');
      return mk('RECAP_READY', 'recap available');
    }
    if (mins != null && mins > -(FT_ESTIMATE_MIN + RECAP_GRACE_MIN)) return mk('FINISHED', 'final-whistle window, recap not due yet');
    return mk('RECAP_PENDING', 'finished, recap generating');
  }
  if (halted) return mk('SCHEDULED', `halted/postponed (${apiStatusShort})`);
  if (trustedLive) return mk('LIVE', `live (${apiStatusShort})`);
  if (mins != null && mins <= 0) return mk('LIVE', 'kickoff passed without a finished signal — frozen');
  if (mins == null) return mk('SCHEDULED', 'no kickoff time on record');
  if (mins <= RESCORE_MIN) return mk('T_MINUS_30', `T-${Math.round(mins)}min`);
  if (mins <= WATCH_MIN) return mk('T_MINUS_2H', `T-${Math.round(mins)}min`);
  return mk('SCHEDULED', `T-${Math.round(mins)}min`);
}

// Convenience for the common case: a bundled fixture + its narrative recap mode.
export function fixtureFreshness(kickoffUtc: string | null, narrativeMode?: string, now?: Date): Freshness {
  return computeFreshness({ kickoffUtc, now, recapReady: narrativeMode === 'real_recap' });
}

// ── Homepage active-fixture selection (Owner §3) — no hardcoded permanent hero ──
export interface FixtureEntry { id: string; kickoffUtc: string | null; recapReady: boolean }
export type HeroMode = 'pre_match' | 'recap_ready' | 'recap_pending' | 'empty';
export interface ActiveSelection { heroId: string | null; heroState: Lifecycle | null; mode: HeroMode }

function ts(s: string | null): number { return s ? new Date(s).getTime() : 0; }

export function pickActiveFixture(entries: FixtureEntry[], now?: Date): ActiveSelection {
  const f = entries.map(e => ({ e, fr: computeFreshness({ kickoffUtc: e.kickoffUtc, now, recapReady: e.recapReady }) }));
  // 1. earliest FUTURE fixture that is genuinely pre-match
  const pre = f.filter(x => x.fr.preMatchAllowed).sort((a, b) => ts(a.e.kickoffUtc) - ts(b.e.kickoffUtc));
  if (pre.length) return { heroId: pre[0].e.id, heroState: pre[0].fr.state, mode: 'pre_match' };
  // 2. latest RECAP_READY (recap exists)
  const ready = f.filter(x => x.fr.recapAllowed).sort((a, b) => ts(b.e.kickoffUtc) - ts(a.e.kickoffUtc));
  if (ready.length) return { heroId: ready[0].e.id, heroState: ready[0].fr.state, mode: 'recap_ready' };
  // 3. latest finished-but-recap-pending
  const pend = f.filter(x => x.fr.recapPending).sort((a, b) => ts(b.e.kickoffUtc) - ts(a.e.kickoffUtc));
  if (pend.length) return { heroId: pend[0].e.id, heroState: pend[0].fr.state, mode: 'recap_pending' };
  // 4. nothing usable
  return { heroId: null, heroState: null, mode: 'empty' };
}
