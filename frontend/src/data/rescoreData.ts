// 30-Min ReScore model layer (QiuGe sprint) — LLM-written product copy on an
// engineering trigger/rule skeleton. Produced by scripts/mvp2_generate_rescore_models.py
// (DeepSeek, inline-guarded: forbidden/tone/URL/persona/vi-Han). DO NOT hand-edit;
// regenerate + re-copy. Bundled — the frontend never calls the LLM or the vendor.
import type { Locale } from '../i18n/useLocale';
import r69zh from './rescoreModels/1489369.zh-CN.json';
import r69vi from './rescoreModels/1489369.vi-VN.json';
import r71zh from './rescoreModels/1489371.zh-CN.json';
import r71vi from './rescoreModels/1489371.vi-VN.json';

export interface RescoreTrigger {
  key: string;
  name: string;
  current_status: string;
  why_it_matters: string;
  possible_impact: string;
  free_copy: string;
  subscriber_copy: string;
}
export interface RescoreRule {
  condition: string;
  change_to_lean: string;
  change_to_risk: string;
  change_to_score_range: string;
  operator_note: string;
}
export interface RescoreModel {
  fixture_id: string;
  pre_match_lean: string;
  pre_match_risk_level: string;
  score_range_before: string;
  rescore_triggers: RescoreTrigger[];
  rescore_decision_rules: RescoreRule[];
  public_teaser: string;
  group_join_hook: string;
  reminder_message: string;
  llm_provider: string;
  model?: string;
}

const DATA: Record<string, Partial<Record<Locale, RescoreModel>>> = {
  '1489369': { zh: r69zh as RescoreModel, vi: r69vi as RescoreModel },
  '1489371': { zh: r71zh as RescoreModel, vi: r71vi as RescoreModel },
};

export function getRescore(id: string, loc: Locale): RescoreModel | null {
  return DATA[id]?.[loc] ?? null;
}
