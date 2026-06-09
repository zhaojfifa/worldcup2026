import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { FeatureBars } from '../components/FeatureBars';
import { MatchHeader } from '../components/MatchHeader';
import { useCopy } from '../i18n/dict';
import { useLocale } from '../i18n/useLocale';
import { homeWinLoc, awayWinLoc, drawLoc, riskShortLoc, noteLoc, scoutHookLoc, contrarianLoc, watchLoc } from '../i18n/viMapping';

const RISK_COLORS = { low: 'var(--green)', medium: 'var(--amber)', high: 'var(--red)' };

function riskColor(v: number) {
  if (v >= 70) return 'var(--red)';
  if (v >= 45) return 'var(--amber)';
  return 'var(--green)';
}

export function ReportPage() {
  const navigate = useNavigate();
  const t = useCopy();
  const loc = useLocale();
  const { matches, selectedMatchId, setSelectedMatch, loadReport } = useAppStore();
  // Deep-link support: /report?match_id=8 (or ?id=8) → select that match (e.g. historical recap).
  const sp = new URLSearchParams(window.location.search);
  const urlMatchId = sp.get('match_id') || sp.get('id');
  const resolvedId = (urlMatchId && matches.some(m => m.id === urlMatchId)) ? urlMatchId : selectedMatchId;
  const match = matches.find(m => m.id === resolvedId) ?? matches[0];

  useEffect(() => {
    if (urlMatchId && matches.some(m => m.id === urlMatchId) && urlMatchId !== selectedMatchId) {
      setSelectedMatch(urlMatchId);
    }
  }, [urlMatchId, matches, selectedMatchId, setSelectedMatch]);

  useEffect(() => {
    if (resolvedId) loadReport(resolvedId);
  }, [resolvedId]);  // eslint-disable-line react-hooks/exhaustive-deps

  if (!match) return null;

  const hasTrend = match.trendHistory.length > 0;
  const maxTrend = hasTrend ? Math.max(...match.trendHistory.map(t => t.prob)) : 100;
  const conf = Math.round(match.confidence);

  // Derived risk-radar dimensions (visual only — no new API fields)
  const topFeature = match.features[0]?.value ?? 0;
  const radar = [
    { label: t.radarForm, value: conf },
    { label: t.radarSquad, value: match.liveCorrection ? 68 : 86 },
    { label: t.radarTactical, value: Math.min(92, Math.max(30, 50 + topFeature * 2)) },
    { label: t.radarLive, value: match.riskLevel === 'high' ? 80 : match.riskLevel === 'medium' ? 55 : 32 },
  ];

  return (
    <div className="page-enter">
      <div className="backbar">
        <button className="bk" onClick={() => navigate('/')}>←</button>
        <span className="ti">{t.reportBack}</span>
        <span style={{ marginLeft: 'auto', background: '#E3F4EA', color: 'var(--green)', display: 'inline-block', fontSize: 11, fontWeight: 800, padding: '5px 10px', borderRadius: 999 }}>
          {t.reportUnlocked}
        </span>
      </div>

      {/* Historical recap banner — finished match is calibration, not a current prediction */}
      {match.status === 'finished' && (
        <div className="recap-banner">🗂️ {t.recapDetailNote}</div>
      )}

      {/* Evidence strip — signal sources (labels only; provenance-tagged, no fabricated data) */}
      <div className="evidence-strip">
        <div className="ev-title">🛰️ {t.evidenceTitle}</div>
        <div className="ev-sources">{t.evidenceSources}</div>
        <div className="ev-mode">{match.status === 'finished' ? t.evidenceModeRecap : t.evidenceMode}</div>
      </div>

      {/* Scout verdict + gauge */}
      <div className="paywall" style={{ borderColor: 'rgba(30,158,90,.4)' }}>
        <div className="sec-en" style={{ marginTop: 0 }}>
          <span className="zh">{t.scoutVerdictTitle}</span>
          <span className="en">{t.scoutSub}</span>
        </div>
        <MatchHeader match={match} />
        <p className="scout-hook">{scoutHookLoc(match.homeTeam.name, match.awayTeam.name, loc)}</p>

        <div className="gauge-wrap mt12">
          <div className="gauge" style={{ background: `conic-gradient(var(--blue) ${conf * 3.6}deg, var(--line) 0)` }}>
            <div className="inner">
              <div className="gv">{conf}%</div>
              <div className="gl">{t.confIndex}</div>
            </div>
          </div>
          <div className="gauge-side">
            <div className="gs-row">
              <span><span className="dotc" style={{ background: 'var(--green)' }} />{homeWinLoc(match.homeTeam.name, loc)}</span>
              <b>{match.winProb.home}%</b>
            </div>
            <div className="gs-row">
              <span><span className="dotc" style={{ background: 'var(--amber)' }} />{drawLoc(loc)}</span>
              <b>{match.winProb.draw}%</b>
            </div>
            <div className="gs-row">
              <span><span className="dotc" style={{ background: 'var(--red)' }} />{awayWinLoc(match.awayTeam.name, loc)}</span>
              <b>{match.winProb.away}%</b>
            </div>
          </div>
        </div>

        <div className="stats">
          <div className="stat">
            <div className="v" style={{ color: 'var(--blueMid)' }}>{match.recommendedScore.split(' / ')[0] || '—'}</div>
            <div className="l">{t.recommendedScore}</div>
          </div>
          <div className="stat">
            <div className="v" style={{ color: RISK_COLORS[match.riskLevel] }}>{riskShortLoc(match.riskLevel, loc)}</div>
            <div className="l">{t.riskGrade}</div>
          </div>
          <div className="stat">
            <div className="v" style={{ color: 'var(--green)' }}>{conf}%</div>
            <div className="l">{t.confidence}</div>
          </div>
        </div>
      </div>

      {/* Key factor contribution */}
      {match.features.length > 0 && (
        <>
          <div className="sec-en">
            <span className="zh">{t.keyFactorsTitle}</span>
            <span className="en">KEY FACTORS</span>
          </div>
          <div className="card">
            <FeatureBars features={match.features} />
          </div>
        </>
      )}

      {/* Contrarian / Risk watch — the "why this could be wrong" angle */}
      <div className="sec-en">
        <span className="zh">{t.contrarianTitle}</span>
        <span className="en">CONTRARIAN</span>
      </div>
      <div className="card accent-amber">
        <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>
          ⚔️ {contrarianLoc(match.homeTeam.name, match.awayTeam.name, loc)}
        </p>
      </div>

      {/* What to watch before kickoff */}
      <div className="sec-en">
        <span className="zh">{t.watchTitle}</span>
        <span className="en">WATCH</span>
      </div>
      <div className="card">
        <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>
          👁️ {watchLoc(match.homeTeam.name, match.awayTeam.name, loc)}
        </p>
      </div>

      {/* Risk radar */}
      <div className="sec-en">
        <span className="zh">{t.riskRadarTitle}</span>
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
          {t.radarNote}
        </p>
      </div>

      {/* Tactics explanation */}
      {match.tacticsNote && (
        <>
          <div className="sec-en">
            <span className="zh">{t.tacticsTitle}</span>
            <span className="en">TACTICS</span>
          </div>
          <div className="card">
            <p className="small" style={{ color: '#3A4A60', lineHeight: 1.75 }}>{noteLoc(match.tacticsNote, loc)}</p>
          </div>
        </>
      )}

      {/* Trend chart */}
      {hasTrend && (
        <>
          <div className="sec-en">
            <span className="zh">{t.trendTitle}</span>
            <span className="en">PROB TREND</span>
          </div>
          <div className="card">
            <div className="trend">
              {match.trendHistory.map((pt, i) => {
                const h = Math.round((pt.prob / maxTrend) * 100);
                const isLast = i === match.trendHistory.length - 1;
                return (
                  <div className="col" key={pt.label}>
                    <span className="pv" style={{ color: isLast ? 'var(--blue)' : 'var(--blueMid)' }}>{pt.prob}%</span>
                    <div className="barv" style={{ height: h, background: isLast ? 'var(--blue)' : 'var(--blueLight)' }} />
                    <span className="pt">{noteLoc(pt.label, loc)}</span>
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
            <span className="zh">{t.lwLogTitle}</span>
            <span className="en">LINEUP WATCH LOG</span>
          </div>
          <div className="card accent-blue">
            <div className="row gap8 mb12">
              <span>🔔</span>
              <span className="b small">{noteLoc(match.liveCorrection.trigger, loc)}</span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{homeWinLoc(match.homeTeam.name, loc)} {t.lwRateWord}</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.home}%</span>{' → '}
                <span style={{ color: 'var(--green)' }}>{match.liveCorrection.after.home}% ▲</span>
              </span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{t.lwDrawProb}</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.draw}%</span>{' → '}
                <span style={{ color: 'var(--red)' }}>{match.liveCorrection.after.draw}% ▼</span>
              </span>
            </div>
            <div className="crow">
              <span className="small" style={{ color: '#3A4A60' }}>{awayWinLoc(match.awayTeam.name, loc)} {t.lwRateWord}</span>
              <span className="b small">
                <span className="sub">{match.liveCorrection.before.away}%</span>{' → '}
                <span style={{ color: 'var(--red)' }}>{match.liveCorrection.after.away}% ▼</span>
              </span>
            </div>
            <p className="xs sub mt12" style={{ lineHeight: 1.7 }}>
              {t.lwChangeReason}{noteLoc(match.liveCorrection.reason, loc)}
            </p>
          </div>
        </>
      )}

      <button className="cta primary" onClick={() => navigate('/community')}>
        {t.reportSubscribeCta}
      </button>
      <div className="muted-note">{t.complianceFooter}</div>
    </div>
  );
}
