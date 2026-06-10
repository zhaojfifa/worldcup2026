// Bundled ScoutScore recap content (customer-readable), mirroring the backend
// /api/v1/recap/{fixture_id} response shape. Used in VITE_USE_MOCK mode so the
// historical-recap product flow renders without a backend — the same dual-mode
// pattern as data/mock.ts. Content is DERIVED from the backend ScoutScore
// accountability report (docs/data_audit/mvp2_prediction_accountability_reports).
//
// Compliance: historical replay only (NOT a real archived prediction); no
// win-rate, no financial signal, no xG, no injury-inference; vi has zero Han.
import type { Locale } from '../i18n/useLocale';

export interface RecapEvidence { label: string; value: string; }
export interface RecapSourceRow { field: string; endpoint: string; }
export interface RecapContent {
  fixtureId: string;
  badge: string;
  headline: string;
  oneLiner: string;
  modelReplay: string;
  actualResult: string;
  replayConclusion: string;
  verdict: 'hit' | 'miss' | 'partial';
  verdictLabel: string;
  keyMisses: string[];
  evidence: RecapEvidence[];
  modelCorrection: string[];
  nextData: string[];
  operatorCopy: string;
  dataGaps: string[];
  aiBoundary: string;
  sourceLedger: RecapSourceRow[];
  disclaimer: string;
}

const SOURCE_LEDGER: RecapSourceRow[] = [
  { field: 'team_statistics', endpoint: '/fixtures/statistics' },
  { field: 'player_statistics', endpoint: '/fixtures/players' },
  { field: 'events', endpoint: '/fixtures/events' },
  { field: 'fixture', endpoint: '/fixtures' },
];

const ZH: RecapContent = {
  fixtureId: '855737',
  badge: '历史复盘 · 模型校准',
  headline: '这场爆冷不是偶然：ScoutScore 发现传统强弱判断的三个盲区',
  oneLiner: 'Argentina 纸面优势明显，但 Saudi Arabia 用下半场反超、门将表现和进攻效率改写了这场比赛。',
  modelReplay: '模型回放：偏 Argentina（基于纸面强弱）',
  actualResult: '实际结果：Saudi Arabia 2–1 取胜',
  replayConclusion: '原始强弱判断未命中，但模型定位到了关键修正方向。',
  verdict: 'miss',
  verdictLabel: '未命中 · MISS',
  keyMisses: [
    '门将表现：Saudi 门将评分 7.7 + 5 次扑救，Argentina 门将仅 6.0',
    '射门效率：Saudi 3 射 2 球，Argentina 15 射 1 球',
    '下半场事件动量：48′、53′ 连入两球完成反超',
  ],
  evidence: [
    { label: '控球率', value: '69% / 31%' },
    { label: '射门', value: '15 / 3' },
    { label: '射正', value: '6 / 2' },
    { label: '门将评分', value: '6.0 / 7.7' },
    { label: '下半场进球', value: "48′、53′ Saudi" },
  ],
  modelCorrection: ['提高射门效率权重', '提高门将状态权重', '提高事件动量权重', '下调纯纸面强弱权重'],
  nextData: ['伤停（P0）', 'xG（P1）', 'Elo / 近期状态（P1）'],
  operatorCopy:
    '这场爆冷说明，单看纸面强弱很容易高估 Argentina。ScoutScore 在历史回放中会把 Argentina 作为优势方，' +
    '但赛后证据显示，Saudi Arabia 的下半场反超、门将高评分和射门效率，是模型必须提高权重的关键因素。' +
    '也就是说，这场不是简单冷门，而是一个模型升级样本。历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
  dataGaps: ['伤停：需二次数据源（source required）', 'xG：暂未接入', 'Elo / 近期状态：待接入', '不做博彩，仅供数据分析与球迷娱乐'],
  aiBoundary: 'AI 仅解释已验证数据，不伪造赛前命中、伤停、xG 或资金建议。',
  sourceLedger: SOURCE_LEDGER,
  disclaimer: '历史回放样例，非真实赛前存档预测；历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
};

const VI: RecapContent = {
  fixtureId: '855737',
  badge: 'Phục dựng lịch sử · Hiệu chỉnh mô hình',
  headline: 'Cú sốc này không ngẫu nhiên: ScoutScore chỉ ra ba điểm mù của cách đánh giá mạnh-yếu truyền thống',
  oneLiner: 'Argentina nhỉnh hơn trên giấy, nhưng Saudi Arabia đã viết lại trận đấu bằng màn lội ngược dòng hiệp hai, màn trình diễn của thủ môn và hiệu suất tấn công.',
  modelReplay: 'Mô hình phát lại: nghiêng về Argentina (dựa trên sức mạnh trên giấy)',
  actualResult: 'Kết quả thực tế: Saudi Arabia thắng 2–1',
  replayConclusion: 'Nhận định mạnh-yếu ban đầu không trúng, nhưng mô hình đã xác định được hướng hiệu chỉnh then chốt.',
  verdict: 'miss',
  verdictLabel: 'Không trúng · MISS',
  keyMisses: [
    'Thủ môn: thủ môn Saudi điểm 7.7 + 5 lần cứu thua, thủ môn Argentina chỉ 6.0',
    'Hiệu suất dứt điểm: Saudi 3 sút 2 bàn, Argentina 15 sút 1 bàn',
    'Động lượng hiệp hai: ghi 2 bàn ở phút 48 và 53 để lội ngược dòng',
  ],
  evidence: [
    { label: 'Kiểm soát bóng', value: '69% / 31%' },
    { label: 'Số cú sút', value: '15 / 3' },
    { label: 'Sút trúng đích', value: '6 / 2' },
    { label: 'Điểm thủ môn', value: '6.0 / 7.7' },
    { label: 'Bàn thắng hiệp hai', value: "48′, 53′ Saudi" },
  ],
  modelCorrection: ['Tăng trọng số hiệu suất dứt điểm', 'Tăng trọng số phong độ thủ môn', 'Tăng trọng số động lượng sự kiện', 'Giảm trọng số sức mạnh trên giấy'],
  nextData: ['Chấn thương (P0)', 'xG (P1)', 'Elo / phong độ gần đây (P1)'],
  operatorCopy:
    'Cú sốc này cho thấy chỉ nhìn sức mạnh trên giấy rất dễ đánh giá quá cao Argentina. Trong phát lại lịch sử, ScoutScore xem Argentina là đội nhỉnh hơn, ' +
    'nhưng bằng chứng sau trận cho thấy màn lội ngược dòng hiệp hai, điểm thủ môn cao và hiệu suất dứt điểm của Saudi Arabia là những yếu tố mô hình phải tăng trọng số. ' +
    'Nói cách khác, đây không chỉ là một cú sốc, mà là một mẫu để nâng cấp mô hình. Thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
  dataGaps: ['Chấn thương: cần nguồn thứ hai (source required)', 'xG: chưa tích hợp', 'Elo / phong độ: chờ tích hợp', 'Không làm cờ bạc, chỉ phân tích dữ liệu và giải trí cho người hâm mộ'],
  aiBoundary: 'AI chỉ giải thích dữ liệu đã xác minh, không bịa ra dự đoán trước trận, chấn thương, xG hay lời khuyên tài chính.',
  sourceLedger: SOURCE_LEDGER,
  disclaimer: 'Mẫu phát lại lịch sử, không phải dự đoán lưu trữ trước trận; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
};

const EN: RecapContent = {
  fixtureId: '855737',
  badge: 'Historical recap · model calibration',
  headline: 'This upset was no fluke: ScoutScore found three blind spots in traditional strength judgement',
  oneLiner: 'Argentina led on paper, but Saudi Arabia rewrote the match with a second-half turnaround, goalkeeping and finishing efficiency.',
  modelReplay: 'Model replay: leaned Argentina (paper strength)',
  actualResult: 'Actual result: Saudi Arabia won 2–1',
  replayConclusion: 'The original strength judgement missed, but the model located the key correction directions.',
  verdict: 'miss',
  verdictLabel: 'Missed · MISS',
  keyMisses: [
    'Goalkeeping: Saudi keeper 7.7 + 5 saves vs Argentina keeper 6.0',
    'Finishing efficiency: Saudi 3 shots → 2 goals vs Argentina 15 → 1',
    'Second-half momentum: goals at 48′ and 53′ completed the turnaround',
  ],
  evidence: [
    { label: 'Possession', value: '69% / 31%' },
    { label: 'Shots', value: '15 / 3' },
    { label: 'Shots on goal', value: '6 / 2' },
    { label: 'Keeper rating', value: '6.0 / 7.7' },
    { label: 'Second-half goals', value: "48′, 53′ Saudi" },
  ],
  modelCorrection: ['Up-weight finishing efficiency', 'Up-weight goalkeeper form', 'Up-weight event momentum', 'Down-weight pure paper strength'],
  nextData: ['Injuries (P0)', 'xG (P1)', 'Elo / recent form (P1)'],
  operatorCopy:
    'This upset shows paper strength easily over-rates Argentina. In replay, ScoutScore leans Argentina, but post-match evidence — ' +
    'Saudi Arabia’s second-half turnaround, high keeper rating and finishing efficiency — are factors the model must weight higher. ' +
    'So this isn’t just a shock; it’s a model-upgrade sample. Past performance does not represent future results — for data analysis and fan entertainment only.',
  dataGaps: ['Injuries: source required', 'xG: not ingested', 'Elo / recent form: pending', 'No gambling — data analysis and fan entertainment only'],
  aiBoundary: 'AI only explains verified data; it never fabricates a pre-match hit, injuries, xG, or financial advice.',
  sourceLedger: SOURCE_LEDGER,
  disclaimer: 'Historical-replay sample, not a real archived pre-match prediction; past performance does not represent future results — for data analysis and fan entertainment only.',
};

// fixtureId -> locale -> content. vi/mm fall back to English (never Chinese); zh default.
export const RECAP_DATA: Record<string, Partial<Record<Locale, RecapContent>>> = {
  '855737': { zh: ZH, vi: VI, en: EN },
};

export function getBundledRecap(fixtureId: string, loc: Locale): RecapContent | null {
  const byLang = RECAP_DATA[fixtureId];
  if (!byLang) return null;
  return byLang[loc] ?? byLang.en ?? byLang.zh ?? null;
}

// Fixtures that have a ScoutScore recap available (drives the Home recap entry).
export const RECAP_AVAILABLE = new Set<string>(['855737']);

// Map a Match to its recap fixture id (mock id '855737' or real external_id 'AF-855737').
export function recapFixtureId(idOrExternal: { id: string; externalId?: string | null }): string | null {
  const ext = idOrExternal.externalId;
  if (ext && /^AF-(\d+)$/.test(ext)) return ext.replace('AF-', '');
  if (/^\d+$/.test(idOrExternal.id)) return idOrExternal.id;
  return null;
}
