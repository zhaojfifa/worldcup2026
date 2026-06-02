import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { ToastProvider } from './Toast';

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
        <span className="topbar-crown">👑</span>
        <div>
          <div className="topbar-t1">世界杯 AI 情报终端</div>
          <div className="topbar-t2">不只告诉你谁会赢，更告诉你为什么</div>
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
