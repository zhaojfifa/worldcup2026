/**
 * Operations derivation layer (frontend).
 *
 * Pure functions that derive operator-readable insight fields from the EXISTING
 * Match / Prediction / Report data already returned by the API. They add NO
 * dependency on new backend fields, do NOT change transform.ts compatibility,
 * and work identically in mock and API modes.
 *
 * In a later phase the backend `home/summary` + an LLM may supply richer
 * versions of some of these fields; the field names here are chosen to align
 * with that future contract so the swap is non-breaking.
 *
 * COMPLIANCE: vocabulary is restricted to an allow-list (倾向/偏强/不败趋势/
 * 可能爆冷/难分胜负/风险升高…). Never emit 稳赢/必中/跟单 or any betting phrasing.
 */
import type { Match } from '../types';

export interface OpsInsight {
  aiPickLabel: string;       // e.g. "主胜偏强"
  confidenceStar: number;    // 1..5
  confidenceStars: string;   // "★★★★☆"
  upsetScore: number;        // 0..100
  riskTags: string[];        // category chips, not fabricated facts
  topRisk: string;           // one-line risk summary
  freeConclusion: string;    // blurred conclusion (label + stars, no exact score)
  premiumTeaser: string[];   // what unlock reveals
  heatLabel: string;         // lightweight, non-fabricated heat label
  liveSensitiveScore: number;// 0..100, how lineup-sensitive the match is
}

// ── AI tendency label ───────────────────────────────────────────────────────
export function aiPickLabel(m: Match): string {
  const { home, draw, away } = m.winProb;
  const lead = home - away;
  const spread = Math.max(home, draw, away) - Math.min(home, draw, away);

  if (home >= 48 && lead >= 12) return '主胜偏强';
  if (away >= 48 && -lead >= 12) return '客胜偏强';
  if (home + draw >= 70 && home >= away) return '主队不败趋势';
  if (away + draw >= 70 && away > home) return '客队不败趋势';
  if (spread < 8) return '难分胜负';
  return lead >= 0 ? '主胜略占优' : '客胜略占优';
}

// ── Confidence → stars ──────────────────────────────────────────────────────
export function confidenceStar(confidence: number): number {
  if (confidence >= 72) return 5;
  if (confidence >= 60) return 4;
  if (confidence >= 50) return 3;
  if (confidence >= 40) return 2;
  return 1;
}

export function starString(n: number): string {
  const full = Math.max(0, Math.min(5, n));
  return '★'.repeat(full) + '☆'.repeat(5 - full);
}

// ── Upset score ─────────────────────────────────────────────────────────────
export function upsetScore(m: Match): number {
  const { home, away } = m.winProb;
  const closeness = Math.max(0, 30 - Math.abs(home - away)); // teams close → higher
  const riskW = m.riskLevel === 'high' ? 40 : m.riskLevel === 'medium' ? 20 : 5;
  const tagW = m.tag === 'upset' ? 25 : 0;
  const confW = m.confidence < 55 ? 15 : 0;
  const score = riskW + tagW + confW + closeness * 0.6;
  return Math.round(Math.max(0, Math.min(100, score)));
}

// ── Live-sensitivity score ──────────────────────────────────────────────────
export function liveSensitiveScore(m: Match): number {
  const base = m.riskLevel === 'high' ? 80 : m.riskLevel === 'medium' ? 55 : 32;
  const liveBump = m.tag === 'live' ? 12 : 0;
  return Math.min(100, base + liveBump);
}

// ── Risk category tags (categories to watch, NOT fabricated facts) ──────────
const KEYWORD_TAGS: Array<[RegExp, string]> = [
  [/伤停|伤病|缺阵/, '伤病'],
  [/反击/, '快速反击'],
  [/首发|阵容|出场/, '临场首发'],
  [/后卫|中卫|防线|防守/, '防线稳定性'],
  [/中场|控制/, '中场控制'],
  [/主场/, '主场氛围'],
  [/状态/, '近期状态'],
  [/裁判/, '裁判尺度'],
  [/体能|旅行/, '体能与旅行'],
  [/阵型/, '阵型变化'],
];

export function riskTags(m: Match): string[] {
  const text = `${m.riskNote} ${m.freeNote}`;
  const tags: string[] = [];
  for (const [re, tag] of KEYWORD_TAGS) {
    if (re.test(text) && !tags.includes(tag)) tags.push(tag);
  }
  if (tags.length === 0) {
    // No specific signal in text → show generic dimensions to watch.
    return m.riskLevel === 'high'
      ? ['临场首发', '阵型变化', '战意']
      : ['临场首发', '近期状态'];
  }
  return tags.slice(0, 4);
}

export function topRisk(m: Match): string {
  if (m.riskNote) {
    const first = m.riskNote.split(/[。；;]/)[0];
    return first ? first.trim() : m.riskNote;
  }
  return m.riskLevel === 'high'
    ? '双方接近，结果对临场阵容较为敏感'
    : '常规波动，关注临场首发';
}

// ── Reason bullets (rules now; LLM in a later phase) ────────────────────────
export function reasonBullets(m: Match): string[] {
  if (m.features && m.features.length) {
    return m.features.slice(0, 3).map(f =>
      `${f.label}：${f.value >= 0 ? '正向贡献 +' : '风险扣减 '}${f.value}%`
    );
  }
  const { home, draw, away } = m.winProb;
  const riskText =
    m.riskLevel === 'high' ? '不确定性较高' :
    m.riskLevel === 'medium' ? '存在一定波动' : '方向相对明确';
  const bullets = [
    `模型综合胜率 主胜 ${home}% / 平局 ${draw}% / 客胜 ${away}%`,
    `信心指数 ${Math.round(m.confidence)}，${riskText}`,
  ];
  const tr = topRisk(m);
  if (tr) bullets.push(`关注点：${tr}`);
  return bullets.slice(0, 3);
}

// ── Lightweight heat label (non-fabricated; capability building) ────────────
export function heatLabel(m: Match): string {
  if (m.tag === 'focus') return '高关注';
  if (m.tag === 'upset') return '热议中';
  if (m.tag === 'live') return '临场热点';
  return m.confidence >= 65 ? '关注中' : '常规';
}

// ── Free conclusion + premium teaser ────────────────────────────────────────
export function freeConclusion(m: Match): string {
  return `${aiPickLabel(m)} · 信心 ${starString(confidenceStar(m.confidence))}`;
}

export function premiumTeaser(): string[] {
  return ['精确推荐比分', '完整 2-3 条理由', '风险等级与详细风险', '临场修正推送'];
}

// ── Aggregate ───────────────────────────────────────────────────────────────
export function deriveOps(m: Match): OpsInsight {
  const star = confidenceStar(m.confidence);
  return {
    aiPickLabel: aiPickLabel(m),
    confidenceStar: star,
    confidenceStars: starString(star),
    upsetScore: upsetScore(m),
    riskTags: riskTags(m),
    topRisk: topRisk(m),
    freeConclusion: freeConclusion(m),
    premiumTeaser: premiumTeaser(),
    heatLabel: heatLabel(m),
    liveSensitiveScore: liveSensitiveScore(m),
  };
}

/** Pick the C-position match: prefer tag=focus, else highest confidence. */
export function pickTopSignal(matches: Match[]): Match | undefined {
  if (!matches.length) return undefined;
  const focus = matches.find(m => m.tag === 'focus');
  if (focus) return focus;
  return [...matches].sort((a, b) => b.confidence - a.confidence)[0];
}

/** Top-N upset matches by derived upset score (desc). */
export function topUpsets(matches: Match[], n = 3): Array<{ match: Match; score: number }> {
  return matches
    .map(m => ({ match: m, score: upsetScore(m) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, n);
}
