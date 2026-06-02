import { useAppStore } from '../store/useAppStore';
import { toast } from '../components/Toast';

const BENEFITS = [
  '每日 3-5 场 AI 预测',
  '单场完整模型解析',
  '首发公布后 30 分钟 AI 重新计算',
  '临场修正推送',
  '高风险比赛提醒',
  'MTC 积分加成',
  '私域社群服务',
];

export function CommunityPage() {
  const { subscribed, subscribe } = useAppStore();

  async function handleSubscribe() {
    if (subscribed) { toast('已订阅'); return; }
    await subscribe();
    toast('订阅成功 · 临场推送已开启');
  }

  return (
    <div className="page-enter">
      <div className="backbar"><span className="ti">👥 社群订阅</span></div>

      <div className="bigcard">
        <span className="pill" style={{ background: '#fff', color: 'var(--blue)' }}>临场情报 VIP</span>
        <div className="val" style={{ fontSize: 42 }}>
          ¥199<span style={{ fontSize: 16, color: '#C5E0F6' }}>/月</span>
        </div>
        <div className="xs" style={{ color: '#C5E0F6', marginTop: 4 }}>
          首发公布后，AI 自动重算并推送给你
        </div>
      </div>

      <div className="sec">会员权益</div>
      <div className="card" style={{ padding: 10 }}>
        {BENEFITS.map(b => (
          <div className="benefit" key={b}>
            <span style={{ color: 'var(--green)' }}>✔</span>{b}
          </div>
        ))}
      </div>

      <div className="sec">为什么社群值钱？</div>
      <div className="card accent">
        <div className="row gap8 mb12">
          <span>⚡</span><span className="b small">实时变盘示例</span>
        </div>
        <div className="row between small">
          <span style={{ color: '#3A4A60' }}>巴西胜率</span>
          <span className="b">
            <span className="sub">45%</span>
            {' → '}
            <span style={{ color: 'var(--green)' }}>49% ▲</span>
          </span>
        </div>
        <p className="xs sub mt8">
          阿根廷主力中卫缺阵 → 巴西右路优势扩大，社群第一时间推送。
        </p>
      </div>

      <button className="cta primary" onClick={handleSubscribe}>
        {subscribed ? '✓ 已订阅 · 临场推送已开启' : '立即订阅 ¥199/月'}
      </button>

      <div className="muted-note">
        订阅为 AI 数据分析与情报服务 · 非博彩 · 不提供现金投注 · MTC 不可提现
      </div>
    </div>
  );
}
