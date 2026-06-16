import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { bootstrapRuntime } from './data/dailyFixtures';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { TrialDetailGate } from './pages/TrialDetailGate';
import { ReportPage } from './pages/ReportPage';
import { TokenPage } from './pages/TokenPage';
import { CommunityPage } from './pages/CommunityPage';
import { RecapDetailPage } from './pages/RecapDetailPage';
import { EvidenceBoardPage } from './pages/EvidenceBoardPage';
import { PredictPage } from './pages/PredictPage';
import { JoinPage } from './pages/JoinPage';
import { GrowthAdminPage } from './pages/GrowthAdminPage';
import { DailyStatusPage } from './pages/DailyStatusPage';
import { ShareCardPage } from './pages/ShareCardPage';
import { captureRef } from './growth/refCapture';
import './styles/global.css';

export default function App() {
  // Growth P1: first-touch ?ref= capture on any route (no PII; mock mode = no network)
  useEffect(() => { captureRef(document.documentElement.getAttribute('data-lang') ?? 'zh'); }, []);
  // R4: populate the runtime CONTENT cache (idempotent) BEFORE rendering routes, so synchronous
  // content accessors (getPredictionArtifact/getObservationArtifact) on ANY route — including a deep
  // link to /predict or /recap — see the runtime package. Bundled content is the fallback; a 3s
  // timeout (or any failure) proceeds with bundled so the app never hangs on the backend.
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let alive = true;
    const done = () => { if (alive) setReady(true); };
    bootstrapRuntime().then(done).catch(done);
    const t = setTimeout(done, 3000);
    return () => { alive = false; clearTimeout(t); };
  }, []);
  if (!ready) {
    return <div className="page-enter" style={{ padding: 24, textAlign: 'center', color: 'var(--blueMid)' }}>·</div>;
  }
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="join" element={<JoinPage />} />
          <Route path="internal/growth" element={<GrowthAdminPage />} />
          <Route path="internal/daily" element={<DailyStatusPage />} />
          <Route path="share/fixture/:fixtureId" element={<ShareCardPage kind="fixture" />} />
          <Route path="share/recap/:fixtureId" element={<ShareCardPage kind="recap" />} />
          <Route path="detail" element={<TrialDetailGate />} />
          <Route path="report" element={<ReportPage />} />
          <Route path="token" element={<TokenPage />} />
          <Route path="community" element={<CommunityPage />} />
          <Route path="recap/:fixtureId" element={<RecapDetailPage />} />
          <Route path="evidence/:fixtureId" element={<EvidenceBoardPage />} />
          <Route path="predict/:slug" element={<PredictPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
