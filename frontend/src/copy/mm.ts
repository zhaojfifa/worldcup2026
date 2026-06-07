/**
 * Burmese / Myanmar (mm) copy — MVP language mode (starting this sprint).
 *
 * Partial: covers the highest-frequency customer-visible surfaces. Any key not
 * present here falls back to English (NOT Chinese) via the dictionary chain
 * (mm → en). Full Burmese localization is deferred; LLM translation deferred.
 */
import type { Copy } from '../i18n/dict';

export const MM: Partial<Copy> = {
  // Header / brand — kept short for Myanmar density
  brandRole: 'AI Football',
  headerSub: 'AI သုံးသပ်ချက် · ပွဲမတိုင်ခင် အချက်အလက်',

  // Bottom nav — short
  navHome: 'Home',
  navDetail: 'AI',
  navToken: 'MTC',
  navCommunity: 'Community',

  // Global
  aiTicker: 'AI intel',
  tickerBody: 'AI intel · {n} models today · live watch on',
  loadingText: 'AI intel loading…',
  syncLabel: 'Sync',

  // Hero — short
  heroTitlePre: 'AI ဘောလုံး',
  heroTitleAccent: 'အချက်အလက်',
  heroSub: 'ဖြစ်နိုင်ခြေ · အန္တရာယ် · 30′ update',

  // Capability chips — short (concise English product terms allowed)
  capModel: 'AI မော်ဒယ်',
  capLive: "30′ Update",
  capRisk: 'Risk',
  capUnlock: 'MTC',

  // Balance / check-in
  balanceLabel: 'ကျွန်ုပ်၏ MTC ပွိုင့်: ',
  checkin: 'ဝင်စစ် +10',
  checkedIn: 'စစ်ဆေးပြီး',
  checkinToastDone: 'ယနေ့ စစ်ဆေးပြီးပါပြီ',
  checkinToastOk: 'ဝင်ရောက်စစ်ဆေးအောင်မြင် +10 MTC',

  // Home core + CTA — short
  signalTitle: 'AI signal',
  tendency: 'AI view',
  topRisk: 'Risk',
  ctaView: 'AI View',
  ctaUnlock: 'Full Analysis',
  winLabel: 'နိုင်',

  // Section titles + states
  listTitle: 'ယနေ့ ပွဲများ',
  upsetTitle: 'အံ့အားသင့် TOP3',
  recordTitle: 'AI မှတ်တမ်း',
  heatTitle: 'Community',
  loopTitle: 'ပရိသတ် Zone',
  recordPending: 'တကယ့်ရလဒ်များ ဖြည့်ပြီးမှ ဖွင့်မည်',
  recordBuilding: 'ဒေတာစွမ်းရည် တည်ဆောက်နေသည်',
  heatComingSoon: 'အသိုင်းအဝိုင်း ပူပြင်းမှု မကြာမီ',
  loopFanPoints: 'ပရိသတ်ပွိုင့်',
  loopDailyCheckin: 'နေ့စဉ်စစ်ဆေး',
  loopStreak: 'ဆက်တိုက်နိုင်ပွဲ စိန်ခေါ်မှု',
  loopFreeJoin: 'အခမဲ့ ပါဝင်',
  loopRanking: 'အဆင့်သတ်မှတ်ဇယား',
  loopComingSoon: 'မကြာမီ',

  // Detail
  detailBack: 'ပွဲ ခန့်မှန်းချက် အသေးစိတ်',
  aiVerdict: 'AI ကောက်ချက်',
  confidence: 'ယုံကြည်မှု',
  riskGrade: 'အန္တရာယ်အဆင့်',
  recommendedScore: 'အကြံပြု ရမှတ်',
  unlockToView: 'ဖွင့်ကြည့်ရန်',
  winProbTitle: 'AI လက်ရှိ နိုင်ခြေ',
  whyTitle: 'AI ဘာကြောင့် ဤသို့ဆုံးဖြတ်သလဲ',
  riskTitle: 'အန္တရာယ် အချက်များ',
  premiumTitle: 'AI Tactics',
  premiumLocked: '🔒 Locked',
  unlockCashLabel: 'AI Tactics',
  unlockMtcLabel: '🪙 Full Analysis',
  joinCommunityLabel: 'Join Community',

  // Token
  tokenBack: '🪙 ပရိသတ် Zone',
  walletLabel: 'ကျွန်ုပ်၏ MTC လက်ကျန်',
  myStreak: 'ဆက်တိုက်နိုင်ပွဲ',
  dailyMissions: 'နေ့စဉ် တာဝန်',
  predictionChallenge: 'ခန့်မှန်း Challenge',
  shopTitle: 'MTC Shop',
  rankingsTitle: 'Ranking',
  tokenInsufficient: 'MTC မလုံလောက်ပါ',

  // Community
  communityBack: '👥 VIP',
  vipKicker: 'VIP',
  communityTitle: 'Community',
  statusComingSoon: 'မကြာမီ',
  statusActive: 'ကြည့်ရန်',
  statusDisabled: 'မဖွင့်သေး',
  benefitsTitle: 'Benefits',
  subscribeNowLabel: 'Join now',
  alreadySubscribed: 'စာရင်းသွင်းပြီး',

  // Compliance
  mtcStatement: 'MTC သည် ပလက်ဖောင်းပွိုင့်သာဖြစ်ပြီး ငွေထုတ်မရ၊ လွှဲမရ၊ ရောင်းဝယ်မရ၊ ဘဏ္ဍာရေးပိုင်ဆိုင်မှု မဟုတ်ပါ။',
  disclaimer: 'အတိတ်စွမ်းဆောင်ရည်သည် အနာဂတ်ရလဒ်ကို အာမမခံပါ။ ဒေတာခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဘောလုံးဖျော်ဖြေရေးအတွက်သာ။',
  complianceFooter: 'AI ဒေတာခွဲခြမ်းစိတ်ဖြာမှုသာ · လောင်းကစားဝန်ဆောင်မှု မဟုတ် · ငွေသားလောင်းကစား မရှိ · MTC ငွေထုတ်မရ',
};
