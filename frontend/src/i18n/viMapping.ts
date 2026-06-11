/**
 * Vietnamese mapping for DYNAMIC data that currently arrives as Chinese from the
 * API / derive layer (team names, AI tendency labels, risk levels, risk notes,
 * heat labels, risk tags, reason bullets, live-correction text).
 *
 * Rule-based, offline (no external translation API). Covers the current seed/demo
 * matches; unmatched text falls back to the original string. Only used when the
 * active locale is 'vi' — callers guard with `loc === 'vi'`.
 *
 * Forbidden (vi): chắc thắng / đảm bảo thắng / cá cược / đặt cược / kiếm tiền /
 * lợi nhuận chắc chắn. ("Không phải dịch vụ cá cược" negation is allowed.)
 */

// ── Team names ───────────────────────────────────────────────────────────────
export const teamNameViMap: Record<string, string> = {
  '巴西': 'Brazil',
  '阿根廷': 'Argentina',
  '摩洛哥': 'Morocco',
  '法国': 'France',
  '西班牙': 'Spain',
  '德国': 'Germany',
};
export function teamVi(name: string): string {
  return teamNameViMap[name] ?? name;
}

// ── Outcome labels (composed with team names) ────────────────────────────────
export function homeWinVi(homeTeam: string): string { return `${teamVi(homeTeam)} thắng`; }
export function awayWinVi(awayTeam: string): string { return `${teamVi(awayTeam)} thắng`; }
export const drawVi = 'Hòa';

// ── AI tendency labels (from ops/derive.aiPickLabel) ─────────────────────────
export const aiPickLabelViMap: Record<string, string> = {
  '主胜偏强': 'Chủ nhà nhỉnh hơn',
  '主胜略占优': 'Chủ nhà có lợi thế nhẹ',
  '客胜偏强': 'Đội khách nhỉnh hơn',
  '客胜略占优': 'Đội khách có lợi thế nhẹ',
  '主队不败趋势': 'Chủ nhà có xu hướng bất bại',
  '客队不败趋势': 'Đội khách có xu hướng bất bại',
  '难分胜负': 'Khó phân định',
};
export function aiPickLabelVi(zh: string): string {
  return aiPickLabelViMap[zh] ?? 'AI trend under review'; // English fallback (not Chinese)
}

// ── Risk level ───────────────────────────────────────────────────────────────
export const riskLevelLongViMap: Record<string, string> = {
  low: 'Rủi ro thấp',
  medium: 'Rủi ro trung bình',
  high: 'Rủi ro cao',
};
export const riskLevelShortViMap: Record<string, string> = {
  low: 'Thấp',
  medium: 'TB',
  high: 'Cao',
};
export function riskLevelLongVi(level: string): string { return riskLevelLongViMap[level] ?? level; }
export function riskLevelShortVi(level: string): string { return riskLevelShortViMap[level] ?? level; }

// ── Heat labels (from ops/derive.heatLabel) ──────────────────────────────────
export const heatLabelViMap: Record<string, string> = {
  '高关注': 'Quan tâm cao',
  '热议中': 'Đang bàn luận',
  '临场热点': 'Điểm nóng sát giờ',
  '关注中': 'Đang chú ý',
  '常规': 'Thường',
};
export function heatLabelVi(zh: string): string { return heatLabelViMap[zh] ?? 'Trending'; }

// ── Risk category tags (from ops/derive.riskTags) ────────────────────────────
export const riskTagViMap: Record<string, string> = {
  '伤病': 'Chấn thương',
  '快速反击': 'Phản công nhanh',
  '临场首发': 'Đội hình xuất phát',
  '防线稳定性': 'Sự ổn định hàng thủ',
  '中场控制': 'Kiểm soát tuyến giữa',
  '主场氛围': 'Không khí sân nhà',
  '近期状态': 'Phong độ gần đây',
  '裁判尺度': 'Mức độ trọng tài',
  '体能与旅行': 'Thể lực & di chuyển',
  '阵型变化': 'Thay đổi đội hình',
  '战意': 'Tinh thần thi đấu',
};
export function riskTagVi(zh: string): string { return riskTagViMap[zh] ?? 'Risk to monitor'; }

// ── Risk notes + first-clause (topRisk) + live-correction text ───────────────
export const noteViMap: Record<string, string> = {
  // Full risk notes (seed)
  '巴西近期中场控制力增强；阿根廷后卫线主力伤停，防线稳定性下降。':
    'Brazil kiểm soát tuyến giữa tốt hơn; hàng thủ Argentina thiếu ổn định, rủi ro phòng ngự tăng.',
  '摩洛哥主场优势显著，爆冷可能性不可忽视。':
    'Morocco có lợi thế sân nhà rõ rệt; khả năng tạo bất ngờ cần được chú ý.',
  '双方实力接近，临场首发阵容影响显著。':
    'Hai đội khá cân bằng; đội hình xuất phát có thể ảnh hưởng lớn đến nhận định AI.',
  '双方实力接近，结果高度依赖临场阵容与战术对位，不确定性较高。':
    'Hai đội khá cân bằng; kết quả phụ thuộc nhiều vào đội hình và đối đầu chiến thuật, mức độ bất định cao.',
  // First clauses (topRisk splits on 。；;)
  '巴西近期中场控制力增强':
    'Brazil kiểm soát tuyến giữa tốt hơn gần đây',
  '摩洛哥主场优势显著，爆冷可能性不可忽视':
    'Morocco có lợi thế sân nhà rõ rệt; khả năng tạo bất ngờ cần chú ý',
  '双方实力接近，临场首发阵容影响显著':
    'Hai đội khá cân bằng; đội hình xuất phát ảnh hưởng lớn',
  '双方实力接近，结果高度依赖临场阵容与战术对位，不确定性较高':
    'Hai đội khá cân bằng; kết quả phụ thuộc vào đội hình & chiến thuật, bất định cao',
  // Generic topRisk fallbacks (ops/derive.topRisk)
  '双方接近，结果对临场阵容较为敏感': 'Hai đội sát nhau, kết quả nhạy với đội hình xuất phát',
  '常规波动，关注临场首发': 'Biến động thường, chú ý đội hình xuất phát',
  // refreshed risk_note (low-risk / clear-direction matches)
  '模型判断方向较为明确，主要因子一致，临场变量影响有限。':
    'Mô hình nhận định khá rõ ràng; các yếu tố chính đồng thuận, biến số sát giờ ảnh hưởng hạn chế.',
  '模型判断方向较为明确，主要因子一致，临场变量影响有限':
    'Mô hình nhận định khá rõ ràng; các yếu tố chính đồng thuận, biến số sát giờ ảnh hưởng hạn chế',
  // live_correction trigger + reason (seed)
  '阿根廷主力中卫未进入首发': 'Trung vệ trụ cột Argentina không đá chính',
  '阿根廷后场出球稳定性下降，巴西右路进攻优势扩大。':
    'Khả năng triển khai bóng của Argentina giảm, lợi thế cánh phải của Brazil tăng.',
  // free_note (seed match 1 — focus match, most viewed)
  'AI 当前更倾向巴西，但这不是低风险比赛。巴西优势在中场控制和右路推进，阿根廷风险来自后卫线伤停。不过阿根廷反击效率较高，因此平局概率也不可忽视。':
    'AI hiện nghiêng về Brazil, nhưng đây không phải trận rủi ro thấp. Lợi thế của Brazil ở kiểm soát tuyến giữa và đẩy biên phải; rủi ro của Argentina đến từ chấn thương hàng thủ. Tuy vậy Argentina phản công hiệu quả, nên khả năng hòa cũng không thể bỏ qua.',
  // report trend labels
  '赛前 3 天': 'Trước 3 ngày', '赛前 1 天': 'Trước 1 ngày', '临场 30 分': 'T-30 phút',
  // report tactics_note (seed)
  '巴西本场优势主要来自中场控制和右路推进。如果阿根廷主力中卫无法首发，巴西右路更容易形成传中和二次进攻。但阿根廷反击效率仍然很高，因此 AI 并不把本场标记为低风险。':
    'Lợi thế Brazil đến từ kiểm soát tuyến giữa & đẩy biên phải. Nếu trung vệ trụ cột Argentina không đá chính, Brazil dễ tạt biên và tấn công lớp hai; nhưng Argentina vẫn phản công hiệu quả, nên AI không xem đây là trận rủi ro thấp.',
  '摩洛哥依靠密集防守与快速反击，法国需要突破其低位防线。若法国前锋状态未能回升，平局或摩洛哥逆转的概率上升。':
    'Morocco dựa vào phòng ngự dày và phản công nhanh; Pháp cần xuyên phá hàng thủ lùi sâu. Nếu tiền đạo Pháp chưa hồi phong độ, khả năng hòa hoặc Morocco lật ngược tăng.',
  '西班牙控球压制节奏，德国依赖定位球和快速反击。若西班牙中场保持高位压迫，得分窗口将集中在上半场。':
    'Tây Ban Nha kiểm soát bóng và áp đặt nhịp; Đức dựa vào bóng cố định và phản công nhanh. Nếu TBN duy trì pressing cao, cửa ghi bàn dồn vào hiệp một.',
};
// English generic fallback for unmapped notes — avoids leaking Chinese into vi UI.
export const NOTE_VI_FALLBACK = 'AI is tracking team form, lineup changes and tactical risk.';
export function noteVi(zh: string): string {
  if (!zh) return zh;
  return noteViMap[zh] ?? noteViMap[zh.trim()] ?? NOTE_VI_FALLBACK;
}

// ── Feature labels (report features → reason bullets) ────────────────────────
export const featureLabelViMap: Record<string, string> = {
  '中场控制力': 'Kiểm soát tuyến giữa',
  '近 5 场 xG 表现': 'Phong độ xG 5 trận gần nhất',
  '阿根廷后卫伤停': 'Hậu vệ Argentina chấn thương',
  '巴西右路突破': 'Đột phá cánh phải của Brazil',
  '体能与旅行因素': 'Yếu tố thể lực & di chuyển',
  '主场氛围加成': 'Cộng hưởng sân nhà',
  '法国控球率': 'Tỷ lệ kiểm soát bóng của Pháp',
  '摩洛哥防线紧凑度': 'Độ chặt hàng thủ Morocco',
  '法国前锋状态': 'Phong độ tiền đạo Pháp',
  '控球与传导': 'Kiểm soát & luân chuyển bóng',
  '德国定位球': 'Bóng cố định của Đức',
  '西班牙锋线效率': 'Hiệu suất hàng công Tây Ban Nha',
  '德国中场疲劳度': 'Mức mệt mỏi tuyến giữa Đức',
};

// ── Premium teaser (ops/derive.premiumTeaser) ────────────────────────────────
export const premiumTeaserViMap: Record<string, string> = {
  '精确推荐比分': 'Tỷ số đề xuất chính xác',
  '完整 2-3 条理由': '2-3 lý do đầy đủ',
  '风险等级与详细风险': 'Mức rủi ro & chi tiết rủi ro',
  '临场修正推送': 'Đẩy hiệu chỉnh sát giờ',
};
export function premiumTeaserVi(zh: string): string { return premiumTeaserViMap[zh] ?? zh; }

// ════════════════════════════════════════════════════════════════════════════
// English dynamic maps — used for en AND mm locales (mm dynamic data → English,
// never Chinese). vi keeps its own maps above; everything else uses English.
// ════════════════════════════════════════════════════════════════════════════
import type { Locale } from './useLocale';
import {
  aiPickLabelMmMap, AI_PICK_FALLBACK_MM, riskLevelLongMmMap, riskLevelShortMmMap,
  heatLabelMmMap, HEAT_FALLBACK_MM, riskTagMmMap, RISK_TAG_FALLBACK_MM,
  noteMmMap, NOTE_FALLBACK_MM, featureLabelMmMap, premiumTeaserMmMap, REASON_MM, WIN_WORD_MM, DRAW_WORD_MM,
  factorInterpretationMmMap, FACTOR_INTERP_FALLBACK_MM,
} from './mmMapping';

export const aiPickLabelEnMap: Record<string, string> = {
  '主胜偏强': 'Home strongly favored',
  '主胜略占优': 'Home slight edge',
  '客胜偏强': 'Away strongly favored',
  '客胜略占优': 'Away slight edge',
  '主队不败趋势': 'Home unbeaten lean',
  '客队不败趋势': 'Away unbeaten lean',
  '难分胜负': 'Too close to call',
};
export const riskLevelLongEnMap: Record<string, string> = { low: 'Low risk', medium: 'Medium risk', high: 'High risk' };
export const riskLevelShortEnMap: Record<string, string> = { low: 'Low', medium: 'Mid', high: 'High' };
export const heatLabelEnMap: Record<string, string> = {
  '高关注': 'High interest', '热议中': 'Trending', '临场热点': 'Live hotspot', '关注中': 'Watching', '常规': 'Normal',
};
export const riskTagEnMap: Record<string, string> = {
  '伤病': 'Injury', '快速反击': 'Fast counter', '临场首发': 'Starting XI', '防线稳定性': 'Defensive stability',
  '中场控制': 'Midfield control', '主场氛围': 'Home atmosphere', '近期状态': 'Recent form', '裁判尺度': 'Referee tendency',
  '体能与旅行': 'Fitness & travel', '阵型变化': 'Formation change', '战意': 'Motivation',
};
export const noteEnMap: Record<string, string> = {
  '巴西近期中场控制力增强；阿根廷后卫线主力伤停，防线稳定性下降。':
    'Brazil controls midfield better; Argentina’s defense is unstable with a key injury, raising defensive risk.',
  '摩洛哥主场优势显著，爆冷可能性不可忽视。':
    'Morocco has a clear home advantage; an upset cannot be ignored.',
  '双方实力接近，临场首发阵容影响显著。':
    'The two sides are close; the starting lineup strongly affects the read.',
  '双方实力接近，结果高度依赖临场阵容与战术对位，不确定性较高。':
    'The two sides are close; the result depends heavily on lineup and tactical matchups, with high uncertainty.',
  '巴西近期中场控制力增强': 'Brazil’s midfield control has improved recently',
  '摩洛哥主场优势显著，爆冷可能性不可忽视': 'Morocco has a clear home advantage; an upset cannot be ignored',
  '双方实力接近，临场首发阵容影响显著': 'The two sides are close; the starting lineup matters a lot',
  '双方实力接近，结果高度依赖临场阵容与战术对位，不确定性较高': 'The two sides are close; result hinges on lineup & tactics, high uncertainty',
  '双方接近，结果对临场阵容较为敏感': 'Teams are close; result is sensitive to the starting lineup',
  '常规波动，关注临场首发': 'Normal variance; watch the starting lineup',
  '模型判断方向较为明确，主要因子一致，临场变量影响有限。':
    'The model’s read is fairly clear; key factors align and live variables have limited impact.',
  '模型判断方向较为明确，主要因子一致，临场变量影响有限':
    'The model’s read is fairly clear; key factors align and live variables have limited impact',
  '阿根廷主力中卫未进入首发': 'Argentina’s key center-back is not starting',
  '阿根廷后场出球稳定性下降，巴西右路进攻优势扩大。':
    'Argentina’s build-up stability drops; Brazil’s right-flank attacking edge grows.',
  'AI 当前更倾向巴西，但这不是低风险比赛。巴西优势在中场控制和右路推进，阿根廷风险来自后卫线伤停。不过阿根廷反击效率较高，因此平局概率也不可忽视。':
    'The AI currently leans Brazil, but this is not a low-risk match. Brazil’s edge is midfield control and the right flank; Argentina’s risk comes from a defensive injury. Still, Argentina counters efficiently, so a draw cannot be ignored.',
  '赛前 3 天': '3 days before', '赛前 1 天': '1 day before', '临场 30 分': 'T-30 min',
  '巴西本场优势主要来自中场控制和右路推进。如果阿根廷主力中卫无法首发，巴西右路更容易形成传中和二次进攻。但阿根廷反击效率仍然很高，因此 AI 并不把本场标记为低风险。':
    'Brazil’s edge is midfield control and right-flank progression. If Argentina’s key center-back can’t start, Brazil more easily creates crosses and second-phase attacks; but Argentina still counters efficiently, so the AI does not mark this as low risk.',
  '摩洛哥依靠密集防守与快速反击，法国需要突破其低位防线。若法国前锋状态未能回升，平局或摩洛哥逆转的概率上升。':
    'Morocco relies on compact defending and fast counters; France must break a deep block. If France’s strikers don’t regain form, the chance of a draw or a Morocco upset rises.',
  '西班牙控球压制节奏，德国依赖定位球和快速反击。若西班牙中场保持高位压迫，得分窗口将集中在上半场。':
    'Spain controls the ball and dictates tempo; Germany relies on set pieces and fast counters. If Spain keeps a high press, the scoring window concentrates in the first half.',
};
export const featureLabelEnMap: Record<string, string> = {
  '中场控制力': 'Midfield control', '近 5 场 xG 表现': 'xG form (last 5)', '阿根廷后卫伤停': 'Argentina defender injury',
  '巴西右路突破': 'Brazil right-flank breaks', '体能与旅行因素': 'Fitness & travel',
  '主场氛围加成': 'Home-crowd boost', '法国控球率': 'France possession', '摩洛哥防线紧凑度': 'Morocco defensive compactness',
  '法国前锋状态': 'France striker form', '控球与传导': 'Possession & circulation', '德国定位球': 'Germany set pieces',
  '西班牙锋线效率': 'Spain attacking efficiency', '德国中场疲劳度': 'Germany midfield fatigue',
};
export const premiumTeaserEnMap: Record<string, string> = {
  '精确推荐比分': 'Exact suggested score', '完整 2-3 条理由': 'Full 2-3 reasons',
  '风险等级与详细风险': 'Risk level & details', '临场修正推送': 'Live-correction push',
};
const AI_PICK_FALLBACK_EN = 'AI trend under review';
const NOTE_FALLBACK_EN = 'AI is tracking team form, lineup changes and tactical risk.';
const RISK_TAG_FALLBACK_EN = 'Risk to monitor';

// ── Locale-aware dispatchers (zh→original, vi→Vietnamese, else→English) ───────
export function teamLoc(name: string, loc: Locale): string { return loc === 'zh' ? name : teamVi(name); }
export function homeWinLoc(home: string, loc: Locale): string {
  if (loc === 'zh') return `${home}胜`;
  if (loc === 'vi') return `${teamVi(home)} thắng`;
  if (loc === 'my') return `${teamVi(home)} ${WIN_WORD_MM}`;
  return `${teamVi(home)} win`;
}
export function awayWinLoc(away: string, loc: Locale): string {
  if (loc === 'zh') return `${away}胜`;
  if (loc === 'vi') return `${teamVi(away)} thắng`;
  if (loc === 'my') return `${teamVi(away)} ${WIN_WORD_MM}`;
  return `${teamVi(away)} win`;
}
export function drawLoc(loc: Locale): string {
  if (loc === 'zh') return '平局';
  if (loc === 'vi') return 'Hòa';
  if (loc === 'my') return DRAW_WORD_MM;
  return 'Draw';
}
export function aiPickLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return aiPickLabelViMap[zh] ?? AI_PICK_FALLBACK_EN;
  if (loc === 'my') return aiPickLabelMmMap[zh] ?? AI_PICK_FALLBACK_MM;
  return aiPickLabelEnMap[zh] ?? AI_PICK_FALLBACK_EN;
}
export function riskLongLoc(level: string, loc: Locale): string {
  if (loc === 'zh') return ({ low: '低风险', medium: '中风险', high: '高风险' } as Record<string, string>)[level] ?? level;
  if (loc === 'vi') return riskLevelLongViMap[level] ?? level;
  if (loc === 'my') return riskLevelLongMmMap[level] ?? level;
  return riskLevelLongEnMap[level] ?? level;
}
export function riskShortLoc(level: string, loc: Locale): string {
  if (loc === 'zh') return ({ low: '低', medium: '中', high: '高' } as Record<string, string>)[level] ?? level;
  if (loc === 'vi') return riskLevelShortViMap[level] ?? level;
  if (loc === 'my') return riskLevelShortMmMap[level] ?? level;
  return riskLevelShortEnMap[level] ?? level;
}
export function heatLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return heatLabelViMap[zh] ?? 'Trending';
  if (loc === 'my') return heatLabelMmMap[zh] ?? HEAT_FALLBACK_MM;
  return heatLabelEnMap[zh] ?? 'Trending';
}
export function riskTagLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return riskTagViMap[zh] ?? RISK_TAG_FALLBACK_EN;
  if (loc === 'my') return riskTagMmMap[zh] ?? RISK_TAG_FALLBACK_MM;
  return riskTagEnMap[zh] ?? RISK_TAG_FALLBACK_EN;
}
export function noteLoc(zh: string, loc: Locale): string {
  if (!zh) return zh;
  if (loc === 'zh') return zh;
  if (loc === 'vi') return noteViMap[zh] ?? noteViMap[zh.trim()] ?? NOTE_VI_FALLBACK;
  if (loc === 'my') return noteMmMap[zh] ?? noteMmMap[zh.trim()] ?? NOTE_FALLBACK_MM;
  return noteEnMap[zh] ?? noteEnMap[zh.trim()] ?? NOTE_FALLBACK_EN;
}
export function premiumTeaserLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return premiumTeaserViMap[zh] ?? zh;
  if (loc === 'my') return premiumTeaserMmMap[zh] ?? zh;
  return premiumTeaserEnMap[zh] ?? zh;
}
export function featureLabelLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return featureLabelViMap[zh] ?? featureLabelEnMap[zh] ?? zh;
  if (loc === 'my') return featureLabelMmMap[zh] ?? featureLabelEnMap[zh] ?? zh;
  return featureLabelEnMap[zh] ?? zh;
}

// ════════════════════════════════════════════════════════════════════════════
// Scout Intelligence layer (frontend-derived; no API/DB fields).
// Factor SOURCE + INTERPRETATION are keyed by the zh factor label (same keys as
// featureLabel maps). vi/mm/en fall back to a generic localized line — never zh.
// ════════════════════════════════════════════════════════════════════════════

// ── Factor SOURCE (signal provenance category) ───────────────────────────────
export const factorSourceZhMap: Record<string, string> = {
  '中场控制力': '中场/战术', '近 5 场 xG 表现': '近期 xG', '阿根廷后卫伤停': '首发/伤停',
  '巴西右路突破': '首发/伤停+战术', '体能与旅行因素': '旅行/体能', '主场氛围加成': '主场/社区',
  '法国控球率': '控球/战术', '摩洛哥防线紧凑度': '战术', '法国前锋状态': '近期状态',
  '控球与传导': '控球/战术', '德国定位球': '定位球', '西班牙锋线效率': '状态/xG', '德国中场疲劳度': '体能',
};
export const factorSourceViMap: Record<string, string> = {
  '中场控制力': 'Tuyến giữa/chiến thuật', '近 5 场 xG 表现': 'xG gần đây', '阿根廷后卫伤停': 'Đội hình/chấn thương',
  '巴西右路突破': 'Đội hình/chấn thương + chiến thuật', '体能与旅行因素': 'Di chuyển/thể lực', '主场氛围加成': 'Sân nhà/cộng đồng',
  '法国控球率': 'Kiểm soát bóng/chiến thuật', '摩洛哥防线紧凑度': 'Chiến thuật', '法国前锋状态': 'Phong độ gần đây',
  '控球与传导': 'Kiểm soát bóng/chiến thuật', '德国定位球': 'Bóng cố định', '西班牙锋线效率': 'Phong độ/xG', '德国中场疲劳度': 'Thể lực',
};
// English source tags — used for en AND mm (mm strip is English by design).
export const factorSourceEnMap: Record<string, string> = {
  '中场控制力': 'Midfield/tactical', '近 5 场 xG 表现': 'Recent xG', '阿根廷后卫伤停': 'Lineup/injury',
  '巴西右路突破': 'Lineup/injury + tactical', '体能与旅行因素': 'Travel/fitness', '主场氛围加成': 'Home/community',
  '法国控球率': 'Possession/tactical', '摩洛哥防线紧凑度': 'Tactical', '法国前锋状态': 'Recent form',
  '控球与传导': 'Possession/tactical', '德国定位球': 'Set-piece', '西班牙锋线效率': 'Form/xG', '德国中场疲劳度': 'Fitness',
};
const FACTOR_SOURCE_FALLBACK_VI = 'Tín hiệu mô hình';
const FACTOR_SOURCE_FALLBACK_EN = 'Model signal';

// ── Factor INTERPRETATION (one-line "why it matters") ────────────────────────
export const factorInterpretationViMap: Record<string, string> = {
  '中场控制力': 'Kiểm soát tuyến giữa quyết định nhịp tấn công.',
  '近 5 场 xG 表现': 'Cho thấy chất lượng cơ hội ở những trận gần đây.',
  '阿根廷后卫伤停': 'Chấn thương hàng thủ làm giảm sự ổn định phòng ngự.',
  '巴西右路突破': 'Hàng thủ cánh trái của Argentina là điểm chịu áp lực.',
  '体能与旅行因素': 'Di chuyển và thể lực ảnh hưởng nhịp độ cuối trận.',
  '主场氛围加成': 'Khán giả sân nhà tiếp thêm lợi thế cho chủ nhà.',
  '法国控球率': 'Kiểm soát bóng giúp định đoạt thế trận.',
  '摩洛哥防线紧凑度': 'Hàng thủ chặt khiến đối thủ khó xuyên phá.',
  '法国前锋状态': 'Phong độ tiền đạo quyết định khả năng ghi bàn.',
  '控球与传导': 'Luân chuyển bóng giúp dựng thế tấn công.',
  '德国定位球': 'Bóng cố định có thể phá khối phòng ngự thấp.',
  '西班牙锋线效率': 'Hiệu suất hàng công biến cơ hội thành bàn thắng.',
  '德国中场疲劳度': 'Mệt mỏi tuyến giữa làm giảm kiểm soát hiệp hai.',
};
export const factorInterpretationEnMap: Record<string, string> = {
  '中场控制力': 'Midfield control sets the attacking tempo.',
  '近 5 场 xG 表现': 'Shows the quality of chances in recent games.',
  '阿根廷后卫伤停': 'A defensive injury lowers backline stability.',
  '巴西右路突破': "Argentina's left side is the pressure point.",
  '体能与旅行因素': 'Travel and fitness affect the late-game tempo.',
  '主场氛围加成': 'The home crowd adds an edge for the hosts.',
  '法国控球率': 'Ball control helps dictate the game.',
  '摩洛哥防线紧凑度': 'A compact block is hard to break down.',
  '法国前锋状态': 'Striker form decides scoring potential.',
  '控球与传导': 'Ball circulation builds the attack.',
  '德国定位球': 'Set pieces can break a low block.',
  '西班牙锋线效率': 'Attacking efficiency turns chances into goals.',
  '德国中场疲劳度': 'Midfield fatigue weakens second-half control.',
};
const FACTOR_INTERP_FALLBACK_VI = 'Yếu tố được mô hình theo dõi.';
const FACTOR_INTERP_FALLBACK_EN = 'A factor the model tracks.';

export function factorSourceLoc(label: string, loc: Locale): string {
  if (loc === 'zh') return factorSourceZhMap[label] ?? '模型信号';
  if (loc === 'vi') return factorSourceViMap[label] ?? FACTOR_SOURCE_FALLBACK_VI;
  return factorSourceEnMap[label] ?? FACTOR_SOURCE_FALLBACK_EN; // mm + en use English tags
}
export function factorInterpretationLoc(label: string, loc: Locale): string {
  if (loc === 'zh') return factorInterpretationZhMap[label] ?? '模型关注的因素。';
  if (loc === 'vi') return factorInterpretationViMap[label] ?? FACTOR_INTERP_FALLBACK_VI;
  if (loc === 'my') return factorInterpretationMmMap[label] ?? FACTOR_INTERP_FALLBACK_MM;
  return factorInterpretationEnMap[label] ?? FACTOR_INTERP_FALLBACK_EN;
}
export const factorInterpretationZhMap: Record<string, string> = {
  '中场控制力': '中场控制决定进攻节奏。', '近 5 场 xG 表现': '反映近期机会质量。',
  '阿根廷后卫伤停': '后防伤停降低防线稳定性。', '巴西右路突破': '阿根廷左路是被施压的薄弱点。',
  '体能与旅行因素': '旅行与体能影响末段节奏。', '主场氛围加成': '主场球迷为主队加成。',
  '法国控球率': '控球有助于掌控比赛。', '摩洛哥防线紧凑度': '紧凑防线更难被打穿。',
  '法国前锋状态': '前锋状态决定把握机会能力。', '控球与传导': '控球传导搭建进攻。',
  '德国定位球': '定位球可破密集防守。', '西班牙锋线效率': '锋线效率把机会转化为进球。',
  '德国中场疲劳度': '中场疲劳削弱下半场控制。',
};

// ── Scout verdict hook / contrarian / watch-before-kickoff (keyed by zh matchup) ──
type Quad = { zh: string; vi: string; mm: string; en: string };
const SCOUT_HOOK: Record<string, Quad> = {
  '巴西|阿根廷': {
    zh: '这场不是看巴西强不强，而是看阿根廷后防能撑多久。',
    vi: 'Không phải câu hỏi Brazil mạnh hơn không. Câu hỏi là hàng thủ Argentina chịu được bao lâu.',
    mm: 'မေးခွန်းက Brazil အားကောင်းလား မဟုတ်ပါ။ Argentina ခံစစ် ဘယ်လောက်ကြာကြာ တောင့်ခံနိုင်မလဲ ဆိုတာပါ။',
    en: "The question isn't whether Brazil is stronger — it's how long Argentina's defense can hold.",
  },
  '摩洛哥|法国': {
    zh: '这场不是看法国多强，而是看摩洛哥的低位防线能不能拖住节奏。',
    vi: 'Không phải Pháp mạnh đến đâu, mà là hàng thủ lùi sâu của Morocco kìm được nhịp bao lâu.',
    mm: 'France အားကို မဟုတ်ပါ၊ Morocco ၏ နက်ရှိုင်းသော ခံစစ်က အရှိန်ကို ဘယ်လောက်ထိန်းနိုင်မလဲ ဆိုတာပါ။',
    en: "Not how strong France is — whether Morocco's deep block can slow the tempo.",
  },
  '西班牙|德国': {
    zh: '这场不是看西班牙控球多漂亮，而是看德国的定位球和反击能不能抓住机会。',
    vi: 'Không phải Tây Ban Nha cầm bóng đẹp ra sao, mà là Đức có chớp được bóng cố định và phản công không.',
    mm: 'Spain ဘောလုံးပိုင်ဆိုင်မှု လှလား မဟုတ်ပါ၊ Germany ၏ set-piece နှင့် တန်ပြန်တိုက်စစ်က အခွင့်အရေးကို ဖမ်းနိုင်မလဲ ဆိုတာပါ။',
    en: "Not how pretty Spain's possession is — whether Germany's set pieces and counters take their chance.",
  },
};
const SCOUT_CONTRARIAN: Record<string, Quad> = {
  '巴西|阿根廷': {
    zh: '若阿根廷中卫及时复出，巴西右路优势会明显减弱。',
    vi: 'Nếu trung vệ Argentina kịp bình phục, lợi thế cánh phải của Brazil giảm mạnh.',
    mm: 'Argentina ဗဟိုခံစစ်သမား ပြန်ကောင်းလာပါက Brazil ၏ ညာခြမ်းအားသာချက် သိသိသာသာ ကျဆင်းသွားမည်။',
    en: "If Argentina's center-back recovers in time, Brazil's right-flank edge shrinks sharply.",
  },
  '摩洛哥|法国': {
    zh: '若法国前锋找回状态，摩洛哥的防守可能很快被打穿。',
    vi: 'Nếu tiền đạo Pháp lấy lại phong độ, thế trận phòng ngự của Morocco có thể vỡ nhanh.',
    mm: 'France ရှေ့တန်းကစားသမားများ ပုံစံပြန်ရပါက Morocco ၏ ခံစစ်က မြန်မြန် ပြိုနိုင်သည်။',
    en: "If France's strikers rediscover form, Morocco's defensive plan can break quickly.",
  },
  '西班牙|德国': {
    zh: '若德国能压制西班牙中场，控球态势可能反转。',
    vi: 'Nếu Đức pressing được tuyến giữa Tây Ban Nha, thế trận kiểm soát có thể đảo chiều.',
    mm: 'Germany က Spain အလယ်တန်းကို ဖိနှိပ်နိုင်ပါက ထိန်းချုပ်မှု ပြောင်းပြန်ဖြစ်နိုင်သည်။',
    en: "If Germany presses Spain's midfield, the control battle can flip.",
  },
};
const SCOUT_WATCH: Record<string, Quad> = {
  '巴西|阿根廷': {
    zh: '临场前 30 分钟关注阿根廷后防首发与巴西右路。',
    vi: 'Theo dõi danh sách ra sân hàng thủ Argentina và biên phải Brazil 30 phút trước trận.',
    mm: 'ပွဲမစမီ ၃၀ မိနစ်အလို Argentina ခံစစ်လူစာရင်းနှင့် Brazil ညာခြမ်းကို စောင့်ကြည့်ပါ။',
    en: "Watch Argentina's defensive lineup and Brazil's right flank 30 min before kickoff.",
  },
  '摩洛哥|法国': {
    zh: '关注法国前锋状态与摩洛哥防线纪律。',
    vi: 'Theo dõi thể trạng tiền đạo Pháp và độ kỷ luật hàng thủ Morocco.',
    mm: 'France ရှေ့တန်း ကြံ့ခိုင်မှုနှင့် Morocco ခံစစ် စည်းကမ်းကို စောင့်ကြည့်ပါ။',
    en: "Watch France's striker fitness and Morocco's defensive discipline.",
  },
  '西班牙|德国': {
    zh: '关注西班牙的压迫强度与德国的定位球。',
    vi: 'Theo dõi cường độ pressing của Tây Ban Nha và các tình huống cố định của Đức.',
    mm: 'Spain ၏ pressing အားနှင့် Germany ၏ set-piece များကို စောင့်ကြည့်ပါ။',
    en: "Watch Spain's press intensity and Germany's set-piece situations.",
  },
};
const SCOUT_HOOK_FALLBACK: Quad = {
  zh: '问题不是谁更强，而是哪个因素决定这场比赛。',
  vi: 'Câu hỏi không phải đội nào mạnh hơn, mà là yếu tố nào quyết định thế trận.',
  mm: 'မေးခွန်းက ဘယ်အသင်း အားကောင်းလဲ မဟုတ်ပါ၊ ဘယ်အချက်က ပွဲကို ဆုံးဖြတ်မလဲ ဆိုတာပါ။',
  en: "The question isn't who's stronger — it's which factor decides the game.",
};
const SCOUT_CONTRARIAN_FALLBACK: Quad = {
  zh: '若主要风险因素反转，判断可能改变。',
  vi: 'Nếu yếu tố rủi ro chính đảo chiều, nhận định có thể thay đổi.',
  mm: 'အဓိက အန္တရာယ်အချက် ပြောင်းသွားပါက သုံးသပ်ချက် ပြောင်းနိုင်သည်။',
  en: 'If the main risk factor flips, the read can change.',
};
const SCOUT_WATCH_FALLBACK: Quad = {
  zh: '关注首发阵容与临场变量。',
  vi: 'Theo dõi đội hình ra sân và biến số sát giờ trước trận.',
  mm: 'ပွဲမစမီ လူစာရင်းနှင့် ပွဲချိန်ပြောင်းလဲမှုများကို စောင့်ကြည့်ပါ။',
  en: 'Watch the starting lineup and last-minute variables before kickoff.',
};
function pickQuad(table: Record<string, Quad>, fallback: Quad, homeZh: string, awayZh: string, loc: Locale): string {
  const q = table[`${homeZh}|${awayZh}`] ?? fallback;
  return loc === 'zh' ? q.zh : loc === 'vi' ? q.vi : loc === 'my' ? q.mm : q.en;
}
export function scoutHookLoc(homeZh: string, awayZh: string, loc: Locale): string {
  return pickQuad(SCOUT_HOOK, SCOUT_HOOK_FALLBACK, homeZh, awayZh, loc);
}
export function contrarianLoc(homeZh: string, awayZh: string, loc: Locale): string {
  return pickQuad(SCOUT_CONTRARIAN, SCOUT_CONTRARIAN_FALLBACK, homeZh, awayZh, loc);
}
export function watchLoc(homeZh: string, awayZh: string, loc: Locale): string {
  return pickQuad(SCOUT_WATCH, SCOUT_WATCH_FALLBACK, homeZh, awayZh, loc);
}

// ── Reason bullets (vi) — mirrors ops/derive.reasonBullets, no logic change ───
import type { Match } from '../types';
import { topRisk } from '../ops/derive';

export function reasonBulletsLoc(m: Match, loc: Locale): string[] {
  const isVi = loc === 'vi';
  const isMm = loc === 'my';
  if (m.features && m.features.length) {
    return m.features.slice(0, 3).map((f) => {
      const label = isVi ? (featureLabelViMap[f.label] ?? f.label)
        : isMm ? (featureLabelMmMap[f.label] ?? f.label)
        : (featureLabelEnMap[f.label] ?? f.label);
      const pos = isVi ? 'đóng góp tích cực +' : isMm ? REASON_MM.posContribution : 'positive +';
      const neg = isVi ? 'trừ rủi ro ' : isMm ? REASON_MM.riskDeduction : 'risk deduction ';
      return `${label}: ${f.value >= 0 ? pos : neg}${f.value}%`;
    });
  }
  const { home, draw, away } = m.winProb;
  let bullets: string[];
  if (isVi) {
    const r = m.riskLevel === 'high' ? 'mức bất định cao' : m.riskLevel === 'medium' ? 'có biến động nhất định' : 'hướng tương đối rõ';
    bullets = [
      `Tỷ lệ mô hình: Chủ nhà ${home}% / Hòa ${draw}% / Khách ${away}%`,
      `Chỉ số tin cậy ${Math.round(m.confidence)}, ${r}`,
    ];
  } else if (isMm) {
    const r = m.riskLevel === 'high' ? REASON_MM.high : m.riskLevel === 'medium' ? REASON_MM.medium : REASON_MM.low;
    bullets = [
      `${REASON_MM.oddsPre}${home}%${REASON_MM.drawWord}${draw}%${REASON_MM.awayWord}${away}%`,
      `${REASON_MM.confPre}${Math.round(m.confidence)}၊ ${r}`,
    ];
  } else {
    const r = m.riskLevel === 'high' ? 'high uncertainty' : m.riskLevel === 'medium' ? 'some variance' : 'relatively clear direction';
    bullets = [
      `Model odds: Home ${home}% / Draw ${draw}% / Away ${away}%`,
      `Confidence ${Math.round(m.confidence)}, ${r}`,
    ];
  }
  const tr = topRisk(m);
  if (tr) {
    const wp = isVi ? 'Điểm chú ý' : isMm ? REASON_MM.watch : 'Watch point';
    bullets.push(`${wp}: ${noteLoc(tr, loc)}`);
  }
  return bullets.slice(0, 3);
}
