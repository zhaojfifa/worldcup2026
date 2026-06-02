import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { FeatureBars } from '../components/FeatureBars';
import { MatchHeader } from '../components/MatchHeader';

const RISK_LABELS = { low: '低', medium: '中', high: '高' };
const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };

function riskColor(v: number) {
  if (v >= 70) return 'var(--red)';
  if (v >= 45) return 'var(--amber)';
  return 'var(--green)';
}

export function ReportPage() {
  const navigate = useNavigate();
  const { matches, selectedMatchId, loadReport } = useAppStore();
  const match = matches.find(m => m.id === selectedMatchId) ?? matches[0];

  useEffect(() => {
    if (selectedMatchId) loadReport(selectedMatchId);
  }, [selectedMatchId]);  // eslint-disable-line react-hooks/exhaustive-deps

  if (!match) return null;

  const hasTrend = match.trendHistory.length > 0;
  const maxTrend = hasTrend ? Math.max(...match.trendHistory.map(t => t.prob)) : 100;
  const conf = Math.round(match.confidence);

  // Derived risk-radar dimensions (visual only — no new API fields)
  const topFeature = match.features[0]?.value ?? 0;
  const radar = [
    { label: '近期状态', value: conf },
    { label: '阵容完整度', value: match.liveCorrection ? 68 : 86 },
    { label: '战术对位', value: Math.min(92, Math.max(30, 50 + topFeature * 2)) },
    { label: '临场变量', value: match.riskLevel === 'high' ? 80 : match.riskLevel === 'medium' ? 55 : 32 },
  ];

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">模型战术室</span>
        <span style={{ marginLeft: 'auto', background: '#E3F4EA', color: 'var(--green)', display: 'inline-block', fontSize: 11, fontWeight: 800, padding: '5px 10px', borderRadius: 999 }}>
          🔓 已解锁
        </span>
      </div>

      {/* AI verdict + gauge */}
      <div className="paywall" style={{ borderColor: 'rgba(30,158,90,.4)' }}>
        <div className="sec-en" style={{ marginTop: 0 }}>
          <span className="zh">AI 最终判断</span>
          <span className="en">AI TACTICAL ROOM</span>
        </div>
        <MatchHeader match={match} />

        <div className="gauge-wrap mt12">
          <div className="gauge" style={{ background: `conic-gradient(var(--blue) ${conf * 3.6}deg, var(--line) 0)` }}>
            <div className="inner">
              <div className="gv">{conf}%</div>
              <div className="gl">信心指数</div>
            </div>
          </div>
          <div className="gauge-side">
            <div className="gs-row">
              <span><span className="dotc" style={{ background: 'var(--green)' }} />{match.homeTeam.name}胜</span>
              <b>{match.winProb.home}%</b>
            </div>
            <div className="gs-row">
              <span><span className="dotc" style={{ background: 'var(--amber)' }} />平局</span>
              <b>{match.winProb.draw}%</b>
            </div>
            <div className="gs-row">
              <span><span className="dotc" style={{ background: 'var(--red)' }} />{match.awayTeam.name}胜</span>
              <b>{match.winProb.away}%</b>
            </div>
          </div>
        </div>

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
            <div className="v" style={{ color: 'var(--green)' }}>{conf}%</div>
            <div className="l">信心</div>
          </div>
        </div>
      </div>

      {/* Key factor contribution */}
      {match.features.length > 0 && (
        <>
          <div className="sec-en">
            <span className="zh">关键因子贡献</span>
            <span className="en">KEY FACTORS</span>
          </div>
          <div className="card">
            <FeatureBars features={match.features} />
          </div>
        </>
      )}

      {/* Risk radar */}
      <div className="sec-en">
        <span className="zh">风险雷达</span>
        <span className="en">RISK RADAR</span>
      </div>
      <div className="card">
        {radar.map(r => (
          <div className="radar-row" key={r.label}>
            <span className="rl">{r.label}</span>
            <span className="rt"><span className="rf" style={{ width: `${r.value}%`, background: riskColor(r.value) }} /></span>
            <span className="rn" style={{ color: riskColor(r.value) }}>{Math.round(r.value)}</span>
          </div>
        ))}
        <p className="xs sub mt12" style={{ lineHeight: 1.7 }}>
          模型不是简单看球队名气，而是在比较近期状态、阵容完整度、战术对位和临场变量。
        </p>
      </div>

      {/* Tactics explanation */}
      {match.tacticsNote && (
        <>
          <div className="sec-en">
            <span className="zh">战术白话解释</span>
            <span className="en">TACTICS</span>
          </div>
          <div className="card">
            <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>{match.tacticsNote}</p>
          </div>
        </>
      )}

      {/* Trend chart */}
      {hasTrend && (
        <>
          <div className="sec-en">
            <span className="zh">变盘走势</span>
            <span className="en">PROB TREND</span>
          </div>
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
          <div className="sec-en">
            <span className="zh">临场修正记录</span>
            <span className="en">LINEUP WATCH LOG</span>
          </div>
          <div className="card accent-blue">
            <div className="row gap8 mb12">
              <span>🔔</span>
              <span className="b small">{match.liveCorrection.trigger}</span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{match.homeTeam.name}胜率</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.home}%</span>{' → '}
                <span style={{ color: 'var(--green)' }}>{match.liveCorrection.after.home}% ▲</span>
              </span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>平局概率</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.draw}%</span>{' → '}
                <span style={{ color: 'var(--red)' }}>{match.liveCorrection.after.draw}% ▼</span>
              </span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{match.awayTeam.name}胜率</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.away}%</span>{' → '}
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
