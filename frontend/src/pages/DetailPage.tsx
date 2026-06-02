import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { MatchHeader } from '../components/MatchHeader';
import { Modal } from '../components/Modal';
import { toast } from '../components/Toast';

const RISK_LABELS = { low: '低风险', medium: '中风险', high: '高风险' };
const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };
const RISK_BG     = { low: '#E3F4EA',     medium: '#FFF6E2',       high: '#FEE8E9' };

export function DetailPage() {
  const navigate = useNavigate();
  const {
    balance, matches, selectedMatchId,
    loadDetail, unlockWithCash, unlockWithToken, simulateCorrection,
  } = useAppStore();

  const match = matches.find(m => m.id === selectedMatchId) ?? matches[0];
  const [modal, setModal] = useState<null | { em: string; title: string; body: string; onOk: () => void }>(null);
  const [lineupSimulated, setLineupSimulated] = useState(!!match?.liveCorrection);

  useEffect(() => {
    if (selectedMatchId) loadDetail(selectedMatchId);
  }, [selectedMatchId]);  // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (match?.liveCorrection) setLineupSimulated(true);
  }, [match?.liveCorrection]);

  if (!match) return null;

  async function handleUnlockCash() {
    const res = await unlockWithCash(match.id);
    setModal({
      em: '💳',
      title: res.success ? '模拟支付成功' : '支付失败',
      body: res.message,
      onOk: () => { if (res.success) navigate('/report'); },
    });
  }

  async function handleUnlockToken() {
    if (balance < 390) { toast('MTC 积分不足，去任务中心点亮比赛日'); return; }
    const res = await unlockWithToken(match.id);
    if (!res.success) { toast(res.message); return; }
    setModal({
      em: '🪙',
      title: '已扣减 390 MTC 积分',
      body: res.message,
      onOk: () => navigate('/report'),
    });
  }

  async function handleSimulateLineup() {
    if (lineupSimulated) return;
    const prevHome = match.winProb.home;
    await simulateCorrection(match.id);
    setLineupSimulated(true);
    const updated = useAppStore.getState().matches.find(m => m.id === match.id);
    const newHome = updated?.winProb.home ?? prevHome + 4;
    toast(`临场修正：${match.homeTeam.name}胜率 ${prevHome}% → ${newHome}%`);
  }

  const riskLevel = match.riskLevel;

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">单场预测详情</span>
      </div>

      {/* Match header */}
      <div className="card">
        <div className="mono-label" style={{ textAlign: 'center', marginBottom: 4 }}>AI PRE-MATCH MODEL</div>
        <MatchHeader match={match} />
        <div className="row center gap8">
          <span className="pill" style={{ background: 'var(--sky)', color: 'var(--blueMid)' }}>免费速览</span>
          <span className="pill" style={{ background: RISK_BG[riskLevel], color: RISK_COLORS[riskLevel] }}>
            {RISK_LABELS[riskLevel]}
          </span>
        </div>
      </div>

      {/* Current win prob */}
      <div className="sec-en">
        <span className="zh">AI 当前胜率</span>
        <span className="en">WIN PROBABILITY</span>
      </div>
      <div className="card">
        <WinBar prob={match.winProb} homeLabel={`${match.homeTeam.name}胜`} awayLabel={`${match.awayTeam.name}胜`} />
        <div className="mcard-meta">
          <div className="conf-block">
            <div className="conf-head">
              <span className="lbl">信心指数</span>
              <span className="num">{Math.round(match.confidence)}</span>
            </div>
            <div className="conf-track">
              <div className="conf-fill" style={{ width: `${match.confidence}%` }} />
            </div>
          </div>
          <div className="score-block">
            <div className="lbl">推荐比分</div>
            <div className="val">{match.recommendedScore}</div>
          </div>
        </div>
      </div>

      {/* ── LINEUP WATCH ──────────────────────────────────────────── */}
      <div className="lineup-watch">
        <div className="lw-head">
          <span className="lw-title">📡 LINEUP WATCH · 临场监听</span>
          {lineupSimulated ? (
            <span className="lw-status"><span className="sync-dot" />已重算</span>
          ) : (
            <span className="lw-status armed"><span className="sync-dot" />待命中</span>
          )}
        </div>

        <div className="lw-steps">
          <div className="lw-step"><div className="n">60'</div><div className="t">赛前自动<br />进入监听</div></div>
          <div className="lw-step"><div className="n">首发</div><div className="t">公布后<br />触发重算</div></div>
          <div className="lw-step"><div className="n">AI</div><div className="t">胜率随变量<br />实时更新</div></div>
        </div>

        {lineupSimulated && match.liveCorrection ? (
          <p className="lw-body">
            <span className="hl">【临场修正】</span>{match.liveCorrection.trigger}，模型重新计算：
            {match.homeTeam.name}胜率 <span className="hl">{match.liveCorrection.before.home}% → {match.liveCorrection.after.home}% ▲</span>，
            平局 {match.liveCorrection.before.draw}% → {match.liveCorrection.after.draw}%，
            {match.awayTeam.name} {match.liveCorrection.before.away}% → {match.liveCorrection.after.away}%。
            <br />原因：{match.liveCorrection.reason}
          </p>
        ) : (
          <p className="lw-body">
            开赛前 60 分钟自动进入监听。首发公布后触发 AI 重算——阵容变化、核心缺阵、战术改动都会影响胜率。
          </p>
        )}

        <button
          className="lw-btn"
          style={{ marginTop: 12 }}
          onClick={handleSimulateLineup}
          disabled={lineupSimulated}
        >
          {lineupSimulated ? '已根据首发重新计算 ✓' : '模拟首发公布 → AI 重算'}
        </button>
      </div>

      {/* ── FREE ZONE ─────────────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">免费解读</span>
        <span className="en">FREE READ</span>
      </div>
      <div className="card">
        <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>
          {match.freeNote || 'AI 数据加载中…'}
        </p>
      </div>

      {/* ── PAID ZONE ─────────────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">AI 战术底牌</span>
        <span className="en">PREMIUM</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, fontWeight: 800, color: 'var(--blueMid)' }}>🔒 未解锁</span>
      </div>
      <div className="paywall">
        <div className="row gap8 mb12"><span>✨</span><span className="b">解锁后可查看完整模型解释</span></div>
        {['为什么 AI 更看好主队', '哪些数据影响了胜率', '客队的核心风险点', '主队是否被高估', '首发公布后胜率如何变化'].map(f => (
          <div className="feat" key={f}><span className="ck">✔</span>{f}</div>
        ))}
        <div className="mt12">
          <button className="cta primary" onClick={handleUnlockCash}>解锁 AI 战术底牌 · 39 元</button>
          <button className="cta ghost" onClick={handleUnlockToken}>
            🪙 查看完整模型解释 · 390 MTC（余额 {balance}）
          </button>
          <button className="cta ghost" onClick={() => navigate('/community')}>加入临场情报社群 · 199 元/月</button>
        </div>
      </div>

      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注 · MTC 不可提现</div>

      {modal && <Modal {...modal} onClose={() => setModal(null)} />}
    </div>
  );
}
