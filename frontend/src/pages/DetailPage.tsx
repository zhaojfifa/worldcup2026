import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { MatchHeader } from '../components/MatchHeader';
import { Modal } from '../components/Modal';
import { toast } from '../components/Toast';
import { deriveOps, reasonBullets } from '../ops/derive';
import { BRAND } from '../copy/zh';
import { useCopy } from '../i18n/dict';
import { useLocale } from '../i18n/useLocale';
import { getPrice } from '../i18n/pricing';
import {
  teamVi, homeWinVi, awayWinVi, aiPickLabelVi, riskLevelLongVi, riskLevelShortVi,
  riskTagVi, noteVi, premiumTeaserVi, reasonBulletsVi,
} from '../i18n/viMapping';

const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };
const RISK_BG     = { low: '#E3F4EA',     medium: '#FFF6E2',       high: '#FEE8E9' };
const STAR_COLOR  = { low: '#8DF2B6', medium: '#FFD27A', high: '#FFAEB2' };

export function DetailPage() {
  const navigate = useNavigate();
  const t = useCopy();
  const loc = useLocale();
  const vi = loc === 'vi';
  const price = getPrice(loc);
  const tn = (name: string) => (vi ? teamVi(name) : name);
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
  const bullets = vi ? reasonBulletsVi(match) : reasonBullets(match);
  const riskLevel = match.riskLevel;
  const riskLong = vi ? riskLevelLongVi(riskLevel) : ({ low: '低风险', medium: '中风险', high: '高风险' }[riskLevel]);
  const riskGrade = vi ? riskLevelShortVi(riskLevel) : ({ low: '低', medium: '中', high: '高' }[riskLevel]);

  async function handleUnlockCash() {
    const res = await unlockWithCash(match.id);
    setModal({
      em: '💳',
      title: res.success ? t.payOkTitle : t.payFailTitle,
      body: res.message,
      onOk: () => { if (res.success) navigate('/report'); },
    });
  }

  async function handleUnlockToken() {
    if (balance < 390) { toast(t.mtcInsufficient); return; }
    const res = await unlockWithToken(match.id);
    if (!res.success) { toast(res.message); return; }
    setModal({
      em: '🪙',
      title: t.mtcDeductedTitle,
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
    toast(`${t.liveToastPrefix}${tn(match.homeTeam.name)} ${t.liveToastRate} ${prevHome}% → ${newHome}%`);
  }

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">{t.detailBack}</span>
      </div>

      {/* Match header */}
      <div className="card">
        <div className="mono-label" style={{ textAlign: 'center', marginBottom: 4 }}>AI PRE-MATCH MODEL</div>
        <MatchHeader match={match} />
      </div>

      {/* ── 1. AI 结论卡（置顶） ──────────────────────────────────── */}
      <div className="verdict-card">
        <div className="verdict-top">
          <span className="zh">🔮 {t.aiVerdict}</span>
          <span className="en">{BRAND.verdictTitle}</span>
        </div>
        <div className="verdict-grid">
          <div className="verdict-cell">
            <div className="l">{t.tendency}</div>
            <div className="v">{vi ? aiPickLabelVi(ops.aiPickLabel) : ops.aiPickLabel}</div>
          </div>
          <div className="verdict-cell">
            <div className="l">{t.confidence}</div>
            <div className="v star">{ops.confidenceStars}</div>
          </div>
          <div className="verdict-cell">
            <div className="l">{t.riskGrade}</div>
            <div className="v" style={{ color: STAR_COLOR[riskLevel] }}>{riskGrade}</div>
          </div>
          <div className="verdict-cell">
            <div className="l">{t.recommendedScore}</div>
            <div className="verdict-lock">{t.unlockToView}<span className="lockchip">🔒</span></div>
          </div>
        </div>
      </div>

      {/* ── 2. 胜率图 ─────────────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.winProbTitle}</span>
        <span className="en">WIN PROBABILITY</span>
      </div>
      <div className="card">
        <WinBar prob={match.winProb} homeLabel={vi ? homeWinVi(match.homeTeam.name) : `${match.homeTeam.name}胜`} awayLabel={vi ? awayWinVi(match.awayTeam.name) : `${match.awayTeam.name}胜`} />
        <div className="conf-block" style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--line)' }}>
          <div className="conf-head">
            <span className="lbl">{t.confIndex}</span>
            <span className="num">{Math.round(match.confidence)}</span>
            <span style={{ marginLeft: 'auto', color: 'var(--gold)', fontWeight: 800 }}>{ops.confidenceStars}</span>
          </div>
          <div className="conf-track"><div className="conf-fill" style={{ width: `${match.confidence}%` }} /></div>
        </div>
      </div>

      {/* ── 3. 为什么 AI 这么判断 ─────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.whyTitle}</span>
        <span className="en">WHY</span>
      </div>
      <div className="card">
        {match.freeNote && (
          <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75, marginBottom: 10 }}>{vi ? noteVi(match.freeNote) : match.freeNote}</p>
        )}
        <ul className="reason-list">
          {bullets.map((b, i) => <li key={i}>{b}</li>)}
        </ul>
      </div>

      {/* ── 4. 风险关注维度 ───────────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.riskTitle}</span>
        <span className="en">RISK FACTORS</span>
        <span style={{ marginLeft: 'auto', background: RISK_BG[riskLevel], color: RISK_COLORS[riskLevel] }} className="pill">
          {riskLong}
        </span>
      </div>
      <div className="card">
        <div className="risk-tagrow">
          {ops.riskTags.map(tag => <span className="risk-tag" key={tag}>{vi ? riskTagVi(tag) : tag}</span>)}
        </div>
        {match.riskNote && (
          <p className="xs sub" style={{ marginTop: 10, lineHeight: 1.7 }}>{vi ? noteVi(match.riskNote) : match.riskNote}</p>
        )}
      </div>

      {/* ── 5. LINEUP WATCH ───────────────────────────────────────── */}
      <div className="lineup-watch">
        <div className="lw-head">
          <span className="lw-title">{t.lineupWatchTitle}</span>
          {lineupSimulated ? (
            <span className="lw-status"><span className="sync-dot" />{t.lwRecalc}</span>
          ) : (
            <span className="lw-status armed"><span className="sync-dot" />{t.lwArmed}</span>
          )}
        </div>
        <div className="lw-steps">
          <div className="lw-step"><div className="n">60'</div><div className="t">{t.lwStep1.split('\n').map((s, i) => <span key={i}>{i > 0 && <br />}{s}</span>)}</div></div>
          <div className="lw-step"><div className="n">{vi ? 'XI' : '首发'}</div><div className="t">{t.lwStep2.split('\n').map((s, i) => <span key={i}>{i > 0 && <br />}{s}</span>)}</div></div>
          <div className="lw-step"><div className="n">AI</div><div className="t">{t.lwStep3.split('\n').map((s, i) => <span key={i}>{i > 0 && <br />}{s}</span>)}</div></div>
        </div>
        {lineupSimulated && match.liveCorrection ? (
          <p className="lw-body">
            <span className="hl">{t.lwCorrectionPrefix}</span>{vi ? noteVi(match.liveCorrection.trigger) : match.liveCorrection.trigger}{t.lwRecalcMid}
            {tn(match.homeTeam.name)} {t.lwRateWord} <span className="hl">{match.liveCorrection.before.home}% → {match.liveCorrection.after.home}% ▲</span>，
            {t.lwDrawWord} {match.liveCorrection.before.draw}% → {match.liveCorrection.after.draw}%，
            {tn(match.awayTeam.name)} {match.liveCorrection.before.away}% → {match.liveCorrection.after.away}%。
            <br />{t.lwReasonWord}{vi ? noteVi(match.liveCorrection.reason) : match.liveCorrection.reason}
          </p>
        ) : (
          <p className="lw-body">{t.lwBodyDefault}</p>
        )}
        <button className="lw-btn" style={{ marginTop: 12 }} onClick={handleSimulateLineup} disabled={lineupSimulated}>
          {lineupSimulated ? t.lwBtnDone : t.lwBtnDo}
        </button>
      </div>

      {/* ── 6. 付费解锁 / 社群引导 ────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.premiumTitle}</span>
        <span className="en">PREMIUM</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, fontWeight: 800, color: 'var(--blueMid)' }}>{t.premiumLocked}</span>
      </div>
      <div className="paywall">
        <div className="row gap8 mb12"><span>✨</span><span className="b">{t.premiumUnlockHint}</span></div>
        {ops.premiumTeaser.map(f => (
          <div className="feat" key={f}><span className="ck">✔</span>{vi ? premiumTeaserVi(f) : f}</div>
        ))}
        <div className="mt12">
          <button className="cta primary" onClick={handleUnlockCash}>{t.unlockCashLabel} · {price.singleUnlock}</button>
          <button className="cta ghost" onClick={handleUnlockToken}>
            {t.unlockMtcLabel} · {price.tokenUnlock}{t.balanceSuffix.replace('{balance}', String(balance))}
          </button>
          <button className="cta ghost" onClick={() => navigate('/community')}>{t.joinCommunityLabel} · {price.monthlyVip}</button>
        </div>
      </div>

      <div className="muted-note">{t.complianceFooter}</div>

      {modal && <Modal {...modal} onClose={() => setModal(null)} />}
    </div>
  );
}
