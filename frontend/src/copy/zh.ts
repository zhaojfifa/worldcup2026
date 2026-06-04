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

// ── Brand: Nhà Tiên Tri AI (足球先知 / 世界杯 AI 情报官) ──────────────────────
export const BRAND = {
  name: 'Nhà Tiên Tri AI',
  nameVn: 'Nhà Tiên Tri Bóng Đá',
  zhRole: '世界杯 AI 情报社区',
  headerSub: '不只看胜率，更看 AI 为什么这样判断',
  heroEn: '2026 World Cup Football Intelligence',
  heroSub: 'AI 数据观点 · 胜率变化 · 风险提示 · 临场修正',
  signalTag: 'Nhà Tiên Tri Signal',
  verdictTitle: 'Nhà Tiên Tri AI Verdict',
};

// ── Community channel matrix (placeholders — no real outbound links yet) ────
export const SOCIAL_CHANNELS = [
  { id: 'zalo',     ic: '💬', name: 'Zalo',     title: '越南球迷主阵地',   desc: '每日 AI 情报、临场修正提醒即将开放' },
  { id: 'telegram', ic: '✈️', name: 'Telegram', title: '临场情报推送',     desc: '首发公布后，AI 修正观点实时同步' },
  { id: 'facebook', ic: '📘', name: 'Facebook', title: '赛事讨论与长图复盘', desc: '适合发布赛前分析与赛后总结' },
  { id: 'tiktok',   ic: '🎵', name: 'TikTok',   title: '每日 AI 三场速览',  desc: '爆冷风险、今日最高信心、临场修正短视频' },
] as const;

export const SOCIAL = {
  title: '社群情报矩阵',
  en: 'COMMUNITY CHANNELS',
  status: '即将开放',
};

// ── Content Studio (placeholders — no copy/share logic yet) ─────────────────
export const CONTENT_STUDIO = {
  title: 'AI 情报内容工厂',
  en: 'CONTENT STUDIO',
  status: '数据能力建设中',
  items: [
    { ic: '⚡', label: '今日 AI 三场速览' },
    { ic: '🎯', label: '今日最高信心' },
    { ic: '⚠️', label: '爆冷风险短图' },
    { ic: '📡', label: '临场修正截图' },
    { ic: '📊', label: '赛后复盘长图' },
    { ic: '📝', label: '社群推送文案' },
  ],
  actions: [
    { label: '复制运营文案（即将开放）' },
    { label: '生成分享卡（即将开放）' },
  ],
};

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
