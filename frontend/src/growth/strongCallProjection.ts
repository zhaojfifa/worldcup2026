// P1.1c-fix — CANONICAL STRONG-CALL PROJECTION (Owner verdict 2026-06-12).
// Share is a projection of the main product, not a separate storyline: every surface
// (/predict StrongCallCard, /share cards, homepage main card, share copy, CLI mirror)
// renders THESE values. The scoreband split and risk harmonization happen HERE, once.
// All judgement strings remain guard-passed LLM narrative fields; this module only
// parses, merges (Owner-directed 中高 rule) and orders them.
import type { Locale } from '../i18n/useLocale';
import { getProductNarrative, type ProductNarrative } from '../data/productNarrativeData';
import { getUpcomingFixture } from '../data/upcomingFixtures';
import { getExternalSignals } from '../data/externalSignalData';
import { getPredictionArtifact, predictionArtifactLocale, type PredictionArtifact } from '../data/predictionArtifacts';

export interface StrongCall {
  fixture_id: string;
  teams: string;
  kickoffUtc: string | null;
  main_lean: string;
  primary_score: string | null;
  backup_scores: string[];
  scoreline_raw: string;          // fallback when the band has no parsable scores
  risk_label: string;             // harmonized (lean 偏高 + label 中 -> 中高)
  top_variable: string;
  why: string;                    // LLM hero_subtitle
  external_expectation: string[]; // projected customer-safe lines
  t30_hook: string;
  cta_line: string;
}

export interface RecapCall {
  fixture_id: string;
  result_title: string;       // 结果 (LLM short_title)
  what_was_right: string;     // 赛前看对了什么 (validated factor)
  why_deviated: string;       // 比分为什么偏离 (LLM screenshot_line)
  calibration_line: string;   // 复盘校准 framing
  next_hook: string;          // 下一场钩子
}

// Canonical per-language wording — defined ONCE; every surface quotes these.
export const T30_HOOK: Record<string, string> = {
  zh: '开球前 30 分钟，首发 11 人出来后，群内更新最终倾向和比分区间。',
  vi: 'Đội hình công bố là nhóm cập nhật thiên hướng cuối + vùng tỷ số, 30 phút trước giờ đá.',
  my: 'Lineup ထွက်တာနဲ့ ပွဲမစခင် မိနစ် ၃၀ မှာ အဖွဲ့ထဲ နောက်ဆုံးအမြင် + စကောအပိုင်းအခြား တင်မည်။',
};
export const CTA_LINE: Record<string, string> = {
  zh: '进群等临场修正', vi: 'Vào nhóm chờ hiệu chỉnh sát giờ', my: 'အဖွဲ့ဝင်ပြီး ပြန်တွက်ချက် စောင့်ပါ',
};
export const CALIBRATION_LINE: Record<string, string> = {
  zh: '复盘校准：赛前看方向，临场看变量，赛后看校准。',
  vi: 'Hiệu chỉnh: trước trận xem hướng, sát giờ xem biến số, sau trận xem hiệu chỉnh.',
  my: 'ပြန်ညှိချက်: ပွဲကြို ဦးတည်ချက် · ပွဲနီး variable · ပွဲပြီး ပြန်ညှိချက်။',
};
// P6 P0-4 (Owner): NEXT_HOOK must NOT hardcode a specific next fixture (was literal
// 'Brazil vs Morocco' → stale for every other recap). Generic, fixture-agnostic pointer; the
// match-specific next-match impact comes from the observation artifact's next_impact, not here.
export const NEXT_HOOK: Record<string, string> = {
  zh: '下一场比赛，开球前 30 分钟继续看首发修正。',
  vi: 'Trận tới, tiếp tục xem hiệu chỉnh đội hình 30 phút trước giờ đá.',
  my: 'နောက်ပွဲ — ပွဲမစခင် မိနစ် ၃၀ lineup ပြန်တွက်ချက် ဆက်ကြည့်ပါ။',
};

/** Owner rule: lean says 风险偏高 but the explicit label word is bare 中 -> display 中高.
 * A deterministic merge of two statements the model itself made — never a new judgement. */
export function harmonizedRisk(mainLean: string, riskLevel: string): string {
  if (/风险偏高|风险高/.test(mainLean) && /^中(?!高)/.test(riskLevel)) {
    return riskLevel.replace(/^中/, '中高');
  }
  return riskLevel;
}

/** First listed score in the LLM band = 主比分, rest = 备选. Parsing only. */
export function splitScoreband(scorelineView: string): { primary: string; alts: string[] } | null {
  const scores = scorelineView.match(/\d+\s*[-–]\s*\d+/g)?.map(s => s.replace(/\s/g, ''));
  if (!scores || !scores.length) return null;
  return { primary: scores[0], alts: scores.slice(1) };
}

const LANG3 = (loc: Locale): 'zh' | 'vi' | 'my' | null =>
  loc === 'zh' || loc === 'vi' || loc === 'my' ? loc : null;

/** THE canonical pre-match projection. Tries the bundled ProductNarrative first; if absent,
 *  falls back to a Prediction Artifact (MVP2-P5: manual hotspot with no narrative). Returns
 *  null only when neither source exists / the narrative is a finished recap. */
export function buildStrongCall(fixtureId: string, loc: Locale): StrongCall | null {
  const lang = LANG3(loc);
  if (!lang) return null;
  const n: ProductNarrative | null = getProductNarrative(fixtureId, lang);
  if (n && n.mode !== 'real_recap') {
    const fx = getUpcomingFixture(fixtureId);
    const band = splitScoreband(n.scoreline_view);
    const ext = getExternalSignals(fixtureId, lang);
    return {
      fixture_id: fixtureId,
      teams: fx ? `${fx.home} vs ${fx.away}` : n.short_title,
      kickoffUtc: fx?.kickoffUtc ?? null,
      main_lean: n.main_lean,
      primary_score: band?.primary ?? null,
      backup_scores: band?.alts ?? [],
      scoreline_raw: n.scoreline_view,
      risk_label: harmonizedRisk(n.main_lean, n.risk_level),
      top_variable: n.watch_next_signals?.[0]?.name || n.risk_factors?.[0]?.name || '',
      why: n.hero_subtitle || '',
      external_expectation: ext?.lines ?? [],
      t30_hook: T30_HOOK[lang],
      cta_line: CTA_LINE[lang],
    };
  }
  const art = getPredictionArtifact(fixtureId);
  if (art) return buildStrongCallFromArtifact(art, lang);
  return null;
}

/** MVP2-P5 — artifact → canonical StrongCall. Unconfirmed numerics stay null and surface as the
 *  pending labels (方向待临场确认 / 比分待开球前 30 分钟确认); never invents a score or probability. */
export function buildStrongCallFromArtifact(art: PredictionArtifact, loc: Locale): StrongCall | null {
  const lang = LANG3(loc);
  if (!lang) return null;
  const A = predictionArtifactLocale(art, lang);
  const p = A.prediction;
  // P8 P0 precedence (Owner 2026-06-15): when a SOURCE-TAGGED model_fields block exists (source
  // computed | seed | operator_confirmed | operator_estimated, never 'unavailable'), it is the
  // canonical source for the locale-neutral SCORE. The localized i18n risk word stays the display
  // (model_fields.risk_level is the same judgement, just the canonical zh token) so vi/my stay Han=0.
  // Unavailable fields (win_prob/confidence) are NOT in StrongCall and are never surfaced.
  const mf = art.model_fields;
  const mfUsable = !!mf && mf.source !== 'unavailable';
  const primary_score = (mfUsable && mf!.recommended_score) || p.score_call;
  const backup_scores = mfUsable && mf!.backup_scores?.length
    ? mf!.backup_scores
    : (p.backup_score ? p.backup_score.split('/').map(s => s.trim()).filter(Boolean) : []);
  return {
    fixture_id: art.fixture_key,
    teams: `${art.home} vs ${art.away}`,
    kickoffUtc: art.kickoffUtc,
    main_lean: p.primary_direction ?? A.pending_direction,
    primary_score,
    backup_scores,
    scoreline_raw: primary_score ?? A.pending_score,
    risk_label: p.risk_level ?? (mfUsable ? (mf!.risk_level ?? '') : ''),
    top_variable: p.top_variable || A.analysis.risk_variables[0] || '',
    why: p.why || p.risk_note || '',
    external_expectation: A.analysis.external_expectation ?? [],
    t30_hook: T30_HOOK[lang],
    cta_line: CTA_LINE[lang],
  };
}

/** THE canonical recap projection (结果 → 看对 → 偏离 → 校准 → 下一场). */
export function buildRecapCall(fixtureId: string, loc: Locale): RecapCall | null {
  const lang = LANG3(loc);
  const n = lang ? getProductNarrative(fixtureId, lang) : null;
  if (!lang || !n || n.mode !== 'real_recap') return null;
  return {
    fixture_id: fixtureId,
    result_title: n.short_title,
    what_was_right: n.validated_factors?.[0]?.name || '',
    why_deviated: n.screenshot_line,
    calibration_line: CALIBRATION_LINE[lang],
    next_hook: NEXT_HOOK[lang],
  };
}
