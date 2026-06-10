// LLM-generated narrative (the football intelligence) — NOT hand-written.
// These JSON files are produced by scripts/mvp2_generate_scoutscore_narrative.py
// (real DeepSeek by default; Gemini benchmark kept in docs/data_audit), gated by
// scripts/check_mvp2_llm_narrative_guard.py, per docs/MVP2_LLM_NARRATIVE_CONTRACT.md.
// DO NOT hand-edit the JSON; regenerate + re-guard instead. Engineering only
// transports + renders the model's output.
//
// vi/mm fall back to English (no en narrative generated -> page uses deterministic
// fallback for en/mm). Loaded at build time (bundled), so the frontend never calls
// the LLM or the vendor.
import type { Locale } from '../i18n/useLocale';
import zhCN from './narratives/855737.zh-CN.json';
import viVN from './narratives/855737.vi-VN.json';

export interface NarrativeSignal {
  name: string;
  text: string;
  source_refs?: unknown[];
  assumption_flag?: boolean;
}
export interface Narrative {
  hero_title: string;
  hero_subtitle: string;
  model_judgement: string;
  validated_signals: NarrativeSignal[];
  underweighted_signals: NarrativeSignal[];
  customer_takeaway: string;
  operator_copy: string;
  cta_copy: string;
  internal_notes: string[];
  source_ref_map: Record<string, string[]>;
  llm_provider: string;
  model?: string;
  language?: string;
  generated_at?: string;
}

// fixtureId -> locale -> guard-passed LLM narrative. Only zh/vi generated; en/mm
// resolve to null so the page uses its deterministic fallback copy.
const DATA: Record<string, Partial<Record<Locale, Narrative>>> = {
  '855737': { zh: zhCN as Narrative, vi: viVN as Narrative },
};

export function getNarrative(fixtureId: string, loc: Locale): Narrative | null {
  return DATA[fixtureId]?.[loc] ?? null;
}
