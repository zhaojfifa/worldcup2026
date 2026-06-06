import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { toast } from '../components/Toast';
import { deriveOps, pickTopSignal, topUpsets } from '../ops/derive';
import { HOME, BRAND } from '../copy/zh';
import { useCopy } from '../i18n/dict';
import { api, safeTrack, type ApiCommunityHeat } from '../api/client';
import type { Match } from '../types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function fmtTime(iso: string) {
  const d = new Date(iso);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}
function fmtDate(iso: string) {
  const d = new Date(iso);
  return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
function upsetHook(score: number): string {
  if (score >= 60) return '爆冷风险升高';
  if (score >= 40) return '需谨慎关注';
  return '风险可控';
}

export function HomePage() {
  const navigate = useNavigate();
  const t = useCopy();
  const CAPABILITIES = [
    { ic: '🧠', label: t.capModel },
    { ic: '⏱️', label: t.capLive },
    { ic: '⚖️', label: t.capRisk },
    { ic: '🪙', label: t.capUnlock },
  ];
  const {
    balance, checkedIn, checkIn,
    matches, matchesLoading, loadMatches,
    setSelectedMatch, syncedAt, apiError,
  } = useAppStore();

  const [heat, setHeat] = useState<ApiCommunityHeat | null>(null);

  useEffect(() => { loadMatches(); }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  // Anonymous home view + community heat (API mode only).
  useEffect(() => {
    if (USE_MOCK) return;
    safeTrack('view_home');
    api.getCommunityHeat().then(setHeat).catch(() => { /* keep building-state */ });
  }, []);

  function goDetail(id: string) {
    safeTrack('click_detail', Number(id));
    setSelectedMatch(id);
    navigate('/detail');
  }

  async function handleCheckIn() {
    if (checkedIn) { toast(t.checkinToastDone); return; }
    await checkIn();
    toast(t.checkinToastOk);
  }

  const syncTime = new Date(syncedAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  const modelCount = matches.length;
  const liveCount = matches.filter(m => m.tag === 'live').length;

  if (matchesLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'var(--sub)' }}>
        <div style={{ fontSize: 30, marginBottom: 12 }}>⚽</div>
        <div className="small">AI 情报加载中…</div>
      </div>
    );
  }

  const signal = pickTopSignal(matches);
  if (!signal) return null;

  const sOps = deriveOps(signal);
  const upsets = topUpsets(matches, 3);

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
        <div className="hero-kicker">GIÀNH CUP</div>
        <div className="hero-title">{t.heroTitlePre}<span className="accent">{t.heroTitleAccent}</span></div>
        <div className="hero-en">{BRAND.heroEn}</div>
        <div className="hero-sub">{t.heroSub}</div>
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
          <span className="small">{t.balanceLabel}<b style={{ color: 'var(--blueMid)' }}>{balance}</b></span>
        </div>
        <button className={`btn-mini ${checkedIn ? 'done' : ''}`} onClick={handleCheckIn} disabled={checkedIn}>
          {checkedIn ? t.checkedIn : t.checkin}
        </button>
      </div>

      {apiError && (
        <div style={{ fontSize: 11, color: 'var(--amber)', padding: '6px 10px', background: '#FFF6E2', borderRadius: 8, marginBottom: 12 }}>
          ⚠️ 使用本地缓存数据（情报源暂时不可用）
        </div>
      )}

      {/* ── 1. 今日 AI 最强信号 (C-position) ───────────────────────── */}
      <div className="signal-card" onClick={() => goDetail(signal.id)}>
        <div className="signal-head">
          <span className="signal-badge">⭐ {t.signalTitle}</span>
          <span className="signal-en">{BRAND.signalTag}</span>
        </div>
        <div className="signal-teams">
          <div className="t"><div className="fl">{signal.homeTeam.flag}</div><div className="nm">{signal.homeTeam.name}</div></div>
          <div className="vs">VS</div>
          <div className="t"><div className="fl">{signal.awayTeam.flag}</div><div className="nm">{signal.awayTeam.name}</div></div>
        </div>
        <div className="signal-row">
          <span className="signal-tend">{t.tendency}：{sOps.aiPickLabel}</span>
          <span className="signal-star">{sOps.confidenceStars}</span>
        </div>
        <div style={{ margin: '4px 0 10px' }}>
          <WinBar prob={signal.winProb} homeLabel={`${signal.homeTeam.name}胜`} awayLabel={`${signal.awayTeam.name}胜`} />
        </div>
        <div className="signal-risk">⚠️ {t.topRisk}：{sOps.topRisk}</div>
        <div className="signal-cta">
          <span className="b1" onClick={(e) => { e.stopPropagation(); goDetail(signal.id); }}>{t.ctaView}</span>
          <span className="b2" onClick={(e) => { e.stopPropagation(); goDetail(signal.id); }}>{t.ctaUnlock}</span>
        </div>
      </div>

      {/* ── 2. 今日比赛简表 ────────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.listTitle}</span>
        <span className="en">{HOME.listEn}</span>
        <span style={{ marginLeft: 'auto' }} className="src-pill"><span className="sync-dot" />同步 {syncTime}</span>
      </div>
      {matches.map((m: Match) => {
        const ops = deriveOps(m);
        return (
          <div className="simrow" key={m.id} onClick={() => goDetail(m.id)}>
            <div className="time">{fmtDate(m.kickoffTime)}<br />{fmtTime(m.kickoffTime)}</div>
            <div className="teams">{m.homeTeam.flag} {m.homeTeam.name}<span className="vs">vs</span>{m.awayTeam.name} {m.awayTeam.flag}</div>
            <div className="chips">
              <span className="tend">{ops.aiPickLabel}</span>
              <span className={`risk-chip ${m.riskLevel}`}>{m.riskLevel === 'low' ? '低' : m.riskLevel === 'medium' ? '中' : '高'}</span>
              <span className="heat-chip">{ops.heatLabel}</span>
            </div>
          </div>
        );
      })}

      {/* ── 3. 今日爆冷风险 TOP3 ───────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.upsetTitle}</span>
        <span className="en">{HOME.upsetEn}</span>
      </div>
      {upsets.map((u, i) => (
        <div className="upset-item" key={u.match.id} onClick={() => goDetail(u.match.id)}>
          <div className="upset-rank">{i + 1}</div>
          <div className="upset-body">
            <div className="upset-match">{u.match.homeTeam.flag} {u.match.homeTeam.name} vs {u.match.awayTeam.name} {u.match.awayTeam.flag}</div>
            <div className="upset-hook">⚠️ {upsetHook(u.score)}</div>
          </div>
          <div className="upset-score">
            <div className="v">{u.score}</div>
            <div className="l">爆冷分</div>
          </div>
        </div>
      ))}

      {/* ── 4. AI 情报战绩 (待真实赛果回灌) ────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.recordTitle}</span>
        <span className="en">{HOME.recordEn}</span>
      </div>
      <div className="status-card">
        <div className="ic">📊</div>
        <div className="st">{t.recordPending}</div>
        <div className="sub2">命中率与连续命中等战绩指标，将在接入真实数据源、完成赛果回灌后开放。</div>
        <span className="status-pill">{t.recordBuilding}</span>
        <div className="disclaimer-line">{t.disclaimer}</div>
      </div>

      {/* ── 5. 社区热门选择 (轻社交证明) ───────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.heatTitle}</span>
        <span className="en">{HOME.heatEn}</span>
      </div>
      {heat && heat.top_matches.length > 0 ? (
        <>
          {heat.top_matches.slice(0, 3).map((m, i) => (
            <div className="upset-item" key={m.match_id} style={{ borderColor: 'var(--line)' }}>
              <div className="upset-rank" style={{ background: 'var(--blueMid)' }}>{i + 1}</div>
              <div className="upset-body">
                <div className="upset-match">{m.home} vs {m.away}</div>
                <div className="upset-hook" style={{ color: 'var(--blueMid)' }}>🔥 社区关注</div>
              </div>
              <div className="upset-score">
                <div className="v" style={{ color: 'var(--blueMid)' }}>{m.interactions}</div>
                <div className="l">互动</div>
              </div>
            </div>
          ))}
          <div className="disclaimer-line" style={{ textAlign: 'center' }}>社区热度为匿名站内互动统计，不含用户个人信息。</div>
        </>
      ) : (
        <div className="status-card">
          <div className="ic">🔥</div>
          <div className="st">{t.heatComingSoon}</div>
          <div className="sub2">社区讨论热度与用户关注趋势，正在建设中。</div>
          <span className="status-pill">{t.heatComingSoon}</span>
        </div>
      )}

      {/* ── 6. Token / 连胜挑战 / 排行榜入口 ───────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.loopTitle}</span>
        <span className="en">{HOME.loopEn}</span>
      </div>
      <div className="loop-grid">
        <div className="loop-tile" onClick={() => navigate('/token')}>
          <div className="ic">🪙</div><div className="nm">球迷积分</div><div className="ds">每日签到</div>
        </div>
        <div className="loop-tile" onClick={() => navigate('/token')}>
          <div className="ic">🎯</div><div className="nm">连胜挑战</div><div className="ds">免费参与</div>
        </div>
        <div className="loop-tile" onClick={() => toast('排行榜即将上线')}>
          <div className="ic">🏅</div><div className="nm">排行榜</div><div className="ds">即将上线</div>
        </div>
      </div>
      <div className="compliance">{t.mtcStatement}</div>

      <div className="muted-note">{t.complianceFooter}</div>
    </div>
  );
}
