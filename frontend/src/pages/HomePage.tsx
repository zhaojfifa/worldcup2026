import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { MatchCard } from '../components/MatchCard';
import { toast } from '../components/Toast';

const DATE_TABS = ['今日', '明日', '本周', '小组赛', '淘汰赛'];

const CAPABILITIES = [
  { ic: '🧠', label: 'AI 赛前模型' },
  { ic: '⏱️', label: '临场 30 分钟修正' },
  { ic: '⚖️', label: '风险评级' },
  { ic: '🪙', label: 'MTC 解锁' },
];

export function HomePage() {
  const navigate = useNavigate();
  const {
    balance, checkedIn, checkIn,
    matches, matchesLoading, loadMatches,
    setSelectedMatch, syncedAt, apiError,
  } = useAppStore();
  const [activeDate, setActiveDate] = useState('今日');

  useEffect(() => { loadMatches(); }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  const focus = matches.find(m => m.tag === 'focus') ?? matches[0];
  const rest  = matches.filter(m => m.id !== focus?.id);

  const liveCount = matches.filter(m => m.tag === 'live').length;
  const modelCount = matches.length;

  function goDetail(id: string) {
    setSelectedMatch(id);
    navigate('/detail');
  }

  async function handleCheckIn() {
    if (checkedIn) { toast('今日已签到'); return; }
    await checkIn();
    toast('签到成功 +10 MTC');
  }

  const syncTime = new Date(syncedAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

  if (matchesLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'var(--sub)' }}>
        <div style={{ fontSize: 30, marginBottom: 12 }}>⚽</div>
        <div className="small">AI 情报加载中…</div>
      </div>
    );
  }

  if (!focus) return null;

  return (
    <div className="page-enter">
      {/* ── AI Intelligence Ticker ───────────────────────────────── */}
      <div className="ai-ticker">
        <span className="live-dot" />
        <span className="tick-label">AI 情报</span>
        <div className="tick-track">
          <span className="tick-move">
            AI 情报更新 · 今日 {modelCount} 场赛前模型已生成 · {liveCount || 1} 场进入临场监听 · 数据同步 {syncTime} · 模型持续追踪阵容与临场变量
          </span>
        </div>
      </div>

      {/* ── Hero ──────────────────────────────────────────────────── */}
      <div className="hero-banner">
        <div className="hero-kicker">WORLD CUP 2026</div>
        <div className="hero-title">AI MATCH <span className="accent">INTELLIGENCE</span></div>
        <div className="hero-sub">用数据拆解比赛，用临场变量追踪胜率变化。</div>
      </div>

      {/* ── Capability bar ────────────────────────────────────────── */}
      <div className="cap-bar">
        {CAPABILITIES.map(c => (
          <div className="cap-chip" key={c.label}>
            <span className="ci">{c.ic}</span>{c.label}
          </div>
        ))}
      </div>

      {/* ── Balance strip ─────────────────────────────────────────── */}
      <div className="strip">
        <div className="row gap8">
          <span>🪙</span>
          <span className="small">我的 MTC 球迷积分：<b style={{ color: 'var(--blueMid)' }}>{balance}</b></span>
        </div>
        <button className={`btn-mini ${checkedIn ? 'done' : ''}`} onClick={handleCheckIn} disabled={checkedIn}>
          {checkedIn ? '已签到' : '签到 +10'}
        </button>
      </div>

      {apiError && (
        <div style={{ fontSize: 11, color: 'var(--amber)', padding: '6px 10px', background: '#FFF6E2', borderRadius: 8, marginBottom: 12 }}>
          ⚠️ 使用本地缓存数据（情报源暂时不可用）
        </div>
      )}

      {/* ── Date / category scroller ──────────────────────────────── */}
      <div className="date-scroll">
        {DATE_TABS.map(t => (
          <button
            key={t}
            className={`date-pill ${activeDate === t ? 'on' : ''}`}
            onClick={() => setActiveDate(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── Section header ────────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">赛事情报</span>
        <span className="en">MATCH INTEL</span>
        <span style={{ marginLeft: 'auto' }} className="src-pill">
          <span className="sync-dot" />数据同步 · {syncTime}
        </span>
      </div>

      {/* ── Match cards ───────────────────────────────────────────── */}
      <MatchCard match={focus} onClick={() => goDetail(focus.id)} />
      {rest.map(m => (
        <MatchCard key={m.id} match={m} onClick={() => goDetail(m.id)} />
      ))}

      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注 · MTC 不可提现</div>
    </div>
  );
}
