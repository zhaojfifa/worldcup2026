// REAL upcoming World Cup 2026 fixtures (engineering facts from API-FOOTBALL /fixtures,
// ingested 2026-06-11 via backend/scripts/mvp2_ingest_scout_pack.py — see
// docs/data_audit/mvp2_scout_pack_samples/{id}.json source_ledger). Bundled statically:
// the frontend never calls the vendor. Narrative for each id lives in productNarrativeData.
export interface UpcomingFixture {
  id: string;
  kickoffUtc: string;
  home: string;
  away: string;
  flagHome: string;
  flagAway: string;
  venue: string;
  city: string;
  round: string;
}

export const UPCOMING_FIXTURES: UpcomingFixture[] = [
  {
    id: '1489369', kickoffUtc: '2026-06-11T19:00:00+00:00',
    home: 'Mexico', away: 'South Africa', flagHome: '🇲🇽', flagAway: '🇿🇦',
    venue: 'Estadio Azteca', city: 'Mexico City', round: 'Group Stage · 1',
  },
  {
    id: '1489371', kickoffUtc: '2026-06-13T22:00:00+00:00',
    home: 'Brazil', away: 'Morocco', flagHome: '🇧🇷', flagAway: '🇲🇦',
    venue: 'MetLife Stadium', city: 'New York / New Jersey', round: 'Group Stage · 1',
  },
];

export function getUpcomingFixture(id: string): UpcomingFixture | null {
  return UPCOMING_FIXTURES.find(f => f.id === id) ?? null;
}
