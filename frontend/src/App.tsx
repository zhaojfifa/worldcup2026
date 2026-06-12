import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
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
import { captureRef } from './growth/refCapture';
import './styles/global.css';

export default function App() {
  // Growth P1: first-touch ?ref= capture on any route (no PII; mock mode = no network)
  useEffect(() => { captureRef(document.documentElement.getAttribute('data-lang') ?? 'zh'); }, []);
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="join" element={<JoinPage />} />
          <Route path="internal/growth" element={<GrowthAdminPage />} />
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
