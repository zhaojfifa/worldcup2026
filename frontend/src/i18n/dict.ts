/**
 * Bilingual copy dictionary (zh | vi) for the operation-trial core surfaces.
 *
 * Scope (intentionally limited — not full i18n): header, hero, home core labels,
 * home CTAs, community title, Content Studio badge, MTC statement, disclaimer,
 * compliance footer, bottom nav, key buttons. Dynamic match data (team names,
 * risk_note, AI prediction text) stays Chinese for now.
 *
 * vi values reuse `copy/vi.ts` where available; zh values reuse `copy/zh.ts`.
 * Missing vi keys fall back to zh.
 */
import {
  BRAND, HOME, SOCIAL, DISCLAIMER_RECORD, COMPLIANCE_FOOTER, MTC_STATEMENT, VI_TRIAL_COPY_READY,
} from '../copy/zh';
import {
  BRAND_VI, MTC_NOTICE_VI, DISCLAIMER_VI, COMPLIANCE_FOOTER_VI,
} from '../copy/vi';
import { useLocale, type Locale } from './useLocale';

interface Pair { zh: string; vi: string }

const D = {
  // Header
  brandName:   { zh: BRAND.name,                 vi: BRAND_VI.name },
  brandRole:   { zh: BRAND.zhRole,               vi: BRAND_VI.sub },
  headerSub:   { zh: BRAND.headerSub,            vi: BRAND_VI.tagline },
  brandHeroEn: { zh: BRAND.heroEn,               vi: BRAND_VI.en },
  heroSub:     { zh: BRAND.heroSub,              vi: 'Xu hướng AI · Thay đổi tỷ lệ · Cảnh báo rủi ro · Hiệu chỉnh sát giờ' },

  // Bottom nav
  navHome:      { zh: '首页',    vi: 'Trang chủ' },
  navDetail:    { zh: 'AI预测',  vi: 'Dự đoán AI' },
  navToken:     { zh: 'MTC积分', vi: 'Điểm MTC' },
  navCommunity: { zh: '社群',    vi: 'Cộng đồng' },

  // Hero title (split into two spans in JSX)
  heroTitlePre:    { zh: 'AI 足球',   vi: 'Thông tin bóng đá ' },
  heroTitleAccent: { zh: '情报社区',  vi: 'AI' },

  // Home capability chips
  capModel:  { zh: 'AI 赛前模型',        vi: 'Mô hình AI trước trận' },
  capLive:   { zh: '临场 30 分钟修正',   vi: 'Hiệu chỉnh sát giờ (30′)' },
  capRisk:   { zh: '风险评级',           vi: 'Đánh giá rủi ro' },
  capUnlock: { zh: 'MTC 解锁',           vi: 'Mở khóa MTC' },

  // Home balance / check-in
  balanceLabel: { zh: '我的 MTC 球迷积分：', vi: 'Điểm MTC của tôi: ' },
  checkin:      { zh: '签到 +10',            vi: 'Điểm danh +10' },
  checkedIn:    { zh: '已签到',              vi: 'Đã điểm danh' },
  checkinToastDone: { zh: '今日已签到',      vi: 'Hôm nay đã điểm danh' },
  checkinToastOk:   { zh: '签到成功 +10 MTC', vi: 'Điểm danh thành công +10 MTC' },

  // Home core labels + CTA
  signalTitle: { zh: HOME.signalTitle,  vi: 'Tín hiệu AI mạnh nhất hôm nay' },
  tendency:    { zh: HOME.tendency,     vi: 'Xu hướng AI' },
  topRisk:     { zh: HOME.topRisk,      vi: 'Rủi ro chính' },
  ctaView:     { zh: HOME.ctaView,      vi: 'Xem nhận định AI' },
  ctaUnlock:   { zh: HOME.ctaUnlock,    vi: 'Mở khóa phân tích đầy đủ' },

  // Home section titles
  listTitle:   { zh: HOME.listTitle,    vi: 'Lịch trận hôm nay' },
  upsetTitle:  { zh: HOME.upsetTitle,   vi: 'Top 3 rủi ro bất ngờ hôm nay' },
  recordTitle: { zh: HOME.recordTitle,  vi: 'Thành tích thông tin AI' },
  heatTitle:   { zh: HOME.heatTitle,    vi: 'Lựa chọn cộng đồng' },
  loopTitle:   { zh: HOME.loopTitle,    vi: 'Trung tâm nhiệm vụ fan' },
  recordPending:  { zh: HOME.recordPending,  vi: 'Mở sau khi cập nhật kết quả thật' },
  recordBuilding: { zh: HOME.recordBuilding, vi: 'Đang xây dựng dữ liệu' },
  heatComingSoon: { zh: HOME.heatComingSoon, vi: 'Độ nóng cộng đồng sắp ra mắt' },

  // Community
  communityTitle: { zh: SOCIAL.title, vi: 'Ma trận cộng đồng' },
  viBadge:        { zh: VI_TRIAL_COPY_READY.text, vi: VI_TRIAL_COPY_READY.text },

  // Compliance
  mtcStatement:     { zh: MTC_STATEMENT,     vi: MTC_NOTICE_VI },
  disclaimer:       { zh: DISCLAIMER_RECORD, vi: DISCLAIMER_VI },
  complianceFooter: { zh: COMPLIANCE_FOOTER, vi: COMPLIANCE_FOOTER_VI },
} satisfies Record<string, Pair>;

export type CopyKey = keyof typeof D;
export type Copy = Record<CopyKey, string>;

/** Resolve all keys for a locale (vi falls back to zh when a vi value is empty). */
export function getCopy(locale: Locale): Copy {
  const out = {} as Copy;
  (Object.keys(D) as CopyKey[]).forEach((k) => {
    const pair = D[k];
    out[k] = locale === 'vi' ? pair.vi || pair.zh : pair.zh;
  });
  return out;
}

/** React hook: returns the resolved copy for the current locale. */
export function useCopy(): Copy {
  return getCopy(useLocale());
}
