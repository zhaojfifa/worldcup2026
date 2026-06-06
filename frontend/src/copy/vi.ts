/**
 * Vietnamese (vi) operation copy — trial-level support, NOT a full i18n switch.
 *
 * Structure mirrors `zh.ts` (named exports) and borrows the per-locale copy-map +
 * fallback idea from the apolloveo-auto reference (CLIENT_DICT per locale, vi → zh
 * fallback). This file is additive: the site stays zh-CN; these strings are for
 * Zalo / Telegram operator dispatch to Vietnamese users.
 *
 * Burmese (my/mm) is deferred — see docs. Do NOT add a language switcher here.
 *
 * Forbidden (never add): chắc thắng / đảm bảo thắng / cá cược / đặt cược /
 * kiếm tiền / lợi nhuận chắc chắn or any betting / guaranteed-profit wording.
 */

// Fallback chain (reference pattern): vi resolves down to zh if a key is missing.
export const VI_FALLBACK_CHAIN = ['vi', 'zh'] as const;
export const LOCALE_VI = 'vi';

export const BRAND_VI = {
  name: 'Giành Cup',
  sub: 'Cộng đồng thông tin bóng đá AI World Cup',
  tagline: 'Không chỉ xem tỷ lệ, hãy hiểu vì sao AI đưa ra nhận định.',
  en: '2026 World Cup AI Football Intelligence',
};

export const HEADER_VI = {
  brand: 'Giành Cup',
  role: 'Cộng đồng thông tin bóng đá AI World Cup',
  sub: 'Không chỉ xem tỷ lệ, hãy hiểu vì sao AI đưa ra nhận định.',
};

export const HERO_VI = {
  kicker: 'THÔNG TIN AI HÔM NAY',
  title: 'Nhận định bóng đá bằng dữ liệu AI',
  sub: 'Xu hướng AI · Thay đổi tỷ lệ · Cảnh báo rủi ro · Hiệu chỉnh sát giờ',
};

export const CTA_VI = {
  viewAI: 'Xem nhận định AI',
  unlock: 'Mở khóa phân tích đầy đủ',
  joinCommunity: 'Vào nhóm để xem thông tin sớm nhất',
  subscribe: 'Đăng ký thông tin sát giờ',
};

export const COMMUNITY_VI = {
  title: 'Ma trận cộng đồng',
  desc: 'Mỗi ngày AI đẩy thông tin 3-5 trận, hiệu chỉnh sát giờ và cảnh báo rủi ro.',
  zalo: 'Zalo · sân nhà của fan Việt',
  telegram: 'Telegram · đẩy thông tin sát giờ',
  facebook: 'Facebook · thảo luận & tổng kết',
  tiktok: 'TikTok · 3 trận nổi bật mỗi ngày',
};

// MTC loyalty-points notice (compliance-critical).
export const MTC_NOTICE_VI =
  'MTC là điểm tích lũy trong nền tảng, không thể rút tiền, không thể chuyển nhượng, ' +
  'không thể giao dịch và không phải tài sản tài chính.';

// Mandatory disclaimer for 战绩 / 命中 / 连胜 surfaces.
export const DISCLAIMER_VI =
  'Kết quả trong quá khứ không đảm bảo kết quả tương lai. ' +
  'Nội dung chỉ dùng cho phân tích dữ liệu và giải trí bóng đá.';

// Compliance footer (mirrors zh COMPLIANCE_FOOTER).
export const COMPLIANCE_FOOTER_VI =
  'Chỉ phân tích dữ liệu AI · Không phải dịch vụ cá cược · Không nhận cược tiền mặt · MTC không thể rút tiền';

/**
 * Three ready-to-send Vietnamese trial messages (Zalo / Telegram).
 * Plain-text bodies; each carries a risk note + disclaimer. No betting / profit wording.
 * Full formatted versions live in docs/OPERATION_TRIAL_MESSAGES_VI.md.
 */
export const SOCIAL_TRIAL_MESSAGES_VI = [
  {
    id: 'vi-top3',
    title: '🔥 3 trận AI đáng chú ý hôm nay',
    body:
      '⚽ Brazil vs Argentina\n' +
      'Xu hướng AI: Brazil nhỉnh hơn (49%) · Độ tin cậy ★★★☆☆\n' +
      'Một câu: Tuyến giữa mạnh hơn, cánh phải gây sức ép — nhưng không chắc chắn.\n\n' +
      '⚽ Morocco vs Pháp\n' +
      'Xu hướng AI: Cân bằng, Morocco sân nhà đáng gờm · ★★☆☆☆\n' +
      'Một câu: Trận rủi ro cao, khả năng bất ngờ rõ rệt.\n\n' +
      '⚽ Tây Ban Nha vs Đức\n' +
      'Xu hướng AI: Tây Ban Nha nhỉnh hơn (41%) · ★★★☆☆\n' +
      'Một câu: Thực lực sát nhau, đội hình ra sân quyết định.',
    cta: 'Vào nhóm để xem nhận định AI đầy đủ + hiệu chỉnh sát giờ 👉',
    risk: 'Xu hướng AI không phải là kết quả. Mỗi trận đều có mức rủi ro.',
    disclaimer: DISCLAIMER_VI,
  },
  {
    id: 'vi-upset',
    title: '⚠️ Rủi ro bất ngờ số 1: Morocco vs Pháp',
    body:
      'AI đánh dấu trận này «rủi ro cao».\n\n' +
      'Điểm rủi ro: Morocco sân nhà sung sức, Pháp sân khách phong độ thất thường.\n' +
      'Vì sao đáng chú ý: Tỷ lệ thắng chủ-khách chỉ chênh 5 điểm, hòa cũng tới 29%.\n\n' +
      'Tên tuổi không quyết định kết quả. Trận này AI nhìn vào chi tiết sát giờ.',
    cta: 'Muốn xem AI mổ xẻ trận này? Vào nhóm 👉',
    risk: 'Trận rủi ro cao, kết quả khó lường.',
    disclaimer: DISCLAIMER_VI,
  },
  {
    id: 'vi-live',
    title: '📡 Cập nhật sát giờ · Brazil vs Argentina',
    body:
      '【Cập nhật thông tin sát giờ】\n' +
      'Yếu tố kích hoạt: Trung vệ trụ cột Argentina không đá chính\n' +
      'Xu hướng AI ban đầu: Brazil 45%\n' +
      'Sau hiệu chỉnh: Brazil 49% ▲\n' +
      'Lý do AI điều chỉnh: Khả năng triển khai bóng của Argentina giảm, ' +
      'lợi thế cánh phải của Brazil tăng.\n\n' +
      'Đội hình vừa công bố, AI đã tính lại. Đó là lý do nên vào nhóm — thấy thay đổi sớm nhất.',
    cta: 'Hiệu chỉnh sát giờ chỉ đẩy sớm nhất trong nhóm 👉',
    risk: 'Hiệu chỉnh sát giờ là «AI tính lại», không phải «chắc chắn thắng».',
    disclaimer: DISCLAIMER_VI,
  },
] as const;
