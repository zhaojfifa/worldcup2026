// Bundled Evidence Board v2 content (customer-readable), DERIVED from the backend
// ScoutScore v0.1 accountability report
// (docs/data_audit/mvp2_prediction_accountability_reports/855737.{zh-CN,vi-VN}.json)
// and factor scores (docs/data_audit/mvp2_scoutscore_v0/855737.factor_scores.json).
//
// Same dual-mode pattern as data/recapData.ts: used directly in VITE_USE_MOCK so the
// Evidence Board renders without a backend; a future GET /api/v1/evidence/{id} proxy
// can replace this without UI change.
//
// Compliance (Evidence Board v2 Gate Spec):
//   - historical replay only — NOT a real archived prediction
//   - confidence = tier + stars, NO probability / win-rate / %  (possession % is an
//     observed match statistic, not a prediction)
//   - every factor carries source_refs OR an `assumption` honesty flag
//   - no SHAP / no feature-importance weights / no xG / no injury inference
//   - vi has ZERO Han characters; vi/mm fall back to English, never Chinese
import type { Locale } from '../i18n/useLocale';

// Qualitative factor status — drives the colour tag. No numeric scores are shown
// (raw ScoutScore weights/aggregate stay internal — no fake probability).
export type FactorTag = 'decisive' | 'validated' | 'partial' | 'invalidated' | 'gap' | 'missing';

export interface FactorView {
  key: string;
  name: string;
  tag: FactorTag;
  tagLabel: string;
  source: string;          // endpoint(s), or an honest "assumption / not ingested"
  impact: string;          // the factor's role + post-match validation
  interpretation: string;  // plain-language reading, grounded in real data
  assumption: boolean;     // true when NOT backed by source_refs (honesty flag)
}

export interface EvidenceItem { label: string; value: string; source: string; }
export interface SourceRow { field: string; endpoint: string; }

export interface EvidenceBoardContent {
  fixtureId: string;
  badge: string;
  headline: string;
  oneLiner: string;
  leanSide: string;        // e.g. "Argentina" (Latin — safe for vi)
  replayTag: string;       // "historical replay (not a pre-match archived prediction)"
  tier: 'low' | 'medium' | 'high';
  tierLabel: string;       // localized tier word
  leanText: string;        // the pre-match (replay) model view
  verdict: 'hit' | 'miss' | 'partial';
  verdictLabel: string;
  factors: FactorView[];
  evidence: EvidenceItem[];
  missingData: string[];
  aiAllowed: string[];
  aiForbidden: string[];
  sourceLedger: SourceRow[];
  rawNote: string;
  derivedFrom: string[];
  disclaimer: string;
}

// Canonical evidence source set (matches accountability report source_refs + lineups).
const SOURCE_LEDGER: SourceRow[] = [
  { field: 'team_statistics', endpoint: '/fixtures/statistics' },
  { field: 'player_statistics', endpoint: '/fixtures/players' },
  { field: 'events_summary', endpoint: '/fixtures/events' },
  { field: 'lineups / formation', endpoint: '/fixtures/lineups' },
  { field: 'fixture', endpoint: '/fixtures' },
];

const DERIVED_FROM = ['/fixtures', '/fixtures/events', '/fixtures/statistics', '/fixtures/players', '/fixtures/lineups'];

const ZH: EvidenceBoardContent = {
  fixtureId: '855737',
  badge: '历史复盘 · 模型校准',
  headline: '证据面板 · 这场爆冷里 ScoutScore 的判断、盲区与缺口',
  oneLiner: 'Argentina 纸面占优,但门将、射门效率和下半场动量改写了结果——逐因子看 AI 判断、真实证据与数据缺口。',
  leanSide: 'Argentina',
  replayTag: '历史回放(非真实赛前存档预测)',
  tier: 'low',
  tierLabel: '低',
  leanText:
    '赛前(回放)模型基于纸面强弱把 Argentina 视为优势方,置信度低——因缺少近期状态 / Elo / 伤停 / xG 等真实赛前数据,判断主要建立在假设上。',
  verdict: 'miss',
  verdictLabel: '未命中 · MISS',
  factors: [
    {
      key: 'team_strength', name: '纸面强弱', tag: 'invalidated', tagLabel: '未兑现',
      source: '假设(Elo / 阵容身价未接入)',
      impact: '权重过高 —— 纸面占优却落败',
      interpretation: '世界级球员让 Argentina 纸面领先,但优势未转化为结果,模型高估了这一项。',
      assumption: true,
    },
    {
      key: 'recent_form', name: '近期状态', tag: 'missing', tagLabel: '数据缺失',
      source: '未接入',
      impact: '无法验证',
      interpretation: '近期状态 / Elo 尚未接入,赛前无法纳入判断。',
      assumption: true,
    },
    {
      key: 'lineup_formation', name: '阵型 / 首发', tag: 'partial', tagLabel: '部分成立',
      source: '/fixtures/lineups（4-4-2 / 4-1-4-1）',
      impact: '部分成立',
      interpretation: 'Argentina 4-4-2 制造机会,但 Saudi Arabia 4-1-4-1 紧凑防守守住了结果。',
      assumption: false,
    },
    {
      key: 'match_control', name: '控场', tag: 'invalidated', tagLabel: '控场成立 · 不预测结果',
      source: '/fixtures/statistics（控球差 38）',
      impact: '控场成立,作为结果预测失效',
      interpretation: '控球 69% vs 31% 印证了控场,但控场并未转化为胜利。',
      assumption: true,
    },
    {
      key: 'efficiency', name: '射门效率', tag: 'decisive', tagLabel: '决定性 · 漏判',
      source: '/fixtures/statistics · /fixtures/players',
      impact: '决定性,赛前漏判',
      interpretation: 'Saudi Arabia 2 射正 → 2 球 vs Argentina 6 射正 → 1;门将评分 6.0 / 7.7,扑救 0 / 5。',
      assumption: false,
    },
    {
      key: 'event_momentum', name: '事件动量', tag: 'decisive', tagLabel: '决定性 · 漏判',
      source: '/fixtures/events',
      impact: '决定性,赛前漏判',
      interpretation: '下半场 48′、53′ Saudi Arabia 连入两球完成反超。',
      assumption: false,
    },
    {
      key: 'missing_risk', name: '缺口风险', tag: 'gap', tagLabel: '已确认缺口',
      source: '/injuries（0 条 · 需二次源）',
      impact: '缺口需补:伤停 P0 / xG P1',
      interpretation: '伤停返回 0 条(不得声称"无伤停"),xG 未接入 —— 无法评估可用性与机会质量。',
      assumption: false,
    },
  ],
  evidence: [
    { label: '控球率', value: '69% / 31%', source: '/fixtures/statistics' },
    { label: '总射门', value: '15 / 3', source: '/fixtures/statistics' },
    { label: '射正', value: '6 / 2', source: '/fixtures/statistics' },
    { label: '门将评分', value: '6.0 / 7.7', source: '/fixtures/players' },
    { label: '门将扑救', value: '0 / 5', source: '/fixtures/statistics' },
  ],
  missingData: [
    '伤停:0 条返回,需二次数据源或当前赛季复验（P0）',
    'xG:本轮未接入（P1）',
    '近期状态 / Elo:未接入（P1）',
  ],
  aiAllowed: [
    '赛程与最终比分', '球队与首发阵容', '阵型 / 教练', '比赛事件(进球 / 换人 / 牌)',
    '球队统计(控球 / 射门 / 扑救)', '球员与门将统计', '大名单',
  ],
  aiForbidden: [
    '伤停(未解析 · 返回 0,不得声称"无伤停")', '缺阵 / 停赛影响', '比赛结果预测',
    '任何资金 / 盈利信号', '声称这是真实赛前存档预测', 'source_ledger 之外的任何字段',
  ],
  sourceLedger: SOURCE_LEDGER,
  rawNote: '原始 Scout Pack(完整 JSON)保留在内部运营预览,不在客户视图展开;此处仅展示派生证据与来源。',
  derivedFrom: DERIVED_FROM,
  disclaimer: '历史回放样例,非真实赛前存档预测;历史表现不代表未来结果,仅供数据分析和球迷娱乐参考。',
};

const VI: EvidenceBoardContent = {
  fixtureId: '855737',
  badge: 'Phục dựng lịch sử · Hiệu chỉnh mô hình',
  headline: 'Bảng bằng chứng · Cách ScoutScore phán đoán, sai ở đâu và còn thiếu gì',
  oneLiner:
    'Argentina nhỉnh hơn trên giấy, nhưng thủ môn, hiệu suất dứt điểm và động lượng hiệp hai đã viết lại kết quả — xem từng yếu tố: phán đoán AI, bằng chứng thật và khoảng trống dữ liệu.',
  leanSide: 'Argentina',
  replayTag: 'Phát lại lịch sử (không phải dự đoán lưu trữ trước trận)',
  tier: 'low',
  tierLabel: 'thấp',
  leanText:
    'Trước trận (phát lại), mô hình dựa trên sức mạnh trên giấy xem Argentina là đội nhỉnh hơn, độ tin cậy thấp — do thiếu phong độ gần đây / Elo / chấn thương / xG, nhận định chủ yếu dựa trên giả định.',
  verdict: 'miss',
  verdictLabel: 'Không trúng · MISS',
  factors: [
    {
      key: 'team_strength', name: 'Sức mạnh trên giấy', tag: 'invalidated', tagLabel: 'Không chuyển hóa',
      source: 'Giả định (chưa tích hợp Elo / giá trị đội hình)',
      impact: 'Trọng số quá cao — mạnh trên giấy nhưng thua',
      interpretation: 'Dàn sao giúp Argentina nhỉnh hơn trên giấy, nhưng ưu thế không thành kết quả; mô hình đánh giá quá cao yếu tố này.',
      assumption: true,
    },
    {
      key: 'recent_form', name: 'Phong độ gần đây', tag: 'missing', tagLabel: 'Thiếu dữ liệu',
      source: 'Chưa tích hợp',
      impact: 'Không thể xác thực',
      interpretation: 'Phong độ gần đây / Elo chưa được tích hợp nên không thể đưa vào nhận định trước trận.',
      assumption: true,
    },
    {
      key: 'lineup_formation', name: 'Đội hình / sơ đồ', tag: 'partial', tagLabel: 'Thành lập một phần',
      source: '/fixtures/lineups (4-4-2 / 4-1-4-1)',
      impact: 'Thành lập một phần',
      interpretation: 'Sơ đồ 4-4-2 của Argentina tạo cơ hội, nhưng khối 4-1-4-1 chặt chẽ của Saudi Arabia giữ được kết quả.',
      assumption: false,
    },
    {
      key: 'match_control', name: 'Kiểm soát thế trận', tag: 'invalidated', tagLabel: 'Đúng kiểm soát · sai kết quả',
      source: '/fixtures/statistics (chênh kiểm soát 38)',
      impact: 'Đúng về kiểm soát, sai khi dự báo kết quả',
      interpretation: 'Kiểm soát bóng 69% vs 31% xác nhận thế trận, nhưng không chuyển thành chiến thắng.',
      assumption: true,
    },
    {
      key: 'efficiency', name: 'Hiệu suất dứt điểm', tag: 'decisive', tagLabel: 'Quyết định · bỏ sót',
      source: '/fixtures/statistics · /fixtures/players',
      impact: 'Quyết định, bị bỏ sót trước trận',
      interpretation: 'Saudi Arabia 2 sút trúng → 2 bàn vs Argentina 6 sút trúng → 1; điểm thủ môn 6.0 / 7.7, cứu thua 0 / 5.',
      assumption: false,
    },
    {
      key: 'event_momentum', name: 'Động lượng sự kiện', tag: 'decisive', tagLabel: 'Quyết định · bỏ sót',
      source: '/fixtures/events',
      impact: 'Quyết định, bị bỏ sót trước trận',
      interpretation: 'Hiệp hai, Saudi Arabia ghi 2 bàn ở phút 48 và 53 để lội ngược dòng.',
      assumption: false,
    },
    {
      key: 'missing_risk', name: 'Rủi ro khuyết dữ liệu', tag: 'gap', tagLabel: 'Khoảng trống đã xác nhận',
      source: '/injuries (0 kết quả · cần nguồn thứ hai)',
      impact: 'Cần bổ sung: chấn thương P0 / xG P1',
      interpretation: 'Chấn thương trả về 0 kết quả (không được nói "không có chấn thương"), xG chưa tích hợp — không thể đánh giá lực lượng và chất lượng cơ hội.',
      assumption: false,
    },
  ],
  evidence: [
    { label: 'Kiểm soát bóng', value: '69% / 31%', source: '/fixtures/statistics' },
    { label: 'Tổng số cú sút', value: '15 / 3', source: '/fixtures/statistics' },
    { label: 'Sút trúng đích', value: '6 / 2', source: '/fixtures/statistics' },
    { label: 'Điểm thủ môn', value: '6.0 / 7.7', source: '/fixtures/players' },
    { label: 'Số lần cứu thua', value: '0 / 5', source: '/fixtures/statistics' },
  ],
  missingData: [
    'Chấn thương: 0 kết quả, cần nguồn thứ hai hoặc mùa hiện tại (P0)',
    'xG: chưa tích hợp vòng này (P1)',
    'Phong độ / Elo: chưa tích hợp (P1)',
  ],
  aiAllowed: [
    'Lịch thi đấu & tỷ số cuối', 'Đội bóng & đội hình ra sân', 'Sơ đồ / HLV',
    'Sự kiện trận đấu (bàn thắng / thay người / thẻ)', 'Thống kê đội (kiểm soát / sút / cứu thua)',
    'Thống kê cầu thủ & thủ môn', 'Danh sách đăng ký',
  ],
  aiForbidden: [
    'Chấn thương (chưa giải quyết · 0 kết quả, không nói "không có chấn thương")',
    'Ảnh hưởng vắng mặt / treo giò', 'Dự đoán kết quả trận đấu', 'Bất kỳ tín hiệu tiền bạc / lợi nhuận',
    'Tuyên bố đây là dự đoán lưu trữ trước trận', 'Bất kỳ trường nào ngoài source_ledger',
  ],
  sourceLedger: SOURCE_LEDGER,
  rawNote:
    'Scout Pack gốc (JSON đầy đủ) được giữ trong bản xem nội bộ của vận hành, không mở trong giao diện khách hàng; ở đây chỉ hiển thị bằng chứng dẫn xuất và nguồn.',
  derivedFrom: DERIVED_FROM,
  disclaimer:
    'Mẫu phát lại lịch sử, không phải dự đoán lưu trữ trước trận; thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
};

const EN: EvidenceBoardContent = {
  fixtureId: '855737',
  badge: 'Historical recap · model calibration',
  headline: 'Evidence Board · how ScoutScore judged, where it missed, and what is missing',
  oneLiner:
    'Argentina led on paper, but goalkeeping, finishing efficiency and second-half momentum rewrote the result — factor by factor: the AI read, the real evidence, and the data gaps.',
  leanSide: 'Argentina',
  replayTag: 'Historical replay (not a real pre-match archived prediction)',
  tier: 'low',
  tierLabel: 'low',
  leanText:
    'Pre-match (replay), the model leaned Argentina on paper strength, confidence low — with recent form / Elo / injuries / xG missing, the view rests largely on assumptions.',
  verdict: 'miss',
  verdictLabel: 'Missed · MISS',
  factors: [
    {
      key: 'team_strength', name: 'Paper strength', tag: 'invalidated', tagLabel: 'Did not convert',
      source: 'Assumption (Elo / squad value not ingested)',
      impact: 'Over-weighted — led on paper but lost',
      interpretation: 'A world-class squad put Argentina ahead on paper, but the edge did not convert; the model over-rated this.',
      assumption: true,
    },
    {
      key: 'recent_form', name: 'Recent form', tag: 'missing', tagLabel: 'Data missing',
      source: 'Not ingested',
      impact: 'Cannot validate',
      interpretation: 'Recent form / Elo is not ingested, so it could not enter the pre-match view.',
      assumption: true,
    },
    {
      key: 'lineup_formation', name: 'Lineup / formation', tag: 'partial', tagLabel: 'Partly held',
      source: '/fixtures/lineups (4-4-2 / 4-1-4-1)',
      impact: 'Partly held',
      interpretation: "Argentina's 4-4-2 created chances, but Saudi Arabia's compact 4-1-4-1 held the result.",
      assumption: false,
    },
    {
      key: 'match_control', name: 'Match control', tag: 'invalidated', tagLabel: 'Control yes · result no',
      source: '/fixtures/statistics (possession diff 38)',
      impact: 'True as control, invalid as a result predictor',
      interpretation: 'Possession 69% vs 31% confirmed control, but control did not convert to a win.',
      assumption: true,
    },
    {
      key: 'efficiency', name: 'Finishing efficiency', tag: 'decisive', tagLabel: 'Decisive · missed',
      source: '/fixtures/statistics · /fixtures/players',
      impact: 'Decisive, missed pre-match',
      interpretation: 'Saudi Arabia 2 on-target → 2 goals vs Argentina 6 → 1; keeper ratings 6.0 / 7.7, saves 0 / 5.',
      assumption: false,
    },
    {
      key: 'event_momentum', name: 'Event momentum', tag: 'decisive', tagLabel: 'Decisive · missed',
      source: '/fixtures/events',
      impact: 'Decisive, missed pre-match',
      interpretation: 'Second-half goals at 48′ and 53′ (Saudi Arabia) completed the turnaround.',
      assumption: false,
    },
    {
      key: 'missing_risk', name: 'Missing-data risk', tag: 'gap', tagLabel: 'Confirmed gap',
      source: '/injuries (0 results · second source required)',
      impact: 'Gaps to fill: injuries P0 / xG P1',
      interpretation: 'Injuries returned 0 (never state "no injuries"); xG not ingested — availability and chance quality cannot be judged.',
      assumption: false,
    },
  ],
  evidence: [
    { label: 'Possession', value: '69% / 31%', source: '/fixtures/statistics' },
    { label: 'Total shots', value: '15 / 3', source: '/fixtures/statistics' },
    { label: 'Shots on goal', value: '6 / 2', source: '/fixtures/statistics' },
    { label: 'Keeper rating', value: '6.0 / 7.7', source: '/fixtures/players' },
    { label: 'Keeper saves', value: '0 / 5', source: '/fixtures/statistics' },
  ],
  missingData: [
    'Injuries: 0 results, second source or current-season re-check required (P0)',
    'xG: not ingested this round (P1)',
    'Recent form / Elo: not ingested (P1)',
  ],
  aiAllowed: [
    'Fixture & final score', 'Teams & starting lineups', 'Formation / coach',
    'Match events (goals / subs / cards)', 'Team statistics (possession / shots / saves)',
    'Player & goalkeeper statistics', 'Squad list',
  ],
  aiForbidden: [
    'Injuries (unresolved · 0 results, never state "no injuries")', 'Absence / suspension impact',
    'Match-result prediction', 'Any money / profit signal', 'Claiming a real pre-match archived prediction',
    'Any field outside source_ledger',
  ],
  sourceLedger: SOURCE_LEDGER,
  rawNote:
    'The raw Scout Pack (full JSON) stays in the internal operator preview and is not expanded in the customer view; only derived evidence and sources are shown here.',
  derivedFrom: DERIVED_FROM,
  disclaimer:
    'Historical-replay sample, not a real archived pre-match prediction; past performance does not represent future results — for data analysis and fan entertainment only.',
};

// fixtureId -> locale -> content. vi/mm fall back to English (never Chinese); zh default.
export const EVIDENCE_DATA: Record<string, Partial<Record<Locale, EvidenceBoardContent>>> = {
  '855737': { zh: ZH, vi: VI, en: EN },
};

export function getBundledEvidence(fixtureId: string, loc: Locale): EvidenceBoardContent | null {
  const byLang = EVIDENCE_DATA[fixtureId];
  if (!byLang) return null;
  return byLang[loc] ?? byLang.en ?? byLang.zh ?? null;
}

// Fixtures that have an Evidence Board available (drives the recap-page entry link).
export const EVIDENCE_AVAILABLE = new Set<string>(['855737']);
