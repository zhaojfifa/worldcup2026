import { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { MOCK_SHOP } from '../data/mock';
import { toast } from '../components/Toast';
import { api, type ApiStreak, type ApiRankings } from '../api/client';
import { useCopy } from '../i18n/dict';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const DEMO_USER_ID = 1;

// Shop label keys → copy keys (labels come from MOCK_SHOP in Chinese).
const SHOP_LABEL_KEY: Record<string, 'shopReport' | 'shopCommunity7' | 'shopFreepass'> = {
  '单场 AI 深度报告': 'shopReport',
  '7 天社群体验': 'shopCommunity7',
  '单场免单券': 'shopFreepass',
};

export function TokenPage() {
  const t = useCopy();
  const { balance, tasks, checkIn, completeTask, spendToken, syncedAt } = useAppStore();
  // Mission copy keyed by task id (localized).
  const MISSION_COPY: Record<string, { title: string; desc: string }> = {
    checkin: { title: t.missionCheckinT, desc: t.missionCheckinD },
    share:   { title: t.missionShareT,   desc: t.missionShareD },
    invite:  { title: t.missionInviteT,  desc: t.missionInviteD },
  };
  const [challengeJoined, setChallengeJoined] = useState<'A' | 'B' | null>(null);
  const [streak, setStreak] = useState<ApiStreak | null>(null);
  const [rankings, setRankings] = useState<ApiRankings | null>(null);

  // Streak + rankings load (API mode only; fallback shows building state).
  useEffect(() => {
    if (USE_MOCK) return;
    api.getUserStreak(DEMO_USER_ID).then(setStreak).catch(() => { /* building state */ });
    api.getRankings().then(setRankings).catch(() => { /* building state */ });
  }, []);

  async function handleTask(taskId: string) {
    if (taskId === 'checkin') {
      const task = tasks.find(x => x.id === 'checkin');
      if (task?.done) { toast(t.checkinToastDone); return; }
      await checkIn();
      toast(t.checkinToastOk);
    } else {
      const task = tasks.find(x => x.id === taskId);
      if (!task || task.done) return;
      completeTask(taskId);
      toast(`+${task.reward} MTC`);
    }
  }

  function joinChallenge(opt: 'A' | 'B') {
    if (challengeJoined) return;
    setChallengeJoined(opt);
    toast(t.challengeJoinedToast);
  }

  function handleSpend(cost: number) {
    const ok = spendToken(cost);
    if (!ok) { toast(t.tokenInsufficient); return; }
    toast(`-${cost} MTC ✓`);
  }

  const syncTime = new Date(syncedAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

  return (
    <div className="page-enter">
      <div className="backbar"><span className="ti">{t.tokenBack}</span></div>

      {/* Balance hero */}
      <div className="bigcard">
        <div className="hero-kicker" style={{ color: 'var(--gold)' }}>MTC FAN MISSION CENTER</div>
        <div className="lbl" style={{ marginTop: 6 }}>{t.walletLabel}</div>
        <div className="val">{balance}</div>
        <div className="xs" style={{ color: '#C5E0F6', marginTop: 4 }}>{t.lastUpdate} {syncTime}</div>
      </div>

      {/* Fan streak */}
      <div className="sec-en">
        <span className="zh">{t.myStreak}</span>
        <span className="en">FAN STREAK</span>
      </div>
      {streak && (streak.current_streak > 0 || streak.best_streak > 0 || streak.mtc_earned > 0) ? (
        <div className="card">
          <div className="stats">
            <div className="stat"><div className="v" style={{ color: 'var(--blueMid)' }}>{streak.current_streak}</div><div className="l">{t.curStreak}</div></div>
            <div className="stat"><div className="v" style={{ color: 'var(--gold)' }}>{streak.best_streak}</div><div className="l">{t.bestStreak}</div></div>
            <div className="stat"><div className="v" style={{ color: 'var(--green)' }}>{streak.mtc_earned}</div><div className="l">{t.challengeMtc}</div></div>
          </div>
          <div className="disclaimer-line" style={{ textAlign: 'center' }}>{t.disclaimer}</div>
        </div>
      ) : (
        <div className="status-card">
          <div className="ic">🎯</div>
          <div className="st">{t.streakBuilding}</div>
          <div className="sub2">{t.streakBuildingSub}</div>
          <div className="disclaimer-line">{t.disclaimer}</div>
        </div>
      )}

      {/* Daily missions */}
      <div className="sec-en">
        <span className="zh">{t.dailyMissions}</span>
        <span className="en">DAILY MISSIONS</span>
      </div>
      {tasks.map(task => {
        const copy = MISSION_COPY[task.id] ?? { title: task.label, desc: '' };
        return (
          <div className={`mission ${task.done ? 'done' : ''}`} key={task.id}>
            <div className="m-ic">{task.done ? '✅' : task.icon}</div>
            <div className="m-body">
              <div className="m-title">{copy.title}</div>
              <div className="m-desc">{copy.desc}</div>
            </div>
            <button
              className={`m-reward ${task.done ? 'done' : ''}`}
              onClick={() => handleTask(task.id)}
              disabled={task.done}
            >
              {task.done ? t.missionDone : `+${task.reward}`}
            </button>
          </div>
        );
      })}

      {/* Prediction challenge */}
      <div className="sec-en">
        <span className="zh">{t.predictionChallenge}</span>
        <span className="en">PREDICTION CHALLENGE</span>
      </div>
      <div className="card">
        <div className="b small mb8">{t.challengeTitle}</div>
        <div className="xs sub" style={{ marginBottom: 14 }}>
          {t.challengeQ}
        </div>
        <div className="row gap8">
          <button
            className={`opt ${challengeJoined === 'A' ? 'sel' : ''}`}
            onClick={() => joinChallenge('A')}
            disabled={!!challengeJoined}
          >{t.challengeYes}</button>
          <button
            className={`opt ${challengeJoined === 'B' ? 'sel' : ''}`}
            onClick={() => joinChallenge('B')}
            disabled={!!challengeJoined}
          >{t.challengeNo}</button>
        </div>
        {challengeJoined && (
          <div className="xs mt12" style={{ color: 'var(--green)', fontWeight: 800 }}>
            {t.challengeJoinedMsgPre}{challengeJoined === 'A' ? t.challengeYes : t.challengeNo}{t.challengeJoinedMsgPost}
          </div>
        )}
      </div>

      {/* Shop */}
      <div className="sec-en">
        <span className="zh">{t.shopTitle}</span>
        <span className="en">MTC SHOP</span>
      </div>
      {MOCK_SHOP.map(item => (
        <div className="shopitem" key={item.id}>
          <span className="row gap8 small"><span>{item.icon}</span>{SHOP_LABEL_KEY[item.label] ? t[SHOP_LABEL_KEY[item.label]] : item.label}</span>
          <button className="shopbtn" onClick={() => handleSpend(item.cost)}>
            {item.cost} MTC
          </button>
        </div>
      ))}

      {/* Rankings */}
      <div className="sec-en">
        <span className="zh">{t.rankingsTitle}</span>
        <span className="en">RANKINGS</span>
      </div>
      {rankings && rankings.top_users.length > 0 ? (
        <div className="card" style={{ padding: 6 }}>
          {rankings.top_users.map(u => (
            <div className="task" key={u.rank}>
              <span className="l">
                <span style={{ color: u.rank <= 3 ? 'var(--gold)' : 'var(--sub)', fontWeight: 800 }}>#{u.rank}</span>
                {u.display_name}
              </span>
              <span className="xs" style={{ fontWeight: 800, color: 'var(--blueMid)' }}>
                {t.rankStreakWord} {u.current_streak} · {u.mtc_earned} MTC
              </span>
            </div>
          ))}
          <div className="disclaimer-line" style={{ textAlign: 'center', padding: '6px 8px' }}>
            {t.rankingsDisclaimerPre}{t.disclaimer}
          </div>
        </div>
      ) : (
        <div className="status-card">
          <div className="ic">🏅</div>
          <div className="st">{t.rankingsBuilding}</div>
          <div className="sub2">{t.rankingsBuildingSub}</div>
        </div>
      )}

      <div className="compliance">
        {t.tokenMtcCompliance}
      </div>
      <div className="muted-note">{t.complianceFooter}</div>
    </div>
  );
}
