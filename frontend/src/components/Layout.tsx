import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { ToastProvider } from './Toast';
import { BRAND } from '../copy/zh';

const NAV_ITEMS = [
  { path: '/',          ic: '🏠', lb: '首页'  },
  { path: '/detail',    ic: '📈', lb: 'AI预测' },
  { path: '/token',     ic: '🪙', lb: 'MTC积分' },
  { path: '/community', ic: '👥', lb: '社群'  },
];

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  const activeNav = (path: string) => {
    if (path === '/') return location.pathname === '/' || location.pathname === '/report';
    return location.pathname.startsWith(path);
  };

  return (
    <div className="phone">
      <div className="topbar">
        <span className="topbar-crown">🔮</span>
        <div>
          <div className="topbar-t1">{BRAND.name} · {BRAND.zhRole}</div>
          <div className="topbar-t2">{BRAND.headerSub}</div>
        </div>
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
