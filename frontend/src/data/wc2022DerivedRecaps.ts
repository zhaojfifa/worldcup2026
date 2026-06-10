/**
 * Real WC2022 recap data — DERIVED from the Kaggle ↔ Render offline alignment
 * (`scripts/audit_kaggle_wc2022.py` → `docs/data_audit/kaggle_wc2022_cross_validation.json`,
 * status=alignment_complete, matched 64/64). Values below are the REAL results
 * (Kaggle martj42, CC0 — license pending operator confirmation), NOT fabricated.
 *
 * Scope: a first batch of model-calibration samples (favorite-failed upsets).
 * These are HISTORICAL recaps for model calibration — NOT current predictions.
 * No hit-rate / 42.2% / betting language anywhere.
 *
 * `winner` / `aiFavorite` are sides relative to the match's home/away so the UI can
 * render localized team names (zh uses the stored names, vi/mm → English, never zh).
 * Per-match `conclusion` prose is localized here (zh/vi/en); mm falls back to en.
 */
import type { Locale } from '../i18n/useLocale';

export interface Wc2022Recap {
  id: number;
  homeGoals: number;
  awayGoals: number;
  winner: 'home' | 'away' | 'draw';
  aiFavorite: 'home' | 'away';
  favoriteProb: number;        // the AI baseline % for the predicted favorite
  favoriteFailed: boolean;     // predicted favorite did not win (upset)
  decidedBy: 'regulation' | 'penalties';
  source: string;
  conclusion: Partial<Record<Locale, string>>;
}

export const WC2022_DERIVED_RECAPS: Record<string, Wc2022Recap> = {
  // Argentina 1–2 Saudi Arabia (2022-11-22) — the famous group-stage upset.
  '8': {
    id: 8,
    homeGoals: 1,
    awayGoals: 2,
    winner: 'away',
    aiFavorite: 'home',
    favoriteProb: 52,
    favoriteFailed: true,
    decidedBy: 'regulation',
    source: 'Kaggle martj42 (CC0, license pending) via scripts/audit_kaggle_wc2022.py',
    conclusion: {
      zh: '典型的大热失手：AI 原始倾向看好阿根廷，实际被 Saudi Arabia 逆转。单靠基线胜率不足以解释世界杯爆冷，需要接入首发、伤停、教练战术与临场变量来校准模型。',
      vi: 'Một ca đội mạnh sẩy chân điển hình: AI ban đầu nghiêng về Argentina nhưng bị Saudi Arabia lội ngược dòng. Chỉ dựa vào xác suất nền là chưa đủ để giải thích bất ngờ ở World Cup — cần bổ sung đội hình xuất phát, chấn thương, chiến thuật HLV và biến số sát giờ để hiệu chỉnh mô hình.',
      en: 'A textbook favorite-failed case: the AI leaned Argentina, but Saudi Arabia turned it around. Baseline win probability alone cannot explain a World Cup upset — lineup, injuries, coaching tactics and live variables are needed to calibrate the model.',
    },
  },
  // Germany 1–2 Japan (2022-11-23) — another group-stage upset.
  '13': {
    id: 13,
    homeGoals: 1,
    awayGoals: 2,
    winner: 'away',
    aiFavorite: 'home',
    favoriteProb: 48,
    favoriteFailed: true,
    decidedBy: 'regulation',
    source: 'Kaggle martj42 (CC0, license pending) via scripts/audit_kaggle_wc2022.py',
    conclusion: {
      zh: '又一例大热失手：AI 原始倾向看好德国，却被 Japan 逆转。基线胜率无法捕捉首发轮换与临场战术变化，需要更深的情报字段（首发、伤停、教练战术、媒体与市场变化）来校准。',
      vi: 'Lại một ca đội mạnh sẩy chân: AI ban đầu nghiêng về Germany nhưng bị Japan lội ngược dòng. Một lần nữa cho thấy xác suất nền không nắm được thay đổi đội hình và chiến thuật sát giờ — cần các trường thông tin sâu hơn (đội hình xuất phát, chấn thương, chiến thuật HLV, truyền thông và biến động thị trường) để hiệu chỉnh.',
      en: 'Another favorite-failed case: the AI leaned Germany, but Japan turned it around. Baseline probability misses lineup rotation and in-game tactics — deeper intelligence fields (lineup, injuries, coaching tactics, media and market movement) are needed to calibrate.',
    },
  },
};

export function getWc2022Recap(id: string): Wc2022Recap | undefined {
  return WC2022_DERIVED_RECAPS[id];
}
