import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { MatchHeader } from '../components/MatchHeader';
import { EvidencePack } from '../components/EvidencePack';
import { Modal } from '../components/Modal';
import { toast } from '../components/Toast';
import { deriveOps, reasonBullets } from '../ops/derive';
import { useCopy } from '../i18n/dict';
import { useLocale } from '../i18n/useLocale';
import { getPrice } from '../i18n/pricing';
import {
  teamLoc, homeWinLoc, awayWinLoc, aiPickLoc, riskLongLoc, riskShortLoc,
  riskTagLoc, noteLoc, premiumTeaserLoc, reasonBulletsLoc,
  scoutHookLoc, contrarianLoc,
} from '../i18n/viMapping';

const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };
const RISK_BG     = { low: '#E3F4EA',     medium: '#FFF6E2',       high: '#FEE8E9' };
const STAR_COLOR  = { low: '#8DF2B6', medium: '#FFD27A', high: '#FFAEB2' };

export function DetailPage() {
  const navigate = useNavigate();
  const t = useCopy();
  const loc = useLocale();
  const price = getPrice(loc);
  const tn = (name: string) => teamLoc(name, loc);
  const {
    balance, matches, selectedMatchId, setSelectedMatch,
    loadDetail, unlockWithCash, unlockWithToken, simulateCorrection,
  } = useAppStore();

  // Deep-link support: /detail?match_id=8 (or ?id=8) → select that match (e.g. historical recap).
  // No API change; reads from the already-loaded /matches list, falls back to current selection.
  const sp = new URLSearchParams(window.location.search);
  const urlMatchId = sp.get('match_id') || sp.get('id');
  const resolvedId = (urlMatchId && matches.some(m => m.id === urlMatchId)) ? urlMatchId : selectedMatchId;
  const match = matches.find(m => m.id === resolvedId) ?? matches[0];
  const [modal, setModal] = useState<null | { em: string; title: string; body: string; okLabel: string; onOk: () => void }>(null);
  const [lineupSimulated, setLineupSimulated] = useState(!!match?.liveCorrection);

  useEffect(() => {
    if (urlMatchId && matches.some(m => m.id === urlMatchId) && urlMatchId !== selectedMatchId) {
      setSelectedMatch(urlMatchId);
    }
  }, [urlMatchId, matches, selectedMatchId, setSelectedMatch]);

  useEffect(() => {
    if (resolvedId) loadDetail(resolvedId);
  }, [resolvedId]);  // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (match?.liveCorrection) setLineupSimulated(true);
  }, [match?.liveCorrection]);

  if (!match) return null;

  // Recap / finished match → no detailed model report. Show the Evidence Pack
  // (data-status) and suppress live-prediction sections; keep the honest basics.
  const reportIncomplete = match.status === 'finished';

  const ops = deriveOps(match);
  const bullets = loc === 'zh' ? reasonBullets(match) : reasonBulletsLoc(match, loc);
  const riskLevel = match.riskLevel;
  const riskLong = riskLongLoc(riskLevel, loc);
  const riskGrade = riskShortLoc(riskLevel, loc);

  async function handleUnlockCash() {
    const res = await unlockWithCash(match.id);
    // Display copy is locale-driven (never the raw store/API message, which may be Chinese).
    setModal({
      em: '💳',
      title: res.success ? t.payOkTitle : t.payFailTitle,
      body: res.success ? t.unlockedBody : t.unlockFailedBody,
      okLabel: t.continueToReport,
      onOk: () => { if (res.success) navigate('/report'); },
    });
  }

  async function handleUnlockToken() {
    if (balance < 390) { toast(t.mtcInsufficient); return; }
    const res = await unlockWithToken(match.id);
    if (!res.success) { toast(t.unlockFailedBody); return; }
    setModal({
      em: '🪙',
      title: t.mtcDeductedTitle,
      body: t.unlockedBody,
      okLabel: t.continueToReport,
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

      {/* Historical recap banner — finished match is calibration, not a current prediction */}
      {match.status === 'finished' && (
        <div className="recap-banner">🗂️ {t.recapDetailNote}</div>
      )}

      {/* Condensed evidence strip (signal sources — labels only) */}
      <div className="evidence-strip compact">
        <div className="ev-title">🛰️ {t.evidenceTitle}</div>
        <div className="ev-sources">{t.evidenceSources}</div>
      </div>

      {/* Evidence Pack — recap / detailed report not generated (no fake full report) */}
      {reportIncomplete && <EvidencePack />}

      {/* ── 1. Scout 结论卡（置顶） ──────────────────────────────────── */}
      <div className="verdict-card">
        <div className="verdict-top">
          <span className="zh">🔮 {t.scoutVerdictTitle}</span>
          <span className="en">{t.scoutSub}</span>
        </div>
        <p className="scout-hook">{reportIncomplete ? t.scoutHookRecap : scoutHookLoc(match.homeTeam.name, match.awayTeam.name, loc)}</p>
        <div className="verdict-grid">
          <div className="verdict-cell">
            <div className="l">{t.tendency}</div>
            <div className="v">{aiPickLoc(ops.aiPickLabel, loc)}</div>
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
        <WinBar prob={match.winProb} homeLabel={homeWinLoc(match.homeTeam.name, loc)} awayLabel={awayWinLoc(match.awayTeam.name, loc)} />
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
          <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75, marginBottom: 10 }}>{noteLoc(match.freeNote, loc)}</p>
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
          {ops.riskTags.map(tag => <span className="risk-tag" key={tag}>{riskTagLoc(tag, loc)}</span>)}
        </div>
        {match.riskNote && (
          <p className="xs sub" style={{ marginTop: 10, lineHeight: 1.7 }}>{noteLoc(match.riskNote, loc)}</p>
        )}
      </div>

      {/* LINEUP WATCH + Contrarian — live-prediction depth; hidden on recap (a 2022 match must not simulate a live correction) */}
      {!reportIncomplete && (
      <>
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
          <div className="lw-step"><div className="n">{loc === 'zh' ? '首发' : 'XI'}</div><div className="t">{t.lwStep2.split('\n').map((s, i) => <span key={i}>{i > 0 && <br />}{s}</span>)}</div></div>
          <div className="lw-step"><div className="n">AI</div><div className="t">{t.lwStep3.split('\n').map((s, i) => <span key={i}>{i > 0 && <br />}{s}</span>)}</div></div>
        </div>
        {lineupSimulated && match.liveCorrection ? (
          <p className="lw-body">
            <span className="hl">{t.lwCorrectionPrefix}</span>{noteLoc(match.liveCorrection.trigger, loc)}{t.lwRecalcMid}
            {tn(match.homeTeam.name)} {t.lwRateWord} <span className="hl">{match.liveCorrection.before.home}% → {match.liveCorrection.after.home}% ▲</span>，
            {t.lwDrawWord} {match.liveCorrection.before.draw}% → {match.liveCorrection.after.draw}%，
            {tn(match.awayTeam.name)} {match.liveCorrection.before.away}% → {match.liveCorrection.after.away}%。
            <br />{t.lwReasonWord}{noteLoc(match.liveCorrection.reason, loc)}
          </p>
        ) : (
          <p className="lw-body">{t.lwBodyDefault}</p>
        )}
        <button className="lw-btn" style={{ marginTop: 12 }} onClick={handleSimulateLineup} disabled={lineupSimulated}>
          {lineupSimulated ? t.lwBtnDone : t.lwBtnDo}
        </button>
      </div>

      {/* Contrarian teaser — drives unlock/community (compliant, no betting) */}
      <div className="card accent-amber" style={{ marginTop: 14 }}>
        <div className="sec-en" style={{ marginTop: 0 }}>
          <span className="zh">{t.contrarianTitle}</span>
          <span className="en">CONTRARIAN</span>
        </div>
        <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75, marginTop: 6 }}>
          ⚔️ {contrarianLoc(match.homeTeam.name, match.awayTeam.name, loc)}
        </p>
      </div>
      </>
      )}

      {/* ── 6. 付费解锁 / 社群引导 ────────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.premiumTitle}</span>
        <span className="en">PREMIUM</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, fontWeight: 800, color: 'var(--blueMid)' }}>{t.premiumLocked}</span>
      </div>
      <div className="paywall">
        <div className="row gap8 mb12"><span>✨</span><span className="b">{t.premiumUnlockHint}</span></div>
        {ops.premiumTeaser.map(f => (
          <div className="feat" key={f}><span className="ck">✔</span>{premiumTeaserLoc(f, loc)}</div>
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
