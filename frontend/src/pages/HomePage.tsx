import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { MatchHeader } from '../components/MatchHeader';
import { toast } from '../components/Toast';

const TAG_LABELS: Record<string, string> = {
  focus: '🏆 焦点战',
  upset: '🔥 爆冷预警',
  live:  '⚡ 临场更新',
  'high-conf': '🎯 高信心',
};

export function HomePage() {
  const navigate = useNavigate();
  const {
    balance, checkedIn, checkIn,
    matches, matchesLoading, loadMatches,
    setSelectedMatch, syncedAt, apiError,
  } = useAppStore();
  const [activeTab, setActiveTab] = useState('焦点');

  // Hydrate from API on first mount
  useEffect(() => { loadMatches(); }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  const focus = matches.find(m => m.tag === 'focus') ?? matches[0];
  const rest  = matches.filter(m => m.id !== focus?.id);

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
      <div style={{ padding: 32, textAlign: 'center', color: 'var(--sub)' }}>
        <div style={{ fontSize: 28, marginBottom: 12 }}>⚽</div>
        <div className="small">AI 数据加载中…</div>
      </div>
    );
  }

  if (!focus) return null;

  return (
    <div className="page-enter">
      {/* API source indicator (dev only) */}
      {apiError && (
        <div style={{ fontSize: 11, color: 'var(--amber)', padding: '4px 8px', background: '#FFF6E2', borderRadius: 8, marginTop: 8 }}>
          ⚠️ 使用本地缓存数据（API 暂时不可用）
        </div>
      )}

      {/* Balance strip */}
      <div className="strip">
        <div className="row gap8">
          <span>🪙</span>
          <span className="small">我的 MTC 球迷积分：<b style={{ color: 'var(--blueMid)' }}>{balance}</b></span>
        </div>
        <button className={`btn-mini ${checkedIn ? 'done' : ''}`} onClick={handleCheckIn} disabled={checkedIn}>
          {checkedIn ? '已签到' : '签到 +10'}
        </button>
      </div>

      {/* Live correction banner */}
      <div className="livebanner" onClick={() => goDetail(focus.id)}>
        <span className="ic">⏱️</span>
        <div style={{ flex: 1 }}>
          <div className="h">赛前 30 分钟 · 临场修正</div>
          <div className="p">首发名单公布后，AI 自动重算胜率并推送变盘</div>
        </div>
        <span style={{ color: 'var(--blueMid)', fontSize: 18 }}>›</span>
      </div>

      {/* Filter tabs */}
      <div className="tabs">
        {['焦点', '高信心', '爆冷预警', '临场更新'].map(t => (
          <button key={t} className={`tab ${activeTab === t ? 'on' : ''}`} onClick={() => setActiveTab(t)}>{t}</button>
        ))}
      </div>

      {/* Focus match */}
      <div className="card accent" style={{ borderColor: 'rgba(16,119,195,.35)' }}>
        <div className="row between mb12">
          <span className="pill" style={{ background: 'var(--blue)', color: '#fff' }}>
            {TAG_LABELS[focus.tag ?? 'focus']}
          </span>
          <span className="xs sub">
            {new Date(focus.kickoffTime).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })}{' '}
            {new Date(focus.kickoffTime).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <MatchHeader match={focus} />

        <div className="mt8 mb12">
          <WinBar prob={focus.winProb} homeLabel={`${focus.homeTeam.name}胜`} awayLabel={`${focus.awayTeam.name}胜`} />
        </div>

        <div className="row gap8 mb12">
          <span>🎯</span>
          <span className="small">AI 推荐比分 <b style={{ color: 'var(--blueMid)' }}>{focus.recommendedScore}</b></span>
        </div>

        <div className="risk mb12">
          <span className="ic">⚠️</span>
          <span className="tx">{focus.riskNote}</span>
        </div>

        <div className="lockline">🔒 39元 / 390 MTC积分 解锁完整 AI 模型解析</div>
        <button className="cta primary" onClick={() => goDetail(focus.id)}>查看详情 →</button>
      </div>

      {/* Secondary matches */}
      {rest.map(m => (
        <button key={m.id} className="smatch" onClick={() => goDetail(m.id)}>
          <div className="row between mb12">
            <span className="tag">{TAG_LABELS[m.tag ?? 'focus']}</span>
            {m.tag === 'live' && (
              <span className="pill" style={{ background: '#E3F4EA', color: 'var(--green)' }}>● LIVE 临场</span>
            )}
          </div>
          <div className="row between">
            <span className="b small">{m.homeTeam.flag} {m.homeTeam.name}</span>
            <span className="probs">
              <span style={{ color: 'var(--green)' }}>{m.winProb.home}%</span>
              <span style={{ color: 'var(--amber)' }}>{m.winProb.draw}%</span>
              <span style={{ color: 'var(--red)' }}>{m.winProb.away}%</span>
            </span>
            <span className="b small">{m.awayTeam.flag} {m.awayTeam.name}</span>
          </div>
        </button>
      ))}

      <p className="xs sub" style={{ textAlign: 'center', marginTop: 8 }}>
        数据同步 · 最近更新 {syncTime}
      </p>
      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注 · MTC 不可提现</div>
    </div>
  );
}
