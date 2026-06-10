import type { Match, ShopItem, TokenTask } from '../types';

// Mock API response — mirrors /api/v1/matches/{id} shape
export const MOCK_MATCHES: Match[] = [
  {
    id: 'BRA-ARG-20260605',
    homeTeam: { name: '巴西', flag: '🇧🇷' },
    awayTeam: { name: '阿根廷', flag: '🇦🇷' },
    kickoffTime: '2026-06-05T07:00:00+08:00',
    tag: 'focus',
    winProb: { home: 45, draw: 27, away: 28 },
    recommendedScore: '2:1 / 1:1',
    riskLevel: 'medium',
    riskNote: '巴西近期中场控制力增强；阿根廷后卫线主力伤停，防线稳定性下降。',
    confidence: 62,
    features: [
      { label: '中场控制力', value: 18 },
      { label: '近 5 场 xG 表现', value: 12 },
      { label: '阿根廷后卫伤停', value: 10 },
      { label: '巴西右路突破', value: 8 },
      { label: '体能与旅行因素', value: -3 },
    ],
    tacticsNote:
      '巴西本场优势主要来自中场控制和右路推进。如果阿根廷主力中卫无法首发，巴西右路更容易形成传中和二次进攻。但阿根廷反击效率仍然很高，因此 AI 并不把本场标记为低风险。',
    freeNote:
      'AI 当前更倾向巴西，但这不是低风险比赛。巴西优势在中场控制和右路推进，阿根廷风险来自后卫线伤停。不过阿根廷反击效率较高，因此平局概率也不可忽视。',
    trendHistory: [
      { label: '赛前 3 天', prob: 42 },
      { label: '赛前 1 天', prob: 45 },
      { label: '临场 30 分', prob: 49 },
    ],
    liveCorrection: undefined,
    updatedAt: '2026-06-02T10:30:00+08:00',
  },
  {
    id: 'MAR-FRA-20260606',
    homeTeam: { name: '摩洛哥', flag: '🇲🇦' },
    awayTeam: { name: '法国', flag: '🇫🇷' },
    kickoffTime: '2026-06-06T20:00:00+08:00',
    tag: 'upset',
    winProb: { home: 38, draw: 29, away: 33 },
    recommendedScore: '1:1 / 0:1',
    riskLevel: 'high',
    riskNote: '摩洛哥主场优势显著，爆冷可能性不可忽视。',
    confidence: 51,
    features: [
      { label: '主场氛围加成', value: 14 },
      { label: '法国控球率', value: 9 },
      { label: '摩洛哥防线紧凑度', value: 8 },
      { label: '法国前锋状态', value: -5 },
    ],
    tacticsNote:
      '摩洛哥依靠密集防守与快速反击，法国需要突破其低位防线。若法国前锋状态未能回升，平局或摩洛哥逆转的概率上升。',
    freeNote: 'AI 当前轻微看好法国，但摩洛哥的爆冷能力不容小觑。',
    trendHistory: [
      { label: '赛前 3 天', prob: 35 },
      { label: '赛前 1 天', prob: 33 },
      { label: '临场 30 分', prob: 33 },
    ],
    updatedAt: '2026-06-02T10:30:00+08:00',
  },
  {
    id: 'ESP-GER-20260607',
    homeTeam: { name: '西班牙', flag: '🇪🇸' },
    awayTeam: { name: '德国', flag: '🇩🇪' },
    kickoffTime: '2026-06-07T03:00:00+08:00',
    tag: 'live',
    winProb: { home: 41, draw: 30, away: 29 },
    recommendedScore: '1:0 / 2:1',
    riskLevel: 'medium',
    riskNote: '双方实力接近，临场首发阵容影响显著。',
    confidence: 57,
    features: [
      { label: '控球与传导', value: 16 },
      { label: '德国定位球', value: 7 },
      { label: '西班牙锋线效率', value: 6 },
      { label: '德国中场疲劳度', value: -4 },
    ],
    tacticsNote:
      '西班牙控球压制节奏，德国依赖定位球和快速反击。若西班牙中场保持高位压迫，得分窗口将集中在上半场。',
    freeNote: '西班牙略占优，但德国的定位球能力让本场充满变数。',
    trendHistory: [
      { label: '赛前 3 天', prob: 39 },
      { label: '赛前 1 天', prob: 41 },
      { label: '临场 30 分', prob: 41 },
    ],
    updatedAt: '2026-06-02T10:30:00+08:00',
  },
  // Historical recap fixture (WC2022) — finished; drives the Home "Historical Recap"
  // surface and the ScoutScore recap detail. English team names match the real API
  // (and keep vi Han-free). status='finished' keeps it out of current predictions.
  {
    id: '855737',
    externalId: 'AF-855737',
    homeTeam: { name: 'Argentina', flag: '🇦🇷' },
    awayTeam: { name: 'Saudi Arabia', flag: '🇸🇦' },
    kickoffTime: '2022-11-22T18:00:00+08:00',
    status: 'finished',
    winProb: { home: 64, draw: 22, away: 14 },
    recommendedScore: '—',
    riskLevel: 'high',
    riskNote: '历史复盘样例：纸面优势方未能取胜，用于模型校准。',
    confidence: 40,
    features: [],
    tacticsNote: '历史复盘 / 模型校准，不是当前比赛预测。',
    freeNote: '历史复盘 / 模型校准，不是当前比赛预测。',
    trendHistory: [],
    updatedAt: '2022-11-22T20:00:00+08:00',
  },
];

export const MOCK_TASKS: TokenTask[] = [
  { id: 'checkin', icon: '✔', label: '每日签到', reward: 10, done: false },
  { id: 'share', icon: '📤', label: '分享预测卡', reward: 50, done: false },
  { id: 'invite', icon: '👥', label: '邀请好友注册', reward: 100, done: false },
];

export const MOCK_SHOP: ShopItem[] = [
  { id: 'report', icon: '🔓', label: '单场 AI 深度报告', cost: 390 },
  { id: 'community7', icon: '👥', label: '7 天社群体验', cost: 1500 },
  { id: 'freepass', icon: '🎁', label: '单场免单券', cost: 3000 },
];
