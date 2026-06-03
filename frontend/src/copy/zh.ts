/**
 * Centralized user-facing copy (zh-CN).
 * Single source of truth for compliance-sensitive strings.
 * Vietnamese / Burmese translation keys plug in here in a later phase.
 *
 * Forbidden vocabulary (never add here): 下注/稳赚/必中/跟单/购彩/回报率/返奖/
 * 收益承诺/现金奖池/Token 提现/转让/交易. "提现" only inside "不可提现".
 */

// Mandatory disclaimer wherever 战绩 / 命中 / 连胜 appears.
export const DISCLAIMER_RECORD =
  '历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。';

// Global compliance footer.
export const COMPLIANCE_FOOTER =
  '仅 AI 数据分析 · 非博彩服务 · 不提供现金投注 · MTC 不可提现';

// MTC loyalty-points statement.
export const MTC_STATEMENT =
  'MTC 为平台积分 · 不可提现 · 不可转让 · 不可交易 · 不作为金融资产';

export const HOME = {
  signalTitle: '今日 AI 最强信号',
  signalTitleAlt: '今日最高信心',
  signalEn: 'TOP SIGNAL',
  tendency: 'AI 倾向',
  confidence: '信心',
  topRisk: '核心风险',
  ctaView: '查看 AI 观点',
  ctaUnlock: '解锁完整分析',

  listTitle: '今日比赛简表',
  listEn: 'TODAY · MATCHES',

  upsetTitle: '今日爆冷风险 TOP3',
  upsetEn: 'UPSET RISK',

  recordTitle: 'AI 情报战绩',
  recordEn: 'TRACK RECORD',
  recordPending: '真实赛果回灌后开放',
  recordBuilding: '数据能力建设中',

  heatTitle: '社区热门选择',
  heatEn: 'COMMUNITY',
  heatComingSoon: '社区热度即将上线',

  loopTitle: '球迷任务中心',
  loopEn: 'FAN ZONE',
};

export const DETAIL = {
  verdictTitle: 'AI 结论',
  verdictEn: 'AI VERDICT',
  tendency: 'AI 倾向',
  recommendedScore: '推荐比分',
  unlockToView: '解锁查看',
  confidence: '信心',
  riskGrade: '风险等级',
  winProbTitle: 'AI 当前胜率',
  winProbEn: 'WIN PROBABILITY',
  whyTitle: '为什么 AI 这么判断',
  whyEn: 'WHY',
  riskTitle: '风险关注维度',
  riskEn: 'RISK FACTORS',
};
