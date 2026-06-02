import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { FeatureBars } from '../components/FeatureBars';
import { MatchHeader } from '../components/MatchHeader';

const RISK_LABELS = { low: '低', medium: '中', high: '高' };
const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };

export function ReportPage() {
  const navigate = useNavigate();
  const { matches, selectedMatchId, loadReport } = useAppStore();
  const match = matches.find(m => m.id === selectedMatchId) ?? matches[0];

  // Load full report (features, tactics, trend) from API
  useEffect(() => {
    if (selectedMatchId) loadReport(selectedMatchId);
  }, [selectedMatchId]);  // eslint-disable-line react-hooks/exhaustive-deps

  if (!match) return null;

  const hasTrend = match.trendHistory.length > 0;
  const maxTrend = hasTrend ? Math.max(...match.trendHistory.map(t => t.prob)) : 100;

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">完整 AI 报告</span>
        <span style={{ marginLeft: 'auto', background: '#E3F4EA', color: 'var(--green)', display: 'inline-block', fontSize: 11, fontWeight: 800, padding: '5px 10px', borderRadius: 999 }}>
          🔓 已解锁
        </span>
      </div>

      {/* AI verdict */}
      <div className="paywall" style={{ borderColor: 'rgba(30,158,90,.4)' }}>
        <div className="row gap8 mb12"><span>✨</span><span className="b">AI 最终判断</span></div>
        <MatchHeader match={match} />
        <p className="small" style={{ color: '#3A4A60' }}>{match.homeTeam.name} 小幅占优，但不是稳胆。</p>
        <div className="stats">
          <div className="stat">
            <div className="v" style={{ color: 'var(--blueMid)' }}>{match.recommendedScore.split(' / ')[0] || '—'}</div>
            <div className="l">推荐比分</div>
          </div>
          <div className="stat">
            <div className="v" style={{ color: RISK_COLORS[match.riskLevel] }}>{RISK_LABELS[match.riskLevel]}</div>
            <div className="l">风险等级</div>
          </div>
          <div className="stat">
            <div className="v" style={{ color: 'var(--green)' }}>{match.confidence}%</div>
            <div className="l">信心</div>
          </div>
        </div>
      </div>

      <div className="sec">胜平负概率分布</div>
      <div className="card">
        <WinBar prob={match.winProb} homeLabel={`${match.homeTeam.name}胜`} awayLabel={`${match.awayTeam.name}胜`} />
      </div>

      {match.features.length > 0 && (
        <>
          <div className="sec">特征贡献度</div>
          <div className="card">
            <FeatureBars features={match.features} />
          </div>
        </>
      )}

      {match.tacticsNote && (
        <>
          <div className="sec">战术白话解释</div>
          <div className="card">
            <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>{match.tacticsNote}</p>
          </div>
        </>
      )}

      {hasTrend && (
        <>
          <div className="sec">胜率变化走势</div>
          <div className="card">
            <div className="trend">
              {match.trendHistory.map((t, i) => {
                const h = Math.round((t.prob / maxTrend) * 100);
                const isLast = i === match.trendHistory.length - 1;
                return (
                  <div className="col" key={t.label}>
                    <span className="pv" style={{ color: isLast ? 'var(--blue)' : 'var(--blueMid)' }}>{t.prob}%</span>
                    <div className="barv" style={{ height: h, background: isLast ? 'var(--blue)' : 'var(--blueLight)' }} />
                    <span className="pt">{t.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* Live correction record */}
      {match.liveCorrection && (
        <>
          <div className="sec">临场修正记录</div>
          <div className="card accent-blue">
            <div className="row gap8 mb12">
              <span>🔔</span>
              <span className="b small">{match.liveCorrection.trigger}</span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{match.homeTeam.name}胜率</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.home}%</span>
                {' → '}
                <span style={{ color: 'var(--green)' }}>{match.liveCorrection.after.home}% ▲</span>
              </span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>平局概率</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.draw}%</span>
                {' → '}
                <span style={{ color: 'var(--red)' }}>{match.liveCorrection.after.draw}% ▼</span>
              </span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{match.awayTeam.name}胜率</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.away}%</span>
                {' → '}
                <span style={{ color: 'var(--red)' }}>{match.liveCorrection.after.away}% ▼</span>
              </span>
            </div>
            <p className="xs sub mt12" style={{ lineHeight: 1.7 }}>
              变化原因：{match.liveCorrection.reason}
            </p>
          </div>
        </>
      )}

      <button className="cta primary" onClick={() => navigate('/community')}>
        订阅社群 · 每场临场修正实时推送
      </button>
      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注 · MTC 不可提现</div>
    </div>
  );
}
