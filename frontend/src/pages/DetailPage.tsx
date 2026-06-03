import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { MatchHeader } from '../components/MatchHeader';
import { Modal } from '../components/Modal';
import { toast } from '../components/Toast';
import { deriveOps, reasonBullets } from '../ops/derive';
import { DETAIL, COMPLIANCE_FOOTER } from '../copy/zh';

const RISK_LABELS = { low: '低风险', medium: '中风险', high: '高风险' };
const RISK_GRADE  = { low: '低', medium: '中', high: '高' };
const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };
const RISK_BG     = { low: '#E3F4EA',     medium: '#FFF6E2',       high: '#FEE8E9' };
const STAR_COLOR  = { low: '#8DF2B6', medium: '#FFD27A', high: '#FFAEB2' };

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

  const ops = deriveOps(match);
  const bullets = reasonBullets(match);
  const riskLevel = match.riskLevel;

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
      </div>

      {/* ── 1. AI 结论卡（置顶） ──────────────────────────────────── */}
      <div className="verdict-card">
        <div className="verdict-top">
          <span className="zh">✨ {DETAIL.verdictTitle}</span>
          <span className="en">{DETAIL.verdictEn}</span>
        </div>
        <div className="verdict-grid">
          <div className="verdict-cell">
            <div className="l">{DETAIL.tendency}</div>
            <div className="v">{ops.aiPickLabel}</div>
          </div>
          <div className="verdict-cell">
            <div className="l">{DETAIL.confidence}</div>
            <div className="v star">{ops.confidenceStars}</div>
          </div>
          <div className="verdict-cell">
            <div className="l">{DETAIL.riskGrade}</div>
            <div className="v" style={{ color: STAR_COLOR[riskLevel] }}>{RISK_GRADE[riskLevel]}</div>
          </div>
          <div className="verdict-cell">
            <div className="l">{DETAIL.recommendedScore}</div>
            <div className="verdict-lock">{DETAIL.unlockToView}<span className="lockchip">🔒</span></div>
          </div>
        </div>
      </div>

      {/* ── 2. 胜率图 ─────────────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{DETAIL.winProbTitle}</span>
        <span className="en">{DETAIL.winProbEn}</span>
      </div>
      <div className="card">
        <WinBar prob={match.winProb} homeLabel={`${match.homeTeam.name}胜`} awayLabel={`${match.awayTeam.name}胜`} />
        <div className="conf-block" style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--line)' }}>
          <div className="conf-head">
            <span className="lbl">信心指数</span>
            <span className="num">{Math.round(match.confidence)}</span>
            <span style={{ marginLeft: 'auto', color: 'var(--gold)', fontWeight: 800 }}>{ops.confidenceStars}</span>
          </div>
          <div className="conf-track"><div className="conf-fill" style={{ width: `${match.confidence}%` }} /></div>
        </div>
      </div>

      {/* ── 3. 为什么 AI 这么判断 ─────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{DETAIL.whyTitle}</span>
        <span className="en">{DETAIL.whyEn}</span>
      </div>
      <div className="card">
        {match.freeNote && (
          <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75, marginBottom: 10 }}>{match.freeNote}</p>
        )}
        <ul className="reason-list">
          {bullets.map((b, i) => <li key={i}>{b}</li>)}
        </ul>
      </div>

      {/* ── 4. 风险关注维度 ───────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{DETAIL.riskTitle}</span>
        <span className="en">{DETAIL.riskEn}</span>
        <span style={{ marginLeft: 'auto', background: RISK_BG[riskLevel], color: RISK_COLORS[riskLevel] }} className="pill">
          {RISK_LABELS[riskLevel]}
        </span>
      </div>
      <div className="card">
        <div className="risk-tagrow">
          {ops.riskTags.map(t => <span className="risk-tag" key={t}>{t}</span>)}
        </div>
        {match.riskNote && (
          <p className="xs sub" style={{ marginTop: 10, lineHeight: 1.7 }}>{match.riskNote}</p>
        )}
      </div>

      {/* ── 5. LINEUP WATCH ───────────────────────────────────────── */}
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
            开赛前 60 分钟自动进入监听。首发公布后，AI 根据核心球员、阵型变化、替补强度重新计算胜率。
          </p>
        )}
        <button className="lw-btn" style={{ marginTop: 12 }} onClick={handleSimulateLineup} disabled={lineupSimulated}>
          {lineupSimulated ? '已根据首发重新计算 ✓' : '模拟首发公布 → AI 重算'}
        </button>
      </div>

      {/* ── 6. 付费解锁 / 社群引导 ────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">AI 战术底牌</span>
        <span className="en">PREMIUM</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, fontWeight: 800, color: 'var(--blueMid)' }}>🔒 未解锁</span>
      </div>
      <div className="paywall">
        <div className="row gap8 mb12"><span>✨</span><span className="b">解锁后可查看完整模型解释</span></div>
        {ops.premiumTeaser.map(f => (
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

      <div className="muted-note">{COMPLIANCE_FOOTER}</div>

      {modal && <Modal {...modal} onClose={() => setModal(null)} />}
    </div>
  );
}
