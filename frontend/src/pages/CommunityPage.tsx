import { useAppStore } from '../store/useAppStore';
import { toast } from '../components/Toast';

const FLOW = [
  { ic: '🧠', title: '赛前模型判断', desc: '每场比赛的胜率分布、推荐比分、风险评级与关键因子。' },
  { ic: '📡', title: '临场阵容修正', desc: '首发公布后 30 分钟内，AI 根据阵容变化重新计算并推送变盘。' },
  { ic: '🔁', title: '赛后模型复盘', desc: '比对模型判断与实际结果，沉淀下一场的情报视角。' },
];

const BENEFITS = [
  '每日 3-5 场 AI 情报推送',
  '单场完整模型解释',
  '首发公布后 30 分钟 AI 重新计算',
  '临场修正实时推送',
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
      <div className="backbar"><span className="ti">👥 临场情报 VIP</span></div>

      {/* Price hero */}
      <div className="bigcard">
        <div className="hero-kicker" style={{ color: 'var(--gold)' }}>LIVE INTELLIGENCE VIP</div>
        <span className="pill" style={{ background: '#fff', color: 'var(--blue)', marginTop: 8 }}>临场情报 VIP</span>
        <div className="val" style={{ fontSize: 42 }}>
          ¥199<span style={{ fontSize: 16, color: '#C5E0F6' }}>/月</span>
        </div>
        <div className="xs" style={{ color: '#C5E0F6', marginTop: 4 }}>
          你获得的不是一条预测，而是一整套比赛情报流。
        </div>
      </div>

      {/* Intelligence flow */}
      <div className="sec-en">
        <span className="zh">一整套情报流</span>
        <span className="en">INTEL FLOW</span>
      </div>
      <div className="card">
        {FLOW.map(f => (
          <div className="flow-step" key={f.title}>
            <div className="fs-dot">{f.ic}</div>
            <div className="fs-body">
              <div className="fs-title">{f.title}</div>
              <div className="fs-desc">{f.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Benefits */}
      <div className="sec-en">
        <span className="zh">会员权益</span>
        <span className="en">BENEFITS</span>
      </div>
      <div className="card" style={{ padding: 10 }}>
        {BENEFITS.map(b => (
          <div className="benefit" key={b}>
            <span style={{ color: 'var(--green)' }}>✔</span>{b}
          </div>
        ))}
      </div>

      {/* Why it's valuable */}
      <div className="sec-en">
        <span className="zh">为什么社群值钱？</span>
        <span className="en">WHY VIP</span>
      </div>
      <div className="card accent">
        <div className="row gap8 mb12">
          <span>⚡</span><span className="b small">实时变盘示例</span>
        </div>
        <div className="row between small">
          <span style={{ color: '#3A4A60' }}>巴西胜率</span>
          <span className="b">
            <span className="sub">45%</span>{' → '}
            <span style={{ color: 'var(--green)' }}>49% ▲</span>
          </span>
        </div>
        <p className="xs sub mt8">
          阿根廷主力中卫缺阵 → 巴西右路优势扩大，社群第一时间推送。
        </p>
      </div>

      <button className="cta primary" onClick={handleSubscribe}>
        {subscribed ? '✓ 已订阅 · 临场推送已开启' : '立即订阅 · ¥199/月'}
      </button>

      <div className="muted-note">
        订阅为 AI 数据分析与情报服务 · 非博彩 · 不提供现金投注 · MTC 不可提现
      </div>
    </div>
  );
}
