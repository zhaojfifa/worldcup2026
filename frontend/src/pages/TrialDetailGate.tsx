import { Navigate, useSearchParams } from 'react-router-dom';
import { DetailPage } from './DetailPage';

// June-11 trial gate for /detail (Owner Task C, option A):
// the legacy single-match detail (mock/2022 placeholder data, e.g. Qatar vs Ecuador)
// must NOT appear in the trial flow. /detail therefore redirects to the real
// tactical room (/predict/1489369). The legacy page remains reachable ONLY via the
// internal demo fold, whose rows navigate with ?demo=1.
export function TrialDetailGate() {
  const [search] = useSearchParams();
  if (search.get('demo') === '1') return <DetailPage />;
  return <Navigate to="/predict/1489369" replace />;
}
