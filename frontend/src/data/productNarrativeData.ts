// LLM-generated PRODUCT PROOF narratives (the football intelligence) — NOT hand-written.
// Produced by scripts/mvp2_generate_product_proof_narratives.py (real DeepSeek bound here;
// Gemini benchmark stays in docs/data_audit), gated by
// scripts/check_mvp2_product_narrative_guard.py per docs/MVP2_LLM_NARRATIVE_CONTRACT.md (v2).
// DO NOT hand-edit the JSON; regenerate + re-guard, then re-copy:
//   cp docs/data_audit/mvp2_product_proof_narratives/{id}.{lang}.deepseek.json \
//      frontend/src/data/productNarratives/{id}.{lang}.json
// Bundled at build time — the frontend never calls the LLM or the vendor.
import type { Locale } from '../i18n/useLocale';
import r855737zh from './productNarratives/855737.zh-CN.json';
import r855737vi from './productNarratives/855737.vi-VN.json';
import r979139zh from './productNarratives/979139.zh-CN.json';
import r979139vi from './productNarratives/979139.vi-VN.json';
import p2026zh from './productNarratives/2026_brazil_argentina.zh-CN.json';
import p2026vi from './productNarratives/2026_brazil_argentina.vi-VN.json';

export interface ProductFactor {
  name: string;
  text: string;
  source_refs?: unknown[];
  assumption_flag?: boolean;
}

export interface ProductNarrative {
  product_name: string;
  fixture_id: string;
  mode: 'historical_recap' | 'pre_match_2026_modeling';
  language: string;
  hero_title: string;
  hero_subtitle: string;
  short_title: string;
  screenshot_line: string;
  model_judgement: string;
  main_lean: string;
  scoreline_view: string;
  risk_level: string;
  risk_factors: ProductFactor[];
  validated_factors: ProductFactor[];
  underweighted_factors: ProductFactor[];
  watch_next_signals: ProductFactor[];
  operator_copy: string;
  subscription_hook: string;
  group_join_copy: string;
  today_cta: string;
  social_post: string;
  internal_notes: string[];
  source_ref_map: Record<string, unknown>;
  llm_provider: string;
  model?: string;
  generated_at?: string;
}

// id -> locale -> guard-passed LLM product narrative. zh/vi only; en/mm resolve to
// null so pages use their deterministic fallback (customer langs of this proof are zh/vi).
const DATA: Record<string, Partial<Record<Locale, ProductNarrative>>> = {
  '855737': { zh: r855737zh as ProductNarrative, vi: r855737vi as ProductNarrative },
  '979139': { zh: r979139zh as ProductNarrative, vi: r979139vi as ProductNarrative },
  '2026_brazil_argentina': { zh: p2026zh as ProductNarrative, vi: p2026vi as ProductNarrative },
};

export const PRODUCT_RECAPS = new Set<string>(['855737', '979139']);

export function getProductNarrative(id: string, loc: Locale): ProductNarrative | null {
  return DATA[id]?.[loc] ?? null;
}

// /predict/2026-brazil-argentina -> narrative id 2026_brazil_argentina
export function predictSlugToId(slug: string): string {
  return slug.replace(/-/g, '_');
}
