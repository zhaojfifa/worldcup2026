import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { ToastProvider } from './Toast';
import { useLocale } from '../i18n/useLocale';
import { useCopy } from '../i18n/dict';
import { LanguageSelector } from './LanguageSelector';

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const locale = useLocale();
  const t = useCopy();

  const NAV_ITEMS = [
    { path: '/',          ic: '🏠', lb: t.navHome     },
    { path: '/detail',    ic: '📈', lb: t.navDetail   },
    { path: '/token',     ic: '🪙', lb: t.navToken    },
    { path: '/community', ic: '👥', lb: t.navCommunity },
  ];

  const activeNav = (path: string) => {
    if (path === '/') return location.pathname === '/' || location.pathname === '/report';
    return location.pathname.startsWith(path);
  };

  return (
    <div className={`phone lang-${locale}`} data-lang={locale}>
      <div className="topbar">
        <span className="topbar-crown">🔮</span>
        <div>
          <div className="topbar-t1">{t.brandName} · {t.brandRole}</div>
          <div className="topbar-t2">{t.headerSub}</div>
        </div>
        <LanguageSelector />
      </div>

      <div className="content">
        <Outlet />
      </div>

      <nav className="bottom-nav">
        {NAV_ITEMS.map(item => (
          <button
            key={item.path}
            className={`nav-btn ${activeNav(item.path) ? 'on' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="ic">{item.ic}</span>
            <span className="lb">{item.lb}</span>
          </button>
        ))}
      </nav>

      <ToastProvider />
    </div>
  );
}
