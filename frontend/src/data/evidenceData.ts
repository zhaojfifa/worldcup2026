// Evidence Board v2 — CUSTOMER PRODUCT VOICE (MVP-2 Product Voice & Model Answer Sprint).
// Bundled, customer-readable model answer + post-match recap. DERIVED from the
// 855737 ScoutScore accountability artifacts (no invented values).
//
// Voice rules (see docs/MVP2_PRODUCT_VOICE_GUIDE.md):
//   - Customer main view: give the JUDGEMENT, not the audit. Less process / gaps /
//     compliance; more read + risk explanation + trust.
//   - NEVER show as the headline: "ScoutScore v0.1 historical replay", "MISS",
//     "not real archived prediction", "source required", "assumption".
//   - Data gaps -> "variables the next model still needs" (forward, not deficit).
//   - Engineering/compliance truth (model replay, MISS verdict, AI boundary,
//     raw missing_evidence, source ledger) lives in the collapsed INTERNAL block.
//   - confidence = tier words only, NO probability/%, no win-rate.
//   - vi has ZERO Han characters; vi/mm fall back to English, never Chinese.
import type { Locale } from '../i18n/useLocale';

// Customer-facing factor status (no internal jargon).
export type FactorTag = 'postmatch-impact' | 'verified' | 'prematch-watch' | 'reweight';

export interface FactorView {
  key: string;
  name: string;
  decisive: boolean;       // true -> shown expanded on first read (the 3 risk factors)
  tag: FactorTag;
  tagLabel: string;
  impact: string;          // 赛后影响 (customer)
  interpretation: string;  // 解读 (customer)
  source: string;          // friendly provenance label (raw endpoints live in the ledger)
}

export interface FirstCard { key: string; label: string; text: string; }
export interface NextVariable { name: string; note: string; }
export interface EvidenceItem { label: string; value: string; source: string; }
export interface SourceRow { field: string; endpoint: string; }

export interface EvidenceBoardContent {
  fixtureId: string;
  title: string;
  subtitle: string;
  replayNote: string;        // small / folded — does not dominate the main visual
  firstCards: FirstCard[];   // 4: lean / verify / takeaway / value
  customerLead: string;      // one readable paragraph (the model's answer)
  factors: FactorView[];     // 6 (3 decisive + 3 context)
  evidence: EvidenceItem[];  // 5 supporting real stats
  nextVariables: NextVariable[]; // 4 forward variables (was "data gaps")
  operatorCopy: string;      // operator group-broadcast version
  // INTERNAL (collapsed; engineering + compliance truth retained for traceability):
  internalModelView: string; // model replay + MISS accountability (engineering voice)
  aiAllowed: string[];
  aiForbidden: string[];
  missingEvidenceRaw: string[]; // real gaps (injuries unresolved / xG not ingested / form)
  sourceLedger: SourceRow[];
  rawNote: string;
  derivedFrom: string[];
  disclaimer: string;
}

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
  title: '这场爆冷不是偶然：AI 赛前应重点盯住三个风险因子',
  subtitle: 'Argentina 纸面实力更强，但 Saudi Arabia 用门将表现、射门效率和下半场动量改写结果。',
  replayNote: '历史回放，用于校准 AI 判断；非真实赛前存档预测。',
  firstCards: [
    { key: 'lean', label: 'AI 赛前倾向', text: 'Argentina 优势，但冷门风险不低' },
    { key: 'verify', label: '赛后验证', text: 'Saudi Arabia 2–1 取胜，风险因子集中兑现' },
    { key: 'takeaway', label: '关键结论', text: '只看纸面强弱会高估 Argentina，门将、效率、临场动量必须提高权重' },
    { key: 'value', label: '用户价值', text: '这类复盘用于校准下一场 AI 判断，而不是单纯解释比分' },
  ],
  customerLead:
    '如果只看纸面实力，Argentina 是更容易被看好的一方。但这场比赛说明，真正影响结果的不是控球本身，' +
    '而是门将表现、射门效率和下半场事件动量。Saudi Arabia 正是在这些变量上打穿了比赛。' +
    '下一场类似强弱分明的比赛，AI 不能只看强队标签，必须提前盯住这些风险因子。',
  factors: [
    {
      key: 'keeper', name: '门将表现', decisive: true, tag: 'postmatch-impact', tagLabel: '赛后影响明显',
      impact: '胜方门将是关键先生',
      interpretation: 'Saudi Arabia 门将评分 7.7、扑救 5 次；Argentina 门将 6.0、扑救 0 次。',
      source: '球员与门将数据',
    },
    {
      key: 'finishing', name: '射门效率', decisive: true, tag: 'postmatch-impact', tagLabel: '赛后影响明显',
      impact: '少射多进，效率碾压',
      interpretation: 'Saudi Arabia 2 次射正全部转化为进球；Argentina 15 射、6 次射正只进 1 球。',
      source: '官方比赛统计',
    },
    {
      key: 'momentum', name: '下半场事件动量', decisive: true, tag: 'postmatch-impact', tagLabel: '赛后影响明显',
      impact: '下半场连入两球完成反超',
      interpretation: '48′、53′ Saudi Arabia 连续进球，比赛在下半场被改写。',
      source: '比赛事件',
    },
    {
      key: 'paper', name: '纸面实力与控场', decisive: false, tag: 'reweight', tagLabel: '需重新加权',
      impact: '占优但未转化',
      interpretation: 'Argentina 控球 69%、球星云集，但纸面与控场没有变成结果——这类标签需要降权。',
      source: '纸面强弱 / 控球',
    },
    {
      key: 'form', name: '近期状态', decisive: false, tag: 'prematch-watch', tagLabel: '需赛前重点关注',
      impact: '当前未纳入判断',
      interpretation: '两队赛前状态尚未进入模型，是下一版要补强的赛前变量。',
      source: '下一版纳入',
    },
    {
      key: 'lineup', name: '首发阵型', decisive: false, tag: 'verified', tagLabel: '已验证（部分成立）',
      impact: '部分成立',
      interpretation: 'Argentina 4-4-2 制造机会，但 Saudi Arabia 4-1-4-1 紧凑防守守住结果。',
      source: '首发与阵型',
    },
  ],
  evidence: [
    { label: '控球率', value: '69% / 31%', source: '官方比赛统计' },
    { label: '总射门', value: '15 / 3', source: '官方比赛统计' },
    { label: '射正', value: '6 / 2', source: '官方比赛统计' },
    { label: '门将评分', value: '6.0 / 7.7', source: '球员数据' },
    { label: '门将扑救', value: '0 / 5', source: '官方比赛统计' },
  ],
  nextVariables: [
    { name: '首发完整性 / 伤停变化', note: '赛前 30 分钟重点关注的阵容风险' },
    { name: '机会质量', note: '射门含金量仍需持续跟踪，不止看射门数' },
    { name: '近期状态', note: '两队赛前势头要纳入下一版判断' },
    { name: '球员状态波动', note: '核心球员临场状态对强弱分明的比赛影响更大' },
  ],
  operatorCopy:
    '这场爆冷给我们的启发很直接：强队控球不等于一定能赢。Argentina 控球占优，但 Saudi Arabia 靠门将表现、' +
    '射门效率和下半场反超改变比赛。我们的 AI 复盘重点不是事后解释比分，而是把这些风险因子沉淀到下一次赛前判断里。',
  internalModelView:
    'ScoutScore v0.1 历史回放：模型赛前偏向 Argentina（基于纸面强弱，信心档位低），赛后判定 MISS——' +
    '风险因子（门将 / 效率 / 事件动量）集中兑现。这是模型升级样本，用于校准因子权重。',
  aiAllowed: [
    '赛程与最终比分', '球队与首发阵容', '阵型 / 教练', '比赛事件(进球 / 换人 / 牌)',
    '球队统计(控球 / 射门 / 扑救)', '球员与门将统计', '大名单',
  ],
  aiForbidden: [
    '伤停(未解析 · 0 条,不得声称"无伤停")', '缺阵 / 停赛影响', '比赛结果预测',
    '任何资金 / 盈利信号', '声称这是真实赛前存档预测', 'source_ledger 之外的字段',
  ],
  missingEvidenceRaw: [
    'injuries: 0 results (source required, unresolved)',
    'xG: not ingested this round',
    'recent_form / Elo: not ingested',
  ],
  sourceLedger: SOURCE_LEDGER,
  rawNote: '原始 Scout Pack(完整 JSON)保留在内部运营预览,不在客户视图展开;此处仅展示派生证据与来源。',
  derivedFrom: DERIVED_FROM,
  disclaimer: '历史表现不代表未来结果，仅供数据分析和球迷娱乐参考。',
};

const VI: EvidenceBoardContent = {
  fixtureId: '855737',
  title: 'Cú sốc này không ngẫu nhiên: AI cần nhắm ba yếu tố rủi ro trước trận',
  subtitle: 'Argentina mạnh hơn trên giấy, nhưng Saudi Arabia đã viết lại kết quả bằng màn trình diễn của thủ môn, hiệu suất dứt điểm và động lượng hiệp hai.',
  replayNote: 'Phát lại lịch sử, dùng để hiệu chỉnh phán đoán của AI; không phải dự đoán lưu trữ trước trận.',
  firstCards: [
    { key: 'lean', label: 'Xu hướng AI trước trận', text: 'Argentina nhỉnh hơn, nhưng rủi ro bất ngờ không thấp' },
    { key: 'verify', label: 'Kiểm chứng sau trận', text: 'Saudi Arabia thắng 2–1, các yếu tố rủi ro cùng lúc thành hiện thực' },
    { key: 'takeaway', label: 'Kết luận then chốt', text: 'Chỉ nhìn sức mạnh trên giấy sẽ đánh giá quá cao Argentina; thủ môn, hiệu suất và động lượng phải được tăng trọng số' },
    { key: 'value', label: 'Giá trị cho bạn', text: 'Bản phục dựng này dùng để hiệu chỉnh phán đoán AI cho trận sau, không chỉ để giải thích tỷ số' },
  ],
  customerLead:
    'Nếu chỉ nhìn sức mạnh trên giấy, Argentina là đội dễ được đánh giá cao hơn. Nhưng trận này cho thấy yếu tố quyết định không phải là kiểm soát bóng, ' +
    'mà là màn trình diễn của thủ môn, hiệu suất dứt điểm và động lượng sự kiện hiệp hai. Saudi Arabia đã xuyên thủng trận đấu đúng ở những biến số đó. ' +
    'Ở trận tiếp theo có chênh lệch rõ ràng, AI không thể chỉ nhìn nhãn "đội mạnh" mà phải nhắm trước các yếu tố rủi ro này.',
  factors: [
    {
      key: 'keeper', name: 'Màn trình diễn thủ môn', decisive: true, tag: 'postmatch-impact', tagLabel: 'Ảnh hưởng rõ sau trận',
      impact: 'Thủ môn đội thắng là nhân tố chính',
      interpretation: 'Thủ môn Saudi Arabia điểm 7.7, cứu thua 5 lần; thủ môn Argentina 6.0, cứu thua 0.',
      source: 'Dữ liệu cầu thủ & thủ môn',
    },
    {
      key: 'finishing', name: 'Hiệu suất dứt điểm', decisive: true, tag: 'postmatch-impact', tagLabel: 'Ảnh hưởng rõ sau trận',
      impact: 'Ít sút nhiều bàn, hiệu suất vượt trội',
      interpretation: 'Saudi Arabia 2 cú trúng đích đều thành bàn; Argentina 15 sút, 6 trúng đích chỉ 1 bàn.',
      source: 'Thống kê trận đấu',
    },
    {
      key: 'momentum', name: 'Động lượng hiệp hai', decisive: true, tag: 'postmatch-impact', tagLabel: 'Ảnh hưởng rõ sau trận',
      impact: 'Hai bàn hiệp hai lật ngược thế cờ',
      interpretation: 'Phút 48 và 53, Saudi Arabia ghi liên tiếp, trận đấu bị viết lại trong hiệp hai.',
      source: 'Sự kiện trận đấu',
    },
    {
      key: 'paper', name: 'Sức mạnh trên giấy & kiểm soát', decisive: false, tag: 'reweight', tagLabel: 'Cần chỉnh lại trọng số',
      impact: 'Nhỉnh hơn nhưng không chuyển hóa',
      interpretation: 'Argentina kiểm soát bóng 69%, đầy sao, nhưng ưu thế trên giấy và thế trận không thành kết quả — loại nhãn này cần giảm trọng số.',
      source: 'Sức mạnh trên giấy / kiểm soát bóng',
    },
    {
      key: 'form', name: 'Phong độ gần đây', decisive: false, tag: 'prematch-watch', tagLabel: 'Cần theo dõi trước trận',
      impact: 'Hiện chưa đưa vào phán đoán',
      interpretation: 'Phong độ trước trận của hai đội chưa vào mô hình, là biến số cần bổ sung ở bản sau.',
      source: 'Sẽ tích hợp ở bản sau',
    },
    {
      key: 'lineup', name: 'Đội hình ra sân', decisive: false, tag: 'verified', tagLabel: 'Đã xác nhận (một phần)',
      impact: 'Thành lập một phần',
      interpretation: 'Sơ đồ 4-4-2 của Argentina tạo cơ hội, nhưng khối 4-1-4-1 của Saudi Arabia giữ được kết quả.',
      source: 'Đội hình & sơ đồ',
    },
  ],
  evidence: [
    { label: 'Kiểm soát bóng', value: '69% / 31%', source: 'Thống kê trận đấu' },
    { label: 'Tổng số cú sút', value: '15 / 3', source: 'Thống kê trận đấu' },
    { label: 'Sút trúng đích', value: '6 / 2', source: 'Thống kê trận đấu' },
    { label: 'Điểm thủ môn', value: '6.0 / 7.7', source: 'Dữ liệu cầu thủ' },
    { label: 'Số lần cứu thua', value: '0 / 5', source: 'Thống kê trận đấu' },
  ],
  nextVariables: [
    { name: 'Mức đầy đủ đội hình / chấn thương', note: 'Rủi ro lực lượng cần theo dõi 30 phút trước trận' },
    { name: 'Chất lượng cơ hội', note: 'Độ nguy hiểm của cú sút cần theo dõi liên tục, không chỉ đếm số sút' },
    { name: 'Phong độ gần đây', note: 'Đà phong độ trước trận của hai đội cần vào bản phán đoán sau' },
    { name: 'Dao động phong độ cầu thủ', note: 'Phong độ tức thời của trụ cột ảnh hưởng lớn ở các trận chênh lệch rõ' },
  ],
  operatorCopy:
    'Trận bất ngờ này cho một bài học trực tiếp: đội mạnh kiểm soát bóng chưa chắc đã thắng. Argentina kiểm soát nhiều hơn, ' +
    'nhưng Saudi Arabia thay đổi trận đấu bằng thủ môn, hiệu suất dứt điểm và màn lội ngược dòng hiệp hai. Trọng tâm bản phục dựng AI ' +
    'của chúng tôi không phải giải thích tỷ số sau trận, mà là đưa các yếu tố rủi ro này vào phán đoán trước trận lần sau.',
  internalModelView:
    'ScoutScore v0.1 phát lại lịch sử: trước trận mô hình nghiêng Argentina (dựa trên sức mạnh trên giấy, độ tin cậy thấp), ' +
    'sau trận kết luận MISS — các yếu tố rủi ro (thủ môn / hiệu suất / động lượng) cùng lúc thành hiện thực. Đây là mẫu nâng cấp mô hình, dùng để hiệu chỉnh trọng số.',
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
  missingEvidenceRaw: [
    'injuries: 0 ket qua (source required, unresolved)',
    'xG: not ingested this round',
    'recent_form / Elo: not ingested',
  ],
  sourceLedger: SOURCE_LEDGER,
  rawNote:
    'Scout Pack gốc (JSON đầy đủ) được giữ trong bản xem nội bộ của vận hành, không mở trong giao diện khách hàng; ở đây chỉ hiển thị bằng chứng dẫn xuất và nguồn.',
  derivedFrom: DERIVED_FROM,
  disclaimer:
    'Thành tích quá khứ không đại diện cho kết quả tương lai, chỉ dùng để phân tích dữ liệu và giải trí cho người hâm mộ.',
};

const EN: EvidenceBoardContent = {
  fixtureId: '855737',
  title: 'This upset was no fluke: three risk factors the AI should watch pre-match',
  subtitle: 'Argentina were stronger on paper, but Saudi Arabia rewrote the result with goalkeeping, finishing efficiency and second-half momentum.',
  replayNote: 'Historical replay, used to calibrate the AI read; not a real pre-match archived prediction.',
  firstCards: [
    { key: 'lean', label: 'AI pre-match lean', text: 'Argentina favoured, but upset risk was not low' },
    { key: 'verify', label: 'Post-match check', text: 'Saudi Arabia won 2–1; the risk factors all landed' },
    { key: 'takeaway', label: 'Key takeaway', text: 'Paper strength over-rates Argentina; goalkeeping, efficiency and momentum must weigh more' },
    { key: 'value', label: 'Why it matters', text: 'This recap calibrates the next AI read — not just an after-the-fact score explainer' },
  ],
  customerLead:
    'On paper strength alone, Argentina were the easier side to back. But this match shows the result hinged not on possession ' +
    'itself, but on goalkeeping, finishing efficiency and second-half momentum — exactly where Saudi Arabia broke the game open. ' +
    'In the next clearly-mismatched fixture, the AI cannot just read the "strong team" label; it must watch these risk factors in advance.',
  factors: [
    {
      key: 'keeper', name: 'Goalkeeping', decisive: true, tag: 'postmatch-impact', tagLabel: 'Clear post-match impact',
      impact: 'The winning keeper was the difference',
      interpretation: 'Saudi Arabia keeper rated 7.7 with 5 saves; Argentina keeper 6.0 with 0.',
      source: 'Player & goalkeeper data',
    },
    {
      key: 'finishing', name: 'Finishing efficiency', decisive: true, tag: 'postmatch-impact', tagLabel: 'Clear post-match impact',
      impact: 'Fewer shots, more goals',
      interpretation: 'Saudi Arabia converted both shots on target; Argentina took 15 shots, 6 on target, scored 1.',
      source: 'Match statistics',
    },
    {
      key: 'momentum', name: 'Second-half momentum', decisive: true, tag: 'postmatch-impact', tagLabel: 'Clear post-match impact',
      impact: 'Two second-half goals turned it around',
      interpretation: 'Goals at 48′ and 53′ (Saudi Arabia) rewrote the match after the break.',
      source: 'Match events',
    },
    {
      key: 'paper', name: 'Paper strength & control', decisive: false, tag: 'reweight', tagLabel: 'Needs re-weighting',
      impact: 'Dominant but did not convert',
      interpretation: 'Argentina held 69% possession with a star squad, but paper strength and control did not become a result — this label needs less weight.',
      source: 'Paper strength / possession',
    },
    {
      key: 'form', name: 'Recent form', decisive: false, tag: 'prematch-watch', tagLabel: 'Watch pre-match',
      impact: 'Not yet in the read',
      interpretation: "Pre-match form is not in the model yet — a pre-match variable to add next.",
      source: 'Add in next version',
    },
    {
      key: 'lineup', name: 'Lineup / formation', decisive: false, tag: 'verified', tagLabel: 'Verified (partly)',
      impact: 'Partly held',
      interpretation: "Argentina's 4-4-2 created chances, but Saudi Arabia's compact 4-1-4-1 held the result.",
      source: 'Lineups & formation',
    },
  ],
  evidence: [
    { label: 'Possession', value: '69% / 31%', source: 'Match statistics' },
    { label: 'Total shots', value: '15 / 3', source: 'Match statistics' },
    { label: 'Shots on goal', value: '6 / 2', source: 'Match statistics' },
    { label: 'Keeper rating', value: '6.0 / 7.7', source: 'Player data' },
    { label: 'Keeper saves', value: '0 / 5', source: 'Match statistics' },
  ],
  nextVariables: [
    { name: 'Squad completeness / injuries', note: 'A squad risk to watch in the 30 minutes before kickoff' },
    { name: 'Chance quality', note: 'Shot danger needs continuous tracking, not just shot counts' },
    { name: 'Recent form', note: "Both sides' pre-match momentum should enter the next read" },
    { name: 'Player form swings', note: 'Key-player form matters more in clearly-mismatched fixtures' },
  ],
  operatorCopy:
    'The lesson from this upset is direct: a strong side controlling possession does not guarantee a win. Argentina had more of the ball, ' +
    'but Saudi Arabia changed the match with goalkeeping, finishing efficiency and a second-half turnaround. Our AI recap is not about explaining ' +
    'the score after the fact — it is about folding these risk factors into the next pre-match read.',
  internalModelView:
    'ScoutScore v0.1 historical replay: the model leaned Argentina pre-match (paper strength, low confidence); post-match verdict MISS — ' +
    'the risk factors (keeper / efficiency / event momentum) all landed. A model-upgrade sample used to recalibrate factor weights.',
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
  missingEvidenceRaw: [
    'injuries: 0 results (source required, unresolved)',
    'xG: not ingested this round',
    'recent_form / Elo: not ingested',
  ],
  sourceLedger: SOURCE_LEDGER,
  rawNote:
    'The raw Scout Pack (full JSON) stays in the internal operator preview and is not expanded in the customer view; only derived evidence and sources are shown here.',
  derivedFrom: DERIVED_FROM,
  disclaimer:
    'Past performance does not represent future results — for data analysis and fan entertainment only.',
};

export const EVIDENCE_DATA: Record<string, Partial<Record<Locale, EvidenceBoardContent>>> = {
  '855737': { zh: ZH, vi: VI, en: EN },
};

export function getBundledEvidence(fixtureId: string, loc: Locale): EvidenceBoardContent | null {
  const byLang = EVIDENCE_DATA[fixtureId];
  if (!byLang) return null;
  return byLang[loc] ?? byLang.en ?? byLang.zh ?? null;
}

export const EVIDENCE_AVAILABLE = new Set<string>(['855737']);
