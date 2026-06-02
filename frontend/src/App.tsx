import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { DetailPage } from './pages/DetailPage';
import { ReportPage } from './pages/ReportPage';
import { TokenPage } from './pages/TokenPage';
import { CommunityPage } from './pages/CommunityPage';
import './styles/global.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="detail" element={<DetailPage />} />
          <Route path="report" element={<ReportPage />} />
          <Route path="token" element={<TokenPage />} />
          <Route path="community" element={<CommunityPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
