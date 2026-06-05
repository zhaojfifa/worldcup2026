import { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { MOCK_SHOP } from '../data/mock';
import { toast } from '../components/Toast';
import { api, type ApiStreak, type ApiRankings } from '../api/client';
import { DISCLAIMER_RECORD } from '../copy/zh';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const DEMO_USER_ID = 1;

// Gamified mission copy, keyed by task id
const MISSION_COPY: Record<string, { title: string; desc: string }> = {
  checkin: { title: '每日签到', desc: '点亮今日比赛日，保持情报在线' },
  share:   { title: '分享预测卡', desc: '带好友进入情报站' },
  invite:  { title: '邀请好友注册', desc: '扩列你的情报小队' },
};

export function TokenPage() {
  const { balance, tasks, checkIn, completeTask, spendToken, syncedAt } = useAppStore();
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
      const task = tasks.find(t => t.id === 'checkin');
      if (task?.done) { toast('今日已点亮比赛日'); return; }
      await checkIn();
      toast('签到成功 +10 MTC');
    } else {
      const task = tasks.find(t => t.id === taskId);
      if (!task || task.done) return;
      completeTask(taskId);
      toast(`任务完成 +${task.reward} MTC`);
    }
  }

  function joinChallenge(opt: 'A' | 'B') {
    if (challengeJoined) return;
    setChallengeJoined(opt);
    toast('已参与免费预测挑战');
  }

  function handleSpend(cost: number, label: string) {
    const ok = spendToken(cost);
    if (!ok) { toast('MTC 积分不足'); return; }
    toast(`已消耗 ${cost} MTC 兑换「${label}」成功`);
  }

  const syncTime = new Date(syncedAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

  return (
    <div className="page-enter">
      <div className="backbar"><span className="ti">🪙 球迷任务中心</span></div>

      {/* Balance hero */}
      <div className="bigcard">
        <div className="hero-kicker" style={{ color: 'var(--gold)' }}>MTC FAN MISSION CENTER</div>
        <div className="lbl" style={{ marginTop: 6 }}>我的 MTC 球迷积分余额</div>
        <div className="val">{balance}</div>
        <div className="xs" style={{ color: '#C5E0F6', marginTop: 4 }}>最近更新 {syncTime}</div>
      </div>

      {/* Fan streak */}
      <div className="sec-en">
        <span className="zh">我的连胜</span>
        <span className="en">FAN STREAK</span>
      </div>
      {streak && (streak.current_streak > 0 || streak.best_streak > 0 || streak.mtc_earned > 0) ? (
        <div className="card">
          <div className="stats">
            <div className="stat"><div className="v" style={{ color: 'var(--blueMid)' }}>{streak.current_streak}</div><div className="l">当前连胜</div></div>
            <div className="stat"><div className="v" style={{ color: 'var(--gold)' }}>{streak.best_streak}</div><div className="l">最佳连胜</div></div>
            <div className="stat"><div className="v" style={{ color: 'var(--green)' }}>{streak.mtc_earned}</div><div className="l">挑战获 MTC</div></div>
          </div>
          <div className="disclaimer-line" style={{ textAlign: 'center' }}>{DISCLAIMER_RECORD}</div>
        </div>
      ) : (
        <div className="status-card">
          <div className="ic">🎯</div>
          <div className="st">连胜挑战建设中</div>
          <div className="sub2">参与免费预测挑战、赛后结算后，这里会显示你的连胜与 MTC 积分进度。</div>
          <div className="disclaimer-line">{DISCLAIMER_RECORD}</div>
        </div>
      )}

      {/* Daily missions */}
      <div className="sec-en">
        <span className="zh">每日任务</span>
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
              {task.done ? '已完成' : `+${task.reward}`}
            </button>
          </div>
        );
      })}

      {/* Prediction challenge */}
      <div className="sec-en">
        <span className="zh">预测挑战</span>
        <span className="en">PREDICTION CHALLENGE</span>
      </div>
      <div className="card">
        <div className="b small mb8">巴西 vs 阿根廷 · 用积分验证你的判断</div>
        <div className="xs sub" style={{ marginBottom: 14 }}>
          本场是否会出现红牌？· 免费参与 · 命中瓜分 MTC 积分奖池
        </div>
        <div className="row gap8">
          <button
            className={`opt ${challengeJoined === 'A' ? 'sel' : ''}`}
            onClick={() => joinChallenge('A')}
            disabled={!!challengeJoined}
          >A. 会</button>
          <button
            className={`opt ${challengeJoined === 'B' ? 'sel' : ''}`}
            onClick={() => joinChallenge('B')}
            disabled={!!challengeJoined}
          >B. 不会</button>
        </div>
        {challengeJoined && (
          <div className="xs mt12" style={{ color: 'var(--green)', fontWeight: 800 }}>
            ✔ 已参与免费预测挑战（选择「{challengeJoined === 'A' ? '会' : '不会'}」）· 赛后结算瓜分积分奖池
          </div>
        )}
      </div>

      {/* Shop */}
      <div className="sec-en">
        <span className="zh">积分兑换</span>
        <span className="en">MTC SHOP</span>
      </div>
      {MOCK_SHOP.map(item => (
        <div className="shopitem" key={item.id}>
          <span className="row gap8 small"><span>{item.icon}</span>{item.label}</span>
          <button className="shopbtn" onClick={() => handleSpend(item.cost, item.label)}>
            {item.cost} MTC
          </button>
        </div>
      ))}

      {/* Rankings */}
      <div className="sec-en">
        <span className="zh">连胜排行榜</span>
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
                连胜 {u.current_streak} · {u.mtc_earned} MTC
              </span>
            </div>
          ))}
          <div className="disclaimer-line" style={{ textAlign: 'center', padding: '6px 8px' }}>
            积分/连胜榜，非收益榜。{DISCLAIMER_RECORD}
          </div>
        </div>
      ) : (
        <div className="status-card">
          <div className="ic">🏅</div>
          <div className="st">排行榜建设中</div>
          <div className="sub2">连胜与 MTC 积分排行榜将在挑战结算累积后开放，仅展示积分/参与/连胜，非收益榜。</div>
        </div>
      )}

      <div className="compliance">
        ⚠️ MTC 球迷积分仅为平台积分：<b>不可提现 · 不可转让 · 不可交易</b> · 不承诺收益 · 不作为金融资产 · 不接入博彩。
      </div>
      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注</div>
    </div>
  );
}
