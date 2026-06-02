import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { MOCK_SHOP } from '../data/mock';
import { toast } from '../components/Toast';

export function TokenPage() {
  const { balance, tasks, checkIn, completeTask, spendToken, syncedAt } = useAppStore();
  const [challengeJoined, setChallengeJoined] = useState<'A' | 'B' | null>(null);

  function handleTask(taskId: string) {
    if (taskId === 'checkin') {
      const task = tasks.find(t => t.id === 'checkin');
      if (task?.done) { toast('今日已签到'); return; }
      checkIn();
      toast('签到成功 +10 MTC');
    } else {
      const task = tasks.find(t => t.id === taskId);
      if (!task || task.done) return;
      completeTask(taskId);
      toast(`获得 ${task.reward} MTC`);
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
      <div className="backbar"><span className="ti">🪙 MTC 球迷积分中心</span></div>

      <div className="bigcard">
        <div className="lbl">我的 MTC 球迷积分余额</div>
        <div className="val">{balance}</div>
        <div className="xs" style={{ color: '#C5E0F6', marginTop: 4 }}>
          最近更新 {syncTime}
        </div>
      </div>

      <div className="sec">今日任务</div>
      <div className="card" style={{ padding: 6 }}>
        {tasks.map(task => (
          <div className="task" key={task.id}>
            <span className="l">
              <span style={{ color: task.done ? 'var(--green)' : 'var(--blueMid)' }}>{task.icon}</span>
              {task.label}
            </span>
            <button
              className={`tbtn ${task.done ? 'done' : ''}`}
              onClick={() => handleTask(task.id)}
              disabled={task.done}
            >
              {task.done ? '已完成' : `+${task.reward}`}
            </button>
          </div>
        ))}
      </div>

      <div className="sec">免费预测挑战</div>
      <div className="card">
        <div className="b small mb8">巴西 vs 阿根廷</div>
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

      <div className="sec">MTC 积分商店</div>
      {MOCK_SHOP.map(item => (
        <div className="shopitem" key={item.id}>
          <span className="row gap8 small"><span>{item.icon}</span>{item.label}</span>
          <button className="shopbtn" onClick={() => handleSpend(item.cost, item.label)}>
            {item.cost} MTC
          </button>
        </div>
      ))}

      <div className="compliance">
        ⚠️ MTC 球迷积分仅为平台积分：<b>不可提现 · 不可转让 · 不承诺收益</b> · 不作为金融资产 · 不接入博彩。
      </div>
      <div className="muted-note">仅 AI 数据分析 · 非博彩服务 · 不提供现金投注</div>
    </div>
  );
}
