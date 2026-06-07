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
  // live_correction trigger + reason (seed)
  '阿根廷主力中卫未进入首发': 'Trung vệ trụ cột Argentina không đá chính',
  '阿根廷后场出球稳定性下降，巴西右路进攻优势扩大。':
    'Khả năng triển khai bóng của Argentina giảm, lợi thế cánh phải của Brazil tăng.',
  // free_note (seed match 1 — focus match, most viewed)
  'AI 当前更倾向巴西，但这不是低风险比赛。巴西优势在中场控制和右路推进，阿根廷风险来自后卫线伤停。不过阿根廷反击效率较高，因此平局概率也不可忽视。':
    'AI hiện nghiêng về Brazil, nhưng đây không phải trận rủi ro thấp. Lợi thế của Brazil ở kiểm soát tuyến giữa và đẩy biên phải; rủi ro của Argentina đến từ chấn thương hàng thủ. Tuy vậy Argentina phản công hiệu quả, nên khả năng hòa cũng không thể bỏ qua.',
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
  '阿根廷主力中卫未进入首发': 'Argentina’s key center-back is not starting',
  '阿根廷后场出球稳定性下降，巴西右路进攻优势扩大。':
    'Argentina’s build-up stability drops; Brazil’s right-flank attacking edge grows.',
  'AI 当前更倾向巴西，但这不是低风险比赛。巴西优势在中场控制和右路推进，阿根廷风险来自后卫线伤停。不过阿根廷反击效率较高，因此平局概率也不可忽视。':
    'The AI currently leans Brazil, but this is not a low-risk match. Brazil’s edge is midfield control and the right flank; Argentina’s risk comes from a defensive injury. Still, Argentina counters efficiently, so a draw cannot be ignored.',
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
  return `${teamVi(home)} win`;
}
export function awayWinLoc(away: string, loc: Locale): string {
  if (loc === 'zh') return `${away}胜`;
  if (loc === 'vi') return `${teamVi(away)} thắng`;
  return `${teamVi(away)} win`;
}
export function drawLoc(loc: Locale): string { return loc === 'zh' ? '平局' : loc === 'vi' ? 'Hòa' : 'Draw'; }
export function aiPickLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return aiPickLabelViMap[zh] ?? AI_PICK_FALLBACK_EN;
  return aiPickLabelEnMap[zh] ?? AI_PICK_FALLBACK_EN;
}
export function riskLongLoc(level: string, loc: Locale): string {
  if (loc === 'zh') return ({ low: '低风险', medium: '中风险', high: '高风险' } as Record<string, string>)[level] ?? level;
  if (loc === 'vi') return riskLevelLongViMap[level] ?? level;
  return riskLevelLongEnMap[level] ?? level;
}
export function riskShortLoc(level: string, loc: Locale): string {
  if (loc === 'zh') return ({ low: '低', medium: '中', high: '高' } as Record<string, string>)[level] ?? level;
  if (loc === 'vi') return riskLevelShortViMap[level] ?? level;
  return riskLevelShortEnMap[level] ?? level;
}
export function heatLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return heatLabelViMap[zh] ?? 'Trending';
  return heatLabelEnMap[zh] ?? 'Trending';
}
export function riskTagLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return riskTagViMap[zh] ?? RISK_TAG_FALLBACK_EN;
  return riskTagEnMap[zh] ?? RISK_TAG_FALLBACK_EN;
}
export function noteLoc(zh: string, loc: Locale): string {
  if (!zh) return zh;
  if (loc === 'zh') return zh;
  if (loc === 'vi') return noteViMap[zh] ?? noteViMap[zh.trim()] ?? NOTE_VI_FALLBACK;
  return noteEnMap[zh] ?? noteEnMap[zh.trim()] ?? NOTE_FALLBACK_EN;
}
export function premiumTeaserLoc(zh: string, loc: Locale): string {
  if (loc === 'zh') return zh;
  if (loc === 'vi') return premiumTeaserViMap[zh] ?? zh;
  return premiumTeaserEnMap[zh] ?? zh;
}

// ── Reason bullets (vi) — mirrors ops/derive.reasonBullets, no logic change ───
import type { Match } from '../types';
import { topRisk } from '../ops/derive';

export function reasonBulletsLoc(m: Match, loc: Locale): string[] {
  const isVi = loc === 'vi';
  if (m.features && m.features.length) {
    return m.features.slice(0, 3).map((f) => {
      const label = isVi ? (featureLabelViMap[f.label] ?? f.label) : (featureLabelEnMap[f.label] ?? f.label);
      const pos = isVi ? 'đóng góp tích cực +' : 'positive +';
      const neg = isVi ? 'trừ rủi ro ' : 'risk deduction ';
      return `${label}: ${f.value >= 0 ? pos : neg}${f.value}%`;
    });
  }
  const { home, draw, away } = m.winProb;
  const riskTextVi =
    m.riskLevel === 'high' ? 'mức bất định cao' :
    m.riskLevel === 'medium' ? 'có biến động nhất định' : 'hướng tương đối rõ';
  const riskTextEn =
    m.riskLevel === 'high' ? 'high uncertainty' :
    m.riskLevel === 'medium' ? 'some variance' : 'relatively clear direction';
  const bullets = isVi
    ? [
        `Tỷ lệ mô hình: Chủ nhà ${home}% / Hòa ${draw}% / Khách ${away}%`,
        `Chỉ số tin cậy ${Math.round(m.confidence)}, ${riskTextVi}`,
      ]
    : [
        `Model odds: Home ${home}% / Draw ${draw}% / Away ${away}%`,
        `Confidence ${Math.round(m.confidence)}, ${riskTextEn}`,
      ];
  const tr = topRisk(m);
  if (tr) bullets.push(`${isVi ? 'Điểm chú ý' : 'Watch point'}: ${noteLoc(tr, loc)}`);
  return bullets.slice(0, 3);
}
