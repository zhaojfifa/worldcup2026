import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { WinBar } from '../components/WinBar';
import { toast } from '../components/Toast';
import { deriveOps, pickTopSignal, topUpsets } from '../ops/derive';
import { HOME, BRAND } from '../copy/zh';
import { useCopy } from '../i18n/dict';
import { useLocale } from '../i18n/useLocale';
import { teamLoc, homeWinLoc, awayWinLoc, aiPickLoc, heatLoc, riskShortLoc, noteLoc } from '../i18n/viMapping';
import { api, safeTrack, type ApiCommunityHeat } from '../api/client';
import { RECAP_AVAILABLE, recapFixtureId } from '../data/recapData';
import { UpcomingTacticalStrip, TrialHeroCard, TrialStatusStrip, HotTopicsSection, RescoreHookCard, RecapAnchorCard } from '../components/UpcomingTacticalStrip';
import { getProductNarrative } from '../data/productNarrativeData';
import { pickActiveFixture } from '../lib/freshness';
import { activeFixtureEntries } from '../data/dailyFixtures';
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

export function HomePage() {
  const navigate = useNavigate();
  const t = useCopy();
  const loc = useLocale();
  // Locale-aware helpers for dynamic data (zh→original, vi→Vietnamese, else→English).
  const tn = (name: string) => teamLoc(name, loc);
  const pick = (zh: string) => aiPickLoc(zh, loc);
  const heatLbl = (zh: string) => heatLoc(zh, loc);
  const note = (zh: string) => noteLoc(zh, loc);
  const riskShort = (lvl: string) => riskShortLoc(lvl, loc);
  const homeWinLabel = (m: Match) => homeWinLoc(m.homeTeam.name, loc);
  const awayWinLabel = (m: Match) => awayWinLoc(m.awayTeam.name, loc);
  const hook = (score: number) =>
    score >= 60 ? t.upsetHookHigh : score >= 40 ? t.upsetHookMid : t.upsetHookLow;
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
    navigate('/detail?demo=1'); // demo escape: trial /detail redirects to the real tactical room
  }

  async function handleCheckIn() {
    if (checkedIn) { toast(t.checkinToastDone); return; }
    await checkIn();
    toast(t.checkinToastOk);
  }

  const syncTime = new Date(syncedAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  // Separate CURRENT operational matches from HISTORICAL finished matches (e.g. synced WC-2022).
  // Current = not finished (seed scheduled has status undefined → treated as current).
  const currentMatches = matches.filter(m => m.status !== 'finished');
  const historicalMatches = matches.filter(m => m.status === 'finished');
  // Prefer the selected WC-2022 recap candidates (id 8/13/58/67), else the first few finished.
  const RECAP_IDS = ['8', '13', '58', '67'];
  const recapMatches = [
    ...RECAP_IDS.map(id => historicalMatches.find(m => m.id === id)).filter((m): m is Match => !!m),
    ...historicalMatches.filter(m => !RECAP_IDS.includes(m.id)),
  ].slice(0, 4);
  const modelCount = currentMatches.length;
  const liveCount = currentMatches.filter(m => m.tag === 'live').length;

  if (matchesLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'var(--sub)' }}>
        <div style={{ fontSize: 30, marginBottom: 12 }}>⚽</div>
        <div className="small">{t.loadingText}</div>
      </div>
    );
  }

  const signal = pickTopSignal(currentMatches);
  if (!signal) return null;

  const sOps = deriveOps(signal);
  const upsets = topUpsets(currentMatches, 3);

  return (
    <div className="page-enter">
      {/* ── AI Intelligence Ticker ───────────────────────────────── */}
      <div className="ai-ticker">
        <span className="live-dot" />
        <span className="tick-label">{t.aiTicker}</span>
        <div className="tick-track">
          <span className="tick-move">
            {t.tickerBody
              .replace('{n}', String(modelCount))
              .replace('{live}', String(liveCount || 1))
              .replace('{time}', syncTime)}
          </span>
        </div>
      </div>

      {/* ── June-11 trial: persona status strip ─────────────────────── */}
      <TrialStatusStrip loc={loc} syncTime={syncTime} />

      {/* ── Hero ──────────────────────────────────────────────────── */}
      <div className="hero-banner">
        <div className="hero-kicker">GIÀNH CUP</div>
        <div className="hero-title">
          {loc === 'zh' ? <>俅哥<span className="accent">说球</span></> : <>{t.heroTitlePre}<span className="accent">{t.heroTitleAccent}</span></>}
        </div>
        <div className="hero-en">{BRAND.heroEn}</div>
        <div className="hero-sub hero-persona">
          {loc === 'zh' ? '世界杯赛前判断 · 临场 30 分钟修正'
            : loc === 'vi' ? 'Nhận định trước trận của Tiên Tri Bóng Đá'
              : loc === 'my' ? 'Football Oracle ၏ World Cup ပွဲကြိုအမြင်'
                : 'Giành Cup pre-match scout model'}
        </div>
        <div className="hero-sub">
          {loc === 'zh' ? '不只看胜率，更看为什么这样判断。'
            : loc === 'vi' ? 'Không chỉ xem ai thắng, hãy hiểu vì sao Tiên Tri nhận định như vậy.'
              : loc === 'my' ? 'ဘယ်သူနိုင်မလဲထက် ဘာကြောင့် ဒီလိုမြင်လဲကပါ အရေးကြီးသည်။'
                : 'Not just who wins — why the call.'}
        </div>
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
          {t.apiErrorCache}
        </div>
      )}

      {/* ── ACTIVE 2026 LOOP (Owner §6 · P1.2b runtime freshness · P1.3 registry-sourced) ──
           Hero is SELECTED at runtime from the daily fixture registry manifest (no permanent
           hardcoded fixture): live → earliest pre-match → latest recap-ready → recap-pending →
           empty. recapReady is recomputed LIVE from the bundled narrative, never trusted stale.
           A finished/live fixture can never be pinned as today's pre-match prediction. */}
      {(() => {
        const entries = activeFixtureEntries();
        const active = pickActiveFixture(entries.map(e => ({
          id: e.id, kickoffUtc: e.kickoffUtc,
          recapReady: getProductNarrative(e.id, loc)?.mode === 'real_recap',
        })));
        // latest recap-ready fixture for the trust anchor (guarded by mode internally)
        const recapAnchorId = [...entries]
          .filter(e => getProductNarrative(e.id, loc)?.mode === 'real_recap')
          .sort((a, b) => new Date(b.kickoffUtc ?? 0).getTime() - new Date(a.kickoffUtc ?? 0).getTime())[0]?.id;
        if (active.mode === 'empty' && !recapAnchorId) {
          return (
            <div className="card th-hero">
              <div className="th-badge">{loc === 'zh' ? '今日暂无可用赛前情报'
                : loc === 'vi' ? 'Hôm nay chưa có tin trước trận khả dụng'
                  : loc === 'my' ? 'ဒီနေ့ အသုံးပြုနိုင်သော ပွဲကြိုသတင်း မရှိသေးပါ'
                    : 'No active pre-match intel today'}</div>
            </div>
          );
        }
        return (
          <>
            {active.heroId && <TrialHeroCard loc={loc} fixtureId={active.heroId} />}
            <UpcomingTacticalStrip loc={loc} excludeId={active.heroId ?? undefined} />
            <HotTopicsSection loc={loc} />
            {active.mode === 'pre_match' && active.heroId && <RescoreHookCard loc={loc} fixtureId={active.heroId} />}
            {recapAnchorId && <RecapAnchorCard loc={loc} fixtureId={recapAnchorId} />}
          </>
        );
      })()}
      <div className="card" style={{ textAlign: 'center' }}>
        <div className="ra-line">
          {loc === 'zh' ? '进群等临场修正——首发公布后，俅哥重新看一遍再给最终倾向。'
            : loc === 'vi' ? 'Vào nhóm chờ hiệu chỉnh sát giờ — đội hình công bố xong, Tiên Tri xem lại rồi mới chốt thiên hướng cuối.'
              : loc === 'my' ? 'အဖွဲ့ဝင်ပြီး ပွဲနီးပြန်တွက်ချက် စောင့်ပါ — lineup ထွက်ပြီးမှ Oracle နောက်ဆုံးအမြင် ပေးမည်။'
                : 'Join the group for the late re-check — final lean lands after lineups.'}
        </div>
        <button className="recap-cta-btn" style={{ width: '100%' }} onClick={() => navigate('/community')}>
          {loc === 'zh' ? '加入情报群 ▸' : loc === 'vi' ? 'Vào nhóm tin báo ▸' : loc === 'my' ? 'အဖွဲ့ဝင်ရန် ▸' : 'Join the group ▸'}
        </button>
      </div>

      {/* ── ARCHIVE: WC2022 recap library (trust archive, below the active loop) ── */}
      {recapMatches.length > 0 && (
        <>
          <div className="sec-en">
            <span className="zh">{loc === 'zh' ? '俅哥复盘档案 · WC2022' : loc === 'vi' ? 'Kho phục dựng của Tiên Tri · WC2022' : loc === 'my' ? 'Oracle ပြန်သုံးသပ်မှတ်တမ်း · WC2022' : 'Recap archive · WC2022'}</span>
            <span className="en">RECAP ARCHIVE</span>
          </div>
          <div className="card recap-card">
            <div className="recap-sub">🗂️ {t.recapSectionSub}</div>
            <div className="recap-bridge">
              {loc === 'zh'
                ? '俅哥不只给赛前判断，也复盘自己为什么看对或看漏，用真实数据修正下一次判断。'
                : loc === 'vi'
                  ? 'Tiên Tri không chỉ đưa nhận định trước trận, mà còn xem lại vì sao mình đúng hay bỏ sót, dùng dữ liệu thật để chỉnh lần nhận định sau.'
                  : loc === 'my'
                    ? 'Oracle သည် ပွဲကြိုအမြင်ပေးရုံသာမက ဘာမှန်ခဲ့/ဘာလွဲခဲ့လဲကိုပါ ပြန်သုံးသပ်ပြီး တကယ့်ဒေတာဖြင့် နောက်တစ်ကြိမ်အမြင်ကို ပြင်သည်။'
                    : 'We don’t just call matches pre-game — we recap why the model was right or wrong, and correct the next version with real data.'}
            </div>
            {recapMatches.map((m: Match) => {
              const rid = recapFixtureId(m);
              const hasRecap = !!rid && RECAP_AVAILABLE.has(rid);
              const recapCta = loc === 'zh' ? '查看复盘 ▸' : loc === 'vi' ? 'Xem phục dựng ▸' : loc === 'my' ? 'ပြန်ကြည့်ရန် ▸' : 'View recap ▸';
              return (
                <div className="recap-row" key={m.id}
                     onClick={() => (hasRecap ? navigate(`/recap/${rid}`) : goDetail(m.id))}>
                  <span className="recap-badge">{t.recapBadge}</span>
                  <span className="recap-teams">{m.homeTeam.flag} {tn(m.homeTeam.name)} vs {tn(m.awayTeam.name)} {m.awayTeam.flag}</span>
                  {hasRecap && <span className="recap-go">{recapCta}</span>}
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* ── demo fold: legacy mock blocks (demoted — internal demo data) ── */}
      <details className="card home-demo-fold">
        <summary>
          {loc === 'zh' ? '内部演示数据（mock 比赛 · 点击展开）'
            : loc === 'vi' ? 'Dữ liệu demo nội bộ (trận mock · nhấn để mở)'
              : loc === 'my' ? 'အတွင်းပိုင်း demo ဒေတာ (mock ပွဲများ · ဖွင့်ကြည့်ရန်)'
                : 'Internal demo data (mock matches · expand)'}
        </summary>

      {/* ── demo 1. 今日 AI 最强信号 (mock) ─────────────────────────── */}
      <div className="signal-card" onClick={() => goDetail(signal.id)}>
        <div className="signal-head">
          <span className="signal-badge">⭐ {t.signalTitle}</span>
          <span className="signal-en">{BRAND.signalTag}</span>
        </div>
        <div className="signal-teams">
          <div className="t"><div className="fl">{signal.homeTeam.flag}</div><div className="nm">{tn(signal.homeTeam.name)}</div></div>
          <div className="vs">VS</div>
          <div className="t"><div className="fl">{signal.awayTeam.flag}</div><div className="nm">{tn(signal.awayTeam.name)}</div></div>
        </div>
        <div className="signal-row">
          <span className="signal-tend">{t.tendency}：{pick(sOps.aiPickLabel)}</span>
          <span className="signal-star">{sOps.confidenceStars}</span>
        </div>
        <div style={{ margin: '4px 0 10px' }}>
          <WinBar prob={signal.winProb} homeLabel={homeWinLabel(signal)} awayLabel={awayWinLabel(signal)} />
        </div>
        <div className="signal-risk">⚠️ {t.topRisk}：{note(sOps.topRisk)}</div>
        <div className="signal-cta">
          <span className="b1" onClick={(e) => { e.stopPropagation(); goDetail(signal.id); }}>{t.ctaView}</span>
          <span className="b2" onClick={(e) => { e.stopPropagation(); goDetail(signal.id); }}>{t.ctaUnlock}</span>
        </div>
      </div>

      {/* ── demo 2. 今日比赛简表 (mock) ─────────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.listTitle}</span>
        <span className="en">{HOME.listEn}</span>
        <span style={{ marginLeft: 'auto' }} className="src-pill"><span className="sync-dot" />{t.syncLabel} {syncTime}</span>
      </div>
      {currentMatches.map((m: Match) => {
        const ops = deriveOps(m);
        return (
          <div className="simrow" key={m.id} onClick={() => goDetail(m.id)}>
            <div className="time">{fmtDate(m.kickoffTime)}<br />{fmtTime(m.kickoffTime)}</div>
            <div className="teams">{m.homeTeam.flag} {tn(m.homeTeam.name)}<span className="vs">vs</span>{tn(m.awayTeam.name)} {m.awayTeam.flag}</div>
            <div className="chips">
              <span className="tend">{pick(ops.aiPickLabel)}</span>
              <span className={`risk-chip ${m.riskLevel}`}>{riskShort(m.riskLevel)}</span>
              <span className="heat-chip">{heatLbl(ops.heatLabel)}</span>
            </div>
          </div>
        );
      })}

      {/* ── demo 3. 今日爆冷风险 TOP3 (mock) ────────────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.upsetTitle}</span>
        <span className="en">{HOME.upsetEn}</span>
      </div>
      {upsets.map((u, i) => (
        <div className="upset-item" key={u.match.id} onClick={() => goDetail(u.match.id)}>
          <div className="upset-rank">{i + 1}</div>
          <div className="upset-body">
            <div className="upset-match">{u.match.homeTeam.flag} {tn(u.match.homeTeam.name)} vs {tn(u.match.awayTeam.name)} {u.match.awayTeam.flag}</div>
            <div className="upset-hook">⚠️ {hook(u.score)}</div>
          </div>
          <div className="upset-score">
            <div className="v">{u.score}</div>
            <div className="l">{t.upsetScoreLabel}</div>
          </div>
        </div>
      ))}
      {/* ── demo 4. AI 情报战绩 (pending placeholder) ────────────────── */}
      <div className="sec-en">
        <span className="zh">{t.recordTitle}</span>
        <span className="en">{HOME.recordEn}</span>
      </div>
      <div className="status-card">
        <div className="ic">📊</div>
        <div className="st">{t.recordPending}</div>
        <div className="sub2">{t.recordSub}</div>
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
                <div className="upset-match">{tn(m.home)} vs {tn(m.away)}</div>
                <div className="upset-hook" style={{ color: 'var(--blueMid)' }}>{t.heatAttention}</div>
              </div>
              <div className="upset-score">
                <div className="v" style={{ color: 'var(--blueMid)' }}>{m.interactions}</div>
                <div className="l">{t.interactions}</div>
              </div>
            </div>
          ))}
          <div className="disclaimer-line" style={{ textAlign: 'center' }}>{t.heatNote}</div>
        </>
      ) : (
        <div className="status-card">
          <div className="ic">🔥</div>
          <div className="st">{t.heatComingSoon}</div>
          <div className="sub2">{t.heatSub}</div>
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
          <div className="ic">🪙</div><div className="nm">{t.loopFanPoints}</div><div className="ds">{t.loopDailyCheckin}</div>
        </div>
        <div className="loop-tile" onClick={() => navigate('/token')}>
          <div className="ic">🎯</div><div className="nm">{t.loopStreak}</div><div className="ds">{t.loopFreeJoin}</div>
        </div>
        <div className="loop-tile" onClick={() => toast(t.rankingComingToast)}>
          <div className="ic">🏅</div><div className="nm">{t.loopRanking}</div><div className="ds">{t.loopComingSoon}</div>
        </div>
      </div>
      <div className="compliance">{t.mtcStatement}</div>
      </details>

      <div className="muted-note">{t.complianceFooter}</div>
    </div>
  );
}
