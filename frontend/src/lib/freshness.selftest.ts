// P1.2b freshness selftest — runnable WITHOUT a test framework via Node's native TS
// type-stripping:  node frontend/src/lib/freshness.selftest.ts
// Covers the Owner §6 cases A/B/C/D plus the lifecycle gate matrix.
import { computeFreshness, fixtureFreshness } from './freshness.ts';

const KO_FUTURE = '2026-06-13T22:00:00+00:00';   // 1489371
const KO_PAST_1 = '2026-06-05T19:00:00+00:00';   // BRA-ARG (stale "scheduled")
const KO_PAST_2 = '2026-06-06T19:00:00+00:00';   // MAR-FRA
const KO_PAST_3 = '2026-06-07T19:00:00+00:00';   // ESP-GER
const KO_1489369 = '2026-06-11T19:00:00+00:00';  // finished, recap ready

// fixed "now" so the test is deterministic
const NOW = new Date('2026-06-13T02:30:00+00:00');

interface Case { name: string; got: ReturnType<typeof computeFreshness>; wantState: string; wantPre: boolean; wantRecap?: boolean }
const cases: Case[] = [
  // A. Future fixture before kickoff -> pre-match allowed
  { name: 'A 1489371 future', got: fixtureFreshness(KO_FUTURE, 'pre_match_2026_modeling', NOW), wantState: 'SCHEDULED', wantPre: true },
  // B. Past fixtures from stale API (status would say scheduled) -> pre-match REFUSED
  { name: 'B BRA-ARG past',  got: computeFreshness({ kickoffUtc: KO_PAST_1, now: NOW, apiStatusShort: 'NS' }), wantState: 'RECAP_PENDING', wantPre: false },
  { name: 'B MAR-FRA past',  got: computeFreshness({ kickoffUtc: KO_PAST_2, now: NOW, apiStatusShort: 'NS' }), wantState: 'RECAP_PENDING', wantPre: false },
  { name: 'B ESP-GER past',  got: computeFreshness({ kickoffUtc: KO_PAST_3, now: NOW, apiStatusShort: 'NS' }), wantState: 'RECAP_PENDING', wantPre: false },
  // C. Finished recap-ready fixture -> recap allowed, pre-match refused
  { name: 'C 1489369 recap', got: fixtureFreshness(KO_1489369, 'real_recap', NOW), wantState: 'RECAP_READY', wantPre: false, wantRecap: true },
  // D. Synthetic live fixture: kickoff now-20min, status scheduled -> LIVE, pre-match refused
  { name: 'D live now-20m',  got: computeFreshness({ kickoffUtc: new Date(NOW.getTime() - 20 * 60000).toISOString(), now: NOW, apiStatusShort: 'NS' }), wantState: 'LIVE', wantPre: false },
  // extra: LIVE via api status while just kicked off
  { name: 'E api 2H live',   got: computeFreshness({ kickoffUtc: new Date(NOW.getTime() - 50 * 60000).toISOString(), now: NOW, apiStatusShort: '2H' }), wantState: 'LIVE', wantPre: false },
  // extra: halted -> not pre-match
  { name: 'F postponed',     got: computeFreshness({ kickoffUtc: KO_FUTURE, now: NOW, apiStatusShort: 'PST' }), wantState: 'SCHEDULED', wantPre: false },
];

let fail = 0;
for (const c of cases) {
  const okState = c.got.state === c.wantState;
  const okPre = c.got.preMatchAllowed === c.wantPre;
  const okRecap = c.wantRecap === undefined || c.got.recapAllowed === c.wantRecap;
  const ok = okState && okPre && okRecap;
  if (!ok) fail++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${c.name.padEnd(16)} -> ${c.got.state.padEnd(13)} pre=${c.got.preMatchAllowed} recap=${c.got.recapAllowed}  (want ${c.wantState}/pre=${c.wantPre})`);
}
if (fail) { console.log(`FRESHNESS SELFTEST FAIL (${fail})`); process.exit(1); }
console.log(`FRESHNESS SELFTEST PASS (${cases.length} cases)`);
