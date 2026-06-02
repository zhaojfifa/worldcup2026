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

  // Load full detail (free_note, live_correction) from API
  useEffect(() => {
    if (selectedMatchId) loadDetail(selectedMatchId);
  }, [selectedMatchId]);  // eslint-disable-line react-hooks/exhaustive-deps

  // Sync lineupSimulated with store correction
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
    if (balance < 390) { toast('MTC 积分不足，去做任务赚积分'); return; }
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
    // match.winProb now updated in store — grab new value for toast
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

      <div className="card">
        <MatchHeader match={match} />
        <div className="row center gap8">
          <span className="pill" style={{ background: 'var(--sky)', color: 'var(--blueMid)' }}>免费结果</span>
          <span className="pill" style={{ background: RISK_BG[riskLevel], color: RISK_COLORS[riskLevel] }}>
            {RISK_LABELS[riskLevel]}
          </span>
        </div>
      </div>

      <div className="sec">AI 当前胜率</div>
      <div className="card">
        <WinBar prob={match.winProb} homeLabel={`${match.homeTeam.name}胜`} awayLabel={`${match.awayTeam.name}胜`} />
        <div className="row center gap8 mt12" style={{ paddingTop: 12, borderTop: '1px solid var(--line)' }}>
          <span>🎯</span>
          <span className="small">推荐比分 <b style={{ color: 'var(--blueMid)' }}>{match.recommendedScore}</b></span>
        </div>
      </div>

      {/* 临场 30 分钟修正模块 */}
      <div className="card accent-blue">
        <div className="row between mb12">
          <span className="row gap8 b small" style={{ color: 'var(--blue)' }}>
            <span>⏱️</span>赛前 30 分钟临场修正
          </span>
          <span className="pill" style={{ background: '#FFF6E2', color: 'var(--amber)' }}>关键功能</span>
        </div>

        {lineupSimulated && match.liveCorrection ? (
          <p className="xs sub" style={{ lineHeight: 1.7 }}>
            【临场修正】{match.liveCorrection.trigger}，AI 重新计算：<br />
            {match.homeTeam.name}胜率{' '}
            <b style={{ color: 'var(--green)' }}>
              {match.liveCorrection.before.home}% → {match.liveCorrection.after.home}% ▲
            </b>
            ，平局 {match.liveCorrection.before.draw}% → {match.liveCorrection.after.draw}%，
            {match.awayTeam.name} {match.liveCorrection.before.away}% → {match.liveCorrection.after.away}%。<br />
            原因：{match.liveCorrection.reason}
          </p>
        ) : (
          <p className="xs sub" style={{ lineHeight: 1.7 }}>
            等待官方首发名单公布。首发确定后，AI 将根据主力出场、阵型变化、替补强度重新计算胜率。
          </p>
        )}

        <button
          className="cta ghost mt12"
          onClick={handleSimulateLineup}
          disabled={lineupSimulated}
          style={lineupSimulated ? { opacity: 0.6 } : {}}
        >
          {lineupSimulated ? '已根据首发重新计算 ✓' : '模拟首发公布 → 重新计算'}
        </button>
      </div>

      <div className="sec">免费解读</div>
      <div className="card">
        <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>
          {match.freeNote || 'AI 数据加载中…'}
        </p>
      </div>

      {/* Paywall */}
      <div className="paywall">
        <div className="row gap8 mb12"><span>🔒</span><span className="b">解锁完整 AI 模型解析</span></div>
        {['为什么 AI 更看好主队', '哪些数据影响了胜率', '客队的核心风险点', '主队是否被高估', '首发公布后胜率如何变化'].map(f => (
          <div className="feat" key={f}><span className="ck">✔</span>{f}</div>
        ))}
        <div className="mt12">
          <button className="cta primary" onClick={handleUnlockCash}>39 元解锁完整分析</button>
          <button className="cta ghost" onClick={handleUnlockToken}>
            🪙 使用 390 MTC积分 解锁（余额 {balance}）
          </button>
          <button className="cta ghost" onClick={() => navigate('/community')}>加入 199元/月 临场社群</button>
        </div>
      </div>

      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注 · MTC 不可提现</div>

      {modal && <Modal {...modal} onClose={() => setModal(null)} />}
    </div>
  );
}
